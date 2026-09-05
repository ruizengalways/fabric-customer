import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
FABRIC_ITEMS = ROOT / "certification/fabric_items"
WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"
NOTEBOOK_ID = "00000000-0000-0000-0000-000000000002"
PIPELINE_ID = "00000000-0000-0000-0000-000000000003"
ITEM_READ_ID = "00000000-0000-0000-0000-000000000011"
COPY_JOB_ID = "00000000-0000-0000-0000-000000000013"
SPARK_JOB_ID = "00000000-0000-0000-0000-000000000014"


def _load_resolver():
    deploy_path = FABRIC_ITEMS / "deploy_fabric_items.py"
    deploy_spec = importlib.util.spec_from_file_location("deploy_fabric_items", deploy_path)
    assert deploy_spec is not None and deploy_spec.loader is not None
    deploy = importlib.util.module_from_spec(deploy_spec)
    sys.modules["deploy_fabric_items"] = deploy
    sys.path.insert(0, str(FABRIC_ITEMS))
    try:
        deploy_spec.loader.exec_module(deploy)
        resolver_path = FABRIC_ITEMS / "resolve_fabric_bindings.py"
        resolver_spec = importlib.util.spec_from_file_location(
            "resolve_fabric_bindings",
            resolver_path,
        )
        assert resolver_spec is not None and resolver_spec.loader is not None
        resolver = importlib.util.module_from_spec(resolver_spec)
        sys.modules["resolve_fabric_bindings"] = resolver
        resolver_spec.loader.exec_module(resolver)
        return resolver
    finally:
        sys.path.remove(str(FABRIC_ITEMS))


def _deployment_result(tmp_path: Path, **updates) -> Path:
    value = {
        "schema_version": 1,
        "environment": "DEV",
        "workspace_id": WORKSPACE_ID,
        "notebook": {
            "id": NOTEBOOK_ID,
            "display_name": "framework-certification-worker",
            "action": "created",
            "definition_sha256": "1" * 64,
        },
        "pipeline": {
            "id": PIPELINE_ID,
            "display_name": "framework-certification-child",
            "action": "created",
            "definition_sha256": "2" * 64,
        },
        "customer_inputs_root": "/lakehouse/default/Files/framework_cert/customer-inputs",
        "contains_secret_values": False,
        "certification_result": "NOT_RUN",
    }
    value.update(updates)
    path = tmp_path / "deployment-result.json"
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return path


class _FakeClient:
    def __init__(self, *, pipeline_id: str = PIPELINE_ID):
        self.pipeline_id = pipeline_id
        self.calls = []

    def find_exact_item(self, workspace_id, *, item_type, display_name):
        self.calls.append((workspace_id, item_type, display_name))
        values = {
            ("Notebook", "framework-certification-worker"): NOTEBOOK_ID,
            ("DataPipeline", "framework-certification-child"): self.pipeline_id,
            ("Lakehouse", "certification-lakehouse"): ITEM_READ_ID,
            ("CopyJob", "framework-certification-copy"): COPY_JOB_ID,
            ("SparkJobDefinition", "framework-certification-spark"): SPARK_JOB_ID,
        }
        item_id = values.get((item_type, display_name))
        if item_id is None:
            return None
        return {
            "id": item_id,
            "type": item_type,
            "displayName": display_name,
            "workspaceId": workspace_id,
        }


def test_resolver_verifies_deployment_and_resolves_remaining_items_by_exact_name(tmp_path):
    module = _load_resolver()
    deployment = _deployment_result(tmp_path)
    result = module.resolve_certification_bindings(
        _FakeClient(),
        deployment_result=deployment,
        item_read_type="Lakehouse",
        item_read_display_name="certification-lakehouse",
        copy_job_display_name="framework-certification-copy",
        spark_job_display_name="framework-certification-spark",
    )

    assert result["verification_status"] == "VERIFIED"
    assert result["environment"] == "DEV"
    assert result["workspace_id"] == WORKSPACE_ID
    assert result["notebook"] == {
        "id": NOTEBOOK_ID,
        "type": "Notebook",
        "display_name": "framework-certification-worker",
    }
    assert result["pipeline"]["id"] == PIPELINE_ID
    assert result["item_read"] == {
        "id": ITEM_READ_ID,
        "type": "Lakehouse",
        "display_name": "certification-lakehouse",
    }
    assert result["copy_job"]["id"] == COPY_JOB_ID
    assert result["spark_job"]["id"] == SPARK_JOB_ID
    assert result["contains_secret_values"] is False
    assert result["certification_result"] == "NOT_RUN"
    assert len(result["deployment_result_sha256"]) == 64
    rendered = json.dumps(result)
    assert "FABRIC_ACCESS_TOKEN" not in rendered
    assert "CONTROL_PLANE_DATABASE_URL" not in rendered
    assert "WAREHOUSE_DATABASE_URL" not in rendered


def test_resolver_fails_when_exact_pipeline_uuid_changed_under_same_display_name(tmp_path):
    module = _load_resolver()
    deployment = _deployment_result(tmp_path)
    with pytest.raises(module.FabricBindingError, match="UUID changed"):
        module.resolve_certification_bindings(
            _FakeClient(pipeline_id="00000000-0000-0000-0000-000000000099"),
            deployment_result=deployment,
            item_read_type="Lakehouse",
            item_read_display_name="certification-lakehouse",
            copy_job_display_name="framework-certification-copy",
            spark_job_display_name="framework-certification-spark",
        )


def test_resolver_rejects_non_deployment_or_secret_claims_before_api_lookup(tmp_path):
    module = _load_resolver()
    secret_claim = _deployment_result(tmp_path, contains_secret_values=True)
    with pytest.raises(module.FabricBindingError, match="contains_secret_values=false"):
        module.resolve_certification_bindings(
            _FakeClient(),
            deployment_result=secret_claim,
            item_read_type="Lakehouse",
            item_read_display_name="certification-lakehouse",
            copy_job_display_name="framework-certification-copy",
            spark_job_display_name="framework-certification-spark",
        )

    certified_claim = _deployment_result(tmp_path, certification_result="PASS")
    with pytest.raises(module.FabricBindingError, match="certification_result=NOT_RUN"):
        module.resolve_certification_bindings(
            _FakeClient(),
            deployment_result=certified_claim,
            item_read_type="Lakehouse",
            item_read_display_name="certification-lakehouse",
            copy_job_display_name="framework-certification-copy",
            spark_job_display_name="framework-certification-spark",
        )


def test_resolver_requires_simple_item_type_and_exact_existing_names(tmp_path):
    module = _load_resolver()
    deployment = _deployment_result(tmp_path)
    with pytest.raises(module.FabricBindingError, match="simple Fabric item type"):
        module.resolve_certification_bindings(
            _FakeClient(),
            deployment_result=deployment,
            item_read_type="Lakehouse&continuationToken=bad",
            item_read_display_name="certification-lakehouse",
            copy_job_display_name="framework-certification-copy",
            spark_job_display_name="framework-certification-spark",
        )

    with pytest.raises(module.FabricBindingError, match="required Fabric item was not found"):
        module.resolve_certification_bindings(
            _FakeClient(),
            deployment_result=deployment,
            item_read_type="Lakehouse",
            item_read_display_name="missing-lakehouse",
            copy_job_display_name="framework-certification-copy",
            spark_job_display_name="framework-certification-spark",
        )
