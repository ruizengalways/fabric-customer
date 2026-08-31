from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "certification"))

from review_binding import load_control_plane_review_binding  # noqa: E402


PLACEHOLDER = (
    ROOT
    / "certification/project/config/certification/integration"
    / "control-plane-external-evidence-review.json"
)


def _write(tmp_path: Path, **updates) -> Path:
    value = {
        "environment": "DEV",
        "control_plane_profile": "fabric_sql_database_v1",
        "review_record_reference": "ticket:SEC-1234",
        "evidence_set_reference": "catalog:control-plane-dev-20260831",
        "reviewed_at_utc": "2026-08-31T07:00:00Z",
    }
    value.update(updates)
    path = tmp_path / "review.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_source_controlled_placeholder_is_intentionally_not_complete():
    binding = load_control_plane_review_binding(PLACEHOLDER)

    assert binding.complete is False
    assert (
        binding.matches(
            environment="DEV",
            control_plane_profile="fabric_sql_database_v1",
        )
        is False
    )


def test_complete_review_binding_matches_only_exact_environment_and_profile(tmp_path):
    binding = load_control_plane_review_binding(_write(tmp_path))

    assert binding.complete is True
    assert binding.matches(
        environment="DEV",
        control_plane_profile="fabric_sql_database_v1",
    )
    assert not binding.matches(
        environment="UAT",
        control_plane_profile="fabric_sql_database_v1",
    )
    assert not binding.matches(
        environment="DEV",
        control_plane_profile="azure_sql_database_v1",
    )


def test_review_binding_rejects_unstructured_or_secret_like_references(tmp_path):
    with pytest.raises(ValueError, match="opaque reference"):
        load_control_plane_review_binding(
            _write(
                tmp_path,
                review_record_reference="https://example.test/review?token=secret",
            )
        )


def test_review_binding_requires_explicit_utc_timestamp(tmp_path):
    with pytest.raises(ValueError, match="explicit UTC offset"):
        load_control_plane_review_binding(
            _write(tmp_path, reviewed_at_utc="2026-08-31T07:00:00")
        )


def test_review_binding_schema_is_fail_closed(tmp_path):
    value = json.loads(_write(tmp_path).read_text(encoding="utf-8"))
    value["unexpected"] = "value"
    path = tmp_path / "unexpected.json"
    path.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(ValueError, match="schema mismatch"):
        load_control_plane_review_binding(path)
