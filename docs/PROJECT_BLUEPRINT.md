# fabric-customer — Project Blueprint

Status: Canonical
Last updated: 2026-08-31

## 1. Goal

Provide a realistic Customer-domain reference proving a domain can consume reusable `fabric-data-framework` behavior without copying generic capture/apply/control-plane algorithms, provide a production-oriented repository pattern for large enterprise onboarding, and provide customer-owned exact inputs for Framework 0.4 release certification without moving PASS authority into the domain repo.

## 2. Ownership

Customer/domain repo owns WHAT:

- source-controlled domain DatasetConfig values;
- source/capture semantic selections and known limitations;
- source parsing/mapping and canonical domain shapes;
- business-specific DQ/reconciliation rule definitions;
- domain fixtures/integration/smoke tests;
- domain-owned Fabric items when introduced;
- execution grouping and non-secret environment bindings;
- representative release-certification datasets/scenarios/driver recipes;
- bounded customer observers/drivers and target mutation extensions;
- exact customer/domain ReleaseManifest artifacts.

Framework owns HOW:

- DatasetConfig schema and capability validation;
- generic capture/runtime contracts;
- Bronze normalization and quarantine execution semantics;
- reusable SCD/apply algorithms;
- reconciliation/state/checkpoint rules;
- runtime audit and deployment/control-plane contracts;
- reusable Fabric adapters;
- project-init/project-validate tooling;
- approved provider runners;
- integration/business-path evidence evaluation;
- release-readiness PASS/FAIL and candidate certification.

No generic capture/SCD/project validation/evidence PASS algorithm should be copied into this repo.

## 3. Current Customer project source of truth

```text
fabric-project.json
config/datasets/crm.customer.json
config/capture/semantic-selections.json
```

`crm.customer` declares WATERMARK capture on `modified_at` with `customer_id` tie-breaker, SCD2 apply, Customer business keys, DQ/reconciliation policy references and execution group `crm_daily`.

The semantic selection explicitly records that hard deletes are not observable without a delete signal and that SCD2 history cannot exceed the changes observed by the watermark path.

DEV/UAT/PROD materialize the same released semantic definition while keeping independent runtime state.

The release-certification project is intentionally separate:

```text
certification/project/
```

It must not be treated as the normal CRM production DatasetConfig bundle.

## 4. Domain code

`src/fabric_customer/domain.py` contains only Customer-specific business behavior.

`certification/extensions/` contains only bounded release-certification extensions:

```text
capture observer
Spark execution-data projection
Warehouse mutation inside framework-owned transaction
real external Warehouse fault-controller adapter
business-path observer
business-path deterministic fixture driver
capture-only forbidden apply guard
```

These extensions may return facts/receipts/provider-neutral mutation evidence. They may not construct readiness or integration PASS results.

## 5. Small runtime correctness fixture

The CRM fixtures remain intentionally small. They prove domain/runtime behavior such as deterministic watermark ordering, quarantine lineage, SCD2 change detection, unchanged-row idempotency, reconciliation-gated state commit and rerun behavior.

Small runtime fixtures prove correctness. They are not a scale benchmark.

## 6. Enterprise 100-table onboarding reference

The checked-in Health intake fixture models one business/domain repository:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT
```

Do not split those into four repositories. Capture and apply are per-dataset semantics; repo boundaries follow ownership, security/compliance and release lifecycle.

`scripts/scaffold_from_manifest.py` retains its released-v0.3-compatible default mode plus the exact framework-next project-contract mode. The framework-next Health proof uses framework-owned `project-init` and `project-validate` instead of inventing a second project validator in Customer.

## 7. Debezium reference contract

For the ten rows whose manifest explicitly declares `source_system=debezium`, framework-next generation writes:

```text
capture_strategy   = CDC
engine             = EXTERNAL_CDC
progress_owner     = EXTERNAL
capability_profile = debezium_kafka_v1
apply_engine       = SPARK
semantic pattern   = FULL_CHANGES_EVENT
```

This is still source-controlled intent. Live topic mapping, offsets/order, tombstones/deletes, replay, outage recovery and provider credentials require real integration evidence.

## 8. Dependency and compatibility model

Production/release dependency remains:

```text
fabric-data-framework==0.3.0
```

The released integration lane downloads the v0.3.0 wheel/checksum and never substitutes Framework `main`.

Historical project-contract compatibility baseline remains:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

A separate certification-contract lane targets current exact evidence-input APIs at:

```text
689bc1097474b26866af8675e32592e4cf65fa1f
```

Those are distinct proof lanes. Neither changes `pyproject.toml` or becomes a production runtime dependency.

When v0.4.0 is published, the Customer runtime/package import migration must happen in a single reviewed PR; do not create permanent dual-runtime compatibility code without a demonstrated need.

## 9. Certification project contract

The isolated exact-release certification bundle contains eight representative DatasetConfig values:

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

The first five support the mandatory live semantic readiness gates. `cert.copy`, `cert.spark` and `cert.warehouse` support provider integration proof.

The business-path plan contains exactly:

```text
full.replace
watermark.scd1
watermark.scd2
retry.idempotency
reconciliation.fail_closed
```

Every plan/scenario/driver/recipe and the customer extension wheel is fingerprinted in the generated exact `ReleaseManifest.artifact_sha256`. DatasetConfig bytes are bound through the exact config-bundle hash.

Driver PREPARE_BASELINE resets bounded certification source/target/progress/history tables before the observer reads BEFORE state. Retry attempt preparation and reconciliation failure controls are explicit source-controlled actions. CLEANUP is mandatory and cannot create PASS.

## 10. Dual exact identity invariant

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

`runner-config.json` binds both:

```text
framework_artifact_sha256 = exact framework wheel SHA256
release_hash              = exact customer/domain release hash
```

They must never be assumed equal.

## 11. Exact input producer

Owner:

```text
.github/workflows/candidate-business-path-inputs.yml
```

It is manual packaging only. It:

```text
requires customer SHA reachable from main
verifies framework candidate main-push CI provenance
verifies exact retained CANDIDATE.json / SHA256SUMS / inner wheel SHA256
installs exact candidate wheel bytes
builds bounded customer extension wheel
runs typed certification/build_candidate_inputs.py
uploads business-path-inputs-<customer SHA>
```

It never invokes the live approved Framework Pipeline/Copy/Spark/Warehouse runners and never emits release proof or integration evidence.

The generated bundle contains `INPUTS.json`, `release-manifest.json`, `runner-config.json`, exact project files and exact extension wheel.

## 12. Fail-closed live prerequisites

Current source deliberately keeps two blockers:

```text
control_plane_external_evidence_incomplete
warehouse_real_fault_controller_not_configured
```

The control-plane external evidence file contains null references; the fault recipe points at `example.invalid`. Therefore a CI-valid customer input package cannot accidentally become live-ready.

Replacing these placeholders requires reviewed real enterprise evidence/fault infrastructure in a new exact customer SHA.

## 13. Current repo shape

```text
fabric-customer/
  fabric-project.json
  pyproject.toml
  config/
    datasets/crm.customer.json
    capture/semantic-selections.json
  certification/
    build_candidate_inputs.py
    project/
      config/datasets/
      config/certification/
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

The project manifest intentionally points `environment_binding_dir` to the existing `deploy/` directory so normal Customer adoption does not create a duplicate binding source of truth. The certification project is a release-proof fixture, not a second business project.

## 14. CI proof model

Proof lanes remain distinct:

```text
source-metadata-and-wheel
  source-only validation + canonical documentation consistency + Customer wheel build

exact-framework-integration
  immutable v0.3.0 release integration + Customer tests + release/deployment plans

framework-next-project-contract
  exact pinned project-contract SHA + Customer project-validate + 100-table Health project-validate

customer-certification-contract
  exact framework 689bc109... + certification extension wheel + typed input build
  + assertion that current live blockers remain fail-closed
```

A PASS in one lane does not imply another proof class.

## 15. Documentation consistency contract

`scripts/validate_docs.py` continues to derive the exact released framework dependency and the historical project-contract SHA. Certification-specific documentation uses `docs/runbooks/CERTIFY_FRAMEWORK_0_4.md` and the separately pinned certification workflow SHA.

This separation prevents a certification-development SHA from being mistaken for the production dependency or the earlier project bootstrap compatibility baseline.

## 16. Proof taxonomy

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

This distinction is non-negotiable in code comments, PR descriptions and documentation.

## 17. Delivery model

The normal business release promotes the same immutable domain Git SHA/config bundle/framework release DEV -> UAT -> PROD while environment-local runtime state remains local.

The certification input producer additionally creates an exact temporary release identity for the isolated certification project. That identity is consumed only by framework evidence workflows and does not change the normal Customer production release package.

Secrets and raw credentials never belong in Git or `business-path-inputs-<customer SHA>`.

## 18. Project bootstrap model

For Framework v0.4+ the intended new-domain flow remains:

```text
install immutable framework wheel
  -> fabric-framework project-init
  -> source inventory
  -> DatasetConfig + semantic selections
  -> fabric-framework project-validate
  -> domain tests
  -> GitHub PR/CI
  -> immutable release artifacts
  -> Fabric DEV integration
  -> UAT
  -> PROD promotion
```

The release-certification flow is separate and documented in `docs/runbooks/CERTIFY_FRAMEWORK_0_4.md`.

## 19. Release-certification order

```text
merge customer input contract
-> replace deliberate external placeholders with reviewed real inputs
-> package exact customer inputs for exact framework candidate
-> only then freeze/select one framework candidate
-> real framework candidate-integration-evidence
-> five live framework business-path gates
-> complete release proofs
-> candidate certification blockers=[]
-> exact-byte framework promotion
-> immutable v0.4.0
-> Customer production dependency migration
```

The existence of a customer input artifact alone is not permission to freeze or release a framework candidate.

## 20. Documentation obligation

Every coherent domain implementation cross-checks:

```text
README.md
docs/PROJECT_BLUEPRINT.md
docs/CURRENT_STATUS.md
docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md
docs/runbooks/CERTIFY_FRAMEWORK_0_4.md
examples/enterprise_100_table/README.md
```

The command examples, version pins, evidence labels and ownership boundaries must agree before merge.
