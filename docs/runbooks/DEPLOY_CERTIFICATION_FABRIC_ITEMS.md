# Runbook — One-click certification bootstrap

Audience: data engineers preparing an isolated Fabric DEV/UAT workspace for the current Framework certification slice.

## Default command

After the environment config is committed, normal preparation is one command:

```powershell
python certification/bootstrap.py --apply --environment DEV
```

`DEV` is a Customer/Framework **logical environment key**. It is not a Microsoft Fabric Environment item.

## 1. One-time environment config

Copy the template:

```powershell
Copy-Item certification/environments/DEV.example.json certification/environments/DEV.json
```

Set the real non-secret workspace UUID. Keep or rename the repository-owned item display names as needed:

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

The all-zero UUID in the `.example.json` file is intentionally rejected. Replace it with the real workspace UUID, review the file, and commit `DEV.json` before running bootstrap. The bootstrap requires a clean Customer checkout because the exact Customer git SHA becomes part of the retained input identity.

Do **not** put tokens, passwords, client secrets, signed URLs or Key Vault secret values in the environment file.

## 2. Local prerequisites

From the exact committed Customer checkout:

```powershell
az login
gh auth status
```

If the corporate identity has Fabric access but no Azure subscription:

```powershell
az login --allow-no-subscriptions
```

Required local capabilities:

```text
Python 3.11+
Git CLI
GitHub CLI authenticated to download the exact Framework Actions artifact
Azure CLI authenticated as the data engineer
Python `pyodbc` package is installed into the isolated bootstrap venv
Microsoft ODBC Driver 18+ for SQL Server must exist on the host
Fabric workspace rights to create/update the dedicated certification items
Entra SQL rights on the dedicated certification SQL Database and Warehouse
```

Tokens are acquired process-locally for these audiences and are never written to retained JSON:

```text
Fabric REST  https://api.fabric.microsoft.com
OneLake      https://storage.azure.com/
Fabric SQL   https://database.windows.net/
```

## 3. What one command prepares

The bootstrap first verifies the exact source/artifact boundary and then prepares Fabric:

```text
explicit --apply authorization
-> load certification/environments/DEV.json
-> require clean exact Customer git source
-> verify current Framework main CI + required jobs
-> download exact Framework Actions artifact
-> verify CANDIDATE.json + SHA256SUMS + wheel SHA256
-> create isolated certification venv and install exact Framework wheel
-> resolve/create schema-enabled certification Lakehouse
-> resolve/create Fabric SQL Database Control Plane
-> resolve/create dedicated Warehouse
-> resolve/create repository-owned seed Spark Job Definition
-> resolve/create repository-owned Copy Job
-> resolve/create repository-owned capture Spark Job Definition
-> resolve/create Lakehouse-bound worker Notebook
-> resolve/create child Data Pipeline bound to the real worker UUID
-> resolve/create Lakehouse-bound runner Notebook
-> execute only the seed Spark job to create real provider source Delta tables
-> build exact Customer extension wheel + Customer input bundle using the real item UUIDs
-> replace/stage exact customer-inputs and exact Framework files in OneLake
-> apply dedicated Warehouse fixture DDL
-> apply Control Plane schema + exact certification DatasetConfig metadata
-> write non-secret bootstrap result
-> STOP at READY / NOT_RUN
```

The seed Spark job creates only setup source tables such as `dbo.cert_copy_source` and `dbo.cert_spark_source`. Its successful execution is tagged as **SETUP ONLY**, never as certification evidence.

### Repository-owned provider items

The bootstrap no longer asks the operator to pre-create or paste Copy/Spark UUIDs.

`framework-certification-copy` is rendered as a real Fabric Copy Job that copies the seeded Lakehouse table:

```text
dbo.cert_copy_source -> dbo.cert_copy_landing
```

`framework-certification-spark` is a real Spark Job Definition whose source is:

```text
dbo.cert_spark_source
```

and whose landing is:

```text
dbo.cert_spark_landing
```

The exact real UUIDs returned by Fabric are written into the Customer `runner-config.json`. Provider completion is still not automatically treated as Framework PASS; the existing Framework capture/evidence gates remain authoritative.

### Existing resource behavior

Exact display-name duplicates fail closed. If an item exists, its definition is updated where the item type supports definitions. If `create_if_missing=false` and the item is absent, bootstrap stops.

A pre-existing certification Lakehouse must already be **schema-enabled** with default schema `dbo`. Bootstrap will not silently change an existing Lakehouse's schema semantics.

## 4. SQL server/database values are discovered

The normal operator does **not** pass:

```text
--control-plane-server
--control-plane-database
--warehouse-server
--warehouse-database
```

Bootstrap gets them from the actual Fabric items:

```text
Fabric SQL Database -> properties.serverFqdn + properties.databaseName
Warehouse           -> Warehouse connectionString endpoint + Warehouse item name
Lakehouse capture   -> exact Lakehouse UUID + schema-enabled `dbo` tables
```

The low-level deployer still accepts explicit SQL bindings for troubleshooting/automation integration, but it is no longer the preferred human path.

## 5. Exact bytes staged to OneLake

The certification Lakehouse receives:

```text
Files/framework_cert/
  CANDIDATE.json
  SHA256SUMS
  fabric_data_framework-0.4.0-py3-none-any.whl
  customer-inputs/
    INPUTS.json
    runner-config.json
    release-manifest.json
    project/
    dist/
```

Before replacing `customer-inputs/`, bootstrap recursively removes the old dedicated bundle so stale project/dist files cannot survive into the new exact input identity.

## 6. Result

Expected local result:

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

It also records the real non-secret workspace/resource/item UUIDs, definition hashes, exact Framework source/run/artifact/wheel identity, exact Customer SHA/input identity, OneLake staging hashes/sizes, seed setup job identity, and SQL bootstrap status.

`READY` means **the environment is prepared**. It does not mean certification PASS, candidate freeze, strict release readiness, or release authorization.

## 7. Stop conditions

Bootstrap is restricted to DEV/UAT and stops on any of these boundaries:

```text
missing --apply
missing/invalid/placeholder environment config
all-zero workspace UUID
uncommitted Customer source
Framework main CI/artifact identity mismatch
required Framework CI job not successful
Fabric exact-name duplicate
Fabric create/update/LRO failure
existing Lakehouse not schema-enabled
OneLake staging failure
seed provider job failure
Customer exact input build mismatch
missing pyodbc / ODBC Driver 18+
Warehouse fixture failure
Control Plane schema/metadata failure
```

Never hand-edit `bootstrap-result.json`, `INPUTS.json`, `runner-config.json`, or `CANDIDATE.json` to manufacture READY/PASS state.

## 8. Run certification after READY

Open and run:

```text
framework-certification-runner
```

The runner verifies/installs the exact staged Framework wheel and uses the exact staged Customer bundle. Its live authorization switches default to `False`, including Control Plane writes, Pipeline, Copy, Spark, Warehouse, fault injection/session termination, and business-path mutation.

Follow `TEST_FRAMEWORK_IN_COMPANY_FABRIC.md` for bounded-first execution and explicit live-stage authorization.

## 9. Low-level contract and troubleshooting reference

The one-click command is the preferred operator path, but recovery must still expose the exact lower-level contract so an engineer can diagnose a rendered Notebook/Pipeline without inventing semantics.

The child Pipeline forwards exactly these Framework-owned dynamic values to the worker Notebook:

```text
framework_pipeline_run_id
framework_dataset_run_id
dataset_id
run_mode
attempt
effective_config_hash
execution_plan_hash
```

These values are runtime correlation/plan inputs. They are **not** additional environment configuration fields.

The low-level deployment entry point remains:

```text
certification/fabric_items/deploy_fabric_items.py
```

and still requires explicit `--apply`. Its safe troubleshooting outputs include:

```text
build/fabric-items/deployment-result.json
certification_result = NOT_RUN
```

The optional automation auth lane can read `FABRIC_ACCESS_TOKEN`; the default human path remains Azure CLI and does not require printing/copying that token.

To inspect definitions without deployment, the underlying renderer remains available:

```powershell
python certification/fabric_items/render_fabric_items.py notebook --output build/worker-notebook.json
python certification/fabric_items/render_fabric_items.py pipeline --workspace-id <WORKSPACE_UUID> --notebook-id <NOTEBOOK_UUID> --control-plane-server <SERVER> --control-plane-database <DATABASE> --warehouse-server <SERVER> --warehouse-database <DATABASE> --output build/child-pipeline.json
```

The dedicated Warehouse DDL remains:

```text
certification/fabric_items/sql/warehouse-certification-fixtures.sql
```

First-time Control Plane migration remains an explicit certification authorization boundary represented by `allow_control_plane_migration=True` only when that later live stage is deliberately approved. Bootstrap schema preparation does not convert later conformance execution into automatic authorization.

The exact runner continues to use `WAREHOUSE_DATABASE_URL` internally for Framework/Customer SQL-based business-path components. `BUSINESS_PATH_DRIVER_RUNTIME_JSON` is a removed/legacy runtime variable and is **not required** by the current business-path driver.

A Fabric provider state of `Completed` is only provider execution state. It is not enough to create a Framework PASS: the Framework must still validate the returned evidence and persist the corresponding `DatasetDispatchOutcome`/capture result under the exact release identity.

## 10. Manual fallback boundary

`deploy_fabric_items.py` and the renderer above are troubleshooting/external-system interfaces, not the normal one-click human workflow. They must not be used to bypass environment config, exact artifact identity, OneLake staging, SQL bootstrap, or the READY/NOT_RUN boundary.

Key Vault remains an optional enterprise integration. The default path is current `az login` for Fabric REST/local SQL bootstrap and the signed-in Fabric Notebook Entra identity for Notebook SQL runtime.
