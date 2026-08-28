# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer WATERMARK/SCD2 vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **IMPLEMENTED ON PR #6; MIGRATED TO PUBLIC-REPOSITORY GITHUB-HOSTED CI; WAITING FOR IMMUTABLE FRAMEWORK `v0.3.0` AND EXACT INTEGRATION PASS**.

## Last completed step

Both `fabric-customer` and `fabric-data-framework` are now public repositories. Customer CI/release workflows on PR #6 have been simplified accordingly:

- runner changed from `self-hosted` to GitHub-hosted `ubuntu-latest`;
- `FRAMEWORK_REPO_TOKEN` removed;
- private-repository skip logic removed;
- exact framework integration now always checks out public `ruizengalways/fabric-data-framework` at exact tag `v0.3.0`;
- Customer release downloads the exact public framework `v0.3.0` wheel using the workflow's normal GitHub token.

This removes the previous false-green mode where the integration job succeeded while all real cross-package steps were skipped.

## Phase 3 Customer content

- exact framework dependency `fabric-data-framework==0.3.0`;
- source metadata validator that rejects physical Fabric IDs in semantic dataset definitions;
- DEV/UAT/PROD environment binding profiles separated from semantic metadata;
- Customer source-contract CI and wheel build;
- exact framework integration test job;
- tag-triggered Customer release workflow;
- release-manifest and same-release DEV/UAT/PROD deployment-plan contract tests.

## Historical runner validation

Before the repositories were made public, Customer run `33137660655` proved both Customer jobs could execute on the self-hosted runner named `Bear`, and the complete source-contract job passed. The exact-framework integration steps were skipped because the old private-repository token gate was absent.

That Bear-specific topology is no longer part of the active design. GitHub-hosted runners are now the default for this public reference implementation.

## Exact framework integration state

The exact integration job no longer has an optional credential gate. It now requires the immutable framework tag `v0.3.0` to exist and then performs:

```text
Checkout Customer
Checkout fabric-data-framework @ v0.3.0
Install exact framework + Customer
Run cross-package tests
Build release manifest
Validate DEV/UAT/PROD deployment plans
```

Because framework `v0.3.0` has not yet been published, this remains the truthful blocking gate for merging Customer Phase 3.

## Environment promotion proof

`deploy/bindings.dev.json`, `bindings.uat.json` and `bindings.prod.json` contain non-secret reference environment bindings only. They are outside the semantic release hash. The same immutable Customer release identity is combined with different environment bindings for DEV/UAT/PROD, while runtime state such as watermarks, leases, run history, quarantine/reprocess records and runtime overrides remains environment-local.

## Validation summary

Previously completed local validation:

- Customer `pytest -q`: **4 passed** against framework `0.3.0` source;
- metadata validator: PASS;
- compile: PASS;
- Customer wheel build: PASS;
- workflow YAML parse: PASS.

Historical remote validation:

- Customer source-contract job on Bear: PASS;
- exact immutable framework integration: not yet proven.

Current public/GitHub-hosted workflow validation must complete on the latest PR #6 head.

## Merge/release state

Customer Phase 3 PR #6 remains **OPEN**.

It must not merge until:

1. framework `v0.3.0` immutable tag/release exists;
2. GitHub-hosted Customer source-contract CI passes;
3. exact framework integration executes all steps and passes.

No Customer production release has been created.

## Known limitations / blockers

- Immutable framework `v0.3.0` GitHub Release is pending.
- No real Fabric workspace deployment has executed.
- Checked-in bindings are reference values, not company resource IDs.
- No Fabric Pipeline/Notebook item exists yet.
- No actual DEV/UAT/PROD control-plane store is bound.
- No multi-dataset Customer dispatcher scenario yet.
- No snapshot/CDC representative scenario yet.

## Exact next implementation sequence

1. Publish/prove framework `v0.3.0` on GitHub-hosted Actions.
2. Let Customer PR #6 exact framework integration run fully and pass, then merge it.
3. Add a tiny multi-dataset Customer graph for dispatcher/failure-isolation testing.
4. Add representative snapshot and CDC datasets only when the generic framework strategies exist.
5. Add real Fabric Notebook/Pipeline items when the runtime adapter is ready.

Do not add dozens of fake tables. A small representative graph should prove the reusable platform behaviour.
