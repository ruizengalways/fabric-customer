# Exact-release certification slice

This project is isolated from the normal CRM project. It owns representative DatasetConfig values and non-secret recipes used only by the 0.4 release-certification workflows and the Framework unified real-Fabric certification runner.

The environment must pre-provision the named certification source/target/progress/control/landing tables, the Fabric Pipeline/Copy/Spark items, the framework Warehouse marker table, and a production-eligible control-plane database. The Framework never creates shared/production resources implicitly merely to make certification pass.

`control-plane-external-evidence.json` intentionally contains null references and `warehouse-fault-run.json` intentionally points at `example.invalid` until real enterprise evidence and a real fault controller are reviewed into this exact customer SHA. Therefore a source/CI-valid input bundle is not live-ready by default.

Business-path driver mutations are limited to certification tables and return receipts only. Observers read actual state. Customer extensions never author readiness PASS.

## Unified Fabric operator contract

`certification/build_candidate_inputs.py` already packages the credential-free exact inputs required by the Framework unified runner:

```text
INPUTS.json
runner-config.json
release-manifest.json
project/
dist/
```

When testing in an attached Fabric Lakehouse, extract that exact artifact under:

```text
/lakehouse/default/Files/framework_cert/customer-inputs/
```

The operator then runs the Framework package entrypoint rather than retyping the physical IDs/recipes in Notebook cells:

```python
from fabric_data_framework.certification import certify, print_certification_summary

report = certify(
    spark=spark,
    allow_live_mutations=True,
)
print_certification_summary(report)
```

The unified runner verifies candidate SHA/wheel/version identity before using this bundle, verifies exact extension-wheel hashes before local install, and preserves the existing approved-run dependency order.

Runtime tokens/database URLs remain protected runtime values and are never added to this source-controlled certification slice.

Incomplete reviewed Control Plane evidence and an unconfigured real Warehouse fault controller remain explicit fail-closed blockers; the unified runner must not convert them into PASS.
