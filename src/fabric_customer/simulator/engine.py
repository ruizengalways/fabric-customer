"""Materialize deterministic source deliveries and framework-neutral expected truth."""

from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .scenarios import scenario_catalog


CHECKSUM_FILE = "SHA256SUMS"
WORKLOAD_FILE = "WORKLOAD.json"


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _payload_files(root: Path) -> tuple[Path, ...]:
    excluded = {CHECKSUM_FILE, WORKLOAD_FILE}
    return tuple(
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.relative_to(root).as_posix() not in excluded
    )


def _digest_lines(lines: Iterable[str]) -> str:
    payload = "".join(lines).encode("utf-8")
    return _sha256_bytes(payload)


def _write_integrity_manifest(root: Path, *, through_day: int) -> None:
    entries: list[tuple[str, str]] = []
    for path in _payload_files(root):
        relative = path.relative_to(root).as_posix()
        entries.append((_sha256_file(path), relative))

    checksum_lines = [f"{digest}  {relative}\n" for digest, relative in entries]
    (root / CHECKSUM_FILE).write_text("".join(checksum_lines), encoding="utf-8")

    source_lines = [
        line
        for line, (_, relative) in zip(checksum_lines, entries, strict=True)
        if relative.startswith("source_systems/")
    ]
    truth_lines = [
        line
        for line, (_, relative) in zip(checksum_lines, entries, strict=True)
        if relative.startswith("expected/")
    ]
    _write_json(
        root / WORKLOAD_FILE,
        {
            "schema_version": 1,
            "seed": 20260907,
            "through_day": through_day,
            "tracked_file_count": len(entries),
            "source_digest": _digest_lines(source_lines),
            "truth_digest": _digest_lines(truth_lines),
            "workload_digest": _digest_lines(checksum_lines),
        },
    )


def verify_scenario(output_root: str | Path) -> dict[str, Any]:
    """Verify that a materialized workload still matches its frozen checksums."""

    root = Path(output_root)
    checksum_path = root / CHECKSUM_FILE
    workload_path = root / WORKLOAD_FILE
    if not checksum_path.is_file() or not workload_path.is_file():
        raise FileNotFoundError("scenario integrity files are missing")

    checksum_lines = checksum_path.read_text(encoding="utf-8").splitlines(keepends=True)
    for raw_line in checksum_lines:
        digest, relative = raw_line.rstrip("\n").split("  ", 1)
        candidate = root / relative
        if not candidate.is_file():
            raise ValueError(f"tracked scenario file is missing: {relative}")
        observed = _sha256_file(candidate)
        if observed != digest:
            raise ValueError(f"scenario file checksum mismatch: {relative}")

    workload = json.loads(workload_path.read_text(encoding="utf-8"))
    if workload["tracked_file_count"] != len(checksum_lines):
        raise ValueError("tracked file count does not match checksum manifest")
    if workload["workload_digest"] != _digest_lines(checksum_lines):
        raise ValueError("workload digest does not match checksum manifest")
    return workload


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
        _write_json(
            root / "source_systems/crm/snapshot" / label / "customers.json",
            list(step.snapshot),
        )
        _write_json(
            root / "source_systems/crm/incremental" / label / "customer_changes.json",
            list(step.incremental),
        )
        _write_jsonl(
            root / "source_systems/crm/cdc" / label / "customer_events.jsonl",
            (event.as_debezium() for event in step.cdc_events),
        )
        _write_json(
            root / "expected/current_state" / label / "customers.json",
            list(step.expected_current),
        )
        _write_json(
            root / "expected/history" / label / "customer_history.json",
            list(step.expected_history),
        )
        _write_jsonl(
            root / "expected/source_events" / label / "customer_events.jsonl",
            (event.as_dict() for event in step.cdc_events),
        )
        manifest.append(
            {
                "day": step.day,
                "slug": step.slug,
                "description": step.description,
                "schema_version": step.schema_version,
                "event_count": len(step.cdc_events),
                "current_row_count": len(step.expected_current),
            }
        )

    _write_json(
        root / "scenario-manifest.json",
        {"seed": 20260907, "through_day": through_day, "steps": manifest},
    )
    _write_integrity_manifest(root, through_day=through_day)
    return root


def replay_day(output_root: str | Path, day: int) -> Path:
    steps = {step.day: step for step in scenario_catalog()}
    if day not in steps:
        raise ValueError("day must be between 1 and 7")
    step = steps[day]
    root = Path(output_root) / "replays" / step.day_label
    _write_json(root / "customer_changes.json", list(step.incremental))
    _write_jsonl(
        root / "customer_events.jsonl",
        (event.as_debezium() for event in step.cdc_events),
    )
    return root
