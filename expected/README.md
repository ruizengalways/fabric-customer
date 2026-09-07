# Expected business truth

This directory defines framework-neutral truth, not target implementation details. `fabric-customer materialize` writes day-scoped files under `expected/current_state`, `expected/history` and `expected/source_events`. A framework v1, v2, another framework or raw Fabric implementation should normalize its output to one of these truth shapes before comparison.

The canonical seed is `20260907`. Generated files are reproducible and are intentionally not committed as build output.
