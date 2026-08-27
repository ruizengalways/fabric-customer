# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

Phase 0 — Canonical architecture and repository boundaries: **COMPLETE**.

Customer runtime implementation: **WAITING FOR FRAMEWORK PHASE 1 FOUNDATION**.

## Last completed step

Aligned the Customer domain blueprint with the metadata-driven framework design: source-controlled per-dataset semantics, deployed config provenance, multi-table dispatcher consumption, failure isolation, domain DQ/quarantine/reconciliation ownership and production audit expectations.

## Current implementation

Documentation-only domain foundation. No Customer dataset config, transformation, Fabric item, fixture or test code has been implemented yet.

## Important decisions made

- Customer owns domain-specific configuration, transformations, canonical model, DQ/reconciliation rules and domain-owned Fabric items/tests.
- Generic runtime behaviours are consumed from `fabric-data-framework`, not copied.
- Customer dataset semantics will be metadata-driven through the framework-owned config schema.
- Dataset metadata will declare business/merge keys, watermark/event-time/tie-breaker fields, capture/apply strategy, execution group, criticality, DQ/quarantine policy and reconciliation policy where applicable.
- Semantic metadata is source-controlled and deployed with config hash/Customer Git SHA; runtime operational overrides do not replace Git as semantic source of truth.
- Tens of Customer datasets should use a small number of generic execution-group dispatchers rather than one bespoke pipeline per table.
- A failed independent dataset must not immediately terminate unrelated Customer datasets; framework aggregate policy determines final `SUCCESS`, `PARTIAL_SUCCESS` or `FAILED`.
- Customer owns criticality/dependency declarations; framework owns generic failure-isolation semantics.
- Customer pins an exact released framework version and upgrades it explicitly through PR/CI.
- Physical Fabric resources are resolved through the shared infrastructure contract.
- Customer deployments promote the same immutable Git SHA through environments.
- The first implementation remains one CRM Customer WATERMARK -> Bronze -> validation/quarantine -> SCD2 -> reconciliation -> Silver/state-commit vertical slice.
- Routine implementation inside accepted architecture should proceed in coherent chunks rather than stopping after every tiny class/file.

## Files/components implemented

Documentation only:

- `README.md`
- `docs/PROJECT_BLUEPRINT.md`
- `docs/CURRENT_STATUS.md`
- `docs/adr/0001-versioned-framework-dependency.md`
- `docs/adr/0002-git-sha-environment-promotion.md`
- `docs/runbooks/README.md`

## Tests/checks executed

Architecture/documentation validation only:

- verified Customer does not claim ownership of generic metadata orchestration, audit, quarantine or state engines;
- verified domain metadata values can express merge/business keys, watermark/tie-breaker, event time, criticality and policy references;
- verified future multi-table Customer orchestration uses framework dispatch/failure isolation rather than bespoke per-table pipelines;
- verified the first vertical slice includes audit/quarantine/reconciliation/state correctness expectations without prematurely implementing them.

## Test results

PASS — Customer architecture is aligned with the expanded framework design. No runtime code exists yet.

## Known limitations

- No pinned framework package exists yet because no framework release exists.
- No dataset configuration, fixtures or Fabric items exist yet.
- No domain CI/integration/smoke execution exists yet.
- No deployed metadata/control-plane records exist yet.

## Open issues/blockers

Customer runtime implementation is intentionally sequenced after the coherent framework Phase 1 foundation exists. This is a roadmap dependency, not an architecture blocker.

## Last known-good release / commit

No Customer application release exists yet. Current state is documentation-only.

## Exact next implementation step

Do not start Customer runtime code yet.

The ecosystem's next step is the `fabric-data-framework` Phase 1 coherent foundation slice covering typed metadata, effective operational overrides, runtime/audit/quarantine/reconciliation contracts, control-plane schema foundations, infrastructure resolution and tests.

After that framework foundation exists and is tested, Customer Phase 2 should add the `crm.customer` source-controlled dataset definition and tiny fixtures/tests for the WATERMARK/SCD2 vertical slice, consuming framework types rather than redefining them.
