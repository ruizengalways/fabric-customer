"""Fabric-native, framework-agnostic customer/source-system simulator."""

from .domain import SourceValidationRule, customer_mapper, customer_rules, parse_crm_rows
from .metadata import SourceTableDefinition, load_customer_config, source_catalog
from .simulator import materialize_scenario, reset_scenario, scenario_catalog

__all__ = [
    "SourceTableDefinition",
    "SourceValidationRule",
    "customer_mapper",
    "customer_rules",
    "load_customer_config",
    "materialize_scenario",
    "parse_crm_rows",
    "reset_scenario",
    "scenario_catalog",
    "source_catalog",
]

__version__ = "0.2.0"
