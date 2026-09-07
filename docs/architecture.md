# Architecture

## WHY

One realistic customer workload must be reusable against framework v1, framework v2, another Fabric framework and a raw Fabric implementation. Coupling the workload to one implementation makes regression and correctness comparisons circular.

## WHAT

### fabric-data-framework

Reusable Fabric data-engineering framework. Owns ingestion semantics, metadata interpretation, bronze/silver logic, merge, SCD1, SCD2, CDC, watermark, audit, observability, retries, idempotency, package lifecycle and lightweight installed-wheel certification.

### fabric-customer

Fabric-native realistic source environment. Owns synthetic source systems, source data, production-like changes, Fabric-native source/landing patterns, deterministic scenarios, workload generation and expected business truth.

### fabric-infra

Owns Fabric infrastructure lifecycle: capacity, workspace, permissions, deployment and infrastructure automation.

## Non-negotiable invariant

```text
fabric-customer MAY use Microsoft Fabric capabilities.
fabric-customer MUST NOT import or depend on fabric-data-framework implementation.
```

Documentation may discuss frameworks. Production simulator Python and runtime dependencies may not import/install one. `tests/test_architecture_guard.py` enforces this boundary.

## Certification vs scenario validation

Framework certification asks: **does this built wheel actually work in Fabric?** It belongs to the framework lifecycle.

Production scenario validation asks: **how does an implementation behave against realistic source changes?** Customer supplies the workload and truth; each implementation supplies its own adapter and output normalization.

## Data flow

```text
synthetic source facts
  -> Lakehouse Files / source Warehouse / CDC-shaped events
  -> optional Fabric Pipeline + Copy Activity
  -> implementation-owned landing/processing
  -> implementation output
  -> normalize output
  -> compare with customer expected business truth
```

No arrow from customer source generation enters a framework API.
