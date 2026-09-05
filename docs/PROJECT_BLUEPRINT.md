# fabric-customer — Project Blueprint

Status: Canonical
Last updated: 2026-09-06

## 1. Goal

Provide a realistic Customer/domain reference that consumes reusable `fabric-data-framework` behavior without copying generic capture/apply/control-plane algorithms, supports large enterprise onboarding in one business-domain repo, and provides customer-owned exact inputs for Framework certification without moving PASS authority into the domain repo.

Exact current SHAs, CI run IDs, artifact hashes and release blockers live in `docs/CURRENT_STATUS.md`. This blueprint describes stable architecture and ownership rather than historical PR archaeology.

## 2. Ownership

Customer/domain repo owns WHAT:

- source-controlled DatasetConfig values and source/capture semantic selections;
- parsing/mapping, business DQ/reconciliation rule definitions and fixtures;
- domain tests, execution grouping and non-secret bindings;
- Customer-owned Fabric item definitions/templates;
- representative certification datasets/scenarios/driver recipes;
- bounded observers/drivers/mutation extensions;
- exact customer/domain `ReleaseManifest` artifacts.

Framework owns HOW:

- DatasetConfig schema and capability validation;
- generic capture/Bronze/apply/reconciliation/state semantics;
- reusable Fabric adapters and approved provider runners;
- relational Control Plane contracts/schema/migrations;
- project-init/project-validate;
- integration/business-path evidence evaluation;
- release-readiness PASS/FAIL and candidate certification.

No generic capture/SCD/project-validation/evidence-PASS algorithm belongs in this repo.

## 3. Enterprise environment topology

DEV is the production architecture at smaller scale, not a different architecture.

```text
DEV  -> Fabric SQL Database control plane + Lakehouse data plane + optional Warehouse
UAT  -> Fabric SQL Database control plane + Lakehouse data plane + optional Warehouse
PROD -> Fabric SQL Database control plane + Lakehouse data plane + optional Warehouse
```

Canonical control-plane profile:

```text
fabric_sql_database_v1
```

The same logical backend class is used in DEV/UAT/PROD. Environment-specific physical resource IDs, credentials, capacity, scale and data remain separate.

Do not use Lakehouse as the enterprise DEV control plane and migrate to SQL Database later. That changes concurrency/transaction semantics between release stages and breaks topology parity.

Full runbook:

```text
docs/runbooks/ENTERPRISE_ENVIRONMENT_TOPOLOGY.md
```

## 4. Medallion data plane and store roles

Bronze/Silver/Gold describe analytical data maturity:

```text
Bronze -> source-faithful/raw history
Silver -> normalized, deduplicated, DQ governed, SCD/current-state models
Gold   -> consumer models, facts/dimensions/KPIs/semantic serving
```

Recommended stores:

```text
Fabric SQL Database -> operational Framework control state
Lakehouse / OneLake -> Bronze/Silver/Gold business data, quarantine payloads, large detail
Fabric Warehouse    -> optional SQL-first Gold/dimensional serving
```

Warehouse is not mandatory. Gold can remain in Lakehouse where that best fits consumption.

The Control Plane stores operational metadata/state such as `pipeline_run`, `dataset_run`, `step_run`, watermarks/checkpoints, retry/reprocess lineage, target-operation journal and reconciliation state. Full quarantined business rows stay in governed data-plane storage; SQL stores summary/reference metadata.

## 5. Why Lakehouse is not the canonical control plane

Delta optimistic concurrency is appropriate for large analytical table mutations but can reject overlapping concurrent updates/merges. A multi-table Pipeline may have many workers simultaneously updating small operational records. That can create control-state contention even when independent business-table work should continue.

The enterprise reference therefore uses Fabric SQL Database from DEV onward for operational state. If business mutation succeeds but the Framework cannot durably prove the corresponding control-state transition, the run fails closed and recovery inspects operation/target evidence before retry.

## 6. Normal business project

```text
fabric-project.json
config/datasets/crm.customer.json
config/capture/semantic-selections.json
```

`crm.customer` uses WATERMARK capture on `modified_at` with `customer_id` tie-breaker and SCD2 apply. Its semantic selection records that hard deletes are not observable without a delete signal and SCD2 history cannot exceed changes observed by the watermark path.

DEV/UAT/PROD materialize the same released semantic definition while retaining independent runtime state.

The release-certification project is intentionally separate:

```text
certification/project/
```

It is not the CRM production DatasetConfig bundle.

## 7. Enterprise onboarding model

The checked-in Health fixture models one domain repo:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT
```

Do not split these into four repositories merely by capture/apply mechanism. Repo boundaries follow ownership, security/compliance and independent release lifecycle. Operational grouping belongs in `orchestration.execution_group`.

Framework 0.4 examples model four groups:

```text
health_full_refresh
health_scd2
health_scd1
health_debezium
```

Each group uses fail-at-end semantics, bounded concurrency and source-controlled DQ/quarantine policy. The 100-table fixture is onboarding/config scale proof, not a runtime performance benchmark.

## 8. Product Pipeline operations

Normal desired behavior:

```text
one table FAIL
-> record durable dataset failure/error
-> independent siblings continue
-> failed dependents become BLOCKED
-> all runnable work reaches terminal state
-> parent Pipeline FAILED at end
```

Runbook:

```text
docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md
```

Recovery is classification-driven, not blind rerun:

```text
explicit transient + retryable=true -> bounded RETRY
DQ threshold exceeded -> fix data/rule then REPLAY
DQ with quarantine disabled -> repair then RETRY
reconciliation failure -> investigate before reprocess
BLOCKED dependency -> recover upstream first
UNKNOWN_COMMIT -> reconcile before retry
bounded source gap -> BACKFILL
authoritative reset only -> FULL_REBUILD
```

## 9. Dependency and compatibility model

Production/release dependency remains:

```text
fabric-data-framework==0.3.0
```

The released integration lane downloads immutable v0.3.0 and never substitutes Framework `main`.

The historical framework-next project-contract lane remains separately pinned for `project-init` / `project-validate` compatibility. The independent 0.4 certification-contract lane tracks the current substantive Framework development baseline recorded in `.github/workflows/certification-contract.yml` and `docs/CURRENT_STATUS.md`.

Neither development lane changes `pyproject.toml` or becomes a production runtime dependency.

## 10. Certification project contract

The isolated certification bundle contains representative DatasetConfig values for:

```text
FULL/REPLACE
WATERMARK/SCD1
WATERMARK/SCD2
retry/idempotency
reconciliation fail-closed
Copy
Spark
Warehouse
```

Customer extensions may return facts, receipts and bounded mutation evidence. They may not construct readiness or integration PASS results. Framework remains the PASS authority.

## 11. Dual exact identity invariant

Framework and Customer release identities are independent:

```text
framework candidate:
  candidate_git_sha
  candidate_wheel_sha256

customer/domain release:
  customer_git_sha
  config_bundle_hash
  ReleaseManifest.bundle.release_hash
```

They must never be assumed equal.

## 12. CI/CD promotion boundary

Promote through Git/CI/CD:

```text
Framework/Customer code
DatasetConfig and capture selections
execution-group policy
DQ/reconciliation rules
Notebook/Pipeline definitions
control-plane SQL schema/migrations
non-secret logical binding templates
```

Never copy DEV runtime truth into UAT/PROD:

```text
pipeline_run/dataset_run rows
watermarks/checkpoints
retry/reprocess history
operation-journal state
credentials/tokens
physical workspace/item UUIDs
business data
```

Deployment resolves each environment's physical bindings after deploying the same logical definitions.

## 13. Exact input producer

Owner:

```text
.github/workflows/candidate-business-path-inputs.yml
```

It packages exact customer inputs only. It does not execute live Framework provider evidence runners and does not emit release proof or integration PASS evidence.

## 14. Fail-closed live prerequisites

Current source deliberately keeps real-environment blockers explicit. Exact current blocker names live in `docs/CURRENT_STATUS.md`.

Only reviewed enterprise evidence and approved real provider/fault-controller bindings may replace placeholders. CI-valid input packaging cannot silently become live-ready.

## 15. CI proof model

```text
source-metadata-and-wheel
  source-only validation + Customer wheel

exact-framework-integration
  immutable v0.3.0 integration + Customer tests + release/deployment plan

framework-next-project-contract
  historical exact Framework project-contract SHA + project-validate

customer-certification-contract
  current substantive Framework development SHA
  + execution-group/topology contracts
  + certification extension wheel
  + typed customer input build
  + fail-closed live prerequisite checks
```

A PASS in one lane does not imply another proof class.

## 16. New-domain flow

```text
install approved immutable framework wheel
-> fabric-framework project-init
-> source inventory
-> DatasetConfig + semantic selections
-> execution-group/DQ/reconciliation policy
-> fabric-framework project-validate
-> domain tests
-> GitHub PR/CI
-> deploy same logical topology to DEV
-> DEV integration/certification
-> promote same definitions to UAT with UAT bindings
-> UAT validation/approval
-> promote same definitions to PROD with PROD bindings
```

## 17. Release-certification order

```text
keep source/compatibility lanes green
-> obtain reviewed real Control Plane evidence and approved provider prerequisites
-> explicitly select/freeze one exact Framework candidate only when prerequisites are ready
-> package exact Customer inputs for that exact candidate
-> real integration evidence
-> five live business-path gates
-> release proof bundle
-> candidate certification blockers=[]
-> exact certified-byte Framework promotion
-> immutable v0.4.0
-> Customer production dependency migration
```

No development compatibility lane by itself authorizes release.

## 18. Documentation obligation

Every coherent change cross-checks:

```text
README.md
docs/PROJECT_BLUEPRINT.md
docs/CURRENT_STATUS.md
docs/runbooks/ENTERPRISE_ENVIRONMENT_TOPOLOGY.md
docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md
docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md
docs/runbooks/CERTIFY_FRAMEWORK_0_4.md
examples/enterprise_100_table/README.md
```

Exact implementation/evidence state belongs in `docs/CURRENT_STATUS.md`; stable architecture belongs here.
