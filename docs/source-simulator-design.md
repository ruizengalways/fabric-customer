# Source simulator design

## WHY

Random-only fake data is weak for regression because the exact source truth changes between runs. The simulator therefore uses a fixed seed, known keys, known source timestamps and explicit deliveries.

## WHAT

`fabric_customer.simulator.scenarios.scenario_catalog()` is the canonical executable scenario. Each `ScenarioStep` contains a source snapshot, that day's incremental delivery, CDC events, expected current business state and cumulative source-history facts.

`SourceEvent.as_debezium()` emits a Debezium-shaped payload while keeping the canonical event model independent from any processing framework.

The materializer writes:

```text
source_systems/crm/snapshot/day_XX/
source_systems/crm/incremental/day_XX/
source_systems/crm/cdc/day_XX/
expected/current_state/day_XX/
expected/history/day_XX/
expected/source_events/day_XX/
```

## HOW

```bash
fabric-customer list
fabric-customer materialize --through-day 1 --output build/customer-scenario
fabric-customer materialize --through-day 7 --output build/customer-scenario
fabric-customer replay 4 --output build/customer-scenario
fabric-customer reset --output build/customer-scenario
```

A replay copies the exact delivery again. It does not invent a new business fact. Duplicate event IDs are deliberate on Days 4 and 7. Day 5 deliberately has a source timestamp older than its delivery timestamp. Day 6 deliberately changes schema version.

## Extending the workload

Add source facts, not target semantics. Good fields describe `delivery_pattern`, primary key, change fidelity, delete behavior and expected business truth. Do not add target apply strategies, bronze/silver table names, framework watermark storage, SCD implementation settings or framework retry metadata.
