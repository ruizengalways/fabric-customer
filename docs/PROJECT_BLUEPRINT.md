# fabric-customer — Project Blueprint

Status: Canonical
Last updated: 2026-08-28

## 1. Goal

Provide a realistic Customer-domain reference proving a domain can consume the reusable `fabric-data-framework` without copying generic capture/apply/control-plane algorithms.

## 2. Ownership

Customer owns:

- source-controlled Customer dataset metadata values;
- source parsing/mapping and canonical Customer shape;
- business-specific DQ/reconciliation rule definitions;
- domain fixtures/integration/smoke tests;
- domain-owned Fabric items when introduced.

Framework owns generic WATERMARK, Bronze envelope, quarantine execution semantics, SCD2, reconciliation/state rules, runtime audit and deployment/control-plane contracts.

## 3. Implemented Phase 2 slice

Source-controlled config:

```text
config/datasets/crm.customer.json
```

declares:

- source `crm / dbo.Customer`;
- target `silver.customer`;
- WATERMARK capture;
- `modified_at` watermark;
- `customer_id` tie-breaker;
- SCD2 apply;
- `customer_id` business/merge key;
- tracked `name`, `address`, `segment`, `email`;
- execution group `crm_daily` and HIGH criticality;
- Customer DQ/quarantine policy reference;
- required reconciliation policy.

This file is the semantic source of truth for the dataset. DEV/UAT/PROD materialize the same released definition but keep independent runtime state.

## 4. Domain code

`src/fabric_customer/domain.py` contains only Customer-specific behaviour:

- parse source ISO timestamps to typed datetimes;
- normalize/trim Customer strings;
- normalize segment casing;
- normalize email casing;
- business DQ rule: email contains `@`;
- business DQ rule: segment belongs to STANDARD/PREMIUM/ENTERPRISE.

No watermark or SCD2 algorithm exists in this repo.

## 5. Reference fixture behaviour

Initial fixture proves:

- two valid customers sharing the same timestamp are both captured through tie-breaker ordering;
- one later invalid-email row is quarantined with lineage;
- accepted records reach Silver SCD2;
- the watermark can advance through the row-level quarantined source position only because reconciliation accounts for the quarantined row.

Incremental fixture proves:

- unchanged C001 at a later timestamp does not create a new SCD2 version;
- changed C002 closes the old version and opens a new current version;
- new C004 inserts;
- invalid-segment C005 is quarantined;
- all incremental rows share the same timestamp, exercising tie-breaker ordering;
- watermark advances to `(timestamp, C005)` after successful reconciliation;
- rerun selects no rows and makes no target change.

A forced-reconciliation-failure integration test proves proposed target changes and new watermark are not committed.

## 6. Current repo shape

```text
fabric-customer/
  pyproject.toml
  config/
    datasets/
      crm.customer.json
  src/fabric_customer/
    __init__.py
    metadata.py
    domain.py
  tests/
    fixtures/
      crm_customer_initial.json
      crm_customer_incremental.json
    test_metadata.py
    test_customer_vertical_slice.py
  docs/
```

## 7. Dependency model

`pyproject.toml` declares exact framework dependency `fabric-data-framework==0.2.0`.

The framework package has not yet been published immutably, so local cross-repo Phase 2 tests install/reference the framework source under test and install Customer without resolving the external dependency. Phase 3 replaces that development arrangement with immutable package release/download semantics.

## 8. Testing responsibility

Customer tests cover domain metadata values, mapping/DQ rules and cross-package integration behaviour. Framework tests cover generic algorithm invariants.

Current Customer test suite covers:

- framework schema compatibility of `crm.customer` metadata;
- initial and incremental WATERMARK execution;
- duplicate timestamps/tie-breaker ordering;
- row quarantine/accounting;
- normalized mapping;
- SCD2 changed/unchanged versions;
- significant step audit sequence;
- rerun idempotency;
- failed reconciliation preserving target and watermark.

## 9. Delivery model

Same immutable Customer Git SHA/config bundle/framework version moves DEV -> UAT -> PROD. Config schema/migrations/definitions are promoted; environment-local runtime state is not.

Phase 3 implements the CI/CD delivery spine compatible with both GitHub-driven Fabric automation and Fabric-native Deployment Pipeline promotion.

## 10. Roadmap status

- Phase 0 — COMPLETE: canonical architecture.
- Phase 1 — COMPLETE dependency: framework foundation.
- Phase 2 — COMPLETE: first `crm.customer` executable vertical slice.
- Phase 3 — NEXT: CI/package/release/deployment spine.
- Later — add only representative datasets needed to prove remaining reusable strategies, multi-dataset failure isolation/recovery and streaming.

## 11. Documentation obligation

Every coherent domain implementation updates `CURRENT_STATUS.md`. Routine work inside accepted architecture continues without per-file approval pauses.
