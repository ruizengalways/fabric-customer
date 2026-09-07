import json
from pathlib import Path

import pytest

from fabric_customer.simulator import (
    materialize_scenario,
    replay_day,
    scenario_catalog,
    verify_scenario,
)


def test_scenario_catalog_contains_deterministic_day_1_to_7_truth():
    steps = scenario_catalog()
    assert [step.day for step in steps] == list(range(1, 8))
    assert steps[3].cdc_events[0].event_id == steps[3].cdc_events[1].event_id
    assert steps[4].cdc_events[0].source_ts < steps[4].cdc_events[0].delivered_at
    assert steps[5].schema_version == 2
    final = {row["customer_id"]: row for row in steps[-1].expected_current}
    assert set(final) == {"C1001", "C1003"}
    assert final["C1003"]["address"] == "Gold Coast"
    assert final["C1001"]["preferred_language"] == "en-AU"


def test_materialization_is_reproducible_and_self_attesting(tmp_path: Path):
    left = materialize_scenario(tmp_path / "left")
    right = materialize_scenario(tmp_path / "right")
    left_files = {p.relative_to(left): p.read_bytes() for p in left.rglob("*") if p.is_file()}
    right_files = {p.relative_to(right): p.read_bytes() for p in right.rglob("*") if p.is_file()}
    assert left_files == right_files

    manifest = json.loads((left / "scenario-manifest.json").read_text())
    assert manifest["seed"] == 20260907
    assert manifest["through_day"] == 7

    workload = verify_scenario(left)
    assert workload["seed"] == 20260907
    assert workload["through_day"] == 7
    assert workload["tracked_file_count"] > 0
    assert len(workload["source_digest"]) == 64
    assert len(workload["truth_digest"]) == 64
    assert len(workload["workload_digest"]) == 64


def test_scenario_verification_detects_tampering(tmp_path: Path):
    root = materialize_scenario(tmp_path / "scenario")
    source = root / "source_systems/crm/snapshot/day_01/customers.json"
    source.write_text("[]\n", encoding="utf-8")

    with pytest.raises(ValueError, match="checksum mismatch"):
        verify_scenario(root)


def test_replay_reuses_exact_day_delivery(tmp_path: Path):
    root = materialize_scenario(tmp_path / "scenario")
    replay = replay_day(root, 7)
    original = root / "source_systems/crm/cdc/day_07/customer_events.jsonl"
    assert (replay / "customer_events.jsonl").read_bytes() == original.read_bytes()
