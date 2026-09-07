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
  preferred_command: python certification/bootstrap.py --apply --environment DEV
  environment_is_fabric_environment_item: false
  environment_config: certification/environments/DEV.json
  repeated_sql_server_database_cli_args_required: false
  lakehouse_resolve_or_create: true
  fabric_sql_database_resolve_or_create: true
  warehouse_resolve_or_create: true
  copy_job_resolve_or_create: true
  spark_job_resolve_or_create: true
  seed_spark_job_resolve_or_create: true
  runner_notebook_deploy: true
  worker_notebook_deploy: true
  pipeline_deploy: true
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

The source capability above does **not** claim that a company Fabric workspace has already been mutated. A real bootstrap result must supply the item UUIDs/actions, and Framework-generated evidence must supply execution outcomes.

## Exact Framework executable for certification

Machine-readable source:

```text
certification/framework-executable.json
```

Current identity:

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

`framework-executable.json` selects the exact next executable bytes and validates their successful main-CI provenance. It is not a candidate freeze.

## Environment is the operator key

`--environment DEV` selects:

```text
certification/environments/DEV.json
```

It does **not** create/use a Fabric Environment item.

The environment document contains only non-secret physical identity and policy:

```text
workspace UUID
exact display names + create_if_missing for Lakehouse / SQL Database / Warehouse
exact display names + create_if_missing for repository-owned Copy/Spark/seed jobs
exact display names + create_if_missing for runner/worker/Pipeline
bounded bootstrap mutation policy
```

Only `.example.json` templates ship without a real workspace identity. Copy the matching example, replace the intentionally invalid all-zero workspace UUID, review, and commit the real `DEV.json`/`UAT.json` once.

Normal operators no longer repeat:

```text
--control-plane-server
--control-plane-database
--warehouse-server
--warehouse-database
```

Those SQL targets are discovered from Fabric REST using the actual resolved items.

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

Bootstrap never enables live certification authorization flags and never writes PASS/release-ready state. A successful preparation deliberately remains `certification_result = NOT_RUN`.

## Repository-owned Copy/Spark provider items

The one-click path now creates/updates real provider definitions instead of asking an operator to paste pre-existing IDs:

```text
Copy Job:
  dbo.cert_copy_source -> dbo.cert_copy_landing in certification Lakehouse

Spark Job Definition:
  reads dbo.cert_spark_source with Framework-supplied bounds
  -> writes dbo.cert_spark_landing in certification Lakehouse
```

The seed Spark job only prepares the source Delta tables. Real Copy/Spark certification remains a later explicitly authorized Framework evidence stage. Provider `Completed` alone is not PASS.

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
release_authorized = false
```

A bootstrap `READY` or bounded certification PASS does not freeze/authorize a release.

## Production boundary

Production remains:

```text
fabric-data-framework==0.3.0
```

Do not change it until immutable Framework `v0.4.0` exists and strict release governance explicitly authorizes migration.

## Normal customer-project baseline

The static framework-next project-contract compatibility pin remains `148e02e3fff7861f238296e7554815a6fd49dd0a`; it is separate from the certification executable identity.

The normal project workflow remains:

```text
fabric-framework project-init <repo> --domain <domain>
-> DatasetConfig / semantic selections / domain rules
-> orchestration.execution_group
-> fabric-framework project-validate <repo>
-> GitHub CI
-> DEV -> UAT -> PROD using the same logical topology
```

The enterprise reference remains 100 tables: 50 FULL/REPLACE, 20 WATERMARK/SCD2, 20 WATERMARK/SCD1, 10 CDC/UPSERT using Debezium / external CDC. That fixture proves onboarding/config scale, not live Fabric performance.

## Exact next real boundary

After this source is on Customer `main` and CI is green:

```text
create/commit certification/environments/DEV.json with the real isolated DEV workspace UUID
-> az login + gh auth
-> python certification/bootstrap.py --apply --environment DEV
-> retain genuine bootstrap-result.json
-> run framework-certification-runner bounded/read-safe first
-> STOP on real FAIL
-> explicitly authorize live stages only when prerequisites are ready
```

No current-source live bootstrap/certification evidence exists yet.

## Canonical operator docs

```text
docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md
docs/runbooks/ENTERPRISE_ENVIRONMENT_TOPOLOGY.md
```
