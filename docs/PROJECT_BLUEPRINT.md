# fabric-customer — Project Blueprint

Status: Canonical
Last updated: 2026-08-30

## 1. Goal

Provide a realistic Customer-domain reference proving a domain can consume reusable `fabric-data-framework` behavior without copying generic capture/apply/control-plane algorithms, and provide a production-oriented repository pattern for large enterprise onboarding.

## 2. Ownership

Customer/domain repo owns WHAT:

- source-controlled domain DatasetConfig values;
- source/capture semantic selections and known limitations;
- source parsing/mapping and canonical domain shapes;
- business-specific DQ/reconciliation rule definitions;
- domain fixtures/integration/smoke tests;
- domain-owned Fabric items when introduced;
- execution grouping and non-secret environment bindings.

Framework owns HOW:

- DatasetConfig schema and capability validation;
- generic capture/runtime contracts;
- Bronze normalization and quarantine execution semantics;
- reusable SCD/apply algorithms;
- reconciliation/state/checkpoint rules;
- runtime audit and deployment/control-plane contracts;
- reusable Fabric adapters;
- project-init/project-validate tooling.

No generic capture/SCD/project validation algorithm should be copied into this repo.

## 3. Current Customer project source of truth

```text
fabric-project.json
config/datasets/crm.customer.json
config/capture/semantic-selections.json
```

`crm.customer` declares WATERMARK capture on `modified_at` with `customer_id` tie-breaker, SCD2 apply, Customer business keys, DQ/reconciliation policy references and execution group `crm_daily`.

The semantic selection explicitly records that hard deletes are not observable without a delete signal and that SCD2 history cannot exceed the changes observed by the watermark path.

DEV/UAT/PROD materialize the same released semantic definition while keeping independent runtime state.

## 4. Domain code

`src/fabric_customer/domain.py` contains only Customer-specific behavior:

- parse source timestamps;
- normalize Customer strings/casing;
- Customer mapping;
- email-format DQ;
- segment-domain DQ.

No watermark, SCD2, capability-selection or project-validation algorithm lives here.

## 5. Small runtime correctness fixture

The CRM fixtures remain intentionally small. They prove domain/runtime behavior such as:

- deterministic watermark tie-breaker ordering;
- quarantine lineage;
- SCD2 change detection;
- unchanged-row idempotency;
- reconciliation-gated target/watermark commit;
- rerun behavior.

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

`scripts/scaffold_from_manifest.py` has two deliberate modes:

```text
default
  -> released v0.3-compatible DatasetConfig generation

--framework-next
  -> exact pinned 0.4-development project-contract generation
  -> semantic selections
  -> explicit Debezium execution capability profile
```

The framework-next Health proof uses framework-owned `project-init` and `project-validate` around the generated project instead of inventing a second project validator in Customer.

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

## 8. Dependency model

Production/release dependency:

```text
fabric-data-framework==0.3.0
```

The released integration lane downloads the v0.3.0 wheel and checksum and never substitutes Framework `main`.

Compatibility-only framework-next baseline:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

CI checks out that exact SHA separately and uses it only to run static project-contract validation. It is not a public release dependency.

The project-contract adoption was merged through Customer PR #8 at:

```text
Customer merge SHA: d05f06d3a2f8d9e31f4c7d9459c8e55df44460ff
validation workflow: 33308362061
```

The validation passed the source/wheel lane, immutable v0.3.0 integration lane, and exact framework-next project-contract lane. The released lane recorded 8 Customer tests passing; the framework-next lane validated the Customer root and the generated 100-dataset Health project.

When v0.4.0 is published, the Customer runtime/package import migration must happen in a single reviewed PR; do not create permanent dual-runtime compatibility code without a demonstrated need.

## 9. Current repo shape

```text
fabric-customer/
  fabric-project.json
  pyproject.toml
  config/
    datasets/
      crm.customer.json
    capture/
      semantic-selections.json
  examples/
    enterprise_100_table/
      health_100_tables.csv
      README.md
  scripts/
    scaffold_from_manifest.py
    validate_metadata.py
    validate_docs.py
  src/fabric_customer/
  tests/
  deploy/
    bindings.dev.json
    bindings.uat.json
    bindings.prod.json
  docs/
    PROJECT_BLUEPRINT.md
    CURRENT_STATUS.md
    runbooks/
      BUILD_NEW_DOMAIN_PROJECT.md
```

The project manifest intentionally points `environment_binding_dir` to the existing `deploy/` directory so adoption does not create a duplicate binding source of truth. New repositories created directly by framework `project-init` use the framework default layout.

## 10. CI proof model

Three proof lanes must remain distinct:

```text
source-metadata-and-wheel
  source-only validation + canonical documentation consistency + Customer wheel build

exact-framework-integration
  immutable v0.3.0 release integration + Customer tests + release/deployment plans

framework-next-project-contract
  exact pinned 0.4-development SHA + Customer project-validate + 100-table Health project-validate
```

PR #8 proved all three lanes can pass together without replacing the released dependency.

A PASS in one lane does not automatically imply another proof class.

## 11. Documentation consistency contract

`scripts/validate_docs.py` is a source CI gate. It derives:

- the exact released framework dependency from `pyproject.toml`;
- the exact framework-next SHA from `.github/workflows/ci.yml`.

It checks the canonical documentation set for consistent version/SHA references, project-init/project-validate guidance, Debezium/100-table terminology and required project source-of-truth files.

This turns documentation synchronization into an executable contract while preserving human review for semantic accuracy.

## 12. Proof taxonomy

```text
manifest/config scale proof
!=
runtime correctness proof
!=
released dependency proof
!=
real Fabric provider integration proof
!=
capacity/performance proof
```

This distinction is non-negotiable in code comments, PR descriptions and documentation.

## 13. Delivery model

The same immutable domain Git SHA/config bundle/framework release moves DEV -> UAT/TEST -> PROD. Environment-local runtime state is not promoted.

`deploy/bindings.*.json` resolves non-secret physical bindings outside semantic DatasetConfig truth. Secrets and raw credentials never belong in Git.

## 14. Project bootstrap model

For Framework v0.4+ the intended new-domain flow is:

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
  -> TEST/UAT
  -> PROD promotion
```

Until v0.4.0 is immutable, Customer CI exercises this flow only against the exact pinned framework-next SHA while the production lane stays on v0.3.0.

## 15. Roadmap status

- Phase 0 — COMPLETE: canonical architecture.
- Phase 1 — COMPLETE dependency: framework foundation.
- Phase 2 — COMPLETE: `crm.customer` executable vertical slice.
- Phase 3 — COMPLETE: CI/package/release/deployment spine.
- Enterprise bulk onboarding — COMPLETE as config/CI/runbook proof.
- Framework-next project contract — COMPLETE AND MERGED through PR #8.
- Next gate — immutable Framework v0.4.0 release and exact Customer dependency/import migration.
- After that — add the smallest representative multi-dataset dispatcher/failure-isolation graph.
- Later — retry/backfill/replay, representative CDC/UPSERT/SNAPSHOT_DIFF, delete/late-arrival/schema-evolution policies, real Fabric evidence and controlled capacity ramp.

## 16. Documentation obligation

Every coherent domain implementation updates and cross-checks:

```text
README.md
docs/PROJECT_BLUEPRINT.md
docs/CURRENT_STATUS.md
docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md
examples/enterprise_100_table/README.md
```

The command examples, version pins, evidence labels and ownership boundaries must agree before merge.
