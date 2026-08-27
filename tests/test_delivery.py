from datetime import datetime, timezone
from pathlib import Path

from fabric_customer.metadata import default_customer_config_path, load_customer_config
from fabric_data_framework.delivery import (
    build_release_manifest,
    load_environment_bindings,
    plan_deployment,
)

ROOT = Path(__file__).resolve().parents[1]


def test_same_customer_release_is_planned_for_dev_uat_prod_with_local_bindings():
    config = load_customer_config(default_customer_config_path())
    manifest = build_release_manifest(
        domain="customer",
        domain_release_version="0.1.0",
        domain_git_sha="a" * 40,
        framework_version="0.3.0",
        configs=(config,),
        config_schema_version=1,
        fabric_item_manifest_version="none-v1",
        build_id="customer-build-1",
        generated_at=datetime(2026, 8, 28, tzinfo=timezone.utc),
    )

    plans = [
        plan_deployment(manifest, load_environment_bindings(ROOT / "deploy" / name))
        for name in ("bindings.dev.json", "bindings.uat.json", "bindings.prod.json")
    ]

    assert {plan.release_hash for plan in plans} == {manifest.bundle.release_hash}
    assert [plan.request.target_environment.value for plan in plans] == ["DEV", "UAT", "PROD"]
    assert len({plan.bindings.profile_name for plan in plans}) == 3
    assert all("watermark" in plan.protected_environment_local_state_tables for plan in plans)
