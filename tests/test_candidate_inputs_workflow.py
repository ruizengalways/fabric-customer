from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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


def test_current_status_cannot_regress_to_unproven_candidate_input_state():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text()
    assert "PR CI PROVEN / PENDING MERGE — PR #10" in status
    assert "33353622482" in status
    assert "33353622537" in status
    assert "12 passed" in status
    assert "IMPLEMENTED ON FEATURE BRANCH; CI/PR PROOF PENDING" not in status
    assert "control_plane_external_evidence_incomplete" in status
    assert "warehouse_real_fault_controller_not_configured" in status
