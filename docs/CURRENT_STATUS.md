# Current Status — fabric-customer

Last updated: 2026-09-07

## Recovery rule

**GitHub `main` is truth.** For a new conversation, read only:

```text
1. fabric-customer/docs/CURRENT_STATUS.md
2. fabric-customer/docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
3. fabric-customer/docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
4. fabric-data-framework/docs/machine/STATE.md
```

Do not reconstruct current state from old PRs, old chat state, or old certification artifacts.

## Current product truth

```yaml
customer_production_dependency: fabric-data-framework==0.3.0
framework_source_line: 0.4.0-development-unreleased
candidate_status: not_frozen
release_allowed: false
strict_release_ready: false
known_strict_required_blockers: 15

enterprise_topology:
  environments: [DEV, UAT, PROD]
  control_plane: Fabric SQL Database
  control_plane_profile: fabric_sql_database_v1
  medallion_data_plane: Lakehouse / OneLake
  warehouse: optional SQL-first Gold / dimensional serving

default_auth:
  fabric_rest: azure-cli
  sql_runtime: fabric-user
  sql_identity: Microsoft Entra signed-in user
  key_vault_required: false
  key_vault_optional: true

certification_bootstrap:
  source_on_main: true
  verified_feature_merge_sha: be9ac81ca7016dbad09b34bc8f03fb6adebaa421
  verified_customer_main_ci: 34072737246
  verified_customer_main_certification_contract_ci: 34072737241
  preferred_command: python certification/bootstrap.py --apply --environment DEV
  environment_is_fabric_environment_item: false
  environment_config: certification/environments/DEV.json
  repeated_sql_server_database_cli_args_required: false
  resource_mode: resolve_or_create
  exact_framework_artifact_staging: true
  exact_customer_input_bundle_staging: true
  provider_source_seed: setup_only_not_evidence
  warehouse_fixture_bootstrap: true
  control_plane_schema_metadata_bootstrap: true
  bootstrap_terminal_state: READY / NOT_RUN

real_fabric_state:
  repository_owned_bootstrap_source_merged: true
  repository_owned_certification_notebook_deployed: false
  repository_owned_certification_pipeline_deployed: false
  repository_owned_certification_resources_bootstrapped_in_company_fabric: false
  current_framework_real_fabric_certification_executed: false
```

The verified source/CI capability above does **not** claim that a company Fabric workspace has already been mutated. Real deployment/execution state must come from retained bootstrap and Framework evidence.

## Exact Framework executable for certification

Machine-readable selector:

```text
certification/framework-executable.json
```

Current executable identity:

```text
Framework executable SHA   17fbbd8ed2afb14771748a25d3e12d9bf63fe986
Framework main CI run      34010629765
artifact ID                9982333832
artifact name              framework-wheel-17fbbd8ed2afb14771748a25d3e12d9bf63fe986
wheel                      fabric_data_framework-0.4.0-py3-none-any.whl
wheel SHA256               0d7d351548712db3293b00a3b8eb968387f573b542d8fe506c9436a1b9b0a834
selected/frozen            false
real-Fabric result         NOT YET
```

`framework-executable.json` verifies the exact successful-main artifact used for the next certification run. It does not freeze a candidate.

## Environment is the operator key

`--environment DEV` selects `certification/environments/DEV.json`. It does **not** create or use a Fabric Environment item.

The environment document contains only non-secret physical identity/policy: workspace UUID, exact display names and `create_if_missing` policy for the certification Lakehouse, Fabric SQL Database, Warehouse, Copy/Spark/seed jobs, runner/worker Notebooks and child Pipeline, plus bounded bootstrap mutation policy.

Only `.example.json` templates ship with an intentionally invalid all-zero workspace UUID. Copy the example, replace the UUID with the real isolated workspace, review it, and commit `DEV.json` once.

Normal operators no longer repeat:

```text
--control-plane-server
--control-plane-database
--warehouse-server
--warehouse-database
```

Those SQL targets are discovered from the actual resolved Fabric items.

## One-click bootstrap boundary

Normal preparation:

```powershell
python certification/bootstrap.py --apply --environment DEV
```

Fail-closed sequence:

```text
clean exact Customer source
+ exact Framework successful-main artifact verification
-> resolve/create schema-enabled Lakehouse
-> resolve/create Fabric SQL Database Control Plane
-> resolve/create dedicated Warehouse
-> resolve/create repository-owned seed Spark / Copy Job / capture Spark Job
-> resolve/create Lakehouse-bound worker Notebook + child Pipeline + runner Notebook
-> run setup-only seed Spark job for real provider source Delta tables
-> build exact Customer extension/input bundle with real Fabric item UUIDs
-> stage exact Framework + Customer bytes to OneLake
-> apply Warehouse fixtures
-> apply Control Plane schema + exact DatasetConfig metadata
-> write build/certification-bootstrap/DEV/bootstrap-result.json
-> STOP at bootstrap_status=READY, certification_result=NOT_RUN
```

Bootstrap never enables live certification authorization flags and never manufactures PASS, freeze, release-ready, or release-authorized state.

## Repository-owned provider path

The one-click path creates/updates real provider definitions rather than asking the operator to paste pre-existing IDs:

```text
Copy Job:
  dbo.cert_copy_source -> dbo.cert_copy_landing

Spark Job Definition:
  dbo.cert_spark_source + Framework-supplied bounds
  -> dbo.cert_spark_landing
```

The seed Spark job only prepares source Delta tables. Real Copy/Spark certification remains a later explicitly authorized Framework evidence stage. Provider `Completed` alone is not PASS.

## Current strict blockers

```text
control_plane_external_evidence_incomplete
control_plane_external_evidence_not_review_bound
warehouse_real_fault_controller_not_configured
```

Therefore:

```text
candidate_status: not_frozen
release_allowed: false
strict_release_ready: false
release_authorized: false
```

## Production boundary

Production remains pinned to `fabric-data-framework==0.3.0`. Do not change it until immutable Framework `v0.4.0` exists and strict release governance explicitly authorizes migration.

## Normal customer-project baseline

The static framework-next project-contract compatibility pin remains:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

It is separate from the certification executable identity.

The normal project workflow remains:

```text
fabric-framework project-init <repo> --domain <domain>
-> DatasetConfig / semantic selections / domain rules
-> orchestration.execution_group
-> fabric-framework project-validate <repo>
-> GitHub CI
-> DEV -> UAT -> PROD using the same logical topology
```

The enterprise reference remains 100 tables: 50 FULL/REPLACE, 20 WATERMARK/SCD2, 20 WATERMARK/SCD1, and 10 CDC/UPSERT using Debezium / external CDC. That fixture proves onboarding/config scale, not live Fabric performance.

## Exact next real boundary

Customer one-click source is now on `main` and both main CI contracts are green. The next boundary is real isolated DEV Fabric:

```text
create/commit certification/environments/DEV.json with the real isolated DEV workspace UUID
-> az login + gh auth
-> python certification/bootstrap.py --apply --environment DEV
-> retain genuine bootstrap-result.json
-> open/run framework-certification-runner bounded/read-safe first
-> STOP on any real FAIL
-> explicitly authorize live stages only when prerequisites are ready
-> retain genuine Framework evidence
```

No current-source live bootstrap/certification evidence exists yet.

## Canonical operator docs

```text
docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md
docs/runbooks/ENTERPRISE_ENVIRONMENT_TOPOLOGY.md
```
