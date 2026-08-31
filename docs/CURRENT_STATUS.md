# Current Status — fabric-customer

Last updated: 2026-08-31

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer WATERMARK/SCD2 vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **COMPLETE AND MERGED**.
- Enterprise bulk-onboarding/domain-bootstrap reference: **IMPLEMENTED**.
- Framework 0.4-next project-contract adoption: **COMPLETE AND MERGED**.
- Framework 0.4 customer certification-input producer: **MERGED + MAIN CI PROVEN — PR #10**.
- Customer production runtime dependency upgrade: **WAITING FOR IMMUTABLE FRAMEWORK `v0.4.0` RELEASE**.

## Merged PR #10 certification-input baseline

```text
fabric-customer PR #10
merge SHA: cda90f1c02fc9606aa64d2d1bd13f2ab89628aab
final PR head: 798e22ab148de0f4bc72d691d06521f6996b0801
final PR customer-ci: 33353755262
final PR certification-contract: 33353755274
main customer-ci: 33353802842
main certification-contract: 33353802887
released v0.3.0 cross-package tests on main: 13 passed
```

Both independent main workflows passed on the exact merge SHA. The certification contract built the bounded extension wheel, loaded all 8 certification DatasetConfig values, validated the exact business-path plan/scenario/driver and integration recipes through Framework `689bc1097474b26866af8675e32592e4cf65fa1f`, and retained the deliberate fail-closed state:

```text
live_prerequisites_configured=false
live_prerequisite_blockers=
  control_plane_external_evidence_incomplete
  warehouse_real_fault_controller_not_configured
```

This upgrades the customer input producer to **MERGED + MAIN CI PROVEN** only. No manual `business-path-inputs-<customer SHA>` artifact has been produced for a real framework candidate, no live provider checks ran, and no framework candidate has been frozen.

## PR #10 implementation proof history

The earlier implementation head `51d8d918b8e73a5b38c20e810117b854f8080b5b` passed:

```text
customer-ci                       33353622482  SUCCESS
customer-certification-contract   33353622537  SUCCESS
released v0.3.0 cross-package tests            12 passed
certification DatasetConfig count              8
```

The final PR head added one documentation-state guard, bringing the stable v0.3.0 cross-package suite to 13 tests. Historical PR proof remains distinct from merged-main proof.

## Merged project-contract baseline

The earlier project-contract adoption remains:

```text
fabric-customer PR #8
merge SHA: d05f06d3a2f8d9e31f4c7d9459c8e55df44460ff
PR validation workflow: 33308362061
framework-next SHA: 148e02e3fff7861f238296e7554815a6fd49dd0a
```

This baseline is source/CI proof. It is not live Fabric/provider/capacity evidence.

## Released runtime baseline remains v0.3.0

Customer production/release packaging still exact-pins:

```text
fabric-data-framework==0.3.0
```

The stable CI integration lane downloads the immutable v0.3.0 wheel, verifies `SHA256SUMS`, installs it, runs the Customer cross-package tests and builds same-release deployment plans.

This remains the only released framework dependency for Customer. Framework source `0.4.0` is still unreleased and must not be substituted into the release workflow.

## Exact framework compatibility lanes

The existing project-contract lane still targets:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

It proves source compatibility for `project-init` / `project-validate`, Customer root project validation and the 100-table Health project.

The separate certification-contract workflow targets:

```text
689bc1097474b26866af8675e32592e4cf65fa1f
```

It validates only the customer certification input schema. Neither exact-SHA development lane changes the released Customer dependency.

## Customer project contract

The normal Customer repository source of truth remains:

```text
fabric-project.json
config/datasets/crm.customer.json
config/capture/semantic-selections.json
```

The existing `deploy/` folder remains the non-secret environment binding owner. The isolated certification project is not substituted for this business project.

## Framework 0.4 certification input slice

The certification slice is isolated under:

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

The five business-path scenarios are:

```text
full.replace
watermark.scd1
watermark.scd2
retry.idempotency
reconciliation.fail_closed
```

The driver deterministically resets bounded source/target/progress/history certification tables before observation and cleans them afterward. It returns only mutation receipts. Observers read actual database state. Customer extensions never build release-readiness or integration PASS results.

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

Current source intentionally reports the two blockers above because:

- `control-plane-external-evidence.json` has null enterprise evidence references;
- `warehouse-fault-run.json` uses `https://warehouse-fault-controller.example.invalid`.

They must be replaced only with reviewed real enterprise evidence and a real provider/session fault controller. They must never be replaced with synthetic PASS values simply to make certification green.

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

The framework-next validated project summary remains:

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

- No real Fabric workspace deployment has executed for the certification slice.
- Real certification Fabric Pipeline/Copy/Spark item UUIDs are not checked into semantic DatasetConfig.
- No actual production control-plane external evidence references are retained in certification source.
- No real Warehouse ambiguous-COMMIT fault controller is configured.
- No successful manual exact-candidate customer input producer run has been retained.
- No certified integration evidence or five-gate business-path proof artifact has been retained.
- No Customer production release using framework v0.4.0 has been created.
- No live Debezium/Kafka integration evidence has been retained.
- No 100-table concurrency/capacity benchmark has been executed.

## Exact next implementation sequence

1. Hard-bind the same customer/domain `domain_release_hash` through final framework ReleaseReadinessProofBundle, candidate certification and exact-byte promotion verification.
2. Keep the two deliberate Customer live placeholders until reviewed real enterprise evidence/fault infrastructure exists in a new exact customer SHA.
3. Produce `business-path-inputs-<customer SHA>` only when real physical inputs and an exact framework candidate are available.
4. Only after producer paths and real prerequisites are ready, select/freeze one exact framework candidate.
5. Run framework `candidate-integration-evidence.yml` against the protected real environment.
6. Run framework `candidate-business-path-evidence.yml` for all five representative gates.
7. Complete release proofs and candidate certification until blockers are zero.
8. Promote the exact certified framework wheel bytes.
9. Only after immutable v0.4.0 is published, upgrade Customer `pyproject.toml` / release CI / imports from v0.3.0 in one reviewed migration PR.

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
