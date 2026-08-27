# fabric-customer

Reference Customer domain for the Enterprise Microsoft Fabric Data Engineering Platform.

This repository owns Customer-specific source-controlled dataset metadata, mappings, business DQ rules, fixtures and domain integration tests. Generic WATERMARK selection, Bronze normalization, quarantine execution, SCD2, reconciliation and state semantics are consumed from `fabric-data-framework` rather than reimplemented.

## Current implementation

Phase 2 implements one realistic reference dataset:

```text
crm.customer
  -> WATERMARK(modified_at, customer_id)
  -> normalized Bronze
  -> Customer DQ / row quarantine
  -> Customer mapping
  -> framework SCD2
  -> reconciliation
  -> target + watermark/state commit sequencing
```

Customer package version: `0.1.0`.
Framework dependency contract: `fabric-data-framework==0.2.0`.

The current cross-repo tests use framework source under test because immutable package publishing is a Phase 3 delivery concern; production delivery must consume an immutable released framework package.

## Structure

- `config/datasets/crm.customer.json` — source-controlled semantic dataset definition.
- `src/fabric_customer/domain.py` — Customer mapping and DQ rule definitions.
- `tests/fixtures/` — tiny deterministic CRM source fixtures.
- `tests/test_customer_vertical_slice.py` — cross-package integration and recovery assertions.
- `docs/` — canonical Customer project state.

Cross-repository architecture remains canonical in `fabric-data-framework/docs/ECOSYSTEM_BLUEPRINT.md`.
