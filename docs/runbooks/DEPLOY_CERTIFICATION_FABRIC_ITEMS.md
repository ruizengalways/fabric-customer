# Runbook — Deploy the reusable certification Fabric items

Audience: a data engineer preparing an isolated company Fabric DEV/UAT workspace for exact Framework certification.

This runbook is written for the common enterprise case where the data engineering team has Fabric workspace permissions but **does not** have Azure subscription/resource-group/Key Vault administration rights.

The default path is now:

```text
az login user identity
-> Fabric REST API
-> repository-owned certification Notebook + Data Pipeline
-> Fabric Notebook signed-in Entra identity
-> Fabric SQL Database / Warehouse
```

Azure Key Vault remains an optional enterprise integration lane; it is no longer a prerequisite for the normal Fabric-native certification path.

## 1. Safety boundary

Use only an isolated or explicitly approved certification workspace and dedicated certification Warehouse.

The repository deployer deliberately accepts only:

```text
DEV
UAT
```

It refuses `PROD`.

Never run the fixture DDL, business-path reset/mutation logic, Warehouse fault drill or session termination against a shared/production Warehouse.

Never commit, paste into Notebook source, include as a CLI argument, or retain in evidence:

```text
Fabric access-token values
SQL passwords
client secrets
Key Vault secret values
signed URLs
```

Fabric SQL server names, database names, workspace UUIDs and item UUIDs are non-secret deployment identity and may be retained.

Creating/updating Fabric items is **not** certification. A successful deployment deliberately records:

```text
certification_result = NOT_RUN
```

## 2. Repository-owned reference implementation

Canonical files:

```text
certification/fabric_items/
  deploy_fabric_items.py
  render_fabric_items.py
  notebook/certification-pipeline-worker.ipynb
  pipeline/pipeline-content.template.json
  sql/warehouse-certification-fixtures.sql

certification/project/config/certification/pipeline-worker.json
certification/extensions/src/fabric_customer_certification_extensions/pipeline_worker.py
```

The Pipeline is reusable across representative business paths. It is not one Pipeline per table.

The remote child contract still has exactly seven Framework-owned dynamic parameters:

```text
framework_pipeline_run_id
framework_dataset_run_id
dataset_id
run_mode
attempt
effective_config_hash
execution_plan_hash
```

Runtime authentication/binding parameters are deployment settings, not additional Framework correlation parameters.

## 3. First prove your Fabric REST API access

On the workstation/jumpbox where the Customer repo is cloned:

```powershell
az login
```

If the corporate account has Fabric access but no Azure subscription:

```powershell
az login --allow-no-subscriptions
```

Read-only smoke test:

```powershell
az rest --method get `
  --url "https://api.fabric.microsoft.com/v1/workspaces?roles=Admin" `
  --resource "https://api.fabric.microsoft.com"
```

Then list the target workspace items:

```powershell
$workspaceId = "<CERTIFICATION_WORKSPACE_UUID>"
az rest --method get `
  --url "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items" `
  --resource "https://api.fabric.microsoft.com"
```

A temporary write-permission smoke test may create an empty Notebook using an `@body.json` request and delete it afterwards. Do not use a real certification item name for the smoke test.

You do **not** need to print the token. The deployer default `--auth-mode azure-cli` calls `az account get-access-token` internally and captures the value only in process memory.

If an automated environment already supplies an approved short-lived token, the optional legacy API-auth lane remains:

```text
FABRIC_ACCESS_TOKEN
--auth-mode env-token
```

## 4. Fabric-native prerequisites — default lane

Have these non-secret values:

```text
certification environment: DEV or UAT
certification workspace UUID
Control Plane Fabric SQL server hostname
Control Plane database name
certification Warehouse SQL server hostname
certification Warehouse database name
```

Examples of acceptable server values are plain hostnames only:

```text
<id>.database.fabric.microsoft.com
<id>.datawarehouse.fabric.microsoft.com
```

Do not pass a SQLAlchemy URL, JDBC URL, password, bearer token, query string or connection-string fragment in a `--*-server` argument.

The Fabric Notebook runtime must have:

```text
pyodbc
Microsoft ODBC Driver 18 or newer for SQL Server
notebookutils.credentials
```

The exact Framework candidate provides the token-aware SQLAlchemy adapter. At connection time it requests a fresh Microsoft Entra SQL token for the SQL resource and injects it into the ODBC connection. The generated `CONTROL_PLANE_DATABASE_URL` and `WAREHOUSE_DATABASE_URL` values contain endpoint/database/driver metadata only; no token or password is embedded.

Warehouse administrator/session-termination authority is deliberately **not** inherited from normal Fabric user authentication. The real ambiguous-COMMIT/session-control drill remains separately gated.

## 5. Preferred deployment — Azure CLI + Fabric user identity

From the Customer repository root, PowerShell example:

```powershell
python certification/fabric_items/deploy_fabric_items.py `
  --apply `
  --environment DEV `
  --workspace-id <CERTIFICATION_WORKSPACE_UUID> `
  --control-plane-server <CONTROL_PLANE_FABRIC_SQL_HOSTNAME> `
  --control-plane-database <CONTROL_PLANE_DATABASE_NAME> `
  --warehouse-server <WAREHOUSE_SQL_HOSTNAME> `
  --warehouse-database <WAREHOUSE_DATABASE_NAME>
```

The defaults are intentionally:

```text
--auth-mode azure-cli
--runtime-auth-mode fabric-user
```

So no `FABRIC_ACCESS_TOKEN` environment variable and no Key Vault arguments are required for the normal interactive data-engineer path.

`--apply` is mandatory because the command mutates the target Fabric workspace.

The deployer performs:

```text
validate DEV/UAT + workspace UUID + runtime binding mode
-> obtain Fabric API token from current az login session
-> list Notebook items by type
-> require zero or one exact display-name match
-> create Notebook or update its definition
-> obtain actual Notebook item UUID
-> render Pipeline against that exact Notebook UUID
-> list DataPipeline items by type
-> require zero or one exact display-name match
-> create Data Pipeline or update its definition
-> poll Fabric long-running operations when required
-> write non-secret deployment-result.json
```

Exact duplicate display names fail closed. The deployer never guesses which item to overwrite.

Expected output:

```text
build/fabric-items/deployment-result.json
```

Representative shape:

```json
{
  "schema_version": 1,
  "environment": "DEV",
  "workspace_id": "<workspace-uuid>",
  "runtime_auth_mode": "fabric-user",
  "notebook": {
    "id": "<notebook-uuid>",
    "display_name": "framework-certification-worker",
    "action": "created",
    "definition_sha256": "<sha256>"
  },
  "pipeline": {
    "id": "<pipeline-uuid>",
    "display_name": "framework-certification-child",
    "action": "created",
    "definition_sha256": "<sha256>"
  },
  "customer_inputs_root": "/lakehouse/default/Files/framework_cert/customer-inputs",
  "contains_secret_values": false,
  "certification_result": "NOT_RUN"
}
```

The actual action is `created` or `updated`.

**Stop condition:** if the command exits non-zero, reports duplicate names, cannot obtain a Fabric token, rejects a SQL binding, receives a Fabric API error, or a long-running operation fails/times out, stop. Never edit `deployment-result.json` by hand to invent IDs or PASS state.

## 6. Optional enterprise API token lane

For non-interactive automation where your organization deliberately supplies a token through a protected runtime environment:

```bash
export FABRIC_ACCESS_TOKEN='<approved runtime token>'
python certification/fabric_items/deploy_fabric_items.py \
  --apply \
  --auth-mode env-token \
  --runtime-auth-mode fabric-user \
  --environment DEV \
  --workspace-id <CERTIFICATION_WORKSPACE_UUID> \
  --control-plane-server <CONTROL_PLANE_FABRIC_SQL_HOSTNAME> \
  --control-plane-database <CONTROL_PLANE_DATABASE_NAME> \
  --warehouse-server <WAREHOUSE_SQL_HOSTNAME> \
  --warehouse-database <WAREHOUSE_DATABASE_NAME>
```

Never put the token in the command line itself.

## 7. Optional Key Vault runtime lane

Use this only where the organization intentionally gives the runtime access to an approved Key Vault containing complete SQLAlchemy database URLs.

```bash
export FABRIC_ACCESS_TOKEN='<approved runtime token>'
python certification/fabric_items/deploy_fabric_items.py \
  --apply \
  --auth-mode env-token \
  --runtime-auth-mode key-vault \
  --environment DEV \
  --workspace-id <CERTIFICATION_WORKSPACE_UUID> \
  --key-vault-url https://<approved-vault>.vault.azure.net/ \
  --control-plane-secret-name <CONTROL_PLANE_URL_SECRET_NAME> \
  --warehouse-secret-name <WAREHOUSE_URL_SECRET_NAME>
```

Only the Key Vault URL and secret **names** enter the Fabric definition. Secret values remain runtime-only.

Key Vault is an enhancement lane, not a prerequisite for a team that only has Fabric workspace rights.

## 8. What the deployer retains

Allowed non-secret anchors:

```text
DEV/UAT environment
workspace UUID
Notebook UUID
Pipeline UUID
exact display names
rendered-definition SHA256 fingerprints
create/update action
customer-inputs conventional path
runtime_auth_mode
```

Never retained:

```text
Fabric access token
Microsoft Entra SQL token
SQL password
Key Vault secret value
certification PASS/FAIL claim
```

For `fabric-user`, the Pipeline definition contains the non-secret Fabric SQL server/database identity. For `key-vault`, it contains the non-secret vault URL + secret names.

## 9. Render-only/manual fallback

Use only when another approved deployment mechanism must consume payload files.

Render the Notebook payload:

```bash
python certification/fabric_items/render_fabric_items.py notebook \
  --display-name framework-certification-worker \
  --output build/fabric-items/notebook-create.json
```

After that mechanism returns the real Notebook UUID, render the default Fabric-native Pipeline:

```bash
python certification/fabric_items/render_fabric_items.py pipeline \
  --display-name framework-certification-child \
  --workspace-id <CERTIFICATION_WORKSPACE_UUID> \
  --notebook-id <WORKER_NOTEBOOK_UUID> \
  --runtime-auth-mode fabric-user \
  --control-plane-server <CONTROL_PLANE_FABRIC_SQL_HOSTNAME> \
  --control-plane-database <CONTROL_PLANE_DATABASE_NAME> \
  --warehouse-server <WAREHOUSE_SQL_HOSTNAME> \
  --warehouse-database <WAREHOUSE_DATABASE_NAME> \
  --output build/fabric-items/pipeline-create.json
```

The renderer validates UUIDs, server/database identity, Key Vault references when selected, and unresolved placeholders. Do not patch around validation failure.

Manual deployment still produces `NOT_RUN`, not certification PASS.

## 10. Runtime SQL preflight in Fabric

Before bounded certification, the worker Notebook should prove the runtime can see an ODBC 18+ driver and can request a SQL token. Do not print the token.

Safe diagnostic example:

```python
import pyodbc
from notebookutils import credentials

print([name for name in pyodbc.drivers() if "ODBC Driver" in name and "SQL Server" in name])
token = credentials.getToken("https://database.windows.net/")
assert isinstance(token, str) and len(token) > 100
print("Fabric SQL token acquired")
del token
```

The exact Framework runtime adapter synthesizes `CONTROL_PLANE_DATABASE_URL` and `WAREHOUSE_DATABASE_URL` internally so existing SQLAlchemy-based Control Plane/Warehouse certification code remains compatible.

If the token call or ODBC driver check fails, the Fabric-native SQL lane is BLOCKED for that environment. Do not fall back to a pasted password.

## 11. Prepare the dedicated certification Warehouse fixtures

Run only against the dedicated DEV/UAT certification Warehouse:

```text
certification/fabric_items/sql/warehouse-certification-fixtures.sql
```

It provisions bounded fixture tables for Pipeline control, progress/checkpoint state, FULL -> REPLACE, WATERMARK -> SCD1/SCD2, retry/idempotency, reconciliation fail-closed, Copy landing and Spark landing.

Stop if you cannot prove the SQL target is the dedicated certification Warehouse.

## 12. Control Plane SQL Database

Use a dedicated certification Fabric SQL Database for the Control Plane.

Do not create DatasetConfig rows manually. The Framework first-time certification bootstrap owns schema/materialization after exact-wheel bounded PASS. The explicit first-time mutation boundary remains:

```python
allow_control_plane_migration=True
```

Normal reruns keep it false.

The Fabric-native runtime is equivalent to a runtime mapping containing:

```text
FABRIC_SQL_AUTH_MODE=fabric-user
CONTROL_PLANE_SQL_SERVER=<non-secret server>
CONTROL_PLANE_SQL_DATABASE=<non-secret database>
WAREHOUSE_SQL_SERVER=<non-secret server>
WAREHOUSE_SQL_DATABASE=<non-secret database>
```

The adapter then exposes compatible non-secret token-aware `CONTROL_PLANE_DATABASE_URL` and `WAREHOUSE_DATABASE_URL` values in-process.

The optional Key Vault lane still resolves the historical secret-bearing URL values directly.

## 13. Copy and Spark item identities remain separate

The Notebook/Pipeline deployer does not invent Copy/Spark bindings.

The exact Customer input builder still requires real values for:

```text
workspace-id
item-read-id
pipeline-item-id
copy-job-id
spark-job-id
control-plane-profile
```

Use the real Pipeline UUID from `deployment-result.json` for `pipeline-item-id`. Do not reuse it as the Copy or Spark item ID.

The canonical Customer enterprise control-plane profile remains:

```text
fabric_sql_database_v1
```

## 14. Exact Customer candidate input artifact

Generate through the existing `candidate-business-path-inputs` / `certification/build_candidate_inputs.py` path only after the exact current Framework executable identity is known.

The bundle binds:

```text
exact Framework candidate Git SHA
exact Framework wheel SHA256
exact Customer Git SHA
exact domain release hash
actual certification Fabric item UUIDs
exact Customer extension wheel SHA256
```

Do not edit retained bundle identities after generation.

Expected Lakehouse layout remains:

```text
/lakehouse/default/Files/framework_cert/
  CANDIDATE.json
  SHA256SUMS
  fabric_data_framework-<version>-py3-none-any.whl
  customer-inputs/
    INPUTS.json
    runner-config.json
    release-manifest.json
    project/
    dist/
```

## 15. Business-path runtime contract

There is no separate `BUSINESS_PATH_DRIVER_RUNTIME_JSON` or `BUSINESS_PATH_OBSERVER_RUNTIME_JSON` credential channel in the current reference implementation.

Business-path driver/observer still consume the exact runner-declared `WAREHOUSE_DATABASE_URL`; in Fabric-user mode that URL is non-secret and token-aware, and a fresh Entra token is injected at physical connection time.

## 16. Pipeline proof behavior

A provider run reaching Fabric `Completed` is not semantic success.

The proof chain remains:

```text
seven exact parameters
-> Framework validates deployed DatasetConfig/effective hash/plan hash
-> Customer physical executor performs bounded fixture mutation
-> Framework persists exact DatasetRunAudit
-> Framework reads exact DatasetDispatchOutcome
```

Therefore the run fails closed when provider `Completed` cannot be correlated to the exact durable `DatasetDispatchOutcome`.

Customer code cannot self-declare release-readiness PASS.

## 17. Still-blocked enterprise evidence

Making Key Vault optional does not manufacture enterprise evidence. Strict blockers remain until real evidence exists, including:

```text
control_plane_external_evidence_incomplete
control_plane_external_evidence_not_review_bound
warehouse_real_fault_controller_not_configured
```

The default Fabric user identity also does not authorize Warehouse session termination. That remains a separately reviewed/admin-controlled capability.

## 18. New-conversation recovery

After context reset, read current GitHub `main` in this order:

```text
1. docs/CURRENT_STATUS.md
2. docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
3. docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
4. certification/fabric_items/deploy_fabric_items.py
5. certification/fabric_items/render_fabric_items.py
6. certification/project/config/certification/pipeline-worker.json
7. fabric-data-framework/docs/machine/STATE.md
8. fabric-data-framework/docs/machine/UNIFIED_CERTIFICATION.md
9. fabric-data-framework/docs/human/ONE_CALL_CERTIFICATION_RUNTIME.md
```

Then verify the exact current Framework substantive executable source/main-CI artifact identity and exact Customer source SHA before continuing. Never recover executable candidate identity from chat memory alone.
