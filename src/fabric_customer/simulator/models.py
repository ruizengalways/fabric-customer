"""Framework-neutral source event and scenario models."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SourceEvent:
    event_id: str
    source_system: str
    table: str
    operation: str
    key: Mapping[str, Any]
    before: Mapping[str, Any] | None
    after: Mapping[str, Any] | None
    source_ts: str
    delivered_at: str
    schema_version: int = 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "source_system": self.source_system,
            "table": self.table,
            "operation": self.operation,
            "key": dict(self.key),
            "before": None if self.before is None else dict(self.before),
            "after": None if self.after is None else dict(self.after),
            "source_ts": self.source_ts,
            "delivered_at": self.delivered_at,
            "schema_version": self.schema_version,
        }

    def as_debezium(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "payload": {
                "before": None if self.before is None else dict(self.before),
                "after": None if self.after is None else dict(self.after),
                "source": {"name": self.source_system, "table": self.table},
                "op": self.operation,
                "ts_ms": self.source_ts,
                "delivery_ts": self.delivered_at,
                "event_id": self.event_id,
            },
        }


@dataclass(frozen=True)
class ScenarioStep:
    day: int
    slug: str
    description: str
    schema_version: int
    snapshot: tuple[Mapping[str, Any], ...]
    incremental: tuple[Mapping[str, Any], ...]
    cdc_events: tuple[SourceEvent, ...]
    expected_current: tuple[Mapping[str, Any], ...]
    expected_history: tuple[Mapping[str, Any], ...]

    @property
    def day_label(self) -> str:
        return f"day_{self.day:02d}"
