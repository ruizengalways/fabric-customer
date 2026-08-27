# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **IMPLEMENTED ON FEATURE BRANCH; WAITING FOR IMMUTABLE FRAMEWORK 0.3.0 RELEASE AND GITHUB-HOSTED RUNNER AVAILABILITY**.

## Last completed step

Extended the Customer reference domain to consume the Phase 3 framework delivery contract:

- exact framework dependency prepared as `fabric-data-framework==0.3.0`;
- dependency-free PR metadata validator added so basic Customer CI does not need private-framework credentials;
- source metadata validation rejects physical Fabric IDs in domain dataset definitions;
- DEV/UAT/PROD environment binding profiles added separately from semantic metadata;
- GitHub Actions Customer CI added;
- optional exact-framework integration job added for private cross-repository validation;
- tag-triggered Customer release workflow added;
- Customer release workflow is designed to consume the exact released framework `0.3.0` wheel, run tests, build the Customer wheel and generate a release manifest;
- deployment-plan tests prove the same Customer release hash is reused for DEV/UAT/PROD while physical bindings differ.

## Framework release dependency

Framework Phase 3 source version `0.3.0` is merged to `fabric-data-framework/main`, but the immutable `v0.3.0` wheel release is **not yet published** because GitHub-hosted Actions jobs are currently failing before runner assignment (`runner_id=0`, no workflow steps).

Therefore this Customer feature branch may prepare and test the exact `==0.3.0` upgrade, but it must not be merged to `main` as a completed production dependency upgrade until the immutable framework artifact exists and exact-release integration can run.

This deliberately preserves the canonical rule that domains consume released immutable framework versions rather than treating framework `main` as a production package source.

## CI credential model

`FRAMEWORK_REPO_TOKEN` is optional for the ordinary Customer source-contract job and required only for private cross-repository/release integration.

Without that secret, metadata/dependency validation, compile and Customer wheel build still run; private framework integration is explicitly skipped. With the secret and an existing framework `v0.3.0` release, CI consumes the exact release, runs the full tests, builds the release manifest and validates DEV/UAT/PROD deployment plans.

## Environment promotion proof

`deploy/bindings.dev.json`, `bindings.uat.json` and `bindings.prod.json` contain non-secret reference environment bindings only. They are not semantic dataset definitions and are not part of the release hash.

The same release manifest is combined with different environment bindings for DEV/UAT/PROD. Watermarks, run history, quarantine state, runtime overrides and reprocess history are never included in these release/binding files.

## Tests/checks executed locally

- Customer `pytest -q`: **4 passed** against framework `0.3.0` source under test.
- `python scripts/validate_metadata.py`: PASS.
- `python -m compileall`: PASS.
- Customer wheel build: PASS (`fabric_customer_reference-0.1.0-py3-none-any.whl`).
- Framework/Customer workflow YAML files parse successfully.
- Framework Phase 3 suite: **37 passed**.

These local source-under-test checks do not replace the required immutable-release integration gate.

## Remote GitHub Actions validation

Customer PR #6 triggered a real `customer-ci` workflow (run `33127710182`). Both jobs failed before any workflow step executed:

```text
source-metadata-and-wheel:
  runner_id = 0
  runner_name = ""
  steps = []

exact-framework-integration:
  runner_id = 0
  runner_name = ""
  steps = []
```

Both terminated within roughly two seconds. Because the source-only job does not require `FRAMEWORK_REPO_TOKEN`, this evidence shows the immediate failure is runner assignment rather than missing private-framework credentials or application-test failure.

This matches the separately reproduced framework-repository hosted-runner blocker. The account-level root cause cannot be established from the repository API available here and must not be guessed.

## Merge/release state

Customer Phase 3 PR #6 remains intentionally **OPEN**.

It must not merge until:

1. GitHub-hosted runner availability is restored;
2. framework `v0.3.0` immutable wheel release exists;
3. the Customer source-contract job runs successfully;
4. exact framework-release integration can run with authorized private-repository read credentials.

No Customer tag/release is created by this implementation PR.

## Known limitations / blockers

- Immutable framework `v0.3.0` wheel release is required before this dependency upgrade can merge as complete.
- GitHub-hosted runner assignment is currently blocked before any workflow step executes on both private repositories.
- No real Fabric workspace deployment has executed.
- Checked-in bindings are reference values, not company resource IDs.
- No Fabric Pipeline/Notebook item exists yet.
- No actual DEV/UAT/PROD control-plane store is bound.
- No multi-dataset Customer dispatcher scenario yet.
- No snapshot/CDC representative scenario yet.

## Exact next implementation step

Once the immutable framework `0.3.0` artifact exists and this Customer Phase 3 dependency PR passes exact-release integration, merge it and then add a small multi-dataset Customer scenario to exercise the framework's dispatcher/failure-isolation slice:

- `crm.customer` remains HIGH/critical path;
- add at least one independent non-critical dataset fixture;
- intentionally fail one non-critical dataset;
- prove unrelated dataset execution continues;
- prove final parent result is `PARTIAL_SUCCESS` rather than immediate all-or-nothing failure;
- add a simple dependent dataset and prove only the dependent branch becomes `BLOCKED_DEPENDENCY`.

Do not add dozens of fake tables. A tiny representative graph should prove the generic pattern.
