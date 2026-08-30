# Enterprise 100-table onboarding example

This directory is a scale/onboarding fixture, not 100 claimed production integrations.

`health_100_tables.csv` demonstrates one domain repository carrying mixed patterns without splitting repos by implementation detail:

| Intake bucket | Capture | Apply | Count |
|---|---|---|---:|
| Full refresh | `FULL` | `REPLACE` | 50 |
| Historical dimensions | `WATERMARK` | `SCD2` | 20 |
| Current-state dimensions | `WATERMARK` | `SCD1` | 20 |
| Debezium current state | `CDC` | `UPSERT` | 10 |

Capture and apply are independent. For example, a real Debezium dataset can use `CDC + SCD2` when the source fidelity and business requirement justify it.

Dry-run without writing files:

```bash
python scripts/scaffold_from_manifest.py \
  --manifest examples/enterprise_100_table/health_100_tables.csv \
  --output build/health-preview \
  --expect-count 100
```

Generate configs for a NEW domain repository:

```bash
python scripts/scaffold_from_manifest.py \
  --manifest manifests/health_datasets.csv \
  --output config/datasets \
  --expect-count 100 \
  --write
```

After generation, review the semantic claims, run `python scripts/validate_metadata.py`, run the exact-framework integration tests, and use the deployment/release procedure in `docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md`.
