# Current Status — fabric-customer

Last updated: 2026-08-31

## New-conversation recovery checkpoint

Start here when resuming this project in a new conversation. This section records the latest **substantive** cross-repo baselines; documentation-only checkpoints remain separate from code baselines.

```text
Framework substantive code baseline
  PR #94 merge SHA             abc8b3a2b80b3f6babf88fdc2347a3bfe69be356
  final PR CI                  33357795244
  main CI                      33357846835
  tests                        738
  candidate-capable wheel SHA  d763cd4410a69ff6a83c492f3a546d096502c96c87eeddb37c2ae9404557e7b7
  candidate frozen             false

Framework documentation checkpoint
  PR #95 merge SHA             4006afb409c81c5510690c8c4dbeadd5e002fd0b
  final PR CI                  33363382792
  main CI                      33363508468
  tests                        740

Customer substantive compatibility baseline
  PR #12 merge SHA             9ddc11405de329fb647fb21b1217d1015e0fa3f5
  PR customer-ci               33363980824 SUCCESS
  PR certification-contract    33363980826 SUCCESS
  main customer-ci             33364050484 SUCCESS
  main certification-contract  33364050481 SUCCESS
  released v0.3 tests          14 passed
  certification framework SHA  abc8b3a2b80b3f6babf88fdc2347a3bfe69be356
  production framework pin     fabric-data-framework==0.3.0

Customer release-hardening checkpoint
  PR #14 merge SHA             c4097dcc1319f382eb370e9c4d46dcbed7bb383b
  final PR head                456d3914743337e9c6ce9506fe1a2a7033e858ca
  PR customer-ci               33367986684 SUCCESS
  PR certification-contract    33367986688 SUCCESS
  main customer-ci             33368063581 SUCCESS
  main certification-contract  33368063590 SUCCESS
  production framework pin     fabric-data-framework==0.3.0
  candidate frozen             false
```

Current release truth remains:

```text
Framework public release                    v0.3.0
Framework 0.4 source                         feature-frozen / unreleased
Framework release_allowed                    false
Framework exact candidate                    not frozen
Framework ordinary readiness blockers        15
selected-candidate Customer input artifact   not retained
certified integration evidence               not produced
five live business-path proofs               not retained
immutable Framework v0.4.0                   not published
```

The next honest work is **real enterprise environment preparation**, not more synthetic proof code: obtain reviewed control-plane external evidence, bind that reviewed evidence to the exact protected environment/control-plane profile using the source-controlled review record, and obtain an approved real Warehouse/session ambiguous-COMMIT fault controller. Only after both real-environment prerequisites exist may a new exact Framework candidate be selected/frozen and the retained-evidence chain executed.

## Current phase

- Phase 0 canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer CRM WATERMARK/SCD2 vertical slice: **COMPLETE**.
- Enterprise delivery spine participation: **COMPLETE AND MERGED**.
- Enterprise 100-table onboarding/domain-bootstrap reference: **IMPLEMENTED**.
- Framework 0.4 project-contract adoption: **COMPLETE AND MERGED**.
- Framework 0.4 customer certification-input producer: **MERGED + MAIN CI PROVEN — PR #10**.
- Framework 0.4 certification compatibility alignment: **MERGED + MAIN CI PROVEN — PR #12**.
- Control-plane external-evidence review binding: **MERGED + MAIN CI PROVEN — PR #14**.
- Framework 0.4 domain-release proof binding: **COMPLETED IN FRAMEWORK PR #92; cleanup PR #94**.
- Customer production runtime dependency upgrade: **WAITING FOR IMMUTABLE FRAMEWORK v0.4.0**.

## Merged control-plane review binding — PR #14

PR #14 closes a fail-open gap in the Customer exact candidate-input producer without claiming any new live evidence. Before this change, seven arbitrary non-empty control-plane evidence reference strings could satisfy the Customer pre-candidate completeness gate. The live Framework runner would still execute real checks later, but the earlier release prerequisite did not encode the runbook requirement that the external evidence be reviewed and bound to the exact environment/profile.

PR #14 adds:

```text
certification/review_binding.py
certification/project/config/certification/integration/control-plane-external-evidence-review.json
docs/runbooks/CONTROL_PLANE_EXTERNAL_EVIDENCE_REVIEW.md
tests/test_certification_review_binding.py
```

The review-binding record is credential-free and contains only:

```text
environment
control_plane_profile
review_record_reference
evidence_set_reference
reviewed_at_utc
```

The exact rule is fail closed:

```text
seven external evidence references incomplete
  -> control_plane_external_evidence_incomplete

seven external evidence references complete
but review binding missing/incomplete/mismatched
  -> control_plane_external_evidence_not_review_bound

seven external evidence references complete
and review binding exactly matches environment/profile
  -> control-plane prerequisite may advance to later live certification gates
```

This does not validate the external enterprise ticket/catalog system, does not contact Fabric, does not execute database probes, and does not create a PASS result. It only prevents the exact Customer input producer from declaring the prerequisite configured from an unbound set of strings.

Verified PR/main identities:

```text
fabric-customer PR #14
merge SHA                    c4097dcc1319f382eb370e9c4d46dcbed7bb383b
final PR head                456d3914743337e9c6ce9506fe1a2a7033e858ca
PR customer-ci               33367986684 SUCCESS
PR certification-contract    33367986688 SUCCESS
main customer-ci             33368063581 SUCCESS
main certification-contract  33368063590 SUCCESS
production runtime pin       fabric-data-framework==0.3.0
candidate frozen             false
```

The source-controlled review-binding JSON remains all `null`; no real evidence was invented or committed.

## Merged compatibility alignment — PR #12

PR #12 moves only the isolated 0.4 certification-contract lane to the current feature-frozen Framework code baseline. It does not change Customer production runtime semantics or dependencies.

```text
fabric-customer PR #12
merge SHA                    9ddc11405de329fb647fb21b1217d1015e0fa3f5
final PR head                440cf23c81c953a15e1b698974eddf1f68a1f434
PR customer-ci               33363980824 SUCCESS
PR certification-contract    33363980826 SUCCESS
main customer-ci             33364050484 SUCCESS
main certification-contract  33364050481 SUCCESS
released v0.3 tests          14 passed
certification framework SHA  abc8b3a2b80b3f6babf88fdc2347a3bfe69be356
production runtime pin       fabric-data-framework==0.3.0
```

The main certification-contract run installed exact Framework PR #94 source, built the bounded Customer certification extension wheel, generated the typed input bundle, and retained the deliberate two-blocker fail-closed state. The independent `customer-ci` main run also kept the immutable v0.3.0 integration lane, source/docs lane and 100-table project-contract lane green.

## Released runtime baseline

Customer production/release packaging remains exactly:

```text
fabric-data-framework==0.3.0
```

The stable integration lane downloads the immutable v0.3.0 wheel, verifies its checksum, installs it, runs Customer tests and builds release/deployment plans. This is the only released Framework dependency for Customer.

Do not substitute Framework `main` or 0.4 development source into the production/release lane.

## Development compatibility lanes

These lanes are intentionally separate from production.

Historical project-contract lane:

```text
framework SHA 148e02e3fff7861f238296e7554815a6fd49dd0a
```

It proves source compatibility for project-init/project-validate, the normal Customer project and the 100-table Health fixture.

Current certification-contract lane:

```text
framework SHA abc8b3a2b80b3f6babf88fdc2347a3bfe69be356
```

This is the current feature-frozen Framework **code** baseline from PR #94. It includes:

```text
PR #92 exact customer/domain domain_release_hash binding
PR #94 removal of the obsolete runner-level unbound candidate-proof path
```

The certification lane builds the Customer certification extension wheel, runs `certification/build_candidate_inputs.py` with non-live test identities, validates typed DatasetConfig/recipes/scenarios/drivers and asserts the live boundary still fails closed. PR #14 additionally requires any future complete external-evidence set to carry an exact environment/profile review binding before that prerequisite can be considered configured.

This source/CI lane does not change the released dependency and is not real Fabric evidence.

## Customer certification producer baseline

Feature PR #10:

```text
merge SHA: cda90f1c02fc9606aa64d2d1bd13f2ab89628aab
final PR head: 798e22ab148de0f4bc72d691d06521f6996b0801
final PR customer-ci: 33353755262
final PR certification-contract: 33353755274
main customer-ci: 33353802842
main certification-contract: 33353802887
released v0.3.0 cross-package tests on main: 13 passed
```

Documentation checkpoint PR #11:

```text
merge SHA: 31f3f506bc1c16a445652de2ad48fe512cfec10a
customer main CI: 33353960915 SUCCESS
certification contract CI: 33353960906 SUCCESS
```

These runs proved the producer contract only. No manual `business-path-inputs-<customer SHA>` artifact has been retained for a selected Framework candidate.

## Framework release identity status

Framework now carries two independent exact SHA256 identities through the certification/release chain:

```text
framework candidate wheel SHA256
!=
customer ReleaseManifest.bundle.release_hash
```

Framework PR #92 binds the customer/domain release hash through:

```text
business-path proof packaging
-> strict ReleaseReadinessProofBundle merge
-> candidate certification
-> ReleaseReadinessReport
-> exact-byte promotion pre-tag checks
```

Framework PR #94 removes the obsolete business-path runner API that could package candidate proof without `domain_release_hash`.

Customer owns the exact `ReleaseManifest`; Customer still never decides PASS.

## Certification input slice

Source-controlled certification project:

```text
certification/project/config/datasets/
certification/project/config/certification/integration/
certification/project/config/certification/business/
certification/extensions/
```

Representative DatasetConfig values:

```text
cert.full_replace                  FULL      -> REPLACE
cert.watermark_scd1                WATERMARK -> SCD1
cert.watermark_scd2                WATERMARK -> SCD2
cert.retry_idempotency             FULL      -> REPLACE
cert.reconciliation_fail_closed    FULL      -> REPLACE
cert.copy                          WATERMARK -> REPLACE via Fabric Copy Job
cert.spark                         WATERMARK -> REPLACE via capture-only Spark
cert.warehouse                     FULL      -> REPLACE for Warehouse drills
```

Mandatory business-path scenarios:

```text
full.replace
watermark.scd1
watermark.scd2
retry.idempotency
reconciliation.fail_closed
```

Customer drivers prepare deterministic bounded fixtures/fault controls and return receipts only. Observers return bounded actual state. Customer extensions never construct readiness or integration PASS results.

## Exact customer input producer

Manual workflow:

```text
.github/workflows/candidate-business-path-inputs.yml
```

It accepts an exact successful Framework main-CI candidate run and non-secret physical Fabric identifiers. It:

```text
requires Customer source SHA reachable from main
authenticates exact Framework main-push CI provenance
downloads framework-wheel-<candidate SHA>
verifies CANDIDATE.json + SHA256SUMS + inner wheel SHA256
installs those exact wheel bytes
builds/fingerprints the Customer certification extension wheel
runs the typed input builder
uploads business-path-inputs-<customer SHA>
```

Output contains:

```text
INPUTS.json
release-manifest.json
runner-config.json
project/
dist/fabric_customer_certification_extensions-0.4.0.dev0-py3-none-any.whl
```

It is an input package only. It is not provider evidence, readiness proof or candidate certification.

## Current intentional real-environment blockers

Current source must report exactly:

```text
live_prerequisites_configured=false
live_prerequisite_blockers=
  control_plane_external_evidence_incomplete
  warehouse_real_fault_controller_not_configured
```

Reason:

```text
control-plane-external-evidence.json
  reviewed enterprise evidence references = null

control-plane-external-evidence-review.json
  exact environment/profile review binding = null

warehouse-fault-run.json
  controller_url = https://warehouse-fault-controller.example.invalid
```

Because the seven external evidence references are currently incomplete, the first blocker remains `control_plane_external_evidence_incomplete`. The new `control_plane_external_evidence_not_review_bound` blocker is intentionally evaluated only after all seven real evidence references exist; it prevents a complete-looking but unreviewed or environment/profile-mismatched set from clearing the prerequisite.

These are still real blockers to advancing certification. Do **not** remove them merely to make CI green.

They may be replaced only when the enterprise environment supplies:

1. reviewed real control-plane certification evidence references for the production-eligible control-plane database, plus a non-secret review record bound to the exact protected environment and exact control-plane profile; and
2. an approved reachable real Warehouse/session fault-controller endpoint capable of the ambiguous-COMMIT drill required by Framework evidence runners.

Neither value should be invented or committed as a secret. Tokens/passwords/connection strings remain environment secrets, not source-controlled evidence metadata.

## Real environment resources required before live certification

Pre-provision an isolated certification environment containing:

```text
Fabric workspace
read-only smoke item
certification Data Pipeline
certification Copy Job
certification Spark Job Definition
production-eligible control-plane SQL database
Fabric Warehouse target
framework Warehouse marker table
bounded certification source/target/progress/control/landing tables
approved real ambiguous-COMMIT fault controller
```

The Customer input producer does not create these resources.

## Enterprise 100-table Health proof

The reference remains:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT (Debezium)
```

Validated static summary:

```text
datasets: 100
semantic selections: 100
capture strategies: FULL=50, WATERMARK=40, CDC=10
apply strategies: REPLACE=50, SCD1=20, SCD2=20, UPSERT=10
execution groups: health_full_refresh=50, health_scd2=20, health_scd1=20, health_debezium=10
capture engines: SPARK=90, EXTERNAL_CDC=10
apply engines: SPARK=100
```

This is onboarding/configuration scale proof, not runtime capacity proof. Debezium live topic mapping/offset/replay/delete behavior still requires real integration evidence if promoted into required GA scope.

## Current evidence boundary

```text
released Customer runtime with Framework v0.3.0              PROVEN by release/integration CI
0.4 project-contract compatibility                            exact-SHA static proof
0.4 certification-input schema compatibility                 MERGED + MAIN CI PROVEN — PR #12
control-plane evidence review-binding gate                   MERGED + MAIN CI PROVEN — PR #14
customer certification producer contract                     MERGED + MAIN CI PROVEN
framework exact domain-release identity chain                MERGED + MAIN CI PROVEN (#92/#94)
selected/frozen Framework 0.4 candidate                       NOT YET
selected-candidate Customer input artifact                   NOT RETAINED
real control-plane external evidence                         NOT RETAINED
review-bound control-plane evidence set                      NOT RETAINED
real Warehouse ambiguous-COMMIT controller                   NOT CONFIGURED
certified Framework integration evidence                     NOT PRODUCED
five live business-path proofs                               NOT RETAINED
certified Framework readiness artifact                       NOT PRODUCED
immutable Framework v0.4.0                                   NOT PUBLISHED
Customer production migration to v0.4.0                      NOT ALLOWED YET
```

## Exact next sequence

1. Keep the Customer certification-contract lane green against the current feature-frozen Framework code baseline.
2. Replace the deliberate control-plane placeholders only after reviewed real enterprise evidence exists: populate the seven evidence references and the exact environment/profile review-binding record in one reviewed Customer SHA. Configure the Warehouse fault-controller placeholder only after approved real fault infrastructure exists.
3. Once both real-environment prerequisites are ready, explicitly select/freeze one **new exact Framework main candidate**; do not infer freeze from artifact existence.
4. Run Customer `candidate-business-path-inputs.yml` for that exact candidate and exact Customer SHA.
5. Run Framework `candidate-integration-evidence.yml` against the protected real environment.
6. Run Framework `candidate-business-path-evidence.yml` for all five representative gates.
7. Run Framework candidate release-proof aggregation for the same framework wheel and customer/domain release hash.
8. Candidate certification must reach `blockers=[]` and `release_ready=true`.
9. Framework release promotes the exact already-certified wheel bytes; no rebuild.
10. Only after immutable v0.4.0 exists, migrate Customer production dependency from v0.3.0 in one reviewed PR.

Do not add fake runtime tables or synthetic PASS evidence. Use the bulk fixture for onboarding/config scale and small representative datasets for reusable runtime/release certification.

## Documentation check obligation

Every coherent change must cross-check:

```text
README.md
docs/PROJECT_BLUEPRINT.md
docs/CURRENT_STATUS.md
docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md
docs/runbooks/CERTIFY_FRAMEWORK_0_4.md
docs/runbooks/CONTROL_PLANE_EXTERNAL_EVIDENCE_REVIEW.md
examples/enterprise_100_table/README.md
```

Commands, framework pins, proof labels and repo-boundary guidance must agree before merge.
