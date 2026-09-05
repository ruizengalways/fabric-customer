# Runbook — Deploy the reusable certification Fabric items

Audience: a data engineer preparing an isolated company Fabric DEV/UAT workspace for exact Framework certification.

This runbook exists so a new engineer does **not** build an arbitrary Pipeline by hand. The repository owns a deterministic worker Notebook, reusable Data Pipeline template, fail-closed deployer, render-only fallback, Warehouse fixture DDL and exact Customer certification configuration.

## 1. Safety boundary

Use only an isolated or explicitly approved certification workspace and dedicated certification Warehouse.

The repository deployer deliberately accepts only:

```text
DEV
UAT
```

It refuses `PROD`.

Never run the fixture DDL, business-path reset/mutation logic, Warehouse fault drill or session termination against a shared/production Warehouse.

Do not commit or pass on a command line:

```text
SQL connection strings
Fabric access-token values
passwords
Key Vault secret values
signed URLs
```

The deployer accepts only non-secret workspace bindings plus a credential-free Key Vault URL and secret **names**. The Fabric API token is read from an environment variable and is never written to `deployment-result.json`.

Creating/updating Fabric items is **not** certification. A successful deployment result deliberately records:

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

The Pipeline is reusable across the representative business paths. It is not one Pipeline per table.

The remote child contract has exactly seven Framework-owned dynamic parameters:

```text
framework_pipeline_run_id
framework_dataset_run_id
dataset_id
run_mode
attempt
effective_config_hash
execution_plan_hash
```

Do not rename them or add aliases. The Framework parent uses them to prove that provider completion and the durable Framework outcome belong to the same exact dataset execution.

## 3. Prerequisites

Before deployment, have these values available:

```text
certification environment: DEV or UAT
certification workspace UUID
Key Vault HTTPS URL
Key Vault secret name containing the Control Plane database URL
Key Vault secret name containing the certification Warehouse database URL
approved Microsoft Fabric API access token
```

The token must have the organization-approved permissions/role required to list and create/update Notebook/Data Pipeline items in the target workspace. Acquire it through your normal corporate identity/credential process.

Do **not** paste the token into this repository, a Notebook cell, shell history as a CLI argument, PR text, retained evidence or chat. Put it only in the runtime environment used for the deployment command.

The deployed worker Notebook must later execute in an environment where the exact Framework wheel/customer extension bundle used for certification is available according to the approved Fabric package/environment setup.

## 4. Preferred path — one-command create or update

Set the token in the local runtime environment. Example shell syntax:

```bash
export FABRIC_ACCESS_TOKEN='<approved runtime token>'
```

Then run from the Customer repository root:

```bash
python certification/fabric_items/deploy_fabric_items.py \
  --apply \
  --environment DEV \
  --workspace-id <CERTIFICATION_WORKSPACE_UUID> \
  --key-vault-url https://<approved-vault>.vault.azure.net/ \
  --control-plane-secret-name <CONTROL_PLANE_URL_SECRET_NAME> \
  --warehouse-secret-name <WAREHOUSE_URL_SECRET_NAME>
```

`--apply` is mandatory because this command mutates the target workspace.

The deployer performs this exact sequence:

```text
validate DEV/UAT + workspace UUID + safe deployment bindings
-> list Notebook items by type
-> require zero or one exact display-name match
-> create Notebook or update its definition
-> obtain the actual Notebook item UUID
-> render Pipeline against that exact Notebook UUID
-> list DataPipeline items by type
-> require zero or one exact display-name match
-> create Data Pipeline or update its definition
-> wait for Fabric long-running operations when required
-> write non-secret deployment-result.json
```

Exact duplicate display names fail closed. The tool never guesses which item to overwrite.

Expected output file:

```text
build/fabric-items/deployment-result.json
```

Representative shape:

```json
{
  "schema_version": 1,
  "environment": "DEV",
  "workspace_id": "<workspace-uuid>",
  "notebook": {
    "id": "<notebook-uuid>",
    "display_name": "framework-certification-worker",
    "action": "created-or-updated",
    "definition_sha256": "<sha256>"
  },
  "pipeline": {
    "id": "<pipeline-uuid>",
    "display_name": "framework-certification-child",
    "action": "created-or-updated",
    "definition_sha256": "<sha256>"
  },
  "contains_secret_values": false,
  "certification_result": "NOT_RUN"
}
```

The actual `action` value is `created` or `updated`.

**Stop condition:** if the command exits non-zero, reports duplicate items, an invalid binding, a Fabric API error, or a failed/timed-out long-running operation, stop. Do not manually edit the result file to invent item UUIDs.

After success, remove the token from the shell/runtime environment according to your organization policy.

## 5. What the deployer does and does not retain

The deployment result may retain these non-secret anchors:

```text
DEV/UAT environment
workspace UUID
Notebook UUID
Pipeline UUID
exact display names
rendered-definition SHA256 fingerprints
create/update action
customer-inputs conventional path
```

It does **not** retain:

```text
Fabric access token
Control Plane database URL
Warehouse database URL
Key Vault secret values
certification PASS/FAIL claims
```

The Key Vault URL and secret names are embedded in the Pipeline definition because the worker needs those non-secret references at runtime; the result file itself does not copy them back out.

## 6. Render-only/manual fallback

Use this fallback only when organizational policy does not permit the repository deployer to call Fabric item APIs and another approved deployment mechanism must consume payload files.

Render the Notebook payload:

```bash
python certification/fabric_items/render_fabric_items.py notebook \
  --display-name framework-certification-worker \
  --output build/fabric-items/notebook-create.json
```

Deploy that payload using the approved mechanism and record the actual Notebook item UUID. Then render the Pipeline payload:

```bash
python certification/fabric_items/render_fabric_items.py pipeline \
  --display-name framework-certification-child \
  --workspace-id <CERTIFICATION_WORKSPACE_UUID> \
  --notebook-id <WORKER_NOTEBOOK_UUID> \
  --key-vault-url https://<approved-vault>.vault.azure.net/ \
  --control-plane-secret-name <CONTROL_PLANE_URL_SECRET_NAME> \
  --warehouse-secret-name <WAREHOUSE_URL_SECRET_NAME> \
  --output build/fabric-items/pipeline-create.json
```

Deploy the resulting Pipeline definition and record the actual Pipeline UUID.

The renderer rejects malformed UUIDs, credential-bearing Key Vault URLs, unsafe secret names and unresolved placeholders. Do not patch around a validation failure.

Manual fallback has the same semantic boundary as the deployer: item creation/update does not produce a certification PASS.

## 7. Prepare the dedicated certification Warehouse fixtures

Open:

```text
certification/fabric_items/sql/warehouse-certification-fixtures.sql
```

Run it only against the dedicated certification DEV/UAT Warehouse after confirming the target database identity.

The script provisions the bounded tables used by:

```text
Pipeline control
progress/checkpoint state
FULL -> REPLACE
WATERMARK -> SCD1
WATERMARK -> SCD2 current/history
retry/idempotency
reconciliation fail-closed
Copy landing
Spark landing
```

Stop immediately if you cannot prove the SQL connection targets the dedicated certification Warehouse.

The script is fixture provisioning only. It is not a substitute for the Framework-approved normal Warehouse COMMIT or ambiguous-COMMIT evidence runners.

## 8. Control Plane SQL Database

Use a dedicated certification SQL Database for the Control Plane.

Do not create DatasetConfig rows manually. The Framework one-call first-time bootstrap owns the correct sequence after bounded exact-wheel PASS:

```python
report = certify(
    spark=spark,
    runtime_environment={
        "CONTROL_PLANE_DATABASE_URL": control_plane_database_url,
        "WAREHOUSE_DATABASE_URL": warehouse_database_url,
    },
    allow_live_mutations=True,
    allow_control_plane_migration=True,
)
```

That explicit first-time path applies the current Control Plane schema **and** idempotently materializes the exact Customer semantic metadata. A schema-only database is not enough for the durable Pipeline child because the Framework verifies deployed DatasetConfig hashes.

Normal reruns keep `allow_control_plane_migration=False`.

## 9. Copy and Spark certification items remain separate

The exact Customer bundle also binds configured Copy and Spark item UUIDs used by the approved capture runners.

The Notebook/Pipeline deployer does **not** create or invent these bindings. They remain independent physical items.

The Customer input builder requires:

```text
workspace-id
item-read-id
pipeline-item-id
copy-job-id
spark-job-id
control-plane-profile
```

Use the real Pipeline UUID from `deployment-result.json` for `pipeline-item-id`. Use separately verified real UUIDs for item-read/Copy/Spark. Never substitute the Pipeline UUID for all item types.

## 10. Produce the exact Customer certification input artifact

Use the existing `candidate-business-path-inputs` workflow / `certification/build_candidate_inputs.py` path for the exact Framework candidate and exact Customer source SHA intended for the run.

The retained bundle must contain:

```text
INPUTS.json
runner-config.json
release-manifest.json
project/
dist/
```

and bind:

```text
exact Framework candidate Git SHA
exact Framework wheel SHA256
exact Customer Git SHA
exact domain release hash
actual certification Fabric item UUIDs
exact Customer extension wheel SHA256
```

Do not edit the retained bundle after generation to swap item IDs or hashes.

## 11. Upload/extract the exact bundle into the certification Lakehouse

Expected layout:

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

The Framework public API validates exact candidate SHA/wheel/version identity before using Customer inputs.

## 12. Runtime secret resolution

The reusable Pipeline worker resolves SQL URLs at execution time from the configured Key Vault URL + secret names.

The top-level unified certification call can use equivalent approved runtime values:

```python
runtime_environment = {
    "CONTROL_PLANE_DATABASE_URL": control_plane_database_url,
    "WAREHOUSE_DATABASE_URL": warehouse_database_url,
}
```

The Framework temporarily exposes only exact runner-declared runtime variable names to Customer/domain extension entry points during the call, then restores the previous process environment.

There is no separate `BUSINESS_PATH_DRIVER_RUNTIME_JSON` or `BUSINESS_PATH_OBSERVER_RUNTIME_JSON` secret channel in the current reference implementation. Business-path driver/observer use the same exact `WAREHOUSE_DATABASE_URL` runtime binding as the approved Warehouse/capture surfaces.

## 13. Expected Pipeline proof behavior

A provider run reaching Fabric `Completed` is not enough.

The worker executes:

```text
seven exact parameters
-> Framework validates deployed DatasetConfig/effective hash/plan hash
-> Customer physical executor performs the bounded fixture mutation
-> Framework persists exact DatasetRunAudit
-> Framework reads exact DatasetDispatchOutcome
```

Therefore certification fails closed when:

```text
Pipeline Completed but no exact durable outcome exists
Pipeline used the wrong DatasetConfig hash
Pipeline used a different execution plan hash
business-path expected a retry/failure but outcome semantics differ
```

Customer code cannot self-declare release-readiness PASS.

## 14. What this deployment still does not solve

Automated Notebook/Pipeline deployment reduces operator setup work, but it does not manufacture enterprise release evidence.

Current strict blockers remain real until independently satisfied:

```text
control_plane_external_evidence_incomplete
control_plane_external_evidence_not_review_bound  # once refs exist but review binding is wrong/missing
warehouse_real_fault_controller_not_configured
```

It also does not provision/approve:

```text
seven Control Plane enterprise evidence records
Warehouse ambiguous-COMMIT fault controller
Warehouse administrator session-termination authorization
Copy/Spark item identities
exact selected-candidate Customer input bundle
```

Do not configure placeholders merely to clear a blocker.

## 15. New-conversation recovery

After a context reset, read current GitHub `main` in this order:

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

Then verify the exact Framework substantive executable source/main-CI artifact identity and exact Customer source SHA before continuing. Never recover executable candidate identity from chat memory alone.
