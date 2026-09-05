from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pr27_enterprise_topology_is_merged_main_ci_proven():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text(encoding="utf-8")
    for token in (
        "Customer PR #27 is **MERGED + MAIN CI PROVEN**",
        "fa495fce622de8a5344bf74ecc52885fe85596f4",
        "33998332579 SUCCESS",
        "33998332576 SUCCESS",
        "33998361497 SUCCESS",
        "33998361592 SUCCESS",
        "3bd3375b796531e5ca6c7e144e7f50e154cec29f",
        "fabric_sql_database_v1",
        "Fabric SQL Database",
        "Warehouse",
    ):
        assert token in status


def test_pr27_checkpoint_keeps_production_pin_and_live_evidence_honest():
    status = (ROOT / "docs/CURRENT_STATUS.md").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "fabric-data-framework==0.3.0" in pyproject
    assert "current_pr109_real_fabric_certification_executed = false" in status
    assert "repository_owned_certification_notebook_deployed = false / not yet evidenced" in status
    assert "repository_owned_certification_pipeline_deployed = false / not yet evidenced" in status
    assert "candidate_status: not_frozen" in status
    assert "release_allowed: false" in status
