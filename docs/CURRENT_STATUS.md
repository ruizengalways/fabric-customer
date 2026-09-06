# Current Status — fabric-customer

Last updated: 2026-09-06

## Recovery rule

**GitHub `main` is truth.** For a new conversation, do not rebuild current state from old PRs, old certification artifacts or chat memory.

Read in this order:

```text
1. fabric-customer/docs/CURRENT_STATUS.md
2. fabric-customer/docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
3. fabric-data-framework/docs/machine/STATE.md
```

Only open deeper architecture/operations docs when the task needs them.

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
  runtime_state_promoted_between_environments: false

default_auth:
  fabric_rest: azure-cli
  sql_runtime: fabric-user
  key_vault_required: false
  key_vault_optional: true
  env_token_optional_for_automation: true

real_fabric_state:
  certification_notebook_source_merged: true
  certification_pipeline_source_merged: true
  repository_owned_certification_notebook_deployed: false
  repository_owned_certification_pipeline_deployed: false
  current_framework_real_fabric_certification_executed: false
```

Do not change the production dependency until immutable Framework `v0.4.0` exists and release governance explicitly authorizes migration.

## Exact Framework executable for the next DEV run

Documentation-only commits after the executable baseline do not create a new candidate. The exact Framework bytes for the next real-Fabric execution remain:

```text
Framework executable SHA   17fbbd8ed2afb14771748a25d3e12d9bf63fe986
Framework main CI run      34010629765
artifact ID                9982333832
artifact name              framework-wheel-17fbbd8ed2afb14771748a25d3e12d9bf63fe986
wheel                      fabric_data_framework-0.4.0-py3-none-any.whl
wheel SHA256               0d7d351548712db3293b00a3b8eb968387f573b542d8fe506c9436a1b9b0a834
artifact ZIP digest        sha256:07e6f54e9fa4a9b93f4536afd2d0f59754cde4fd33bd26dd3a15ae4b8c2b9791
selected/frozen            false
real-Fabric result         NOT YET
```

If executable Framework source changes, stop and resolve a new exact artifact identity before testing.

## What is already complete

Source/CI work is complete for the current boundary:

- enterprise DEV/UAT/PROD topology is aligned;
- `fabric_sql_database_v1` is the only canonical Customer Control Plane profile;
- Fabric-native Entra SQL runtime exists in the current Framework executable;
- Customer certification Notebook/Pipeline definitions are source-controlled;
- common deployment defaults to Azure CLI user auth for Fabric REST and signed-in Fabric user auth for SQL;
- Key Vault is optional rather than a prerequisite;
- normal multi-table execution-group/recovery examples are present;
- Customer production remains safely pinned to Framework `0.3.0`.

More source-only recovery/checkpoint work is not the next priority.

## Next boundary — isolated DEV Fabric

The next action is a real isolated DEV execution:

```text
current fabric-customer main
+ exact Framework wheel above
-> deploy repository-owned certification Notebook + Pipeline
-> retain deployment-result.json with real Fabric item UUIDs
-> run bounded certification
-> STOP on any real FAIL
-> only then continue approved live Control Plane / Pipeline / Copy / Spark / Warehouse stages
-> retain real evidence
```

Canonical operator docs:

```text
docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md
docs/runbooks/ENTERPRISE_ENVIRONMENT_TOPOLOGY.md
```

Default lane requires Fabric permissions, not Azure Key Vault administration:

```text
az login / az login --allow-no-subscriptions
Fabric REST auth = azure-cli
SQL runtime auth = fabric-user
```

Warehouse administrator/session-control authority is separate and must never be inferred from ordinary Fabric user access.

Successful Fabric-item deployment writes `deployment-result.json` with `certification_result = NOT_RUN`; deployment is not certification.

## Current strict blockers

The current fail-closed blockers include:

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

A bounded certification PASS is not a candidate freeze. A manual/admin record is not a substitute for strict evidence-based release readiness.

## Normal customer-project baseline

The normal project workflow remains:

```text
fabric-framework project-init <repo> --domain <domain>
-> DatasetConfig / semantic selections / domain rules
-> orchestration.execution_group
-> fabric-framework project-validate <repo>
-> GitHub CI
-> DEV -> UAT -> PROD using the same logical topology
```

The static framework-next compatibility lane remains pinned to:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

The enterprise reference contains **100** tables:

```text
50 FULL -> REPLACE
20 WATERMARK -> SCD2
20 WATERMARK -> SCD1
10 CDC -> UPSERT using Debezium / external CDC
```

That fixture proves onboarding/config scale, not live Fabric performance.

## Do not do these next

Do not:

- create more PR-number recovery checkpoints;
- resurrect old Framework wheel identities from historical docs;
- make Key Vault mandatory for the ordinary Fabric-only data-engineer lane;
- edit retained evidence by hand to invent item UUIDs or PASS state;
- freeze or release Framework 0.4 before current-byte real-Fabric evidence exists;
- change Customer production from `fabric-data-framework==0.3.0` because source CI is green.

Git history contains historical implementation detail when it is genuinely needed. Current docs intentionally contain current truth only.
