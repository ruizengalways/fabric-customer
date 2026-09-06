# Runbooks

Use these documents for current operations. Historical PR/checkpoint narratives are intentionally not kept here; Git history already preserves them.

## New conversation recovery

Read only:

```text
1. docs/CURRENT_STATUS.md
2. docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
3. fabric-data-framework/docs/machine/STATE.md
```

Then open a task-specific runbook below.

## Build a domain

`BUILD_NEW_DOMAIN_PROJECT.md`

End-to-end domain bootstrap and onboarding: `project-init`, source inventory, DatasetConfig, semantic selections, the 100-table Health reference, Debezium/external CDC, `project-validate`, PR/CI and DEV -> UAT -> PROD promotion.

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

Execution groups, fail-at-end behavior, dataset failure isolation, blocked dependencies, DQ/quarantine handling and conservative retry/replay/backfill/rebuild decisions.

## Deploy certification Fabric items

`DEPLOY_CERTIFICATION_FABRIC_ITEMS.md`

Creates/updates the repository-owned certification Notebook and Data Pipeline in an isolated DEV/UAT workspace. Default path uses Azure CLI user authentication for Fabric REST and signed-in Fabric user Entra authentication for SQL. Key Vault remains optional.

## Test the current Framework in company Fabric

`TEST_FRAMEWORK_IN_COMPANY_FABRIC.md`

Current exact-artifact real-Fabric path. Run bounded certification first, stop on a real FAIL, and only then continue approved live Control Plane/Pipeline/Copy/Spark/Warehouse stages.

## Review Control Plane evidence

`CONTROL_PLANE_EXTERNAL_EVIDENCE_REVIEW.md`

Use only when binding genuine external Control Plane evidence into the strict release-evidence chain.

## Rule

Do not add PR-number checkpoint runbooks or duplicate current-state history. Update `docs/CURRENT_STATUS.md` with current facts and rely on Git history for old implementation details.
