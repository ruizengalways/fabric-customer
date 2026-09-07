# Source simulator design

## WHY

Random-only fake data is weak for regression because the exact source truth changes between runs. The simulator therefore uses a fixed seed, known keys, known source timestamps and explicit deliveries.

The second requirement is **byte identity**. Framework v1 and v2 comparisons are only trustworthy when both consume the same source/truth bytes. The simulator therefore generates its own checksum and workload-digest evidence instead of asking operators to hash directories manually.

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
scenario-manifest.json
SHA256SUMS
WORKLOAD.json
```

`SHA256SUMS` freezes every generated source/truth payload plus `scenario-manifest.json`. `WORKLOAD.json` records:

- `source_digest` — digest of the tracked source delivery set;
- `truth_digest` — digest of the tracked expected-truth set;
- `workload_digest` — digest of the complete tracked workload manifest;
- `tracked_file_count`, seed and `through_day`.

The digests are framework-neutral. They are workload identity, not framework release identity.

## HOW

```bash
fabric-customer list
fabric-customer materialize --through-day 1 --output build/customer-scenario
fabric-customer materialize --through-day 7 --output build/customer-scenario
fabric-customer verify --output build/customer-scenario
fabric-customer replay 4 --output build/customer-scenario
fabric-customer reset --output build/customer-scenario
```

`materialize` prints the generated `workload_digest`. `verify` re-hashes every tracked file and fails on a missing or modified byte.

A replay copies the exact delivery again. It does not invent a new business fact. Duplicate event IDs are deliberate on Days 4 and 7. Day 5 deliberately has a source timestamp older than its delivery timestamp. Day 6 deliberately changes schema version.

Replay output is intentionally outside the frozen base workload manifest. The base workload proves canonical Day 1-N source/truth identity; replay is an explicit subsequent delivery used to test idempotency/reprocessing behavior.

## Extending the workload

Add source facts, not target semantics. Good fields describe `delivery_pattern`, primary key, change fidelity, delete behavior and expected business truth. Do not add target apply strategies, Bronze/Silver table names, framework watermark storage, SCD implementation settings or framework retry metadata.

When a canonical scenario changes, expect the workload digest to change. Treat that as a new workload version for comparisons; do not compare results from different digests as if they were the same test input.
