# Current status

As of the v0.2 architecture refactor, `fabric-customer` is a Fabric-specific, framework-agnostic source-system simulator.

## Implemented locally-testable contracts

- no runtime dependency on `fabric-data-framework`
- no production Python import of framework implementation
- deterministic Day 1-7 CRM scenario
- snapshot, incremental and Debezium-shaped CDC deliveries
- hard delete, duplicate delivery, late arrival, schema evolution, source correction and replay
- framework-neutral current/history/source-event truth
- reset and exact replay commands
- Fabric Lakehouse notebook source and optional Warehouse source fixture
- architecture guard in CI
- 100-table scale target represented as workload counts, not 100 fake implementations

## Fabric validation still required

The repository cannot prove Fabric workspace permissions, Environment publication, Notebook execution, Copy Activity, Warehouse SQL execution or Eventstream delivery from local tests. Follow `docs/fabric-setup-runbook.md` in a real workspace.

Framework installed-wheel certification is intentionally absent from this repository and must be run from `fabric-data-framework`.
