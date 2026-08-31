# fabric-customer

Reference Customer domain for the Enterprise Microsoft Fabric Data Engineering Platform.

This repository owns Customer-specific source-controlled dataset metadata, semantic capture selections, mappings, business DQ rules, fixtures, domain integration tests and non-secret deployment bindings. Generic capture selection, Bronze normalization, quarantine execution, SCD/apply algorithms, reconciliation, state semantics, capability validation and delivery contracts are consumed from `fabric-data-framework` rather than reimplemented.

## Two framework lanes

The production/release dependency remains immutable:

```text
fabric-data-framework==0.3.0
```

`pyproject.toml`, the released-wheel integration job and Customer release workflow continue to use the published v0.3.0 wheel and checksum. This branch does **not** replace that dependency with Framework `main`.

In parallel, CI has an exact-SHA **framework-next project-contract lane** pinned to:

```text
fabric-data-framework @ 148e02e3fff7861f238296e7554815a6fd49dd0a
```

That lane validates the source-controlled Customer project and the 100-table Health reference against the current 0.4-development `project-init` / `project-validate` contract. It is compatibility evidence for an exact source SHA, not an immutable public release and not production Fabric evidence.

A separate **0.4 certification-contract lane** validates the exact customer evidence-input schema against framework SHA:

```text
689bc1097474b26866af8675e32592e4cf65fa1f
```

That lane builds the bounded certification extension wheel and runs `certification/build_candidate_inputs.py` with non-live test identities. It proves typed input compatibility only. It does not execute Fabric, does not change the v0.3.0 runtime dependency, and does not create PASS evidence.

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

The repository now also declares the project-level semantic source of truth:

```text
fabric-project.json
config/datasets/crm.customer.json
config/capture/semantic-selections.json
```

Under the exact framework-next lane, this is checked with:

```bash
fabric-framework project-validate .
```

A PASS means the source-controlled project is internally valid: DatasetConfig parsing, dependency graph, capture/apply capability compatibility, semantic-selection coverage and semantic overclaim checks passed. It does **not** mean a live Fabric deployment is certified.

## Enterprise project bootstrap / 100-table onboarding

The repo acts as the reference shape for a new domain such as `fabric-health`.

The checked-in scale fixture demonstrates one repo onboarding 100 mixed datasets:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT (Debezium)
```

Released v0.3-compatible manifest dry run:

```bash
python scripts/scaffold_from_manifest.py \
  --manifest examples/enterprise_100_table/health_100_tables.csv \
  --output build/health-preview \
  --expect-count 100
```

Exact framework-next project proof:

```bash
fabric-framework project-init build/health-project --domain health

python scripts/scaffold_from_manifest.py \
  --manifest examples/enterprise_100_table/health_100_tables.csv \
  --output build/health-project/config/datasets \
  --expect-count 100 \
  --framework-next \
  --semantic-selections-output build/health-project/config/capture/semantic-selections.json \
  --write

fabric-framework project-validate build/health-project \
  --output build/health-project-validation.json
```

In framework-next mode the 10 declared Debezium datasets explicitly emit:

```text
EXTERNAL_CDC + debezium_kafka_v1 + EXTERNAL progress owner
```

and all 100 datasets receive semantic selections. This closes the previous gap where the CSV said “Debezium” but generated metadata only said generic `CDC`.

## Exact Framework 0.4 certification inputs

Framework release certification needs customer-owned WHAT without letting this repo decide PASS. The isolated certification slice is under:

```text
certification/project/
certification/extensions/
```

It contains representative FULL/REPLACE, WATERMARK/SCD1, WATERMARK/SCD2, retry/idempotency, reconciliation fail-closed, Copy, Spark and Warehouse recipes. The normal `crm.customer` project remains separate.

The manual producer is:

```text
.github/workflows/candidate-business-path-inputs.yml
```

It authenticates an exact successful framework `main` CI run, verifies the exact retained candidate wheel bytes, builds the fingerprinted customer certification extension wheel and uploads only:

```text
business-path-inputs-<customer SHA>
```

The bundle includes `release-manifest.json`, `runner-config.json`, the exact certification project, extension wheel and `INPUTS.json`. It is an input artifact, not provider evidence.

Current source intentionally remains **not live-ready**:

```text
control-plane external evidence references = null
Warehouse real fault controller = example.invalid
```

Those two blockers must be replaced by reviewed real enterprise inputs before a live certification attempt. See `docs/runbooks/CERTIFY_FRAMEWORK_0_4.md`.

## Repository rule

Framework owns HOW. Domain repositories own WHAT.

Do not create separate repos merely because datasets use FULL, WATERMARK, CDC, SCD1 or SCD2. Split only for a real ownership, security/compliance, data-product or independent release boundary. Operational batches belong in `orchestration.execution_group`.

## Structure

- `fabric-project.json` — framework project layout manifest for the Customer domain.
- `config/datasets/crm.customer.json` — current executable Customer dataset definition.
- `config/capture/semantic-selections.json` — source/capture/history semantic declaration.
- `certification/project/` — isolated customer-owned exact-release certification DatasetConfig/recipe/scenario inputs.
- `certification/extensions/` — bounded evidence observers/drivers/mutation adapters; no PASS authority.
- `.github/workflows/candidate-business-path-inputs.yml` — manual exact customer certification-input producer.
- `examples/enterprise_100_table/` — 100-dataset Health onboarding fixture.
- `scripts/scaffold_from_manifest.py` — deterministic intake-manifest validator/generator; default v0.3 output plus explicit framework-next mode.
- `src/fabric_customer/domain.py` — Customer mapping and DQ rules.
- `deploy/bindings.*.json` — non-secret reference environment binding profiles. The project manifest points `environment_binding_dir` here for backward-compatible adoption.
- `scripts/validate_metadata.py` — source-only v0.3 release-lane contract.
- `tests/fixtures/` — tiny deterministic CRM fixtures.
- `tests/` — domain integration, recovery, delivery-plan and bulk-onboarding contract tests.
- `docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md` — end-to-end jumpbox/CI/Fabric promotion runbook.
- `docs/runbooks/CERTIFY_FRAMEWORK_0_4.md` — exact customer input and live-certification preparation runbook.
- `docs/CURRENT_STATUS.md` — exact current engineering and evidence state.

## CI model

Customer CI has deliberately different proofs:

```text
source-metadata-and-wheel
  -> dependency-free source validation + Customer wheel build

exact-framework-integration
  -> published v0.3.0 wheel + checksum + Customer tests + release/deployment plan

framework-next-project-contract
  -> exact pinned project-contract SHA + project-validate + 100-table Health project proof

customer-certification-contract
  -> framework 689bc109... + typed certification input build + fail-closed live blockers
```

Do not collapse those labels. A framework-next static project PASS is not a released dependency, the certification-contract lane is not live evidence, and neither source lane upgrades the normal Customer runtime dependency.

## Start here

- `docs/PROJECT_BLUEPRINT.md` — repository ownership and architecture.
- `docs/CURRENT_STATUS.md` — exact current state and next work.
- `docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md` — how to start a real new domain, validate it, push it through GitHub and then prove it in Fabric.
- `docs/runbooks/CERTIFY_FRAMEWORK_0_4.md` — how to produce exact customer certification inputs and what must be real before framework live certification.
- `examples/enterprise_100_table/README.md` — exact 100-table reference commands.
