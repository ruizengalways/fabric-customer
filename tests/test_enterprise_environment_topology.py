from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_enterprise_dev_uat_prod_use_same_control_plane_backend_class():
    runbook = (ROOT / "docs/runbooks/ENTERPRISE_ENVIRONMENT_TOPOLOGY.md").read_text(
        encoding="utf-8"
    )
    assert "DEV is not a reduced architecture" in runbook
    assert "control_plane_profile = fabric_sql_database_v1" in runbook
    assert "DEV  -> Fabric SQL Database control plane" in runbook
    assert "UAT  -> Fabric SQL Database control plane" in runbook
    assert "PROD -> Fabric SQL Database control plane" in runbook
    assert "never copy as deployment truth" in runbook


def test_medallion_and_storage_engine_roles_stay_distinct():
    runbook = (ROOT / "docs/runbooks/ENTERPRISE_ENVIRONMENT_TOPOLOGY.md").read_text(
        encoding="utf-8"
    )
    assert "Bronze/Silver/Gold are data maturity layers" in runbook
    assert "Bronze Lakehouse" in runbook
    assert "Silver Lakehouse" in runbook
    assert "Gold Lakehouse OR optional Fabric Warehouse" in runbook
    assert "Warehouse is optional" in runbook
    assert "Why not Lakehouse control tables" in runbook
