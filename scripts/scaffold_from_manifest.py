"""Deterministically scaffold DatasetConfig JSON files from an enterprise onboarding CSV.

This is domain-repository tooling, not the Fabric runtime. It intentionally uses only the
Python standard library so a jumpbox can validate an intake manifest before the framework
wheel or Fabric access is available.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import sys

SUPPORTED_CAPTURE = {"FULL", "WATERMARK", "CDC", "MIRROR", "STREAM", "SNAPSHOT"}
SUPPORTED_APPLY = {"APPEND", "REPLACE", "UPSERT", "SCD1", "SCD2", "SNAPSHOT_DIFF"}
SUPPORTED_CRITICALITY = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
STATEFUL_APPLY = {"UPSERT", "SCD1", "SCD2", "SNAPSHOT_DIFF"}
REQUIRED_COLUMNS = {
    "dataset_id",
    "source_system",
    "source_object",
    "connection_ref",
    "target_object",
    "capture_strategy",
    "apply_strategy",
    "primary_key",
    "watermark_column",
    "event_time_column",
    "tracked_columns",
    "delete_policy",
    "execution_group",
    "criticality",
}


def _split_columns(raw: str) -> list[str]:
    return [item.strip() for item in raw.split("|") if item.strip()]


def _required(row: dict[str, str], field: str, line_number: int) -> str:
    value = (row.get(field) or "").strip()
    if not value:
        raise ValueError(f"line {line_number}: {field} is required")
    return value


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("manifest has no header")
        missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames))
        if missing:
            raise ValueError("manifest missing columns: " + ", ".join(missing))

        rows: list[dict[str, str]] = []
        dataset_ids: set[str] = set()
        for line_number, raw in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw.items()}
            dataset_id = _required(row, "dataset_id", line_number)
            if dataset_id in dataset_ids:
                raise ValueError(f"line {line_number}: duplicate dataset_id {dataset_id!r}")
            dataset_ids.add(dataset_id)

            _required(row, "source_system", line_number)
            _required(row, "source_object", line_number)
            _required(row, "target_object", line_number)
            _required(row, "execution_group", line_number)

            capture = _required(row, "capture_strategy", line_number).upper()
            apply = _required(row, "apply_strategy", line_number).upper()
            criticality = (row["criticality"] or "MEDIUM").upper()
            if capture not in SUPPORTED_CAPTURE:
                raise ValueError(
                    f"line {line_number}: unsupported capture_strategy {capture!r}"
                )
            if apply not in SUPPORTED_APPLY:
                raise ValueError(
                    f"line {line_number}: unsupported apply_strategy {apply!r}"
                )
            if criticality not in SUPPORTED_CRITICALITY:
                raise ValueError(
                    f"line {line_number}: unsupported criticality {criticality!r}"
                )

            keys = _split_columns(row["primary_key"])
            if apply in STATEFUL_APPLY and not keys:
                raise ValueError(
                    f"line {line_number}: {apply} requires at least one primary_key"
                )
            if capture == "WATERMARK":
                if not row["watermark_column"]:
                    raise ValueError(
                        f"line {line_number}: WATERMARK requires watermark_column"
                    )
                if not keys:
                    raise ValueError(
                        f"line {line_number}: WATERMARK scaffold requires primary_key "
                        "for deterministic tie-breaker ordering"
                    )

            row["capture_strategy"] = capture
            row["apply_strategy"] = apply
            row["criticality"] = criticality
            rows.append(row)

    if not rows:
        raise ValueError("manifest contains no datasets")
    return rows


def build_dataset_config(row: dict[str, str]) -> dict:
    keys = _split_columns(row["primary_key"])
    capture = row["capture_strategy"]
    apply = row["apply_strategy"]

    load: dict = {
        "capture_strategy": capture,
        "apply_strategy": apply,
        "business_key": keys if apply == "SCD2" else [],
        "merge_key": keys if apply in STATEFUL_APPLY else [],
        "event_time_column": row["event_time_column"] or None,
        "tracked_columns": _split_columns(row["tracked_columns"]),
        "delete_policy": row["delete_policy"] or "IGNORE",
    }
    if capture == "WATERMARK":
        load["watermark"] = {
            "column": row["watermark_column"],
            "tie_breaker": keys,
            "overlap_window_seconds": 0,
        }

    if capture == "FULL":
        reconciliation_policy = "full_snapshot_count"
    elif capture == "CDC":
        reconciliation_policy = "cdc_checkpoint"
    else:
        reconciliation_policy = "incremental_checkpoint"

    return {
        "dataset_id": row["dataset_id"],
        "source": {
            "system": row["source_system"],
            "object": row["source_object"],
            "connection_ref": row["connection_ref"] or None,
        },
        "target": {
            "layer": "silver",
            "object": row["target_object"],
        },
        "load": load,
        "orchestration": {
            "execution_group": row["execution_group"],
            "criticality": row["criticality"] or "MEDIUM",
            "dependencies": [],
            "priority": 100,
            "retry_count": 2,
            "timeout_seconds": 3600,
            "batch_size": 100000,
            "max_concurrency": 4,
        },
        "quality": {
            "policy_name": "standard",
            "quarantine_policy": "row",
        },
        "reconciliation": {
            "policy_name": reconciliation_policy,
            "required_for_state_commit": True,
        },
        "enabled": True,
        "config_schema_version": 1,
    }


def summarize(rows: list[dict[str, str]]) -> str:
    capture = Counter(row["capture_strategy"] for row in rows)
    apply = Counter(row["apply_strategy"] for row in rows)
    groups = Counter(row["execution_group"] for row in rows)

    def render(counter: Counter[str]) -> str:
        return ", ".join(f"{key}={counter[key]}" for key in sorted(counter))

    return (
        f"datasets={len(rows)}\n"
        f"capture: {render(capture)}\n"
        f"apply: {render(apply)}\n"
        f"execution_groups: {render(groups)}"
    )


def write_configs(rows: list[dict[str, str]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for row in rows:
        dataset_id = row["dataset_id"]
        path = output_dir / f"{dataset_id}.json"
        payload = build_dataset_config(row)
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and optionally scaffold DatasetConfig JSON from a CSV manifest."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write generated JSON files. Without this flag the command is a dry-run.",
    )
    parser.add_argument(
        "--expect-count",
        type=int,
        help="Fail if the manifest dataset count differs from this value.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    rows = load_manifest(args.manifest)
    if args.expect_count is not None and len(rows) != args.expect_count:
        raise ValueError(
            f"expected {args.expect_count} datasets but manifest contains {len(rows)}"
        )

    print(summarize(rows))
    if args.write:
        write_configs(rows, args.output)
        print(f"wrote={len(rows)} output={args.output}")
    else:
        print("dry_run=true no_files_written=true")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f"bulk onboarding failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
