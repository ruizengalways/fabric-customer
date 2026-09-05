# Enterprise DEV / UAT / PROD topology

This is the canonical environment/storage topology for the Customer reference project.

## Principle

DEV is not a reduced architecture. DEV, UAT and PROD use the same logical component types so CI/CD promotes definitions rather than changing storage semantics between stages.

```text
DEV  -> Fabric SQL Database control plane + Lakehouse data plane + optional Warehouse
UAT  -> Fabric SQL Database control plane + Lakehouse data plane + optional Warehouse
PROD -> Fabric SQL Database control plane + Lakehouse data plane + optional Warehouse
```

Only environment-local bindings, credentials, capacity, scale and data differ.

## Control plane

Canonical profile in all enterprise stages:

```text
control_plane_profile = fabric_sql_database_v1
```

Fabric SQL Database owns operational Framework state:

```text
dataset / deployed semantic metadata
pipeline_run
dataset_run
step_run
watermark / CDC checkpoint
reprocess_request
attempt lineage
target operation journal
reconciliation state
quarantine batch metadata/reference
```

Never promote DEV runtime rows or watermarks to UAT/PROD. CI/CD promotes the SQL schema/migrations and logical definitions; each stage starts/maintains its own runtime state.

## Medallion data plane

Bronze/Silver/Gold are data maturity layers, not names of database products.

Recommended Customer topology:

```text
Source
  -> Bronze Lakehouse
  -> Silver Lakehouse
  -> Gold Lakehouse OR optional Fabric Warehouse
```

Use Lakehouse/OneLake for scalable business data, SCD processing, quarantine row payloads and large reconciliation detail.

Warehouse is optional. Use it when Gold is primarily SQL-first dimensional/star-schema serving or relational BI. An all-Lakehouse Bronze/Silver/Gold topology is valid when Warehouse adds no value.

## Why not Lakehouse control tables

Delta optimistic concurrency protects correctness by rejecting conflicting concurrent writers. A multi-table Pipeline can have many workers simultaneously trying to update small operational records such as `dataset_run`, `step_run`, watermarks and operation-journal state. Overlapping Delta updates/merges can therefore conflict even when independent business-table processing should continue.

That is expected Delta behavior, but it is not the preferred enterprise operational-state workload. The Customer reference therefore uses Fabric SQL Database from DEV onward for control state.

If a business mutation succeeds but the Framework cannot durably prove its control-state transition, the run must fail closed and recovery must inspect the operation journal/target evidence before retry.

## CI/CD promotion boundary

Promote:

```text
Customer/Framework code
DatasetConfig
execution-group policy
DQ/reconciliation rules
Notebook/Pipeline definitions
control-plane SQL schema/migrations
non-secret binding templates
```

Resolve separately per environment and never copy as deployment truth:

```text
workspace/item UUIDs
connection strings
secrets/tokens
pipeline_run/dataset_run rows
watermarks/checkpoints
retry/reprocess history
operation-journal state
business data
```

Recommended release path:

```text
PR
-> CI
-> deploy same logical topology to DEV
-> integration/certification
-> deploy same definitions to UAT with UAT bindings
-> approval/certification
-> deploy same definitions to PROD with PROD bindings
```

## Resource naming example

```text
DEV
  sqldb-framework-control-dev
  lh-bronze-dev
  lh-silver-dev
  lh-gold-dev OR wh-gold-dev

UAT
  sqldb-framework-control-uat
  lh-bronze-uat
  lh-silver-uat
  lh-gold-uat OR wh-gold-uat

PROD
  sqldb-framework-control-prod
  lh-bronze-prod
  lh-silver-prod
  lh-gold-prod OR wh-gold-prod
```

Names are examples; actual organization naming standards win. The invariant is component-role parity, not exact display names.

## New project checklist

Before onboarding business tables, confirm:

```text
[ ] independent DEV Fabric SQL Database exists for Framework control state
[ ] UAT/PROD topology is defined with the same component roles
[ ] Lakehouse(s) own business medallion data, not operational control state
[ ] Warehouse is included only if Gold SQL-serving requirements justify it
[ ] control-plane schema migration is source controlled
[ ] environment bindings are non-secret/source-controlled by logical name where possible
[ ] secrets and physical IDs are resolved at deployment/runtime
[ ] CI/CD never copies DEV runtime state to UAT/PROD
```

Framework generic architecture details live in `fabric-data-framework/docs/human/ENTERPRISE_FABRIC_ARCHITECTURE.md`.
