# fabric-customer

Reference Customer domain for the Enterprise Microsoft Fabric Data Engineering Platform.

This repository owns Customer-specific source-controlled dataset metadata, mappings, business DQ rules, fixtures and domain integration tests. Generic WATERMARK selection, Bronze normalization, quarantine execution, SCD2, reconciliation, state semantics and delivery contracts are consumed from `fabric-data-framework` rather than reimplemented.

## Current implementation

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
Framework dependency contract: `fabric-data-framework==0.3.0`.

Phase 3 adds Customer CI/release participation:

- dependency-free source metadata validation;
- GitHub Actions Customer wheel build;
- optional exact private-framework integration using `FRAMEWORK_REPO_TOKEN`;
- DEV/UAT/PROD binding profiles outside semantic metadata;
- same-release deployment-plan tests;
- tag-triggered Customer release workflow that consumes the exact released framework wheel and emits a release manifest.

If the private-framework token is absent, source metadata/compile/wheel checks still run and the cross-repo integration path is explicitly skipped rather than reported as executed.

## Structure

- `config/datasets/crm.customer.json` — source-controlled semantic dataset definition.
- `src/fabric_customer/domain.py` — Customer mapping and DQ rules.
- `deploy/bindings.*.json` — non-secret reference environment binding profiles.
- `scripts/validate_metadata.py` — source-only CI contract.
- `tests/fixtures/` — tiny deterministic CRM fixtures.
- `tests/` — domain integration, recovery and delivery-plan tests.
- `docs/` — canonical Customer project state.

Cross-repository architecture remains canonical in `fabric-data-framework/docs/ECOSYSTEM_BLUEPRINT.md`.
