"""Fabric-native, framework-agnostic customer/source-system simulator."""

from .domain import (
    SourceValidationRule,
    customer_mapper,
    customer_rules,
    parse_crm_rows,
)
from .metadata import SourceTableDefinition, load_customer_config, source_catalog
from .simulator import (
    materialize_scenario,
    replay_day,
    reset_scenario,
    scenario_catalog,
    verify_scenario,
)

__all__ = [
    "SourceTableDefinition",
    "SourceValidationRule",
    "customer_mapper",
    "customer_rules",
    "load_customer_config",
    "materialize_scenario",
    "parse_crm_rows",
    "replay_day",
    "reset_scenario",
    "scenario_catalog",
    "source_catalog",
    "verify_scenario",
]

__version__ = "0.2.0"
