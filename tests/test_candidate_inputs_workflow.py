from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_CERTIFICATION_FRAMEWORK_SHA = "4c8ad9994f3800e901c146b919f85454d78f080e"
CURRENT_CUSTOMER_DEPLOYER_SHA = "88d7c3b7b473ad84b5d96aa472293ae24c055c88"
CURRENT_CUSTOMER_OPERATIONS_SHA = "1d70fe26baf3ceef1be7c0b0cd359f330316e0ee"
CURRENT_CUSTOMER_MAIN_CI = "33969382068"
CURRENT_CUSTOMER_MAIN_CERTIFICATION_CI = "33969382063"
HISTORICAL_FIRST_FABRIC_SHA = "303683729c4915d78200d463a6def01c8de9eae6"
HISTORICAL_FIRST_FABRIC_WHEEL_SHA = (
    "0638c95c19ebcc43ec4ec462b7f960a164209874223517e3f74b951264b0eaf6"
)


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
    assert f"CERTIFICATION_FRAMEWORK_SHA: {CURRENT_CERTIFICATION_FRAMEWORK_SHA}" in workflow
    assert "one-call runtime/Control Plane bootstrap" in workflow
    assert "fail-at-end parent" in workflow
    assert "execution-group policy" in workflow
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


def test_current_status_is_recoverable_without_chat_history():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    for token in (
        "New-conversation recovery checkpoint",
        CURRENT_CERTIFICATION_FRAMEWORK_SHA,
        "33968014547",
        "06d4a9ca948693c87a658a34e8c4fccb42439a7f9f67c44985ac726dedb4e04d",
        "9970044954",
        CURRENT_CUSTOMER_DEPLOYER_SHA,
        "33963661173",
        "33963661167",
        "33963703737",
        "33963703747",
        "merged substantive certification/deployment tooling baseline",
        "deploy_fabric_items.py",
        "certification_result = NOT_RUN",
        "fabric-data-framework==0.3.0",
        "candidate_status: not_frozen",
        "release_allowed: false",
        "control_plane_external_evidence_incomplete",
        "warehouse_real_fault_controller_not_configured",
        "DEPLOY_CERTIFICATION_FABRIC_ITEMS.md",
        "OPERATE_MULTI_TABLE_PIPELINES.md",
    ):
        assert token in status


def test_current_status_locks_merged_product_operations_baseline():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    for token in (
        "Customer PR #25 is **MERGED + MAIN CI PROVEN**",
        CURRENT_CUSTOMER_OPERATIONS_SHA,
        "33969274525",
        "33969274509",
        CURRENT_CUSTOMER_MAIN_CI,
        CURRENT_CUSTOMER_MAIN_CERTIFICATION_CI,
        "health_full_refresh.json",
        "health_scd2.json",
        "health_scd1.json",
        "health_debezium.json",
        "FAIL_AT_END",
    ):
        assert token in status


def test_current_status_keeps_actual_fabric_deployment_unclaimed():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    assert "repository_owned_certification_notebook_deployed = false / not yet evidenced" in status
    assert "repository_owned_certification_pipeline_deployed = false / not yet evidenced" in status
    assert "current_pr107_real_fabric_certification_executed = false" in status
    assert "organization-approved Fabric API access token" in status
    assert "run deploy_fabric_items.py once" in status.lower()


def test_historical_first_company_fabric_evidence_remains_exact_and_old_byte_only():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    wrapper = ROOT / "docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md"
    certification_runbook = ROOT / "docs/runbooks/CERTIFY_FRAMEWORK_0_4.md"

    assert wrapper.is_file()
    assert certification_runbook.is_file()
    for token in (
        HISTORICAL_FIRST_FABRIC_SHA,
        "33381666892",
        HISTORICAL_FIRST_FABRIC_WHEEL_SHA,
        "historical",
        "warehouse.commit",
        "NOT_RUN",
        "release authorized",
        "false",
    ):
        assert token in status or token in wrapper.read_text()

    wrapper_text = wrapper.read_text()
    assert "unified real-Fabric certification is the default path" in wrapper_text
    assert "from fabric_data_framework.certification import certify" in wrapper_text
    assert "runtime_environment" in wrapper_text
    assert "allow_live_mutations=True" in wrapper_text
    assert "allow_control_plane_migration=True" in wrapper_text
    assert "release_authorized = false" in wrapper_text
    assert "fabric-data-framework==0.3.0" in wrapper_text
    assert "DEPLOY_CERTIFICATION_FABRIC_ITEMS.md" in wrapper_text
    assert "deploy_fabric_items.py" in wrapper_text

    certification_text = certification_runbook.read_text()
    assert "Lane A — bounded company-Fabric Notebook validation" in certification_text
    assert "Lane B — full evidence-based release certification" in certification_text
    assert "not the current Framework main code baseline" in certification_text


def test_current_status_keeps_strict_release_prerequisites_honest():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    assert "seven" in status.lower() or "7" in status
    assert "control_plane_external_evidence_incomplete" in status
    assert "control_plane_external_evidence_not_review_bound" in status
    assert "warehouse_real_fault_controller_not_configured" in status
    assert "release_allowed: false" in status
    assert "candidate_status: not_frozen" in status
    assert "release_authorized=false" in status or "release_authorized = false" in status
    assert "fabric-data-framework==0.3.0" in status
