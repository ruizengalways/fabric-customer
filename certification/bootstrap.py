"""One-command, fail-closed bootstrap for repository-owned Fabric certification.

Preparation stops at READY / NOT_RUN. Live certification mutations, candidate freeze,
and release authorization remain separate explicit gates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

CERT_ROOT = Path(__file__).resolve().parent
FABRIC_ITEMS_ROOT = CERT_ROOT / "fabric_items"
sys.path.insert(0, str(CERT_ROOT))
sys.path.insert(0, str(FABRIC_ITEMS_ROOT))

from bootstrap_identity import (
    REPO_ROOT,
    BootstrapError,
    _load_framework_pin,
    _prepare_certification_venv,
    _require_exact_customer_main,
    _verify_and_download_framework,
)
from environment_config import default_config_path, load_environment_config
from fabric_bootstrap_support import (
    _bound_notebook_payload,
    _build_customer_inputs,
    _deploy_notebook,
    _deploy_pipeline,
    _item_id,
    _lakehouse_properties,
    _resolve_definition_item,
    _resolve_resource,
    _resource_result,
    _run_seed_job,
    _run_sql_bootstrap,
    _sql_database_target,
    _stage_exact_bytes,
    _warehouse_target,
)
from deploy_fabric_items import (
    FabricApiClient,
    RUNTIME_AUTH_FABRIC_USER,
    _azure_cli_access_token,
)
from provider_definitions import (
    capture_spark_job_payload,
    copy_job_payload,
    seed_spark_job_payload,
)
from render_fabric_items import DEFAULT_INPUTS_ROOT, render_pipeline_create_payload

WORKER_NOTEBOOK = FABRIC_ITEMS_ROOT / "notebook" / "certification-pipeline-worker.ipynb"
RUNNER_NOTEBOOK = FABRIC_ITEMS_ROOT / "notebook" / "certification-runner.ipynb"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="certification-bootstrap")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--environment", choices=("DEV", "UAT"), required=True)
    parser.add_argument("--config", type=Path)
    return parser


def bootstrap(environment: str, *, config_path: Path | None = None) -> dict[str, object]:
    config_file = config_path or default_config_path(environment)
    config = load_environment_config(config_file, expected_environment=environment)
    customer_sha = _require_exact_customer_main()
    pin = _load_framework_pin()

    build_root = REPO_ROOT / "build" / "certification-bootstrap" / config.environment
    if build_root.exists():
        shutil.rmtree(build_root)
    build_root.mkdir(parents=True)
    framework_dir = build_root / "framework-artifact"
    framework = _verify_and_download_framework(pin, framework_dir)
    framework_wheel = framework_dir / str(framework["wheel_filename"])
    venv_python, extension_wheel = _prepare_certification_venv(build_root, framework_wheel)

    fabric_token = _azure_cli_access_token()
    client = FabricApiClient(fabric_token)
    workspace = config.workspace_id
    resources: dict[str, object] = {}

    lakehouse, lakehouse_action = _resolve_resource(
        client,
        workspace_id=workspace,
        item_type="Lakehouse",
        config=config.lakehouse,
        create_path=f"workspaces/{workspace}/lakehouses",
        create_payload={
            "displayName": config.lakehouse.display_name,
            "description": "Dedicated schema-enabled Framework certification Lakehouse.",
            "creationPayload": {"enableSchemas": True},
        },
    )
    lakehouse_id = _item_id(lakehouse, "Lakehouse")
    _lakehouse_properties(client, workspace, lakehouse_id)
    resources["lakehouse"] = _resource_result(lakehouse, lakehouse_action)

    control, control_action = _resolve_resource(
        client,
        workspace_id=workspace,
        item_type="SQLDatabase",
        config=config.control_plane,
        create_path=f"workspaces/{workspace}/sqlDatabases",
        create_payload={
            "displayName": config.control_plane.display_name,
            "description": "Dedicated Framework certification Control Plane.",
        },
    )
    control_id = _item_id(control, "SQLDatabase")
    control_server, control_database = _sql_database_target(client, workspace, control_id)
    resources["control_plane"] = _resource_result(control, control_action)

    warehouse, warehouse_action = _resolve_resource(
        client,
        workspace_id=workspace,
        item_type="Warehouse",
        config=config.warehouse,
        create_path=f"workspaces/{workspace}/warehouses",
        create_payload={
            "displayName": config.warehouse.display_name,
            "description": "Dedicated disposable Framework certification Warehouse.",
        },
    )
    warehouse_id = _item_id(warehouse, "Warehouse")
    warehouse_server, warehouse_database = _warehouse_target(
        client,
        workspace,
        warehouse_id,
        config.warehouse.display_name,
    )
    resources["warehouse"] = _resource_result(warehouse, warehouse_action)

    copy_payload = copy_job_payload(
        display_name=config.copy_job.display_name,
        workspace_id=workspace,
        lakehouse_id=lakehouse_id,
    )
    copy_item, copy_action, copy_sha = _resolve_definition_item(
        client,
        workspace_id=workspace,
        item_type="CopyJob",
        config=config.copy_job,
        payload=copy_payload,
    )
    copy_id = _item_id(copy_item, "CopyJob")
    resources["copy_job"] = {**_resource_result(copy_item, copy_action), "definition_sha256": copy_sha}

    spark_payload = capture_spark_job_payload(
        display_name=config.spark_job.display_name,
        workspace_id=workspace,
        lakehouse_id=lakehouse_id,
    )
    spark_item, spark_action, spark_sha = _resolve_definition_item(
        client,
        workspace_id=workspace,
        item_type="SparkJobDefinition",
        config=config.spark_job,
        payload=spark_payload,
    )
    spark_id = _item_id(spark_item, "SparkJobDefinition")
    resources["spark_job"] = {**_resource_result(spark_item, spark_action), "definition_sha256": spark_sha}

    seed_payload = seed_spark_job_payload(
        display_name=config.seed_spark_job.display_name,
        workspace_id=workspace,
        lakehouse_id=lakehouse_id,
    )
    seed_item, seed_action, seed_sha = _resolve_definition_item(
        client,
        workspace_id=workspace,
        item_type="SparkJobDefinition",
        config=config.seed_spark_job,
        payload=seed_payload,
    )
    seed_id = _item_id(seed_item, "Seed SparkJobDefinition")
    resources["seed_spark_job"] = {
        **_resource_result(seed_item, seed_action),
        "definition_sha256": seed_sha,
    }

    worker_payload = _bound_notebook_payload(
        template=WORKER_NOTEBOOK,
        display_name=config.worker_notebook.display_name,
        workspace_id=workspace,
        lakehouse_id=lakehouse_id,
        lakehouse_name=config.lakehouse.display_name,
    )
    worker, worker_action, worker_sha = _deploy_notebook(
        client,
        workspace_id=workspace,
        config=config.worker_notebook,
        payload=worker_payload,
    )
    worker_id = _item_id(worker, "worker Notebook")
    resources["worker_notebook"] = {
        **_resource_result(worker, worker_action),
        "definition_sha256": worker_sha,
    }

    pipeline_payload = render_pipeline_create_payload(
        display_name=config.child_pipeline.display_name,
        workspace_id=workspace,
        notebook_id=worker_id,
        runtime_auth_mode=RUNTIME_AUTH_FABRIC_USER,
        control_plane_server=control_server,
        control_plane_database=control_database,
        warehouse_server=warehouse_server,
        warehouse_database=warehouse_database,
        customer_inputs_root=DEFAULT_INPUTS_ROOT,
    )
    pipeline, pipeline_action, pipeline_sha = _deploy_pipeline(
        client,
        workspace_id=workspace,
        config=config.child_pipeline,
        payload=pipeline_payload,
    )
    pipeline_id = _item_id(pipeline, "DataPipeline")
    resources["child_pipeline"] = {
        **_resource_result(pipeline, pipeline_action),
        "definition_sha256": pipeline_sha,
    }

    runner_payload = _bound_notebook_payload(
        template=RUNNER_NOTEBOOK,
        display_name=config.runner_notebook.display_name,
        workspace_id=workspace,
        lakehouse_id=lakehouse_id,
        lakehouse_name=config.lakehouse.display_name,
        replacements={
            "__CERTIFICATION_ENVIRONMENT__": config.environment,
            "__CONTROL_PLANE_SERVER__": control_server,
            "__CONTROL_PLANE_DATABASE__": control_database,
            "__WAREHOUSE_SERVER__": warehouse_server,
            "__WAREHOUSE_DATABASE__": warehouse_database,
        },
    )
    runner, runner_action, runner_sha = _deploy_notebook(
        client,
        workspace_id=workspace,
        config=config.runner_notebook,
        payload=runner_payload,
    )
    runner_id = _item_id(runner, "runner Notebook")
    resources["runner_notebook"] = {
        **_resource_result(runner, runner_action),
        "definition_sha256": runner_sha,
    }

    seed_result: dict[str, object] = {"setup_only": True, "status": "NOT_REQUESTED"}
    if config.mutations.seed_provider_sources:
        seed_result = _run_seed_job(client, workspace, seed_id)

    customer_inputs = _build_customer_inputs(
        python=venv_python,
        extension_wheel=extension_wheel,
        build_root=build_root,
        customer_sha=customer_sha,
        framework=framework,
        config=config,
        runner_notebook_id=runner_id,
        pipeline_id=pipeline_id,
        copy_job_id=copy_id,
        spark_job_id=spark_id,
    )
    stage = _stage_exact_bytes(
        config=config,
        lakehouse_id=lakehouse_id,
        framework_artifact=framework_dir,
        customer_inputs=customer_inputs,
    )
    sql = _run_sql_bootstrap(
        python=venv_python,
        build_root=build_root,
        config=config,
        customer_sha=customer_sha,
        framework_version=str(framework["framework_version"]),
        control_plane_server=control_server,
        control_plane_database=control_database,
        warehouse_server=warehouse_server,
        warehouse_database=warehouse_database,
    )

    result = {
        "schema_version": 1,
        "contains_secret_values": False,
        "environment": config.environment,
        "environment_config_fingerprint": config.safe_fingerprint(),
        "workspace_id": workspace,
        "customer_git_sha": customer_sha,
        "framework": {key: value for key, value in framework.items() if key != "wheel_path"},
        "resources": resources,
        "sql_targets": {
            "control_plane": {"server": control_server, "database": control_database},
            "warehouse": {"server": warehouse_server, "database": warehouse_database},
        },
        "seed_provider_sources": seed_result,
        "staging": stage,
        "sql_bootstrap": sql,
        "customer_inputs_root": DEFAULT_INPUTS_ROOT,
        "bootstrap_status": "READY",
        "certification_result": "NOT_RUN",
        "release_authorized": False,
    }
    return result


def main() -> int:
    args = _parser().parse_args()
    build_root = REPO_ROOT / "build" / "certification-bootstrap" / args.environment
    result_path = build_root / "bootstrap-result.json"
    if not args.apply:
        print("error: --apply is required; bootstrap is an explicit DEV/UAT mutation", file=sys.stderr)
        return 2
    try:
        result = bootstrap(args.environment, config_path=args.config)
    except Exception as exc:
        build_root.mkdir(parents=True, exist_ok=True)
        blocked = {
            "schema_version": 1,
            "contains_secret_values": False,
            "environment": args.environment,
            "bootstrap_status": "BLOCKED",
            "certification_result": "NOT_RUN",
            "release_authorized": False,
            "error_type": type(exc).__name__,
            "error": str(exc)[:1000],
        }
        result_path.write_text(json.dumps(blocked, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"certification bootstrap BLOCKED: {exc}", file=sys.stderr)
        print(result_path, file=sys.stderr)
        return 2
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result_path)
    print("bootstrap_status=READY certification_result=NOT_RUN release_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
