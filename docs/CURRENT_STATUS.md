# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer WATERMARK/SCD2 vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **COMPLETE ON PR #6; RELEASED-WHEEL INTEGRATION VALIDATED**.

## Last completed step

Framework `v0.3.0` was published from GitHub Actions and Customer PR #6 was revalidated against the actual release artifact rather than framework source.

The exact framework gate now proves the immutable artifact path end to end:

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

Customer run `33143386148` was rerun after the release became available. Both jobs completed successfully:

```text
source-metadata-and-wheel     SUCCESS
exact-framework-integration   SUCCESS
```

Within the exact integration job, framework wheel download/checksum verification, exact installation, cross-package tests and release-manifest/deployment-plan validation all passed.

## Phase 3 Customer content

- exact dependency declaration `fabric-data-framework==0.3.0`;
- source metadata validator rejecting physical Fabric IDs in semantic dataset definitions;
- DEV/UAT/PROD environment binding profiles separated from semantic metadata;
- Customer source-contract CI and wheel build;
- exact released-framework-wheel integration job;
- tag-triggered Customer release workflow;
- framework release SHA-256 verification before installation;
- release-manifest and same-release DEV/UAT/PROD deployment-plan contract tests.

## Environment promotion proof

`deploy/bindings.dev.json`, `bindings.uat.json` and `bindings.prod.json` contain non-secret reference environment bindings only. They are outside the semantic release hash. The same immutable Customer release identity is combined with different environment bindings for DEV/UAT/PROD, while runtime state such as watermarks, leases, run history, quarantine/reprocess records and runtime overrides remains environment-local.

## Validation summary

Current remote validation:

- Framework GitHub Release `v0.3.0`: **PUBLISHED**;
- framework wheel asset: **PUBLISHED**;
- framework `SHA256SUMS`: **PUBLISHED**;
- Customer source-contract job: **PASS**;
- exact immutable framework released-wheel download/checksum verification: **PASS**;
- exact framework installation: **PASS**;
- Customer cross-package tests: **PASS**;
- release manifest and DEV/UAT/PROD deployment-plan validation: **PASS**.

## Merge/release state

Customer Phase 3 PR #6 is ready for final CI and squash merge.

No Customer production release has been created. This PR establishes the delivery contract; a formal Customer release should be created only when a coherent domain deployment candidate is intentionally frozen for promotion.

## Known limitations / blockers

- No real Fabric workspace deployment has executed.
- Checked-in bindings are reference values, not company resource IDs.
- No Fabric Pipeline/Notebook item exists yet.
- No actual DEV/UAT/PROD control-plane store is bound.
- No multi-dataset Customer dispatcher scenario yet; Framework PR #9 contains the generic 0.4.0 dispatcher candidate.
- No snapshot/CDC representative scenario yet.

## Exact next implementation sequence

1. Finalize and squash merge Customer PR #6.
2. Rebase/revalidate and merge Framework 0.4.0 dispatcher PR #9 now that the 0.3.0 release boundary is frozen.
3. Add a tiny multi-dataset Customer graph for dispatcher/failure-isolation testing.
4. Continue with retry/backfill/replay.
5. Add representative SNAPSHOT_DIFF and CDC/UPSERT scenarios.
6. Add delete/late-arrival/schema-evolution correctness policies.
7. Add real Fabric Environment/Notebook/Pipeline deployment integration.

Do not add dozens of fake tables. A small representative graph should prove the reusable platform behaviour.
