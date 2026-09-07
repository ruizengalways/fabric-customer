# fabric-customer documentation

This repository is the **independent source-system simulator/testbed**. It is Fabric-specific and framework-agnostic.

## Read in this order

1. `architecture.md` — repository boundaries and non-negotiable decoupling rule.
2. `source-simulator-design.md` — deterministic source generation, expected truth and workload digests.
3. `scenario-catalog.md` — Day 1-7 source facts and why each case exists.
4. `fabric-setup-runbook.md` — run the simulator in a real Fabric workspace.
5. `framework-testing-runbook.md` — freeze one workload and compare framework v1/v2/other implementations.
6. `NEW_PROJECT_RUNBOOK.md` — how this simulator fits into a new Fabric data-engineering project.
7. `CURRENT_STATUS.md` — current implemented/validated boundary and remaining Fabric validation.

## Ownership rule

```text
fabric-customer
  owns source facts + deterministic delivery + expected business truth

implementation repo
  owns framework adapter/config + ingestion/apply behavior + output normalization

fabric-data-framework
  owns reusable framework code + installed-wheel certification
```

Do not move framework DatasetConfig, SCD settings, framework retry metadata, control-plane schema or framework certification back into this repository.

## Status labels

Use these labels precisely:

- `LOCAL PASS` — deterministic source/unit checks passed locally or in CI.
- `CI PASS` — repository CI passed for exact Git bytes.
- `FABRIC CERTIFICATION REQUIRED` — behavior requires a real Microsoft Fabric workspace and has not been executed/retained for the exact bytes being discussed.

Local simulator success never proves Notebook, Copy Activity, Warehouse or Eventstream execution in Fabric.
