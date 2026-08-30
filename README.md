# fabric-customer

Reference Customer domain for the Enterprise Microsoft Fabric Data Engineering Platform.

This repository owns Customer-specific source-controlled dataset metadata, mappings, business DQ rules, fixtures and domain integration tests. Generic capture selection, Bronze normalization, quarantine execution, SCD/apply algorithms, reconciliation, state semantics and delivery contracts are consumed from `fabric-data-framework` rather than reimplemented.

## Current implementation

```text
crm.customer
  -> WATERMARK(modified_at, customer_id)
  -> normalized Bronze
  -> Customer DQ / row quarantine
  -> Customer mapping
  -> framework SCD2
  -> reconciliation
  -> target + watermark/state commit sequencing
```

Customer package version: `0.1.0`.
Framework dependency contract: `fabric-data-framework==0.3.0`.

Phase 3 adds Customer CI/release participation:

- dependency-free source metadata validation;
- GitHub Actions Customer wheel build;
- exact released-framework integration;
- DEV/UAT/PROD binding profiles outside semantic metadata;
- same-release deployment-plan tests;
- tag-triggered Customer release workflow that consumes the exact released framework wheel and emits a release manifest.

## Enterprise project bootstrap / 100-table onboarding

The repo also acts as the reference shape for a new domain project such as `fabric-health`.

A checked-in scale fixture demonstrates one repo onboarding 100 mixed datasets without splitting repositories by implementation detail:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT (Debezium example)
```

Use:

```bash
python scripts/scaffold_from_manifest.py \
  --manifest examples/enterprise_100_table/health_100_tables.csv \
  --output build/health-preview \
  --expect-count 100
```

Add `--write` only when generating real `config/datasets/*.json` in a new domain repo.

The generator is local domain-repository tooling. It is not the Fabric runtime and it does not replace the released `fabric-framework` CLI.

The end-to-end procedure from jumpbox/VDI bootstrap through GitHub CI, Fabric Environment setup, DEV integration and DEV -> TEST -> PROD promotion is documented in:

```text
docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md
```

Important boundary: the 100-table fixture proves deterministic onboarding/config-schema scale, not that 100 real sources have already executed in Fabric. Provider integration, capacity/concurrency and production promotion require retained approved-environment evidence.

## Repository rule

Framework owns HOW. Domain repositories own WHAT.

Do not create separate repos merely because datasets use FULL, WATERMARK, CDC, SCD1 or SCD2. Split only for a real ownership, security/compliance, data-product or independent release boundary.

## Structure

- `config/datasets/crm.customer.json` — current source-controlled executable Customer dataset definition.
- `examples/enterprise_100_table/` — 100-dataset onboarding/scale fixture.
- `scripts/scaffold_from_manifest.py` — deterministic manifest dry-run/config generator for new domains.
- `src/fabric_customer/domain.py` — Customer mapping and DQ rules.
- `deploy/bindings.*.json` — non-secret reference environment binding profiles.
- `scripts/validate_metadata.py` — source-only CI contract.
- `tests/fixtures/` — tiny deterministic CRM fixtures.
- `tests/` — domain integration, recovery, delivery-plan and bulk-onboarding contract tests.
- `docs/runbooks/` — project bootstrap/deployment and operational procedures.
- `docs/` — canonical Customer project state.

Cross-repository architecture remains canonical in `fabric-data-framework`; this repo contains the domain-side reference implementation and runbooks.
