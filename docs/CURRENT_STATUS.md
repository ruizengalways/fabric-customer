# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer WATERMARK/SCD2 vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **COMPLETE AND MERGED**.
- Next domain slice — multi-dataset dispatcher/failure isolation: **BLOCKED ONLY ON IMMUTABLE FRAMEWORK `v0.4.0` RELEASE**.

## Last completed step

Customer Phase 3 PR #6 was fully validated against the published Framework `v0.3.0` wheel and squash-merged as commit `32f6cabc093541270b271ae37754ba8fe1e9544b`.

Final PR CI run `33157883463` passed both jobs:

```text
source-metadata-and-wheel     SUCCESS
exact-framework-integration   SUCCESS
```

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

## Current framework dependency

Customer currently exact-pins:

```text
fabric-data-framework==0.3.0
```

Framework Phase 4 dispatcher has now been merged to Framework `main` as source version `0.4.0`, but immutable GitHub Release `v0.4.0` is still pending.

Customer must not switch to Framework `main` or an unpublished branch. After `v0.4.0` is published, Customer will upgrade the exact pin to `0.4.0` and its CI will download/verify/install that released wheel before running the new dispatcher scenario.

## Phase 3 Customer content

- exact framework dependency and released-wheel integration;
- source metadata validator rejecting physical Fabric IDs in semantic dataset definitions;
- DEV/UAT/PROD environment binding profiles separated from semantic metadata;
- Customer source-contract CI and wheel build;
- tag-triggered Customer release workflow;
- framework release SHA-256 verification before installation;
- release-manifest and same-release DEV/UAT/PROD deployment-plan contract tests.

## Next domain proof

Once Framework `v0.4.0` exists, add the smallest representative Customer graph needed to prove generic orchestration behaviour. Do not add dozens of fake tables.

Target scenario:

```text
customer      SUCCESS
address       SUCCESS
contact       FAILED (non-critical)
preference    SUCCESS
Pipeline      PARTIAL_SUCCESS
```

And dependency isolation:

```text
customer FAILED
  -> customer_detail depends on customer -> BLOCKED
preference unrelated -> SUCCESS
```

The Customer repo should supply domain metadata/fixtures/executor resolution only. It must not reimplement dispatcher algorithms.

## Environment promotion proof

`deploy/bindings.dev.json`, `bindings.uat.json` and `bindings.prod.json` contain non-secret reference environment bindings only. They are outside the semantic release hash. The same immutable Customer release identity is combined with different environment bindings for DEV/UAT/PROD, while runtime state such as watermarks, leases, run history, quarantine/reprocess records and runtime overrides remains environment-local.

## Current external boundary

- No real Fabric workspace deployment has executed.
- Checked-in bindings are reference values, not company resource IDs.
- No Fabric Pipeline/Notebook item exists yet.
- No actual DEV/UAT/PROD control-plane store is bound.
- No Customer production release has been created.

## Exact next implementation sequence

1. Publish/prove Framework `v0.4.0` through the existing GitHub Actions UI release workflow.
2. Upgrade Customer exact framework pin/integration to `0.4.0`.
3. Add the tiny Customer multi-dataset dispatcher/failure-isolation scenario.
4. Continue with retry/backfill/replay.
5. Add representative SNAPSHOT_DIFF and CDC/UPSERT scenarios.
6. Add delete/late-arrival/schema-evolution correctness policies.
7. Add real Fabric Environment/Notebook/Pipeline deployment integration.

Do not add dozens of fake tables. A small representative graph should prove the reusable platform behaviour.
