"""Fail-closed review binding for real control-plane external evidence.

This module does not prove that any external evidence is true and never creates a
PASS result. It only requires source-controlled review metadata to bind a complete
external-evidence set to the exact protected certification environment and selected
production-eligible control-plane profile before Customer may call the live
prerequisites configured.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path
import re


_ALLOWED_ENVIRONMENTS = frozenset({"DEV", "UAT", "PROD"})
_ALLOWED_CONTROL_PLANE_PROFILES = frozenset(
    {"fabric_sql_database_v1", "azure_sql_database_v1"}
)
_REQUIRED_KEYS = frozenset(
    {
        "environment",
        "control_plane_profile",
        "review_record_reference",
        "evidence_set_reference",
        "reviewed_at_utc",
    }
)
_SAFE_OPAQUE_REFERENCE = re.compile(
    r"^[A-Za-z][A-Za-z0-9._-]{0,31}:[A-Za-z0-9][A-Za-z0-9._/@-]{0,255}$"
)


@dataclass(frozen=True)
class ControlPlaneEvidenceReviewBinding:
    """Non-secret metadata binding reviewed evidence to one certification target."""

    environment: str | None
    control_plane_profile: str | None
    review_record_reference: str | None
    evidence_set_reference: str | None
    reviewed_at_utc: str | None

    @property
    def complete(self) -> bool:
        return all(
            (
                self.environment,
                self.control_plane_profile,
                self.review_record_reference,
                self.evidence_set_reference,
                self.reviewed_at_utc,
            )
        )

    def matches(self, *, environment: str, control_plane_profile: str) -> bool:
        return (
            self.complete
            and self.environment == environment
            and self.control_plane_profile == control_plane_profile
        )


def _optional_string(value: object, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be null or a non-empty string")
    return value.strip()


def _validate_opaque_reference(value: str | None, *, field_name: str) -> None:
    if value is None:
        return
    if _SAFE_OPAQUE_REFERENCE.fullmatch(value) is None:
        raise ValueError(
            f"{field_name} must be a non-secret opaque reference like 'ticket:SEC-1234'"
        )


def _validate_reviewed_at(value: str | None) -> None:
    if value is None:
        return
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("reviewed_at_utc must be an ISO-8601 timestamp") from exc
    if parsed.utcoffset() is None or parsed.utcoffset() != timedelta(0):
        raise ValueError("reviewed_at_utc must carry an explicit UTC offset")


def load_control_plane_review_binding(
    path: str | Path,
) -> ControlPlaneEvidenceReviewBinding:
    source = Path(path)
    raw = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("control-plane review binding must be a JSON object")
    observed_keys = frozenset(raw)
    if observed_keys != _REQUIRED_KEYS:
        missing = sorted(_REQUIRED_KEYS - observed_keys)
        extra = sorted(observed_keys - _REQUIRED_KEYS)
        raise ValueError(
            f"control-plane review binding schema mismatch: missing={missing}, extra={extra}"
        )

    environment = _optional_string(raw["environment"], field_name="environment")
    profile = _optional_string(
        raw["control_plane_profile"], field_name="control_plane_profile"
    )
    review_record = _optional_string(
        raw["review_record_reference"], field_name="review_record_reference"
    )
    evidence_set = _optional_string(
        raw["evidence_set_reference"], field_name="evidence_set_reference"
    )
    reviewed_at = _optional_string(raw["reviewed_at_utc"], field_name="reviewed_at_utc")

    if environment is not None and environment not in _ALLOWED_ENVIRONMENTS:
        raise ValueError(f"unsupported control-plane review environment: {environment}")
    if profile is not None and profile not in _ALLOWED_CONTROL_PLANE_PROFILES:
        raise ValueError(f"unsupported control-plane review profile: {profile}")
    _validate_opaque_reference(
        review_record, field_name="review_record_reference"
    )
    _validate_opaque_reference(
        evidence_set, field_name="evidence_set_reference"
    )
    _validate_reviewed_at(reviewed_at)

    return ControlPlaneEvidenceReviewBinding(
        environment=environment,
        control_plane_profile=profile,
        review_record_reference=review_record,
        evidence_set_reference=evidence_set,
        reviewed_at_utc=reviewed_at,
    )


__all__ = [
    "ControlPlaneEvidenceReviewBinding",
    "load_control_plane_review_binding",
]
