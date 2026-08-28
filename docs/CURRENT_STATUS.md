# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer WATERMARK/SCD2 vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **IMPLEMENTED ON PR #6; GITHUB-HOSTED SOURCE CI PASSES; EXACT FRAMEWORK INTEGRATION CORRECTLY BLOCKED ON MISSING `v0.3.0` TAG/RELEASE**.

## Last completed step

Both `fabric-customer` and `fabric-data-framework` are public repositories. Customer CI/release workflows on PR #6 now:

- use GitHub-hosted `ubuntu-latest`;
- require no cross-repository PAT or `FRAMEWORK_REPO_TOKEN`;
- always run the exact framework integration gate;
- checkout public `ruizengalways/fabric-data-framework` at exact tag `v0.3.0`;
- release logic downloads the exact public framework `v0.3.0` wheel using the normal workflow token.

This removes the previous false-green mode where the integration job could succeed while its real cross-package steps were skipped.

## Phase 3 Customer content

- exact framework dependency `fabric-data-framework==0.3.0`;
- source metadata validator rejecting physical Fabric IDs in semantic dataset definitions;
- DEV/UAT/PROD environment binding profiles separated from semantic metadata;
- Customer source-contract CI and wheel build;
- exact framework integration test job;
- tag-triggered Customer release workflow;
- release-manifest and same-release DEV/UAT/PROD deployment-plan contract tests.

## GitHub-hosted validation

Customer run `33140847380` proved the public runner model:

```text
source-metadata-and-wheel       SUCCESS
runner group                    GitHub Actions
requested label                 ubuntu-latest

exact-framework-integration     FAILURE
failing step                    Checkout exact framework release source
runner group                    GitHub Actions
requested label                 ubuntu-latest
```

The source job successfully validated metadata, compiled source, built the Customer wheel and uploaded the artifact.

The exact integration failure is expected and truthful: framework tag `v0.3.0` does not yet exist. The workflow no longer hides this release dependency behind an optional secret or skipped steps.

## Exact framework integration contract

Once framework `v0.3.0` exists, the Customer gate must execute:

```text
Checkout Customer
Checkout fabric-data-framework @ v0.3.0
Install exact framework + Customer
Run cross-package tests
Build release manifest
Validate DEV/UAT/PROD deployment plans
```

Customer PR #6 must remain open until all of these steps pass.

## Environment promotion proof

`deploy/bindings.dev.json`, `bindings.uat.json` and `bindings.prod.json` contain non-secret reference environment bindings only. They are outside the semantic release hash. The same immutable Customer release identity is combined with different environment bindings for DEV/UAT/PROD, while runtime state such as watermarks, leases, run history, quarantine/reprocess records and runtime overrides remains environment-local.

## Validation summary

Previously completed local validation:

- Customer `pytest -q`: **4 passed** against framework `0.3.0` source;
- metadata validator: PASS;
- compile: PASS;
- Customer wheel build: PASS;
- workflow YAML parse: PASS.

Current remote validation:

- GitHub-hosted source-contract job: **PASS**;
- exact immutable framework integration: **BLOCKED ON MISSING `v0.3.0` TAG/RELEASE**.

## Merge/release state

Customer Phase 3 PR #6 remains **OPEN**.

It must not merge until:

1. framework `v0.3.0` immutable tag/release exists;
2. exact framework integration executes all steps and passes.

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
2. Rerun Customer PR #6; require exact framework integration to pass; merge it.
3. Add a tiny multi-dataset Customer graph for dispatcher/failure-isolation testing.
4. Add representative snapshot and CDC datasets only when the generic framework strategies exist.
5. Add real Fabric Notebook/Pipeline items when the runtime adapter is ready.

Do not add dozens of fake tables. A small representative graph should prove the reusable platform behaviour.
