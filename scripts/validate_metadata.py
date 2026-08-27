"""Dependency-free PR gate for Customer source metadata and dependency pinning."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_FRAMEWORK_VERSION = "0.3.0"
FORBIDDEN_PHYSICAL_KEYS = {"workspace_id", "lakehouse_id", "warehouse_id", "capacity_id"}


def _walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def main() -> int:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = pyproject["project"].get("dependencies", [])
    expected = f"fabric-data-framework=={EXPECTED_FRAMEWORK_VERSION}"
    framework_dependencies = [dep for dep in dependencies if dep.startswith("fabric-data-framework")]
    if framework_dependencies != [expected]:
        raise ValueError(
            f"framework dependency must be exactly {expected!r}; found {framework_dependencies!r}"
        )

    config_paths = sorted((ROOT / "config" / "datasets").glob("*.json"))
    if not config_paths:
        raise ValueError("no Customer dataset metadata found")

    dataset_ids: set[str] = set()
    normalized: list[dict] = []
    for path in config_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        dataset_id = payload.get("dataset_id")
        if not isinstance(dataset_id, str) or not dataset_id:
            raise ValueError(f"{path}: dataset_id is required")
        if dataset_id in dataset_ids:
            raise ValueError(f"duplicate dataset_id: {dataset_id}")
        dataset_ids.add(dataset_id)
        if path.stem != dataset_id:
            raise ValueError(f"{path}: filename must match dataset_id {dataset_id!r}")
        if payload.get("load", {}).get("capture_strategy") == "WATERMARK":
            watermark = payload.get("load", {}).get("watermark") or {}
            if not watermark.get("column"):
                raise ValueError(f"{path}: WATERMARK dataset requires watermark column")
        forbidden = FORBIDDEN_PHYSICAL_KEYS.intersection(_walk_keys(payload))
        if forbidden:
            raise ValueError(
                f"{path}: physical Fabric IDs are forbidden in domain metadata: {sorted(forbidden)}"
            )
        normalized.append(payload)

    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
    source_hash = hashlib.sha256(encoded).hexdigest()
    if not re.fullmatch(r"[0-9a-f]{64}", source_hash):
        raise AssertionError("invalid SHA-256")
    print(
        f"validated datasets={len(normalized)} framework_dependency={expected} "
        f"source_metadata_sha256={source_hash}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"metadata validation failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
