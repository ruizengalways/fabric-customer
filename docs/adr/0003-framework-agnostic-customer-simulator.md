# ADR 0003: Framework-agnostic customer simulator

Status: Accepted

## Decision

`fabric-customer` may use Microsoft Fabric capabilities but must not depend on a downstream data-framework implementation. Framework certification moves to the framework lifecycle. Customer owns source facts, deterministic deliveries and expected business truth only.

## Consequences

The previous versioned framework runtime dependency and customer-owned certification project are removed in v0.2. Framework-specific adapters/configuration live with the consuming implementation. One customer workload can now be replayed unchanged against multiple framework versions.
