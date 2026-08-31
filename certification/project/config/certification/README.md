# Exact-release certification slice

This project is isolated from the normal CRM project. It owns representative DatasetConfig values and non-secret recipes used only by the 0.4 release-certification workflows.

The environment must pre-provision the named certification source/target/progress/control/landing tables, the Fabric Pipeline/Copy/Spark items, the framework Warehouse marker table, and a production-eligible control-plane database. The framework workflow never creates those resources implicitly.

`control-plane-external-evidence.json` intentionally contains null references and `warehouse-fault-run.json` intentionally points at `example.invalid` until real enterprise evidence and a real fault controller are reviewed into this exact customer SHA. Therefore a source/CI-valid input bundle is not live-ready by default.

Business-path driver mutations are limited to certification tables and return receipts only. Observers read actual state. Customer extensions never author readiness PASS.
