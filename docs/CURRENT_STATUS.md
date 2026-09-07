# Current Status — fabric-customer

Last updated: 2026-09-07

## Recovery rule

**GitHub `main` is truth.** For a new conversation, read only:

```text
1. fabric-customer/docs/CURRENT_STATUS.md
2. fabric-customer/docs/ARCHITECTURE.md
3. the task-specific runbook under fabric-customer/docs/runbooks/
4. fabric-data-framework/docs/machine/STATE.md when Framework release/certification identity matters
```

Do not reconstruct current state from old PRs, old chat state or old certification artifacts. Git history is the historical record.

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

repository_layout:
  runtime_config: config/
  environment_bindings: config/environments/
  orchestration_policy: config/orchestration/execution-groups/
  normal_fabric_items: fabric/
  certification_root: certification/
  examples_are_runtime_truth: false
  version_named_runtime_directories_allowed: false

certification_bootstrap:
  source_on_main: true
  preferred_command: python certification/bootstrap.py --apply --environment DEV
  environment_is_fabric_environment_item: false
  environment_config: certification/config/environments/DEV.json
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

The source capability above does **not** claim that a company Fabric workspace has already been mutated. Real deployment/execution state must come from genuine retained bootstrap and Framework evidence.

## Canonical repository structure

```text
config/
  datasets/
  capture/
  orchestration/execution-groups/
  environments/

src/
fabric/

certification/
  bootstrap.py
  framework-executable.json
  config/environments/
  fabric/
  project/
  extensions/
  support/

examples/
tests/
scripts/
docs/
.github/
```

Directory names describe role, not Framework version. Current contracts are upgraded in place through reviewed PRs; Git preserves old bytes. `examples/` is teaching/intake material only and must not become a second runtime configuration source.

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

Later Framework docs/test-only commits do not replace these executable bytes.

## Environment is the operator key

`--environment DEV` selects:

```text
certification/config/environments/DEV.json
```

It does **not** create or select a Microsoft Fabric Environment item.

The certification environment document contains only non-secret physical identity/policy: workspace UUID, repository-owned item display names, `create_if_missing` policy and bounded preparation mutations. SQL server/database values are discovered from the actual resolved Fabric SQL Database and Warehouse items.

Normal domain DEV/UAT/PROD bindings are separate and live under:

```text
config/environments/
```

## One-click certification preparation

Normal command:

```powershell
python certification/bootstrap.py --apply --environment DEV
```

Fail-closed sequence:

```text
clean exact Customer main source
+ exact Framework successful-main artifact verification
-> resolve/create schema-enabled certification Lakehouse
-> resolve/create Fabric SQL Database Control Plane
-> resolve/create dedicated Warehouse
-> resolve/create seed Spark / Copy Job / capture Spark Job
-> resolve/create worker Notebook + child Pipeline + runner Notebook
-> execute setup-only seed Spark job
-> build exact Customer extension/input bundle with real Fabric item UUIDs
-> stage exact Framework + Customer bytes to OneLake
-> apply Warehouse fixtures
-> apply Control Plane schema + exact DatasetConfig metadata
-> write bootstrap-result.json
-> STOP at READY / NOT_RUN
```

Canonical retained state remains:

```text
certification_result = NOT_RUN
release_authorized = false
```

Bootstrap never manufactures certification PASS, candidate freeze, strict release readiness or release authorization.

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

## Production and project-contract boundary

Production remains pinned to `fabric-data-framework==0.3.0` until immutable Framework `v0.4.0` exists and strict release governance explicitly authorizes migration.

The established project-contract compatibility pin remains:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

It is only for `project-init` / `project-validate` transition compatibility and is separate from the current certification executable identity.

The enterprise reference remains 100 datasets: 50 FULL/REPLACE, 20 WATERMARK/SCD2, 20 WATERMARK/SCD1 and 10 CDC/UPSERT using Debezium / external CDC. That fixture proves onboarding/configuration scale, not live Fabric performance.

## Exact next real boundary

The next boundary is an isolated real DEV Fabric workspace:

```text
create/commit certification/config/environments/DEV.json with the real DEV workspace UUID
-> az login + gh auth
-> python certification/bootstrap.py --apply --environment DEV
-> retain genuine bootstrap-result.json
-> open/run framework-certification-runner bounded/read-safe first
-> STOP on any real FAIL
-> explicitly authorize later live stages only when prerequisites are ready
-> retain genuine Framework evidence
```

No current-source live bootstrap/certification evidence exists yet.

## Canonical runbooks

```text
docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md
docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md
docs/runbooks/ENTERPRISE_ENVIRONMENT_TOPOLOGY.md
docs/runbooks/CONTROL_PLANE_EXTERNAL_EVIDENCE_REVIEW.md
```
