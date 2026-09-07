"""Canonical non-secret certification environment configuration.

``--environment DEV`` is a logical Customer/Framework key. It is not a Fabric
Environment item. The selected JSON file contains only non-secret workspace/item
identity and bootstrap policy. SQL server/database values are discovered from the
resolved Fabric items at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from uuid import UUID


_ALLOWED_ENVIRONMENTS = frozenset({"DEV", "UAT"})
_PLACEHOLDER_MARKERS = ("<", ">", "REPLACE_ME", "TODO")
_ZERO_UUID = UUID(int=0)


def _required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    candidate = value.strip()
    if any(marker in candidate for marker in _PLACEHOLDER_MARKERS):
        raise ValueError(f"{label} still contains an unresolved placeholder")
    return candidate


def _uuid(value: object, label: str, *, reject_zero: bool = False) -> str:
    candidate = _required_string(value, label)
    try:
        parsed = UUID(candidate)
    except ValueError as exc:
        raise ValueError(f"{label} must be a UUID") from exc
    if reject_zero and parsed == _ZERO_UUID:
        raise ValueError(f"{label} must not use the all-zero template UUID")
    return str(parsed)


def _https_endpoint(value: object, label: str) -> str:
    candidate = _required_string(value, label).rstrip("/")
    parsed = urlparse(candidate)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(f"{label} must be a credential-free HTTPS endpoint")
    return candidate


@dataclass(frozen=True)
class NamedFabricItemConfig:
    display_name: str
    create_if_missing: bool = True


@dataclass(frozen=True)
class BootstrapMutationConfig:
    seed_provider_sources: bool = True
    apply_warehouse_fixtures: bool = True
    apply_control_plane_schema: bool = True
    materialize_control_plane_metadata: bool = True


@dataclass(frozen=True)
class CertificationEnvironmentConfig:
    schema_version: int
    environment: str
    workspace_id: str
    lakehouse: NamedFabricItemConfig
    control_plane: NamedFabricItemConfig
    warehouse: NamedFabricItemConfig
    copy_job: NamedFabricItemConfig
    spark_job: NamedFabricItemConfig
    seed_spark_job: NamedFabricItemConfig
    runner_notebook: NamedFabricItemConfig
    worker_notebook: NamedFabricItemConfig
    child_pipeline: NamedFabricItemConfig
    mutations: BootstrapMutationConfig
    onelake_endpoint: str

    @property
    def conventional_customer_inputs_root(self) -> str:
        return "/lakehouse/default/Files/framework_cert/customer-inputs"

    def safe_fingerprint(self) -> str:
        payload = {
            field.name: _json_value(getattr(self, field.name))
            for field in fields(self)
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()


def _json_value(value: object) -> object:
    if hasattr(value, "__dataclass_fields__"):
        return {
            field.name: _json_value(getattr(value, field.name))
            for field in fields(value)  # type: ignore[arg-type]
        }
    return value


def default_config_path(environment: str, *, root: Path | None = None) -> Path:
    env = environment.upper()
    if env not in _ALLOWED_ENVIRONMENTS:
        raise ValueError("certification bootstrap environment must be DEV or UAT")
    base = Path("certification/environments") if root is None else root
    return base / f"{env}.json"


def _named_item(value: object, label: str) -> NamedFabricItemConfig:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    create_if_missing = value.get("create_if_missing", True)
    if not isinstance(create_if_missing, bool):
        raise ValueError(f"{label}.create_if_missing must be boolean")
    return NamedFabricItemConfig(
        display_name=_required_string(value.get("display_name"), f"{label}.display_name"),
        create_if_missing=create_if_missing,
    )


def load_environment_config(
    path: str | Path,
    *,
    expected_environment: str | None = None,
) -> CertificationEnvironmentConfig:
    source = Path(path)
    if not source.is_file():
        raise ValueError(
            f"certification environment config is missing: {source}; copy the matching "
            ".example.json, replace the all-zero workspace UUID, review, and commit it"
        )
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("certification environment config must be a JSON object")
    if data.get("schema_version") != 1:
        raise ValueError("certification environment config schema_version must be 1")

    environment = _required_string(data.get("environment"), "environment").upper()
    if environment not in _ALLOWED_ENVIRONMENTS:
        raise ValueError("certification bootstrap environment must be DEV or UAT")
    if expected_environment is not None and environment != expected_environment.upper():
        raise ValueError(
            f"environment config is {environment}, expected {expected_environment.upper()}"
        )

    mutations_raw = data.get("mutations", {})
    if not isinstance(mutations_raw, dict):
        raise ValueError("mutations must be a JSON object")
    for key, value in mutations_raw.items():
        if key not in {field.name for field in fields(BootstrapMutationConfig)}:
            raise ValueError(f"unsupported bootstrap mutation key: {key}")
        if not isinstance(value, bool):
            raise ValueError(f"mutations.{key} must be boolean")
    mutations = BootstrapMutationConfig(**mutations_raw)
    if mutations.materialize_control_plane_metadata and not mutations.apply_control_plane_schema:
        raise ValueError(
            "materialize_control_plane_metadata requires apply_control_plane_schema=true"
        )

    onelake_endpoint = _https_endpoint(
        data.get("onelake_endpoint", "https://onelake.dfs.fabric.microsoft.com"),
        "onelake_endpoint",
    )
    host = urlparse(onelake_endpoint).hostname or ""
    if not host.endswith(".dfs.fabric.microsoft.com"):
        raise ValueError("onelake_endpoint must be a Microsoft Fabric OneLake DFS endpoint")

    return CertificationEnvironmentConfig(
        schema_version=1,
        environment=environment,
        workspace_id=_uuid(data.get("workspace_id"), "workspace_id", reject_zero=True),
        lakehouse=_named_item(data.get("lakehouse"), "lakehouse"),
        control_plane=_named_item(data.get("control_plane"), "control_plane"),
        warehouse=_named_item(data.get("warehouse"), "warehouse"),
        copy_job=_named_item(data.get("copy_job"), "copy_job"),
        spark_job=_named_item(data.get("spark_job"), "spark_job"),
        seed_spark_job=_named_item(data.get("seed_spark_job"), "seed_spark_job"),
        runner_notebook=_named_item(data.get("runner_notebook"), "runner_notebook"),
        worker_notebook=_named_item(data.get("worker_notebook"), "worker_notebook"),
        child_pipeline=_named_item(data.get("child_pipeline"), "child_pipeline"),
        mutations=mutations,
        onelake_endpoint=onelake_endpoint,
    )


__all__ = [
    "BootstrapMutationConfig",
    "CertificationEnvironmentConfig",
    "NamedFabricItemConfig",
    "default_config_path",
    "load_environment_config",
]
