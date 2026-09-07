import base64
import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
FABRIC_ITEMS = ROOT / "certification/fabric"
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

WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"
NOTEBOOK_ID = "00000000-0000-0000-0000-000000000002"
PIPELINE_ID = "00000000-0000-0000-0000-000000000003"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(FABRIC_ITEMS))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(FABRIC_ITEMS))
    return module


def _renderer_module():
    return _load_module(
        "certification_fabric_renderer",
        FABRIC_ITEMS / "render_fabric_items.py",
    )


def _deployer_module():
    return _load_module(
        "certification_fabric_deployer",
        FABRIC_ITEMS / "deploy_fabric_items.py",
    )


def _decode_definition(payload: dict[str, object]) -> dict[str, object]:
    definition = payload["definition"]
    assert isinstance(definition, dict)
    parts = definition["parts"]
    assert isinstance(parts, list) and len(parts) == 1
    part = parts[0]
    assert isinstance(part, dict)
    return json.loads(base64.b64decode(part["payload"]))


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


def test_customer_extensions_return_facts_not_readiness_pass():
    combined = (
        WORKER_SOURCE.read_text()
        + DRIVER_SOURCE.read_text()
        + OBSERVER_SOURCE.read_text()
    )
    assert "FabricPipelineChildResult" in combined
    assert "WAREHOUSE_DATABASE_URL" in combined
    assert "ReleaseReadinessStatus" not in combined
    assert "IntegrationEvidenceCheckResult" not in combined
    assert "BUSINESS_PATH_DRIVER_RUNTIME_JSON" not in combined

    pyproject = EXTENSION_PYPROJECT.read_text()
    assert "cert.business-path-observer" in pyproject
    assert "cert.business-path-driver" in pyproject


def test_renderer_only_accepts_safe_non_secret_deployment_bindings():
    module = _renderer_module()
    content = module.render_pipeline_content(
        workspace_id=WORKSPACE_ID,
        notebook_id=NOTEBOOK_ID,
        key_vault_url="https://certification.vault.azure.net/",
        control_plane_secret_name="cert-control-plane-url",
        warehouse_secret_name="cert-warehouse-url",
    )
    rendered = json.dumps(content)
    assert WORKSPACE_ID in rendered
    assert NOTEBOOK_ID in rendered
    assert "certification.vault.azure.net" in rendered
    assert "@pipeline().parameters.dataset_id" in rendered
    assert "__" not in rendered

    with pytest.raises(ValueError, match="credential-free HTTPS URL"):
        module.render_pipeline_content(
            workspace_id=WORKSPACE_ID,
            notebook_id=NOTEBOOK_ID,
            key_vault_url="https://user:password@certification.vault.azure.net/",
            control_plane_secret_name="cert-control-plane-url",
            warehouse_secret_name="cert-warehouse-url",
        )


def test_deployer_create_path_binds_real_notebook_id_and_retains_no_secrets():
    module = _deployer_module()

    class FakeClient:
        def find_exact_item(self, workspace_id, *, item_type, display_name):
            return None

        def create_notebook(self, workspace_id, payload):
            return {
                "id": NOTEBOOK_ID,
                "type": "Notebook",
                "displayName": payload["displayName"],
            }

        def create_pipeline(self, workspace_id, payload):
            self.created_pipeline_payload = payload
            return {
                "id": PIPELINE_ID,
                "type": "DataPipeline",
                "displayName": payload["displayName"],
            }

        def update_notebook_definition(self, *args, **kwargs):
            raise AssertionError("create path must not update Notebook")

        def update_pipeline_definition(self, *args, **kwargs):
            raise AssertionError("create path must not update Pipeline")

    client = FakeClient()
    result = module.deploy_certification_items(
        client,
        environment="DEV",
        workspace_id=WORKSPACE_ID,
        runtime_auth_mode="fabric-user",
        control_plane_server="cp.database.fabric.microsoft.com",
        control_plane_database="framework_control",
        warehouse_server="wh.datawarehouse.fabric.microsoft.com",
        warehouse_database="framework_cert",
    )

    assert result["notebook"]["id"] == NOTEBOOK_ID
    assert result["pipeline"]["id"] == PIPELINE_ID
    assert result["contains_secret_values"] is False
    assert result["certification_result"] == "NOT_RUN"
    assert "secret_value" not in json.dumps(result).lower()
    content = _decode_definition(client.created_pipeline_payload)
    assert NOTEBOOK_ID in json.dumps(content)


def test_deployer_rejects_prod():
    module = _deployer_module()
    with pytest.raises(module.FabricDeploymentError, match="restricted to DEV/UAT"):
        module.deploy_certification_items(
            object(),
            environment="PROD",
            workspace_id=WORKSPACE_ID,
            runtime_auth_mode="fabric-user",
            control_plane_server="cp.database.fabric.microsoft.com",
            control_plane_database="framework_control",
            warehouse_server="wh.datawarehouse.fabric.microsoft.com",
            warehouse_database="framework_cert",
        )


def test_low_level_recovery_contract_remains_documented_under_new_path():
    text = DEPLOY_RUNBOOK.read_text()
    assert "certification/fabric/deploy_fabric_items.py" in text
    assert "certification/fabric/render_fabric_items.py" in text
    for token in EXACT_DYNAMIC_PARAMETERS:
        assert token in text
    for token in (
        "deployment-result.json",
        "certification_result = NOT_RUN",
        "WAREHOUSE_DATABASE_URL",
        "FABRIC_ACCESS_TOKEN",
    ):
        assert token in text
