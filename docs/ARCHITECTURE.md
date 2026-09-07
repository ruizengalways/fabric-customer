# Customer architecture

Status: canonical current architecture

This document describes stable ownership, topology and repository structure. Exact live proof, current executable identity and release blockers belong in `docs/CURRENT_STATUS.md`; Git history owns old PR/migration narratives.

## 1. Ownership boundary

Customer/domain repository owns **WHAT**:

- DatasetConfig and source/capture semantic selections;
- business mappings, DQ and reconciliation policy;
- execution groups, dependencies, criticality and bounded domain overrides;
- non-secret environment bindings;
- normal domain Fabric item definitions;
- domain tests and customer-owned release identity;
- bounded certification inputs/extensions that return facts, never Framework PASS authority.

`fabric-data-framework` owns reusable **HOW**:

- DatasetConfig schema/capability validation;
- generic capture/Bronze/apply/SCD/reconciliation/state semantics;
- provider adapters and approved runners;
- relational Control Plane contracts/schema/migrations;
- `project-init` / `project-validate`;
- integration/business-path evidence evaluation;
- candidate certification and release-readiness PASS/FAIL authority.

Do not copy generic Framework algorithms into this repo.

## 2. Enterprise topology

DEV, UAT and PROD use the same logical component roles:

```text
DEV  -> Fabric SQL Database control plane + Lakehouse data plane + optional Warehouse
UAT  -> Fabric SQL Database control plane + Lakehouse data plane + optional Warehouse
PROD -> Fabric SQL Database control plane + Lakehouse data plane + optional Warehouse
```

Canonical Control Plane profile:

```text
fabric_sql_database_v1
```

Fabric SQL Database owns operational state such as pipeline/dataset/step runs, watermarks/checkpoints, reprocess lineage, target-operation journal and reconciliation state. Lakehouse / OneLake owns scalable business Bronze/Silver/Gold data and quarantine detail. Warehouse is optional SQL-first Gold/dimensional serving.

Do not use Lakehouse control tables in DEV and change to SQL Database in PROD; that changes concurrency/transaction semantics between release stages.

## 3. Repository structure

```text
config/
  datasets/                         DatasetConfig
  capture/                          semantic selections
  orchestration/execution-groups/   current execution policy
  environments/                     DEV/UAT/PROD non-secret bindings

src/                                customer-specific Python
fabric/                             normal domain Fabric definitions

certification/
  bootstrap.py                      one-click preparation entrypoint
  framework-executable.json         exact Framework executable selector
  config/environments/              certification environment bindings/templates
  fabric/                           certification Notebook/Pipeline/Copy/Spark/SQL
  project/                          exact certification DatasetConfig/scenarios
  extensions/                       bounded certification extension package
  support/                          internal bootstrap helpers

examples/                           teaching/intake examples only
tests/                              automated contracts
scripts/                            developer/CI utilities
docs/                               current architecture/runbooks
.github/                            CI/CD
```

Directory names express **role**, not Framework version. Never create current runtime trees such as `framework_0_4`, `framework_0_5`, `latest` or `legacy`. Framework upgrades modify the current contract in place through Git/PR/CI; Git preserves historical bytes.

## 4. Configuration and Fabric item boundaries

`config/` is runtime configuration truth. `fabric/` is the home for normal customer/domain Fabric definitions. `examples/` is never runtime truth.

Normal physical bindings are environment-local:

```text
config/environments/dev.json
config/environments/uat.json
config/environments/prod.json
```

Certification is intentionally separate because it may create disposable proof resources and uses an unreleased exact Framework executable. Its environment key resolves:

```text
certification/config/environments/DEV.json
```

`--environment DEV` is a Customer/Framework logical key, not a Fabric Environment item.

## 5. Medallion and store roles

```text
Bronze -> source-faithful/raw history
Silver -> normalized/deduplicated/DQ-governed/SCD/current models
Gold   -> consumer facts/dimensions/KPIs/semantic serving
```

Recommended stores:

```text
Fabric SQL Database -> operational Framework Control Plane
Lakehouse / OneLake -> Bronze/Silver/Gold business data + quarantine detail
Fabric Warehouse    -> optional SQL-first Gold serving
```

## 6. Enterprise onboarding model

One coherent domain repo can model 100 datasets across different technical patterns:

```text
50 FULL      -> REPLACE
20 WATERMARK -> SCD2
20 WATERMARK -> SCD1
10 CDC       -> UPSERT using Debezium / external CDC
```

Do not split repositories merely by capture or SCD strategy. Repo boundaries follow ownership, security/compliance and independent release lifecycle. Operational grouping belongs in `config/orchestration/execution-groups/`.

## 7. Pipeline operating model

Dataset is the unit of fault isolation/recovery; execution group / parent Pipeline is the scheduling and aggregate-status unit.

Default behavior:

```text
one dataset FAIL
-> record durable failure
-> independent siblings continue
-> failed dependents become BLOCKED
-> runnable work reaches terminal state
-> parent Pipeline ends FAILED
```

The normal parent policy is `FAIL_AT_END`. Recovery is classification-driven (`RETRY`, `REPLAY`, `BACKFILL`, `FULL_REBUILD`); `UNKNOWN_COMMIT` must be reconciled before retry.

## 8. Dependency/release identity

Production remains exactly pinned to:

```text
fabric-data-framework==0.3.0
```

The established project-contract transition lane remains pinned to Framework SHA:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

It exists only for `project-init` / `project-validate` compatibility. Current Framework 0.4 certification uses the independent executable selector in `certification/framework-executable.json` and does not alter the production dependency.

Framework identity and Customer identity are independent and must never be assumed equal.

## 9. CI/CD promotion boundary

Promote the same immutable application/release identity through:

```text
PR -> CI -> DEV -> UAT -> PROD
```

Promote code, DatasetConfig, capture semantics, orchestration policy, DQ/reconciliation rules, Fabric definitions, Control Plane schema/migrations and logical non-secret templates.

Never copy DEV runtime truth into UAT/PROD: workspace/item UUIDs, credentials, pipeline/dataset runs, watermarks/checkpoints, retry history, operation-journal state or business data are environment-local.

## 10. Certification boundary

Preferred preparation:

```powershell
python certification/bootstrap.py --apply --environment DEV
```

Successful preparation stops at:

```text
bootstrap_status = READY
certification_result = NOT_RUN
release_authorized = false
```

Bootstrap READY is not certification PASS. Certification PASS is not release authorization. Current strict prerequisites and next real boundary are recorded only in `docs/CURRENT_STATUS.md`.
