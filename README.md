# fabric-customer

Reference domain repository for the Enterprise Microsoft Fabric Data Engineering Platform.

This repo owns customer/domain **WHAT**: DatasetConfig, semantic capture selections, mappings, business DQ rules, execution-group policy, non-secret environment bindings, tests and certification inputs. Generic execution **HOW** belongs in `fabric-data-framework`.

## Start here

For a new conversation or a new engineer, read only these first:

1. `docs/CURRENT_STATUS.md` — current truth and exact next action.
2. `docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md` — create/onboard a domain.
3. `docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md` — operate and recover pipelines.
4. `docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md` — current real-Fabric certification path.

Do not reconstruct current state from old PR numbers or Git history. Git history is history; `docs/CURRENT_STATUS.md` is the human recovery checkpoint.

## Enterprise topology

DEV, UAT and PROD use the same logical architecture:

```text
Fabric SQL Database = Framework operational Control Plane
Lakehouse / OneLake = Bronze / Silver / Gold business data + quarantine detail
Fabric Warehouse    = optional SQL-first Gold / dimensional serving
```

Canonical control-plane profile:

```text
fabric_sql_database_v1
```

Do not use Lakehouse control tables in DEV and switch to SQL Database later. CI/CD promotes code, DatasetConfig, execution-group policy, DQ/reconciliation rules, Fabric item definitions and control-plane schema/migrations. Runtime rows, watermarks, credentials, business data and physical item UUIDs remain environment-local.

See `docs/runbooks/ENTERPRISE_ENVIRONMENT_TOPOLOGY.md`.

## Framework version lanes

Production stays pinned to the released dependency:

```text
fabric-data-framework==0.3.0
```

Do not change that pin until immutable Framework `v0.4.0` exists and release governance authorizes migration.

The static framework-next project-contract lane remains pinned to:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

It proves `project-init` / `project-validate` compatibility only. The current Framework 0.4 executable used for certification is recorded separately in `docs/CURRENT_STATUS.md`.

## Normal domain workflow

```text
fabric-framework project-init <repo> --domain <domain>
-> inventory sources
-> author DatasetConfig / semantic selections / domain rules
-> assign orchestration.execution_group
-> fabric-framework project-validate <repo>
-> GitHub PR + CI
-> deploy to DEV
-> validate and operate
-> promote the same logical definitions to UAT and PROD with environment-local bindings
```

A `project-validate` PASS is static consistency, not real-Fabric certification.

## 100-table enterprise reference

One Health-style domain repo intentionally models mixed ingestion/change patterns:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT using Debezium / external CDC
```

Repo boundaries follow business ownership, security/compliance and release lifecycle—not ingestion mechanism. Operational grouping belongs in `orchestration.execution_group`.

Reference files:

```text
examples/enterprise_100_table/
examples/pipeline_development/
```

The 100-table fixture proves onboarding/configuration scale; it is not a performance benchmark.

## Pipeline operating model

Framework 0.4 examples model product behavior where one failed dataset does not blindly abort independent work:

```text
one dataset FAIL
-> durable dataset error
-> independent siblings continue
-> failed dependents become BLOCKED
-> runnable work reaches terminal state
-> parent Pipeline fails at end
```

Recovery is conservative: retry only explicit retryable failures, replay after DQ fixes, investigate reconciliation/unknown-commit cases before reprocessing, recover dependencies first, use bounded backfill for source gaps, and reserve full rebuild for authoritative reset cases.

See `docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md`.

## Framework 0.4 certification

Customer-owned certification definitions live under:

```text
certification/project/
certification/extensions/
certification/fabric_items/
```

Default operator path is Fabric-native:

```text
Fabric REST auth = Azure CLI signed-in user
SQL runtime auth = signed-in Fabric Notebook user (Microsoft Entra)
Key Vault         = optional enterprise integration
```

Use:

```text
docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
```

Repository-owned Notebook/Pipeline source being merged is not proof that company Fabric was mutated. Deployment evidence, real execution evidence, candidate freeze and release authorization are separate gates.

## Release boundary

Framework 0.4 remains unreleased until strict evidence is complete. Do not manufacture PASS evidence, do not silently freeze a candidate, and do not replace the production `0.3.0` dependency from source/main.

Current executable identity, deployment status, blockers and the exact next step are intentionally kept in one place: `docs/CURRENT_STATUS.md`.
