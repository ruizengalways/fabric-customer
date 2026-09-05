# Runbook — Deploy the reusable certification Fabric items

Audience: a data engineer preparing an isolated company Fabric DEV/UAT workspace for exact Framework certification.

This runbook exists so a new engineer does **not** build an arbitrary Pipeline by hand. The repository owns a deterministic reference Notebook, Data Pipeline template, renderer, Warehouse fixture DDL and exact Customer certification configuration.

## 1. Safety boundary

Use only an isolated or explicitly approved certification workspace and dedicated certification Warehouse.

Never run the fixture DDL, business-path reset/mutation logic, Warehouse fault drill or session termination against a shared/production Warehouse.

Do not commit:

```text
SQL connection strings
access tokens
passwords
Key Vault secret values
signed URLs
```

The renderer accepts only non-secret deployment bindings. Runtime SQL URLs are resolved later from approved secrets.

## 2. Repository-owned reference implementation

Canonical files:

```text
certification/fabric_items/
  render_fabric_items.py
  notebook/certification-pipeline-worker.ipynb
  pipeline/pipeline-content.template.json
  sql/warehouse-certification-fixtures.sql

certification/project/config/certification/pipeline-worker.json
certification/extensions/src/fabric_customer_certification_extensions/pipeline_worker.py
```

The Pipeline is intentionally reusable across the representative business paths. It is not one Pipeline per table.

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

Do not rename them or add aliases. The Framework parent uses these values to prove that provider completion and the durable Framework outcome belong to the same exact dataset execution.

## 3. Prerequisites

Before rendering/deploying items, have these non-secret values available:

```text
certification workspace UUID
Key Vault HTTPS URL
Key Vault secret name containing the Control Plane database URL
Key Vault secret name containing the certification Warehouse database URL
```

The secret **names** may appear in deployment configuration. The secret values must not.

The worker Notebook must run in an environment where the exact Framework wheel used for certification is available according to the approved Fabric package/environment setup.

## 4. Render the worker Notebook create payload

From the Customer repo:

```bash
python certification/fabric_items/render_fabric_items.py notebook \
  --display-name framework-certification-worker \
  --output build/fabric-items/notebook-create.json
```

Expected result:

```text
build/fabric-items/notebook-create.json
```

The payload contains the repository Notebook definition encoded for Fabric item creation. It contains no SQL secret values.

Stop if the renderer fails. Do not manually patch an invalid payload to bypass its validation.

## 5. Create/update the worker Notebook in the certification workspace

Use your organization-approved Fabric deployment mechanism to create the Notebook from the rendered payload.

Record the resulting **Notebook item UUID** as an environment-local deployment binding. Do not put company-specific UUIDs into generic Framework source.

Expected state:

```text
workspace: dedicated certification DEV/UAT
Notebook: framework-certification-worker
Notebook item UUID: known locally for the next render step
```

No business-path PASS has been produced by creating the Notebook.

## 6. Render the reusable Data Pipeline payload

Using the actual workspace UUID and newly created Notebook UUID:

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

Expected result:

```text
build/fabric-items/pipeline-create.json
```

The renderer rejects malformed UUIDs, credential-bearing Key Vault URLs, unsafe secret names and unresolved template placeholders.

## 7. Create/update the Data Pipeline

Deploy `build/fabric-items/pipeline-create.json` with the approved Fabric item deployment mechanism.

The Pipeline must contain one Notebook activity that forwards the exact seven Framework parameters to `framework-certification-worker`.

Record the resulting **Pipeline item UUID**. This value is later bound into the exact Customer candidate-input artifact as the `fabric.pipeline` physical item.

Creating the Pipeline does not certify it. A real certification run must invoke it and read the exact durable Framework outcome.

## 8. Prepare the dedicated certification Warehouse fixtures

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

## 9. Control Plane SQL Database

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

That explicit first-time path applies the current Control Plane schema **and** idempotently materializes the exact Customer semantic metadata. A schema-only database is not enough for the durable Pipeline child because the Framework repository verifies deployed DatasetConfig hashes.

Normal reruns keep `allow_control_plane_migration=False`.

## 10. Copy and Spark certification items

The exact Customer bundle also binds the configured Copy and Spark item UUIDs used by the approved capture runners.

These are independent physical bindings from the reusable Pipeline child. Do not substitute the Pipeline UUID for Copy/Spark bindings simply because the Pipeline exists.

The Customer input builder requires:

```text
workspace-id
item-read-id
pipeline-item-id
copy-job-id
spark-job-id
control-plane-profile
```

These are environment-local non-secret identities. The builder fingerprints them into the exact runner configuration; the Notebook operator should not retype them during certification.

## 11. Produce the exact Customer certification input artifact

Use the existing `candidate-business-path-inputs` workflow / `certification/build_candidate_inputs.py` path for the exact Framework candidate and exact Customer main SHA.

The retained bundle must contain:

```text
INPUTS.json
runner-config.json
release-manifest.json
project/
dist/
```

and must bind:

```text
exact Framework candidate Git SHA
exact Framework wheel SHA256
exact Customer Git SHA
exact domain release hash
actual certification Fabric item UUIDs
exact Customer extension wheel SHA256
```

Do not edit the retained bundle after generation to swap item IDs or hashes.

## 12. Upload/extract the exact bundle into the certification Lakehouse

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

## 13. Runtime secret resolution

The reusable Pipeline worker resolves SQL URLs at execution time from the configured Key Vault URL + secret names.

The top-level unified certification call can use equivalent approved runtime variables:

```python
runtime_environment = {
    "CONTROL_PLANE_DATABASE_URL": control_plane_database_url,
    "WAREHOUSE_DATABASE_URL": warehouse_database_url,
}
```

The Framework temporarily exposes only exact runner-declared runtime variable names to Customer/domain extension entry points during the call, then restores the previous process environment.

There is no separate `BUSINESS_PATH_DRIVER_RUNTIME_JSON` or `BUSINESS_PATH_OBSERVER_RUNTIME_JSON` secret channel in the current reference implementation. Business-path driver/observer use the same exact `WAREHOUSE_DATABASE_URL` runtime binding as the approved Warehouse/capture surfaces.

## 14. Expected Pipeline proof behavior

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

## 15. What this deployment does not solve

The reference items make Pipeline/business-path execution deployable, but they do not manufacture enterprise release evidence.

Current strict blockers remain real until independently satisfied:

```text
control_plane_external_evidence_incomplete
control_plane_external_evidence_not_review_bound  # when refs exist but review binding is wrong/missing
warehouse_real_fault_controller_not_configured
```

Do not configure a placeholder Warehouse fault endpoint as though it were real evidence.

## 16. New-conversation recovery

After a context reset, read current GitHub `main` in this order:

```text
1. docs/CURRENT_STATUS.md
2. docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
3. docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
4. certification/fabric_items/render_fabric_items.py
5. certification/project/config/certification/pipeline-worker.json
6. fabric-data-framework/docs/machine/STATE.md
7. fabric-data-framework/docs/machine/UNIFIED_CERTIFICATION.md
8. fabric-data-framework/docs/human/ONE_CALL_CERTIFICATION_RUNTIME.md
```

Then verify the exact Framework main SHA/main-CI artifact identity and Customer main SHA before continuing. Never recover an executable candidate identity from chat memory alone.
