from fabric_customer import (
    customer_mapper,
    customer_rules,
    load_customer_config,
    parse_crm_rows,
)


def test_compatibility_source_helpers_are_framework_neutral():
    config = load_customer_config()
    assert config.source_system == "crm"
    assert config.table == "customer"
    assert config.delivery_pattern == "incremental_watermark"

    rows = parse_crm_rows(
        [
            {
                "customer_id": "C1",
                "name": " Alice ",
                "address": "Sydney",
                "segment": "premium",
                "email": "ALICE@EXAMPLE.COM",
                "modified_at": "2026-09-07T00:00:00Z",
            }
        ]
    )
    mapped = customer_mapper(rows[0])
    assert mapped["name"] == "Alice"
    assert mapped["segment"] == "PREMIUM"
    assert mapped["email"] == "alice@example.com"
    assert all(rule.accepts(mapped) for rule in customer_rules())
