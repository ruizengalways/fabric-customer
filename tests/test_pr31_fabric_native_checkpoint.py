from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FRAMEWORK_SHA = "17fbbd8ed2afb14771748a25d3e12d9bf63fe986"
FRAMEWORK_MAIN_CI = "34010629765"
FRAMEWORK_WHEEL_SHA = "0d7d351548712db3293b00a3b8eb968387f573b542d8fe506c9436a1b9b0a834"
FRAMEWORK_ARTIFACT_ID = "9982333832"
CUSTOMER_PR31_MAIN = "b8791ee3f7c575e87d457501ea2e93e40d75fcb6"
CUSTOMER_PR31_CI = "34016083859"
CUSTOMER_PR31_CERT_CI = "34016083851"
CUSTOMER_PR31_MAIN_CI = "34016136469"
CUSTOMER_PR31_MAIN_CERT_CI = "34016136281"
HISTORICAL_PROJECT_CONTRACT_SHA = "148e02e3fff7861f238296e7554815a6fd49dd0a"


def test_pr31_checkpoint_records_current_fabric_native_identity_without_release_claims():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()
    cert_workflow = (ROOT / ".github/workflows/certification-contract.yml").read_text()
    pyproject = (ROOT / "pyproject.toml").read_text()

    for token in (
        "Customer Fabric-native certification/deployment baseline — PR #31",
        CUSTOMER_PR31_MAIN,
        CUSTOMER_PR31_CI,
        CUSTOMER_PR31_CERT_CI,
        CUSTOMER_PR31_MAIN_CI,
        CUSTOMER_PR31_MAIN_CERT_CI,
        FRAMEWORK_SHA,
        FRAMEWORK_MAIN_CI,
        FRAMEWORK_WHEEL_SHA,
        FRAMEWORK_ARTIFACT_ID,
        "azure-cli",
        "fabric-user",
        "Key Vault optional",
        "env-token",
        "repository_owned_certification_notebook_deployed = false / not yet evidenced",
        "repository_owned_certification_pipeline_deployed = false / not yet evidenced",
        "current_pr112_real_fabric_certification_executed = false",
        "candidate_status: not_frozen",
        "release_allowed: false",
    ):
        assert token in status

    assert f"FRAMEWORK_NEXT_SHA: {HISTORICAL_PROJECT_CONTRACT_SHA}" in workflow
    assert f"CERTIFICATION_FRAMEWORK_SHA: {FRAMEWORK_SHA}" in cert_workflow
    assert "fabric-data-framework==0.3.0" in pyproject


def test_pr31_checkpoint_keeps_live_boundary_fail_closed():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    for token in (
        "control_plane_external_evidence_incomplete",
        "control_plane_external_evidence_not_review_bound",
        "warehouse_real_fault_controller_not_configured",
        "real-Fabric result  NOT YET",
        "certification_result = NOT_RUN",
    ):
        assert token in status
