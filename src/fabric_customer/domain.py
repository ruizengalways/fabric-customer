"""Customer-specific source parsing, mapping and data-quality rules."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Mapping

from fabric_data_framework.quality import RowRule


def parse_crm_rows(rows: Iterable[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    parsed: list[dict[str, Any]] = []
    for source in rows:
        row = dict(source)
        value = row.get("modified_at")
        if isinstance(value, str):
            row["modified_at"] = datetime.fromisoformat(value.replace("Z", "+00:00"))
        parsed.append(row)
    return tuple(parsed)


def customer_mapper(row: dict[str, Any]) -> dict[str, Any]:
    """Explicit domain mapping; generic SCD2 behaviour remains in the framework."""

    return {
        "customer_id": row["customer_id"],
        "name": str(row["name"]).strip(),
        "address": str(row.get("address") or "").strip(),
        "segment": str(row.get("segment") or "UNKNOWN").upper(),
        "email": str(row.get("email") or "").lower(),
        "modified_at": row["modified_at"],
    }


def customer_rules() -> tuple[RowRule, ...]:
    return (
        RowRule(
            code="EMAIL_FORMAT",
            message="email must contain @",
            predicate=lambda row: "@" in str(row.get("email") or ""),
        ),
        RowRule(
            code="SEGMENT_ALLOWED",
            message="segment must be STANDARD, PREMIUM or ENTERPRISE",
            predicate=lambda row: str(row.get("segment") or "").upper()
            in {"STANDARD", "PREMIUM", "ENTERPRISE"},
        ),
    )
