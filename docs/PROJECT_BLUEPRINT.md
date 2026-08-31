# fabric-customer — Project Blueprint

Status: Canonical
Last updated: 2026-08-31

## 1. Goal

Provide a realistic Customer-domain reference that consumes reusable `fabric-data-framework` behavior without copying generic capture/apply/control-plane algorithms, supports large enterprise onboarding in one business-domain repo, and provides customer-owned exact inputs for Framework 0.4 release certification without moving PASS authority into the domain repo.

## 2. Ownership

Customer/domain repo owns WHAT:

- source-controlled DatasetConfig values and source/capture semantic selections;
- parsing/mapping, business DQ/reconciliation rule definitions and fixtures;
- domain tests, execution grouping and non-secret bindings;
- domain-owned Fabric items when introduced;
- representative certification datasets/scenarios/driver recipes;
- bounded observers/drivers/mutation extensions;
- exact customer/domain `ReleaseManifest` artifacts.

Framework owns HOW:

- DatasetConfig schema and capability validation;
- generic capture/Bronze/apply/reconciliation/state semantics;
- reusable Fabric adapters and approved provider runners;
- project-init/project-validate;
- integration/business-path evidence evaluation;
- release-readiness PASS/FAIL and candidate certification.

No generic capture/SCD/project-validation/evidence-PASS algorithm belongs in this repo.

## 3. Normal business project

```text
fabric-project.json
config/datasets/crm.customer.json
config/capture/semantic-selections.json
```

`crm.customer` uses WATERMARK capture on `modified_at` with `customer_id` tie-breaker and SCD2 apply. Its semantic selection explicitly records that hard deletes are not observable without a delete signal and that SCD2 history cannot exceed changes observed by the watermark path.

DEV/UAT/PROD materialize the same released semantic definition while retaining independent runtime state.

The release-certification project is intentionally separate:

```text
certification/project/
```

It is not the CRM production DatasetConfig bundle.

## 4. Domain and certification code

`src/fabric_customer/domain.py` contains Customer-specific business behavior.

`certification/extensions/` contains bounded certification extensions only:

```text
capture observer
Spark execution-data projection
Warehouse mutation inside framework-owned transaction
real external Warehouse fault-controller adapter
business-path observer
deterministic fixture/fault driver
capture-only forbidden apply guard
```

These extensions may return facts, receipts and bounded mutation evidence. They may not construct readiness or integration PASS results.

## 5. Enterprise onboarding model

The checked-in Health fixture models one domain repo:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT
```

Do not split those into four repositories. Capture/apply are per-dataset semantics; repo boundaries follow ownership, security/compliance and independent release lifecycle.

For the ten rows declaring Debezium, framework-next generation emits:

```text
capture_strategy   = CDC
engine             = EXTERNAL_CDC
progress_owner     = EXTERNAL
capability_profile = debezium_kafka_v1
apply_engine       = SPARK
semantic pattern   = FULL_CHANGES_EVENT
```

This remains source-controlled intent, not live Kafka evidence.

## 6. Dependency and compatibility model

Production/release dependency remains:

```text
fabric-data-framework==0.3.0
```

The released integration lane downloads the immutable v0.3.0 wheel/checksum and never substitutes Framework `main`.

Historical project-contract compatibility lane remains:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

It proves project-init/project-validate compatibility and the 100-table Health static project contract.

The independent **certification-contract lane** now tracks the current feature-frozen Framework code baseline:

```text
abc8b3a2b80b3f6babf88fdc2347a3bfe69be356
```

This is Framework PR #94: exact domain-release identity binding from PR #92 is present, and the obsolete runner-level candidate-proof path without `domain_release_hash` has been removed. The lane validates the Customer certification input schema against this exact source SHA only.

Neither development lane changes `pyproject.toml` or becomes a production runtime dependency.

## 7. Certification project contract

The isolated exact-release bundle contains eight representative DatasetConfig values:

```text
cert.full_replace
cert.watermark_scd1
cert.watermark_scd2
cert.retry_idempotency
cert.reconciliation_fail_closed
cert.copy
cert.spark
cert.warehouse
```

The five mandatory business-path entries are:

```text
full.replace
watermark.scd1
watermark.scd2
retry.idempotency
reconciliation.fail_closed
```

Plan/scenario/driver/recipe files and the Customer extension wheel are fingerprinted in the generated exact `ReleaseManifest.artifact_sha256`. DatasetConfig bytes are bound through the config-bundle hash.

The deterministic driver prepares baseline/attempt state and mandatory cleanup. It returns mutation receipts only. The observer reads actual bounded state. Framework evaluates PASS/FAIL.

## 8. Dual exact identity invariant

Framework and customer release identities are independent:

```text
framework candidate:
  candidate_git_sha
  candidate_wheel_sha256

customer/domain release:
  customer_git_sha
  config_bundle_hash
  ReleaseManifest.bundle.release_hash
```

`runner-config.json` binds both separately:

```text
framework_artifact_sha256 = exact framework wheel SHA256
release_hash              = exact customer/domain release hash
```

They must never be assumed equal.

Framework PR #92 carries `domain_release_hash` through business-path proof, strict proof merge, candidate certification and final promotion verification. Framework PR #94 removes the obsolete runner-level unbound proof packaging path. Customer never chooses readiness PASS.

## 9. Exact input producer

Owner:

```text
.github/workflows/candidate-business-path-inputs.yml
```

It is manual packaging only. It:

```text
requires customer SHA reachable from main
verifies exact framework candidate main-push CI provenance
verifies retained CANDIDATE.json / SHA256SUMS / inner wheel SHA256
installs exact candidate wheel bytes
builds bounded Customer extension wheel
runs typed certification/build_candidate_inputs.py
uploads business-path-inputs-<customer SHA>
```

It never invokes live Framework Pipeline/Copy/Spark/Warehouse evidence runners and never emits release proof or integration evidence.

## 10. Fail-closed live prerequisites

Current source deliberately retains exactly two blockers:

```text
control_plane_external_evidence_incomplete
warehouse_real_fault_controller_not_configured
```

The control-plane external evidence file has null reviewed evidence references; the fault recipe points to `example.invalid`. Therefore a CI-valid customer input package cannot accidentally become live-ready.

Only reviewed enterprise evidence and an approved real provider/session fault-controller endpoint may replace these placeholders, in a new exact Customer SHA.

## 11. CI proof model

```text
source-metadata-and-wheel
  source-only validation + canonical docs + Customer wheel

exact-framework-integration
  immutable v0.3.0 integration + Customer tests + release/deployment plan

framework-next-project-contract
  exact historical project-contract SHA + Customer/Health project-validate

customer-certification-contract
  exact current Framework PR #94 code SHA
  + certification extension wheel
  + typed customer input build
  + assertion that live blockers remain fail-closed
```

A PASS in one lane does not imply another proof class.

## 12. Current repo shape

```text
fabric-customer/
  fabric-project.json
  pyproject.toml
  config/
  certification/
    build_candidate_inputs.py
    project/
    extensions/
  examples/enterprise_100_table/
  scripts/
  src/fabric_customer/
  tests/
  deploy/
  docs/
    PROJECT_BLUEPRINT.md
    CURRENT_STATUS.md
    runbooks/
      BUILD_NEW_DOMAIN_PROJECT.md
      CERTIFY_FRAMEWORK_0_4.md
```

`deploy/` remains the normal non-secret environment-binding owner. The certification project is a release-proof fixture, not a second business project.

## 13. Proof taxonomy

```text
manifest/config scale proof
!=
runtime correctness proof
!=
released dependency proof
!=
certification input packaging proof
!=
real Fabric provider integration proof
!=
framework release readiness proof
!=
capacity/performance proof
```

## 14. New-domain flow

For Framework v0.4+ the intended flow remains:

```text
install immutable framework wheel
-> fabric-framework project-init
-> source inventory
-> DatasetConfig + semantic selections
-> fabric-framework project-validate
-> domain tests
-> GitHub PR/CI
-> immutable domain release artifacts
-> Fabric DEV integration
-> UAT
-> PROD promotion
```

The release-certification flow is separate.

## 15. Release-certification order

```text
keep customer input producer contract green against current feature-frozen Framework code baseline
-> replace deliberate external placeholders with reviewed real inputs
-> explicitly select/freeze one exact Framework candidate only when real prerequisites are ready
-> package exact Customer inputs for that exact candidate
-> real candidate-integration-evidence
-> five live business-path gates
-> candidate-release-proofs
-> candidate certification blockers=[]
-> exact certified-byte Framework promotion
-> immutable v0.4.0
-> Customer production dependency migration
```

No selected/frozen Framework candidate, selected-candidate Customer input artifact, live certified integration evidence or five-gate live business proof exists yet.

## 16. Documentation obligation

Every coherent change cross-checks:

```text
README.md
docs/PROJECT_BLUEPRINT.md
docs/CURRENT_STATUS.md
docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md
docs/runbooks/CERTIFY_FRAMEWORK_0_4.md
examples/enterprise_100_table/README.md
```

Version pins, commands, evidence labels and ownership boundaries must agree before merge.
