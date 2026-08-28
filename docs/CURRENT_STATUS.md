# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **IMPLEMENTED ON FEATURE BRANCH; WAITING FOR CUSTOMER-REPO SELF-HOSTED RUNNER REGISTRATION AND IMMUTABLE FRAMEWORK 0.3.0 RELEASE**.

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
- deployment-plan tests prove the same Customer release hash is reused for DEV/UAT/PROD while physical bindings differ;
- CI/release workflows now target `runs-on: self-hosted` rather than GitHub-hosted runners.

## Framework release dependency

Framework Phase 3 source version `0.3.0` is merged to `fabric-data-framework/main`. Framework CI has now been successfully validated on the self-hosted runner named `Bear`, but the immutable `v0.3.0` wheel release is not yet published.

Therefore this Customer feature branch may prepare and test the exact `==0.3.0` upgrade, but it must not be merged to `main` as a completed production dependency upgrade until the immutable framework artifact exists and exact-release integration can run.

This deliberately preserves the canonical rule that domains consume released immutable framework versions rather than treating framework `main` as a production package source.

## Self-hosted runner topology

GitHub job metadata proved the Framework runner display identity is:

```text
runner_name = "Bear"
runner_group_name = "Default"
job requested labels = ["self-hosted"]
```

Framework jobs successfully schedule with:

```yaml
runs-on: self-hosted
```

The jobs API labels field describes the labels requested by the job and does not prove the runner's complete configured-label set. The design therefore does not assume that `Bear` is a custom scheduler label unless that label is independently configured/verified later.

The repositories are owned by the personal GitHub account `ruizengalways` (`owner.type = User`), not by a GitHub Organization. GitHub repository-level self-hosted runners are dedicated to a single repository. The existing Bear runner instance is proven usable by `fabric-data-framework`, while Customer run `33137219877` remains queued after Framework work completed, with no steps assigned.

The current evidence therefore shows there is no online/eligible self-hosted runner available to the Customer repository. For the current personal-account layout, the minimal path is a second repository-level runner registration/runner process on the same Bear machine for `ruizengalways/fabric-customer`. A distinct runner directory/service should be used so Framework and Customer installations do not overwrite each other.

If the repositories later move under a GitHub Organization, an organization-level runner can serve multiple authorized repositories and is the cleaner enterprise shared-runner topology. The application CI/CD contracts do not change either way.

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

The earlier GitHub-hosted Customer CI attempt failed before runner assignment. Customer CI was then changed to `runs-on: self-hosted`.

Current Customer self-hosted run:

```text
run_id = 33137219877
source-metadata-and-wheel = queued
exact-framework-integration = queued
steps = []
```

Framework Bear CI and the subsequent Framework `main` CI both completed successfully while these Customer jobs remained unassigned. This is now understood as repository-level runner eligibility/scope rather than a Python/application failure and not a missing `FRAMEWORK_REPO_TOKEN` failure.

Once a Customer-repository runner instance is online on Bear, rerun PR #6 CI. The source-only job should execute without the framework token; exact-release integration remains additionally gated on the immutable framework `v0.3.0` artifact and authorized private-repository read credentials.

## Merge/release state

Customer Phase 3 PR #6 remains intentionally **OPEN**.

It must not merge until:

1. an eligible self-hosted runner is registered/online for `fabric-customer` and the source-contract job passes;
2. framework `v0.3.0` immutable wheel release exists;
3. exact framework-release integration runs successfully with authorized private-repository read credentials.

No Customer tag/release is created by this implementation PR.

## Known limitations / blockers

- Customer currently has no online/eligible repository-level self-hosted runner; Bear is proven on Framework but Customer jobs remain queued.
- Immutable framework `v0.3.0` wheel release is required before this dependency upgrade can merge as complete.
- No real Fabric workspace deployment has executed.
- Checked-in bindings are reference values, not company resource IDs.
- No Fabric Pipeline/Notebook item exists yet.
- No actual DEV/UAT/PROD control-plane store is bound.
- No multi-dataset Customer dispatcher scenario yet.
- No snapshot/CDC representative scenario yet.

## Exact next implementation step

1. Register/start a second repository-level self-hosted runner instance on the Bear machine for `ruizengalways/fabric-customer` (or later move to an organization-level shared runner model).
2. Rerun Customer PR #6 source-contract CI on Bear.
3. Publish/prove immutable framework `v0.3.0` release through the Framework Bear release workflow.
4. Run Customer exact-release integration and merge PR #6 when green.
5. Continue with a small multi-dataset Customer scenario to exercise dispatcher/failure isolation.

Do not add dozens of fake tables. A tiny representative graph should prove the generic pattern.
