# Current Status — fabric-customer

Last updated: 2026-08-31

## New-conversation recovery checkpoint

Start here when resuming this project. `main` is truth. The current project is no longer waiting for additional synthetic certification machinery: Framework now supports both a company-Fabric Notebook/manual certification transport and the existing fully automated evidence-based transport.

### Framework current substantive baseline

```text
Framework PR #97
  purpose                      Notebook/manual certification + explicit GitHub Admin Override
  merge SHA                    3b39448fcefbeba7a66469c847542c3255e462ff
  final PR CI                  33377064054 SUCCESS
  main CI                      33377208722 SUCCESS
  tests                        748 passed on Python 3.11 main lane
  candidate-capable wheel SHA  5d0c2f1f4348543bb8b9da0748788cc68b3ccbfed96fd73cec11ad7f475c0517
  candidate artifact ID        9752314929
  candidate frozen             false

Framework machine-state checkpoint PR #98
  merge SHA                    cc3f16099f5d9dc6c42189ec281a4d9d1a11e565
  PR CI                        33377525790 SUCCESS
  main CI                      33377589383 SUCCESS
```

PR #97 supersedes PR #94 as the current substantive Framework code baseline. PR #94 remains an important historical release-proof/domain-binding milestone:

```text
PR #94 merge SHA               abc8b3a2b80b3f6babf88fdc2347a3bfe69be356
PR #94 main CI                 33357846835 SUCCESS
PR #94 tests                   738
PR #94 wheel SHA               d763cd4410a69ff6a83c492f3a546d096502c96c87eeddb37c2ae9404557e7b7
```

### Customer current baseline

```text
Customer compatibility PR #12 merge       9ddc11405de329fb647fb21b1217d1015e0fa3f5
Customer control-plane hardening PR #14    c4097dcc1319f382eb370e9c4d46dcbed7bb383b
Customer recovery checkpoint PR #15       f83dc722da479971cdfd68d883291646c433ec15
Customer main CI                           33368266794 SUCCESS
Customer main certification-contract CI    33368266793 SUCCESS
production Framework dependency            fabric-data-framework==0.3.0
```

### Compatibility / recovery anchors retained by CI

These historical anchors remain in the canonical status because Customer CI uses them to prevent cross-repo recovery information from silently regressing while newer Framework capabilities are added.

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

**Do not change the production dependency to 0.4 development source.** The normal Customer runtime remains `fabric-data-framework==0.3.0` until an immutable Framework v0.4.0 is actually published and the release policy permits migration.

## Current release truth

```text
Framework public release                    v0.3.0
Framework 0.4 source                         feature-frozen / unreleased
Framework release_allowed                    false
Framework exact candidate                    not frozen
Framework ordinary readiness blockers        15
manual/admin certification capability         implemented
manual/admin certification record retained    no
selected-candidate Customer input artifact   not retained
certified integration evidence               not produced
five live business-path proofs               not retained
immutable Framework v0.4.0                   not published
Customer production pin                      fabric-data-framework==0.3.0
```

No candidate was frozen by implementing PR #97. No live Fabric evidence was invented. No administrator override has actually been executed yet.

## Certification now has two supported operating paths

### Path A — Company Fabric Notebook / manual certification

Use this now when corporate Fabric administration makes GitHub-to-Fabric connectivity undesirable or impractical.

```text
successful Framework main CI
  -> exact wheel + CANDIDATE.json
  -> bring files into isolated company Fabric environment
  -> install wheel in Fabric Notebook / Environment
  -> run the real checks that company permissions allow
  -> use Framework Notebook certification form
  -> create manual-certification.json
```

Framework PR #97 provides:

```python
from fabric_data_framework.evidence.manual_certification import (
    display_notebook_certification_form,
)

display_notebook_certification_form(
    candidate_manifest_path="CANDIDATE.json",
    output_path="manual-certification.json",
)
```

When `CANDIDATE.json` is available, the operator does not have to copy long identifiers manually. Framework auto-resolves:

```text
framework_version
candidate_git_sha
wheel SHA256
```

If the original wheel file is also available, the Notebook API can hash those actual bytes and reject an identity mismatch.

The form supports observed checks for:

```text
Lakehouse smoke
FULL -> REPLACE
WATERMARK -> SCD1
WATERMARK -> SCD2
retry / idempotency
reconciliation fail-closed
Warehouse commit
Warehouse ambiguous-COMMIT recovery
```

A normal non-override Notebook record is fail-closed. If exact candidate identity is missing it remains `PARTIAL`; normal `CERTIFIED` requires exact identity plus supplied checks that are all PASS.

### Explicit Admin Override

For a corporate environment where some identifiers/evidence cannot conveniently leave Fabric, the Notebook form also supports an explicit administrator override.

It may produce:

```text
status = CERTIFIED
admin_override = true
override_reason = required
missing_fields = retained
```

Fields that cannot be supplied may remain absent. The record does not silently fabricate them. Unrun Warehouse, control-plane, Lakehouse, or business-path checks are not converted into fake evidence.

The Framework also contains:

```text
.github/workflows/candidate-admin-certification.yml
```

This workflow **does not connect to company Fabric**. It needs no `FABRIC_ACCESS_TOKEN`, Fabric Service Principal, Warehouse URL, control-plane URL, or company tenant credentials.

For candidate identity, the operator supplies only a successful Framework `main` CI `candidate_run_id`. GitHub then automatically resolves/verifies:

```text
candidate_git_sha
workflow run attempt
framework_version
CANDIDATE.json
SHA256SUMS
exact wheel SHA256
exact wheel bytes
```

The user may optionally provide:

```text
environment
notebook_reference
notes
```

and must explicitly provide:

```text
override_reason
confirm_admin_override = true
```

This meets the practical requirement that long SHA values do not have to be manually copied from a locked-down corporate environment.

### Important release-policy boundary

Admin Override is a real, explicit governance decision, but it is deliberately distinguishable from evidence-based certification.

Framework PR #97 did **not** change the existing strict `release.yml`. The current immutable-release workflow still expects the normal evidence-based candidate-certification provenance and release-readiness/proof/integration artifacts.

Therefore:

```text
manual/admin record can say CERTIFIED
!=
missing live checks were automatically proven
!=
existing framework-release is automatically unblocked
```

If the project later decides that an Admin Override should also be able to authorize tag/release creation directly, that is a separate release-policy decision and must be implemented explicitly rather than hidden inside the manual record.

## Path B — Full automated evidence-based certification

This existing path remains for a later private/approved Fabric environment where GitHub Actions may authenticate into Fabric and related databases.

```text
exact frozen candidate
  -> Customer exact certification inputs
  -> candidate-integration-evidence
  -> candidate-business-path-evidence
  -> candidate-release-proofs
  -> candidate-certification
  -> blockers=[] / release_ready=true
  -> framework-release exact certified bytes
```

It remains the strongest machine-verifiable release path.

## Current Customer evidence-based prerequisites

Customer PR #14 hardened the pre-candidate control-plane prerequisite. Seven arbitrary non-empty strings are not enough. The real evidence set must eventually be bound to the exact protected environment/control-plane profile by a credential-free review record.

Current source intentionally still contains incomplete placeholders:

```text
certification/project/config/certification/integration/control-plane-external-evidence.json
  real reviewed evidence references = incomplete/null

certification/project/config/certification/integration/control-plane-external-evidence-review.json
  environment = null
  control_plane_profile = null
  review_record_reference = null
  evidence_set_reference = null
  reviewed_at_utc = null

certification/project/config/certification/integration/warehouse-fault-run.json
  controller_url = example.invalid placeholder
```

Therefore the current exact evidence-based Customer builder truth remains:

```text
live_prerequisites_configured=false
live_prerequisite_blockers=
  control_plane_external_evidence_incomplete
  warehouse_real_fault_controller_not_configured
```

If all seven real control-plane evidence references later become complete but the exact review binding is absent/mismatched, the fail-closed transition is:

```text
control_plane_external_evidence_not_review_bound
```

The manual/Admin Override path does not rewrite or delete these evidence-based prerequisites. It is a separate governance path.

## What certification means in this project

Keep these concepts separate:

```text
fabric-data-framework
  = reusable engine/product

fabric-customer
  = concrete project/configuration and representative certification inputs

certification inputs
  = what/where/how to test

certification evidence
  = what actually happened in the environment

manual/admin certification
  = explicit human governance decision, with provenance and missing fields retained

automated evidence-based certification
  = machine-verifiable retained proof chain
```

Certification is a Framework release activity. Normal future customer projects do not repeat the entire Framework release certification every day; they consume an immutable released version and use normal `project-init / project-validate / dry-run / deploy / run` workflows. The 100-table reference continues to cover mixed FULL, watermark/SCD and Debezium-style onboarding patterns.

## Company Fabric operating sequence now

For the current corporate-account situation, the practical next sequence is:

```text
1. use an isolated company Fabric DEV workspace/item set that permissions allow
2. choose/download one exact Framework main CI artifact; do not infer candidate freeze merely from artifact existence
3. keep the wheel and CANDIDATE.json together when possible
4. install the wheel in a Fabric Notebook / Environment
5. start with Lakehouse/small-data smoke validation; Warehouse may remain unavailable until company permission is granted
6. run additional FULL/SCD1/SCD2/retry/reconciliation checks that are allowed
7. generate manual-certification.json using the Notebook form
8. if some details cannot be exported, use explicit Admin Override and record a reason rather than inventing missing fields
9. if a GitHub-side exact admin record is desired, run Framework candidate-admin-certification using the exact main CI candidate_run_id; GitHub still does not connect to corporate Fabric
```

A manual partial or override record is allowed even while the evidence-based control-plane/Warehouse prerequisites remain unavailable.

## Full automated release sequence later

When an approved/private Fabric environment is available and the project wants full evidence-based certification:

```text
1. obtain reviewed real control-plane external evidence and exact review binding
2. obtain/approve a real Warehouse ambiguous-COMMIT fault controller
3. explicitly select/freeze one NEW exact Framework main candidate
4. run Customer candidate-business-path-inputs for the same exact candidate and Customer SHA
5. run Framework candidate-integration-evidence
6. run the five Framework candidate-business-path-evidence drills
7. run candidate-release-proofs
8. candidate-certification must reach blockers=[] and release_ready=true
9. framework-release promotes exact already-certified wheel bytes; no rebuild
10. only after immutable v0.4.0 exists may Customer production dependency migrate from v0.3.0
```

## Current remaining evidence-based release gaps

```text
exact Framework candidate freeze                    NOT YET
selected-candidate Customer input artifact           NOT YET RETAINED
reviewed real control-plane external evidence        NOT YET RETAINED
review-bound control-plane evidence set              NOT YET RETAINED
real Warehouse ambiguous-COMMIT fault controller     NOT YET CONFIGURED
certified integration evidence                       NOT YET PRODUCED
five live business-path proofs                       NOT YET RETAINED
complete release proof                               NOT YET RETAINED
certified readiness artifact                         NOT YET PRODUCED
ordinary readiness blockers                          15
immutable v0.4.0                                      NOT YET PUBLISHED
Customer production dependency migration             NOT ALLOWED YET
```

## Evidence vocabulary boundary

Green CI, a candidate-capable wheel, a Notebook checkbox, an administrator decision, a source-controlled reference, or a successful Fabric item status must not be described as proof for a check that did not actually run.

The new manual lane may legitimately say `CERTIFIED` because an administrator explicitly accepted the candidate. That provenance must remain distinct from claims such as `FABRIC PROVEN`, `PRODUCTION DB PROVEN`, `FABRIC WAREHOUSE PROVEN`, and evidence-based `RELEASE PROVEN`.