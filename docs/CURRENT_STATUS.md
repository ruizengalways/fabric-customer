# Current Status — fabric-customer

Last updated: 2026-09-05

## New-conversation recovery checkpoint

**GitHub `main` is truth.** Re-read current Framework and Customer `main` before making release/governance decisions. Do not recover candidate identity from chat memory.

Current project direction:

```text
Framework 0.4 source is development/unreleased
Customer production runtime remains on released Framework v0.3.0
unified real-Fabric certification is the default test path
reusable certification Pipeline/worker is merged and CI-proven in Customer
actual company-Fabric certification items have not yet been deployed from this source
current Framework PR #105 wheel has not yet been executed in real Fabric
strict release evidence is still incomplete
no exact Framework candidate is frozen
no 0.4 release is authorized
```

Read in this order after a context reset:

```text
1. fabric-customer/docs/CURRENT_STATUS.md
2. fabric-customer/docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
3. fabric-customer/docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
4. fabric-customer/docs/runbooks/CONTROL_PLANE_EXTERNAL_EVIDENCE_REVIEW.md
5. fabric-data-framework/docs/machine/STATE.md
6. fabric-data-framework/docs/machine/UNIFIED_CERTIFICATION.md
7. fabric-data-framework/docs/human/ONE_CALL_CERTIFICATION_RUNTIME.md
8. fabric-data-framework/docs/human/FABRIC_PIPELINE_CHILD_CONTRACT.md
```

## Hard governance locks

```yaml
public_framework_release: v0.3.0
framework_source_line: 0.4.0-development-unreleased
candidate_status: not_frozen
release_allowed: false
unified_certification_release_authorized: false
customer_production_dependency: fabric-data-framework==0.3.0
strict_release_ready: false
known_strict_required_blockers: 15
```

Do not change the Customer production dependency until immutable Framework `v0.4.0` exists and release governance explicitly permits migration.

A bounded/manual/unified certification result cannot silently freeze/select a candidate and cannot publish a release. `UnifiedCertificationReport.release_authorized=false` remains structural.

## Customer project / 100-table product baseline

The certification work does not replace the normal reusable Customer-project contract. The repo still supports the product-grade one-repo domain model used by the 100-table Health example, including Full, SCD1, SCD2 and Debezium-style capture selections.

The ordinary project workflow remains:

```text
fabric project-init
-> source-controlled DatasetConfig / semantic selections
-> fabric project-validate
-> GitHub CI
-> approved environment deployment
```

The `customer-ci` project compatibility lane is separately pinned to the exact Framework-next source SHA:

```text
FRAMEWORK_NEXT_SHA = 148e02e3fff7861f238296e7554815a6fd49dd0a
```

This SHA is part of the existing 100-table project/bootstrap contract and is independent from the 0.4 certification compatibility SHA documented below. Do not replace one with the other merely because both point at Framework development source.

## Current Framework substantive executable source baseline

Framework PR #105 is the current substantive executable source baseline used by the Customer certification compatibility lane:

```text
PR                            #105
merge/main SHA                cb9f9be77a98a0a5aa8c5f85e0fa3d92697c60f0
PR framework-ci               33961766325 SUCCESS
independent main framework-ci 33961827610 SUCCESS
Python 3.11                   SUCCESS
Python 3.13                   SUCCESS
build-wheel                   SUCCESS
release-readiness-contract    SUCCESS
```

Exact executable Framework artifact from that independent main run:

```text
artifact name       framework-wheel-cb9f9be77a98a0a5aa8c5f85e0fa3d92697c60f0
artifact ID         9968172160
artifact ZIP digest sha256:2b746b43237d221331ba6418459b2d2d3f62dfc3eaf98d4e3897384787bbefa6
wheel filename      fabric_data_framework-0.4.0-py3-none-any.whl
wheel SHA256        13c9c7696f9c657243af1133731bf58600cffb3a78f77bede606a1b00a6c2c79
workflow run ID     33961827610
workflow attempt    1
```

PR #105 owns the one-call runtime bridge and explicit first-time dedicated Control Plane bootstrap. Exact runner-declared runtime names are temporarily made visible to Customer/domain extension entry points during `certify()`, then the prior process environment is restored. First-time `allow_control_plane_migration=True` requires bounded PASS + exact Customer identity before current schema and exact Customer semantic metadata are materialized.

Framework PR #104 is the immediately preceding durable-Pipeline milestone:

```text
PR/main SHA        94cc0c90631a6582c8ba84911bc100195e2fbb86
main CI            33959169173 SUCCESS
capability          reusable seven-parameter Fabric Pipeline child contract
```

The remote child validates exact DatasetConfig/effective-config/execution-plan identity and persists the exact terminal `DatasetRunAudit`/`DatasetDispatchOutcome`. Fabric provider `Completed` alone is never semantic PASS.

Because PR #105 changed Framework source, all earlier real-Fabric executions remain historical evidence only for their exact old wheel bytes. **There is not yet a real-Fabric execution result for the PR #105 wheel.**

## Current Customer substantive certification/deployment source baseline

Customer PR #21 is **MERGED + MAIN CI PROVEN**.

```text
PR                                  #21
substantive merge/main SHA          cedba6673f08ddfda9cae2e29a27cc6ecc768b58
PR customer-ci                      33962244955 SUCCESS
PR customer-certification-contract  33962244950 SUCCESS
independent main customer-ci        33962296475 SUCCESS
independent main certification      33962296508 SUCCESS
```

This substantive SHA is the source baseline for the reusable certification Pipeline/worker implementation and deployment runbook. A later documentation-only checkpoint SHA does **not** replace `cedba667...` as the executable Customer certification/deployment source baseline unless a new exact Customer candidate-input artifact is intentionally built from that later SHA.

The Customer production dependency remains exactly:

```text
fabric-data-framework==0.3.0
```

The certification-contract CI lane intentionally validates Customer certification source against Framework PR #105 source. This compatibility lane is separate from the released Customer production dependency.

## Reusable certification Pipeline reference — merged product surface

The following repository-owned surface is merged on Customer `main`:

```text
certification/fabric_items/
  render_fabric_items.py
  notebook/certification-pipeline-worker.ipynb
  pipeline/pipeline-content.template.json
  sql/warehouse-certification-fixtures.sql

certification/project/config/certification/pipeline-worker.json
certification/extensions/src/fabric_customer_certification_extensions/pipeline_worker.py
certification/extensions/src/fabric_customer_certification_extensions/business_driver.py
certification/extensions/src/fabric_customer_certification_extensions/business_observer.py
docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
```

The Data Pipeline forwards exactly:

```text
framework_pipeline_run_id
framework_dataset_run_id
dataset_id
run_mode
attempt
effective_config_hash
execution_plan_hash
```

The worker supports the five representative live business paths:

```text
full.replace
watermark.scd1
watermark.scd2
retry.idempotency
reconciliation.fail_closed
```

Business-path driver/observer consume the same exact runtime binding:

```text
WAREHOUSE_DATABASE_URL
```

There is no separate JSON-wrapped business-path secret channel in the current reference design.

The Fabric-item renderer accepts non-secret deployment bindings only. Runtime Control Plane/Warehouse URLs remain secret/runtime values and are not committed into item templates or retained certification evidence.

**Merged + CI-proven source is not the same thing as deployed Fabric items.** No claim is made here that the repository-owned Notebook/Pipeline/fixtures already exist in the company Fabric workspace. The next company-Fabric phase must deploy them to the isolated approved DEV workspace and record their environment-local item UUIDs.

## Historical first company-Fabric bounded result — old bytes only

The first real company-Fabric bounded execution remains valid historical evidence for its exact Framework PR #99 artifact only:

```text
Framework SHA        303683729c4915d78200d463a6def01c8de9eae6
main CI              33381666892
artifact ID          9753976212
wheel SHA256         0638c95c19ebcc43ec4ec462b7f960a164209874223517e3f74b951264b0eaf6
environment          DEV
```

Observed bounded result:

```text
identity.exact                  PASS
lakehouse.smoke                 PASS
full.replace                    PASS
watermark.scd1                  PASS
watermark.scd2                  PASS
retry.idempotency               PASS
reconciliation.fail_closed      PASS
warehouse.commit                NOT_RUN
warehouse.ambiguous_commit      NOT_RUN
manual Notebook certification   CERTIFIED
manual Admin Override           not used
manual release authorization    false
```

That run must **not** be copied forward as proof for Framework PR #104/#105 bytes. The historical certification form was a result recorder, not the source of PASS; PASS values came from actual bounded checks executed in company Fabric.

## Control Plane configuration and real evidence

Selected certification profile remains conceptually:

```text
environment = DEV
control_plane_profile = fabric_sql_database_v1
```

The Framework does not scan the workspace and guess a SQL Database. The exact Customer runner config declares the runtime variable name and the Notebook/runtime supplies the actual approved value:

```text
runner-config.json:
  control_plane_database_url_env_var = CONTROL_PLANE_DATABASE_URL

runtime only:
  CONTROL_PLANE_DATABASE_URL = <actual approved dedicated certification DB URL>
```

For a newly created dedicated certification SQL Database, first-time bootstrap is explicitly:

```python
report = certify(
    spark=spark,
    runtime_environment={
        "CONTROL_PLANE_DATABASE_URL": control_plane_database_url,
        "WAREHOUSE_DATABASE_URL": warehouse_database_url,
    },
    allow_live_mutations=True,
    allow_control_plane_migration=True,
)
```

This first runs exact bounded checks, verifies exact Customer/Framework identity, then applies current Control Plane schema plus exact Customer semantic metadata. Normal reruns keep migration disabled.

Seven enterprise Control Plane evidence references still need real internal evidence/review before strict approved Control Plane certification can PASS:

```text
backend_service_identity_reference
identity_access_control_reference
network_security_reference
backup_restore_reference
availability_recovery_reference
monitoring_alerting_reference
retention_governance_reference
```

Current blocker semantics remain real:

```text
control_plane_external_evidence_incomplete
control_plane_external_evidence_not_review_bound
```

Do not fabricate public placeholder evidence to clear them.

## Warehouse strict evidence

A dedicated DEV Warehouse exists conceptually for the certification lane, but strict normal/fault evidence remains governed.

Current blocker:

```text
warehouse_real_fault_controller_not_configured
```

A dedicated Warehouse alone is not a real ambiguous-COMMIT fault controller. Do not substitute ad-hoc SQL or synthetic exceptions for the Framework-approved Warehouse evidence runner.

Admin-level exact-session termination must remain separately authorized. `allow_live_mutations=True` never implies session-termination permission.

Never fault inject against a shared/PROD Warehouse.

## Recovery checkpoint versus executable baseline

This file may be updated in a later docs-only PR so a new conversation can recover current truth. Keep the identities separate:

```text
Framework substantive executable source baseline  cb9f9be77a98a0a5aa8c5f85e0fa3d92697c60f0
Framework exact executable wheel SHA256           13c9c7696f9c657243af1133731bf58600cffb3a78f77bede606a1b00a6c2c79
Customer substantive certification source         cedba6673f08ddfda9cae2e29a27cc6ecc768b58
later docs-only recovery checkpoint SHA            informational only
```

A docs-only commit does not create a new real-Fabric PASS, does not freeze a candidate, does not authorize a release, and does not by itself require rerunning Fabric. If executable Framework source changes, however, a new exact Framework main artifact and new real-Fabric execution are required.

## Next repository step

Update Framework `docs/machine/STATE.md` and its consistency tests so:

```text
PR #105 is current substantive Framework source
PR #21 is current substantive Customer certification/deployment source
PR #99 is historical first-Fabric old-byte evidence only
candidate_status remains not_frozen
release_allowed remains false
strict blocker count remains 15
```

After both repo recovery checkpoints are merged + main-CI proven, the repository side is ready for a brand-new conversation without relying on chat history.

## Next real-Fabric phase — only after recovery checkpoints are settled

Use the exact substantive identities above, then follow:

```text
1. deploy repository-owned certification Notebook/Pipeline/fixtures to isolated DEV
2. record actual environment-local item UUIDs
3. build exact Customer candidate-input artifact for the exact Framework PR #105 wheel + exact selected Customer source SHA
4. upload exact Framework wheel/CANDIDATE/SHA256SUMS + customer-inputs
5. run bounded certification first
6. STOP on any real bounded FAIL
7. first-time Control Plane bootstrap only for a newly created dedicated certification DB
8. proceed to ordinary live stages only with approved mutations
9. keep missing external evidence/fault controller as BLOCKED/NOT_RUN
```

Do not reuse the historical PR #99 PASS values for the PR #105 wheel.

## Strict release path remains later

Even after reusable Pipeline automation works, full Framework 0.4 release still requires:

```text
complete reviewed real Control Plane external evidence
exact review binding
approved reachable Warehouse ambiguous-COMMIT fault controller
explicit session-termination authorization when required
NEW exact Framework candidate explicitly selected/frozen only after prerequisites are genuinely ready
strict integration evidence
five live business-path proofs
release proof bundle
candidate certification with blockers=[] / release_ready=true
release exact certified bytes without rebuilding
```

Only after immutable `v0.4.0` exists may Customer production pin migration be considered.
