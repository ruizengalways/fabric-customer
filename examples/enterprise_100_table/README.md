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

## Released v0.3.0 lane

The default generator remains compatible with the immutable framework v0.3.0 release:

```bash
python scripts/scaffold_from_manifest.py \
  --manifest examples/enterprise_100_table/health_100_tables.csv \
  --output build/health-preview \
  --expect-count 100
```

Add `--write` only when you intentionally want v0.3-compatible DatasetConfig files.

## Exact 0.4-next project-contract lane

Customer CI also checks the exact pinned framework development SHA recorded in `.github/workflows/ci.yml`. That lane exercises the new framework-owned project bootstrap and static dry run without changing the production dependency pin:

```bash
fabric-framework project-init build/health-project --domain health

python scripts/scaffold_from_manifest.py \
  --manifest examples/enterprise_100_table/health_100_tables.csv \
  --output build/health-project/config/datasets \
  --expect-count 100 \
  --framework-next \
  --semantic-selections-output build/health-project/config/capture/semantic-selections.json \
  --write

fabric-framework project-validate build/health-project \
  --output build/health-project-validation.json
```

The next-contract output makes the ten declared `source_system=debezium` datasets explicit physical capture contracts:

```text
engine             = EXTERNAL_CDC
progress_owner     = EXTERNAL
capability_profile = debezium_kafka_v1
apply_engine       = SPARK
```

It also creates one semantic selection per dataset. The expected project validation summary is:

```text
100 DatasetConfig
100 semantic selections
capture: FULL=50, WATERMARK=40, CDC=10
apply: REPLACE=50, SCD1=20, SCD2=20, UPSERT=10
capture engines: SPARK=90, EXTERNAL_CDC=10
apply engines: SPARK=100
```

`project-validate` is static source-controlled validation. It does not prove source connectivity, Fabric permissions, Debezium/Kafka offsets, Pipeline/Spark execution, target commit behavior, capacity or production scale.

The complete bootstrap, review, CI, Fabric DEV integration and promotion procedure is in `docs/runbooks/BUILD_NEW_DOMAIN_PROJECT.md`.
