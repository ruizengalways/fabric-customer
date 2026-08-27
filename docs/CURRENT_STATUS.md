# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

Phase 0 — Canonical architecture and repository boundaries: **COMPLETE**.

Framework Phase 1 dependency: **SATISFIED**.

Customer Phase 2 — `crm.customer` WATERMARK -> Bronze -> validation/quarantine -> SCD2 -> reconciliation -> Silver/state-commit vertical slice: **READY TO START**.

## Last completed step

The framework Phase 1 coherent foundation is now merged to `fabric-data-framework/main` at merge commit `24432cadfba8e9e08091fe22614450a812fd56f8` with source package version `0.1.0`.

That foundation provides the contracts Customer was waiting for:

- strict typed dataset/source/target/load/orchestration/DQ/reconciliation metadata;
- business/merge key and WATERMARK `(column, tie_breaker)` validation;
- audited operational overrides and immutable effective-config hashing;
- provider-neutral environment/resource resolution;
- runtime context and status aggregation contracts;
- watermark/state commit gates;
- audit/quarantine/reconciliation contracts;
- logical control-plane schema foundation;
- provider-neutral release/deployment provenance contracts.

Customer implementation can now begin without redefining framework-owned primitives.

## Current implementation

Documentation-only Customer domain foundation. No Customer dataset config, transformation, Fabric item, fixture or test code has been implemented yet.

## Important decisions made

- Customer owns domain-specific configuration, transformations, canonical model, DQ/reconciliation rules and domain-owned Fabric items/tests.
- Generic runtime behaviours are consumed from `fabric-data-framework`, not copied.
- Customer dataset semantics are metadata-driven through the framework-owned config schema.
- Dataset metadata declares business/merge keys, watermark/event-time/tie-breaker fields, capture/apply strategy, execution group, criticality, DQ/quarantine policy and reconciliation policy where applicable.
- Semantic metadata is source-controlled and deployed with config hash/Customer Git SHA; runtime operational overrides do not replace Git as semantic source of truth.
- Tens of Customer datasets should use a small number of generic execution-group dispatchers rather than one bespoke pipeline per table.
- A failed independent dataset must not immediately terminate unrelated Customer datasets; framework aggregate policy determines final `SUCCESS`, `PARTIAL_SUCCESS` or `FAILED`.
- Customer owns criticality/dependency declarations; framework owns generic failure-isolation semantics.
- Customer pins an exact released framework version and upgrades it explicitly through PR/CI. During local cross-repo Phase 2 development, the framework source under test may be referenced directly, but production delivery must use an immutable released version.
- Physical Fabric resources are resolved through the shared infrastructure contract.
- Customer deployments promote the same immutable release identity/Git SHA through DEV -> UAT -> PROD.
- DEV, UAT and PROD each have their own isolated Customer control-plane runtime state.
- Control-plane schema migrations and Customer semantic metadata definitions are promoted as release artifacts; watermarks/run history/runtime overrides/quarantine/reprocess state are not promoted.
- The first implementation is one CRM Customer vertical slice, not a broad strategy catalog.
- Routine implementation inside accepted architecture proceeds in coherent chunks rather than stopping after every tiny class/file.

## Files/components implemented

Documentation only:

- `README.md`
- `docs/PROJECT_BLUEPRINT.md`
- `docs/CURRENT_STATUS.md`
- `docs/adr/0001-versioned-framework-dependency.md`
- `docs/adr/0002-git-sha-environment-promotion.md`
- `docs/runbooks/README.md`

Cross-repository runtime/control-plane/CI-CD details remain canonical in `fabric-data-framework` docs and ADRs.

## Tests/checks executed

Customer still has no runtime code, so no Customer unit/integration suite has run yet.

Cross-repo dependency verification completed:

- `fabric-data-framework` Phase 1 package source exists and is merged;
- framework local validation reported 24 passing unit/contract tests plus package build checks;
- framework contracts now express the metadata, runtime-state, quarantine/reconciliation and deployment boundaries required by Customer Phase 2.

## Test results

PASS — framework dependency required to start Customer Phase 2 is satisfied.

## Known limitations

- No published immutable framework package release yet; source package version is `0.1.0`.
- No `crm.customer` metadata definition yet.
- No Customer fixture/mapping/DQ code yet.
- No Customer integration/smoke execution yet.
- No deployed metadata/control-plane records yet.
- No GitHub Actions/Fabric Deployment Pipeline release automation yet.

## Open issues/blockers

No architecture blocker for starting Phase 2.

The exact physical Fabric control-plane store and initial deployment mechanism remain deferred and do not block the local/integration vertical slice.

## Last known-good release / commit

Customer has no application release yet.

Framework foundation dependency: `fabric-data-framework` source package `0.1.0`, merge commit `24432cadfba8e9e08091fe22614450a812fd56f8`.

## Exact next implementation step

**Phase 2 — implement one coherent `crm.customer` vertical slice across `fabric-data-framework` and `fabric-customer`.**

Customer work:

1. add the source-controlled `crm.customer` dataset definition using framework models;
2. configure WATERMARK capture on `modified_at` with `customer_id` tie-breaker;
3. configure SCD2 with `customer_id` business/merge key and tracked Customer attributes;
4. add tiny deterministic CRM fixtures covering new, changed, unchanged, duplicate-timestamp and invalid rows;
5. add the Customer-specific mapping and DQ rule required by those fixtures;
6. consume framework validation/quarantine/SCD2/reconciliation/state semantics rather than reimplementing them;
7. add cross-repo integration tests and synchronize docs.

Framework work for the same slice is recorded in `fabric-data-framework/docs/CURRENT_STATUS.md`: local control-plane adapter, WATERMARK selection, Bronze normalization, reusable validation/quarantine primitives, deterministic SCD2 apply, reconciliation and atomic state commit.

Do not build the complete strategy catalog, full enterprise CI/CD automation or Terraform in Phase 2.