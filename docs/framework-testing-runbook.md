# Framework comparison runbook

This runbook is framework-neutral. Customer never imports the implementation being tested.

## 1. Prepare and freeze one immutable workload

```bash
fabric-customer materialize --through-day 7 --output build/customer-scenario
fabric-customer verify --output build/customer-scenario
cat build/customer-scenario/WORKLOAD.json
```

Record the `workload_digest`. Every implementation in the comparison must consume source bytes from a directory with the same verified digest.

Do not compare v1 and v2 runs from different workload digests and call that a framework regression test.

## 2. Full snapshot validation

Use `source_systems/crm/snapshot/day_01/customers.json` as a representative full snapshot input. Compare the implementation's normalized current state with `expected/current_state/day_01/customers.json`.

## 3. Incremental/current-state validation

Deliver Day 2 incrementals, then Day 3 delete and Day 4 duplicates. Compare normalized current state after each day with the matching `expected/current_state/day_XX` file.

## 4. History-sensitive validation

Process Days 1-7 with the implementation's own history semantics. Normalize the resulting business versions/change facts and compare them with `expected/history/day_XX/customer_history.json`.

Do not compare framework-internal surrogate keys, audit columns or physical SCD flags unless the implementation-specific test deliberately adds a separate implementation-contract assertion.

## 5. CDC validation

Deliver `source_systems/crm/cdc/day_XX/customer_events.jsonl` exactly. Day 4 and Day 7 contain duplicate event IDs; Day 5 is late; Day 6 changes schema version. Compare consumed source-event facts with `expected/source_events` and resulting business state with `expected/current_state`.

Transport must preserve event IDs, ordering evidence and deliberate duplicates. If Eventstream/Copy preprocessing rewrites those facts, the downstream run is no longer consuming the canonical workload.

## 6. Retry / replay

```bash
fabric-customer replay 7 --output build/customer-scenario
```

Feed the replay back to the implementation without changing customer truth. Whether the implementation is idempotent is an implementation result, not simulator behavior.

The replay directory is not part of the original base `workload_digest`; record the replay day explicitly in the implementation test evidence.

## 7. v1 vs v2 evidence

For each implementation record at minimum:

```text
customer workload_digest
implementation/framework Git SHA or release
framework wheel SHA256 when applicable
Fabric environment/workspace identity
scenario day/replay action
normalized output result
```

Then:

1. verify the frozen customer workload;
2. run framework v1 using a v1-owned adapter/config;
3. reset implementation-owned state, not customer truth;
4. run framework v2 using a v2-owned adapter/config;
5. normalize both outputs to the same business-truth shape;
6. compare v1 vs expected, v2 vs expected, then v1 vs v2 for regression/performance evidence.

Adapters belong with the consuming implementation or an explicitly isolated benchmark harness, never in production simulator code.
