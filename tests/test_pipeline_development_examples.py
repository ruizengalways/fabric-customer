from __future__ import annotations

import csv
import json
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]
POLICY_ROOT = ROOT / "examples" / "pipeline_development" / "framework_0_4" / "execution-groups"
MANIFEST = ROOT / "examples" / "enterprise_100_table" / "health_100_tables.csv"
EXPECTED_GROUPS = {
    "health_full_refresh",
    "health_scd2",
    "health_scd1",
    "health_debezium",
}


def _production_dependencies() -> list[str]:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    return list(project.get("dependencies", []))


def _manifest_groups() -> dict[str, str]:
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        return {
            row["dataset_id"]: row["execution_group"]
            for row in csv.DictReader(handle)
        }


def test_framework_0_4_pipeline_examples_are_complete_and_safe() -> None:
    assert "fabric-data-framework==0.3.0" in _production_dependencies()

    paths = sorted(POLICY_ROOT.glob("*.json"))
    assert {path.stem for path in paths} == EXPECTED_GROUPS

    manifest_groups = _manifest_groups()
    seen: set[str] = set()
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        group = payload["execution_group"]
        seen.add(group)
        assert group == path.stem
        assert payload["failure_policy"] == "FAIL_AT_END"
        assert isinstance(payload["max_concurrency"], int)
        assert payload["max_concurrency"] > 0

        defaults = payload["quality_defaults"]
        assert defaults["enabled"] is True
        assert defaults["quarantine_enabled"] is True
        assert defaults["quarantine_detail_mode"] == "FULL"
        assert defaults["max_quarantine_rows"] >= 0
        assert 0 <= defaults["max_quarantine_fraction"] <= 1

        for dataset_id, override in payload["dataset_quality_overrides"].items():
            assert dataset_id in manifest_groups
            assert manifest_groups[dataset_id] == group
            if "max_quarantine_rows" in override:
                assert override["max_quarantine_rows"] >= 0
            if "max_quarantine_fraction" in override:
                assert 0 <= override["max_quarantine_fraction"] <= 1

        serialized = path.read_text(encoding="utf-8").lower()
        for forbidden in ("password", "access_token", "secret_value", "signed_url"):
            assert forbidden not in serialized

    assert seen == EXPECTED_GROUPS


def test_pipeline_operations_runbook_is_present_and_fail_closed() -> None:
    text = (ROOT / "docs" / "runbooks" / "OPERATE_MULTI_TABLE_PIPELINES.md").read_text(
        encoding="utf-8"
    )
    for token in (
        "FAIL_AT_END",
        "RETRY",
        "REPLAY",
        "BACKFILL",
        "FULL_REBUILD",
        "UNKNOWN_COMMIT",
        "Debezium",
        "fabric-data-framework==0.3.0",
    ):
        assert token in text
    assert "blind retry" in text
