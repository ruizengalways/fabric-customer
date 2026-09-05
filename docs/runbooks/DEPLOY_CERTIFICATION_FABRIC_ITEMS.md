# Runbook — Deploy and bind the reusable certification Fabric items

Audience: a data engineer preparing an isolated company Fabric DEV/UAT workspace for exact Framework certification.

This runbook exists so a new engineer does **not** build an arbitrary Pipeline by hand and does **not** manually copy Fabric item UUIDs when the approved Fabric API is available. The repository owns a deterministic worker Notebook, reusable Data Pipeline template, fail-closed deployer, read-only binding resolver, render-only fallback, Warehouse fixture DDL and exact Customer certification configuration.

## 1. Safety boundary

Use only an isolated or explicitly approved certification workspace and dedicated certification Warehouse.

The mutating repository deployer deliberately accepts only:

```text
DEV
UAT
```

It refuses `PROD`.

Never run fixture DDL, business-path reset/mutation logic, Warehouse fault drill or session termination against a shared/production Warehouse.

Do not commit or pass on a command line:

```text
SQL connection strings
Fabric access-token values
passwords
Key Vault secret values
signed URLs
```

The deployer accepts only non-secret workspace bindings plus a credential-free Key Vault URL and secret **names**. The Fabric API token is read from an environment variable and is never written to `deployment-result.json` or `fabric-bindings.json`.

Creating/updating or resolving Fabric items is **not** certification. Both setup records deliberately retain:

```text
certification_result = NOT_RUN
```

## 2. Repository-owned reference implementation

Canonical files:

```text
certification/fabric_items/
  deploy_fabric_items.py
  resolve_fabric_bindings.py
  render_fabric_items.py
  notebook/certification-pipeline-worker.ipynb
  pipeline/pipeline-content.template.json
  sql/warehouse-certification-fixtures.sql

certification/project/config/certification/pipeline-worker.json
certification/extensions/src/fabric_customer_certification_extensions/pipeline_worker.py
certification/build_candidate_inputs.py
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

For exact binding resolution, also know the **display names**, not UUIDs, of the already-existing physical items used for:

```text
read-only Fabric item smoke         + its exact Fabric item type
Copy capture certification          CopyJob
Spark capture certification         SparkJobDefinition
```

Example item-read type may be `Lakehouse` if that is the approved item used for the read-only smoke. Do not assume the type; use the actual item type in your environment.

The token must have the organization-approved permissions/role required to read/list items and, for the deployment command, create/update Notebook/Data Pipeline items in the target workspace. Acquire it through the normal corporate identity/credential process.

Do **not** paste the token into this repository, a Notebook cell, shell history as a CLI argument, PR text, retained evidence or chat. Put it only in the runtime environment used by the commands.

The deployed worker Notebook must later execute in an environment where the exact Framework wheel/customer extension bundle used for certification is available according to the approved Fabric package/environment setup.

## 4. Preferred path — one-command Notebook/Pipeline create or update

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

## 5. Preferred path — resolve all exact physical item bindings by display name

After Notebook/Pipeline deployment succeeds, keep the same short-lived approved Fabric token in the runtime environment long enough to run the **read-only** resolver:

```bash
python certification/fabric_items/resolve_fabric_bindings.py \
  --deployment-result build/fabric-items/deployment-result.json \
  --item-read-type <ACTUAL_ITEM_TYPE> \
  --item-read-display-name '<EXACT_READ_ITEM_DISPLAY_NAME>' \
  --copy-job-display-name '<EXACT_COPY_JOB_DISPLAY_NAME>' \
  --spark-job-display-name '<EXACT_SPARK_JOB_DISPLAY_NAME>'
```

Example only, when the read smoke intentionally targets a Lakehouse:

```bash
python certification/fabric_items/resolve_fabric_bindings.py \
  --item-read-type Lakehouse \
  --item-read-display-name 'certification-lakehouse' \
  --copy-job-display-name 'framework-certification-copy' \
  --spark-job-display-name 'framework-certification-spark'
```

The example display names are not defaults and are not evidence that those items exist in your workspace. Use the actual approved names.

The resolver performs no Fabric mutations. It:

```text
loads deployment-result.json
-> requires schema_version=1 / DEV|UAT / contains_secret_values=false / certification_result=NOT_RUN
-> re-reads exact Notebook by type + display name
-> requires its real UUID still equals the deployment record
-> re-reads exact DataPipeline by type + display name
-> requires its real UUID still equals the deployment record
-> resolves item-read by exact user-supplied item type + display name
-> resolves CopyJob by exact display name
-> resolves SparkJobDefinition by exact display name
-> fails if an exact item is missing or ambiguous
-> writes one credential-free verified binding record
```

Expected output:

```text
build/fabric-items/fabric-bindings.json
```

Representative shape:

```json
{
  "schema_version": 1,
  "verification_status": "VERIFIED",
  "environment": "DEV",
  "workspace_id": "<workspace-uuid>",
  "deployment_result_sha256": "<sha256>",
  "notebook": {
    "id": "<notebook-uuid>",
    "type": "Notebook",
    "display_name": "framework-certification-worker"
  },
  "item_read": {
    "id": "<item-read-uuid>",
    "type": "<actual-item-type>",
    "display_name": "<actual-display-name>"
  },
  "pipeline": {
    "id": "<pipeline-uuid>",
    "type": "DataPipeline",
    "display_name": "framework-certification-child"
  },
  "copy_job": {
    "id": "<copy-job-uuid>",
    "type": "CopyJob",
    "display_name": "<actual-display-name>"
  },
  "spark_job": {
    "id": "<spark-job-uuid>",
    "type": "SparkJobDefinition",
    "display_name": "<actual-display-name>"
  },
  "contains_secret_values": false,
  "certification_result": "NOT_RUN"
}
```

This is the preferred physical-binding input to the Customer candidate-input builder. The engineer no longer needs to copy the workspace/Pipeline/Copy/Spark/item-read UUIDs into the builder command.

**Stop condition:** if the resolver says an item is missing, duplicated, wrong type, in another workspace, or the Notebook/Pipeline UUID no longer matches the deployment record, stop. Do not pick a visually similar item or edit the JSON by hand.

After the resolver succeeds, remove the API token from the shell/runtime environment according to organization policy. The next local packaging command does not need Fabric API access.

## 6. What setup records do and do not retain

The deployment/binding records may retain these non-secret anchors:

```text
DEV/UAT environment
workspace UUID
exact Notebook/Pipeline/item-read/Copy/Spark UUIDs
exact item types
exact display names
rendered-definition SHA256 fingerprints
deployment-result SHA256
create/update action
customer-inputs conventional path
```

They do **not** retain:

```text
Fabric access token
Control Plane database URL
Warehouse database URL
Key Vault secret values
certification PASS/FAIL claims
```

The Key Vault URL and secret names are embedded in the Pipeline definition because the worker needs those non-secret references at runtime; the deployment/binding output does not copy the actual database URL secret values.

## 7. Render-only/manual deployment fallback

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

If API read/list access is allowed even though mutation is not, you may still construct a deployment-result-equivalent record only through an organization-approved process and then run the read-only resolver. Otherwise retain exact IDs through the approved manual process and use the builder's backwards-compatible explicit binding flags.

Manual fallback has the same semantic boundary as the deployer: item creation/update does not produce a certification PASS.

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

That explicit first-time path applies the current Control Plane schema **and** idempotently materializes the exact Customer semantic metadata. A schema-only database is not enough for the durable Pipeline child because the Framework verifies deployed DatasetConfig hashes.

Normal reruns keep `allow_control_plane_migration=False`.

## 10. Produce the exact Customer certification input artifact

For a real environment, prefer the verified binding file produced above:

```bash
python certification/build_candidate_inputs.py \
  --extension-wheel <EXACT_CUSTOMER_CERTIFICATION_EXTENSION_WHEEL> \
  --output <EXACT_OUTPUT_DIRECTORY> \
  --customer-git-sha <EXACT_CUSTOMER_GIT_SHA> \
  --candidate-git-sha <EXACT_FRAMEWORK_GIT_SHA> \
  --candidate-wheel-sha256 <EXACT_FRAMEWORK_WHEEL_SHA256> \
  --framework-version 0.4.0 \
  --environment DEV \
  --fabric-bindings build/fabric-items/fabric-bindings.json \
  --control-plane-profile fabric_sql_database_v1
```

The builder validates that:

```text
binding schema is supported
verification_status = VERIFIED
environment matches
contains_secret_values = false
certification_result = NOT_RUN
deployment_result_sha256 is a real lowercase SHA256
Pipeline type = DataPipeline
Copy type = CopyJob
Spark type = SparkJobDefinition
Notebook type = Notebook
all retained IDs are UUIDs
optional explicit IDs, if also supplied, exactly match the verified file
```

The builder copies the exact verified record into the retained bundle as:

```text
fabric-bindings.json
```

and records its SHA256 in `INPUTS.json`:

```text
physical_binding_source = verified_fabric_bindings
fabric_bindings_sha256 = <sha256 of retained fabric-bindings.json>
```

The older explicit form remains supported for controlled fallback/testing:

```text
--workspace-id
--item-read-id
--pipeline-item-id
--copy-job-id
--spark-job-id
```

When `--fabric-bindings` is not supplied, **all five** explicit values are required and UUID-validated. If both a verified file and explicit values are supplied, every explicit value must match the verified file; disagreement fails closed.

Use the existing `candidate-business-path-inputs` workflow when retained GitHub producer provenance is required. That workflow still accepts explicit IDs and remains backwards compatible; do not claim a local bundle has GitHub workflow provenance it does not have.

The exact retained bundle may now contain:

```text
INPUTS.json
runner-config.json
release-manifest.json
fabric-bindings.json      # when verified binding-file path is used
project/
dist/
```

It binds:

```text
exact Framework candidate Git SHA
exact Framework wheel SHA256
exact Customer Git SHA
exact domain release hash
actual verified certification Fabric item UUIDs
exact Customer extension wheel SHA256
```

Do not edit the retained bundle after generation to swap item IDs or hashes.

## 11. Upload/extract the exact bundle into the certification Lakehouse

Expected layout when verified bindings were used:

```text
/lakehouse/default/Files/framework_cert/
  CANDIDATE.json
  SHA256SUMS
  fabric_data_framework-<version>-py3-none-any.whl
  customer-inputs/
    INPUTS.json
    runner-config.json
    release-manifest.json
    fabric-bindings.json
    project/
    dist/
```

The Framework public API validates exact candidate SHA/wheel/version identity before using Customer inputs. `fabric-bindings.json` is retained Customer-side physical-binding provenance; it does not by itself create a Framework PASS.

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

## 14. What this automation still does not solve

Deployment + binding resolution reduces operator setup work, but does not manufacture enterprise release evidence or physical items that do not exist.

It does **not** create the CopyJob or SparkJobDefinition. Those must already be real approved certification items before the resolver can find them. It also does not decide which item should own the read-only smoke; the engineer supplies the exact approved item type/name.

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
exact selected-candidate Customer input artifact provenance
```

Do not configure placeholders merely to clear a blocker.

## 15. Recommended operator sequence

For a new exact Framework real-Fabric run:

```text
1. verify current GitHub main/recovery docs and exact Framework executable wheel identity
2. obtain approved short-lived Fabric API access token
3. deploy/update repository-owned Notebook + Pipeline
4. resolve/verify Notebook + Pipeline + item-read + Copy + Spark into fabric-bindings.json
5. remove the Fabric API token from the local environment when no longer needed
6. provision/verify dedicated Warehouse fixture tables
7. build the exact Customer input bundle using --fabric-bindings
8. upload exact Framework wheel/CANDIDATE/SHA256SUMS + exact Customer bundle
9. run bounded certification first
10. STOP on any real bounded FAIL
11. use first-time Control Plane migration only for a new dedicated certification DB
12. proceed to ordinary live stages only with approved mutations
13. leave missing enterprise evidence/fault controller as BLOCKED/NOT_RUN
```

## 16. New-conversation recovery

After a context reset, read current GitHub `main` in this order:

```text
1. docs/CURRENT_STATUS.md
2. docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
3. docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
4. certification/fabric_items/deploy_fabric_items.py
5. certification/fabric_items/resolve_fabric_bindings.py
6. certification/build_candidate_inputs.py
7. certification/project/config/certification/pipeline-worker.json
8. fabric-data-framework/docs/machine/STATE.md
9. fabric-data-framework/docs/machine/UNIFIED_CERTIFICATION.md
10. fabric-data-framework/docs/human/ONE_CALL_CERTIFICATION_RUNTIME.md
```

Then verify the exact Framework substantive executable source/main-CI artifact identity and exact Customer source SHA before continuing. Never recover executable candidate identity from chat memory alone.
