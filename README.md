# fabric-customer

Fabric-native, framework-agnostic realistic customer/source-system simulator for Microsoft Fabric.

## Architectural invariant

```text
fabric-customer MAY depend on Microsoft Fabric capabilities.
fabric-customer MUST NOT depend on fabric-data-framework implementation.
```

This repository answers **what happened in the source system?** It owns synthetic source systems, deterministic source changes, production-like delivery patterns, Fabric-native source/landing patterns and expected business truth. A downstream implementation owns ingestion, Bronze/Silver, merge, watermark, SCD, CDC interpretation, audit, retries and idempotency.

Framework certification is not owned here. Installed-wheel acceptance belongs to `fabric-data-framework`.

## Deterministic scenario

The canonical seed is `20260907` and the representative CRM scenario is:

| Day | Source fact |
|---:|---|
| 1 | initial snapshot |
| 2 | insert + update |
| 3 | hard delete |
| 4 | duplicate row/event delivery |
| 5 | late-arriving update |
| 6 | schema v2 adds `preferred_language` |
| 7 | source correction + replay |

Generate all source deliveries and framework-neutral truth:

```bash
python -m pip install -e '.[dev]'
fabric-customer materialize --through-day 7 --output build/customer-scenario
fabric-customer verify --output build/customer-scenario
```

Reset and replay:

```bash
fabric-customer reset --output build/customer-scenario
fabric-customer replay 7 --output build/customer-scenario
```

Generated source feeds are separated into snapshot, incremental and Debezium-style CDC paths. Expected truth is separated into `expected/current_state`, `expected/history` and `expected/source_events`.

Every materialization also writes:

```text
SHA256SUMS
WORKLOAD.json
```

`WORKLOAD.json` records deterministic source, truth and combined workload digests. Use the same `workload_digest` when comparing framework v1, framework v2 or any other implementation. `fabric-customer verify` fails if any tracked source/truth byte has changed.

## Fabric-native use

Install the customer wheel into a Fabric Environment, attach `fabric/notebooks/source_simulator.py` to a Lakehouse, and run it to materialize deterministic source files under `Files/fabric-customer`. A Fabric Pipeline may run that notebook and a Copy Activity may move those source files into a separate implementation-owned landing area. `fabric/sql/source_warehouse_seed.sql` is an optional Warehouse source fixture.

Pipeline/Copy/Eventstream transport must preserve the source facts. It must not invoke framework runtime APIs from the simulator.

## What this repository is not

`fabric-customer` is not:

- a framework certification repo;
- a business implementation/config repo;
- the owner of DatasetConfig/SCD/apply strategy;
- a place for framework-specific adapters in production simulator code.

A real business implementation may live in its own repository and depend on a released framework wheel. This simulator stays reusable across implementations.

## Documentation

Start with `docs/README.md`, then use:

- `docs/architecture.md`
- `docs/source-simulator-design.md`
- `docs/scenario-catalog.md`
- `docs/fabric-setup-runbook.md`
- `docs/framework-testing-runbook.md`
- `docs/NEW_PROJECT_RUNBOOK.md`
- `docs/CURRENT_STATUS.md`

## Scale model

The simulator starts with representative sources rather than 100 toy implementations. `source_systems/catalog.json` defines a scale target of 100 tables: 50 full snapshots, 20 incremental current-state sources, 20 history-sensitive incremental sources and 10 Debezium CDC sources. New source tables extend the same source contracts without introducing downstream framework configuration.

## Compatibility note

Version `0.2.0` intentionally removed the old runtime dependency on `fabric-data-framework`, customer-owned framework certification, and framework-specific DatasetConfig/deployment examples. The helper name `load_customer_config()` remains temporarily available but now returns a framework-neutral CRM source definition. Consumers that relied on the old DatasetConfig object must move their framework adapter/configuration into the consuming implementation project.
