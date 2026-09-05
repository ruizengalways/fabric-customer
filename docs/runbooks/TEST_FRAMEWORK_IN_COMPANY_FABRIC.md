# Runbook — Test Framework in Company Fabric

Status: unified real-Fabric certification is the default path. The original 2026-09-03 bounded test remains historical evidence for its exact old wheel only.

This is the Customer-side operator entrypoint for testing an exact Framework candidate in company Fabric. New candidates should not require an engineer to copy many Notebook cells, build a random Pipeline by hand, or manually fill PASS/FAIL dropdowns.

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

If Framework source changes after a real-Fabric run, the old PASS values remain evidence only for the old wheel bytes.

## 2. Do not improvise the certification Pipeline

The Customer repo now owns a deployable reusable reference implementation:

```text
certification/fabric_items/
  render_fabric_items.py
  notebook/certification-pipeline-worker.ipynb
  pipeline/pipeline-content.template.json
  sql/warehouse-certification-fixtures.sql

certification/project/config/certification/pipeline-worker.json
certification/extensions/src/fabric_customer_certification_extensions/pipeline_worker.py
```

Before full Pipeline/business-path certification, deploy these items using:

```text
docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
```

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

## 3. Conventional Lakehouse layout

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

## 4. Bounded certification comes first

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

## 5. Exact Customer input bundle

Full environment stages require the exact Customer candidate-input artifact produced for the same Framework candidate and exact Customer main SHA.

Extract it under:

```text
/lakehouse/default/Files/framework_cert/customer-inputs/
```

Expected layout:

```text
customer-inputs/
  INPUTS.json
  runner-config.json
  release-manifest.json
  project/
  dist/
```

The bundle owns non-secret routing/configuration:

```text
workspace/item physical bindings
representative dataset IDs
control-plane profile
Pipeline/Copy/Spark recipes
Warehouse normal/fault recipes
five-business-path plan
exact Customer extension wheel fingerprints
runtime environment-variable names
```

Do not manually edit the exact retained bundle to swap GUIDs or hashes.

## 6. Runtime values are explicit and shared consistently

The source-controlled Customer bundle stores variable **names**, never secret values.

Reference names:

```text
FABRIC_ACCESS_TOKEN
CONTROL_PLANE_DATABASE_URL
WAREHOUSE_DATABASE_URL
WAREHOUSE_ADMIN_DATABASE_URL   # only when separately required/approved
```

For full certification, prefer an explicit runtime mapping from your organization-approved secret mechanism:

```python
runtime_environment = {
    "CONTROL_PLANE_DATABASE_URL": control_plane_database_url,
    "WAREHOUSE_DATABASE_URL": warehouse_database_url,
}
```

Do not paste real connection strings into this repo or retained evidence.

The Framework one-call API temporarily mirrors only exact runner-declared runtime names into process environment while the certification call runs. This allows approved Framework runners and exact Customer/domain extension entry points to consume one consistent runtime, and the previous process environment is restored when the call returns.

Current business-path driver/observer use the same exact:

```text
WAREHOUSE_DATABASE_URL
```

There is no separate JSON-wrapped business-path database-secret channel to configure.

Fabric REST authentication may use the declared token runtime value or the current NotebookUtils Fabric/Power BI token when available.

## 7. Full ordinary live certification

Only after the dedicated DEV/UAT certification resources and ordinary certification mutations are approved:

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

## 8. First-time dedicated Fabric SQL Control Plane

A brand-new certification SQL Database needs both:

```text
current Framework Control Plane schema
exact Customer semantic DatasetConfig definitions
```

A schema-only database is not enough for Pipeline/Warehouse because `SqlAlchemyControlPlaneRepository` verifies the deployed exact config hash.

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

If bounded checks fail, SQL bootstrap is not attempted.

Normal reruns use:

```text
allow_control_plane_migration=False
```

Never enable first-time bootstrap against a shared/production SQL Control Plane just to make certification green.

## 9. Seven Control Plane external-evidence references remain real governance

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

The public Customer repo may retain only stable non-secret references to real internal evidence/review records.

Fail-closed blocker semantics remain:

```text
control_plane_external_evidence_incomplete
control_plane_external_evidence_not_review_bound
```

Successful SQL connectivity is not a substitute for either.

## 10. Warehouse ambiguous COMMIT remains separately governed

A real fault drill requires a reviewed reachable real fault controller from exact Customer inputs.

Until configured:

```text
warehouse_real_fault_controller_not_configured
```

remains a real blocker.

`allow_live_mutations=True` does not imply Admin/session-control permission.

Only if company governance explicitly authorizes exact-session termination against the isolated certification Warehouse:

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

## 11. Unified status semantics

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

## 12. Customer production pin boundary

Until immutable Framework `v0.4.0` is actually published and governance permits migration, keep exactly:

```text
fabric-data-framework==0.3.0
```

Candidate compatibility/certification source may be 0.4 while the production dependency remains 0.3.0. Do not conflate these lanes.

## 13. Historical first company run — old bytes only

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

That evidence remains valid for those exact old bytes only. It cannot be copied onto a current Framework main wheel.

## 14. Manual cells/form are fallback diagnostics

Older explicit diagnostic paths remain useful for isolating failures:

```text
fabric-data-framework/docs/human/FIRST_FABRIC_NOTEBOOK_TEST.md
fabric-data-framework/docs/human/MANUAL_CERTIFICATION.md
```

The form is a result recorder, not a test executor.

## 15. New-conversation recovery

Always re-read current GitHub `main`, not chat memory:

```text
1. fabric-customer/docs/CURRENT_STATUS.md
2. fabric-customer/docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
3. fabric-customer/docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
4. fabric-customer/docs/runbooks/CONTROL_PLANE_EXTERNAL_EVIDENCE_REVIEW.md
5. fabric-data-framework/docs/machine/STATE.md
6. fabric-data-framework/docs/machine/UNIFIED_CERTIFICATION.md
7. fabric-data-framework/docs/human/ONE_CALL_CERTIFICATION_RUNTIME.md
8. fabric-data-framework/docs/human/FABRIC_PIPELINE_CHILD_CONTRACT.md
```

Then verify:

```text
current Framework substantive main SHA / independent main CI
current exact Framework wheel SHA256
current Customer main SHA / independent CI
candidate_status = not_frozen unless explicit governance changed it
release_allowed = false unless explicit release governance changed it
Customer production pin
control-plane external-evidence blockers
Warehouse fault-controller blocker
```

If Framework source changed after the last real-Fabric run, obtain a new exact successful-main artifact before continuing testing.
