# New Fabric data engineering project runbook

This document explains how the reusable framework, independent source simulator and real business implementation fit together. It does **not** imply that `fabric-customer` is the business implementation repository.

## Repository responsibilities

1. `fabric-infra` — provision/operate Fabric capacity, workspace, permissions and infrastructure lifecycle when required.
2. `fabric-customer` — create realistic, deterministic source systems/source changes and expected business truth.
3. `fabric-data-framework` — reusable processing framework and framework-owned installed-wheel certification.
4. **implementation/domain repo** — project-specific DatasetConfig, source-to-target mapping, framework adapter/config, environment bindings and deployment content for the real business project.

The fourth repo can be named for the actual domain/product, for example `fabric-health`. It may depend on a released framework wheel. `fabric-customer` must not.

## Start a project

1. Provision or select a DEV Fabric workspace.
2. Build/install the customer simulator wheel in a source-simulator Fabric Environment.
3. Generate Day 1, verify the workload and record its `workload_digest`.
4. Separately build the framework wheel, install it in the implementation Environment and run framework-owned certification.
5. Create the implementation/domain repo, for example with `fabric-framework project-init ./fabric-health --domain health`.
6. Configure that implementation project to consume customer-generated source paths. Do not put framework config back into `fabric-customer`.
7. Process Day 1 and compare normalized output with customer truth.
8. Advance Day 2 through Day 7, verifying the same workload identity and comparing after each delivery.
9. Replay duplicate/late deliveries to evaluate retry/idempotency behavior.
10. Repeat the same frozen workload with framework v2 or another implementation.

## Commands

```bash
# customer/source side
fabric-customer materialize --through-day 7 --output build/customer-scenario
fabric-customer verify --output build/customer-scenario
fabric-customer replay 4 --output build/customer-scenario

# framework package lifecycle
python -m build --wheel
fabric-framework certify --certification-root /lakehouse/default/Files/framework_cert

# implementation/domain repo
fabric-framework project-init ./fabric-health --domain health
fabric-framework project-validate ./fabric-health
```

These are intentionally different lifecycle gates:

```text
customer materialize/verify
  proves deterministic source/truth identity

framework certify
  proves exact framework wheel behavior

implementation project validation
  proves project-specific config/contracts

end-to-end scenario execution
  proves the implementation behaves correctly against the frozen customer workload
```
