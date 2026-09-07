# Scenario catalog

| Day | Slug | Delivery | Business/source truth |
|---:|---|---|---|
| 1 | `initial_load` | snapshot + read events | C1001 Sydney, C1002 Melbourne |
| 2 | `insert_update` | incremental + CDC | C1001 moves to Melbourne; C1003 inserted in Brisbane |
| 3 | `hard_delete` | delete CDC | C1002 no longer exists in current source truth |
| 4 | `duplicate_delivery` | duplicated incremental row and event ID | business truth unchanged |
| 5 | `late_arrival` | late update | C1001 becomes PREMIUM; source timestamp predates delivery |
| 6 | `schema_evolution` | schema v2 updates | `preferred_language` appears on current rows |
| 7 | `source_correction_replay` | correction delivered twice | C1003 corrected to Gold Coast once in business truth |

The scenario JSON files under `/scenarios` are human-readable contracts. The Python catalog is executable truth and tests assert the important invariants.

Expected history is a sequence of source business-change facts; it is intentionally not a framework-specific SCD2 physical layout. Expected source events preserve event IDs, source timestamps, delivery timestamps, before/after images and schema version.
