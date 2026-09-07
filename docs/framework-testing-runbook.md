# Framework comparison runbook

This runbook is framework-neutral. Customer never imports the implementation being tested.

## Prepare one immutable workload

```bash
fabric-customer materialize --through-day 7 --output build/customer-scenario
```

Archive or hash this directory if comparing implementations at different times. Both implementations must consume the same source bytes.

## Full snapshot validation

Use `source_systems/crm/snapshot/day_01/customers.json` as a representative full snapshot input. Compare the implementation's normalized current state with `expected/current_state/day_01/customers.json`.

## Incremental/current-state validation

Deliver Day 2 incrementals, then Day 3 delete and Day 4 duplicates. Compare normalized current state after each day with the matching `expected/current_state/day_XX` file.

## History-sensitive validation

Process Days 1-7 with the implementation's own history semantics. Normalize the resulting business versions/change facts and compare them with `expected/history/day_XX/customer_history.json`. Do not compare framework-internal surrogate keys, audit columns or physical SCD flags unless the implementation-specific test chooses to do so separately.

## CDC validation

Deliver `source_systems/crm/cdc/day_XX/customer_events.jsonl` exactly. Day 4 and Day 7 contain duplicate event IDs; Day 5 is late; Day 6 changes schema version. Compare consumed source-event facts with `expected/source_events` and resulting business state with `expected/current_state`.

## Retry / replay

```bash
fabric-customer replay 7 --output build/customer-scenario
```

Feed the replay back to the implementation without changing customer truth. Whether the implementation is idempotent is an implementation result, not simulator behavior.

## v1 vs v2

1. Freeze one generated customer workload.
2. Run framework v1 using a v1-owned adapter/config.
3. Run framework v2 using a v2-owned adapter/config.
4. Normalize both outputs to the same business-truth shape.
5. Compare v1 vs expected, v2 vs expected, then v1 vs v2 for regression/performance evidence.

Adapters belong with the consuming implementation or an explicitly isolated benchmark harness, never in production simulator code.
