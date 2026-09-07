# New Fabric data engineering project runbook

## Repository responsibilities

1. `fabric-infra`: provision/operate Fabric capacity, workspace, permissions and infrastructure lifecycle when required.
2. `fabric-customer`: create realistic, deterministic source systems and source changes.
3. `fabric-data-framework`: install/configure the reusable processing framework and certify its built wheel in Fabric.

## Start a project

1. Provision or select a DEV Fabric workspace.
2. Build/install the customer simulator wheel in a source-simulator Fabric Environment.
3. Run Day 1 and verify the generated expected truth.
4. Separately build the framework wheel, install it in the implementation Environment and run framework-owned certification.
5. Configure the framework project to consume customer-generated source paths. Do not put framework config back into `fabric-customer`.
6. Process Day 1, compare normalized output with customer truth.
7. Advance Day 2 through Day 7, comparing after each delivery.
8. Replay duplicate/late deliveries to evaluate retry/idempotency behavior.
9. Repeat the same frozen workload with framework v2 or another implementation.

## Commands

```bash
# customer side
fabric-customer materialize --through-day 1 --output build/customer-scenario
fabric-customer materialize --through-day 2 --output build/customer-scenario
fabric-customer replay 4 --output build/customer-scenario
fabric-customer reset --output build/customer-scenario

# framework side (from fabric-data-framework lifecycle)
python -m build --wheel
fabric-framework certify --certification-root /lakehouse/default/Files/framework_cert
```

The customer command creates source truth. The framework command certifies framework bytes. They are intentionally different lifecycle gates.
