# Runbook — Test Framework in Company Fabric

Status: unified real-Fabric certification is the default path; the original 2026-09-03 bounded test remains historical evidence for its exact old wheel only.

Last updated: 2026-09-03

This is the Customer-side operator entrypoint for testing an exact Framework candidate in company Fabric. New candidates should **not** require an engineer to copy many notebook cells or manually fill PASS/FAIL dropdowns.

The Framework package now owns one unified execution surface:

```text
fabric-data-framework/docs/human/UNIFIED_FABRIC_CERTIFICATION.md
```

## 1. CI versus real Fabric

Both are required, but they prove different things.

PR/main CI proves deterministic Framework and Customer contracts: algorithms, recovery state machines, configuration validation, package boundaries, failure cases and build integrity.

Real Fabric certification proves the exact built wheel against the actual tenant/resources:

```text
exact wheel bytes/install
Lakehouse Delta behavior
Fabric item authorization
Fabric SQL Control Plane behavior
Pipeline/Copy/Spark provider execution
Warehouse commit/recovery behavior
five representative live business paths
```

Do not run the entire pytest suite inside Fabric merely to duplicate CI.

## 2. Conventional Lakehouse layout

Use an isolated/approved certification workspace, normally DEV first.

Create/use:

```text
Files/framework_cert/
```

The attached default Lakehouse should expose:

```text
/lakehouse/default/Files/framework_cert/
```

Place the exact Framework main-CI artifact contents there:

```text
CANDIDATE.json
SHA256SUMS
fabric_data_framework-<version>-py3-none-any.whl
```

Keep exactly one Framework wheel in this directory. If Framework source changes, replace the old artifact with a new successful `main` artifact; old real-Fabric PASS values belong only to old bytes.

## 3. Bounded certification — minimum input

Install the exact Framework wheel, then run one cell:

```python
from fabric_data_framework.certification import certify, print_certification_summary

report = certify(spark=spark)
print_certification_summary(report)
```

This automatically runs:

```text
exact candidate identity / wheel hash
Lakehouse write/read
FULL -> REPLACE + incomplete-FULL destructive guard
WATERMARK -> SCD1
WATERMARK -> SCD2
retry/idempotency
reconciliation fail-closed
```

It writes the retained report under:

```text
Files/framework_cert/certification-output/
```

No manual certification form is required for the normal unified path.

## 4. Exact Customer input bundle — do not retype IDs in Notebook

The strict environment stages require the exact Customer candidate-input artifact produced for the same Framework candidate.

Extract that artifact under:

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

The bundle already owns the non-secret environment configuration required by the approved runners:

```text
workspace/item physical bindings
representative dataset IDs
control-plane profile
Pipeline/Copy/Spark recipes
Warehouse normal/fault recipes
five-business-path plan
exact Customer extension wheel fingerprints
```

Therefore the Fabric operator should not repeatedly type Lakehouse/SQL/Pipeline/Warehouse GUIDs into test cells.

The unified runner verifies Customer candidate SHA/wheel/version binding before using the bundle.

## 5. Runtime secrets stay runtime-only

The source-controlled Customer files contain secret **environment-variable names**, not secret values.

Typical protected runtime values are:

```text
CONTROL_PLANE_DATABASE_URL
WAREHOUSE_DATABASE_URL
WAREHOUSE_ADMIN_DATABASE_URL   # only when exact-session Admin control is needed
```

Fabric REST authentication may use the configured runtime token or, in a Fabric Notebook, the current NotebookUtils Fabric/Power BI token when available.

Never put connection strings, bearer tokens, passwords, signed URLs or access keys into GitHub evidence-reference JSON or certification output.

## 6. Full ordinary live certification

Only when the dedicated DEV/UAT certification resources and ordinary certification mutations are approved, run:

```python
from fabric_data_framework.certification import certify, print_certification_summary

report = certify(
    spark=spark,
    allow_live_mutations=True,
)
print_certification_summary(report)
```

The runner attempts the fullest safe sequence automatically:

```text
bounded suite
-> Fabric item read
-> real Control Plane reference conformance
-> approved production Control Plane certification
-> Pipeline
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

The package reuses existing approved runners; the Notebook is only the orchestration entrypoint.

## 7. New Fabric SQL Control Plane

For Framework 0.4 company testing, the selected profile may be:

```text
fabric_sql_database_v1
```

A newly provisioned dedicated certification Control Plane requires an explicit schema bootstrap decision. Only for that initial approved setup:

```python
report = certify(
    spark=spark,
    allow_live_mutations=True,
    allow_control_plane_migration=True,
)
```

Normal reruns should leave migration disabled. Production certification must not silently migrate a database just to make schema checks pass.

## 8. Seven Control Plane external-evidence references remain real governance

The unified runner does not eliminate the enterprise evidence requirement. The exact Customer inputs still require these seven reviewed references before approved production Control Plane certification can PASS:

```text
backend_service_identity_reference
identity_access_control_reference
network_security_reference
backup_restore_reference
availability_recovery_reference
monitoring_alerting_reference
retention_governance_reference
```

The public Customer repo stores only stable, non-secret references to real internal evidence/review records. Do not commit internal credentials or secret URLs.

Current fail-closed blockers remain meaningful:

```text
control_plane_external_evidence_incomplete
control_plane_external_evidence_not_review_bound
```

Successful SQL connectivity cannot turn either blocker into PASS.

## 9. Warehouse ambiguous COMMIT remains governed

A real Warehouse fault drill requires the reviewed real fault controller configured by the exact Customer input bundle.

If it is not configured, the unified report must surface:

```text
warehouse_real_fault_controller_not_configured
```

and the fault stage remains blocked/not-run.

`allow_live_mutations=True` does not imply permission to perform Admin-level exact-session termination.

Only if company governance separately approves exact-session termination for the isolated certification Warehouse:

```python
report = certify(
    spark=spark,
    allow_live_mutations=True,
    allow_warehouse_session_termination=True,
)
```

Never use session termination or fault injection against a shared/production Warehouse merely to complete certification.

## 10. Unified status semantics

The report uses:

```text
PASS      the actual stage ran and passed
FAIL      the actual stage ran and failed
NOT_RUN   the stage intentionally did not run
BLOCKED   a required external/configuration prerequisite is not ready
```

A real FAIL must be investigated/fixed. Missing permissions/evidence do not become synthetic PASS.

The unified report always has:

```text
release_authorized = false
```

Running certification does not freeze/select a candidate and does not publish Framework 0.4.

## 11. Customer production pin boundary

Candidate testing never changes the released Customer runtime dependency.

Until immutable Framework 0.4.0 is actually released and release governance explicitly permits migration, keep:

```text
fabric-data-framework==0.3.0
```

## 12. Historical first company run — old bytes only

The first bounded company-Fabric execution occurred on 2026-09-03 before the unified runner existed.

Exact historical Framework identity:

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

That run remains useful historical compatibility evidence for those exact bytes. It is **not** evidence for a newer Framework wheel containing the unified certification feature.

## 13. Manual cells and form are fallback diagnostics

The older Framework files remain available:

```text
docs/human/FIRST_FABRIC_NOTEBOOK_TEST.md
docs/human/MANUAL_CERTIFICATION.md
```

Use the explicit cells to isolate a failing unified check or validate an old wheel. Use the manual/Admin-Override lane only when policy specifically requires that governance record.

Do not make the manual form the normal test executor; it only records operator-observed results.

## 14. Recovery sequence for a new chat

Read current GitHub `main`, not chat memory, in this order:

```text
fabric-customer/docs/CURRENT_STATUS.md
fabric-customer/docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
fabric-customer/docs/runbooks/CONTROL_PLANE_EXTERNAL_EVIDENCE_REVIEW.md
fabric-data-framework/docs/machine/STATE.md
fabric-data-framework/docs/machine/UNIFIED_CERTIFICATION.md
fabric-data-framework/docs/human/UNIFIED_FABRIC_CERTIFICATION.md
```

Then verify:

```text
current Framework main SHA / CI
current Customer main SHA / CI
candidate_status
release_allowed
Customer production dependency pin
control-plane external evidence blockers
Warehouse fault-controller blocker
```

If Framework code changed after the last real-Fabric run, generate/download a new exact main artifact before continuing testing.
