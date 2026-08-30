# Current Status — fabric-customer

Last updated: 2026-08-30

## Current phase

- Phase 0 — canonical architecture: **COMPLETE**.
- Framework Phase 1 foundation: **SATISFIED**.
- Customer Phase 2 CRM Customer WATERMARK/SCD2 vertical slice: **COMPLETE**.
- Phase 3 enterprise delivery spine participation: **COMPLETE AND MERGED**.
- Enterprise bulk-onboarding/domain-bootstrap reference: **IMPLEMENTED**.
- Framework 0.4-next project-contract adoption: **IMPLEMENTED; CI/PR VALIDATION REQUIRED BEFORE MERGE**.
- Next runtime domain slice — multi-dataset dispatcher/failure isolation: **WAITING FOR IMMUTABLE FRAMEWORK `v0.4.0` RELEASE BEFORE CUSTOMER RUNTIME DEPENDENCY UPGRADE**.

## Released runtime baseline remains v0.3.0

Customer production/release packaging still exact-pins:

```text
fabric-data-framework==0.3.0
```

The stable CI integration lane downloads the immutable v0.3.0 wheel, verifies `SHA256SUMS`, installs it, runs the Customer cross-package tests and builds same-release deployment plans.

This remains the only released framework dependency for Customer. Framework source `0.4.0` is still unreleased and must not be substituted into the release workflow.

## Exact framework-next compatibility baseline

A separate CI lane now targets the exact framework development SHA:

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

Framework-next `project-validate .` is expected to fail closed on:

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

The new `--framework-next` mode additionally:

- resolves one semantic selection for every dataset;
- writes `semantic-selections.json` when explicitly requested;
- makes all ten declared Debezium datasets explicit `EXTERNAL_CDC` capture operations;
- sets Debezium `progress_owner=EXTERNAL`;
- pins `capability_profile=debezium_kafka_v1`;
- keeps final target apply on framework Spark authority.

Expected exact framework-next project summary:

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

1. Complete CI and merge the framework-next project-contract adoption.
2. Keep the v0.3.0 released dependency lane green until Framework v0.4.0 is actually published.
3. Publish/prove Framework v0.4.0 through the framework release process and retained exact-release evidence gates.
4. Upgrade Customer `pyproject.toml`, release CI and canonical Python imports to the immutable v0.4.0 release in one migration PR.
5. Add the smallest representative multi-dataset dispatcher/failure-isolation scenario.
6. Continue with retry/backfill/replay and representative CDC/UPSERT/SNAPSHOT_DIFF runtime slices.
7. Execute the real Fabric DEV integration sequence in `docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md` and retain evidence.
8. Ramp controlled concurrency before claiming 100-table production-scale support.

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
