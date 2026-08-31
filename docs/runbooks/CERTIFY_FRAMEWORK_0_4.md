# Runbook — Produce Exact Customer Inputs for Framework 0.4 Certification

Status: source/CI contract implemented; live prerequisites intentionally incomplete

Last updated: 2026-08-31

This runbook covers the customer/domain side of Framework 0.4 release certification. It does **not** replace the normal Customer runtime dependency, which remains `fabric-data-framework==0.3.0` until v0.4.0 is actually released.

## 1. Purpose

Framework certification needs customer-owned WHAT without allowing the customer repo to decide PASS. This repository therefore owns an isolated certification slice:

```text
certification/project/config/datasets/
certification/project/config/certification/integration/
certification/project/config/certification/business/
certification/extensions/
```

The normal CRM project remains unchanged.

The certification slice contains representative paths for:

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

## 2. Evidence boundary

Customer code may provide only bounded facts or controlled fixture mutations:

```text
capture observer        -> actual landing facts
business observer       -> actual target/progress/history facts
business driver         -> deterministic fixture/control mutations + receipt
Warehouse mutation      -> mutation inside framework-owned transaction
fault controller        -> delegate to a real external provider/session fault controller
```

Customer extensions must never construct:

```text
ReleaseReadinessProofResult(PASS)
IntegrationEvidenceCheckResult(PASS)
certified IntegrationEvidenceManifest
release-readiness-certified artifact
```

PASS authority remains in `fabric-data-framework`.

## 3. Exact identities

The customer producer binds two independent identities:

```text
framework identity
  candidate_git_sha
  candidate_wheel_sha256

customer/domain identity
  customer_git_sha
  config_bundle_hash
  ReleaseManifest.bundle.release_hash
  exact certification recipe/scenario/driver/extension hashes
```

The framework wheel SHA256 and customer/domain release hash are deliberately different values and must never be substituted for each other.

## 4. CI-only static contract

`.github/workflows/certification-contract.yml` pins the certification schema/API to framework SHA:

```text
689bc1097474b26866af8675e32592e4cf65fa1f
```

That workflow:

```text
checkout exact framework source
install framework source
build customer certification extension wheel
run certification/build_candidate_inputs.py with dummy UUIDs/hashes
validate all typed DatasetConfig/recipe/plan/scenario/driver contracts
assert live_prerequisites_configured=false
assert exactly two current external blockers
```

This is source/CI proof only. It performs no Fabric REST call and no database mutation.

## 5. Current intentional live blockers

The repository currently ships these deliberate placeholders:

```text
control-plane-external-evidence.json
  all enterprise evidence references = null

warehouse-fault-run.json
  controller_url = https://warehouse-fault-controller.example.invalid
```

Therefore the builder must emit:

```text
live_prerequisites_configured=false
live_prerequisite_blockers=
  control_plane_external_evidence_incomplete
  warehouse_real_fault_controller_not_configured
```

Do not remove these blockers merely to make a workflow green. Replace them only with reviewed real enterprise evidence references and a real approved fault-controller endpoint.

## 6. Required real environment preparation

Before a live certification attempt, platform/data engineering must pre-provision the isolated certification resources named by the configs and recipes:

```text
Fabric workspace
read-only smoke item
certification Fabric Pipeline
certification Fabric Copy Job
certification Spark Job Definition
production-eligible control-plane SQL database
Fabric Warehouse target connection
framework Warehouse marker table
certification source/target/progress/control/landing tables
real ambiguous-COMMIT fault controller
```

The input producer never creates these resources and never stores passwords, tokens or connection strings.

The representative Pipeline must implement the certification contract expected by the source-controlled scenarios: it must run the selected DatasetConfig, persist the exact durable `DatasetDispatchOutcome`, honor the isolated certification control row for retry/reconciliation drills, and write the corresponding target/progress/history state. Fabric `Completed` alone is insufficient.

## 7. Produce an exact customer input artifact

After the customer certification configuration is merged to `main`, manually run:

```text
.github/workflows/candidate-business-path-inputs.yml
```

Required inputs:

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

The workflow also requires repository secret:

```text
FRAMEWORK_REPO_TOKEN
```

It is used only to authenticate downloading the retained exact framework Actions artifact. It is never written to customer output.

The workflow refuses customer source that is not reachable from Customer `main`.

## 8. What the producer verifies

The producer verifies the framework candidate run is:

```text
head_sha = candidate_git_sha
head_branch = main
event = push
conclusion = success
workflow path = .github/workflows/ci.yml
required framework jobs = success
```

It downloads only:

```text
framework-wheel-<candidate SHA>
```

and verifies `CANDIDATE.json`, `SHA256SUMS`, run attempt, version and exact inner wheel SHA256 before installing the candidate wheel.

It then builds the bounded customer extension wheel and runs the typed builder.

## 9. Output artifact

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

`INPUTS.json` records exact framework/customer identities and whether live prerequisites are configured. The artifact is an **input package**, not evidence that any provider check passed.

## 10. Framework consumers

The same exact customer artifact is consumed by framework workflows:

```text
candidate-integration-evidence.yml
candidate-business-path-evidence.yml
```

The integration workflow performs the real approved Fabric/control-plane/Warehouse checks. The business-path workflow consumes fully certified integration evidence and executes the five representative semantic drills.

Both framework consumers independently re-check customer SHA, workflow provenance, ReleaseManifest/config identity, extension wheel hashes and relevant recipe bytes.

## 11. Failure semantics

Expected failures are healthy when prerequisites are absent or inconsistent. Examples:

```text
candidate wheel hash mismatch          -> fail
customer commit not on main            -> fail
scenario/driver hash mismatch          -> fail
extension wheel not fingerprinted      -> fail
physical UUID malformed                -> fail
control-plane external evidence null   -> later live certification blocked
fault controller example.invalid       -> later Warehouse fault drill blocked
provider Completed but framework FAIL  -> no semantic success upgrade
cleanup failure                         -> no business-path PASS artifact
```

Never replace a missing real prerequisite with a synthetic PASS JSON.

## 12. Promotion sequence

Use this order:

```text
1. merge customer certification input contract
2. replace deliberate external placeholders with reviewed real bindings/evidence
3. run customer candidate-business-path-inputs for exact customer SHA + framework candidate
4. freeze/select one exact framework candidate only after producer paths are ready
5. run framework candidate-integration-evidence against real protected environment
6. run framework candidate-business-path-evidence for all five representative gates
7. merge non-integration release proofs
8. candidate certification must reach blockers=[]
9. exact-byte framework release promotion
10. only after immutable v0.4.0 exists, migrate Customer production dependency from v0.3.0
```

The presence of a customer input artifact does not justify freezing a candidate by itself.
