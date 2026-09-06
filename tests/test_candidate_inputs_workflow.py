from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_CERTIFICATION_FRAMEWORK_SHA = "17fbbd8ed2afb14771748a25d3e12d9bf63fe986"
WORKFLOW_CERTIFICATION_FRAMEWORK_SHA = CURRENT_CERTIFICATION_FRAMEWORK_SHA
CURRENT_CERTIFICATION_FRAMEWORK_MAIN_CI = "34010629765"
CURRENT_CERTIFICATION_FRAMEWORK_WHEEL_SHA = (
    "0d7d351548712db3293b00a3b8eb968387f573b542d8fe506c9436a1b9b0a834"
)
CURRENT_CERTIFICATION_FRAMEWORK_ARTIFACT_ID = "9982333832"


def test_candidate_input_workflow_is_manual_exact_input_packaging_only():
    workflow = (ROOT / ".github/workflows/candidate-business-path-inputs.yml").read_text()
    assert "workflow_dispatch:" in workflow
    assert "framework-wheel-${CANDIDATE_SHA}" in workflow
    assert "candidate_artifact.py verify" in workflow
    assert "business-path-inputs-${{ github.sha }}" in workflow
    assert "FRAMEWORK_REPO_TOKEN" in workflow
    assert "git merge-base --is-ancestor \"${GITHUB_SHA}\" origin/main" in workflow
    assert "candidate-business-path-run" not in workflow
    assert "candidate-certify" not in workflow
    assert "IntegrationEvidenceStatus.PASS" not in workflow
    assert "ReleaseReadinessStatus.PASS" not in workflow


def test_certification_slice_is_separate_from_released_customer_runtime_pin():
    pyproject = (ROOT / "pyproject.toml").read_text()
    assert "fabric-data-framework==0.3.0" in pyproject
    dataset_dir = ROOT / "certification/project/config/datasets"
    expected = {
        "cert.full_replace.json",
        "cert.watermark_scd1.json",
        "cert.watermark_scd2.json",
        "cert.retry_idempotency.json",
        "cert.reconciliation_fail_closed.json",
        "cert.copy.json",
        "cert.spark.json",
        "cert.warehouse.json",
    }
    assert {path.name for path in dataset_dir.glob("*.json")} == expected


def test_certification_contract_tracks_current_framework_substantive_baseline_only():
    workflow = (ROOT / ".github/workflows/certification-contract.yml").read_text()
    assert f"CERTIFICATION_FRAMEWORK_SHA: {WORKFLOW_CERTIFICATION_FRAMEWORK_SHA}" in workflow
    assert "one-call runtime/Control Plane bootstrap" in workflow
    assert "fail-at-end parent" in workflow
    assert "execution-group policy" in workflow
    assert "canonical enterprise Fabric SQL Database" in workflow
    assert "get_enterprise_fabric_control_plane_profile" in workflow
    assert "assert_enterprise_fabric_control_plane_profile" in workflow
    assert "Fabric-native Entra SQL runtime" in workflow
    assert "Customer production remains" in workflow
    assert "fabric-data-framework==0.3.0" in (ROOT / "pyproject.toml").read_text()


def test_customer_extensions_cannot_author_readiness_status():
    source = (
        ROOT
        / "certification/extensions/src/fabric_customer_certification_extensions/__init__.py"
    ).read_text()
    driver = (
        ROOT
        / "certification/extensions/src/fabric_customer_certification_extensions/business_driver.py"
    ).read_text()
    observer = (
        ROOT
        / "certification/extensions/src/fabric_customer_certification_extensions/business_observer.py"
    ).read_text()
    worker = (
        ROOT
        / "certification/extensions/src/fabric_customer_certification_extensions/pipeline_worker.py"
    ).read_text()
    combined = source + driver + observer + worker
    assert "ReleaseReadinessProofResult" not in combined
    assert "ReleaseReadinessStatus" not in combined
    assert "IntegrationEvidenceCheckResult" not in combined
    assert "example.invalid" in combined


def test_exact_business_path_plan_covers_five_required_gates():
    import json

    plan = json.loads(
        (ROOT / "certification/project/config/certification/business-path-plan.json").read_text()
    )
    assert {entry["gate_id"] for entry in plan["entries"]} == {
        "full.replace",
        "watermark.scd1",
        "watermark.scd2",
        "retry.idempotency",
        "reconciliation.fail_closed",
    }


def test_current_status_is_recoverable_without_legacy_history():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    for token in (
        "GitHub `main` is truth",
        CURRENT_CERTIFICATION_FRAMEWORK_SHA,
        CURRENT_CERTIFICATION_FRAMEWORK_MAIN_CI,
        CURRENT_CERTIFICATION_FRAMEWORK_WHEEL_SHA,
        CURRENT_CERTIFICATION_FRAMEWORK_ARTIFACT_ID,
        "fabric-data-framework==0.3.0",
        "candidate_status: not_frozen",
        "release_allowed: false",
        "fabric_sql_database_v1",
        "Fabric SQL Database",
        "Lakehouse / OneLake",
        "azure-cli",
        "fabric-user",
        "key_vault_required: false",
        "DEPLOY_CERTIFICATION_FABRIC_ITEMS.md",
        "TEST_FRAMEWORK_IN_COMPANY_FABRIC.md",
        "OPERATE_MULTI_TABLE_PIPELINES.md",
        "ENTERPRISE_ENVIRONMENT_TOPOLOGY.md",
    ):
        assert token in status

    for legacy in (
        "Customer PR #25 is **MERGED + MAIN CI PROVEN**",
        "303683729c4915d78200d463a6def01c8de9eae6",
        "33381666892",
        "CERTIFY_FRAMEWORK_0_4.md",
        "merged substantive certification/deployment tooling baseline",
    ):
        assert legacy not in status


def test_current_status_keeps_actual_fabric_deployment_unclaimed():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    assert "repository_owned_certification_notebook_deployed: false" in status
    assert "repository_owned_certification_pipeline_deployed: false" in status
    assert "current_framework_real_fabric_certification_executed: false" in status
    assert "certification_result = NOT_RUN" in status


def test_current_company_fabric_runbook_is_fabric_native_and_fail_closed():
    runbook = (ROOT / "docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md").read_text()
    assert CURRENT_CERTIFICATION_FRAMEWORK_SHA in runbook
    assert CURRENT_CERTIFICATION_FRAMEWORK_WHEEL_SHA in runbook
    assert "azure-cli" in runbook
    assert "fabric-user" in runbook
    assert "Key Vault is optional" in runbook
    assert "from fabric_data_framework.certification import certify" in runbook
    assert "STOP" in runbook
    assert "certification_result = NOT_RUN" in runbook
    assert "fabric-data-framework==0.3.0" in runbook
    assert "DEPLOY_CERTIFICATION_FABRIC_ITEMS.md" in runbook
    assert "export FABRIC_ACCESS_TOKEN" not in runbook
    assert "--key-vault-url" not in runbook
    assert "CERTIFY_FRAMEWORK_0_4.md" not in runbook


def test_current_status_keeps_strict_release_prerequisites_honest():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    assert "control_plane_external_evidence_incomplete" in status
    assert "control_plane_external_evidence_not_review_bound" in status
    assert "warehouse_real_fault_controller_not_configured" in status
    assert "known_strict_required_blockers: 15" in status
    assert "release_allowed: false" in status
    assert "candidate_status: not_frozen" in status
    assert "release_authorized = false" in status
    assert "fabric-data-framework==0.3.0" in status
