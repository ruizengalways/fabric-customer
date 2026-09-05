"""Resolve exact real-Fabric item bindings without copying workspace item UUIDs by hand.

The resolver is read-only. It consumes the non-secret deployment result produced by
``deploy_fabric_items.py``, verifies that the deployed Notebook/DataPipeline identities
still exist exactly, resolves the remaining approved items by exact type + display name,
and writes a credential-free binding file for ``build_candidate_inputs.py``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Mapping
from uuid import UUID

try:
    from deploy_fabric_items import (
        DEFAULT_ACCESS_TOKEN_ENV_VAR,
        FabricApiClient,
        FabricDeploymentError,
    )
except ModuleNotFoundError:  # pragma: no cover - package-style import fallback
    from .deploy_fabric_items import (
        DEFAULT_ACCESS_TOKEN_ENV_VAR,
        FabricApiClient,
        FabricDeploymentError,
    )


_SAFE_ITEM_TYPE = re.compile(r"^[A-Za-z][A-Za-z0-9]{0,63}$")


class FabricBindingError(RuntimeError):
    """Fail-closed exact binding resolution error."""


def _uuid(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise FabricBindingError(f"{label} must be a UUID string")
    try:
        return str(UUID(value))
    except ValueError as exc:
        raise FabricBindingError(f"{label} must be a UUID") from exc


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise FabricBindingError(f"{label} must be an object")
    return value


def _display_name(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FabricBindingError(f"{label} must be a non-empty display name")
    return value


def _load_deployment_result(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise FabricBindingError(f"deployment result does not exist: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FabricBindingError("deployment result is not valid JSON") from exc
    root = _mapping(value, "deployment result")
    if root.get("schema_version") != 1:
        raise FabricBindingError("unsupported deployment-result schema_version")
    environment = root.get("environment")
    if environment not in {"DEV", "UAT"}:
        raise FabricBindingError("deployment result environment must be DEV or UAT")
    if root.get("contains_secret_values") is not False:
        raise FabricBindingError("deployment result must declare contains_secret_values=false")
    if root.get("certification_result") != "NOT_RUN":
        raise FabricBindingError(
            "deployment result must remain a deployment-only record with certification_result=NOT_RUN"
        )
    workspace_id = _uuid(root.get("workspace_id"), "deployment workspace_id")
    notebook = _mapping(root.get("notebook"), "deployment notebook")
    pipeline = _mapping(root.get("pipeline"), "deployment pipeline")
    result = dict(root)
    result["workspace_id"] = workspace_id
    result["notebook"] = dict(notebook)
    result["pipeline"] = dict(pipeline)
    return result


def _require_item_identity(
    item: Mapping[str, object] | None,
    *,
    workspace_id: str,
    item_type: str,
    display_name: str,
    expected_id: str | None = None,
) -> dict[str, str]:
    if item is None:
        raise FabricBindingError(
            f"required Fabric item was not found: type={item_type!r} display_name={display_name!r}"
        )
    observed_id = _uuid(item.get("id"), f"{item_type} item id")
    if expected_id is not None and observed_id != expected_id:
        raise FabricBindingError(
            f"{item_type} exact display-name item UUID changed: expected={expected_id} observed={observed_id}"
        )
    if item.get("type") != item_type:
        raise FabricBindingError(f"Fabric item type mismatch for {display_name!r}")
    observed_name = item.get("displayName")
    if observed_name != display_name:
        raise FabricBindingError(f"Fabric item display name mismatch for {item_type}")
    observed_workspace = item.get("workspaceId")
    if observed_workspace is not None and _uuid(observed_workspace, f"{item_type} workspaceId") != workspace_id:
        raise FabricBindingError(f"{item_type} item belongs to a different workspace")
    return {
        "id": observed_id,
        "type": item_type,
        "display_name": display_name,
    }


def resolve_certification_bindings(
    client: FabricApiClient,
    *,
    deployment_result: Path,
    item_read_type: str,
    item_read_display_name: str,
    copy_job_display_name: str,
    spark_job_display_name: str,
) -> dict[str, object]:
    if _SAFE_ITEM_TYPE.fullmatch(item_read_type) is None:
        raise FabricBindingError("item_read_type must be a simple Fabric item type name")
    item_read_display_name = _display_name(item_read_display_name, "item_read_display_name")
    copy_job_display_name = _display_name(copy_job_display_name, "copy_job_display_name")
    spark_job_display_name = _display_name(spark_job_display_name, "spark_job_display_name")

    deployed = _load_deployment_result(deployment_result)
    workspace_id = str(deployed["workspace_id"])
    notebook_record = _mapping(deployed["notebook"], "deployment notebook")
    pipeline_record = _mapping(deployed["pipeline"], "deployment pipeline")
    notebook_id = _uuid(notebook_record.get("id"), "deployment notebook id")
    pipeline_id = _uuid(pipeline_record.get("id"), "deployment pipeline id")
    notebook_name = _display_name(notebook_record.get("display_name"), "deployment notebook display_name")
    pipeline_name = _display_name(pipeline_record.get("display_name"), "deployment pipeline display_name")

    notebook = _require_item_identity(
        client.find_exact_item(
            workspace_id,
            item_type="Notebook",
            display_name=notebook_name,
        ),
        workspace_id=workspace_id,
        item_type="Notebook",
        display_name=notebook_name,
        expected_id=notebook_id,
    )
    pipeline = _require_item_identity(
        client.find_exact_item(
            workspace_id,
            item_type="DataPipeline",
            display_name=pipeline_name,
        ),
        workspace_id=workspace_id,
        item_type="DataPipeline",
        display_name=pipeline_name,
        expected_id=pipeline_id,
    )
    item_read = _require_item_identity(
        client.find_exact_item(
            workspace_id,
            item_type=item_read_type,
            display_name=item_read_display_name,
        ),
        workspace_id=workspace_id,
        item_type=item_read_type,
        display_name=item_read_display_name,
    )
    copy_job = _require_item_identity(
        client.find_exact_item(
            workspace_id,
            item_type="CopyJob",
            display_name=copy_job_display_name,
        ),
        workspace_id=workspace_id,
        item_type="CopyJob",
        display_name=copy_job_display_name,
    )
    spark_job = _require_item_identity(
        client.find_exact_item(
            workspace_id,
            item_type="SparkJobDefinition",
            display_name=spark_job_display_name,
        ),
        workspace_id=workspace_id,
        item_type="SparkJobDefinition",
        display_name=spark_job_display_name,
    )

    return {
        "schema_version": 1,
        "verification_status": "VERIFIED",
        "environment": deployed["environment"],
        "workspace_id": workspace_id,
        "deployment_result_sha256": _sha256_file(deployment_result),
        "notebook": notebook,
        "item_read": item_read,
        "pipeline": pipeline,
        "copy_job": copy_job,
        "spark_job": spark_job,
        "contains_secret_values": False,
        "certification_result": "NOT_RUN",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve and verify exact real-Fabric certification item bindings by display name."
    )
    parser.add_argument(
        "--deployment-result",
        type=Path,
        default=Path("build/fabric-items/deployment-result.json"),
    )
    parser.add_argument("--item-read-type", required=True)
    parser.add_argument("--item-read-display-name", required=True)
    parser.add_argument("--copy-job-display-name", required=True)
    parser.add_argument("--spark-job-display-name", required=True)
    parser.add_argument("--access-token-env-var", default=DEFAULT_ACCESS_TOKEN_ENV_VAR)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/fabric-items/fabric-bindings.json"),
    )
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    token = os.environ.get(args.access_token_env_var)
    if not token:
        parser.error(
            f"environment variable {args.access_token_env_var} must contain an approved Fabric API access token"
        )
    try:
        result = resolve_certification_bindings(
            FabricApiClient(token),
            deployment_result=args.deployment_result,
            item_read_type=args.item_read_type,
            item_read_display_name=args.item_read_display_name,
            copy_job_display_name=args.copy_job_display_name,
            spark_job_display_name=args.spark_job_display_name,
        )
    except (FabricDeploymentError, FabricBindingError) as exc:
        parser.error(str(exc))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "workspace_id": result["workspace_id"],
                "item_read": result["item_read"],
                "pipeline": result["pipeline"],
                "copy_job": result["copy_job"],
                "spark_job": result["spark_job"],
                "verification_status": "VERIFIED",
                "certification_result": "NOT_RUN",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
