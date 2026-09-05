# Runbook — Test Framework in Company Fabric

Status: unified real-Fabric certification is the default path. The original 2026-09-03 bounded test remains historical evidence for its exact old wheel only.

This is the Customer-side operator entrypoint for testing an exact Framework candidate in company Fabric. New candidates should not require an engineer to copy many Notebook cells, build a random Pipeline by hand, manually fill PASS/FAIL dropdowns, manually create the repository-owned certification Notebook/Pipeline, or hand-copy Fabric item GUIDs when the approved Fabric API path is available.

Canonical companion runbooks:

```text
fabric-customer/docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
fabric-data-framework/docs/human/FRAMEWORK_DEVELOPER_CERTIFICATION.md
fabric-data-framework/docs/human/ONE_CALL_CERTIFICATION_RUNTIME.md
fabric-data-framework/docs/human/FABRIC_PIPELINE_CHILD_CONTRACT.md
```

## 1. CI versus real Fabric

PR/main CI proves deterministic Framework and Customer contracts. Real Fabric certification proves one **exact built Framework wheel** against one real approved tenant/resource set.

Do not run the entire pytest suite inside Fabric merely to duplicate CI.

If Framework executable source changes after a real-Fabric run, old PASS values remain evidence only for the old wheel bytes.

## 2. Deploy the repository-owned Notebook/Pipeline; do not improvise

The Customer repo owns:

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
```

Follow:

```text
docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
```

Preferred DEV deployment path:

```bash
export FABRIC_ACCESS_TOKEN='<approved runtime token>'
python certification/fabric_items/deploy_fabric_items.py \
  --apply \
  --environment DEV \
  --workspace-id <CERTIFICATION_WORKSPACE_UUID> \
  --key-vault-url https://<approved-vault>.vault.azure.net/ \
  --control-plane-secret-name <CONTROL_PLANE_URL_SECRET_NAME> \
  --warehouse-secret-name <WAREHOUSE_URL_SECRET_NAME>
```

Do not put the token in a CLI argument, Notebook, Git, retained evidence or chat. The deployment record deliberately says:

```text
certification_result = NOT_RUN
```

Successful item deployment is not certification PASS.

The reusable Pipeline forwards exactly seven Framework-owned dynamic parameters:

```text
framework_pipeline_run_id
framework_dataset_run_id
dataset_id
run_mode
attempt
effective_config_hash
execution_plan_hash
```

Fabric provider `Completed` is not enough. The worker must persist the exact Framework `DatasetRunAudit`/`DatasetDispatchOutcome` for the generated dataset-run ID.

## 3. Resolve exact Fabric physical bindings by human-readable names

After the deployment command succeeds, use the read-only resolver instead of manually copying workspace/Pipeline/Copy/Spark/item-read UUIDs:

```bash
python certification/fabric_items/resolve_fabric_bindings.py \
  --deployment-result build/fabric-items/deployment-result.json \
  --item-read-type <ACTUAL_ITEM_TYPE> \
  --item-read-display-name '<EXACT_READ_ITEM_DISPLAY_NAME>' \
  --copy-job-display-name '<EXACT_COPY_JOB_DISPLAY_NAME>' \
  --spark-job-display-name '<EXACT_SPARK_JOB_DISPLAY_NAME>'
```

Expected output:

```text
build/fabric-items/fabric-bindings.json
```

The resolver re-verifies the exact Notebook and DataPipeline UUIDs from deployment, then resolves:

```text
item-read        exact caller-supplied Fabric type + exact display name
Pipeline         DataPipeline + deployed exact display name/UUID
Copy             CopyJob + exact display name
Spark            SparkJobDefinition + exact display name
```

Missing, ambiguous, wrong-type, wrong-workspace, or changed Notebook/Pipeline identity fails closed. The resolver is read-only and retains no token or SQL secret values.

The binding record deliberately says:

```text
verification_status = VERIFIED
contains_secret_values = false
certification_result = NOT_RUN
```

`VERIFIED` means only that those physical item identities were read from Fabric and cross-checked; it is not a Framework test PASS.

Once this succeeds, remove the setup API token from the local environment according to company policy.

## 4. Conventional Lakehouse layout and exact Framework artifact

Use an isolated/approved certification workspace, normally DEV first.

Create/use:

```text
Files/framework_cert/
```

The attached default Lakehouse exposes:

```text
/lakehouse/default/Files/framework_cert/
```

Place the exact Framework successful-main-CI artifact contents there:

```text
CANDIDATE.json
SHA256SUMS
fabric_data_framework-<version>-py3-none-any.whl
```

Keep exactly one Framework wheel in this directory.

## 5. Bounded certification comes first

Install the exact Framework wheel, restart the Notebook session if Fabric requires it, then run:

```python
from fabric_data_framework.certification import certify, print_certification_summary

report = certify(spark=spark)
print_certification_summary(report)
```

This runs:

```text
identity.exact
lakehouse.smoke
full.replace
watermark.scd1
watermark.scd2
retry.idempotency
reconciliation.fail_closed
```

Expected output directory:

```text
Files/framework_cert/certification-output/
```

With no `customer-inputs/`, overall `PARTIAL` can be correct when every bounded check is PASS and environment-specific stages are legitimately not configured.

**Stop on any real bounded FAIL.** Do not proceed to SQL/Pipeline/Warehouse mutations just to see whether later checks pass.

## 6. Build the exact Customer input bundle from verified bindings

Full environment stages require an exact Customer candidate-input artifact for the same Framework candidate and exact Customer source SHA intended for the run.

For a real environment, prefer:

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

The builder re-validates the binding schema, environment, UUIDs and exact item types before writing `runner-config.json`. It copies the exact verified physical binding record into the retained bundle and records its SHA256 in `INPUTS.json`.

Expected retained shape:

```text
customer-inputs/
  INPUTS.json
  runner-config.json
  release-manifest.json
  fabric-bindings.json       # when verified binding-file path is used
  project/
  dist/
```

`INPUTS.json` records:

```text
physical_binding_source = verified_fabric_bindings
fabric_bindings_sha256 = <exact retained binding-file SHA256>
```

The builder still supports the old explicit `--workspace-id/--item-read-id/--pipeline-item-id/--copy-job-id/--spark-job-id` path for controlled fallback. Without `--fabric-bindings`, all five explicit UUIDs are required. If a verified file and explicit values are both supplied, mismatches fail closed.

When retained GitHub workflow provenance is required, use the existing `candidate-business-path-inputs` workflow and record the exact workflow artifact. Do not claim a locally built bundle has GitHub workflow provenance it does not have.

Do not manually edit an exact retained bundle to swap GUIDs or hashes.

## 7. Runtime values are explicit and shared consistently

The source-controlled/retained Customer bundle stores runtime variable **names**, never SQL secret values.

Reference names:

```text
FABRIC_ACCESS_TOKEN
CONTROL_PLANE_DATABASE_URL
WAREHOUSE_DATABASE_URL
WAREHOUSE_ADMIN_DATABASE_URL   # only when separately required/approved
```

For full certification, prefer an explicit runtime mapping from an organization-approved secret mechanism:

```python
runtime_environment = {
    "CONTROL_PLANE_DATABASE_URL": control_plane_database_url,
    "WAREHOUSE_DATABASE_URL": warehouse_database_url,
}
```

Do not paste real connection strings into this repo or retained evidence.

The Framework one-call API temporarily mirrors only exact runner-declared runtime names into process environment while the certification call runs, then restores the prior process environment.

Current business-path driver/observer use the same exact:

```text
WAREHOUSE_DATABASE_URL
```

There is no separate JSON-wrapped business-path database-secret channel to configure.

## 8. Full ordinary live certification

Only after dedicated DEV/UAT certification resources and ordinary certification mutations are approved:

```python
from fabric_data_framework.certification import certify, print_certification_summary

runtime_environment = {
    "CONTROL_PLANE_DATABASE_URL": control_plane_database_url,
    "WAREHOUSE_DATABASE_URL": warehouse_database_url,
}

report = certify(
    spark=spark,
    runtime_environment=runtime_environment,
    allow_live_mutations=True,
)
print_certification_summary(report)
```

The runner attempts the configured sequence:

```text
bounded suite
-> Fabric item read
-> real Control Plane reference conformance
-> reviewed Control Plane evidence/certification
-> reusable Pipeline + durable Framework outcome
-> Copy
-> Spark
-> Warehouse normal COMMIT
-> reviewed ambiguous-COMMIT fault drill
-> strict integration evidence merge
-> full.replace live business path
-> watermark.scd1 live business path
-> watermark.scd2 live business path
-> retry.idempotency live business path
-> reconciliation.fail_closed live business path
-> merged business-path proof bundle
```

Missing evidence/configuration/authorization stays `BLOCKED` or `NOT_RUN`. Do not manufacture PASS values.

## 9. First-time dedicated Fabric SQL Control Plane

A brand-new certification SQL Database needs both current Framework Control Plane schema and exact Customer semantic DatasetConfig definitions.

For the **first approved bootstrap only**:

```python
report = certify(
    spark=spark,
    runtime_environment=runtime_environment,
    allow_live_mutations=True,
    allow_control_plane_migration=True,
)
```

The public API is fail-closed:

```text
bounded exact-wheel checks must all PASS
-> Customer INPUTS must match the same Framework candidate SHA/wheel/version
-> resolve exact configured Control Plane URL
-> apply baseline schema
-> idempotently materialize exact Customer semantic metadata
-> verify config bundle hash
-> proceed to normal unified stages
```

If bounded checks fail, SQL bootstrap is not attempted. Normal reruns keep `allow_control_plane_migration=False`.

Never enable first-time bootstrap against a shared/production SQL Control Plane just to make certification green.

## 10. Seven Control Plane external-evidence references remain real governance

The unified runner does not eliminate enterprise evidence requirements:

```text
backend_service_identity_reference
identity_access_control_reference
network_security_reference
backup_restore_reference
availability_recovery_reference
monitoring_alerting_reference
retention_governance_reference
```

Fail-closed blockers remain:

```text
control_plane_external_evidence_incomplete
control_plane_external_evidence_not_review_bound
```

Successful SQL connectivity is not a substitute.

## 11. Warehouse ambiguous COMMIT remains separately governed

A real fault drill requires a reviewed reachable fault controller from exact Customer inputs.

Until configured:

```text
warehouse_real_fault_controller_not_configured
```

remains a real blocker.

`allow_live_mutations=True` does not imply Admin/session-control permission.

Only if governance explicitly authorizes exact-session termination against the isolated certification Warehouse:

```python
runtime_environment = {
    "CONTROL_PLANE_DATABASE_URL": control_plane_database_url,
    "WAREHOUSE_DATABASE_URL": warehouse_database_url,
    "WAREHOUSE_ADMIN_DATABASE_URL": warehouse_admin_database_url,
}

report = certify(
    spark=spark,
    runtime_environment=runtime_environment,
    allow_live_mutations=True,
    allow_warehouse_session_termination=True,
)
```

Never fault inject or terminate sessions against shared/PROD resources.

## 12. Unified status semantics

```text
PASS      actual stage ran and passed
FAIL      actual stage ran and failed
NOT_RUN   stage intentionally did not execute
BLOCKED   required external/config prerequisite is not ready
```

A real FAIL must be retained and investigated. Missing permission/evidence does not become synthetic PASS.

The unified report always has:

```text
release_authorized = false
```

Certification does not select/freeze a candidate and does not publish Framework 0.4.

## 13. Customer production pin boundary

Until immutable Framework `v0.4.0` is actually published and governance permits migration, keep exactly:

```text
fabric-data-framework==0.3.0
```

Candidate compatibility/certification source may be 0.4 while production dependency remains 0.3.0. Do not conflate these lanes.

## 14. Historical first company run — old bytes only

The first bounded company-Fabric execution occurred on 2026-09-03.

Exact historical identity:

```text
framework-ci main run   33381666892
Framework SHA           303683729c4915d78200d463a6def01c8de9eae6
wheel SHA256            0638c95c19ebcc43ec4ec462b7f960a164209874223517e3f74b951264b0eaf6
```

Observed result:

```text
identity                           PASS
lakehouse.smoke                    PASS
full.replace                       PASS
watermark.scd1                     PASS
watermark.scd2                     PASS
retry.idempotency                  PASS
reconciliation.fail_closed         PASS
warehouse.commit                   NOT_RUN
warehouse.ambiguous_commit         NOT_RUN
manual certification               CERTIFIED / NOTEBOOK
admin override                     false
release authorized                 false
```

That evidence remains valid for those exact old bytes only. It cannot be copied onto the current Framework PR #105 wheel.

## 15. Manual cells/form are fallback diagnostics

Older explicit diagnostic paths remain useful for isolating failures:

```text
fabric-data-framework/docs/human/FIRST_FABRIC_NOTEBOOK_TEST.md
fabric-data-framework/docs/human/MANUAL_CERTIFICATION.md
```

The form is a result recorder, not a test executor.

## 16. New-conversation recovery

Always re-read current GitHub `main`, not chat memory:

```text
1. fabric-customer/docs/CURRENT_STATUS.md
2. fabric-customer/docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
3. fabric-customer/docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
4. fabric-customer/certification/fabric_items/deploy_fabric_items.py
5. fabric-customer/certification/fabric_items/resolve_fabric_bindings.py
6. fabric-customer/certification/build_candidate_inputs.py
7. fabric-customer/docs/runbooks/CONTROL_PLANE_EXTERNAL_EVIDENCE_REVIEW.md
8. fabric-data-framework/docs/machine/STATE.md
9. fabric-data-framework/docs/machine/UNIFIED_CERTIFICATION.md
10. fabric-data-framework/docs/human/ONE_CALL_CERTIFICATION_RUNTIME.md
```

Then verify:

```text
current Framework substantive executable source SHA / independent main CI
current exact Framework wheel SHA256
current Customer substantive certification/deployment source SHA / independent CI
candidate_status = not_frozen unless explicit governance changed it
release_allowed = false unless explicit release governance changed it
Customer production pin
control-plane external-evidence blockers
Warehouse fault-controller blocker
actual company-Fabric deployment/binding state
```

If Framework executable source changed after the last real-Fabric run, obtain a new exact successful-main artifact before continuing testing.
