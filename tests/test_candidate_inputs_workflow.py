from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_CERTIFICATION_FRAMEWORK_SHA = "abc8b3a2b80b3f6babf88fdc2347a3bfe69be356"
CUSTOMER_PR12_MERGE_SHA = "9ddc11405de329fb647fb21b1217d1015e0fa3f5"


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


def test_certification_contract_tracks_current_framework_code_baseline_only():
    workflow = (ROOT / ".github/workflows/certification-contract.yml").read_text()
    assert f"CERTIFICATION_FRAMEWORK_SHA: {CURRENT_CERTIFICATION_FRAMEWORK_SHA}" in workflow
    assert "689bc1097474b26866af8675e32592e4cf65fa1f" not in workflow
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
    combined = source + driver
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


def test_current_status_cannot_regress_from_merged_candidate_input_baseline():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    assert "MERGED + MAIN CI PROVEN — PR #10" in status
    assert "cda90f1c02fc9606aa64d2d1bd13f2ab89628aab" in status
    assert "fabric-data-framework==0.3.0" in status
    assert CURRENT_CERTIFICATION_FRAMEWORK_SHA in status
    assert "PR CI PROVEN / PENDING MERGE — PR #10" not in status
    assert "IMPLEMENTED ON FEATURE BRANCH; CI/PR PROOF PENDING" not in status
    assert "control_plane_external_evidence_incomplete" in status
    assert "warehouse_real_fault_controller_not_configured" in status


def test_current_status_locks_merged_pr12_cross_repo_recovery_baseline():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    assert "New-conversation recovery checkpoint" in status
    assert "MERGED + MAIN CI PROVEN — PR #12" in status
    assert CUSTOMER_PR12_MERGE_SHA in status
    assert "33363980824 SUCCESS" in status
    assert "33363980826 SUCCESS" in status
    assert "33364050484 SUCCESS" in status
    assert "33364050481 SUCCESS" in status
    assert "14 passed" in status
    assert "abc8b3a2b80b3f6babf88fdc2347a3bfe69be356" in status
    assert "4006afb409c81c5510690c8c4dbeadd5e002fd0b" in status
    assert "15" in status
    assert "candidate frozen             false" in status
    assert "selected-candidate Customer input artifact   not retained" in status


def test_first_company_fabric_test_recovery_context_is_locked():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    wrapper = ROOT / "docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md"
    certification_runbook = ROOT / "docs/runbooks/CERTIFY_FRAMEWORK_0_4.md"

    assert wrapper.is_file()
    assert certification_runbook.is_file()
    for token in (
        "303683729c4915d78200d463a6def01c8de9eae6",
        "33381666892",
        "9753976212",
        "0638c95c19ebcc43ec4ec462b7f960a164209874223517e3f74b951264b0eaf6",
        "TEST_FRAMEWORK_IN_COMPANY_FABRIC.md",
        "first company-Fabric test executed            yes — bounded PASS/NOT_RUN result",
        "manual Notebook certification                 CERTIFIED",
        "manual Admin Override                         not used",
        "manual release authorization                  false",
        "release_allowed                    false",
        "Framework exact candidate                    not frozen",
        "Customer production pin                       fabric-data-framework==0.3.0",
    ):
        assert token in status

    wrapper_text = wrapper.read_text()
    assert "candidate-capable, not frozen" in wrapper_text
    assert "warehouse.commit = NOT_RUN" in wrapper_text
    assert "warehouse.ambiguous_commit = NOT_RUN" in wrapper_text
    assert "Dropdowns **record what you observed**" in wrapper_text
    assert "Authorize exact-candidate release = OFF" in wrapper_text
    assert "admin override                     false" in wrapper_text
    assert "release authorized                 false" in wrapper_text

    certification_text = certification_runbook.read_text()
    assert "Lane A — bounded company-Fabric Notebook validation" in certification_text
    assert "Lane B — full evidence-based release certification" in certification_text
    assert "not the current Framework main code baseline" in certification_text


def test_pr17_merged_main_recovery_checkpoint_is_retained():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    assert "Customer PR #17" in status
    assert "0e128380e6b4ed54d4f192e0676da397177f6e2f" in status
    assert "33382409587 SUCCESS" in status
    assert "33382409601 SUCCESS" in status
    assert "33382529532 SUCCESS" in status
    assert "33382529539 SUCCESS" in status
    assert "33382034631 SUCCESS" in status
    assert "production Framework dependency fabric-data-framework==0.3.0" in status
