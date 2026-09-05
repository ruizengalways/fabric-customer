import base64
import importlib.util
import json
from pathlib import Path
import sys

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

WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"
NOTEBOOK_ID = "00000000-0000-0000-0000-000000000002"
PIPELINE_ID = "00000000-0000-0000-0000-000000000003"
OPERATION_ID = "00000000-0000-0000-0000-000000000004"


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
    raw = base64.b64decode(part["payload"])
    return json.loads(raw)


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

    create_payload = module.render_pipeline_create_payload(
        display_name="framework-certification-child",
        workspace_id=WORKSPACE_ID,
        notebook_id=NOTEBOOK_ID,
        key_vault_url="https://certification.vault.azure.net/",
        control_plane_secret_name="cert-control-plane-url",
        warehouse_secret_name="cert-warehouse-url",
    )
    assert set(create_payload) == {"displayName", "definition"}
    assert "type" not in create_payload

    with pytest.raises(ValueError, match="credential-free HTTPS URL"):
        module.render_pipeline_content(
            workspace_id=WORKSPACE_ID,
            notebook_id=NOTEBOOK_ID,
            key_vault_url="https://user:password@certification.vault.azure.net/",
            control_plane_secret_name="cert-control-plane-url",
            warehouse_secret_name="cert-warehouse-url",
        )


def test_deployer_create_path_binds_real_notebook_id_into_pipeline_and_retains_no_secrets():
    module = _deployer_module()

    class FakeClient:
        def __init__(self):
            self.created_notebook_payload = None
            self.created_pipeline_payload = None
            self.lookups = []

        def find_exact_item(self, workspace_id, *, item_type, display_name):
            self.lookups.append((workspace_id, item_type, display_name))
            return None

        def create_notebook(self, workspace_id, payload):
            self.created_notebook_payload = payload
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
        key_vault_url="https://certification.vault.azure.net/",
        control_plane_secret_name="cert-control-plane-url",
        warehouse_secret_name="cert-warehouse-url",
    )

    assert result["notebook"]["id"] == NOTEBOOK_ID
    assert result["notebook"]["action"] == "created"
    assert result["pipeline"]["id"] == PIPELINE_ID
    assert result["pipeline"]["action"] == "created"
    assert result["contains_secret_values"] is False
    assert result["certification_result"] == "NOT_RUN"
    assert "key_vault_url" not in result
    assert "control_plane_secret_name" not in result
    assert "warehouse_secret_name" not in result

    assert client.created_pipeline_payload is not None
    content = _decode_definition(client.created_pipeline_payload)
    rendered = json.dumps(content)
    assert NOTEBOOK_ID in rendered
    assert WORKSPACE_ID in rendered
    assert "cert-control-plane-url" in rendered
    assert "cert-warehouse-url" in rendered


def test_deployer_update_path_updates_definitions_without_creating_items():
    module = _deployer_module()

    class FakeClient:
        def __init__(self):
            self.notebook_updates = []
            self.pipeline_updates = []

        def find_exact_item(self, workspace_id, *, item_type, display_name):
            if item_type == "Notebook":
                return {
                    "id": NOTEBOOK_ID,
                    "type": "Notebook",
                    "displayName": display_name,
                }
            return {
                "id": PIPELINE_ID,
                "type": "DataPipeline",
                "displayName": display_name,
            }

        def create_notebook(self, *args, **kwargs):
            raise AssertionError("update path must not create Notebook")

        def create_pipeline(self, *args, **kwargs):
            raise AssertionError("update path must not create Pipeline")

        def update_notebook_definition(self, workspace_id, notebook_id, definition):
            self.notebook_updates.append((workspace_id, notebook_id, definition))

        def update_pipeline_definition(self, workspace_id, pipeline_id, definition):
            self.pipeline_updates.append((workspace_id, pipeline_id, definition))

    client = FakeClient()
    result = module.deploy_certification_items(
        client,
        environment="UAT",
        workspace_id=WORKSPACE_ID,
        key_vault_url="https://certification.vault.azure.net/",
        control_plane_secret_name="cert-control-plane-url",
        warehouse_secret_name="cert-warehouse-url",
    )

    assert result["notebook"]["action"] == "updated"
    assert result["pipeline"]["action"] == "updated"
    assert client.notebook_updates[0][0:2] == (WORKSPACE_ID, NOTEBOOK_ID)
    assert client.pipeline_updates[0][0:2] == (WORKSPACE_ID, PIPELINE_ID)
    rendered_pipeline = json.dumps(client.pipeline_updates[0][2])
    assert NOTEBOOK_ID in base64.b64decode(
        client.pipeline_updates[0][2]["parts"][0]["payload"]
    ).decode("utf-8")
    assert "cert-control-plane-url" not in json.dumps(result)
    assert "cert-warehouse-url" not in json.dumps(result)


def test_deployer_rejects_prod_and_duplicate_exact_display_names(monkeypatch):
    module = _deployer_module()

    with pytest.raises(module.FabricDeploymentError, match="restricted to DEV/UAT"):
        module.deploy_certification_items(
            object(),
            environment="PROD",
            workspace_id=WORKSPACE_ID,
            key_vault_url="https://certification.vault.azure.net/",
            control_plane_secret_name="cert-control-plane-url",
            warehouse_secret_name="cert-warehouse-url",
        )

    client = module.FabricApiClient("test-token")
    monkeypatch.setattr(
        client,
        "list_items",
        lambda workspace_id, item_type: [
            {"id": NOTEBOOK_ID, "type": item_type, "displayName": "duplicate"},
            {"id": PIPELINE_ID, "type": item_type, "displayName": "duplicate"},
        ],
    )
    with pytest.raises(module.FabricDeploymentError, match="Multiple Notebook items"):
        client.find_exact_item(
            WORKSPACE_ID,
            item_type="Notebook",
            display_name="duplicate",
        )


def test_deployer_polls_fabric_lro_and_fetches_create_result(monkeypatch):
    module = _deployer_module()
    client = module.FabricApiClient(
        "test-token",
        sleep_fn=lambda seconds: None,
        monotonic_fn=lambda: 0.0,
    )
    responses = iter(
        [
            module.HttpResult(200, {"Retry-After": "1"}, {"status": "Running"}),
            module.HttpResult(200, {}, {"status": "Succeeded"}),
            module.HttpResult(200, {}, {"id": NOTEBOOK_ID, "type": "Notebook"}),
        ]
    )
    calls = []

    def fake_request(method, path_or_url, payload=None):
        calls.append((method, path_or_url, payload))
        return next(responses)

    monkeypatch.setattr(client, "_request", fake_request)
    result = client._wait_operation(
        {"x-ms-operation-id": OPERATION_ID, "Retry-After": "1"},
        expect_result=True,
    )
    assert result["id"] == NOTEBOOK_ID
    assert calls == [
        ("GET", f"operations/{OPERATION_ID}", None),
        ("GET", f"operations/{OPERATION_ID}", None),
        ("GET", f"operations/{OPERATION_ID}/result", None),
    ]


def test_deployer_list_items_follows_same_host_continuation(monkeypatch):
    module = _deployer_module()
    client = module.FabricApiClient("test-token")
    continuation = (
        "https://api.fabric.microsoft.com/v1/workspaces/"
        f"{WORKSPACE_ID}/items?type=Notebook&continuationToken=next"
    )
    responses = iter(
        [
            module.HttpResult(
                200,
                {},
                {
                    "value": [
                        {"id": NOTEBOOK_ID, "type": "Notebook", "displayName": "one"}
                    ],
                    "continuationUri": continuation,
                },
            ),
            module.HttpResult(
                200,
                {},
                {
                    "value": [
                        {"id": PIPELINE_ID, "type": "Notebook", "displayName": "two"}
                    ]
                },
            ),
        ]
    )
    monkeypatch.setattr(client, "_request", lambda method, url, payload=None: next(responses))
    items = client.list_items(WORKSPACE_ID, "Notebook")
    assert [item["displayName"] for item in items] == ["one", "two"]

    with pytest.raises(module.FabricDeploymentError, match="approved API host"):
        client._absolute_url("https://example.com/v1/operations/anything")


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
    assert "deploy_fabric_items.py" in text
    assert "--apply" in text
    assert "FABRIC_ACCESS_TOKEN" in text
    assert "deployment-result.json" in text
    assert "certification_result" in text
    assert "NOT_RUN" in text
    assert "render_fabric_items.py notebook" in text
    assert "render_fabric_items.py pipeline" in text
    assert "warehouse-certification-fixtures.sql" in text
    assert "allow_control_plane_migration=True" in text
    assert "WAREHOUSE_DATABASE_URL" in text
    assert "BUSINESS_PATH_DRIVER_RUNTIME_JSON" in text  # documented as removed/not required
    assert "Completed" in text
    assert "DatasetDispatchOutcome" in text
    assert "fabric-data-framework==0.3.0" not in text  # deployment runbook is candidate-only
