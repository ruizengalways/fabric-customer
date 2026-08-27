# fabric-customer

Reference Customer business domain for the Enterprise Microsoft Fabric Data Engineering Platform.

This repository owns Customer-specific source configuration, mappings, transformations, canonical models, domain data-quality/reconciliation rules, domain-owned Fabric item definitions, fixtures and domain integration/smoke tests.

It consumes an exact released version of `fabric-data-framework`; generic watermark, CDC normalization, snapshot-diff, reconciliation and SCD algorithms are not reimplemented here.

Project memory:

- `docs/PROJECT_BLUEPRINT.md`
- `docs/CURRENT_STATUS.md`
- `docs/adr/`
- `docs/runbooks/`

Cross-repository architecture is canonical in `fabric-data-framework/docs/ECOSYSTEM_BLUEPRINT.md`.
