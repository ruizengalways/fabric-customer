import json
from pathlib import Path

from fabric_customer import customer_mapper, customer_rules, load_customer_config, parse_crm_rows
from fabric_data_framework.execution import execute_watermark_scd2
from fabric_data_framework.repository import InMemoryControlPlane
from fabric_data_framework.scd2 import IS_CURRENT, VALID_FROM, VALID_TO, InMemorySCD2Target


FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name: str):
    return parse_crm_rows(json.loads((FIXTURES / name).read_text(encoding="utf-8")))


def current_by_id(rows):
    return {row["customer_id"]: row for row in rows if row[IS_CURRENT] is True}


def test_customer_vertical_slice_incremental_quarantine_scd2_and_rerun():
    config = load_customer_config()
    control = InMemoryControlPlane()
    control.deploy_dataset(config)
    target = InMemorySCD2Target()

    first = execute_watermark_scd2(
        repository=control,
        target=target,
        dataset_id=config.dataset_id,
        source_rows=fixture("crm_customer_initial.json"),
        rules=customer_rules(),
        mapper=customer_mapper,
    )

    assert first.status.value == "SUCCEEDED"
    assert len(first.bronze) == 3
    assert len(first.quarantined) == 1
    assert first.watermark_after.tie_breaker == ("C003",)
    assert len(first.target_rows) == 2
    assert control.dataset_runs[-1].row_accounting.rows_read == 3
    assert control.dataset_runs[-1].row_accounting.rows_accepted == 2
    assert control.dataset_runs[-1].row_accounting.rows_quarantined == 1
    first_step_names = [step.step_name for step in control.step_runs if step.dataset_run_id == first.dataset_run_id]
    assert first_step_names == [
        "CAPTURE",
        "BRONZE_NORMALIZE",
        "VALIDATE",
        "QUARANTINE",
        "TRANSFORM",
        "APPLY_PLAN",
        "RECONCILE",
        "COMMIT_STATE",
    ]
    first_current = current_by_id(first.target_rows)
    assert first_current["C001"]["name"] == "Alice"
    assert first_current["C001"]["email"] == "alice@example.com"
    assert first_current["C002"]["segment"] == "PREMIUM"

    second = execute_watermark_scd2(
        repository=control,
        target=target,
        dataset_id=config.dataset_id,
        source_rows=fixture("crm_customer_initial.json") + fixture("crm_customer_incremental.json"),
        rules=customer_rules(),
        mapper=customer_mapper,
    )

    assert second.status.value == "SUCCEEDED"
    assert len(second.bronze) == 4
    assert len(second.quarantined) == 1
    assert control.quarantine_batches[-1].reason_code == "SEGMENT_ALLOWED"
    assert second.watermark_before == first.watermark_after
    assert second.watermark_after.tie_breaker == ("C005",)

    rows = second.target_rows
    current = current_by_id(rows)
    assert set(current) == {"C001", "C002", "C004"}
    assert current["C002"]["name"] == "Bob Smith"
    assert current["C002"]["segment"] == "ENTERPRISE"
    assert current["C004"]["name"] == "Dana"

    c001_versions = [row for row in rows if row["customer_id"] == "C001"]
    c002_versions = [row for row in rows if row["customer_id"] == "C002"]
    assert len(c001_versions) == 1, "unchanged attributes must not create a new SCD2 version"
    assert len(c002_versions) == 2
    assert c002_versions[0][VALID_TO] == c002_versions[1][VALID_FROM]

    before_rerun = target.read()
    rerun = execute_watermark_scd2(
        repository=control,
        target=target,
        dataset_id=config.dataset_id,
        source_rows=fixture("crm_customer_initial.json") + fixture("crm_customer_incremental.json"),
        rules=customer_rules(),
        mapper=customer_mapper,
    )
    assert rerun.bronze == ()
    assert target.read() == before_rerun
    assert rerun.watermark_after == second.watermark_after


def test_failed_reconciliation_preserves_customer_target_and_watermark():
    config = load_customer_config()
    control = InMemoryControlPlane()
    control.deploy_dataset(config)
    target = InMemorySCD2Target()

    execute_watermark_scd2(
        repository=control,
        target=target,
        dataset_id=config.dataset_id,
        source_rows=fixture("crm_customer_initial.json"),
        rules=customer_rules(),
        mapper=customer_mapper,
    )
    target_before = target.read()
    watermark_before = control.get_watermark(config.dataset_id)

    failed = execute_watermark_scd2(
        repository=control,
        target=target,
        dataset_id=config.dataset_id,
        source_rows=fixture("crm_customer_initial.json") + fixture("crm_customer_incremental.json"),
        rules=customer_rules(),
        mapper=customer_mapper,
        force_reconciliation_failure=True,
    )

    assert failed.status.value == "FAILED"
    assert target.read() == target_before
    assert control.get_watermark(config.dataset_id) == watermark_before
    assert control.dataset_runs[-1].error_code == "RECONCILIATION_FAILED"
