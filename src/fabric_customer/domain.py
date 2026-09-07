"""Source-system parsing and validation rules owned by the customer simulator.

Nothing in this module imports or assumes a downstream data-engineering framework.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class SourceValidationRule:
    """A source-quality fact used when generating deliberately good/bad source rows."""

    code: str
    message: str
    predicate: Callable[[Mapping[str, Any]], bool]

    def accepts(self, row: Mapping[str, Any]) -> bool:
        return bool(self.predicate(row))


def parse_crm_rows(rows: Iterable[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    parsed: list[dict[str, Any]] = []
    for source in rows:
        row = dict(source)
        value = row.get("modified_at")
        if isinstance(value, str):
            row["modified_at"] = datetime.fromisoformat(value)
        parsed.append(row)
    return tuple(parsed)


def customer_mapper(row: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize a CRM source row without applying target SCD/merge semantics."""

    return {
        "customer_id": row["customer_id"],
        "name": str(row["name"]).strip(),
        "address": str(row.get("address") or "").strip(),
        "segment": str(row.get("segment") or "UNKNOWN").upper(),
        "email": str(row.get("email") or "").lower(),
        "modified_at": row["modified_at"],
        **({"preferred_language": row["preferred_language"]} if "preferred_language" in row else {}),
    }


def customer_rules() -> tuple[SourceValidationRule, ...]:
    return (
        SourceValidationRule(
            code="EMAIL_FORMAT",
            message="email must contain @",
            predicate=lambda row: "@" in str(row.get("email") or ""),
        ),
        SourceValidationRule(
            code="SEGMENT_ALLOWED",
            message="segment must be STANDARD, PREMIUM or ENTERPRISE",
            predicate=lambda row: str(row.get("segment") or "").upper()
            in {"STANDARD", "PREMIUM", "ENTERPRISE"},
        ),
    )
