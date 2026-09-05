# Current Status — fabric-customer

Last updated: 2026-09-05

## New-conversation recovery checkpoint

**GitHub `main` is truth.** Re-read current Framework and Customer `main` before release/governance decisions. Do not recover candidate identity from chat memory.

Current direction:

```text
Framework 0.4 source is development/unreleased
Customer production runtime remains on released Framework v0.3.0
normal multi-table Pipeline operations/recovery is now a first-class product concern
unified real-Fabric certification remains the default certification path
reusable certification Pipeline/worker and DEV/UAT item deployer are merged + main-CI proven
actual company-Fabric certification items from that deployer are not yet evidenced as deployed
current Framework PR #107 wheel has not yet been executed in real Fabric
strict release evidence is incomplete
no exact Framework candidate is frozen
no 0.4 release is authorized
```

Read in this order after a context reset:

```text
1. fabric-customer/docs/CURRENT_STATUS.md
2. fabric-customer/docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md
3. fabric-customer/examples/pipeline_development/README.md
4. fabric-customer/docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
5. fabric-customer/docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
6. fabric-data-framework/docs/machine/STATE.md
7. fabric-data-framework/docs/human/PIPELINE_OPERATIONS_AND_RECOVERY.md
8. fabric-data-framework/docs/machine/UNIFIED_CERTIFICATION.md
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

Do not change the Customer production dependency until immutable Framework `v0.4.0` exists and release governance explicitly permits migration. A bounded/manual/unified certification result cannot silently freeze/select a candidate or publish a release; `release_authorized=false` remains structural for the unified report.

## Customer project / 100-table product baseline

The normal reusable Customer-project contract remains:

```text
fabric-framework project-init <repo> --domain <domain>
-> source-controlled DatasetConfig / semantic selections
-> assign execution_group
-> fabric-framework project-validate <repo>
-> GitHub CI
-> approved DEV/UAT deployment
```

The one-repo Health reference remains:

```text
50 FULL      -> REPLACE
20 WATERMARK -> SCD2
20 WATERMARK -> SCD1
10 CDC       -> UPSERT using Debezium/external CDC
```

The `customer-ci` project compatibility lane remains intentionally pinned to its historical exact Framework-next project-contract SHA:

```text
FRAMEWORK_NEXT_SHA = 148e02e3fff7861f238296e7554815a6fd49dd0a
```

That SHA is independent from the current 0.4 certification compatibility SHA. Do not replace one with the other merely because both are Framework development lines.

Normal Pipeline development guidance now lives in:

```text
examples/pipeline_development/README.md
docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md
```

The forward-looking 0.4 examples cover all four Health execution groups and use `FAIL_AT_END`, bounded concurrency, DQ/quarantine budgets and per-table overrides. They are not production runtime config while Customer remains on v0.3.0.

## Current Framework executable identity — PR #107

Current Framework `main` substantive executable baseline is PR #107:

```text
PR                            #107
merge/main SHA                4c8ad9994f3800e901c146b919f85454d78f080e
PR framework-ci               33967940246 SUCCESS
independent main framework-ci 33968014547 SUCCESS
Python 3.11                   SUCCESS
Python 3.13                   SUCCESS
build-wheel                   SUCCESS
release-readiness-contract    SUCCESS
```

Exact current main artifact:

```text
artifact name       framework-wheel-4c8ad9994f3800e901c146b919f85454d78f080e
artifact ID         9970044954
artifact ZIP digest sha256:7c297a36eb3146356f2ba7a39e87e9fee3f2ea53bc9a9711cbebe9031ec00a97
wheel filename      fabric_data_framework-0.4.0-py3-none-any.whl
wheel SHA256        06d4a9ca948693c87a658a34e8c4fccb42439a7f9f67c44985ac726dedb4e04d
workflow run ID     33968014547
workflow attempt    1
selected/frozen     false
real-Fabric result  NOT YET
```

PR #107 changes executable bytes and adds:

```text
FAIL_AT_END parent Pipeline aggregation
dataset fault isolation + dependency BLOCKED semantics
pipeline_run aggregate error persistence
Control Plane schema v5 additive migration
source-controlled ExecutionGroupPolicy
DQ enabled/quarantine enabled/detail-mode contracts
absolute + fractional quarantine budgets
governed full quarantine payload retention
conservative recovery classification/planning
```

Therefore the former PR #105 wheel (`13c9c769...`) is historical old bytes for future certification purposes. Any real-Fabric PASS for older Framework bytes cannot be projected onto PR #107.

PR #105 remains the historical one-call runtime/first-time Control Plane bootstrap milestone, and PR #104 remains the durable seven-parameter Pipeline-child milestone. Their capabilities remain in current source, but their exact wheel identities are not current.

## Current Customer substantive deployment baseline

Customer PR #23 remains the merged substantive certification/deployment tooling baseline:

```text
PR                                  #23
substantive merge/main SHA          88d7c3b7b473ad84b5d96aa472293ae24c055c88
PR customer-ci                      33963661173 SUCCESS
PR customer-certification-contract  33963661167 SUCCESS
independent main customer-ci        33963703737 SUCCESS
independent main certification      33963703747 SUCCESS
```

Customer PR #24 is a later documentation/recovery checkpoint:

```text
Customer main before the current operations-reference change
c0c01c9f84b3922a558dd05e31bd0cc02ed01099
```

The current operations-reference change adds the 0.4 execution-group examples, normal Pipeline recovery runbook and CI compatibility update. Its exact merged Customer `main` SHA is recorded in the next post-merge checkpoint rather than guessed in advance.

The Customer production dependency remains exactly:

```text
fabric-data-framework==0.3.0
```

The separate certification-contract CI lane now validates Customer certification and 0.4 operations examples against Framework PR #107 source `4c8ad9994f3800e901c146b919f85454d78f080e`.

## Reusable certification Pipeline + deployer truth

Merged substantive source includes:

```text
certification/fabric_items/
  deploy_fabric_items.py
  render_fabric_items.py
  notebook/certification-pipeline-worker.ipynb
  pipeline/pipeline-content.template.json
  sql/warehouse-certification-fixtures.sql

certification/project/config/certification/pipeline-worker.json
certification/extensions/src/fabric_customer_certification_extensions/pipeline_worker.py
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

The deployer remains fail-closed: DEV/UAT only, explicit `--apply`, runtime token only, duplicate display names rejected, LRO polling bounded to the approved Fabric host, non-secret retained output, and `certification_result = NOT_RUN`.

Merged/green deployment code does **not** mean the company workspace was mutated. Current actual deployment truth remains:

```text
repository_owned_certification_notebook_deployed = false / not yet evidenced
repository_owned_certification_pipeline_deployed = false / not yet evidenced
current_pr107_real_fabric_certification_executed = false
```

The immediate live step still requires an organization-approved Fabric API access token and an isolated approved DEV/UAT workspace. Run `deploy_fabric_items.py` once only when those prerequisites are real; retain only its non-secret result.

## Historical first company-Fabric bounded result — PR #99 old bytes only

The first company-Fabric bounded execution remains historical evidence for its exact PR #99 artifact only:

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
manual release authorized       false
```

Do not reuse those PASS values for PR #107 bytes. The form was a result recorder; PASS came from actual checks executed in company Fabric.

## Control Plane configuration and strict evidence

Selected certification profile remains:

```text
environment = DEV
control_plane_profile = fabric_sql_database_v1
```

Framework does not scan the workspace and guess a SQL Database. `runner-config.json` declares the runtime variable name; the Notebook/runtime supplies the actual approved value.

A newly created dedicated certification SQL Database may use the explicit first-time path only after bounded PASS + exact Customer/Framework identity:

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

Seven real enterprise evidence references are still required for strict Control Plane certification:

```text
backend_service_identity_reference
identity_access_control_reference
network_security_reference
backup_restore_reference
availability_recovery_reference
monitoring_alerting_reference
retention_governance_reference
```

Current blocker semantics remain honest:

```text
control_plane_external_evidence_incomplete
control_plane_external_evidence_not_review_bound
warehouse_real_fault_controller_not_configured
```

Never fabricate placeholders to clear them.

## Warehouse strict evidence

A dedicated DEV Warehouse is not by itself an approved ambiguous-COMMIT fault controller. Do not substitute ad-hoc SQL/synthetic exceptions for the Framework-approved runner. Admin-level exact-session termination remains separately authorized and must never be inferred from ordinary live-mutation permission. Never fault inject against shared/PROD Warehouse.

## Normal business Pipeline recovery boundary

For daily/production incidents, use `docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md` rather than certification tooling.

Default repair mapping:

```text
explicit transient + retryable=true -> bounded RETRY
DQ threshold exceeded -> fix data/rule then REPLAY
DQ failure with quarantine disabled -> fix data/rule/config then RETRY
reconciliation fail -> investigate before reprocess
BLOCKED dependency -> recover upstream first
UNKNOWN_COMMIT -> reconcile target/operation evidence before retry
bounded source gap -> BACKFILL
authoritative reset only -> FULL_REBUILD
```

Whole-Pipeline blind retry is not the default incident response.

## Next real-Fabric phase

Use the exact current PR #107 artifact unless Framework executable source changes again:

```text
1. obtain organization-approved Fabric API token for isolated DEV certification workspace
2. run deploy_fabric_items.py once and retain non-secret Notebook/Pipeline UUID result
3. prepare dedicated Warehouse fixture tables
4. verify separate real item-read/Copy/Spark UUIDs
5. build exact Customer candidate-input artifact against PR #107 wheel + exact selected Customer SHA
6. upload exact Framework wheel/CANDIDATE/SHA256SUMS + customer-inputs
7. run bounded certification first
8. STOP on any real bounded FAIL
9. first-time Control Plane bootstrap only for a new dedicated certification DB
10. proceed to ordinary live stages only with approved mutations
11. keep missing external evidence/fault controller as BLOCKED/NOT_RUN
```

## Strict release path remains later

Framework 0.4 release still requires complete reviewed real Control Plane evidence, exact review binding, approved reachable Warehouse ambiguous-COMMIT control, explicit session-termination authorization where required, then explicit selection/freeze of a **new exact** Framework candidate, strict integration evidence, five live business-path proofs, release proof bundle, blockers `[]`, and promotion of exact certified bytes without rebuild.

Only after immutable `v0.4.0` exists may Customer production pin migration be considered.
