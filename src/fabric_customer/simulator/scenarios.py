"""Canonical deterministic CRM customer scenario.

The catalog describes only what happened in the source system. It deliberately has no
knowledge of bronze/silver, merge, watermark, SCD, retry or audit implementations.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .models import ScenarioStep, SourceEvent


def _ordered(state: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(state[key]) for key in sorted(state))


def _event(
    event_id: str,
    op: str,
    *,
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    source_ts: str,
    delivered_at: str,
    schema_version: int = 1,
) -> SourceEvent:
    row = after or before or {}
    return SourceEvent(
        event_id=event_id,
        source_system="crm",
        table="customer",
        operation=op,
        key={"customer_id": row["customer_id"]},
        before=deepcopy(before),
        after=deepcopy(after),
        source_ts=source_ts,
        delivered_at=delivered_at,
        schema_version=schema_version,
    )


def scenario_catalog() -> tuple[ScenarioStep, ...]:
    state: dict[str, dict[str, Any]] = {}
    history: list[dict[str, Any]] = []
    steps: list[ScenarioStep] = []

    def record(change_type: str, source_ts: str, row: dict[str, Any] | None, customer_id: str) -> None:
        history.append(
            {
                "customer_id": customer_id,
                "change_type": change_type,
                "source_ts": source_ts,
                "values": deepcopy(row),
            }
        )

    c1001 = {
        "customer_id": "C1001",
        "name": "Alice Ng",
        "address": "Sydney",
        "segment": "STANDARD",
        "email": "alice@example.com",
        "modified_at": "2026-09-07T00:00:00Z",
    }
    c1002 = {
        "customer_id": "C1002",
        "name": "Bob Li",
        "address": "Melbourne",
        "segment": "PREMIUM",
        "email": "bob@example.com",
        "modified_at": "2026-09-07T00:00:00Z",
    }
    state.update({"C1001": deepcopy(c1001), "C1002": deepcopy(c1002)})
    record("INITIAL", c1001["modified_at"], c1001, "C1001")
    record("INITIAL", c1002["modified_at"], c1002, "C1002")
    day1_events = (
        _event("crm.customer.C1001.initial", "r", before=None, after=c1001, source_ts=c1001["modified_at"], delivered_at="2026-09-07T01:00:00Z"),
        _event("crm.customer.C1002.initial", "r", before=None, after=c1002, source_ts=c1002["modified_at"], delivered_at="2026-09-07T01:00:00Z"),
    )
    steps.append(ScenarioStep(1, "initial_load", "Initial source snapshot", 1, _ordered(state), _ordered(state), day1_events, _ordered(state), tuple(deepcopy(history))))

    before = deepcopy(state["C1001"])
    state["C1001"].update(address="Melbourne", modified_at="2026-09-08T02:00:00Z")
    after_update = deepcopy(state["C1001"])
    c1003 = {
        "customer_id": "C1003",
        "name": "Carol Tan",
        "address": "Brisbane",
        "segment": "STANDARD",
        "email": "carol@example.com",
        "modified_at": "2026-09-08T03:00:00Z",
    }
    state["C1003"] = deepcopy(c1003)
    record("UPDATE", after_update["modified_at"], after_update, "C1001")
    record("INSERT", c1003["modified_at"], c1003, "C1003")
    day2_events = (
        _event("crm.customer.C1001.update.1", "u", before=before, after=after_update, source_ts=after_update["modified_at"], delivered_at="2026-09-08T04:00:00Z"),
        _event("crm.customer.C1003.insert.1", "c", before=None, after=c1003, source_ts=c1003["modified_at"], delivered_at="2026-09-08T04:00:00Z"),
    )
    steps.append(ScenarioStep(2, "insert_update", "One update and one insert", 1, _ordered(state), (deepcopy(after_update), deepcopy(c1003)), day2_events, _ordered(state), tuple(deepcopy(history))))

    deleted = deepcopy(state.pop("C1002"))
    delete_ts = "2026-09-09T02:00:00Z"
    record("DELETE", delete_ts, None, "C1002")
    day3_events = (_event("crm.customer.C1002.delete.1", "d", before=deleted, after=None, source_ts=delete_ts, delivered_at="2026-09-09T03:00:00Z"),)
    steps.append(ScenarioStep(3, "hard_delete", "Hard delete of C1002", 1, _ordered(state), (), day3_events, _ordered(state), tuple(deepcopy(history))))

    duplicate_row = deepcopy(state["C1003"])
    duplicate_event = _event("crm.customer.C1003.insert.1", "c", before=None, after=duplicate_row, source_ts=duplicate_row["modified_at"], delivered_at="2026-09-10T03:00:00Z")
    steps.append(ScenarioStep(4, "duplicate_delivery", "Duplicate row and duplicate CDC event delivery; source truth is unchanged", 1, _ordered(state), (deepcopy(duplicate_row), deepcopy(duplicate_row)), (duplicate_event, duplicate_event), _ordered(state), tuple(deepcopy(history))))

    before = deepcopy(state["C1001"])
    state["C1001"].update(segment="PREMIUM", modified_at="2026-09-08T12:00:00Z")
    late = deepcopy(state["C1001"])
    record("LATE_UPDATE", late["modified_at"], late, "C1001")
    day5_events = (_event("crm.customer.C1001.late.1", "u", before=before, after=late, source_ts=late["modified_at"], delivered_at="2026-09-11T05:00:00Z"),)
    steps.append(ScenarioStep(5, "late_arrival", "Late-arriving source update with an older source timestamp", 1, _ordered(state), (deepcopy(late),), day5_events, _ordered(state), tuple(deepcopy(history))))

    changed_rows: list[dict[str, Any]] = []
    schema_events: list[SourceEvent] = []
    for customer_id in sorted(state):
        before = deepcopy(state[customer_id])
        state[customer_id]["preferred_language"] = "en-AU"
        state[customer_id]["modified_at"] = "2026-09-12T02:00:00Z"
        after = deepcopy(state[customer_id])
        changed_rows.append(after)
        record("SCHEMA_EVOLUTION", after["modified_at"], after, customer_id)
        schema_events.append(_event(f"crm.customer.{customer_id}.schema-v2", "u", before=before, after=after, source_ts=after["modified_at"], delivered_at="2026-09-12T03:00:00Z", schema_version=2))
    steps.append(ScenarioStep(6, "schema_evolution", "Schema v2 adds preferred_language", 2, _ordered(state), tuple(deepcopy(changed_rows)), tuple(schema_events), _ordered(state), tuple(deepcopy(history))))

    before = deepcopy(state["C1003"])
    state["C1003"].update(address="Gold Coast", modified_at="2026-09-13T02:00:00Z")
    correction = deepcopy(state["C1003"])
    record("SOURCE_CORRECTION", correction["modified_at"], correction, "C1003")
    correction_event = _event("crm.customer.C1003.correction.1", "u", before=before, after=correction, source_ts=correction["modified_at"], delivered_at="2026-09-13T03:00:00Z", schema_version=2)
    steps.append(ScenarioStep(7, "source_correction_replay", "Source correction plus a replayed delivery", 2, _ordered(state), (deepcopy(correction), deepcopy(correction)), (correction_event, correction_event), _ordered(state), tuple(deepcopy(history))))

    return tuple(steps)
