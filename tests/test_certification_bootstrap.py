import base64
import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "certification"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_bootstrap_python_sources_compile():
    paths = [
        CERT / "bootstrap.py",
        CERT / "bootstrap_identity.py",
        CERT / "fabric_bootstrap_support.py",
        CERT / "environment_config.py",
        CERT / "onelake_staging.py",
        CERT / "sql_bootstrap.py",
        CERT / "fabric_items/provider_definitions.py",
        CERT / "fabric_items/spark/seed.py",
        CERT / "fabric_items/spark/capture.py",
        CERT / "extensions/src/fabric_customer_certification_extensions/lakehouse_capture_observer.py",
        CERT / "extensions/src/fabric_customer_certification_extensions/spark_runtime.py",
    ]
    for path in paths:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")


def test_environment_key_is_not_fabric_environment_and_rejects_template_uuid(tmp_path):
    module = _load_module("cert_environment_config", CERT / "environment_config.py")
    example = CERT / "environments/DEV.example.json"
    with pytest.raises(ValueError, match="all-zero template UUID"):
        module.load_environment_config(example, expected_environment="DEV")

    value = json.loads(example.read_text())
    value["workspace_id"] = "00000000-0000-0000-0000-000000000123"
    path = tmp_path / "DEV.json"
    path.write_text(json.dumps(value))
    config = module.load_environment_config(path, expected_environment="DEV")
    assert config.environment == "DEV"
    assert config.control_plane.display_name == "framework-certification-control"
    assert config.copy_job.display_name == "framework-certification-copy"
    assert len(config.safe_fingerprint()) == 64


def test_repository_owned_copy_and_spark_definitions_are_real_lakehouse_items():
    module = _load_module(
        "cert_provider_definitions",
        CERT / "fabric_items/provider_definitions.py",
    )
    workspace = "00000000-0000-0000-0000-000000000001"
    lakehouse = "00000000-0000-0000-0000-000000000002"
    copy = module.copy_job_payload(
        display_name="framework-certification-copy",
        workspace_id=workspace,
        lakehouse_id=lakehouse,
    )
    assert copy["type"] == "CopyJob"
    content = json.loads(base64.b64decode(copy["definition"]["parts"][0]["payload"]))
    assert content["properties"]["source"]["type"] == "LakehouseTable"
    assert content["properties"]["destination"]["type"] == "LakehouseTable"
    activity = content["activities"][0]["properties"]
    assert activity["source"]["datasetSettings"] == {
        "schema": "dbo",
        "table": "cert_copy_source",
    }
    assert activity["destination"]["datasetSettings"] == {
        "schema": "dbo",
        "table": "cert_copy_landing",
    }
    assert activity["destination"]["tableOption"] == "autoCreate"

    spark = module.capture_spark_job_payload(
        display_name="framework-certification-spark",
        workspace_id=workspace,
        lakehouse_id=lakehouse,
    )
    assert spark["type"] == "SparkJobDefinition"
    assert spark["definition"]["format"] == "SparkJobDefinitionV2"
    parts = {part["path"]: part for part in spark["definition"]["parts"]}
    assert {"SparkJobDefinitionV1.json", "Main/main.py"} <= set(parts)
    definition = json.loads(base64.b64decode(parts["SparkJobDefinitionV1.json"]["payload"]))
    assert definition["executableFile"] == "main.py"
    assert definition["defaultLakehouseArtifactId"] == lakehouse


def test_capture_evidence_observes_lakehouse_and_spark_execution_data_uses_supported_shape():
    pyproject = (CERT / "extensions/pyproject.toml").read_text()
    assert "lakehouse_capture_observer:observe_capture" in pyproject
    assert "spark_runtime:spark_execution_data" in pyproject

    observer = (
        CERT
        / "extensions/src/fabric_customer_certification_extensions/lakehouse_capture_observer.py"
    ).read_text()
    runtime = (
        CERT
        / "extensions/src/fabric_customer_certification_extensions/spark_runtime.py"
    ).read_text()
    spark_job = (CERT / "fabric_items/spark/capture.py").read_text()
    assert "spark.table(request.landing_reference)" in observer
    assert "dbo.cert_spark_run_marker" in observer
    assert '"commandLineArguments"' in runtime
    assert "--payload-b64" in runtime
    assert "dbo.cert_spark_landing" in spark_job
    assert "dbo.cert_spark_run_marker" in spark_job


def test_runner_is_bounded_first_and_never_auto_authorizes_live_mutations():
    notebook = json.loads(
        (CERT / "fabric_items/notebook/certification-runner.ipynb").read_text()
    )
    source = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    )
    assert "from fabric_data_framework.certification import certify" in source
    assert "candidate['wheel_sha256']" in source
    for flag in (
        "allow_control_plane_migration",
        "allow_control_plane_writes",
        "allow_pipeline_execution",
        "allow_capture_execution",
        "allow_warehouse_execution",
        "allow_warehouse_fault_injection",
        "allow_warehouse_session_termination",
        "allow_business_path_execution",
        "allow_scenario_mutation",
    ):
        assert f"{flag}=False" in source
    assert "=True" not in source


def test_bootstrap_contract_is_ready_not_run_and_keeps_production_pin():
    source = (CERT / "bootstrap.py").read_text()
    support = (CERT / "fabric_bootstrap_support.py").read_text()
    assert '"bootstrap_status": "READY"' in source
    assert '"certification_result": "NOT_RUN"' in source
    assert '"release_authorized": False' in source
    assert "--control-plane-server" in support  # internal resolved binding only
    assert "--warehouse-server" in support
    assert "allow_pipeline_execution=True" not in source
    assert "certification_result\": \"PASS" not in source
    assert "fabric-data-framework==0.3.0" in (ROOT / "pyproject.toml").read_text()


def test_framework_executable_pin_and_recovery_docs_are_machine_recoverable():
    pin = json.loads((CERT / "framework-executable.json").read_text())
    assert pin["candidate_git_sha"] == "17fbbd8ed2afb14771748a25d3e12d9bf63fe986"
    assert pin["main_ci_run_id"] == 34010629765
    assert pin["artifact_id"] == 9982333832
    assert pin["wheel_sha256"] == "0d7d351548712db3293b00a3b8eb968387f573b542d8fe506c9436a1b9b0a834"
    assert pin["selected_as_frozen_candidate"] is False
    assert pin["release_authorized"] is False

    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    deploy = (ROOT / "docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md").read_text()
    runbook = (ROOT / "docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md").read_text()
    for text in (status, deploy, runbook):
        assert "python certification/bootstrap.py --apply --environment DEV" in text
        assert "certification_result" in text and "NOT_RUN" in text
    assert "certification/environments/DEV.json" in status
    assert "environment_is_fabric_environment_item: false" in status
