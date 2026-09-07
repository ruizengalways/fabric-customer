"""Materialize deterministic source deliveries and framework-neutral expected truth."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
from typing import Any, Iterable

from .models import SourceEvent
from .scenarios import scenario_catalog


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def reset_scenario(output_root: str | Path) -> Path:
    root = Path(output_root)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    return root


def materialize_scenario(
    output_root: str | Path,
    *,
    through_day: int = 7,
    clean: bool = True,
) -> Path:
    if through_day < 1 or through_day > 7:
        raise ValueError("through_day must be between 1 and 7")
    root = reset_scenario(output_root) if clean else Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []

    for step in scenario_catalog():
        if step.day > through_day:
            break
        label = step.day_label
        _write_json(root / "source_systems/crm/snapshot" / label / "customers.json", list(step.snapshot))
        _write_json(root / "source_systems/crm/incremental" / label / "customer_changes.json", list(step.incremental))
        _write_jsonl(root / "source_systems/crm/cdc" / label / "customer_events.jsonl", (event.as_debezium() for event in step.cdc_events))
        _write_json(root / "expected/current_state" / label / "customers.json", list(step.expected_current))
        _write_json(root / "expected/history" / label / "customer_history.json", list(step.expected_history))
        _write_jsonl(root / "expected/source_events" / label / "customer_events.jsonl", (event.as_dict() for event in step.cdc_events))
        manifest.append({
            "day": step.day,
            "slug": step.slug,
            "description": step.description,
            "schema_version": step.schema_version,
            "event_count": len(step.cdc_events),
            "current_row_count": len(step.expected_current),
        })

    _write_json(root / "scenario-manifest.json", {"seed": 20260907, "through_day": through_day, "steps": manifest})
    return root


def replay_day(output_root: str | Path, day: int) -> Path:
    steps = {step.day: step for step in scenario_catalog()}
    if day not in steps:
        raise ValueError("day must be between 1 and 7")
    step = steps[day]
    root = Path(output_root) / "replays" / step.day_label
    _write_json(root / "customer_changes.json", list(step.incremental))
    _write_jsonl(root / "customer_events.jsonl", (event.as_debezium() for event in step.cdc_events))
    return root
