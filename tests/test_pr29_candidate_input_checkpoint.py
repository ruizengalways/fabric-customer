from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pr29_candidate_input_topology_is_merged_main_ci_proven():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text(encoding="utf-8")
    for token in (
        "Customer PR #29 is **MERGED + MAIN CI PROVEN**",
        "1effd5fe283afeb5b960a87e64638f1674433580",
        "34001442382 SUCCESS",
        "34001442376 SUCCESS",
        "34001481213 SUCCESS",
        "34001481204 SUCCESS",
        "candidate-business-path-inputs.yml",
        "certification/build_candidate_inputs.py",
        "fabric_sql_database_v1",
    ):
        assert token in status


def test_pr29_checkpoint_keeps_live_and_release_boundaries_honest():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "fabric-data-framework==0.3.0" in pyproject
    assert "repository_owned_certification_notebook_deployed = false / not yet evidenced" in status
    assert "repository_owned_certification_pipeline_deployed = false / not yet evidenced" in status
    assert "current_pr109_real_fabric_certification_executed = false" in status
    assert "candidate_status: not_frozen" in status
    assert "release_allowed: false" in status
    assert "profile must be fabric_sql_database_v1" in status
