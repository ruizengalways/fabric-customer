"""Fabric resource, OneLake staging, and SQL preparation helpers."""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import time
from typing import Mapping
from uuid import UUID

FABRIC_ITEMS_ROOT = Path(__file__).resolve().parent / "fabric_items"
import sys
sys.path.insert(0, str(FABRIC_ITEMS_ROOT))

from deploy_fabric_items import FabricApiClient, FabricDeploymentError
from environment_config import CertificationEnvironmentConfig, NamedFabricItemConfig
from onelake_staging import OneLakeDfsClient, staging_manifest
from bootstrap_identity import BootstrapError, _az_token, _run

CERT_ROOT = Path(__file__).resolve().parent
WAREHOUSE_FIXTURES = FABRIC_ITEMS_ROOT / "sql" / "warehouse-certification-fixtures.sql"
CONTROL_PLANE_PROFILE = "fabric_sql_database_v1"
ONELAKE_RESOURCE = "https://storage.azure.com/"


def _header(headers: Mapping[str, str], name: str) -> str | None:
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return None


def _item_id(item: Mapping[str, object], label: str) -> str:
    value = item.get("id")
    if not isinstance(value, str):
        raise BootstrapError(f"{label} did not return an item UUID")
    try:
        return str(UUID(value))
    except ValueError as exc:
        raise BootstrapError(f"{label} returned an invalid item UUID") from exc


def _create_lro_item(client: FabricApiClient, path: str, payload: Mapping[str, object], label: str):
    response = client._request("POST", path, payload)  # noqa: SLF001
    client._require_status(response, {201, 202}, label)  # noqa: SLF001
    body = response.body if response.status == 201 else client._wait_operation(  # noqa: SLF001
        response.headers, expect_result=True
    )
    if not isinstance(body, Mapping):
        raise BootstrapError(f"{label} did not return an item object")
    return body


def _resolve_resource(
    client: FabricApiClient,
    *,
    workspace_id: str,
    item_type: str,
    config: NamedFabricItemConfig,
    create_path: str,
    create_payload: Mapping[str, object],
) -> tuple[Mapping[str, object], str]:
    existing = client.find_exact_item(
        workspace_id,
        item_type=item_type,
        display_name=config.display_name,
    )
    if existing is not None:
        return existing, "reused"
    if not config.create_if_missing:
        raise BootstrapError(
            f"required {item_type} {config.display_name!r} is absent and create_if_missing=false"
        )
    created = _create_lro_item(client, create_path, create_payload, f"Create {item_type}")
    return created, "created"


def _resolve_definition_item(
    client: FabricApiClient,
    *,
    workspace_id: str,
    item_type: str,
    config: NamedFabricItemConfig,
    payload: Mapping[str, object],
) -> tuple[Mapping[str, object], str, str]:
    definition = payload.get("definition")
    if not isinstance(definition, Mapping):
        raise BootstrapError(f"rendered {item_type} definition is invalid")
    definition_sha = hashlib.sha256(
        json.dumps(definition, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    existing = client.find_exact_item(
        workspace_id,
        item_type=item_type,
        display_name=config.display_name,
    )
    if existing is None:
        if not config.create_if_missing:
            raise BootstrapError(
                f"required {item_type} {config.display_name!r} is absent and create_if_missing=false"
            )
        created = _create_lro_item(
            client,
            f"workspaces/{workspace_id}/items",
            payload,
            f"Create {item_type}",
        )
        return created, "created", definition_sha

    item_id = _item_id(existing, item_type)
    response = client._request(  # noqa: SLF001
        "POST",
        f"workspaces/{workspace_id}/items/{item_id}/updateDefinition",
        {"definition": definition},
    )
    client._require_status(response, {200, 202}, f"Update {item_type} definition")  # noqa: SLF001
    if response.status == 202:
        client._wait_operation(response.headers, expect_result=False)  # noqa: SLF001
    return existing, "updated", definition_sha


def _bound_notebook_payload(
    *,
    template: Path,
    display_name: str,
    workspace_id: str,
    lakehouse_id: str,
    lakehouse_name: str,
    replacements: Mapping[str, str] | None = None,
) -> dict[str, object]:
    raw = template.read_text(encoding="utf-8")
    for source, target in (replacements or {}).items():
        raw = raw.replace(source, target)
    notebook = json.loads(raw)
    metadata = notebook.setdefault("metadata", {})
    dependencies = metadata.setdefault("dependencies", {})
    dependencies["lakehouse"] = {
        "known_lakehouses": [{"id": lakehouse_id}],
        "default_lakehouse": lakehouse_id,
        "default_lakehouse_name": lakehouse_name,
        "default_lakehouse_workspace_id": workspace_id,
    }
    encoded = base64.b64encode(
        (json.dumps(notebook, indent=2) + "\n").encode("utf-8")
    ).decode("ascii")
    return {
        "displayName": display_name,
        "description": "Repository-owned exact Framework certification Notebook.",
        "definition": {
            "format": "ipynb",
            "parts": [
                {
                    "path": "notebook-content.ipynb",
                    "payload": encoded,
                    "payloadType": "InlineBase64",
                }
            ],
        },
    }


def _deploy_notebook(
    client: FabricApiClient,
    *,
    workspace_id: str,
    config: NamedFabricItemConfig,
    payload: Mapping[str, object],
) -> tuple[Mapping[str, object], str, str]:
    definition = payload.get("definition")
    if not isinstance(definition, Mapping):
        raise BootstrapError("rendered Notebook definition is invalid")
    definition_sha = hashlib.sha256(
        json.dumps(definition, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    existing = client.find_exact_item(
        workspace_id,
        item_type="Notebook",
        display_name=config.display_name,
    )
    if existing is None:
        if not config.create_if_missing:
            raise BootstrapError(
                f"required Notebook {config.display_name!r} is absent and create_if_missing=false"
            )
        created = client.create_notebook(workspace_id, payload)
        return created, "created", definition_sha
    client.update_notebook_definition(workspace_id, _item_id(existing, "Notebook"), definition)
    return existing, "updated", definition_sha


def _deploy_pipeline(
    client: FabricApiClient,
    *,
    workspace_id: str,
    config: NamedFabricItemConfig,
    payload: Mapping[str, object],
) -> tuple[Mapping[str, object], str, str]:
    definition = payload.get("definition")
    if not isinstance(definition, Mapping):
        raise BootstrapError("rendered Pipeline definition is invalid")
    definition_sha = hashlib.sha256(
        json.dumps(definition, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    existing = client.find_exact_item(
        workspace_id,
        item_type="DataPipeline",
        display_name=config.display_name,
    )
    if existing is None:
        if not config.create_if_missing:
            raise BootstrapError(
                f"required DataPipeline {config.display_name!r} is absent and create_if_missing=false"
            )
        created = client.create_pipeline(workspace_id, payload)
        return created, "created", definition_sha
    client.update_pipeline_definition(workspace_id, _item_id(existing, "DataPipeline"), definition)
    return existing, "updated", definition_sha


def _get_object(client: FabricApiClient, path: str, label: str) -> Mapping[str, object]:
    response = client._request("GET", path)  # noqa: SLF001
    client._require_status(response, {200}, label)  # noqa: SLF001
    if not isinstance(response.body, Mapping):
        raise BootstrapError(f"{label} returned an unsupported response")
    return response.body


def _lakehouse_properties(
    client: FabricApiClient,
    workspace_id: str,
    lakehouse_id: str,
    *,
    timeout_seconds: int = 300,
) -> Mapping[str, object]:
    deadline = time.monotonic() + timeout_seconds
    last_properties: object | None = None
    while True:
        item = _get_object(
            client,
            f"workspaces/{workspace_id}/lakehouses/{lakehouse_id}",
            "Get Lakehouse",
        )
        properties = item.get("properties")
        last_properties = properties
        if isinstance(properties, Mapping) and properties.get("defaultSchema"):
            return properties
        if time.monotonic() >= deadline:
            break
        time.sleep(5)
    del last_properties
    raise BootstrapError(
        "certification Lakehouse did not expose a defaultSchema; it must be schema-enabled "
        "and an existing non-schema Lakehouse will not be mutated implicitly"
    )


def _sql_database_target(
    client: FabricApiClient,
    workspace_id: str,
    item_id: str,
    *,
    timeout_seconds: int = 300,
) -> tuple[str, str]:
    deadline = time.monotonic() + timeout_seconds
    while True:
        item = _get_object(
            client,
            f"workspaces/{workspace_id}/sqlDatabases/{item_id}",
            "Get SQL Database",
        )
        props = item.get("properties")
        if isinstance(props, Mapping):
            server = props.get("serverFqdn")
            database = props.get("databaseName")
            if (
                isinstance(server, str)
                and server
                and isinstance(database, str)
                and database
            ):
                return server, database
        if time.monotonic() >= deadline:
            raise BootstrapError(
                "SQL Database did not expose serverFqdn/databaseName before the bounded timeout"
            )
        time.sleep(5)


def _warehouse_target(
    client: FabricApiClient,
    workspace_id: str,
    item_id: str,
    display_name: str,
    *,
    timeout_seconds: int = 300,
) -> tuple[str, str]:
    deadline = time.monotonic() + timeout_seconds
    while True:
        item = _get_object(
            client,
            f"workspaces/{workspace_id}/warehouses/{item_id}",
            "Get Warehouse",
        )
        props = item.get("properties")
        server = props.get("connectionString") if isinstance(props, Mapping) else None
        if not isinstance(server, str) or not server:
            try:
                response = _get_object(
                    client,
                    f"workspaces/{workspace_id}/warehouses/{item_id}/connectionString",
                    "Get Warehouse connection string",
                )
                server = response.get("connectionString")
            except FabricDeploymentError:
                server = None
        if isinstance(server, str) and server:
            return server, display_name
        if time.monotonic() >= deadline:
            raise BootstrapError(
                "Warehouse SQL connection string was unavailable before the bounded timeout"
            )
        time.sleep(5)


def _run_seed_job(client: FabricApiClient, workspace_id: str, spark_job_id: str) -> dict[str, object]:
    response = client._request(  # noqa: SLF001
        "POST",
        f"workspaces/{workspace_id}/sparkJobDefinitions/{spark_job_id}/jobs/sparkjob/instances",
    )
    client._require_status(response, {202}, "Run seed Spark Job Definition")  # noqa: SLF001
    location = _header(response.headers, "Location")
    if not location:
        raise BootstrapError("seed Spark job response did not include Location")
    deadline = time.monotonic() + 3600
    delay = int(_header(response.headers, "Retry-After") or "5")
    last: Mapping[str, object] | None = None
    while time.monotonic() < deadline:
        time.sleep(max(1, min(60, delay)))
        status = client._request("GET", location)  # noqa: SLF001
        client._require_status(status, {200}, "Get seed Spark job instance")  # noqa: SLF001
        if not isinstance(status.body, Mapping):
            raise BootstrapError("seed Spark job status returned an unsupported response")
        last = status.body
        state = str(last.get("status"))
        if state == "Completed":
            return {
                "setup_only": True,
                "status": state,
                "job_instance_id": last.get("id") or location.rstrip("/").split("/")[-1],
            }
        if state in {"Failed", "Cancelled", "Deduped"}:
            raise BootstrapError(f"seed Spark job ended with status {state}")
        if state not in {"NotStarted", "InProgress"}:
            raise BootstrapError(f"unsupported seed Spark job status: {state}")
        delay = int(_header(status.headers, "Retry-After") or "5")
    raise BootstrapError("seed Spark job timed out")


def _build_customer_inputs(
    *,
    python: Path,
    extension_wheel: Path,
    build_root: Path,
    customer_sha: str,
    framework: Mapping[str, object],
    config: CertificationEnvironmentConfig,
    runner_notebook_id: str,
    pipeline_id: str,
    copy_job_id: str,
    spark_job_id: str,
) -> Path:
    output = build_root / "customer-inputs"
    _run(
        [
            str(python),
            str(CERT_ROOT / "build_candidate_inputs.py"),
            "--project-root",
            str(CERT_ROOT / "project"),
            "--extension-wheel",
            str(extension_wheel),
            "--output",
            str(output),
            "--customer-git-sha",
            customer_sha,
            "--candidate-git-sha",
            str(framework["candidate_git_sha"]),
            "--candidate-wheel-sha256",
            str(framework["wheel_sha256"]),
            "--framework-version",
            str(framework["framework_version"]),
            "--environment",
            config.environment,
            "--workspace-id",
            config.workspace_id,
            "--item-read-id",
            runner_notebook_id,
            "--pipeline-item-id",
            pipeline_id,
            "--copy-job-id",
            copy_job_id,
            "--spark-job-id",
            spark_job_id,
            "--control-plane-profile",
            CONTROL_PLANE_PROFILE,
        ],
        label="build exact Customer certification input bundle",
    )
    required = ("INPUTS.json", "runner-config.json", "release-manifest.json", "project", "dist")
    for name in required:
        if not (output / name).exists():
            raise BootstrapError(f"Customer input builder did not produce {name}")
    return output


def _stage_exact_bytes(
    *,
    config: CertificationEnvironmentConfig,
    lakehouse_id: str,
    framework_artifact: Path,
    customer_inputs: Path,
) -> dict[str, object]:
    token = _az_token(ONELAKE_RESOURCE)
    client = OneLakeDfsClient(token, endpoint=config.onelake_endpoint)
    uploads = []
    for name in (
        "CANDIDATE.json",
        "SHA256SUMS",
        "framework-executable.json",
    ):
        path = framework_artifact / name
        uploads.append(
            client.upload_bytes(
                config.workspace_id,
                lakehouse_id,
                f"Files/framework_cert/{name}",
                path.read_bytes(),
            )
        )
    wheel = next(framework_artifact.glob("fabric_data_framework-*.whl"), None)
    if wheel is None:
        raise BootstrapError("verified Framework artifact no longer contains its wheel")
    uploads.append(
        client.upload_bytes(
            config.workspace_id,
            lakehouse_id,
            f"Files/framework_cert/{wheel.name}",
            wheel.read_bytes(),
        )
    )
    uploads.extend(
        client.upload_tree(
            config.workspace_id,
            lakehouse_id,
            local_root=customer_inputs,
            remote_root="Files/framework_cert/customer-inputs",
            replace_remote_root=True,
        )
    )
    return staging_manifest(tuple(uploads))


def _run_sql_bootstrap(
    *,
    python: Path,
    build_root: Path,
    config: CertificationEnvironmentConfig,
    customer_sha: str,
    framework_version: str,
    control_plane_server: str,
    control_plane_database: str,
    warehouse_server: str,
    warehouse_database: str,
) -> dict[str, object]:
    output = build_root / "sql-bootstrap-result.json"
    command = [
        str(python),
        str(CERT_ROOT / "sql_bootstrap.py"),
        "--control-plane-server",
        control_plane_server,
        "--control-plane-database",
        control_plane_database,
        "--warehouse-server",
        warehouse_server,
        "--warehouse-database",
        warehouse_database,
        "--project-root",
        str(CERT_ROOT / "project"),
        "--warehouse-fixtures",
        str(WAREHOUSE_FIXTURES),
        "--customer-git-sha",
        customer_sha,
        "--framework-version",
        framework_version,
        "--output",
        str(output),
    ]
    if config.mutations.apply_warehouse_fixtures:
        command.append("--apply-warehouse-fixtures")
    if config.mutations.apply_control_plane_schema:
        command.append("--apply-control-plane-schema")
    if config.mutations.materialize_control_plane_metadata:
        command.append("--materialize-control-plane-metadata")
    _run(command, label="SQL certification bootstrap")
    value = json.loads(output.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("contains_secret_values") is not False:
        raise BootstrapError("SQL bootstrap result is invalid")
    return value


def _resource_result(item: Mapping[str, object], action: str) -> dict[str, object]:
    return {
        "id": _item_id(item, str(item.get("type") or "Fabric item")),
        "display_name": item.get("displayName"),
        "type": item.get("type"),
        "action": action,
    }
