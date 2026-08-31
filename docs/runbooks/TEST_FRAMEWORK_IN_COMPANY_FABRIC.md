# Runbook — Test Framework 0.4 in Company Fabric

Status: ready for the first bounded real-company Fabric validation

Last updated: 2026-08-31

This is the Customer-side entrypoint for the first company-Fabric test. It intentionally keeps the test bounded so it can be run in an isolated DEV workspace without requiring GitHub-to-Fabric authentication or privileged Warehouse fault injection.

The detailed executable Notebook cells live in the Framework runbook:

```text
fabric-data-framework/docs/human/FIRST_FABRIC_NOTEBOOK_TEST.md
```

Use this wrapper to recover the exact artifact and project state before following those cells.

## 1. Exact package to test

Download from `ruizengalways/fabric-data-framework`:

```text
Actions -> framework-ci -> run 33381666892
artifact name   framework-wheel-303683729c4915d78200d463a6def01c8de9eae6
artifact ID     9753976212
```

Expected exact identity:

```text
Framework main SHA     303683729c4915d78200d463a6def01c8de9eae6
wheel                   fabric_data_framework-0.4.0-py3-none-any.whl
wheel SHA256            0638c95c19ebcc43ec4ec462b7f960a164209874223517e3f74b951264b0eaf6
```

The downloaded artifact must contain:

```text
fabric_data_framework-0.4.0-py3-none-any.whl
CANDIDATE.json
SHA256SUMS
```

Keep these three files together.

This package is **candidate-capable, not frozen**. Testing it does not authorize release.

## 2. Corporate Fabric setup

Use only an isolated/approved DEV workspace for the first run.

Prepare:

```text
[ ] Fabric DEV workspace you are permitted to use
[ ] Notebook
[ ] disposable/default Lakehouse attached to the Notebook
[ ] permission to upload three files under Files/framework_cert/
[ ] permission to create/read/delete small test Delta data under that area
```

Do not use production business data.

## 3. Upload package

Upload all three files into:

```text
Files/framework_cert/
```

With the default Lakehouse attached, the normal Notebook file API paths are:

```text
/lakehouse/default/Files/framework_cert/fabric_data_framework-0.4.0-py3-none-any.whl
/lakehouse/default/Files/framework_cert/CANDIDATE.json
/lakehouse/default/Files/framework_cert/SHA256SUMS
```

If your tenant shows a different file path, use the exact local path Fabric exposes and verify it exists before installing.

## 4. Install exact wheel

Notebook cell:

```text
%pip install /lakehouse/default/Files/framework_cert/fabric_data_framework-0.4.0-py3-none-any.whl
```

If Fabric requires a restart after inline installation:

```python
notebookutils.session.restartPython()
```

Then rerun your path-variable cell because Python variables are cleared by restart.

If outbound package access is blocked and a dependency is missing, do not weaken corporate network policy. Prepare dependency wheels externally for the matching Fabric Python runtime, upload them as approved local libraries, and install locally.

## 5. Verify package identity first

Before any semantic test, run the identity-verification cell from Framework `FIRST_FABRIC_NOTEBOOK_TEST.md`.

It must prove:

```text
actual wheel bytes SHA256 == CANDIDATE.json wheel_sha256
installed fabric-data-framework version == CANDIDATE.json framework_version
```

Expected values for this first run:

```text
candidate_git_sha = 303683729c4915d78200d463a6def01c8de9eae6
wheel_sha256      = 0638c95c19ebcc43ec4ec462b7f960a164209874223517e3f74b951264b0eaf6
workflow_run_id   = 33381666892
```

Do not manually type these long values into the certification UI later. Pass the actual `CANDIDATE.json` and wheel paths to Framework.

If identity verification fails, stop the test.

## 6. Run the bounded checks

Follow the Framework runbook cells in this exact order:

```text
1. Lakehouse write/read smoke
2. FULL -> REPLACE
3. WATERMARK -> SCD1
4. WATERMARK -> SCD2
5. retry / idempotency
6. reconciliation fail-closed
```

Record each actual result as PASS or FAIL.

The reconciliation test deliberately forces the underlying reconciliation result to `FAIL`; the certification check is PASS only when Framework also proves `blocks_state_advance=true`.

## 7. Warehouse boundary

Unless you genuinely have an approved isolated Warehouse and the required permissions/resources, use:

```text
warehouse.commit = NOT_RUN
warehouse.ambiguous_commit = NOT_RUN
```

Do not perform session termination, fault injection, or ambiguous-COMMIT simulation against a shared or production Warehouse merely to complete the form.

This bounded first test is still useful without those two Warehouse checks.

## 8. Create manual certification record

After running the real checks, use:

```python
from fabric_data_framework.evidence.manual_certification import (
    display_notebook_certification_form,
)

WHEEL_PATH = "/lakehouse/default/Files/framework_cert/fabric_data_framework-0.4.0-py3-none-any.whl"
CANDIDATE_PATH = "/lakehouse/default/Files/framework_cert/CANDIDATE.json"

display_notebook_certification_form(
    candidate_manifest_path=CANDIDATE_PATH,
    wheel_path=WHEEL_PATH,
    output_path="/lakehouse/default/Files/framework_cert/manual-certification.json",
)
```

The UI uses:

```text
NOT RUN / PASS / FAIL
```

for each check.

Important: these Dropdowns **record what you observed**. They do not execute the test.

Map results honestly:

```text
Lakehouse smoke                 actual PASS/FAIL
FULL -> REPLACE                 actual PASS/FAIL
WATERMARK -> SCD1              actual PASS/FAIL
WATERMARK -> SCD2              actual PASS/FAIL
Retry / idempotency            actual PASS/FAIL
Reconciliation fail-closed     actual PASS/FAIL
Warehouse commit               NOT RUN unless really tested
Ambiguous COMMIT recovery      NOT RUN unless really tested
```

## 9. Admin Override policy

Use Admin Override only as an explicit governance decision when some coverage/context cannot be obtained or exported because of corporate constraints.

Example acceptable reason:

```text
Bounded Framework validation completed in corporate Fabric DEV; Warehouse fault-injection coverage is unavailable under current permissions.
```

Do not put passwords, tokens or connection strings into the form.

A real functional FAIL remains retained as FAIL even when overall Admin Override status is CERTIFIED. The default response to a failed identity/Lakehouse/SCD/retry/reconciliation test is to stop, investigate, fix and retest.

For the first smoke test, leave:

```text
Authorize exact-candidate release = OFF
```

unless separate release governance explicitly requires otherwise. The current strict Framework release workflow does not use this manual flag as a substitute for evidence-based release readiness anyway.

## 10. Inspect generated JSON

Open:

```text
Files/framework_cert/manual-certification.json
```

Verify:

```text
[ ] candidate_git_sha matches CANDIDATE.json
[ ] artifact_sha256 matches the actual wheel
[ ] every executed check has the correct PASS/FAIL state
[ ] unexecuted privileged checks are not represented as PASS
[ ] admin_override is correct
[ ] override_reason exists when admin_override=true
[ ] missing_fields is honest
[ ] no secret material is present
```

Retain the file only if company policy permits it to be retained/exported.

## 11. Optional GitHub-side administrator record

If policy allows the short GitHub run ID / decision to be communicated but not the full corporate evidence bundle, return to Framework GitHub Actions:

```text
candidate-admin-certification
```

Use:

```text
candidate_run_id = 33381666892
override_reason  = explicit non-secret governance reason
confirm_admin_override = true
```

Optional environment/notebook reference/notes may be left blank.

GitHub independently retrieves/verifies its own exact candidate artifact. It does **not** connect into company Fabric.

## 12. Stop conditions

Stop and investigate if any of these occur:

```text
wheel SHA mismatch
installed Framework version mismatch
Lakehouse smoke cannot write/read isolated Delta data
FULL incomplete-snapshot guard fails to block
SCD1 mutation/result is incorrect
SCD2 history/current-row invariant is incorrect
idempotent retry creates a new mutation/history row
forced reconciliation does not return FAIL + blocks_state_advance=true
```

Admin Override should not be used simply to hide one of these known product failures.

## 13. Cleanup

Remove only disposable test data created under the isolated test area. Keep the exact wheel + `CANDIDATE.json` together until the decision is recorded.

Do not modify normal Customer production configuration or the production dependency pin as part of this test.

## 14. After the test

Update canonical recovery docs with the **actual** result:

```text
test executed / not executed
exact Framework run + SHA
which bounded checks PASS/FAIL/NOT_RUN
manual-certification record retained or not retained
Admin Override used or not used
```

Do not label the bounded test as full evidence-based `RELEASE PROVEN`.

The later strict release lane still requires real reviewed control-plane evidence, exact review binding, approved real Warehouse fault controller, explicit candidate freeze, retained integration/business-path/release proofs, and `candidate-certification blockers=[] / release_ready=true`.