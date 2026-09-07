# fabric-customer

Reference customer/domain repository for the Enterprise Microsoft Fabric data-engineering platform.

Customer owns **WHAT**: DatasetConfig, source/capture semantics, domain mappings, DQ/reconciliation rules, execution-group policy, non-secret environment bindings and domain Fabric items. `fabric-data-framework` owns reusable execution **HOW**.

## Start here

For a new conversation or engineer, read only:

1. `docs/CURRENT_STATUS.md` — current truth and next boundary.
2. `docs/ARCHITECTURE.md` — stable ownership/topology/layout.
3. The task-specific runbook under `docs/runbooks/`.

Git history owns old implementations and migration history. Current directories describe only the current world.

## Repository map

```text
config/          current domain runtime configuration
src/             customer-specific Python code
fabric/          normal domain Fabric item definitions
certification/   isolated Framework certification tooling and fixtures
examples/        teaching/intake examples only
tests/           automated contracts
scripts/         developer/CI utilities
docs/            current architecture and operator runbooks
.github/         CI/CD
```

Rules:

- do not create `framework_0_4`, `framework_0_5`, `latest` or `legacy` runtime trees;
- upgrade current contracts in place through reviewed PRs; Git preserves history;
- `examples/` must never become a hidden production runtime source;
- certification-only resources stay under `certification/`.

## Enterprise topology

DEV, UAT and PROD use the same logical component roles:

```text
Fabric SQL Database = Framework operational Control Plane
Lakehouse / OneLake = Bronze / Silver / Gold business data + quarantine detail
Fabric Warehouse    = optional SQL-first Gold / dimensional serving
```

Canonical profile: `fabric_sql_database_v1`.

## Version boundary

Production remains pinned to:

```text
fabric-data-framework==0.3.0
```

The project-contract compatibility lane remains pinned to Framework SHA `148e02e3fff7861f238296e7554815a6fd49dd0a` for `project-init` / `project-validate` transition validation only. Current 0.4 certification bytes are independently selected by `certification/framework-executable.json`.

## Normal domain workflow

```text
fabric-framework project-init <repo> --domain <domain>
-> source inventory
-> config/datasets + config/capture
-> config/orchestration/execution-groups
-> fabric-framework project-validate <repo>
-> domain tests + CI
-> same release identity DEV -> UAT -> PROD
```

Environment-local non-secret bindings live in `config/environments/`. Normal domain Fabric definitions belong in `fabric/`.

The enterprise intake reference models 100 datasets: 50 FULL/REPLACE, 20 WATERMARK/SCD2, 20 WATERMARK/SCD1 and 10 CDC/UPSERT using Debezium / external CDC. It proves onboarding/configuration scale, not runtime performance.

## Certification

Certification is isolated from normal domain runtime:

```text
certification/bootstrap.py
certification/framework-executable.json
certification/config/environments/
certification/fabric/
certification/project/
certification/extensions/
certification/support/
```

Preferred DEV preparation:

```powershell
python certification/bootstrap.py --apply --environment DEV
```

`DEV` selects `certification/config/environments/DEV.json`; it is not a Microsoft Fabric Environment item. Bootstrap deliberately stops at:

```text
bootstrap_status = READY
certification_result = NOT_RUN
release_authorized = false
```

Real certification execution, candidate freeze and release authorization remain separate fail-closed gates.

## Pipeline operating model

Execution-group policy is source-controlled under `config/orchestration/execution-groups/`. The default product behavior is fail-at-end:

```text
one dataset FAIL
-> independent siblings continue
-> dependents become BLOCKED
-> all runnable work reaches terminal state
-> parent Pipeline ends FAILED
```

See `docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md`.
