# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **IMPLEMENTED LOCALLY; REMOTE GITHUB CI VALIDATION PENDING**.

## Last completed step

Extended the Customer reference domain to consume the Phase 3 framework delivery contract:

- exact framework dependency advanced to `fabric-data-framework==0.3.0`;
- dependency-free PR metadata validator added so basic Customer CI does not need private-framework credentials;
- source metadata validation rejects physical Fabric IDs in domain dataset definitions;
- DEV/UAT/PROD environment binding profiles added separately from semantic metadata;
- GitHub Actions Customer CI added;
- optional exact-framework integration job added for private cross-repository validation;
- tag-triggered Customer release workflow added;
- Customer release workflow consumes the exact released framework `0.3.0` wheel, runs tests, builds the Customer wheel and generates a release manifest;
- deployment-plan tests prove the same Customer release hash is reused for DEV/UAT/PROD while physical bindings differ.

## CI credential model

`FRAMEWORK_REPO_TOKEN` is optional for the ordinary Customer source-contract job and required only for private cross-repository/release integration.

Without that secret, metadata/dependency validation, compile and Customer wheel build still run; private framework integration is explicitly skipped. With the secret, CI consumes the exact framework `0.3.0` tag/release, runs the full tests, builds the release manifest and validates DEV/UAT/PROD deployment plans.

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

## Remote CI/release state

GitHub Actions definitions are present but have not yet run on GitHub at the time of this status update. The PR must prove the source-contract job on GitHub.

The exact private framework integration job runs only if `FRAMEWORK_REPO_TOKEN` exists. If the secret is absent, the job states the skip explicitly and this limitation remains documented.

No Customer tag/release is created in this implementation PR.

## Known limitations

- No real Fabric workspace deployment has executed.
- Checked-in bindings are reference values, not company resource IDs.
- No Fabric Pipeline/Notebook item exists yet.
- No actual DEV/UAT/PROD control-plane store is bound.
- No multi-dataset Customer dispatcher scenario yet.
- No snapshot/CDC representative scenario yet.

## Exact next implementation step

After Phase 3 CI is green, add a small multi-dataset Customer scenario to exercise the framework's next dispatcher/failure-isolation slice:

- `crm.customer` remains HIGH/critical path;
- add at least one independent non-critical dataset fixture;
- intentionally fail one non-critical dataset;
- prove unrelated dataset execution continues;
- prove final parent result is `PARTIAL_SUCCESS` rather than immediate all-or-nothing failure;
- add a simple dependent dataset and prove only the dependent branch becomes `BLOCKED_DEPENDENCY`.

Do not add dozens of fake tables. A tiny representative graph should prove the generic pattern.
