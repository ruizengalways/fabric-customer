# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer WATERMARK/SCD2 vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **IMPLEMENTED ON PR #6; GITHUB-HOSTED SOURCE CI PASSES; EXACT RELEASED-WHEEL INTEGRATION CORRECTLY BLOCKED ON MISSING FRAMEWORK `v0.3.0` RELEASE**.

## Last completed step

Both repositories are public and Customer CI/release workflows now use GitHub-hosted `ubuntu-latest` with no cross-repository PAT.

The exact framework gate has been tightened from source checkout at tag `v0.3.0` to true immutable artifact integration:

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

A missing framework release now fails at the artifact download step. There is no skip path and no fallback to framework `main` or tag source.

Customer CI and release outputs also generate portable checksum files from inside their artifact directory so checksums contain artifact basenames rather than producer-local `dist/` paths.

## Phase 3 Customer content

- exact dependency declaration `fabric-data-framework==0.3.0`;
- source metadata validator rejecting physical Fabric IDs in semantic dataset definitions;
- DEV/UAT/PROD environment binding profiles separated from semantic metadata;
- Customer source-contract CI and wheel build;
- exact released-framework-wheel integration job;
- tag-triggered Customer release workflow;
- framework release SHA-256 verification before installation;
- release-manifest and same-release DEV/UAT/PROD deployment-plan contract tests.

## GitHub-hosted validation

Earlier Customer run `33140847380` proved the public runner model:

```text
source-metadata-and-wheel       SUCCESS
runner group                    GitHub Actions
requested label                 ubuntu-latest

exact-framework-integration     FAILURE
failing step                    exact framework acquisition
runner group                    GitHub Actions
requested label                 ubuntu-latest
```

That run still used tag-source checkout. The workflow has since been hardened to released-wheel download plus checksum verification. Until framework `v0.3.0` is actually published, the exact integration is expected to remain red at the download gate.

## Exact framework integration contract

Once framework `v0.3.0` exists, Customer must prove all of the following against the published assets, not source-under-test:

```text
Download released framework wheel
Download framework SHA256SUMS
Verify framework wheel checksum
Install released framework wheel
Install Customer
Run cross-package tests
Build release manifest
Validate DEV/UAT/PROD deployment plans
```

Customer PR #6 must remain open until all steps pass.

## Environment promotion proof

`deploy/bindings.dev.json`, `bindings.uat.json` and `bindings.prod.json` contain non-secret reference environment bindings only. They are outside the semantic release hash. The same immutable Customer release identity is combined with different environment bindings for DEV/UAT/PROD, while runtime state such as watermarks, leases, run history, quarantine/reprocess records and runtime overrides remains environment-local.

## Validation summary

Previously completed local validation:

- Customer `pytest -q`: **4 passed** against framework `0.3.0` source;
- metadata validator: PASS;
- compile: PASS;
- Customer wheel build: PASS;
- workflow YAML parse: PASS.

Current remote state:

- GitHub-hosted source-contract job: **PASS** on the public runner model;
- exact immutable framework released-wheel integration: **BLOCKED ON MISSING `v0.3.0` RELEASE**.

## Merge/release state

Customer Phase 3 PR #6 remains **OPEN**.

It must not merge until:

1. framework `v0.3.0` immutable GitHub Release exists with wheel and portable `SHA256SUMS` assets;
2. Customer downloads and verifies those assets;
3. exact framework integration, cross-package tests and release/deployment-plan checks pass.

No Customer production release has been created.

## Known limitations / blockers

- Immutable framework `v0.3.0` GitHub Release is pending.
- The newly hardened released-wheel integration is expected to fail until that release exists.
- No real Fabric workspace deployment has executed.
- Checked-in bindings are reference values, not company resource IDs.
- No Fabric Pipeline/Notebook item exists yet.
- No actual DEV/UAT/PROD control-plane store is bound.
- No multi-dataset Customer dispatcher scenario yet; Framework PR #9 contains the generic 0.4.0 dispatcher candidate and is intentionally held behind the 0.3.0 release boundary.
- No snapshot/CDC representative scenario yet.

## Exact next implementation sequence

1. Merge Framework portable-checksum hardening before tagging `v0.3.0`.
2. Publish/prove framework `v0.3.0` with wheel + `SHA256SUMS` on GitHub-hosted Actions.
3. Rerun Customer PR #6; require released-wheel checksum verification, cross-package tests and release/deployment-plan checks to pass; merge it.
4. Merge/revalidate Framework 0.4.0 dispatcher PR #9 after the 0.3.0 release boundary is frozen.
5. Add a tiny multi-dataset Customer graph for dispatcher/failure-isolation testing.
6. Add representative snapshot and CDC datasets only when the generic framework strategies exist.
7. Add real Fabric Notebook/Pipeline items when the runtime adapter is ready.

Do not add dozens of fake tables. A small representative graph should prove the reusable platform behaviour.
