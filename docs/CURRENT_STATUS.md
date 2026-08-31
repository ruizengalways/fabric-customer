# Current Status — fabric-customer

Last updated: 2026-08-31

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer WATERMARK/SCD2 vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **COMPLETE AND MERGED**.
- Enterprise bulk-onboarding/domain-bootstrap reference: **IMPLEMENTED**.
- Framework 0.4-next project-contract adoption: **COMPLETE AND MERGED**.
- Framework 0.4 customer certification-input producer: **PR CI PROVEN / PENDING MERGE — PR #10**.
- Customer production runtime dependency upgrade: **WAITING FOR IMMUTABLE FRAMEWORK `v0.4.0` RELEASE**.

## PR #10 certification-input implementation proof

The implementation head `51d8d918b8e73a5b38c20e810117b854f8080b5b` passed both independent PR workflows before this documentation checkpoint:

```text
customer-ci                       33353622482  SUCCESS
  source-metadata-and-wheel                       SUCCESS
  exact-framework-integration                    SUCCESS
  framework-next-project-contract                SUCCESS
  released v0.3.0 cross-package tests            12 passed

customer-certification-contract   33353622537  SUCCESS
  framework certification SHA                    689bc1097474b26866af8675e32592e4cf65fa1f
  certification DatasetConfig count              8
  extension wheel build                           SUCCESS
  typed customer input builder                    SUCCESS
  live_prerequisites_configured                   false
  blocker: control_plane_external_evidence_incomplete
  blocker: warehouse_real_fault_controller_not_configured
```

This is **PR CI proof**, not merged-main proof and not live Fabric proof. The static certification run used dummy candidate identities solely to validate schemas and fail-closed packaging. Its generated domain release hash and extension-wheel build are not release/candidate evidence.

## Merged project-contract baseline

Feature PR:

```text
fabric-customer PR #8
merge SHA: d05f06d3a2f8d9e31f4c7d9459c8e55df44460ff
PR validation workflow: 33308362061
framework-next SHA: 148e02e3fff7861f238296e7554815a6fd49dd0a
```

All three CI proof lanes passed before merge:

```text
source-metadata-and-wheel        SUCCESS
exact-framework-integration      SUCCESS
framework-next-project-contract  SUCCESS
```

This baseline is source/CI proof. It is not live Fabric/provider/capacity evidence.

## Released runtime baseline remains v0.3.0

Customer production/release packaging still exact-pins:

```text
fabric-data-framework==0.3.0
```

The stable CI integration lane downloads the immutable v0.3.0 wheel, verifies `SHA256SUMS`, installs it, runs the Customer cross-package tests and builds same-release deployment plans.

This remains the only released framework dependency for Customer. Framework source `0.4.0` is still unreleased and must not be substituted into the release workflow.

## Exact framework-next compatibility baseline

The existing project-contract lane still targets:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

It proves source compatibility for `project-init` / `project-validate`, Customer root project validation and the 100-table Health project. It does not establish an immutable framework release or live Fabric evidence.

A separate certification-contract workflow targets current framework certification APIs at:

```text
689bc1097474b26866af8675e32592e4cf65fa1f
```

That second SHA is deliberately a different lane. It validates only the new customer certification input schema and does not change the released Customer dependency or the historical project-contract baseline.

## Customer project contract

The normal Customer repository source of truth remains:

```text
fabric-project.json
config/datasets/crm.customer.json
config/capture/semantic-selections.json
```

The existing `deploy/` folder remains the non-secret environment binding owner, and `fabric-project.json` points `environment_binding_dir` to that existing directory so adoption does not duplicate environment binding sources of truth.

Framework-next `project-validate .` fails closed on invalid/duplicate DatasetConfig values, unknown dependencies, cycles, unsupported capture/apply capability combinations, missing/unknown semantic selections and semantic history/delete overclaims. A PASS is static project validation only.

## Framework 0.4 certification input slice

The certification slice is isolated from the normal CRM project:

```text
certification/project/config/datasets/
certification/project/config/certification/integration/
certification/project/config/certification/business/
certification/extensions/
```

Representative DatasetConfig values cover:

```text
cert.full_replace                  FULL      -> REPLACE
cert.watermark_scd1                WATERMARK -> SCD1
cert.watermark_scd2                WATERMARK -> SCD2
cert.retry_idempotency             FULL      -> REPLACE
cert.reconciliation_fail_closed    FULL      -> REPLACE
cert.copy                          WATERMARK -> REPLACE via Fabric Copy Job
cert.spark                         WATERMARK -> REPLACE via capture-only Spark
cert.warehouse                     FULL      -> REPLACE for Warehouse commit drills
```

The five business-path scenarios are exact source-controlled expectations for:

```text
full.replace
watermark.scd1
watermark.scd2
retry.idempotency
reconciliation.fail_closed
```

The business driver resets bounded source/target/progress/history certification tables before observation and cleans them afterward. It returns only mutation receipts. Observers read actual database state. Customer extensions never build release-readiness or integration PASS results.

## Exact customer input producer

Manual workflow:

```text
.github/workflows/candidate-business-path-inputs.yml
```

It accepts an exact successful framework main-CI run and non-secret physical Fabric UUIDs. It requires the customer source SHA to be reachable from Customer `main`, authenticates the framework run, downloads `framework-wheel-<candidate SHA>`, verifies `CANDIDATE.json` + `SHA256SUMS` + exact inner wheel SHA256, installs those exact bytes, builds the fingerprinted customer extension wheel and runs the typed builder.

Successful packaging uploads only:

```text
business-path-inputs-<customer SHA>
```

containing:

```text
INPUTS.json
release-manifest.json
runner-config.json
project/
dist/fabric_customer_certification_extensions-0.4.0.dev0-py3-none-any.whl
```

This is an input artifact, not provider evidence and not readiness proof.

The two release identities remain separate:

```text
framework candidate wheel SHA256
!=
customer ReleaseManifest.bundle.release_hash
```

The framework consumers independently re-check both identities.

## Fail-closed current live boundary

Current source intentionally reports:

```text
live_prerequisites_configured=false
live_prerequisite_blockers=
  control_plane_external_evidence_incomplete
  warehouse_real_fault_controller_not_configured
```

Reason:

- `control-plane-external-evidence.json` has null enterprise evidence references;
- `warehouse-fault-run.json` uses `https://warehouse-fault-controller.example.invalid`.

These placeholders must be replaced only with reviewed real enterprise evidence and a real provider/session fault controller. They must never be replaced with synthetic PASS values simply to make certification green.

Dedicated runbook:

```text
docs/runbooks/CERTIFY_FRAMEWORK_0_4.md
```

## Enterprise 100-table Health proof

The fixture remains:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT
```

The default generator mode remains compatible with released Framework v0.3.0.

The `--framework-next` mode resolves one semantic selection per dataset, writes explicit Debezium `EXTERNAL_CDC` capture operations, uses `progress_owner=EXTERNAL`, pins `capability_profile=debezium_kafka_v1` and keeps final target apply on framework Spark authority.

The validated exact framework-next project summary remains:

```text
datasets: 100
semantic selections: 100
capture strategies: FULL=50, WATERMARK=40, CDC=10
apply strategies: REPLACE=50, SCD1=20, SCD2=20, UPSERT=10
execution groups: health_full_refresh=50, health_scd2=20, health_scd1=20, health_debezium=10
capture engines: SPARK=90, EXTERNAL_CDC=10
apply engines: SPARK=100
```

This is configuration/onboarding scale proof, not a 100-table runtime capacity benchmark.

## CI proof taxonomy

Keep these claims separate:

```text
v0.3 released-wheel integration PASS
!=
0.4-next exact-SHA static project PASS
!=
0.4 certification-contract typed input PASS
!=
customer candidate input artifact produced
!=
real Fabric/provider/runtime PASS
!=
100-table capacity/performance PASS
```

## Current external boundary

- No real Fabric workspace deployment has executed for the new certification slice.
- Normal checked-in `deploy/` bindings remain reference values, not company production resource IDs.
- Real certification Fabric Pipeline/Copy/Spark item UUIDs are not checked into semantic DatasetConfig.
- No actual production control-plane external evidence references are retained in the certification source yet.
- No real Warehouse ambiguous-COMMIT fault controller is configured yet.
- No certified integration evidence or five-gate business-path proof artifact has been retained.
- No Customer production release using framework v0.4.0 has been created.
- No live Debezium/Kafka integration evidence has been retained.
- No 100-table concurrency/capacity benchmark has been executed.

## Exact next implementation sequence

1. Finish PR #10 final documentation/contract CI, squash merge, then independently verify both workflows on Customer `main`.
2. Replace the two deliberate live placeholders with reviewed real enterprise evidence/fault infrastructure in a separate exact customer SHA.
3. Produce `business-path-inputs-<customer SHA>` for the exact selected framework candidate only when real physical inputs are available.
4. Hard-bind the same customer/domain `domain_release_hash` through final framework release proof/candidate certification before candidate freeze.
5. Only after producer paths and real prerequisites are ready, select/freeze one exact framework candidate.
6. Run framework `candidate-integration-evidence.yml` against the protected real environment.
7. Run framework `candidate-business-path-evidence.yml` for all five representative gates.
8. Complete release proofs and candidate certification until blockers are zero.
9. Promote the exact certified framework wheel bytes.
10. Only after immutable v0.4.0 is published, upgrade Customer `pyproject.toml` / release CI / imports from v0.3.0 in one reviewed migration PR.

Do not add dozens of fake runtime tables. Use the bulk manifest for onboarding/config scale and small representative datasets for reusable runtime correctness and release certification.

## Documentation check obligation

Every coherent implementation must cross-check at least:

```text
README.md
docs/PROJECT_BLUEPRINT.md
docs/CURRENT_STATUS.md
docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md
docs/runbooks/CERTIFY_FRAMEWORK_0_4.md
examples/enterprise_100_table/README.md
```

Commands, framework pins, evidence labels and repo-boundary guidance must agree before merge.
