"""Framework-neutral source-system catalog."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceTableDefinition:
    source_system: str
    table: str
    delivery_pattern: str
    primary_key: tuple[str, ...]
    truth_model: str
    notes: str = ""


_CATALOG = (
    SourceTableDefinition("crm", "customer", "incremental_watermark", ("customer_id",), "current_and_history"),
    SourceTableDefinition("billing", "invoice", "full_snapshot", ("invoice_id",), "current_state"),
    SourceTableDefinition("health", "patient_profile", "incremental_changes", ("patient_id",), "current_and_history"),
    SourceTableDefinition("claims", "claim_events", "debezium_cdc", ("claim_id",), "source_events"),
)


def source_catalog() -> tuple[SourceTableDefinition, ...]:
    return _CATALOG


def load_customer_config() -> SourceTableDefinition:
    """Compatibility name returning the CRM source definition, not framework metadata.

    v0.2 deliberately removes the former fabric-data-framework DatasetConfig dependency.
    """

    return _CATALOG[0]
