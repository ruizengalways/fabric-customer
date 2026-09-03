# Current Status — fabric-customer

Last updated: 2026-09-03

## New-conversation recovery checkpoint

Start here when resuming this project. `main` is truth.

The **first bounded company-Fabric Notebook test has now been executed successfully and recorded**. Do not inflate that bounded result into full release evidence, do not freeze the already-tested PR #99 Framework artifact merely because it passed, and do not release Framework 0.4 yet.

The next release-oriented work is to close the real evidence prerequisites: reviewed/bound control-plane evidence plus an explicitly approved reachable Warehouse ambiguous-COMMIT fault controller. Only after those prerequisites are genuinely ready should a **NEW exact Framework candidate** be explicitly selected/frozen for the strict evidence-based release lane.

Read in this order:

```text
1. fabric-customer/docs/CURRENT_STATUS.md
2. fabric-customer/docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
3. fabric-data-framework/docs/machine/STATE.md
4. fabric-data-framework/docs/machine/FIRST_COMPANY_FABRIC_TEST_2026-09-03.md
5. fabric-data-framework/docs/human/FIRST_FABRIC_NOTEBOOK_TEST.md
6. fabric-data-framework/docs/human/MANUAL_CERTIFICATION.md
```

The certification form is a **result recorder**. It does not execute the tests.

## Current cross-repo baselines

### Framework substantive code baseline

```text
Framework PR #99
  purpose                      first company-Fabric Notebook hardening + executable test runbook
  merge SHA                    303683729c4915d78200d463a6def01c8de9eae6
  final PR CI                  33381590800 SUCCESS
  main CI                      33381666892 SUCCESS
  tests                        753 passed on Python 3.11 main lane
  candidate frozen             false

Framework machine-state checkpoint PR #100
  merge SHA                    2f7535eae86b0ed7b3ba104bad5e9352a598cab0
  PR CI                        33381983754 SUCCESS
  main CI                      33382034631 SUCCESS
```

PR #99 remains the current substantive Framework code baseline. PR #97 remains the original Notebook/manual certification + GitHub Admin Override feature milestone. PR #100 is the prior documentation/machine-state checkpoint and did not select a release candidate.

### Exact Framework artifact that was tested

The first company test used **this PR #99 main artifact**, not the older PR #97 wheel and not a later documentation-only wheel:

```text
framework-ci main run          33381666892
candidate Git SHA              303683729c4915d78200d463a6def01c8de9eae6
artifact name                  framework-wheel-303683729c4915d78200d463a6def01c8de9eae6
artifact ID                    9753976212
wheel filename                 fabric_data_framework-0.4.0-py3-none-any.whl
wheel inner SHA256             0638c95c19ebcc43ec4ec462b7f960a164209874223517e3f74b951264b0eaf6
artifact ZIP digest            sha256:cd790310378d8aa11e950b004c9183125c52bbbc0ddf484d7749faa675e7171b
artifact expires               2026-11-29T10:16:35Z
```

The artifact contains:

```text
fabric_data_framework-0.4.0-py3-none-any.whl
CANDIDATE.json
SHA256SUMS
```

All three were kept together. The Notebook verified the actual wheel bytes, installed Framework version, exact candidate Git SHA and workflow run ID before semantic testing.

This artifact remains **candidate-capable only**. Testing it did not select/freeze it.

### First bounded company-Fabric result — 2026-09-03

Detailed Framework checkpoint:

```text
fabric-data-framework/docs/machine/FIRST_COMPANY_FABRIC_TEST_2026-09-03.md
```

Actual result:

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

The forced reconciliation test correctly returned underlying `FAIL` plus `blocks_state_advance=true`; therefore the certification check `reconciliation.fail_closed` is PASS.

A dedicated test Warehouse exists in the DEV workspace, but session termination/fault-injection authorization was not confirmed and the full approved Warehouse runner prerequisites were not assembled for this bounded lane. Both Warehouse checks therefore remain `NOT_RUN`, not synthetic PASS.

The generated manual record reported `environment=DEV`, `missing_fields=['notebook_reference']`, `admin_override=false`, and `release_authorized=false`. A final sanity inspection found `operator`, `notebook_reference`, `notes`, and `override_reason` null/empty and no secret-bearing material. The raw JSON remains in the company Fabric DEV environment; the public repos retain only the non-secret summary.

### Customer current recovery/test-readiness baseline

```text
Customer PR #17
  purpose                      make first company-Fabric test fully recoverable from main docs
  merge SHA                    0e128380e6b4ed54d4f192e0676da397177f6e2f
  final PR customer-ci         33382409587 SUCCESS
  final PR certification CI    33382409601 SUCCESS
  main customer-ci             33382529532 SUCCESS
  main certification-contract  33382529539 SUCCESS

Customer docs checkpoint PR #18
  merge SHA                    5e6007f1e62a04644d31f89ecbd15419b1cc4a81

previous Customer PR #16       0c6cb0afd662f61082b41d34ef245ec2b055c97d
production Framework dependency fabric-data-framework==0.3.0
bounded company-Fabric test summary retained yes
raw manual-certification JSON in repo       no
```

The Customer production dependency must remain exactly `fabric-data-framework==0.3.0` until immutable Framework v0.4.0 is actually published and release governance permits migration.

## Current release truth

```text
Framework public release                     v0.3.0
Framework 0.4 source                         feature-frozen / unreleased
Framework release_allowed                    false
Framework exact candidate                    not frozen
Framework ordinary readiness blockers        15
first company-Fabric test runbook             implemented
first company-Fabric test executed            yes — bounded PASS/NOT_RUN result
manual Notebook certification                 CERTIFIED
manual Admin Override                         not used
manual release authorization                  false
raw manual certification JSON in repo         no
selected-candidate Customer input artifact    not retained
certified integration evidence                not produced
five live business-path proofs                not retained
immutable Framework v0.4.0                    not published
Customer production pin                       fabric-data-framework==0.3.0
```

A real bounded Fabric DEV test has now been executed for the exact PR #99 wheel. No candidate was frozen. No Admin Override has been executed. No current claim is full evidence-based `PRODUCTION DB PROVEN`, `FABRIC WAREHOUSE PROVEN`, or `RELEASE PROVEN`.

## Documentation/test-readiness gaps closed before testing

The pre-test audit found three practical gaps:

```text
1. MANUAL_CERTIFICATION described recording a decision but not how to execute each first test.
2. the old Notebook UI used PASS-only checkboxes, so a real FAIL could disappear as an unchecked/absent item.
3. the old UI used ipywidgets.Output, which Microsoft Fabric documents as unsupported.
```

Framework PR #99 closed them:

```text
Notebook result controls      NOT RUN / PASS / FAIL dropdowns
callback result display       supported disabled Textarea, not Output
form responsibility           result recorder only; it does not execute tests
executable test runbook       docs/human/FIRST_FABRIC_NOTEBOOK_TEST.md
known FAIL under override     remains explicitly retained as FAIL
```

The bounded runbook executed:

```text
exact wheel/CANDIDATE identity verification
Lakehouse write/read smoke
FULL -> REPLACE + destructive incomplete-snapshot guard
WATERMARK -> SCD1
WATERMARK -> SCD2
retry / idempotency
reconciliation fail-closed
manual-certification.json generation
```

The privileged checks remained honestly unexecuted:

```text
warehouse.commit = NOT_RUN
warehouse.ambiguous_commit = NOT_RUN
```

No synthetic Warehouse PASS was created merely to fill the form.

## Two certification lanes remain separate

### Lane A — bounded company Fabric Notebook/manual validation — COMPLETED 2026-09-03

```text
successful Framework main CI artifact
  -> isolated company Fabric DEV workspace
  -> exact wheel + CANDIDATE.json + SHA256SUMS
  -> attached disposable/default Lakehouse
  -> bounded real tests PASS
  -> Warehouse privileged checks NOT_RUN
  -> normal Notebook manual record CERTIFIED
  -> admin_override=false
  -> release_authorized=false
```

No candidate freeze is required for this bounded pre-freeze compatibility/smoke test.

Admin Override was not needed. The missing `notebook_reference` remained explicit and did not justify manufacturing evidence or release authorization.

The GitHub-side `.github/workflows/candidate-admin-certification.yml` remains available but was not used for this bounded execution. It does not connect to corporate Fabric. For the tested artifact, `candidate_run_id=33381666892` remains the exact GitHub identity anchor.

### Lane B — full automated evidence-based Framework release — NEXT RELEASE-ORIENTED WORK

```text
reviewed real control-plane evidence + exact binding
  -> approved reachable Warehouse/session fault controller
  -> explicitly freeze/select one NEW exact Framework candidate
  -> Customer exact certification inputs
  -> candidate-integration-evidence
  -> candidate-business-path-evidence
  -> candidate-release-proofs
  -> candidate-certification
  -> blockers=[] / release_ready=true
  -> framework-release exact already-certified bytes
```

The existing strict `release.yml` does **not** accept the bounded Notebook/manual record as a substitute for this retained evidence chain.

Do not freeze the already-tested PR #99 artifact simply because its bounded test passed. The strict lane should start with a NEW exact candidate only after the real environment prerequisites are ready.

## Current Customer evidence-based prerequisites

Customer PR #14 hardened the control-plane prerequisite. Seven arbitrary non-empty strings are not enough; a real external evidence set must eventually be review-bound to the exact protected environment/profile.

Current source intentionally remains incomplete:

```text
control-plane external evidence              incomplete/null
control-plane review binding                 incomplete/null
Warehouse fault controller                   example.invalid placeholder
```

Therefore current exact builder truth remains:

```text
live_prerequisites_configured=false
live_prerequisite_blockers=
  control_plane_external_evidence_incomplete
  warehouse_real_fault_controller_not_configured
```

If all seven real control-plane evidence references later exist but the exact review binding is absent/mismatched, the fail-closed transition is:

```text
control_plane_external_evidence_not_review_bound
```

The bounded manual test does not rewrite these evidence-based prerequisites.

## Compatibility / recovery anchors retained by CI

These older anchors are intentionally retained because Customer CI uses them to prevent new-conversation context from silently regressing:

```text
100-table enterprise onboarding reference  retained
project CLI contracts                      project-init / project-validate
capture reference                          includes Debezium
historical framework-next project SHA      148e02e3fff7861f238296e7554815a6fd49dd0a
Framework documentation checkpoint PR #95  4006afb409c81c5510690c8c4dbeadd5e002fd0b

Customer candidate-input producer           MERGED + MAIN CI PROVEN — PR #10
PR #10 merge SHA                            cda90f1c02fc9606aa64d2d1bd13f2ab89628aab

Customer certification alignment            MERGED + MAIN CI PROVEN — PR #12
PR #12 merge SHA                            9ddc11405de329fb647fb21b1217d1015e0fa3f5
PR #12 customer-ci                          33363980824 SUCCESS
PR #12 certification-contract               33363980826 SUCCESS
PR #12 main customer-ci                     33364050484 SUCCESS
PR #12 main certification-contract          33364050481 SUCCESS
released v0.3 tests                         14 passed
certification Framework SHA                 abc8b3a2b80b3f6babf88fdc2347a3bfe69be356
candidate frozen             false
selected-candidate Customer input artifact   not retained
```

`abc8b3a2...` remains the exact historical Framework source used by the Customer portable certification-contract lane. It must not be confused with current substantive Framework PR #99 source `303683729...` used for the bounded company test.

## Exact next operating sequence

```text
1. treat the 2026-09-03 bounded Notebook result as completed and keep its evidence class bounded
2. keep Framework release_allowed=false and candidate_status=not_frozen
3. keep Customer production dependency exactly fabric-data-framework==0.3.0
4. obtain the seven real control-plane evidence references for the intended protected environment/profile
5. create/review the exact source-controlled control-plane evidence binding
6. obtain explicit approval and a reachable real Warehouse/session ambiguous-COMMIT fault controller
7. verify BOTH prerequisite families are genuinely ready before any candidate freeze
8. build a NEW Framework main artifact after the documentation/prerequisite work and explicitly select/freeze that exact candidate
9. produce Customer candidate inputs for that exact candidate and exact Customer SHA
10. run candidate-integration-evidence
11. run all five candidate-business-path-evidence drills
12. run candidate-release-proofs
13. candidate-certification must reach blockers=[] and release_ready=true
14. framework-release must promote the exact already-certified bytes with no rebuild
15. only after immutable Framework v0.4.0 exists may Customer production migration from v0.3.0 be considered
```

Do not rerun or freeze the old PR #99 artifact by default. It served its purpose as the first pre-freeze company compatibility/smoke artifact.

## After the first test

The bounded test result has been recorded in canonical recovery docs. Any future rerun against changed Framework bytes must use a new exact artifact identity; results from `303683729...` cannot be reused to certify different wheel bytes.

If a later real bounded or strict-lane test fails, retain which check failed, fix/retest, and do not use Admin Override merely to conceal a known Framework defect.

## Evidence vocabulary boundary

Green CI, a candidate-capable wheel, successful package installation, a Notebook dropdown, an administrator decision, or a source-controlled reference is not proof for a check that did not run.

The 2026-09-03 manual lane legitimately says `CERTIFIED` for the exact bounded checks that were actually executed with exact candidate identity and no Admin Override. Keep that provenance distinct from evidence-based `PRODUCTION DB PROVEN`, `FABRIC WAREHOUSE PROVEN`, and `RELEASE PROVEN`.