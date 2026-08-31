# Current Status — fabric-customer

Last updated: 2026-08-31

## New-conversation recovery checkpoint

Start here when resuming this project. `main` is truth.

The **next action is now the first bounded company-Fabric Notebook test**, not more synthetic certification code and not a Framework release. Use the exact Framework PR #99 main artifact identified below and follow the Customer wrapper runbook:

```text
docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
```

That wrapper points to the canonical Framework executable runbook:

```text
fabric-data-framework/docs/human/FIRST_FABRIC_NOTEBOOK_TEST.md
```

Do not start by opening the certification form and clicking PASS. The form records results; it does not execute the tests.

## Current cross-repo baselines

### Framework current substantive baseline

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
  main CI                      33382034631
```

PR #99 supersedes PR #97 as the current substantive Framework code baseline. PR #97 remains the original Notebook/manual certification + GitHub Admin Override feature baseline.

### Exact Framework artifact for the first company test

Use **this artifact**, not the older PR #97 wheel:

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

Keep all three together. `CANDIDATE.json` lets the Notebook form auto-resolve the long Framework Git SHA and wheel SHA256 so they do not need to be manually copied from the corporate tenant.

This artifact is **candidate-capable only**. Downloading it or testing it does not select/freeze it.

### Customer current baseline

```text
Customer PR #16 merge                       0c6cb0afd662f61082b41d34ef245ec2b055c97d
Customer PR #16 final customer-ci           33378015885 SUCCESS
Customer PR #16 certification-contract      33378015947 SUCCESS
Customer main customer-ci                   33378071077 SUCCESS
Customer main certification-contract        33378071142 SUCCESS
production Framework dependency             fabric-data-framework==0.3.0
manual/company-Fabric certification retained no
```

**Do not change the production dependency.** Customer runtime remains exactly `fabric-data-framework==0.3.0` until an immutable Framework v0.4.0 is actually published and release governance permits migration.

## Current release truth

```text
Framework public release                    v0.3.0
Framework 0.4 source                         feature-frozen / unreleased
Framework release_allowed                    false
Framework exact candidate                    not frozen
Framework ordinary readiness blockers        15
first company-Fabric test runbook             implemented
first company-Fabric test executed            no
manual/admin certification record retained    no
selected-candidate Customer input artifact   not retained
certified integration evidence               not produced
five live business-path proofs               not retained
immutable Framework v0.4.0                   not published
Customer production pin                      fabric-data-framework==0.3.0
```

No live Fabric test has been claimed. No candidate was frozen. No Admin Override has been executed.

## What changed before testing — Framework PR #99

The documentation audit found two practical gaps and one Fabric compatibility bug:

```text
1. MANUAL_CERTIFICATION explained how to record a result but not how to execute each first test.
2. the old UI used PASS-only checkboxes, so a real FAIL could disappear as an unchecked/absent item.
3. the old UI used ipywidgets.Output, which Microsoft Fabric documents as unsupported.
```

PR #99 fixes them:

```text
Notebook result controls      NOT RUN / PASS / FAIL dropdowns
callback result display       supported disabled Textarea, not Output
form responsibility           result recorder only; it does not execute tests
executable test runbook       docs/human/FIRST_FABRIC_NOTEBOOK_TEST.md
known FAIL under override     remains explicitly retained as FAIL
```

The bounded first-test runbook actually executes:

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

If real approved Warehouse resources/permissions are unavailable, retain:

```text
warehouse.commit = NOT_RUN
warehouse.ambiguous_commit = NOT_RUN
```

Do not create synthetic Warehouse PASS just to fill the form.

## Two certification lanes remain separate

### Lane A — bounded company Fabric Notebook / manual governance — NEXT

```text
successful Framework main CI artifact
  -> isolated company Fabric DEV workspace
  -> exact wheel + CANDIDATE.json + SHA256SUMS
  -> attached disposable/default Lakehouse
  -> run bounded real tests
  -> record PASS / FAIL / NOT RUN
  -> optional explicit Admin Override
  -> manual-certification.json
```

No candidate freeze is required for this bounded pre-freeze smoke/compatibility test.

Admin Override may accept missing/unavailable/export-restricted coverage, with reason and missing fields retained. It should not be used to erase a known product defect: if an executed SCD/Lakehouse/identity check fails, retain `FAIL` and normally investigate first.

The GitHub-side `.github/workflows/candidate-admin-certification.yml` remains available. It does not connect to corporate Fabric; when supplied `candidate_run_id=33381666892`, GitHub independently resolves/verifies candidate SHA, run attempt, framework version, wheel bytes, `CANDIDATE.json`, `SHA256SUMS`, and wheel SHA256.

### Lane B — full automated evidence-based Framework release — LATER

This remains the strongest release path:

```text
exact frozen candidate
  -> Customer exact certification inputs
  -> candidate-integration-evidence
  -> candidate-business-path-evidence
  -> candidate-release-proofs
  -> candidate-certification
  -> blockers=[] / release_ready=true
  -> framework-release exact already-certified bytes
```

The existing strict `release.yml` does **not** accept a manual/Admin Override record as a substitute for this retained evidence chain.

## Current Customer evidence-based prerequisites

Customer PR #14 hardened the control-plane prerequisite. Seven arbitrary non-empty strings are not enough; the real external evidence set must eventually be review-bound to the exact protected environment/profile.

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

These older anchors are intentionally retained because Customer CI uses them to prevent recovery context from silently regressing:

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

`abc8b3a2...` is still the exact historical Framework source used by the Customer certification-contract lane. It must not be confused with the **current Framework substantive main baseline** `303683729...` used for the bounded company test.

## Exact next operating sequence

```text
1. read this file plus Framework docs/machine/STATE.md
2. open docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
3. in GitHub download Framework main run 33381666892 artifact 9753976212
4. create/use isolated company Fabric DEV workspace + disposable/default Lakehouse
5. upload wheel + CANDIDATE.json + SHA256SUMS together
6. install exact wheel; restart Python session if required
7. verify actual wheel SHA/version against CANDIDATE.json
8. run Lakehouse smoke
9. run FULL -> REPLACE
10. run SCD1
11. run SCD2
12. rerun SCD2 input to prove idempotency
13. force reconciliation FAIL and prove blocks_state_advance=true
14. keep Warehouse checks NOT_RUN if not genuinely available
15. open Notebook certification form and record actual PASS/FAIL/NOT RUN
16. optionally use explicit Admin Override for unavailable/export-restricted gaps; retain any real FAIL
17. inspect/retain manual-certification.json if company policy permits
18. optional GitHub admin record using candidate_run_id 33381666892
19. do NOT change Customer production pin and do NOT infer candidate freeze/release from this test
```

## What to do after the first test

If the bounded test passes, record the real result in canonical recovery docs without inflating its evidence class. Then decide whether to continue broader company-Fabric validation or prepare the still-missing real enterprise prerequisites for the full evidence-based release lane.

If a bounded test fails, retain which check failed and fix/retest. Do not use Admin Override merely to conceal a known framework defect.

## Evidence vocabulary boundary

Green CI, a candidate-capable wheel, successful package install, a Notebook dropdown, an administrator decision, or a source-controlled reference is not proof for a check that did not run.

The manual lane may legitimately say `CERTIFIED` because an administrator explicitly accepted a candidate. Keep that provenance distinct from claims such as `FABRIC PROVEN`, `PRODUCTION DB PROVEN`, `FABRIC WAREHOUSE PROVEN`, and evidence-based `RELEASE PROVEN`.