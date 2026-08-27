"""Customer reference domain for fabric-data-framework."""

from .domain import customer_mapper, customer_rules, parse_crm_rows
from .metadata import load_customer_config

__all__ = ["customer_mapper", "customer_rules", "load_customer_config", "parse_crm_rows"]

__version__ = "0.1.0"
