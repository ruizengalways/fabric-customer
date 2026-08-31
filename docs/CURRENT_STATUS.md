# Current Status — fabric-customer

Last updated: 2026-08-31

## Current phase

- Phase 0 canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer CRM WATERMARK/SCD2 vertical slice: **COMPLETE**.
- Enterprise delivery spine participation: **COMPLETE AND MERGED**.
- Enterprise 100-table onboarding/domain-bootstrap reference: **IMPLEMENTED**.
- Framework 0.4 project-contract adoption: **COMPLETE AND MERGED**.
- Framework 0.4 customer certification-input producer: **MERGED + MAIN CI PROVEN — PR #10**.
- Framework 0.4 domain-release proof binding: **COMPLETED IN FRAMEWORK PR #92; cleanup PR #94**.
- Customer production runtime dependency upgrade: **WAITING FOR IMMUTABLE FRAMEWORK v0.4.0**.

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

The certification lane builds the Customer certification extension wheel, runs `certification/build_candidate_inputs.py` with non-live test identities, validates typed DatasetConfig/recipes/scenarios/drivers and asserts the live boundary still fails closed.

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

warehouse-fault-run.json
  controller_url = https://warehouse-fault-controller.example.invalid
```

These are now the real blockers to advancing certification. Do **not** remove them merely to make CI green.

They may be replaced only when the enterprise environment supplies:

1. reviewed real control-plane certification evidence references for the production-eligible control-plane database; and
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
0.4 certification-input schema compatibility                 exact-SHA static proof
customer certification producer contract                     MERGED + MAIN CI PROVEN
framework exact domain-release identity chain                MERGED + MAIN CI PROVEN (#92/#94)
selected/frozen Framework 0.4 candidate                       NOT YET
selected-candidate Customer input artifact                   NOT RETAINED
real control-plane external evidence                         NOT RETAINED
real Warehouse ambiguous-COMMIT controller                   NOT CONFIGURED
certified Framework integration evidence                     NOT PRODUCED
five live business-path proofs                               NOT RETAINED
certified Framework readiness artifact                       NOT PRODUCED
immutable Framework v0.4.0                                   NOT PUBLISHED
Customer production migration to v0.4.0                      NOT ALLOWED YET
```

## Exact next sequence

1. Keep the Customer certification-contract lane green against the current feature-frozen Framework code baseline.
2. Replace the two deliberate live placeholders only after reviewed real enterprise evidence/fault infrastructure exists in a new exact Customer SHA.
3. Once the real environment is ready, explicitly select/freeze one **new exact Framework main candidate**; do not infer freeze from artifact existence.
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
examples/enterprise_100_table/README.md
```

Commands, framework pins, proof labels and repo-boundary guidance must agree before merge.
