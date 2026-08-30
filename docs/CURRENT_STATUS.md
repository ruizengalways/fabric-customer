# Current Status — fabric-customer

Last updated: 2026-08-30

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer WATERMARK/SCD2 vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **COMPLETE AND MERGED**.
- Enterprise bulk-onboarding/domain-bootstrap reference: **IMPLEMENTED AS CONFIG/CI/RUNBOOK PROOF**.
- Next runtime domain slice — multi-dataset dispatcher/failure isolation: **BLOCKED ONLY ON IMMUTABLE FRAMEWORK `v0.4.0` RELEASE**.

## Released runtime baseline

Customer currently exact-pins:

```text
fabric-data-framework==0.3.0
```

Framework source on `main` has advanced to source version `0.4.0`, but immutable GitHub Release `v0.4.0` is still pending. Customer must not switch to Framework `main` or an unpublished branch.

## Proven v0.3.0 delivery path

Customer Phase 3 was validated against the published Framework `v0.3.0` wheel.

The exact integration path proved:

```text
GitHub Release v0.3.0
  -> download fabric_data_framework-0.3.0-py3-none-any.whl
  -> download SHA256SUMS
  -> sha256sum -c SHA256SUMS
  -> install released wheel
  -> install Customer
  -> cross-package tests
  -> release manifest
  -> DEV/UAT/PROD deployment-plan validation
```

Current delivery content includes:

- exact framework dependency and released-wheel integration;
- source metadata validator rejecting physical Fabric IDs in semantic dataset definitions;
- DEV/UAT/PROD environment binding profiles separated from semantic metadata;
- Customer source-contract CI and wheel build;
- tag-triggered Customer release workflow;
- framework release SHA-256 verification before installation;
- release-manifest and same-release DEV/UAT/PROD deployment-plan contract tests.

## Enterprise 100-table onboarding proof

The repo now contains a scale fixture and deterministic scaffold path for the realistic new-project scenario:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT (Debezium example)
```

Artifacts:

```text
examples/enterprise_100_table/health_100_tables.csv
scripts/scaffold_from_manifest.py
tests/test_bulk_onboarding.py
docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md
```

The scaffold supports a non-mutating local dry-run and explicit `--write` generation of framework `DatasetConfig` JSON files. CI validates the 100-row manifest without requiring framework dependencies; the cross-package test then generates all 100 configs and validates them against the exact released framework v0.3.0 schema.

This is deliberately a **configuration/onboarding scale proof**, not 100 fake runtime integrations. The repository still uses small representative runtime fixtures to prove algorithms and failure semantics.

## Repository boundary rule

```text
Framework owns HOW.
Domain repo owns WHAT.
```

Do not split a domain repository merely because some datasets use FULL, WATERMARK, CDC, SCD1 or SCD2. Split only for a real ownership, security/compliance, data-product or independent release boundary.

## Environment promotion proof

`deploy/bindings.dev.json`, `bindings.uat.json` and `bindings.prod.json` contain non-secret reference environment bindings only. They are outside the semantic release hash. The same immutable Customer release identity is combined with different environment bindings for DEV/UAT/PROD, while runtime state such as watermarks, leases, run history, quarantine/reprocess records and runtime overrides remains environment-local.

## Current external boundary

- No real Fabric workspace deployment has executed.
- Checked-in bindings are reference values, not company resource IDs.
- No Fabric Pipeline/Notebook item exists yet.
- No actual DEV/UAT/PROD control-plane store is bound.
- No Customer production release has been created.
- The Debezium rows in the 100-table fixture express onboarding semantics; they are not proof of a live Debezium-to-Fabric integration.

`docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md` now defines the step-by-step procedure for performing the real jumpbox -> GitHub -> Fabric DEV -> TEST -> PROD proof without overstating current evidence.

## Exact next implementation sequence

1. Publish/prove Framework `v0.4.0` through the existing GitHub Actions UI release workflow.
2. Upgrade Customer exact framework pin/integration to `0.4.0`.
3. Add the smallest representative Customer multi-dataset dispatcher/failure-isolation scenario.
4. Continue with retry/backfill/replay.
5. Add representative SNAPSHOT_DIFF and CDC/UPSERT runtime scenarios.
6. Add delete/late-arrival/schema-evolution correctness policies.
7. Execute real Fabric Environment/Notebook/Pipeline deployment integration following the runbook and retain evidence.
8. Ramp representative workload/concurrency before claiming 100-table production-scale support.

Do not add dozens of fake runtime tables. Use the bulk manifest for onboarding/config scale and small representative datasets for reusable runtime correctness proof.
