# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

Phase 0 — Canonical architecture and repository boundaries: **COMPLETE**.

Customer runtime implementation: **WAITING FOR FRAMEWORK PHASE 1 FOUNDATION**.

## Last completed step

Aligned the Customer domain with two cross-repository platform designs:

1. metadata-driven execution: source-controlled per-dataset semantics, deployed config provenance, multi-table dispatcher consumption, failure isolation, domain DQ/quarantine/reconciliation ownership and production audit expectations;
2. enterprise CI/CD: provider-neutral Git/Fabric promotion with isolated DEV/UAT/PROD control planes.

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
- Customer deployments promote the same immutable release identity/Git SHA through DEV -> UAT -> PROD.
- The delivery architecture must support Fabric workspace Git integration backed by GitHub or Azure DevOps and must also support Fabric Deployment Pipelines and external GitHub Actions/Azure Pipelines automation through a common deployment contract.
- DEV, UAT and PROD each have their own isolated Customer control-plane runtime state.
- Control-plane schema migrations and Customer semantic metadata definitions are promoted as release artifacts.
- Environment-specific workspace/resource/connection/secret bindings are resolved separately per stage.
- Runtime state is not promoted between environments: watermarks, dataset state/leases, run history, reconciliation results, quarantine execution state, runtime overrides and reprocess history remain environment-local.
- `deployment_history` is written independently in each stage and records the Customer Git SHA, framework version and config bundle hash that reached that environment.
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

Cross-repository CI/CD and control-plane promotion details are canonical in `fabric-data-framework/docs/CICD_DESIGN.md` and ADR 0005.

## Tests/checks executed

Architecture/documentation validation only:

- verified Customer does not claim ownership of generic metadata orchestration, audit, quarantine, state engines or deployment-provider internals;
- verified domain metadata values can express merge/business keys, watermark/tie-breaker, event time, criticality and policy references;
- verified future multi-table Customer orchestration uses framework dispatch/failure isolation rather than bespoke per-table pipelines;
- verified the first vertical slice includes audit/quarantine/reconciliation/state correctness expectations without prematurely implementing them;
- verified CI/CD promotion preserves the same Customer release/config definitions while keeping environment runtime state isolated;
- verified no design requires DEV/UAT/PROD source branches or copying DEV control-table state into higher environments.

## Test results

PASS — Customer architecture is aligned with the expanded framework metadata-driven and enterprise CI/CD designs. No runtime code exists yet.

## Known limitations

- No pinned framework package exists yet because no framework release exists.
- No dataset configuration, fixtures or Fabric items exist yet.
- No domain CI/integration/smoke execution exists yet.
- No deployed metadata/control-plane records exist yet.
- No GitHub Actions/Fabric Deployment Pipeline release automation exists yet.

## Open issues/blockers

Customer runtime implementation is intentionally sequenced after the coherent framework Phase 1 foundation exists. This is a roadmap dependency, not an architecture blocker.

The exact enterprise CI/CD mechanism used in the initial company Fabric environment can be selected later without changing Customer runtime contracts.

## Last known-good release / commit

No Customer application release exists yet. Current state is documentation-only.

## Exact next implementation step

Do not start Customer runtime code yet.

The ecosystem's next step is the `fabric-data-framework` Phase 1 coherent foundation slice covering typed metadata, effective operational overrides, runtime/audit/quarantine/reconciliation contracts, control-plane schema foundations, infrastructure resolution, provider-neutral deployment/provenance contracts and tests.

After that framework foundation exists and is tested, Customer Phase 2 should add the `crm.customer` source-controlled dataset definition and tiny fixtures/tests for the WATERMARK/SCD2 vertical slice, consuming framework types rather than redefining them.

Full DEV/UAT/PROD CI/CD automation remains Phase 3, but the Customer release/config provenance established in Phase 1/2 must already be compatible with both Fabric-native and external GitHub/Azure deployment paths.
