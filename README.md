# fabric-customer

Reference Customer domain for the Enterprise Microsoft Fabric Data Engineering Platform.

This repository owns Customer-specific source-controlled dataset metadata, semantic capture selections, mappings, business DQ rules, fixtures, domain tests, non-secret deployment bindings and bounded release-certification inputs. Generic capture/apply/control-plane/evidence algorithms remain in `fabric-data-framework`.

## Framework lanes

The **production/release dependency remains immutable**:

```text
fabric-data-framework==0.3.0
```

`pyproject.toml`, released-wheel CI and Customer release packaging continue to use published v0.3.0. Do not replace this with Framework `main` before immutable v0.4.0 exists.

The historical **framework-next project-contract lane** remains pinned to:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

It proves project-init/project-validate compatibility for the normal Customer project and 100-table Health fixture. It is static compatibility evidence only.

The separate **0.4 certification-contract lane** tracks the current feature-frozen Framework code baseline:

```text
abc8b3a2b80b3f6babf88fdc2347a3bfe69be356
```

That is Framework PR #94, the code baseline after exact customer/domain release-hash binding and removal of the obsolete unbound business-path proof path. The certification lane builds the bounded extension wheel and runs `certification/build_candidate_inputs.py` with non-live identities. It does not execute Fabric, create PASS evidence, freeze a candidate, or change the production v0.3.0 dependency.

## Current executable Customer slice

```text
crm.customer
  -> WATERMARK(modified_at, customer_id)
  -> normalized Bronze
  -> Customer DQ / row quarantine
  -> Customer mapping
  -> framework SCD2
  -> reconciliation
  -> target + watermark/state commit sequencing
```

Project source of truth:

```text
fabric-project.json
config/datasets/crm.customer.json
config/capture/semantic-selections.json
```

A framework-next `project-validate` PASS is static project consistency, not live Fabric certification.

## Enterprise 100-table onboarding reference

One domain repo intentionally contains mixed mechanisms:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT (Debezium)
```

Repo boundaries follow ownership/security/compliance/release lifecycle, not FULL/WATERMARK/CDC or SCD1/SCD2 implementation choices. Operational grouping belongs in `orchestration.execution_group`.

The 10 Debezium rows in framework-next mode explicitly select:

```text
EXTERNAL_CDC + debezium_kafka_v1 + EXTERNAL progress owner
```

This is onboarding/config scale proof, not a 100-table runtime benchmark.

## Exact Framework 0.4 certification inputs

Customer-owned certification source lives under:

```text
certification/project/
certification/extensions/
```

It contains representative FULL/REPLACE, WATERMARK/SCD1, WATERMARK/SCD2, retry/idempotency, reconciliation fail-closed, Copy, Spark and Warehouse inputs. Customer extensions provide bounded facts/mutations only; Framework remains the sole PASS authority.

Manual exact-input producer:

```text
.github/workflows/candidate-business-path-inputs.yml
```

It authenticates an exact successful Framework main-CI candidate run, verifies the retained candidate wheel bytes, builds the fingerprinted Customer certification extension wheel and uploads:

```text
business-path-inputs-<customer SHA>
```

The bundle includes `INPUTS.json`, `release-manifest.json`, `runner-config.json`, exact certification project files and the extension wheel. This is an **input artifact**, not integration evidence or release readiness proof.

The two exact release identities remain independent:

```text
framework candidate wheel SHA256
!=
customer ReleaseManifest.bundle.release_hash
```

Framework evidence workflows independently verify both.

## Current live blockers

Source intentionally remains fail-closed:

```text
control_plane_external_evidence_incomplete
warehouse_real_fault_controller_not_configured
```

Concretely:

```text
control-plane external evidence references = null
Warehouse real fault controller = example.invalid
```

Replace them only with reviewed real enterprise evidence references and an approved real provider/session fault-controller endpoint. Never replace them with synthetic PASS JSON just to make certification green.

No selected/frozen Framework candidate exists, no selected-candidate Customer input artifact is retained, no certified integration artifact exists, and no five-gate live business-path artifact exists.

## CI proof model

```text
source-metadata-and-wheel
  -> source validation + Customer wheel

exact-framework-integration
  -> immutable v0.3.0 wheel/checksum + Customer tests + release/deployment plan

framework-next-project-contract
  -> exact historical project-contract SHA + project-validate + 100-table static proof

customer-certification-contract
  -> exact current Framework PR #94 code SHA + typed certification input build
  -> asserts current real-environment blockers remain fail-closed
```

These proof classes are deliberately separate. None of the development lanes upgrades the production runtime dependency.

## Structure / start here

- `docs/CURRENT_STATUS.md` — exact current engineering/evidence state and next work.
- `docs/PROJECT_BLUEPRINT.md` — repository ownership and architecture.
- `docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md` — how to start and validate a real new domain.
- `docs/runbooks/CERTIFY_FRAMEWORK_0_4.md` — exact 0.4 customer input and live-environment certification preparation.
- `examples/enterprise_100_table/README.md` — 100-table onboarding reference.

Framework owns HOW. Domain repositories own WHAT.
