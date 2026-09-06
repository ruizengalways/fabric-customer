# Current Status — fabric-customer

Last updated: 2026-09-06

## New-conversation recovery checkpoint

**GitHub `main` is truth.** Re-read current Framework and Customer `main` before release/governance decisions. Do not recover candidate identity from chat memory.

Current direction:

```text
Framework 0.4 source is development/unreleased
Customer production runtime remains on released Framework v0.3.0
DEV/UAT/PROD use the same logical enterprise topology
Fabric SQL Database is the canonical Framework operational Control Plane
Lakehouse/OneLake owns Bronze/Silver/Gold business data and quarantine detail
Fabric Warehouse is optional SQL-first Gold/dimensional serving
Customer enterprise topology/reference is merged + independent main-CI proven
Customer candidate-input enterprise profile is fail-closed + independent main-CI proven
Customer Fabric-native deployment/auth path is merged + independent main-CI proven
normal multi-table Pipeline operations/recovery is a first-class product concern
unified real-Fabric certification remains the default certification path
actual company-Fabric certification items are not yet evidenced as deployed
current Framework PR #112 wheel has not yet been executed in real Fabric
strict release evidence is incomplete
no exact Framework candidate is frozen
no 0.4 release is authorized
```

Read in this order after a context reset:

```text
1. fabric-customer/docs/CURRENT_STATUS.md
2. fabric-customer/docs/runbooks/ENTERPRISE_ENVIRONMENT_TOPOLOGY.md
3. fabric-customer/docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md
4. fabric-customer/examples/pipeline_development/README.md
5. fabric-customer/docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
6. fabric-customer/docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
7. fabric-data-framework/docs/machine/STATE.md
8. fabric-data-framework/docs/machine/ENTERPRISE_TOPOLOGY.md
9. fabric-data-framework/docs/human/ENTERPRISE_FABRIC_ARCHITECTURE.md
10. fabric-data-framework/docs/human/PIPELINE_OPERATIONS_AND_RECOVERY.md
11. fabric-data-framework/docs/human/FABRIC_NATIVE_SQL_AUTH.md
12. fabric-data-framework/docs/machine/UNIFIED_CERTIFICATION.md
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

## Enterprise DEV / UAT / PROD topology

DEV is the production architecture at smaller scale. Do not use Lakehouse control tables in DEV and switch to SQL Database in UAT/PROD.

```text
DEV/UAT/PROD Control Plane = Fabric SQL Database
control_plane_profile       = fabric_sql_database_v1
Bronze/Silver/Gold           = Lakehouse / OneLake data plane
Gold SQL/dimensional serving = optional Fabric Warehouse
```

Bronze/Silver/Gold are analytical maturity layers. Lakehouse/Warehouse/SQL Database are workload engines. **Warehouse is optional.** CI/CD promotes code, DatasetConfig, execution-group policy, DQ/reconciliation rules, Fabric item definitions and control-plane migrations; it never promotes DEV runtime rows, watermarks/checkpoints, credentials, business data or physical item UUIDs into UAT/PROD.

Canonical topology runbook: `docs/runbooks/ENTERPRISE_ENVIRONMENT_TOPOLOGY.md`.

## Customer enterprise-topology baseline — PR #27

Customer PR #27 is **MERGED + MAIN CI PROVEN**:

```text
merge/main SHA                      fa495fce622de8a5344bf74ecc52885fe85596f4
PR customer-ci                      33998332579 SUCCESS
PR customer-certification-contract  33998332576 SUCCESS
independent main customer-ci        33998361497 SUCCESS
independent main certification      33998361592 SUCCESS
```

It established Fabric SQL Database = operational Framework Control Plane, Lakehouse/OneLake = medallion business data + quarantine detail, and Warehouse = optional SQL-first Gold/dimensional serving.

Historical PR #27 recovery assertion remains true:

```text
current_pr109_real_fabric_certification_executed = false
```

This line records the historical PR #109 state only; it does not make PR #109 current again.

## Customer candidate-input topology hardening — PR #29

Customer PR #29 is **MERGED + MAIN CI PROVEN**:

```text
merge/main SHA                      1effd5fe283afeb5b960a87e64638f1674433580
PR customer-ci                      34001442382 SUCCESS
PR customer-certification-contract  34001442376 SUCCESS
independent main customer-ci        34001481213 SUCCESS
independent main certification      34001481204 SUCCESS
```

The Customer candidate-input lane exposes only `fabric_sql_database_v1`. Its source-of-truth producer and builder remain:

```text
.github/workflows/candidate-business-path-inputs.yml
certification/build_candidate_inputs.py
```

Framework may support generic alternate relational backends, but the Customer canonical enterprise certification lane fails closed on profile drift. The historical PR #29 checkpoint also recorded `current_pr109_real_fabric_certification_executed = false`; that historical fact remains true.

## Customer project and 100-table product baseline

The normal project path remains:

```text
fabric-framework project-init <repo> --domain <domain>
-> source-controlled DatasetConfig / semantic selections
-> assign execution_group
-> fabric-framework project-validate <repo>
-> GitHub CI
-> deploy same logical topology to DEV
-> validate
-> promote same definitions to UAT/PROD with environment-local bindings
```

One Health domain repo intentionally models 100 tables:

```text
50 FULL      -> REPLACE
20 WATERMARK -> SCD2
20 WATERMARK -> SCD1
10 CDC       -> UPSERT using Debezium/external CDC
```

The historical project-contract compatibility lane remains intentionally pinned to:

```text
FRAMEWORK_NEXT_SHA = 148e02e3fff7861f238296e7554815a6fd49dd0a
```

This lane proves the established `project-init` / `project-validate` transition contract only. It is independent from the current 0.4 certification executable lane.

## Current Framework executable identity — PR #112

Framework PR #112 is the current substantive 0.4 executable baseline. It supersedes PR #109 as current bytes because it adds the Fabric-native Entra SQL runtime while preserving the approved runner authorization gate.

```text
PR                            #112
merge/main SHA                17fbbd8ed2afb14771748a25d3e12d9bf63fe986
latest successful PR CI       34010577594 SUCCESS
independent main framework-ci 34010629765 SUCCESS
Python 3.11                   SUCCESS
Python 3.13                   SUCCESS
build-wheel                   SUCCESS
release-readiness-contract    SUCCESS
```

Exact current executable artifact:

```text
artifact name       framework-wheel-17fbbd8ed2afb14771748a25d3e12d9bf63fe986
artifact ID         9982333832
artifact ZIP digest sha256:07e6f54e9fa4a9b93f4536afd2d0f59754cde4fd33bd26dd3a15ae4b8c2b9791
wheel filename      fabric_data_framework-0.4.0-py3-none-any.whl
wheel SHA256        0d7d351548712db3293b00a3b8eb968387f573b542d8fe506c9436a1b9b0a834
workflow run ID     34010629765
workflow attempt    1
selected/frozen     false
real-Fabric result  NOT YET
```

Fabric-native SQL runtime contract:

```text
database-url = backward-compatible runtime URL lane
fabric-user  = signed-in Fabric Notebook user + non-secret SQL server/database
SQL token audience = https://database.windows.net/
ODBC = Microsoft ODBC Driver 18+
```

The Framework never treats normal `fabric-user` authentication as Warehouse administrator/session-control authority.

PR #109 (`3bd3375b796531e5ca6c7e144e7f50e154cec29f`) remains a historical predecessor and must not be used as the current executable identity after PR #112.

## Customer Fabric-native certification/deployment baseline — PR #31

Customer PR #31 is **MERGED + MAIN CI PROVEN**:

```text
PR                                  #31
merge/main SHA                      b8791ee3f7c575e87d457501ea2e93e40d75fcb6
PR customer-ci                      34016083859 SUCCESS
PR customer-certification-contract  34016083851 SUCCESS
independent main customer-ci        34016136469 SUCCESS
independent main certification      34016136281 SUCCESS
```

PR #31 makes the common certification-item deployment lane Fabric-native:

```text
Fabric REST auth default = azure-cli
SQL runtime auth default = fabric-user
Key Vault optional
alternate automation auth = env-token
```

Default Fabric REST authentication uses the operator's approved Azure CLI user session (`az login` / `az account get-access-token`). The organization-approved Fabric API access token stays process-local; do not paste it into Git, Notebook source, Pipeline JSON, a CLI argument, retained evidence, or chat.

Default SQL authentication uses the signed-in Fabric Notebook user's Microsoft Entra identity and non-secret Control Plane/Warehouse server + database names. Key Vault remains an optional enterprise compatibility lane rather than a prerequisite for ordinary Fabric workspace users. The existing `env-token` lane remains available for approved automation.

The deployer remains fail-closed: DEV/UAT only, explicit `--apply`, duplicate display names rejected, long-running operations polled, Fabric API host boundary enforced, retained output non-secret, and `certification_result = NOT_RUN`.

Merged/green source does **not** prove the company workspace was mutated:

```text
repository_owned_certification_notebook_deployed = false / not yet evidenced
repository_owned_certification_pipeline_deployed = false / not yet evidenced
current_pr112_real_fabric_certification_executed = false
```

Run deploy_fabric_items.py once only against the intended isolated DEV/UAT workspace, then retain only its non-secret deployment result.

## Customer product Pipeline operations baseline — PR #25

Customer PR #25 is **MERGED + MAIN CI PROVEN**:

```text
merge/main SHA                      1d70fe26baf3ceef1be7c0b0cd359f330316e0ee
PR customer-ci                      33969274525 SUCCESS
PR customer-certification-contract  33969274509 SUCCESS
independent main customer-ci        33969382068 SUCCESS
independent main certification      33969382063 SUCCESS
```

It owns the normal multi-table Pipeline operations/recovery examples:

```text
health_full_refresh.json
health_scd2.json
health_scd1.json
health_debezium.json
FAIL_AT_END
```

For daily incidents use `docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md`; whole-Pipeline blind retry is not the default repair strategy.

## Historical certification/deployment tooling baseline — PR #23

Customer PR #23 remains the **merged substantive certification/deployment tooling baseline** that originally introduced the reusable certification Notebook/Pipeline and DEV/UAT deployer:

```text
substantive merge/main SHA          88d7c3b7b473ad84b5d96aa472293ae24c055c88
PR customer-ci                      33963661173 SUCCESS
PR customer-certification-contract  33963661167 SUCCESS
independent main customer-ci        33963703737 SUCCESS
independent main certification      33963703747 SUCCESS
```

PR #31 is the current auth/deployment hardening on top of that tooling. Runbook: `docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md`.

## Historical first company-Fabric bounded result — PR #99 old bytes only

Historical evidence remains bound to exact old bytes only:

```text
Framework SHA        303683729c4915d78200d463a6def01c8de9eae6
main CI              33381666892
artifact ID          9753976212
wheel SHA256         0638c95c19ebcc43ec4ec462b7f960a164209874223517e3f74b951264b0eaf6
environment          DEV
```

Observed old-byte result included `identity.exact`, Lakehouse smoke, FULL/REPLACE, SCD1, SCD2, retry/idempotency and reconciliation fail-closed PASS. `warehouse.commit` and ambiguous-commit were `NOT_RUN`; release authorized was false. This historical result must not be projected onto PR #112 bytes.

## Control Plane and strict evidence

Selected enterprise certification profile remains:

```text
environment = DEV
control_plane_profile = fabric_sql_database_v1
```

Seven real enterprise evidence references remain required: backend service identity, identity access control, network security, backup/restore, availability/recovery, monitoring/alerting and retention/governance.

Current blockers remain honest:

```text
control_plane_external_evidence_incomplete
control_plane_external_evidence_not_review_bound
warehouse_real_fault_controller_not_configured
```

Never fabricate placeholders to clear them. A dedicated DEV Warehouse is not by itself an approved ambiguous-COMMIT fault controller, and normal signed-in Fabric user identity is not automatically session-termination authority.

## Next real-Fabric phase

Use exact Framework PR #112 bytes and current Customer main after PR #31:

```text
1. use an isolated approved DEV certification workspace
2. use/provision the dedicated DEV Fabric SQL Database as canonical Control Plane
3. run az login with the approved operator identity
4. run deploy_fabric_items.py once with --apply using default azure-cli + fabric-user auth
5. pass only non-secret Control Plane/Warehouse server + database identities; Key Vault optional
6. retain build/fabric-items/deployment-result.json; certification_result = NOT_RUN
7. verify separate real item-read, Pipeline, Copy and Spark UUID bindings
8. build exact Customer candidate-input artifact against Framework SHA 17fbbd8ed2afb14771748a25d3e12d9bf63fe986 and wheel SHA 0d7d351548712db3293b00a3b8eb968387f573b542d8fe506c9436a1b9b0a834
9. profile must be fabric_sql_database_v1
10. upload/use exact Framework wheel + CANDIDATE.json + SHA256SUMS and exact Customer inputs
11. run bounded real-Fabric certification first
12. STOP on any real bounded FAIL
13. keep missing external evidence/fault controller BLOCKED/NOT_RUN
```

No live Fabric deployment or current-byte PASS is claimed by this checkpoint.

## Strict release path remains later

Framework 0.4 release still requires reviewed real Control Plane evidence, exact review binding, approved reachable Warehouse ambiguous-COMMIT control, explicit session-termination authorization where required, explicit selection/freeze of a new exact Framework candidate only after prerequisites are genuinely ready, strict integration evidence, five live business-path proofs, release proof bundle, blockers `[]`, and promotion of exact certified bytes without rebuild.

Only after immutable `v0.4.0` exists may Customer production pin migration be considered.
