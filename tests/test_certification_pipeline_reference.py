import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
FABRIC_ITEMS = ROOT / "certification/fabric_items"
PIPELINE_TEMPLATE = FABRIC_ITEMS / "pipeline/pipeline-content.template.json"
NOTEBOOK_TEMPLATE = FABRIC_ITEMS / "notebook/certification-pipeline-worker.ipynb"
WORKER_CONFIG = ROOT / "certification/project/config/certification/pipeline-worker.json"
WORKER_SOURCE = (
    ROOT
    / "certification/extensions/src/fabric_customer_certification_extensions/pipeline_worker.py"
)
DRIVER_SOURCE = (
    ROOT
    / "certification/extensions/src/fabric_customer_certification_extensions/business_driver.py"
)
OBSERVER_SOURCE = (
    ROOT
    / "certification/extensions/src/fabric_customer_certification_extensions/business_observer.py"
)
EXTENSION_PYPROJECT = ROOT / "certification/extensions/pyproject.toml"
DEPLOY_RUNBOOK = ROOT / "docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md"

EXACT_DYNAMIC_PARAMETERS = {
    "framework_pipeline_run_id",
    "framework_dataset_run_id",
    "dataset_id",
    "run_mode",
    "attempt",
    "effective_config_hash",
    "execution_plan_hash",
}


def _renderer_module():
    path = FABRIC_ITEMS / "render_fabric_items.py"
    spec = importlib.util.spec_from_file_location("certification_fabric_renderer", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pipeline_template_forwards_exact_framework_parameter_contract():
    value = json.loads(PIPELINE_TEMPLATE.read_text())
    properties = value["properties"]
    assert set(properties["parameters"]) == EXACT_DYNAMIC_PARAMETERS
    assert len(properties["activities"]) == 1
    activity = properties["activities"][0]
    assert activity["type"] == "TridentNotebook"
    parameters = activity["typeProperties"]["parameters"]
    for name in EXACT_DYNAMIC_PARAMETERS:
        assert parameters[name]["value"]["value"] == f"@pipeline().parameters.{name}"
        assert parameters[name]["value"]["type"] == "Expression"
    assert parameters["customer_inputs_root"]["value"] == "__CUSTOMER_INPUTS_ROOT__"
    assert parameters["key_vault_url"]["value"] == "__KEY_VAULT_URL__"
    assert parameters["control_plane_secret_name"]["value"] == "__CONTROL_PLANE_SECRET_NAME__"
    assert parameters["warehouse_secret_name"]["value"] == "__WAREHOUSE_SECRET_NAME__"


def test_worker_notebook_is_parameterized_exact_artifact_execution_not_inline_pip():
    notebook = json.loads(NOTEBOOK_TEMPLATE.read_text())
    parameter_cells = [
        cell
        for cell in notebook["cells"]
        if "parameters" in cell.get("metadata", {}).get("tags", [])
    ]
    assert len(parameter_cells) == 1
    parameter_text = "".join(parameter_cells[0]["source"])
    for name in EXACT_DYNAMIC_PARAMETERS:
        assert f"{name} =" in parameter_text

    source = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    )
    assert "credentials.getSecret" in source
    assert "extension_wheel_sha256" in source
    assert "manifest.artifact_sha256[wheel_name]" in source
    assert "execute_pipeline_child" in source
    assert "pipeline_child_request_from_parameters" in source
    assert "%pip" not in source
    assert "CONTROL_PLANE_DATABASE_URL" in source
    assert "WAREHOUSE_DATABASE_URL" in source


def test_pipeline_worker_config_covers_all_five_live_business_paths():
    value = json.loads(WORKER_CONFIG.read_text())
    assert value["schema_version"] == 1
    assert value["warehouse_database_url_env_var"] == "WAREHOUSE_DATABASE_URL"
    assert set(value["datasets"]) == {
        "cert.full_replace",
        "cert.watermark_scd1",
        "cert.watermark_scd2",
        "cert.retry_idempotency",
        "cert.reconciliation_fail_closed",
    }
    assert value["datasets"]["cert.full_replace"]["success_checkpoint"] == "full-1"
    assert value["datasets"]["cert.retry_idempotency"]["success_checkpoint"] == "retry-1"
    assert (
        value["datasets"]["cert.watermark_scd1"]["success_checkpoint"]
        == "2026-08-31T00:00:00Z"
    )
    assert (
        value["datasets"]["cert.watermark_scd2"]["success_checkpoint"]
        == "2026-08-31T00:00:00Z"
    )


def test_customer_worker_returns_framework_child_result_not_readiness_evidence():
    source = WORKER_SOURCE.read_text()
    assert "FabricPipelineChildResult" in source
    assert "execute_certification_dataset" in source
    assert "ReleaseReadinessStatus" not in source
    assert "IntegrationEvidenceCheckResult" not in source
    assert "CERTIFICATION_RETRYABLE_FAILURE" in source
    assert "RECONCILIATION_FAILED" in source
    assert "apply_scd1" in source
    assert "apply_scd2" in source
    assert "plan_replace" in source
    assert "reconcile_full_replace" in source


def test_business_path_extensions_share_runner_declared_warehouse_runtime():
    driver = DRIVER_SOURCE.read_text()
    observer = OBSERVER_SOURCE.read_text()
    combined = driver + observer
    assert "WAREHOUSE_DATABASE_URL" in driver
    assert "WAREHOUSE_DATABASE_URL" in observer
    assert "BUSINESS_PATH_DRIVER_RUNTIME_JSON" not in combined
    assert "BUSINESS_PATH_OBSERVER_RUNTIME_JSON" not in combined
    assert "ReleaseReadinessStatus" not in combined
    assert "IntegrationEvidenceCheckResult" not in combined

    pyproject = EXTENSION_PYPROJECT.read_text()
    assert (
        '"cert.business-path-observer" = '
        '"fabric_customer_certification_extensions.business_observer:observe_business_path"'
        in pyproject
    )
    assert (
        '"cert.business-path-driver" = '
        '"fabric_customer_certification_extensions.business_driver:drive_business_path"'
        in pyproject
    )


def test_renderer_only_accepts_safe_non_secret_deployment_bindings(tmp_path):
    module = _renderer_module()
    content = module.render_pipeline_content(
        workspace_id="00000000-0000-0000-0000-000000000001",
        notebook_id="00000000-0000-0000-0000-000000000002",
        key_vault_url="https://certification.vault.azure.net/",
        control_plane_secret_name="cert-control-plane-url",
        warehouse_secret_name="cert-warehouse-url",
    )
    rendered = json.dumps(content)
    assert "00000000-0000-0000-0000-000000000001" in rendered
    assert "00000000-0000-0000-0000-000000000002" in rendered
    assert "certification.vault.azure.net" in rendered
    assert "@pipeline().parameters.dataset_id" in rendered
    assert "__" not in rendered

    with pytest.raises(ValueError, match="credential-free HTTPS URL"):
        module.render_pipeline_content(
            workspace_id="00000000-0000-0000-0000-000000000001",
            notebook_id="00000000-0000-0000-0000-000000000002",
            key_vault_url="https://user:password@certification.vault.azure.net/",
            control_plane_secret_name="cert-control-plane-url",
            warehouse_secret_name="cert-warehouse-url",
        )


def test_dedicated_warehouse_ddl_contains_required_certification_tables():
    ddl = (FABRIC_ITEMS / "sql/warehouse-certification-fixtures.sql").read_text()
    for table in (
        "cert_pipeline_control",
        "cert_progress",
        "cert_full_source",
        "cert_full_target",
        "cert_scd1_source",
        "cert_scd1_target",
        "cert_scd2_source",
        "cert_scd2_current",
        "cert_scd2_history",
        "cert_retry_source",
        "cert_retry_target",
        "cert_recon_source",
        "cert_recon_target",
        "cert_copy_landing",
        "cert_spark_landing",
    ):
        assert table in ddl
    assert "DO NOT run this script against a shared or production Warehouse" in ddl


def test_deployment_runbook_is_recoverable_and_does_not_invent_pipeline_semantics():
    text = DEPLOY_RUNBOOK.read_text()
    for name in EXACT_DYNAMIC_PARAMETERS:
        assert name in text
    assert "render_fabric_items.py notebook" in text
    assert "render_fabric_items.py pipeline" in text
    assert "warehouse-certification-fixtures.sql" in text
    assert "allow_control_plane_migration=True" in text
    assert "WAREHOUSE_DATABASE_URL" in text
    assert "BUSINESS_PATH_DRIVER_RUNTIME_JSON" in text  # documented as removed/not required
    assert "Completed" in text
    assert "DatasetDispatchOutcome" in text
    assert "fabric-data-framework==0.3.0" not in text  # deployment runbook is candidate-only
