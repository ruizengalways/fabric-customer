"""Source-controlled Customer dataset metadata loading."""

from __future__ import annotations

from pathlib import Path

from fabric_data_framework.config import DatasetConfig


def default_customer_config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "datasets" / "crm.customer.json"


def load_customer_config(path: Path | None = None) -> DatasetConfig:
    source = path or default_customer_config_path()
    return DatasetConfig.model_validate_json(source.read_text(encoding="utf-8"))
