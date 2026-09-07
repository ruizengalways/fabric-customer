# Enterprise 100-table scale profile

The simulator is designed to scale to a realistic mixed workload without implementing 100 toy pipelines up front.

Target source mix:

| Source delivery pattern | Count |
|---|---:|
| Full snapshot | 50 |
| Incremental current-state changes | 20 |
| History-sensitive incremental changes | 20 |
| Debezium-style CDC | 10 |

These are **source delivery facts**, not target apply strategies. The canonical counts also live in `source_systems/catalog.json`. Add representative source tables/scenarios incrementally as real test coverage needs them; never encode a downstream framework's SCD/merge configuration here.
