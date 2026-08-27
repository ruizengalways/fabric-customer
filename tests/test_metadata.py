from fabric_customer import load_customer_config
from fabric_data_framework.config import ApplyStrategy, CaptureStrategy


def test_crm_customer_metadata_consumes_framework_schema():
    config = load_customer_config()
    assert config.dataset_id == "crm.customer"
    assert config.load.capture_strategy is CaptureStrategy.WATERMARK
    assert config.load.apply_strategy is ApplyStrategy.SCD2
    assert config.load.business_key == ("customer_id",)
    assert config.load.merge_key == ("customer_id",)
    assert config.load.watermark.tie_breaker == ("customer_id",)
    assert len(config.config_hash) == 64
