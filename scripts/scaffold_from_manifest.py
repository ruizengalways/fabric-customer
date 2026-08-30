"""Deterministically scaffold DatasetConfig JSON files from an enterprise onboarding CSV.

This is domain-repository tooling, not the Fabric runtime. It intentionally uses only the
Python standard library so a jumpbox can validate an intake manifest before the framework
wheel or Fabric access is available.

The default output remains compatible with the released framework v0.3.0 contract.
``--framework-next`` adds source-controlled fields needed to exercise the exact pinned
0.4-development project contract in CI. It does not change the production dependency pin.
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
SUPPORTED_SEMANTIC_PATTERNS = {
    "FULL_SNAPSHOT_CURRENT",
    "FULL_SNAPSHOT_HISTORY",
    "WATERMARK_CURRENT",
    "WATERMARK_LOOKBACK_CURRENT",
    "WATERMARK_LOOKBACK_RAW",
    "WATERMARK_SOFT_DELETE_CURRENT",
    "WATERMARK_LOOKBACK_SOFT_DELETE_RAW",
    "NET_CHANGES_CURRENT",
    "NET_CHANGES_APPEND",
    "FULL_CHANGES_EVENT",
    "FULL_CHANGES_CURRENT_LOSSY",
    "BUSINESS_EVENTS",
    "SNAPSHOT_DIFF_CURRENT",
    "SNAPSHOT_DIFF_APPEND",
}
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

            semantic_pattern = row.get("semantic_pattern", "").upper()
            if semantic_pattern and semantic_pattern not in SUPPORTED_SEMANTIC_PATTERNS:
                raise ValueError(
                    f"line {line_number}: unsupported semantic_pattern {semantic_pattern!r}"
                )

            row["capture_strategy"] = capture
            row["apply_strategy"] = apply
            row["criticality"] = criticality
            row["semantic_pattern"] = semantic_pattern
            rows.append(row)

    if not rows:
        raise ValueError("manifest contains no datasets")
    return rows


def _semantic_pattern(row: dict[str, str]) -> str:
    explicit = row.get("semantic_pattern", "")
    if explicit:
        return explicit

    capture = row["capture_strategy"]
    apply = row["apply_strategy"]
    source_system = row["source_system"].lower()

    if capture == "FULL" and apply == "REPLACE":
        return "FULL_SNAPSHOT_CURRENT"
    if capture == "WATERMARK":
        return "WATERMARK_CURRENT"
    if capture == "CDC" and source_system == "debezium":
        return "FULL_CHANGES_EVENT"
    if capture == "CDC":
        return "NET_CHANGES_CURRENT"
    if capture == "STREAM":
        return "BUSINESS_EVENTS"
    if capture == "SNAPSHOT" and apply == "APPEND":
        return "SNAPSHOT_DIFF_APPEND"
    if capture == "SNAPSHOT":
        return "SNAPSHOT_DIFF_CURRENT"

    raise ValueError(
        f"dataset {row['dataset_id']!r}: no safe default semantic_pattern for "
        f"capture={capture} apply={apply}; add an explicit semantic_pattern column"
    )


def _default_limitations(row: dict[str, str], semantic_pattern: str) -> list[str]:
    explicit = _split_columns(row.get("known_limitations", ""))
    if explicit:
        return explicit
    if semantic_pattern == "FULL_SNAPSHOT_CURRENT":
        return [
            "current-state snapshots do not expose intermediate source changes between snapshots"
        ]
    if semantic_pattern == "WATERMARK_CURRENT":
        return [
            "hard deletes are not observable unless the source exposes an explicit delete signal",
            "history is limited to changes observed by the watermark capture path",
        ]
    if semantic_pattern == "FULL_CHANGES_EVENT":
        return [
            "provider ordering, tombstone/delete handling and replay recovery still require live Debezium/Kafka evidence"
        ]
    return []


def build_semantic_selection(row: dict[str, str]) -> dict:
    semantic_pattern = _semantic_pattern(row)
    return {
        "dataset_id": row["dataset_id"],
        "cheatsheet_pattern": semantic_pattern,
        "rationale": (
            "Generated from the reviewed onboarding manifest; source owner must confirm "
            "this semantic selection before production promotion."
        ),
        "known_limitations": _default_limitations(row, semantic_pattern),
    }


def build_dataset_config(row: dict[str, str], *, framework_next: bool = False) -> dict:
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

    payload: dict = {
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

    if framework_next and row["source_system"].lower() == "debezium":
        if capture != "CDC":
            raise ValueError(
                f"dataset {row['dataset_id']!r}: Debezium source requires CDC capture"
            )
        payload["execution"] = {
            "engine": "EXTERNAL_CDC",
            "progress_owner": "EXTERNAL",
            "capability_profile": "debezium_kafka_v1",
            "apply_engine": "SPARK",
        }

    return payload


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


def write_configs(
    rows: list[dict[str, str]],
    output_dir: Path,
    *,
    framework_next: bool = False,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for row in rows:
        dataset_id = row["dataset_id"]
        path = output_dir / f"{dataset_id}.json"
        payload = build_dataset_config(row, framework_next=framework_next)
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )


def write_semantic_selections(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [build_semantic_selection(row) for row in rows]
    output_path.write_text(
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
    parser.add_argument(
        "--framework-next",
        action="store_true",
        help=(
            "Emit the additional execution contract used by the pinned 0.4-development "
            "compatibility lane. This does not change the production framework pin."
        ),
    )
    parser.add_argument(
        "--semantic-selections-output",
        type=Path,
        help=(
            "Optional path for generated semantic-selections.json. The file is written "
            "only together with --write."
        ),
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
    if args.framework_next:
        # Resolve every semantic selection during dry-run so unsupported/ambiguous
        # combinations fail before any files can be written.
        for row in rows:
            build_semantic_selection(row)
        print("framework_next=true semantic_contracts=validated")

    if args.write:
        write_configs(rows, args.output, framework_next=args.framework_next)
        if args.semantic_selections_output is not None:
            write_semantic_selections(rows, args.semantic_selections_output)
        print(f"wrote={len(rows)} output={args.output}")
        if args.semantic_selections_output is not None:
            print(f"semantic_selections={args.semantic_selections_output}")
    else:
        print("dry_run=true no_files_written=true")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f"bulk onboarding failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
