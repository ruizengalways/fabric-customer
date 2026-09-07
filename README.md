# fabric-customer

Reference domain repository for the Enterprise Microsoft Fabric Data Engineering Platform.

This repo owns customer/domain **WHAT**: DatasetConfig, semantic capture selections, mappings, DQ/reconciliation rules, execution-group policy, non-secret environment bindings, certification inputs and domain tests. Generic execution **HOW** belongs in `fabric-data-framework`.

## Start here

For a new conversation or engineer, read:

1. `docs/CURRENT_STATUS.md` — current truth and next boundary.
2. `docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md` — onboard a domain.
3. `docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md` — operate/recover pipelines.
4. `docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md` — one-click certification preparation.
5. `docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md` — real-Fabric execution.

Git history is history; do not use old PR timelines to reconstruct current state.

## Enterprise topology

DEV/UAT/PROD use the same logical architecture:

```text
Fabric SQL Database = Framework operational Control Plane
Lakehouse / OneLake = Bronze / Silver / Gold business data + quarantine detail
Fabric Warehouse    = optional SQL-first Gold / dimensional serving
```

Canonical Control Plane profile: `fabric_sql_database_v1`.

## Version boundary

Production stays pinned to:

```text
fabric-data-framework==0.3.0
```

The static framework-next project-contract lane remains pinned to `148e02e3fff7861f238296e7554815a6fd49dd0a` for `project-init` / `project-validate` compatibility only.

Framework 0.4 certification uses the exact executable recorded in `certification/framework-executable.json` and `docs/CURRENT_STATUS.md`. Certification source/CI does not authorize a production dependency change.

## Normal domain workflow

```text
fabric-framework project-init <repo> --domain <domain>
-> DatasetConfig / source semantics / domain rules
-> orchestration.execution_group
-> fabric-framework project-validate <repo>
-> GitHub CI
-> DEV -> UAT -> PROD with environment-local bindings
```

The enterprise reference models 100 tables: 50 FULL/REPLACE, 20 WATERMARK/SCD2, 20 WATERMARK/SCD1 and 10 CDC/UPSERT using Debezium / external CDC. It proves onboarding/configuration scale, not performance.

## Certification — preferred path

The normal preparation command is:

```powershell
python certification/bootstrap.py --apply --environment DEV
```

`DEV` selects `certification/environments/DEV.json`; it is not a Fabric Environment item. After the one-time non-secret workspace binding is committed, bootstrap resolves/creates the dedicated Lakehouse, Fabric SQL Database, Warehouse, real Copy/Spark provider items, runner/worker/Pipeline, stages exact Framework + Customer bytes to OneLake, seeds real provider source Delta tables, and initializes dedicated SQL fixtures/schema/metadata.

The operator does not repeatedly pass SQL server/database values; bootstrap discovers them from the actual Fabric items.

Bootstrap deliberately stops at:

```text
bootstrap_status = READY
certification_result = NOT_RUN
release_authorized = false
```

Live certification remains explicit and fail-closed. Key Vault is optional. Real deployment, real execution, candidate freeze and release authorization are separate gates.

## Pipeline operating model

The reference product behavior remains fail-at-end:

```text
one dataset FAIL
-> independent siblings continue
-> dependents BLOCKED
-> runnable work reaches terminal state
-> parent Pipeline fails at the end
```

See `docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md`.
