# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **IMPLEMENTED ON FEATURE BRANCH; SELF-HOSTED CI VALIDATED ON `Bear`; WAITING FOR IMMUTABLE FRAMEWORK 0.3.0 RELEASE AND EXACT-RELEASE INTEGRATION**.

## Last completed step

Customer CI is now executing successfully on the repository self-hosted runner named `Bear`.

Phase 3 Customer work already includes:

- exact framework dependency prepared as `fabric-data-framework==0.3.0`;
- dependency-free PR metadata validator;
- source metadata validation that rejects physical Fabric IDs in domain dataset definitions;
- DEV/UAT/PROD environment binding profiles separated from semantic metadata;
- GitHub Actions Customer CI on `runs-on: self-hosted`;
- exact private-framework integration job;
- tag-triggered Customer release workflow;
- same-release DEV/UAT/PROD deployment-plan tests.

## Self-hosted runner validation

Customer PR #6 workflow run `33137660655` completed successfully.

GitHub job metadata proves both Customer jobs were assigned to:

```text
runner_id = 2
runner_name = "Bear"
runner_group_name = "Default"
job requested labels = ["self-hosted"]
```

`source-metadata-and-wheel` executed all required source-only steps successfully:

```text
Checkout Customer                         SUCCESS
Setup Python                              SUCCESS
Validate exact framework pin and metadata SUCCESS
Compile Customer source                   SUCCESS
Build Customer wheel                      SUCCESS
Upload Customer wheel                     SUCCESS
```

This closes the previous Customer repository runner-registration blocker.

The jobs API labels field records labels requested by the job and does not prove the runner's complete configured-label set. The workflow therefore continues to use the already validated scheduler expression:

```yaml
runs-on: self-hosted
```

## Exact framework integration state

The `exact-framework-integration` job was also assigned to Bear and the job itself completed successfully, but the actual cross-repository integration steps were intentionally skipped because `FRAMEWORK_REPO_TOKEN` was not present in the workflow environment.

Observed result:

```text
Explain skipped private integration       SUCCESS
Checkout exact framework release source   SKIPPED
Install exact framework and Customer      SKIPPED
Run cross-package tests                    SKIPPED
Build release manifest contract            SKIPPED
```

Therefore a green workflow currently proves Customer source-contract/build CI and Bear runner availability, but does **not** yet prove exact immutable framework-release integration.

`FRAMEWORK_REPO_TOKEN` must provide authorized read access to the private `ruizengalways/fabric-data-framework` repository for that gate.

## Framework release dependency

Framework Phase 3 source version `0.3.0` is merged to `fabric-data-framework/main`, and Framework CI has been successfully validated on Bear.

GitHub Releases for `fabric-data-framework` are still empty as of this status update, so immutable framework release `v0.3.0` has not yet been published.

Customer PR #6 must therefore remain open until:

1. framework `v0.3.0` is published by the Framework release workflow on Bear;
2. `FRAMEWORK_REPO_TOKEN` (or an equivalent authorized private-repository read mechanism) is configured for Customer CI;
3. the exact-framework integration steps execute rather than skip;
4. the full cross-package tests and release-manifest / DEV-UAT-PROD deployment-plan checks pass.

This preserves the canonical rule that domains consume released immutable framework artifacts rather than framework `main`.

## CI credential model

`FRAMEWORK_REPO_TOKEN` is not required for ordinary Customer source-contract CI.

Without it, Customer can still validate metadata, compile source, build the Customer wheel and upload the artifact. With it, and with framework `v0.3.0` published, CI can consume the exact framework release and run the cross-package release gate.

No secret or physical Fabric resource ID is committed to Git.

## Environment promotion proof

`deploy/bindings.dev.json`, `bindings.uat.json` and `bindings.prod.json` contain non-secret reference environment bindings only. They are not semantic dataset definitions and are not part of the release hash.

The same release manifest is combined with different environment bindings for DEV/UAT/PROD. Watermarks, run history, quarantine state, runtime overrides and reprocess history are never included in release/binding files.

## Validation summary

Local validation already completed:

- Customer `pytest -q`: **4 passed** against framework `0.3.0` source under test;
- `python scripts/validate_metadata.py`: PASS;
- `python -m compileall`: PASS;
- Customer wheel build: PASS;
- workflow YAML parse: PASS;
- Framework Phase 3 suite: **37 passed**.

Remote validation now completed:

- Customer Bear runner assignment: **PASS**;
- source metadata validation: **PASS**;
- source compile: **PASS**;
- Customer wheel build/upload: **PASS**;
- exact immutable framework release integration: **PENDING / SKIPPED BY DESIGN**.

## Merge/release state

Customer Phase 3 PR #6 remains intentionally **OPEN**.

The runner blocker is resolved. Remaining release gates are the immutable Framework `v0.3.0` artifact and authorized exact-release integration.

No Customer tag/release is created by this implementation PR.

## Known limitations / blockers

- Immutable framework `v0.3.0` GitHub Release is not yet published.
- `FRAMEWORK_REPO_TOKEN` is not currently available to the Customer workflow, so exact cross-repository release integration is skipped.
- No real Fabric workspace deployment has executed.
- Checked-in bindings are reference values, not company resource IDs.
- No Fabric Pipeline/Notebook item exists yet.
- No actual DEV/UAT/PROD control-plane store is bound.
- No multi-dataset Customer dispatcher scenario yet.
- No snapshot/CDC representative scenario yet.

## Exact next implementation step

1. Create/push Framework tag `v0.3.0` and prove the immutable Framework release workflow on Bear.
2. Configure authorized private-framework read access for Customer exact-release CI.
3. Rerun Customer PR #6 and require the exact-framework integration steps to execute and pass.
4. Merge Customer PR #6 when all release gates are green.
5. Continue with the metadata-driven multi-dataset dispatcher/failure-isolation slice.

Do not add dozens of fake tables. A tiny representative graph should prove the generic pattern.
