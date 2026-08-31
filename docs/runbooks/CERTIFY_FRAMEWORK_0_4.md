# Runbook — Produce Exact Customer Inputs for Framework 0.4 Certification

Status: source/CI contract implemented; live prerequisites intentionally incomplete

Last updated: 2026-08-31

This runbook covers the Customer/domain side of Framework 0.4 release certification. It does **not** replace the normal Customer runtime dependency, which remains `fabric-data-framework==0.3.0` until immutable v0.4.0 is released.

## 1. What this runbook produces

Customer owns an isolated certification input slice:

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

The normal CRM project remains separate.

Customer code supplies bounded facts or controlled mutations only. Framework remains the sole PASS authority.

## 2. Exact compatibility baseline

`.github/workflows/certification-contract.yml` installs exact Framework source at:

```text
abc8b3a2b80b3f6babf88fdc2347a3bfe69be356
```

This is Framework PR #94, the current feature-frozen **code** baseline. It contains the PR #92 customer/domain release-hash binding and PR #94 removal of the obsolete runner-level proof packaging path that lacked `domain_release_hash`.

The CI contract:

```text
checks out that exact Framework SHA
installs Framework source
builds the bounded Customer certification extension wheel
runs certification/build_candidate_inputs.py with dummy non-live identities
validates typed DatasetConfig/recipe/plan/scenario/driver contracts
asserts live_prerequisites_configured=false
asserts exactly two current external blockers
```

This is source/CI compatibility proof only. It performs no live Fabric REST call and no real database mutation.

The Customer production dependency remains:

```text
fabric-data-framework==0.3.0
```

## 3. Exact identities

Certification binds independent identities:

```text
framework identity
  candidate_git_sha
  candidate_wheel_sha256

customer/domain identity
  customer_git_sha
  config_bundle_hash
  ReleaseManifest.bundle.release_hash
  exact recipe/scenario/driver/extension hashes
```

Framework wheel SHA256 and Customer/domain release hash must never be substituted for each other.

Framework PR #92 carries the Customer hash through business-path proof, strict proof merge, candidate certification and final release checks. Framework PR #94 removes the old unbound business-path proof constructor. Customer never authors `ReleaseReadinessProofResult(PASS)` or `IntegrationEvidenceCheckResult(PASS)`.

## 4. Current intentional blockers

Current source deliberately contains:

```text
control-plane-external-evidence.json
  reviewed enterprise evidence references = null

warehouse-fault-run.json
  controller_url = https://warehouse-fault-controller.example.invalid
```

Therefore the typed builder must report:

```text
live_prerequisites_configured=false
live_prerequisite_blockers=
  control_plane_external_evidence_incomplete
  warehouse_real_fault_controller_not_configured
```

Do not remove these blockers merely to make CI green.

They can be replaced only by:

1. **reviewed real control-plane evidence metadata** for the production-eligible control-plane SQL database; and
2. an **approved reachable real Warehouse/session fault-controller endpoint** capable of the ambiguous-COMMIT drill.

Passwords, tokens and connection strings remain protected runtime secrets. They must not be committed into the evidence metadata or Customer input artifact.

## 5. Real environment preparation checklist

Before selecting a release candidate for live certification, platform/data engineering must have an isolated certification environment with:

```text
[ ] Fabric workspace
[ ] read-only smoke item
[ ] certification Fabric Data Pipeline
[ ] certification Fabric Copy Job
[ ] certification Spark Job Definition
[ ] production-eligible control-plane SQL database
[ ] Fabric Warehouse target
[ ] framework Warehouse marker table
[ ] bounded certification source tables
[ ] bounded target/progress/history tables
[ ] bounded retry/reconciliation control table
[ ] bounded Copy/Spark landing area
[ ] approved real ambiguous-COMMIT fault controller
```

The input producer does not create these resources.

The representative Pipeline must run the selected DatasetConfig and persist the durable Framework `DatasetDispatchOutcome`. It must honor the isolated certification control row used for retry/reconciliation drills and write the corresponding target/progress/history state. Fabric `Completed` alone is insufficient.

## 6. What must be reviewed before replacing each placeholder

### Control-plane external evidence

The source-controlled evidence file may contain safe references/identifiers proving the selected database/profile has been reviewed for the Framework control-plane contract. It must not contain credentials.

Before merge, reviewers should be able to answer:

```text
which production-eligible control-plane database/profile is being certified?
what retained enterprise evidence proves that selection?
are the references stable and safe to retain in a release artifact?
do they correspond to the same protected certification environment?
```

### Warehouse fault controller

The controller endpoint must refer to a real approved service able to induce/coordinate the required provider/session ambiguous-COMMIT condition. Before merge, verify:

```text
endpoint is real and reachable from the protected certification runner
controller acts on the exact Warehouse/session under test
authorization is separate from normal mutation authorization
session termination / fault action is auditable
the controller does not return a synthetic PASS decision
```

Framework remains responsible for interpreting the resulting provider/runtime evidence.

## 7. Select/freeze candidate only after prerequisites are ready

Do **not** freeze a Framework candidate simply because main CI produced a wheel.

When the two real blockers are resolved and the protected environment is ready, explicitly select one **new exact Framework main candidate**. Record:

```text
candidate main CI run ID
candidate source SHA
exact inner candidate wheel SHA256
```

Any Framework code change after selection creates a new candidate and invalidates reuse of exact-candidate evidence.

## 8. Produce exact Customer input artifact

With the exact candidate selected, manually run:

```text
.github/workflows/candidate-business-path-inputs.yml
```

Inputs:

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

Repository secret used only for authenticated Framework artifact retrieval:

```text
FRAMEWORK_REPO_TOKEN
```

The workflow refuses Customer source that is not reachable from Customer `main`.

## 9. Producer verification

The Framework candidate run must be:

```text
head_sha = candidate_git_sha
head_branch = main
event = push
conclusion = success
workflow path = .github/workflows/ci.yml
required Framework jobs = success
```

The producer downloads only:

```text
framework-wheel-<candidate SHA>
```

and verifies `CANDIDATE.json`, `SHA256SUMS`, run attempt, Framework version and exact inner wheel SHA256 before installing those exact bytes.

It then builds/fingerprints the Customer extension wheel and runs the typed input builder.

## 10. Output artifact

Successful packaging uploads:

```text
business-path-inputs-<customer SHA>
```

with:

```text
INPUTS.json
release-manifest.json
runner-config.json
project/config/datasets/*.json
project/config/certification/**
dist/fabric_customer_certification_extensions-0.4.0.dev0-py3-none-any.whl
```

`INPUTS.json` records exact Framework/Customer identities and live-prerequisite state. This remains an **input package**, not evidence that any provider check passed.

## 11. Framework live consumers

The same exact Customer artifact is consumed by:

```text
candidate-integration-evidence.yml
candidate-business-path-evidence.yml
```

The integration workflow performs real approved Fabric/control-plane/Warehouse checks. The business-path workflow requires fully certified integration evidence and executes the five representative semantic drills.

Both independently re-check Customer SHA, producer provenance, `ReleaseManifest`, config identity, extension hashes and relevant recipe bytes.

## 12. Five representative business paths

Framework business-path certification must retain proof for:

```text
full.replace
watermark.scd1
watermark.scd2
retry.idempotency
reconciliation.fail_closed
```

The Customer driver/observer never say PASS. Framework's evaluator determines readiness from independent fixture receipts, provider execution facts, durable Framework outcomes and observed target/progress/history state.

Cleanup failure means no business-path proof publication.

## 13. Failure semantics

Expected fail-closed outcomes include:

```text
candidate wheel hash mismatch          -> fail
Customer commit not on main            -> fail
scenario/driver hash mismatch          -> fail
extension wheel not fingerprinted      -> fail
physical UUID malformed                -> fail
control-plane evidence still null      -> live certification blocked
fault controller example.invalid       -> Warehouse fault drill blocked
provider Completed but Framework FAIL  -> no semantic success upgrade
cleanup failure                         -> no business-path PASS artifact
Framework/domain release hash mismatch -> candidate proof/certification rejected
```

Never replace a missing real prerequisite with synthetic PASS JSON.

## 14. Exact promotion sequence

```text
1. keep Customer certification-contract green against current feature-frozen Framework code baseline
2. provision/review the two real enterprise prerequisites
3. merge those real non-secret bindings/evidence references in a new exact Customer SHA
4. explicitly select/freeze one new exact Framework main candidate
5. run Customer candidate-business-path-inputs for that candidate and exact Customer SHA
6. run Framework candidate-integration-evidence in the protected real environment
7. run all five Framework candidate-business-path-evidence drills
8. run Framework candidate-release-proofs for the same framework wheel + domain release hash
9. candidate-certify must reach release_ready=true and blockers=[]
10. Framework release promotes the exact already-certified wheel bytes
11. only after immutable v0.4.0 exists, migrate Customer production dependency from v0.3.0
```

No current artifact or green CI run authorizes candidate freeze by itself.

## 15. Current truth

```text
Customer production runtime                     fabric-data-framework==0.3.0
Customer certification producer contract        merged + main CI proven
certification-contract Framework code baseline  abc8b3a2b80b3f6babf88fdc2347a3bfe69be356
real control-plane evidence                      missing
real Warehouse fault controller                  missing
selected/frozen Framework candidate              none
selected-candidate Customer input artifact       none retained
certified integration evidence                   none retained
five-gate live business proof                    none retained
immutable Framework v0.4.0                       not published
```
