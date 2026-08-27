# fabric-customer — Project Blueprint

Status: Canonical
Last updated: 2026-08-28

## 1. Goal

Provide the first realistic domain/reference implementation proving that a business domain can consume the reusable `fabric-data-framework` package without copying generic runtime logic or depending on a shared cross-workspace execution notebook.

The Customer domain will demonstrate representative ingestion/state-management behaviours with tiny synthetic datasets and production-oriented correctness, audit, quarantine and recovery tests.

## 2. Ownership

This repository owns:

- Customer source-system configuration and contracts;
- Customer source-controlled dataset metadata;
- Customer Bronze/source-faithful mappings;
- Customer-specific transformations and canonical model;
- Customer-specific data-quality and reconciliation rules;
- domain-owned Fabric Pipeline/Notebook/Lakehouse/Warehouse item definitions where applicable;
- fixtures, integration tests and deployment smoke tests.

It does not own infrastructure provisioning or generic framework algorithms.

## 3. Non-goals

- Reimplementing `apply_scd2`, watermark engines, snapshot diff, CDC normalization, generic orchestration, quarantine or reconciliation engines.
- Power BI dashboards, DAX, semantic models or BI visualization.
- Managing capacity, Domains, workspace RBAC, networking or tenant settings.
- Building dozens of bespoke source pipelines merely to simulate scale.
- Hard-coding one pipeline branch/activity chain per table when stable framework metadata can drive the same behaviour.

## 4. Framework dependency model

The domain pins an immutable released framework version, for example:

```text
fabric-data-framework==1.2.0
```

Mutable branch dependencies such as `@main` are prohibited for production delivery. A framework upgrade is an explicit Customer pull request with CI validation. Customer release/version and framework release/version remain independent provenance dimensions.

## 5. Environment and infrastructure contract

Customer configuration refers to logical environment/domain resources. Physical workspace, Lakehouse, Warehouse and control-plane resource identifiers are supplied through the shared infrastructure contract defined by the ecosystem architecture.

The domain must not assume whether those resources were manually provisioned by an enterprise platform team or later created by Terraform in `fabric-infra`.

## 6. Metadata-driven domain configuration

Customer declares dataset semantics in source-controlled configuration using the framework-owned schema. The domain provides values; the framework defines and executes their meaning.

Representative metadata fields include:

- dataset/source/target identity;
- capture strategy;
- apply strategy;
- business key and merge key;
- watermark column and tie-breaker;
- event-time column;
- tracked columns;
- delete/late-arrival policy selection;
- execution group and criticality;
- simple dependency declarations;
- domain DQ policy/rules;
- quarantine action policy;
- reconciliation policy.

Example:

```yaml
dataset: crm.customer
source:
  system: crm
  object: dbo.Customer
target:
  layer: silver
  object: customer
capture_strategy: WATERMARK
apply_strategy: SCD2
business_key:
  - customer_id
merge_key:
  - customer_id
watermark:
  column: modified_at
  tie_breaker:
    - customer_id
event_time_column: modified_at
tracked_columns:
  - name
  - address
  - segment
orchestration:
  execution_group: crm_daily
  criticality: HIGH
quality:
  policy: customer_standard
  quarantine_policy: reject_bad_rows
reconciliation:
  policy: standard_count_and_key
```

This source-controlled definition is deployed/materialized into the framework control plane with config version/hash and Customer Git SHA. Runtime operational overrides may temporarily tune allowed operational parameters, but they do not replace Git as the source of semantic truth.

## 7. Multi-table orchestration model

When Customer eventually contains tens of datasets, it should use a small number of execution-group dispatchers rather than one bespoke pipeline per dataset.

Reference pattern:

```text
Customer schedule/trigger
  -> framework metadata lookup
  -> select enabled datasets for execution group
  -> bounded parallel dispatch
  -> generic dataset executor per dataset
  -> aggregate outcomes
```

A failed independent dataset must not immediately terminate all other Customer datasets. The framework records per-dataset outcomes and computes a final aggregate status according to criticality/failure policy.

Customer owns dataset criticality and dependency declarations; the framework owns generic failure isolation/status aggregation semantics.

## 8. Initial vertical slice

The first domain implementation after the framework foundation is available is one CRM Customer dataset:

```text
CRM customer
  -> WATERMARK capture using modified_at + customer_id tie-breaker
  -> Bronze normalized framework contract
  -> validation/quarantine/reconciliation hooks
  -> SCD2 apply
  -> Silver canonical customer
  -> committed watermark only after required gates pass
```

The exact config schema is owned by the framework and will be consumed rather than duplicated.

Initial tests should use tiny fixtures but include production-significant cases:

- new customer;
- changed customer;
- duplicate watermark timestamp with tie-breaker;
- unchanged record;
- rerun/idempotency;
- late arrival once framework policy supports it;
- invalid/quarantinable row;
- reconciliation accounting;
- failed attempt not advancing watermark.

## 9. Representative future scenarios

After the thin vertical slice works end to end, the domain may add small representative fixtures for:

- legacy full snapshot -> snapshot diff -> SCD2;
- CDC-style transactional events -> normalized Bronze -> dedupe -> UPSERT/APPEND;
- multi-dataset execution group with an intentionally failing non-critical dataset proving siblings continue and aggregate `PARTIAL_SUCCESS`;
- quarantine/replay scenario proving lineage from original rejected data to replayed run.

Lightweight streaming belongs later and remains secondary.

## 10. Domain DQ and quarantine responsibility

Customer owns business-specific rule definitions and acceptable thresholds. The framework owns reusable execution, action semantics, lineage and audit contracts.

Examples of Customer-owned rules:

- Customer ID must be non-null;
- email format rule if part of Customer contract;
- segment allowed-value rule;
- domain-specific freshness expectations.

The configured action can be warn, quarantine row, quarantine batch or fail dataset subject to framework-supported policy.

Quarantine is never used to hide platform/permission/code failures.

## 11. Planned repository structure

Only documentation exists currently. Later structure will be created as needed, for example:

```text
fabric-customer/
  pyproject.toml or dependency manifest
  config/
    datasets/
    quality/
    reconciliation/
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

## 12. Testing model

Customer tests validate domain integration with the pinned framework version.

Domain tests are responsible for:

- dataset metadata values/contract compatibility;
- domain transformations;
- domain DQ/reconciliation rules;
- representative integration/recovery behaviour;
- deployed smoke tests.

Generic engine correctness, effective-config override rules, orchestration aggregation and generic quarantine/audit invariants belong in framework tests.

## 13. Delivery model

Use feature branch -> PR -> CI -> merge. The resulting immutable Customer Git SHA is promoted through DEV -> UAT -> PROD as the same artifact/source revision.

Deployment provenance records at least Customer release, Customer Git SHA, deployed config hash/version and exact framework version.

A runtime override does not change the recorded semantic deployment provenance; each affected run additionally records the effective-config hash and active override lineage.

## 14. Roadmap

- Phase 0 — COMPLETE: canonical project memory and dependency/delivery ADRs.
- Phase 1 — no Customer runtime implementation; framework foundation establishes metadata/control-plane/runtime contracts first.
- Phase 2 — implement the single CRM Customer WATERMARK -> Bronze -> validation/quarantine -> SCD2 -> reconciliation -> Silver/state-commit slice.
- Phase 3 — participate in delivery-spine implementation and same-SHA promotion.
- Later phases — add only representative scenarios needed to prove reusable multi-dataset/failure-isolation/quarantine/recovery behaviours.

## 15. Documentation obligations

Every meaningful domain implementation change updates `docs/CURRENT_STATUS.md`; domain architecture changes update this blueprint and/or a Customer ADR. Cross-repository architecture changes are made in the framework ecosystem blueprint.

Routine implementation inside accepted architecture should proceed in coherent chunks without stopping for approval after every tiny file or class.
