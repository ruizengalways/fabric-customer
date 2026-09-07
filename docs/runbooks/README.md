# Runbooks

Use these documents for current operations. Historical PR/checkpoint narratives are intentionally not kept here; Git history preserves them.

## New conversation recovery

Read:

```text
1. docs/CURRENT_STATUS.md
2. docs/ARCHITECTURE.md
3. the task-specific runbook below
4. fabric-data-framework/docs/machine/STATE.md only when Framework release/certification identity matters
```

## Build a domain

`BUILD_NEW_DOMAIN_PROJECT.md`

Current end-to-end onboarding: `project-init`, source inventory, DatasetConfig/semantic selections, execution groups under `config/orchestration/`, the 100-table Health reference, Debezium/external CDC, `project-validate`, PR/CI and DEV -> UAT -> PROD promotion.

## Enterprise topology

`ENTERPRISE_ENVIRONMENT_TOPOLOGY.md`

Canonical environment contract:

```text
DEV / UAT / PROD Control Plane = Fabric SQL Database
profile                          = fabric_sql_database_v1
business data                    = Lakehouse / OneLake
Warehouse                        = optional SQL-first Gold serving
```

## Operate pipelines

`OPERATE_MULTI_TABLE_PIPELINES.md`

Execution groups, `FAIL_AT_END`, dataset failure isolation, dependency blocking, DQ/quarantine and conservative `RETRY` / `REPLAY` / `BACKFILL` / `FULL_REBUILD` decisions.

## One-click certification preparation

`DEPLOY_CERTIFICATION_FABRIC_ITEMS.md`

Preferred command:

```powershell
python certification/bootstrap.py --apply --environment DEV
```

Certification config lives under `certification/config/`; certification-only Fabric definitions live under `certification/fabric/`. Bootstrap stops at `READY / NOT_RUN`.

## Test current Framework in company Fabric

`TEST_FRAMEWORK_IN_COMPANY_FABRIC.md`

Run bounded/read-safe certification first, stop on a real FAIL, and only then enable approved live Control Plane/Pipeline/Copy/Spark/Warehouse stages.

## Review Control Plane evidence

`CONTROL_PLANE_EXTERNAL_EVIDENCE_REVIEW.md`

Use only when binding genuine external Control Plane evidence into the strict release-evidence chain.

## Rule

Do not add PR-number checkpoint runbooks, version-named current directories or duplicate current-state history. Update `docs/CURRENT_STATUS.md` with current facts and rely on Git history for old implementation details.
