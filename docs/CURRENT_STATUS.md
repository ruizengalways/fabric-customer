# Current Status — fabric-customer

Last updated: 2026-08-30

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer WATERMARK/SCD2 vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **COMPLETE AND MERGED**.
- Enterprise bulk-onboarding/domain-bootstrap reference: **IMPLEMENTED**.
- Framework 0.4-next project-contract adoption: **COMPLETE AND MERGED**.
- Next runtime domain slice — multi-dataset dispatcher/failure isolation: **WAITING FOR IMMUTABLE FRAMEWORK `v0.4.0` RELEASE BEFORE CUSTOMER RUNTIME DEPENDENCY UPGRADE**.

## Merged project-contract baseline

Feature PR:

```text
fabric-customer PR #8
merge SHA: d05f06d3a2f8d9e31f4c7d9459c8e55df44460ff
PR validation workflow: 33308362061
framework-next SHA: 148e02e3fff7861f238296e7554815a6fd49dd0a
```

All three CI proof lanes passed before merge:

```text
source-metadata-and-wheel        SUCCESS
exact-framework-integration      SUCCESS
framework-next-project-contract  SUCCESS
```

Observed validation details:

```text
released v0.3.0 wheel SHA256 verification: PASS
Customer cross-package tests: 8 passed
canonical documentation consistency: 5 documents validated
Customer root project-validate: PASS
Health project-init: PASS
Health generated DatasetConfig: 100
Health generated semantic selections: 100
Health project-validate: PASS
Health validation JSON reports: retained as CI artifact for the PR run
```

This baseline is source/CI proof. It is not live Fabric/provider/capacity evidence.

## Released runtime baseline remains v0.3.0

Customer production/release packaging still exact-pins:

```text
fabric-data-framework==0.3.0
```

The stable CI integration lane downloads the immutable v0.3.0 wheel, verifies `SHA256SUMS`, installs it, runs the Customer cross-package tests and builds same-release deployment plans.

This remains the only released framework dependency for Customer. Framework source `0.4.0` is still unreleased and must not be substituted into the release workflow.

## Exact framework-next compatibility baseline

A separate CI lane targets the exact framework development SHA:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

This SHA contains the framework-owned non-destructive `project-init` and static `project-validate` contracts. Customer CI checks that exact source snapshot without changing `pyproject.toml`.

The lane proves source compatibility only:

```text
checkout Customer
checkout exact framework-next SHA
install framework-next source
project-validate Customer root
project-init temporary Health project
generate 100 DatasetConfig + 100 semantic selections
project-validate temporary Health project
retain both JSON validation reports
```

It does **not** establish an immutable framework release or live Fabric evidence.

## Customer project contract

The Customer repository now declares:

```text
fabric-project.json
config/datasets/crm.customer.json
config/capture/semantic-selections.json
```

The existing `deploy/` folder remains the non-secret environment binding owner, and `fabric-project.json` points `environment_binding_dir` to that existing directory so adoption does not duplicate environment binding sources of truth.

Framework-next `project-validate .` fails closed on:

- invalid/duplicate DatasetConfig values;
- missing/unknown dataset dependencies;
- dependency cycles;
- unsupported capture/apply engine capability combinations;
- missing or unknown semantic selections;
- semantic pattern/capture mismatches;
- semantic history/delete overclaims.

A PASS is static project validation only.

## Enterprise 100-table Health proof

The fixture remains:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT
```

The default generator mode remains compatible with released Framework v0.3.0.

The `--framework-next` mode additionally:

- resolves one semantic selection for every dataset;
- writes `semantic-selections.json` when explicitly requested;
- makes all ten declared Debezium datasets explicit `EXTERNAL_CDC` capture operations;
- sets Debezium `progress_owner=EXTERNAL`;
- pins `capability_profile=debezium_kafka_v1`;
- keeps final target apply on framework Spark authority.

The validated exact framework-next project summary is:

```text
datasets: 100
semantic selections: 100
capture strategies: FULL=50, WATERMARK=40, CDC=10
apply strategies: REPLACE=50, SCD1=20, SCD2=20, UPSERT=10
execution groups: health_full_refresh=50, health_scd2=20, health_scd1=20, health_debezium=10
capture engines: SPARK=90, EXTERNAL_CDC=10
apply engines: SPARK=100
```

This closes the previous documentation/config mismatch where the fixture called the CDC rows “Debezium” while the generated DatasetConfig contained no Debezium capability profile.

## Documentation consistency contract

`scripts/validate_docs.py` is now a CI gate rather than a manual convention.

It derives the current released framework pin from `pyproject.toml` and the exact framework-next SHA from `.github/workflows/ci.yml`, then checks the canonical docs for agreement on the version/SHA, project commands, Debezium reference, 100-table workflow and required project source-of-truth files.

The PR #8 source job observed:

```text
validated canonical docs released_framework=0.3.0
framework_next_sha=148e02e3fff7861f238296e7554815a6fd49dd0a
documents=5
```

The validator complements human review; it does not attempt to judge every prose statement semantically.

## Proof taxonomy

Keep these claims separate:

```text
v0.3 released-wheel integration PASS
!=
0.4-next exact-SHA static project PASS
!=
real Fabric provider/runtime PASS
!=
100-table capacity/performance PASS
```

The 100-table fixture is still a configuration/onboarding scale proof. Runtime correctness remains proven with small representative fixtures, and real provider/capacity claims require approved environment evidence.

## Current external boundary

- No real Fabric workspace deployment has executed for this Customer repository.
- Checked-in bindings are reference values, not company production resource IDs.
- No production Pipeline/Notebook/Spark Job Definition is proven here.
- No actual DEV/UAT/PROD production control-plane store is bound.
- No Customer production release has been created.
- No live Debezium/Kafka integration evidence has been retained.
- No 100-table concurrency/capacity benchmark has been executed.

## Exact next implementation sequence

1. Keep the v0.3.0 released dependency lane green until Framework v0.4.0 is actually published.
2. Publish/prove Framework v0.4.0 through the framework release process and retained exact-release evidence gates.
3. Upgrade Customer `pyproject.toml`, release CI and canonical Python imports to the immutable v0.4.0 release in one migration PR.
4. Add the smallest representative multi-dataset dispatcher/failure-isolation scenario.
5. Continue with retry/backfill/replay and representative CDC/UPSERT/SNAPSHOT_DIFF runtime slices.
6. Execute the real Fabric DEV integration sequence in `docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md` and retain evidence.
7. Ramp controlled concurrency before claiming 100-table production-scale support.

Do not add dozens of fake runtime tables. Use the bulk manifest for onboarding/config scale and small representative datasets for reusable runtime correctness proof.

## Documentation check obligation

Every coherent implementation must update and cross-check at least:

```text
README.md
docs/PROJECT_BLUEPRINT.md
docs/CURRENT_STATUS.md
docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md
examples/enterprise_100_table/README.md
```

Commands, framework pins, evidence labels and repo-boundary guidance must agree across those files before merge.
