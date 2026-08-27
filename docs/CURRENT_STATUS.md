# Current Status — fabric-customer

Last updated: 2026-08-28

## Current phase

Phase 0 — canonical architecture: **COMPLETE**.

Framework Phase 1 foundation: **SATISFIED**.

Customer Phase 2 — `crm.customer` WATERMARK -> Bronze -> validation/quarantine -> SCD2 -> reconciliation -> state-commit vertical slice: **COMPLETE**.

## Last completed step

Implemented the first Customer runtime/reference slice against `fabric-data-framework` source version `0.2.0`.

Customer now has real source-controlled semantic metadata, domain mapping/DQ code, deterministic CRM fixtures and cross-package integration tests. Generic capture/apply/reconciliation logic remains in the framework.

## Implemented components

- `pyproject.toml` with exact `fabric-data-framework==0.2.0` dependency contract.
- `config/datasets/crm.customer.json`.
- `src/fabric_customer/metadata.py`.
- `src/fabric_customer/domain.py`.
- deterministic initial/incremental CRM fixture JSON.
- metadata contract test.
- end-to-end Customer vertical-slice integration/recovery tests.

## Dataset semantics

`crm.customer` uses:

- WATERMARK `modified_at`;
- tie-breaker `customer_id`;
- SCD2;
- business/merge key `customer_id`;
- tracked attributes `name`, `address`, `segment`, `email`;
- HIGH criticality / `crm_daily` execution group;
- Customer email/segment DQ rules with row quarantine;
- required reconciliation before state advancement.

## Tests/checks executed

Customer suite against framework `0.2.0` source under test:

- `pytest -q`: **3 passed**.
- `python -m compileall`: PASS.
- wheel build: PASS (`fabric_customer_reference-0.1.0-py3-none-any.whl`) and package modules verified in wheel contents.

Cross-package assertions cover:

- source-controlled metadata validation/hash;
- two customers sharing one source timestamp captured without loss;
- invalid email and invalid segment quarantine;
- row accounting and significant step audit sequence;
- Customer mapping normalization;
- unchanged C001 causing no new SCD2 version;
- changed C002 close/open SCD2 behaviour;
- new C004 insert;
- duplicate-timestamp incremental tie-breaker through C005;
- successful watermark advance after accounted row quarantine;
- exact rerun selecting no rows and not changing target;
- forced reconciliation failure leaving target and watermark unchanged.

Framework suite for the same slice: **30 passed**.

## Test results

**PASS — Phase 2 vertical slice is executable locally across both repositories.**

No enterprise Fabric workspace was modified or required for these tests.

## Known limitations

- Framework `0.2.0` is source-versioned but not yet published as an immutable package release.
- No real CRM connection; fixtures are intentionally tiny and deterministic.
- No physical Fabric Lakehouse/Warehouse/control-plane adapter yet.
- No Fabric Pipeline/Notebook item yet.
- No late-arriving correction policy or delete handling yet.
- No multi-dataset dispatcher execution in Fabric yet.
- No GitHub Actions/Fabric Deployment Pipeline automation yet.

## Open issues/blockers

No architecture blocker for Phase 3.

External deployment/integration validation requires enterprise Fabric credentials/workspace bindings and an approved deployment path; CI/build/release/dry-run plumbing can be implemented before those credentials are used.

## Version/provenance state

Customer source package version: `0.1.0`.

Exact framework dependency contract: `fabric-data-framework==0.2.0`.

No immutable published Customer/framework release exists yet.

## Exact next implementation step

**Phase 3 — enterprise delivery spine across Framework and Customer.**

1. GitHub Actions PR CI for both repos.
2. Framework wheel build/version/tag guardrails and immutable artifact/release workflow.
3. Customer exact dependency/config-bundle validation.
4. Provider-neutral release manifest generation with Customer Git SHA, framework version, config hash/schema version and Fabric item manifest version.
5. CLI commands/contracts for control-plane schema migration and semantic metadata materialization.
6. Environment binding/dry-run deployment planning and deployment-history recording.
7. A GitHub-driven Fabric deployment adapter/path and Fabric Deployment Pipeline-compatible promotion path where enterprise credentials/permissions allow testing.
8. Preserve isolated DEV/UAT/PROD runtime state throughout promotion.

Do not start Terraform or broad strategy-catalog implementation in this Phase 3 slice.
