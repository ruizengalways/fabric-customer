# fabric-customer — Project Blueprint

Status: Canonical
Last updated: 2026-08-28

## 1. Goal

Provide the first realistic domain/reference implementation proving that a business domain can consume the reusable `fabric-data-framework` package without copying generic runtime logic or depending on a shared cross-workspace execution notebook.

The Customer domain will demonstrate representative ingestion/state-management behaviours with tiny synthetic datasets and production-oriented correctness tests.

## 2. Ownership

This repository owns:

- Customer source-system configuration and contracts;
- Customer Bronze/source-faithful mappings;
- Customer-specific transformations and canonical model;
- Customer-specific data-quality and reconciliation rules;
- domain-owned Fabric Pipeline/Notebook/Lakehouse/Warehouse item definitions where applicable;
- fixtures, integration tests and deployment smoke tests.

It does not own infrastructure provisioning or generic framework algorithms.

## 3. Non-goals

- Reimplementing `apply_scd2`, watermark engines, snapshot diff, CDC normalization or generic reconciliation.
- Power BI dashboards, DAX, semantic models or BI visualization.
- Managing capacity, Domains, workspace RBAC, networking or tenant settings.
- Building dozens of bespoke source pipelines merely to simulate scale.

## 4. Framework dependency model

The domain pins an immutable released framework version, for example:

```text
fabric-data-framework==1.2.0
```

Mutable branch dependencies such as `@main` are prohibited for production delivery. A framework upgrade is an explicit Customer pull request with CI validation. Customer release/version and framework release/version remain independent provenance dimensions.

## 5. Environment and infrastructure contract

Customer configuration refers to logical environment/domain resources. Physical workspace, Lakehouse and Warehouse identifiers are supplied through the shared infrastructure contract defined by the ecosystem architecture.

The domain must not assume whether those resources were manually provisioned by an enterprise platform team or later created by Terraform in `fabric-infra`.

## 6. Initial vertical slice

The first domain implementation after the framework foundation is available is one CRM Customer dataset:

```text
CRM customer
  -> WATERMARK capture using modified_at + customer_id tie-breaker
  -> Bronze normalized framework contract
  -> SCD2 apply
  -> Silver canonical customer
```

Expected configuration shape:

```yaml
dataset: crm.customer
capture_strategy: WATERMARK
apply_strategy: SCD2
business_key:
  - customer_id
watermark:
  column: modified_at
  tie_breaker:
    - customer_id
tracked_columns:
  - name
  - address
  - segment
```

The exact config schema is owned by the framework and will be consumed rather than duplicated.

## 7. Representative future scenarios

After the thin vertical slice works end to end, the domain may add small representative fixtures for:

- a legacy full-snapshot source -> snapshot diff -> SCD2;
- CDC-style transactional events -> normalized Bronze -> dedupe -> UPSERT/APPEND.

Lightweight streaming belongs later and remains secondary.

## 8. Planned repository structure

Only documentation exists in Phase 0. Later structure will be created as needed, for example:

```text
fabric-customer/
  pyproject.toml or dependency manifest
  config/
  src/ or domain notebooks/
  tests/
    fixtures/
    integration/
    smoke/
  fabric/                  # only when domain-owned Fabric item definitions are introduced
  docs/
    PROJECT_BLUEPRINT.md
    CURRENT_STATUS.md
    adr/
    runbooks/
```

No placeholder source-system directories are created before a scenario is implemented.

## 9. Testing model

Customer tests validate domain integration with the pinned framework version. The first vertical slice must cover small cases for new records, updates, duplicate watermark timestamps, rerun/idempotency and late arrival once those framework capabilities exist.

Domain-specific DQ/reconciliation assertions belong here; generic engine correctness belongs in framework tests.

## 10. Delivery model

Use feature branch -> PR -> CI -> merge. The resulting immutable Customer Git SHA is promoted through DEV -> UAT -> PROD as the same artifact/source revision.

Deployment provenance must record at least Customer release, Customer Git SHA and exact framework version.

## 11. Roadmap

- Phase 0 — COMPLETE: canonical project memory and dependency/delivery ADRs.
- Phase 1 — no Customer runtime implementation; allow framework foundation to establish contracts first.
- Phase 2 — implement the single CRM Customer WATERMARK -> Bronze -> SCD2 -> Silver slice.
- Phase 3 — participate in delivery-spine implementation and same-SHA promotion.
- Later phases — add only representative scenarios needed to prove reusable framework behaviours.

## 12. Documentation obligations

Every meaningful domain implementation change updates `docs/CURRENT_STATUS.md`; domain architecture changes update this blueprint and/or a Customer ADR. Cross-repository architecture changes are made in the framework ecosystem blueprint.
