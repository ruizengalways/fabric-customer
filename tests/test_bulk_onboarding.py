from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import subprocess
import sys

from fabric_data_framework.config import DatasetConfig

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "examples" / "enterprise_100_table" / "health_100_tables.csv"
SCRIPT = ROOT / "scripts" / "scaffold_from_manifest.py"


def test_health_100_table_manifest_dry_run_is_non_mutating(tmp_path: Path) -> None:
    output = tmp_path / "configs"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(MANIFEST),
            "--output",
            str(output),
            "--expect-count",
            "100",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "datasets=100" in result.stdout
    assert "CDC=10" in result.stdout
    assert "FULL=50" in result.stdout
    assert "WATERMARK=40" in result.stdout
    assert "REPLACE=50" in result.stdout
    assert "SCD1=20" in result.stdout
    assert "SCD2=20" in result.stdout
    assert "UPSERT=10" in result.stdout
    assert "dry_run=true no_files_written=true" in result.stdout
    assert not output.exists()


def test_health_100_table_manifest_generates_framework_valid_configs(tmp_path: Path) -> None:
    output = tmp_path / "configs"
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(MANIFEST),
            "--output",
            str(output),
            "--expect-count",
            "100",
            "--write",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    paths = sorted(output.glob("*.json"))
    assert len(paths) == 100

    configs = [
        DatasetConfig.model_validate(json.loads(path.read_text(encoding="utf-8")))
        for path in paths
    ]
    assert len({config.dataset_id for config in configs}) == 100

    capture = Counter(config.load.capture_strategy.value for config in configs)
    apply = Counter(config.load.apply_strategy.value for config in configs)

    assert capture == {"FULL": 50, "WATERMARK": 40, "CDC": 10}
    assert apply == {"REPLACE": 50, "SCD2": 20, "SCD1": 20, "UPSERT": 10}

    for config in configs:
        if config.load.capture_strategy.value == "WATERMARK":
            assert config.load.watermark is not None
            assert config.load.watermark.tie_breaker
        if config.load.apply_strategy.value == "SCD2":
            assert config.load.business_key
            assert config.load.merge_key
        if config.load.apply_strategy.value in {"SCD1", "UPSERT"}:
            assert config.load.merge_key


def test_framework_next_generation_adds_semantics_and_debezium_profile(
    tmp_path: Path,
) -> None:
    project = tmp_path / "health"
    output = project / "config" / "datasets"
    selections_path = project / "config" / "capture" / "semantic-selections.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(MANIFEST),
            "--output",
            str(output),
            "--expect-count",
            "100",
            "--framework-next",
            "--semantic-selections-output",
            str(selections_path),
            "--write",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "framework_next=true semantic_contracts=validated" in result.stdout
    assert len(list(output.glob("*.json"))) == 100

    selections = json.loads(selections_path.read_text(encoding="utf-8"))
    assert len(selections) == 100
    patterns = Counter(item["cheatsheet_pattern"] for item in selections)
    assert patterns == {
        "FULL_SNAPSHOT_CURRENT": 50,
        "WATERMARK_CURRENT": 40,
        "FULL_CHANGES_EVENT": 10,
    }
    assert len({item["dataset_id"] for item in selections}) == 100

    for index in range(1, 11):
        path = output / f"health.cdc_{index:03d}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["source"]["system"] == "debezium"
        assert payload["load"]["capture_strategy"] == "CDC"
        assert payload["execution"] == {
            "engine": "EXTERNAL_CDC",
            "progress_owner": "EXTERNAL",
            "capability_profile": "debezium_kafka_v1",
            "apply_engine": "SPARK",
        }


def test_full_replace_can_be_onboarded_without_a_primary_key(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(
        "dataset_id,source_system,source_object,connection_ref,target_object,"
        "capture_strategy,apply_strategy,primary_key,watermark_column,"
        "event_time_column,tracked_columns,delete_policy,execution_group,criticality\n"
        "health.code_set,health_sql,dbo.CodeSet,health_sql_readonly,code_set,"
        "FULL,REPLACE,,,,,APPLY,health_full_refresh,LOW\n",
        encoding="utf-8",
    )
    output = tmp_path / "configs"

    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(manifest),
            "--output",
            str(output),
            "--expect-count",
            "1",
            "--write",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    config = DatasetConfig.model_validate(
        json.loads((output / "health.code_set.json").read_text(encoding="utf-8"))
    )
    assert config.load.capture_strategy.value == "FULL"
    assert config.load.apply_strategy.value == "REPLACE"
    assert config.load.merge_key == ()
    assert config.load.business_key == ()
