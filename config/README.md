# Customer configuration

`config/` is the source of truth for the current customer/domain runtime contract.

- `datasets/`: DatasetConfig
- `capture/`: capture semantic selections
- `orchestration/`: execution-group and runtime policy
- `environments/`: non-secret DEV/UAT/PROD physical bindings

Do not create `framework_0_4`, `framework_0_5`, `latest`, or `legacy` configuration trees. Upgrade the current contract in place through a reviewed PR; Git preserves history.
