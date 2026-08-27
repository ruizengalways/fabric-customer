# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

Phase 0 — Canonical architecture and repository boundaries: **COMPLETE**.

## Last completed step

Established Customer-domain ownership, immutable framework dependency policy, same-SHA promotion policy, planned first vertical slice and recoverable project status documentation.

## Current implementation

Documentation-only domain foundation. No Customer dataset config, transformation, Fabric item, fixture or test code has been implemented yet.

## Important decisions made

- Customer owns domain-specific configuration, transformations, canonical model, DQ/reconciliation rules and domain-owned Fabric items/tests.
- Generic runtime behaviours are consumed from `fabric-data-framework`, not copied.
- Customer pins an exact released framework version and upgrades it explicitly through PR/CI.
- Physical Fabric resources are resolved through the shared infrastructure contract.
- Customer deployments promote the same immutable Git SHA through environments.
- The first implementation will be one CRM Customer WATERMARK -> Bronze -> SCD2 -> Silver vertical slice.

## Files/components implemented

- `README.md`
- `docs/PROJECT_BLUEPRINT.md`
- `docs/CURRENT_STATUS.md`
- `docs/adr/0001-versioned-framework-dependency.md`
- `docs/adr/0002-git-sha-environment-promotion.md`
- `docs/runbooks/README.md`

## Tests executed

Phase 0 documentation validation only:

- confirmed the repo previously contained only its initial README/commit;
- checked that Customer does not claim ownership of framework algorithms or infrastructure;
- checked that the first planned domain slice depends on framework contracts rather than defining competing generic implementations.

## Test results

PASS — Customer Phase 0 boundaries are documented and no premature runtime implementation exists.

## Known limitations

- No pinned framework package exists yet because no framework release exists.
- No dataset configuration, fixtures or Fabric items exist yet.
- No domain CI/integration/smoke execution exists yet.

## Open issues/blockers

Customer runtime implementation is intentionally sequenced after the minimal framework configuration/runtime contracts exist. This is a roadmap dependency, not an architecture blocker.

## Last known-good release / commit

No Customer application release exists yet. Phase 0 is documentation-only.

## Exact next implementation step

Do not start Customer runtime code yet. The ecosystem's next step is `fabric-data-framework` Phase 1 / Step 1 (package + typed configuration/infrastructure contract foundation).

After that framework contract exists and is tested, the Customer repo's next step is to add the single `crm.customer` dataset configuration plus tiny fixtures for the WATERMARK/SCD2 vertical slice, consuming the framework types rather than redefining them.
