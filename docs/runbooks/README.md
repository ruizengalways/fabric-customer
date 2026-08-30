# Runbooks

Runbooks in this directory describe domain-repository procedures without duplicating generic framework runtime semantics.

## Available

### `BUILD_NEW_DOMAIN_PROJECT.md`

Canonical end-to-end enterprise project runbook covering:

- jumpbox/VDI Python/Git setup;
- released framework dependency vs exact framework-next compatibility lane;
- framework-owned `project-init` adoption;
- source inventory before DatasetConfig authoring;
- 100-table Health manifest onboarding;
- semantic selections and `project-validate`;
- explicit Debezium `EXTERNAL_CDC / debezium_kafka_v1` contract;
- local tests and GitHub PR/CI gates;
- immutable release artifacts and non-secret environment bindings;
- Fabric DEV/TEST/PROD setup;
- thin metadata-driven runtime drivers;
- representative FULL/SCD1/SCD2/Debezium live evidence sequence;
- DEV -> TEST -> PROD promotion and go-live checklist.

The runbook deliberately distinguishes:

```text
released dependency proof
static project-contract proof
runtime correctness proof
real Fabric/provider proof
capacity/performance proof
```

Do not treat one proof class as another.

## Future operational runbooks

Add source-outage handling, reconciliation investigation, backfill/replay and smoke-test procedures only when the corresponding deployed behaviors have real retained evidence.

Generic framework recovery/state semantics remain documented in `fabric-data-framework`.
