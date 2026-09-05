# fabric-customer

Reference Customer/domain repository for the Enterprise Microsoft Fabric Data Engineering Platform.

This repo owns Customer-specific WHAT: DatasetConfig, semantic capture selections, mappings, business DQ rules, execution-group choices, fixtures, non-secret deployment bindings, tests and certification inputs. Generic HOW remains in `fabric-data-framework`.

## Framework lanes

The **production/release dependency remains immutable**:

```text
fabric-data-framework==0.3.0
```

`pyproject.toml`, released-wheel CI and Customer release packaging continue to use published v0.3.0. Do not replace this with Framework `main` before immutable v0.4.0 exists and migration is explicitly approved.

The historical **framework-next project-contract lane** remains pinned to:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

It proves `project-init` / `project-validate` compatibility for the normal Customer project and the 100-table Health fixture. It is static compatibility evidence only.

The separate **0.4 certification-contract lane** now tracks Framework PR #107 / current substantive main baseline:

```text
4c8ad9994f3800e901c146b919f85454d78f080e
```

That baseline adds product-level parent-Pipeline fault isolation, `FAIL_AT_END`, source-controlled execution-group policy, DQ/quarantine budgets, full quarantine payload retention and conservative recovery planning. The certification lane is still only a source/CI compatibility lane: it does not execute Fabric, create live PASS evidence, freeze a candidate, authorize release or change the v0.3.0 production dependency.

## Normal Customer runtime model

Current executable Customer vertical slice remains:

```text
crm.customer
  -> WATERMARK(modified_at, customer_id)
  -> normalized Bronze
  -> Customer DQ / row quarantine
  -> Customer mapping
  -> Framework SCD2
  -> reconciliation
  -> target + watermark/state commit sequencing
```

Project source of truth:

```text
fabric-project.json
config/datasets/crm.customer.json
config/capture/semantic-selections.json
```

A `project-validate` PASS is static project consistency, not live Fabric certification.

## 100-table enterprise onboarding reference

One domain repo intentionally contains mixed mechanisms:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT (Debezium/external CDC)
```

Repo boundaries follow ownership, security/compliance and release lifecycle, not FULL/WATERMARK/CDC or SCD1/SCD2 implementation choices. Operational grouping belongs in `orchestration.execution_group`.

The four operational groups are:

```text
health_full_refresh
health_scd2
health_scd1
health_debezium
```

The 10 Debezium rows explicitly model external CDC/checkpoint ownership. The 100-table fixture is onboarding/config scale proof, not a runtime performance benchmark.

## Product Pipeline operations reference

Start here for normal multi-table Pipeline design and incidents:

```text
examples/pipeline_development/README.md
docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md
```

The forward-looking Framework 0.4 examples include source-controlled execution-group policies for all four Health groups:

```text
examples/pipeline_development/framework_0_4/execution-groups/
  health_full_refresh.json
  health_scd2.json
  health_scd1.json
  health_debezium.json
```

They demonstrate the intended product behavior:

```text
one table FAIL
-> durable dataset error
-> independent siblings continue
-> failed dependents BLOCKED
-> all runnable work reaches terminal state
-> parent Pipeline FAILED at end
```

They also show Pipeline-level DQ/quarantine defaults plus per-table overrides. These files are **not production runtime inputs yet** because Customer production remains on Framework v0.3.0.

Recovery is intentionally conservative:

```text
explicit transient + retryable=true -> bounded RETRY
DQ threshold -> fix data/rule then REPLAY
reconciliation failure -> investigate before reprocess
blocked dependency -> recover upstream first
unknown commit -> reconcile before retry
bounded source gap -> BACKFILL
authoritative reset only -> FULL_REBUILD
```

Whole-Pipeline blind retry is not the default repair strategy.

## New domain bootstrap

Normal flow:

```text
fabric-framework project-init <repo> --domain <domain>
-> add DatasetConfig / semantic selections / domain rules
-> assign execution_group
-> fabric-framework project-validate <repo>
-> GitHub CI
-> approved DEV/UAT deployment
-> controlled operational validation
-> PROD promotion
```

When Framework v0.4.0 eventually becomes an approved production dependency, execution-group policy belongs in the same source-controlled release identity rather than being silently edited in the Fabric UI.

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

The bundle includes `INPUTS.json`, `release-manifest.json`, `runner-config.json`, exact certification project files and the extension wheel. This is an **input artifact**, not integration evidence or release readiness proof.

Framework candidate wheel identity and Customer/domain release identity remain separate and must never be assumed equal.

## Current live blockers

Source intentionally remains fail-closed:

```text
control_plane_external_evidence_incomplete
warehouse_real_fault_controller_not_configured
```

Replace these only with reviewed real enterprise evidence and an approved real provider/session fault controller. Never manufacture synthetic PASS JSON.

No selected/frozen Framework 0.4 candidate exists, no strict live evidence bundle is complete, and release is not authorized.

## CI proof model

```text
source-metadata-and-wheel
  -> source validation + Customer wheel

exact-framework-integration
  -> immutable Framework v0.3.0 + Customer tests + release/deployment plan

framework-next-project-contract
  -> exact historical project-contract SHA + project-validate + 100-table static proof

customer-certification-contract
  -> exact Framework PR #107 source compatibility
  -> validates 0.4 execution-group policy examples
  -> builds typed certification inputs
  -> asserts real-environment blockers remain fail-closed
```

These lanes are deliberately separate. None of the development lanes upgrades the production runtime dependency.

## Structure / start here

- `docs/CURRENT_STATUS.md` — exact current engineering/evidence checkpoint.
- `docs/PROJECT_BLUEPRINT.md` — repository ownership and architecture.
- `docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md` — create and validate a new domain.
- `docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md` — normal multi-table Pipeline operations and repair.
- `docs/runbooks/CERTIFY_FRAMEWORK_0_4.md` — exact 0.4 certification preparation.
- `examples/enterprise_100_table/README.md` — 100-table onboarding reference.
- `examples/pipeline_development/README.md` — production-oriented Pipeline grouping/policy examples.

Framework owns HOW. Domain repositories own WHAT.
