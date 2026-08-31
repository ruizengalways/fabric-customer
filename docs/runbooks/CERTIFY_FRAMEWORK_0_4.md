# Runbook — Framework 0.4 Certification from fabric-customer

Status: bounded company-Fabric test path ready; full evidence-based release prerequisites intentionally incomplete

Last updated: 2026-08-31

This runbook explains the **two different certification lanes** now supported by the project. Do not confuse the bounded company-Fabric Notebook test with the full release-evidence chain.

Customer production runtime remains exactly:

```text
fabric-data-framework==0.3.0
```

until immutable Framework v0.4.0 is actually published and release governance permits migration.

## 1. Current Framework identities

Current substantive Framework source baseline:

```text
PR #99 merge SHA        303683729c4915d78200d463a6def01c8de9eae6
PR #99 PR CI            33381590800 SUCCESS
PR #99 main CI          33381666892 SUCCESS
Python 3.11 tests       753 passed
```

The exact candidate-capable artifact recommended for the **first bounded company test** is:

```text
main run                33381666892
artifact ID             9753976212
wheel                    fabric_data_framework-0.4.0-py3-none-any.whl
wheel SHA256             0638c95c19ebcc43ec4ec462b7f960a164209874223517e3f74b951264b0eaf6
candidate Git SHA        303683729c4915d78200d463a6def01c8de9eae6
```

The Customer `.github/workflows/certification-contract.yml` still installs exact historical Framework source:

```text
abc8b3a2b80b3f6babf88fdc2347a3bfe69be356
```

That SHA is the **Customer certification-contract compatibility baseline**, not the current Framework main code baseline. It remains pinned so the Customer portable contract lane has a stable exact source identity while the 0.4 development branch continues to evolve.

## 2. Choose the correct lane

### Lane A — bounded company-Fabric Notebook validation

Use now when GitHub cannot or should not authenticate into the corporate Fabric tenant.

Canonical Customer wrapper:

```text
docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
```

Canonical Framework executable runbook:

```text
fabric-data-framework/docs/human/FIRST_FABRIC_NOTEBOOK_TEST.md
```

This lane executes real bounded checks in an isolated DEV workspace, then records observed `PASS / FAIL / NOT RUN` values in `manual-certification.json`.

No candidate freeze is required for this pre-freeze compatibility/smoke test.

### Lane B — full evidence-based release certification

Use later when the protected real environment and all enterprise prerequisites exist.

```text
exact frozen candidate
  -> exact Customer certification inputs
  -> candidate-integration-evidence
  -> candidate-business-path-evidence
  -> candidate-release-proofs
  -> candidate-certification blockers=[] / release_ready=true
  -> framework-release exact already-certified bytes
```

This remains the only lane consumed by the current strict Framework `release.yml`.

## 3. Lane A — what to test first

The bounded company-Fabric test should cover:

```text
exact wheel/CANDIDATE identity verification
Lakehouse write/read smoke
FULL -> REPLACE + destructive guard
WATERMARK -> SCD1
WATERMARK -> SCD2
retry / idempotency
reconciliation fail-closed
manual-certification.json generation
```

If Warehouse resources/permissions are not genuinely available, retain:

```text
warehouse.commit = NOT_RUN
warehouse.ambiguous_commit = NOT_RUN
```

Do not create synthetic PASS evidence.

Framework PR #99 hardened the Notebook form so it uses Fabric-compatible widgets and explicit Dropdown values:

```text
NOT RUN
PASS
FAIL
```

The form **records** observations. It does not execute the underlying test.

Admin Override may accept missing/unavailable/export-restricted coverage, but an executed FAIL remains explicitly retained. The normal policy is to investigate a known functional failure rather than use override to conceal it.

## 4. Lane A — exact artifact transport

Download from Framework main CI run `33381666892`:

```text
framework-wheel-303683729c4915d78200d463a6def01c8de9eae6
```

Keep together:

```text
fabric_data_framework-0.4.0-py3-none-any.whl
CANDIDATE.json
SHA256SUMS
```

`CANDIDATE.json` allows Framework to auto-resolve:

```text
framework_version
candidate_git_sha
wheel SHA256
```

so the corporate operator does not need to retype long hashes.

The Notebook test should additionally hash the actual wheel bytes and assert they match `CANDIDATE.json` before semantic testing.

## 5. Lane A — Admin Override / GitHub admin record

The Notebook form may create:

```text
status = CERTIFIED
admin_override = true
override_reason = required
missing_fields = retained
```

This is an explicit governance decision. It does not manufacture unexecuted evidence.

The Framework also has:

```text
.github/workflows/candidate-admin-certification.yml
```

It does not authenticate to corporate Fabric. If a GitHub-side exact administrator record is wanted, supply:

```text
candidate_run_id = 33381666892
override_reason
confirm_admin_override = true
```

GitHub independently resolves/verifies the exact candidate identity from its own artifact.

The current Framework release workflow does not consume this manual/admin record as a substitute for full evidence-based readiness.

## 6. Lane B — Customer-owned exact certification input slice

For the full release lane, Customer owns:

```text
certification/project/config/datasets/
certification/project/config/certification/integration/
certification/project/config/certification/business/
certification/extensions/
```

It represents:

```text
FULL -> REPLACE
WATERMARK -> SCD1
WATERMARK -> SCD2
retry/idempotency
reconciliation fail-closed
Fabric Copy capture
Fabric Spark capture
Warehouse commit/recovery
Warehouse ambiguous-COMMIT fault drill
```

The normal CRM/domain project remains separate.

Customer code supplies bounded facts or controlled mutations only. Framework remains the sole PASS authority in the evidence-based release lane.

## 7. Lane B — current intentional blockers

Current source deliberately contains incomplete real-enterprise prerequisites:

```text
control-plane-external-evidence.json
  reviewed enterprise evidence references = null/incomplete

control-plane-external-evidence-review.json
  exact review binding = null/incomplete

warehouse-fault-run.json
  controller_url = example.invalid placeholder
```

Therefore the typed builder must report:

```text
live_prerequisites_configured=false
live_prerequisite_blockers=
  control_plane_external_evidence_incomplete
  warehouse_real_fault_controller_not_configured
```

If all seven real control-plane evidence references later exist but exact environment/profile review binding is absent or mismatched:

```text
control_plane_external_evidence_not_review_bound
```

Do not remove these blockers merely to make CI green.

## 8. Lane B — real environment preparation

Before selecting/freeze of a release candidate, platform/data engineering must have an isolated protected certification environment with the required real resources, including as applicable:

```text
[ ] Fabric workspace
[ ] read-only smoke item
[ ] certification Fabric Data Pipeline
[ ] certification Fabric Copy Job
[ ] certification Spark Job Definition
[ ] production-eligible control-plane SQL database
[ ] Fabric Warehouse target
[ ] framework Warehouse marker table
[ ] bounded certification source/target/control tables
[ ] bounded Copy/Spark landing area
[ ] approved real ambiguous-COMMIT fault controller
```

The Customer input producer does not create these resources.

Passwords, tokens and connection strings remain runtime secrets and must not be committed into source-controlled evidence metadata or Customer input artifacts.

## 9. Lane B — control-plane evidence review

Seven arbitrary non-empty strings are not sufficient.

The real evidence set must be bound using the source-controlled credential-free review record to the exact:

```text
environment
control_plane_profile
review_record_reference
evidence_set_reference
reviewed_at_utc
```

Before merge, reviewers must be able to identify which production-eligible database/profile is being certified and which retained enterprise review accepted it.

## 10. Lane B — Warehouse fault controller

The endpoint must refer to a real approved service capable of inducing/coordinating the required provider/session ambiguous-COMMIT condition against the exact isolated Warehouse/session under test.

Before use, verify:

```text
endpoint is real and reachable from the protected runner
fault action is bounded to the intended Warehouse/session
authorization is separate from normal mutation authorization
session termination/fault action is auditable
controller does not return a synthetic PASS decision
```

Framework interprets the resulting provider/runtime evidence.

## 11. Lane B — candidate freeze only after prerequisites

Do **not** freeze a Framework candidate merely because main CI produced a wheel or because the bounded Lane A test passed.

Once both real external blockers are resolved and the protected environment is ready, explicitly select one **new exact Framework main candidate** and record:

```text
candidate main CI run ID
candidate source SHA
exact inner candidate wheel SHA256
```

Any Framework code change after selection creates a different candidate and invalidates reuse of exact-candidate evidence.

## 12. Lane B — produce exact Customer input artifact

With the exact candidate selected, manually run:

```text
.github/workflows/candidate-business-path-inputs.yml
```

Inputs include:

```text
candidate_run_id
candidate_git_sha
candidate_wheel_sha256
environment
workspace_id
item_read_id
pipeline_item_id
copy_job_id
spark_job_id
control_plane_profile
```

The workflow validates Framework producer provenance and exact wheel bytes before installing them, then fingerprints the Customer extension/configuration bundle.

Successful packaging uploads:

```text
business-path-inputs-<customer SHA>
```

with typed input/config/release-manifest material. This is an **input package**, not evidence that provider checks passed.

## 13. Lane B — live Framework consumers

The same exact Customer artifact is consumed by:

```text
candidate-integration-evidence.yml
candidate-business-path-evidence.yml
```

The integration workflow performs the approved real Fabric/control-plane/Warehouse checks. The business-path workflow requires certified integration evidence and executes the five representative semantic drills:

```text
full.replace
watermark.scd1
watermark.scd2
retry.idempotency
reconciliation.fail_closed
```

Customer driver/observer code never authors PASS. Framework evaluators determine readiness from retained execution/provider/state evidence.

## 14. Fail-closed semantics

Expected failures include:

```text
candidate wheel hash mismatch          -> fail
Customer commit not on main            -> fail
scenario/driver/extension hash mismatch -> fail
control-plane evidence incomplete      -> release lane blocked
review binding missing/mismatched      -> release lane blocked
fault controller example.invalid       -> Warehouse drill blocked
provider Completed but Framework FAIL  -> no semantic success upgrade
cleanup failure                         -> no business-path PASS artifact
Framework/domain release hash mismatch -> proof/certification rejected
```

Never replace a missing real prerequisite with synthetic PASS JSON.

## 15. Current exact truth

```text
Customer production runtime                     fabric-data-framework==0.3.0
current Framework substantive code baseline     PR #99 / 303683729c4915d78200d463a6def01c8de9eae6
first bounded company test artifact             main run 33381666892 / artifact 9753976212
first bounded company test executed             no
manual/admin certification record retained      no
Customer certification-contract Framework SHA   abc8b3a2b80b3f6babf88fdc2347a3bfe69be356
real control-plane evidence                      missing
review-bound control-plane evidence              missing
real Warehouse fault controller                  missing
selected/frozen Framework candidate              none
selected-candidate Customer input artifact       none retained
certified integration evidence                   none retained
five-gate live business proof                    none retained
immutable Framework v0.4.0                       not published
```

## 16. What to do next

For the current corporate-account situation, go to:

```text
docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
```

Do not start the full Lane B sequence yet. The bounded company-Fabric Notebook test is the next honest step.