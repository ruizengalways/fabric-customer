# Runbook — One-click certification bootstrap

Audience: data engineers preparing an isolated Fabric DEV/UAT workspace for the current Framework certification slice.

## 1. Preferred command

After the environment config is committed, normal preparation is one command:

```powershell
python certification/bootstrap.py --apply --environment DEV
```

`DEV` is a Customer/Framework logical environment key. It is not a Microsoft Fabric Environment item.

## 2. One-time environment config

Copy the template:

```powershell
Copy-Item certification/config/environments/DEV.example.json certification/config/environments/DEV.json
```

Set the real non-secret workspace UUID. Keep the repository-owned display names unless there is a reviewed reason to change them:

```json
{
  "schema_version": 1,
  "environment": "DEV",
  "workspace_id": "<REAL_WORKSPACE_UUID>",
  "lakehouse": {"display_name": "framework-certification-lakehouse", "create_if_missing": true},
  "control_plane": {"display_name": "framework-certification-control", "create_if_missing": true},
  "warehouse": {"display_name": "framework-certification-warehouse", "create_if_missing": true},
  "copy_job": {"display_name": "framework-certification-copy", "create_if_missing": true},
  "spark_job": {"display_name": "framework-certification-spark", "create_if_missing": true},
  "seed_spark_job": {"display_name": "framework-certification-seed", "create_if_missing": true},
  "runner_notebook": {"display_name": "framework-certification-runner", "create_if_missing": true},
  "worker_notebook": {"display_name": "framework-certification-worker", "create_if_missing": true},
  "child_pipeline": {"display_name": "framework-certification-child", "create_if_missing": true},
  "mutations": {
    "seed_provider_sources": true,
    "apply_warehouse_fixtures": true,
    "apply_control_plane_schema": true,
    "materialize_control_plane_metadata": true
  }
}
```

The all-zero UUID in the example is intentionally rejected. Do not put tokens, passwords, client secrets, signed URLs or Key Vault secret values in this file.

The bootstrap requires a clean Customer `main` checkout because the exact Customer Git SHA becomes part of retained input identity.

## 3. Local prerequisites

```text
Python 3.11+
Git CLI
GitHub CLI authenticated for exact Framework Actions artifact download
Azure CLI authenticated as the data engineer
Microsoft ODBC Driver 18+ for SQL Server
workspace rights to create/update dedicated certification items
Entra SQL rights on the certification SQL Database and Warehouse
```

Authenticate:

```powershell
az login
gh auth status
```

If the identity has Fabric rights but no Azure subscription:

```powershell
az login --allow-no-subscriptions
```

Default auth labels remain:

```text
fabric_rest = azure-cli
sql_runtime = fabric-user
```

Key Vault is optional enterprise integration. It is not required for the default user lane.

Process-local token audiences:

```text
Fabric REST  https://api.fabric.microsoft.com
OneLake      https://storage.azure.com/
Fabric SQL   https://database.windows.net/
```

Tokens are not written to retained JSON.

## 4. What the one command prepares

```text
explicit --apply authorization
-> load certification/config/environments/DEV.json
-> require clean exact Customer main source
-> verify pinned successful Framework main CI and required jobs
-> download exact Framework Actions artifact
-> verify CANDIDATE.json + SHA256SUMS + wheel SHA256
-> create isolated certification venv and install exact Framework wheel
-> resolve/create schema-enabled certification Lakehouse
-> resolve/create Fabric SQL Database Control Plane
-> resolve/create dedicated Warehouse
-> resolve/create seed Spark Job Definition
-> resolve/create real Copy Job
-> resolve/create capture Spark Job Definition
-> resolve/create Lakehouse-bound worker Notebook
-> resolve/create child Data Pipeline bound to the real worker UUID
-> resolve/create Lakehouse-bound runner Notebook
-> execute only the seed Spark job for provider source tables
-> build exact Customer extension wheel + input bundle with real item UUIDs
-> replace/stage exact Customer + Framework bytes in OneLake
-> apply Warehouse fixture DDL
-> apply Control Plane schema + exact certification DatasetConfig metadata
-> write non-secret bootstrap result
-> STOP at READY / NOT_RUN
```

The seed job creates setup source tables such as:

```text
dbo.cert_copy_source
dbo.cert_spark_source
```

It is **SETUP ONLY**, never certification evidence.

Repository-owned provider paths:

```text
Copy Job:
  dbo.cert_copy_source -> dbo.cert_copy_landing

Spark Job Definition:
  dbo.cert_spark_source + Framework-supplied bounds
  -> dbo.cert_spark_landing
```

Provider state `Completed` alone is not Framework PASS.

## 5. Existing resource behavior

Exact display-name duplicates fail closed. If an item exists, its definition is updated where supported. If `create_if_missing=false` and the item is absent, bootstrap stops.

A pre-existing certification Lakehouse must already be schema-enabled with default schema `dbo`; bootstrap does not silently alter its schema semantics.

## 6. SQL targets are discovered

The normal operator does not pass:

```text
--control-plane-server
--control-plane-database
--warehouse-server
--warehouse-database
```

Bootstrap resolves:

```text
Fabric SQL Database -> properties.serverFqdn + properties.databaseName
Warehouse           -> Warehouse SQL endpoint + Warehouse item name
Lakehouse capture   -> exact Lakehouse UUID + dbo tables
```

## 7. Exact bytes staged to OneLake

```text
Files/framework_cert/
  CANDIDATE.json
  SHA256SUMS
  framework-executable.json
  fabric_data_framework-0.4.0-py3-none-any.whl
  customer-inputs/
    INPUTS.json
    runner-config.json
    release-manifest.json
    project/
    dist/
```

The old dedicated `customer-inputs/` subtree is replaced first so stale files cannot survive into a new exact input identity.

## 8. Result

Expected local output:

```text
build/certification-bootstrap/DEV/bootstrap-result.json
```

Successful preparation must contain:

```text
bootstrap_status       READY
certification_result   NOT_RUN
release_authorized     false
contains_secret_values false
```

`READY` means the environment is prepared. It does not mean certification PASS, candidate freeze, strict release readiness or release authorization.

## 9. Stop conditions

Stop on any of these:

```text
missing --apply
missing/invalid/placeholder environment config
all-zero workspace UUID
uncommitted Customer source
local main != GitHub main
Framework CI/artifact identity mismatch
required Framework CI job not successful
Fabric exact-name duplicate
Fabric create/update/LRO failure
existing Lakehouse not schema-enabled
OneLake staging failure
seed provider job failure
Customer exact input mismatch
missing pyodbc / ODBC Driver 18+
Warehouse fixture failure
Control Plane schema/metadata failure
```

Never hand-edit `bootstrap-result.json`, `INPUTS.json`, `runner-config.json` or `CANDIDATE.json` to manufacture READY/PASS state.

## 10. After READY

Open/run:

```text
framework-certification-runner
```

Its live authorization switches default to `False`, including Control Plane writes/migration, Pipeline, Copy, Spark, Warehouse, fault injection/session termination and business-path mutation.

Follow `TEST_FRAMEWORK_IN_COMPANY_FABRIC.md` and stop on any real FAIL.

## 11. Low-level troubleshooting contract

The preferred human entrypoint remains `certification/bootstrap.py`. These lower-level files are for diagnosis/integration only:

```text
certification/fabric/deploy_fabric_items.py
certification/fabric/render_fabric_items.py
certification/fabric/sql/warehouse-certification-fixtures.sql
```

The child Pipeline forwards exactly these Framework-owned dynamic values:

```text
framework_pipeline_run_id
framework_dataset_run_id
dataset_id
run_mode
attempt
effective_config_hash
execution_plan_hash
```

They are runtime correlation/plan inputs, not environment config fields.

The low-level deployer still requires explicit `--apply` and writes a non-secret result such as:

```text
build/fabric-items/deployment-result.json
certification_result = NOT_RUN
```

Optional automation may read `FABRIC_ACCESS_TOKEN`; the default human path remains Azure CLI and must never print/copy the token.

Definition-only troubleshooting examples:

```powershell
python certification/fabric/render_fabric_items.py notebook --output build/worker-notebook.json
python certification/fabric/render_fabric_items.py pipeline --workspace-id <WORKSPACE_UUID> --notebook-id <NOTEBOOK_UUID> --control-plane-server <SERVER> --control-plane-database <DATABASE> --warehouse-server <SERVER> --warehouse-database <DATABASE> --output build/child-pipeline.json
```

The exact runner continues to use `WAREHOUSE_DATABASE_URL` internally for Framework/Customer SQL business-path components.

First-time later Control Plane migration and any Warehouse admin/session-control/fault action remain explicit certification authorization boundaries; bootstrap preparation does not grant those later permissions.
