# Current Status — fabric-customer

Last updated: 2026-09-05

## New-conversation recovery checkpoint

**GitHub `main` is truth.** Re-read current Framework and Customer `main` before release/governance decisions. Do not recover candidate identity from chat memory.

Current direction:

```text
Framework 0.4 source is development/unreleased
Customer production runtime remains on released Framework v0.3.0
normal multi-table Pipeline operations/recovery is a first-class product concern
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

Do not change the Customer production dependency until immutable Framework `v0.4.0` exists and release governance explicitly permits migration. A bounded/manual/unified certification result cannot silently freeze/select a candidate or publish a release; `release_authorized=false` remains structural for unified certification.

## Customer project and 100-table product baseline

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

The project compatibility lane remains intentionally pinned to its historical exact Framework-next project-contract SHA:

```text
FRAMEWORK_NEXT_SHA = 148e02e3fff7861f238296e7554815a6fd49dd0a
```

That SHA is independent from the current 0.4 certification compatibility SHA. Do not replace one with the other merely because both are Framework development lines.

## Current Framework executable identity — PR #107

Current Framework substantive executable baseline:

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

Exact current executable artifact:

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

PR #107 changes executable bytes and adds `FAIL_AT_END`, dataset fault isolation, dependency-aware `BLOCKED`, parent aggregate error persistence, Control Plane schema v5, source-controlled `ExecutionGroupPolicy`, DQ/quarantine budgets, governed full quarantine detail and conservative recovery planning.

The former PR #105 wheel is historical old bytes for future certification purposes. PR #105 remains the one-call runtime/first-time Control Plane bootstrap milestone and PR #104 remains the durable seven-parameter Pipeline-child milestone, but neither exact artifact is current.

## Customer product Pipeline operations baseline — PR #25

Customer PR #25 is **MERGED + MAIN CI PROVEN** and is now the normal multi-table Pipeline operations/reference baseline:

```text
PR                                  #25
merge/main SHA                      1d70fe26baf3ceef1be7c0b0cd359f330316e0ee
PR customer-ci                      33969274525 SUCCESS
PR customer-certification-contract  33969274509 SUCCESS
independent main customer-ci        33969382068 SUCCESS
independent main certification      33969382063 SUCCESS
```

PR #25 adds:

```text
examples/pipeline_development/README.md
docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md
examples/pipeline_development/framework_0_4/execution-groups/
  health_full_refresh.json
  health_scd2.json
  health_scd1.json
  health_debezium.json
```

All four execution-group examples use `FAIL_AT_END`, bounded concurrency, governed FULL quarantine detail, DQ budgets and real per-table overrides tied to the existing 100-table manifest. The 0.4 certification compatibility lane validates them against Framework PR #107 SHA `4c8ad9994f3800e901c146b919f85454d78f080e` and proves group-policy bytes alter the config bundle identity.

These examples are forward-looking Framework 0.4 contracts only. They are **not** promoted into the production runtime while Customer remains pinned to:

```text
fabric-data-framework==0.3.0
```

## Customer certification/deployment tooling baseline

Customer PR #23 remains the merged substantive certification/deployment tooling baseline:

```text
PR                                  #23
substantive merge/main SHA          88d7c3b7b473ad84b5d96aa472293ae24c055c88
PR customer-ci                      33963661173 SUCCESS
PR customer-certification-contract  33963661167 SUCCESS
independent main customer-ci        33963703737 SUCCESS
independent main certification      33963703747 SUCCESS
```

This is the merged substantive certification/deployment tooling baseline. It owns the reusable certification Notebook/Pipeline source plus fail-closed DEV/UAT Fabric item deployer.

The deployer contract remains: DEV/UAT only, explicit `--apply`, runtime token only, duplicate display names fail closed, long-running operations are polled, operation/pagination URLs cannot leave the approved Fabric API host, retained output is non-secret, and `certification_result = NOT_RUN`.

Merged/green deployer source does **not** prove the company workspace was mutated. Current actual deployment truth remains:

```text
repository_owned_certification_notebook_deployed = false / not yet evidenced
repository_owned_certification_pipeline_deployed = false / not yet evidenced
current_pr107_real_fabric_certification_executed = false
```

The immediate live step still requires an organization-approved Fabric API access token and an isolated approved DEV/UAT workspace. Run deploy_fabric_items.py once only when those prerequisites are real; retain only its non-secret result. See `DEPLOY_CERTIFICATION_FABRIC_ITEMS.md`.

## Normal business Pipeline recovery boundary

For daily/production incidents use `docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md`, not certification tooling.

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

Whole-Pipeline blind retry is not the default incident response. For Debezium/external CDC, Framework must not invent a competing checkpoint owner; if retained source log no longer covers a gap, do not claim lossless replay.

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
release authorized              false
```

Do not reuse those PASS values for PR #107 bytes. The form was a result recorder; PASS came from actual checks executed in company Fabric.

## Control Plane and strict evidence

Selected certification profile remains:

```text
environment = DEV
control_plane_profile = fabric_sql_database_v1
```

Framework does not scan the workspace and guess a SQL Database. Runtime-only bindings supply the approved Control Plane/Warehouse URLs. A new dedicated certification SQL Database may use `allow_control_plane_migration=True` only after bounded PASS and exact Customer/Framework identity.

Seven real enterprise evidence references remain required:

```text
backend_service_identity_reference
identity_access_control_reference
network_security_reference
backup_restore_reference
availability_recovery_reference
monitoring_alerting_reference
retention_governance_reference
```

Current blockers remain honest:

```text
control_plane_external_evidence_incomplete
control_plane_external_evidence_not_review_bound
warehouse_real_fault_controller_not_configured
```

Never fabricate placeholders to clear them. A dedicated DEV Warehouse is not by itself an approved ambiguous-COMMIT fault controller, and Admin-level exact-session termination remains separately authorized. Never fault inject against shared/PROD Warehouse.

## Next real-Fabric phase

Use the exact current PR #107 Framework artifact unless executable source changes again:

```text
1. obtain organization-approved Fabric API token for isolated DEV certification workspace
2. run deploy_fabric_items.py once and retain non-secret Notebook/Pipeline UUID result
3. prepare dedicated Warehouse fixture tables
4. verify separate real item-read/Copy/Spark UUIDs
5. build exact Customer candidate-input artifact against PR #107 wheel + exact Customer SHA
6. upload exact Framework wheel/CANDIDATE/SHA256SUMS + customer-inputs
7. run bounded certification first
8. STOP on any real bounded FAIL
9. first-time Control Plane bootstrap only for a new dedicated certification DB
10. proceed to ordinary live stages only with approved mutations
11. keep missing external evidence/fault controller as BLOCKED/NOT_RUN
```

## Strict release path remains later

Framework 0.4 release still requires reviewed real Control Plane evidence, exact review binding, approved reachable Warehouse ambiguous-COMMIT control, explicit session-termination authorization where required, explicit selection/freeze of a **new exact** Framework candidate only after prerequisites are genuinely ready, strict integration evidence, five live business-path proofs, release proof bundle, blockers `[]`, and promotion of exact certified bytes without rebuild.

Only after immutable `v0.4.0` exists may Customer production pin migration be considered.
