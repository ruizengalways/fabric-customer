# Current status

`fabric-customer` is a Fabric-specific, framework-agnostic source-system simulator/testbed.

## Implemented and CI-testable contracts

- no runtime or dev dependency on `fabric-data-framework`
- no production Python import of framework implementation
- AST/TOML architecture guard prevents framework recoupling
- deterministic Day 1-7 CRM scenario
- snapshot, incremental and Debezium-shaped CDC deliveries
- hard delete, duplicate delivery, late arrival, schema evolution, source correction and replay
- framework-neutral current/history/source-event truth
- reset and exact replay commands
- deterministic `SHA256SUMS` + `WORKLOAD.json`
- `fabric-customer verify` detects modified/missing tracked workload bytes
- source/truth/combined workload digests for v1/v2 comparisons
- Fabric Lakehouse notebook source and optional Warehouse source fixture
- 100-table scale target represented as workload counts, not 100 fake implementations

## Architectural boundary

```text
fabric-customer = source facts + delivery behavior + expected truth
implementation repo = framework config/adapters + target processing
fabric-data-framework = reusable framework + installed-wheel certification
```

Framework certification is intentionally absent from this repository.

## Fabric validation still required

Local/CI tests cannot prove:

- Fabric Environment publication
- real Notebook execution against the exact simulator wheel
- Copy Activity behavior
- Warehouse SQL execution
- Eventstream delivery/order preservation
- downstream implementation end-to-end results

Follow `docs/fabric-setup-runbook.md` in a real workspace. Until those calls are executed and retained for exact bytes, report them as `FABRIC CERTIFICATION REQUIRED`.

## Next practical boundary

1. merge a green simulator CI change;
2. build/install that exact simulator wheel in isolated Fabric DEV;
3. materialize Day 1-7 and retain `WORKLOAD.json` / `SHA256SUMS`;
4. use the same `workload_digest` for framework v1 and v2 implementation runs;
5. compare normalized business output with `expected/*`.
