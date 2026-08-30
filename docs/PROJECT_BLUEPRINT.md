# fabric-customer — Project Blueprint

Status: Canonical
Last updated: 2026-08-30

## 1. Goal

Provide a realistic Customer-domain reference proving a domain can consume the reusable `fabric-data-framework` without copying generic capture/apply/control-plane algorithms, and provide the domain-repository bootstrap pattern for large enterprise onboarding.

## 2. Ownership

Customer/domain repo owns WHAT:

- source-controlled domain dataset metadata values;
- source parsing/mapping and canonical domain shapes;
- business-specific DQ/reconciliation rule definitions;
- domain fixtures/integration/smoke tests;
- domain-owned Fabric items when introduced;
- domain execution grouping and deployment bindings.

Framework owns HOW:

- generic capture/runtime contracts;
- Bronze normalization and quarantine execution semantics;
- reusable SCD/apply algorithms;
- reconciliation/state/checkpoint rules;
- runtime audit and deployment/control-plane contracts;
- reusable Fabric adapters.

No generic capture/SCD algorithm should be copied into this repo.

## 3. Implemented executable Customer slice

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

This file is the semantic source of truth for the executable Customer dataset. DEV/UAT/PROD materialize the same released definition but keep independent runtime state.

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

The small runtime fixture proves algorithm/domain correctness without pretending scale through duplicated fake tables.

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
- watermark advances after successful reconciliation;
- rerun selects no rows and makes no target change.

A forced-reconciliation-failure integration test proves proposed target changes and new watermark are not committed.

## 6. Enterprise bulk-onboarding reference

Large domains should not hand-author hundreds of repeated files or notebooks.

The checked-in scale fixture:

```text
examples/enterprise_100_table/health_100_tables.csv
```

models:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT
```

`scripts/scaffold_from_manifest.py` provides deterministic local dry-run and explicit generation of one framework `DatasetConfig` JSON per manifest row.

`tests/test_bulk_onboarding.py` proves all 100 generated definitions validate against the exact released Framework v0.3.0 schema.

This is a config/onboarding scale proof only. Production scale requires provider/runtime/capacity evidence in an approved Fabric environment.

## 7. Repository boundary

Do not organize repos around capture/apply implementation details.

```text
bad boundary:
  fabric-health-full-refresh
  fabric-health-scd1
  fabric-health-scd2
  fabric-health-debezium
```

Default:

```text
fabric-health
```

Split only when there is a real independent ownership, security/compliance, data-product or release boundary.

## 8. Current repo shape

```text
fabric-customer/
  pyproject.toml
  config/
    datasets/
      crm.customer.json
  examples/
    enterprise_100_table/
      health_100_tables.csv
      README.md
  scripts/
    scaffold_from_manifest.py
    validate_metadata.py
  src/fabric_customer/
    __init__.py
    metadata.py
    domain.py
  tests/
    fixtures/
    test_bulk_onboarding.py
    ...
  deploy/
    bindings.dev.json
    bindings.uat.json
    bindings.prod.json
  docs/
    runbooks/
      BUILD_NEW_DOMAIN_PROJECT.md
```

## 9. Dependency model

`pyproject.toml` exact-pins:

```text
fabric-data-framework==0.3.0
```

CI downloads the immutable released Framework v0.3.0 wheel, verifies its SHA-256 checksum, installs it, installs Customer, runs cross-package tests, and creates same-release deployment plans.

Do not switch the domain repo to Framework `main` or an unpublished source version. Upgrade only after a new immutable framework release is available and the domain CI is updated to consume that release exactly.

## 10. Testing responsibility

Domain tests cover metadata values, mapping/DQ rules, bulk onboarding contracts and cross-package integration behaviour. Framework tests cover generic algorithm invariants.

Separate proof types:

```text
manifest/config scale proof
!=
runtime correctness proof
!=
real Fabric provider integration proof
!=
capacity/performance proof
```

Do not use one as evidence for another.

## 11. Delivery model

The same immutable domain Git SHA/config bundle/framework version moves DEV -> UAT/TEST -> PROD. Config schema/definitions are promoted; environment-local runtime state is not.

`deploy/bindings.*.json` resolves environment-specific non-secret physical bindings outside the semantic metadata hash.

The supported CI/CD shape is compatible with GitHub-driven Fabric automation and Fabric-native Deployment Pipeline promotion.

## 12. Project bootstrap / Fabric runbook

`docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md` is the canonical domain-side procedure for:

- jumpbox/VDI bootstrap;
- local Python environment and exact framework release installation;
- bulk manifest dry-run/generation;
- GitHub PR/CI;
- Fabric DEV/TEST/PROD workspaces;
- Fabric Environment custom wheels;
- logical connection/secrets boundary;
- thin metadata-driven drivers;
- representative pattern integration proof;
- immutable release/deployment plan;
- production promotion checklist.

The runbook explicitly records the current external limitation: this reference repo has not yet completed a real Fabric workspace deployment, so documentation is not evidence of deployment.

## 13. Roadmap status

- Phase 0 — COMPLETE: canonical architecture.
- Phase 1 — COMPLETE dependency: framework foundation.
- Phase 2 — COMPLETE: first `crm.customer` executable vertical slice.
- Phase 3 — COMPLETE: CI/package/release/deployment spine.
- Enterprise bulk onboarding — COMPLETE as config/CI/runbook proof.
- Next runtime proof — after immutable Framework v0.4.0, add the smallest representative multi-dataset failure-isolation graph.
- Later — retry/backfill/replay, representative SNAPSHOT_DIFF and CDC/UPSERT, delete/late-arrival/schema-evolution policies, and real Fabric Environment/Notebook/Pipeline evidence.

## 14. Documentation obligation

Every coherent domain implementation updates `CURRENT_STATUS.md`. Routine work inside accepted architecture continues without per-file approval pauses.
