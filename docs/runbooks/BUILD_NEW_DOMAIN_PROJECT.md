# Runbook — Build a new enterprise Fabric domain project

Status: canonical current onboarding and promotion procedure.

Use this when a data engineer receives a new Microsoft Fabric domain containing tens or hundreds of datasets.

Reference workload:

```text
100 datasets
50 FULL      -> REPLACE
20 WATERMARK -> SCD2
20 WATERMARK -> SCD1
10 CDC       -> UPSERT using Debezium / external CDC
```

Capture and apply are separate axes. Repository boundaries do not follow SCD type or capture technology.

## 1. Repository boundary

Default to one repository for one coherent ownership/security/release boundary, for example:

```text
fabric-health
```

Do not split `full`, `scd1`, `scd2` and `debezium` into separate repos only because their technical patterns differ.

Split only for a real boundary such as independent ownership/release authority, PHI/PII/compliance scope, independent data product, materially different approval lifecycle or an unmanageable blast radius.

Inside one repo, operational grouping belongs in:

```text
config/orchestration/execution-groups/
```

## 2. Framework vs domain ownership

Domain repo owns WHAT:

```text
dataset inventory
source system/object + logical connection_ref
business/merge keys
watermark/order/delete facts
capture/apply selection
semantic limitations
execution group/dependencies/criticality
domain mappings and DQ/reconciliation rules
non-secret environment bindings
domain Fabric item definitions
domain tests/docs
```

`fabric-data-framework` owns HOW:

```text
DatasetConfig schema
project-init / project-validate
capability resolution
generic capture/Bronze/apply/SCD
checkpoint/state/reconciliation
provider adapters/recovery/evidence
release/certification contracts
```

Do not copy generic Framework source into a domain repo.

## 3. Current Framework lanes

Production remains exactly pinned to:

```text
fabric-data-framework==0.3.0
```

The established project-contract compatibility lane remains pinned to:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

That SHA is only for current `project-init` / `project-validate` transition validation. It does not replace the production dependency and is separate from Framework 0.4 certification identity.

When immutable approved `v0.4.0` exists, migrate the production dependency through one reviewed dependency-upgrade PR rather than creating a new versioned directory tree.

## 4. Prepare developer machine / jumpbox

Required:

```text
Git
Python 3.11+
company-approved Git/package credentials
```

Example virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
```

The Framework CLI is a developer/jumpbox/CI operator tool; normal scheduled Fabric execution does not require an interactive Fabric terminal.

## 5. Bootstrap project structure

With an approved Framework version that contains the project CLI:

```bash
fabric-framework project-init ./fabric-health --domain health
cd fabric-health
```

Expected current structure follows roles, not Framework versions:

```text
config/
  datasets/
  capture/
  orchestration/execution-groups/
  environments/
src/
fabric/
examples/
tests/
docs/
```

For an existing repo:

```bash
fabric-framework project-init . --domain health --allow-existing
```

`project-init` must not guess PKs, watermarks, delete visibility, history fidelity, SCD strategy, provider capability, physical Fabric IDs or secrets. Existing files are not silently overwritten.

Before immutable v0.4.0 is released, use this Customer repo as the reference but keep the production dependency at `fabric-data-framework==0.3.0`; CI may validate the exact compatibility SHA independently.

## 6. Start with source inventory

Do not start by writing 100 notebooks. For every dataset collect at least:

```text
dataset_id
source system/object
logical connection_ref
business/primary key
source change shape
ordering signal
watermark + tie-breaker
hard/soft delete signal
late/back-dated update risk
history requirement
capture strategy
apply strategy
target object
execution group
criticality
```

`unknown` is an acceptable temporary answer; a guessed semantic claim is not.

## 7. Use the 100-table intake fixture

Reference:

```text
examples/enterprise_100_table/health_100_tables.csv
```

Distribution:

```text
Capture: FULL=50, WATERMARK=40, CDC=10
Apply:   REPLACE=50, SCD2=20, SCD1=20, UPSERT=10
Groups:  health_full_refresh=50, health_scd2=20, health_scd1=20, health_debezium=10
```

Run dependency-free intake validation first:

```bash
python scripts/scaffold_from_manifest.py \
  --manifest examples/enterprise_100_table/health_100_tables.csv \
  --output build/health-preview \
  --expect-count 100
```

This validates manifest shape/key/watermark requirements only; it is not full Framework semantic validation.

## 8. Author current runtime configuration

Current domain runtime truth belongs under:

```text
config/datasets/
config/capture/semantic-selections.json
config/orchestration/execution-groups/
config/environments/
```

Do not place runtime policy under `examples/` and do not create directories named after Framework versions.

Generated configs are bootstrap aids, not authority. Every real dataset still needs source-owner/data-engineer review.

## 9. Debezium / external CDC contract

For a Debezium dataset the intended Framework contract may look like:

```json
{
  "execution": {
    "engine": "EXTERNAL_CDC",
    "progress_owner": "EXTERNAL",
    "capability_profile": "debezium_kafka_v1",
    "apply_engine": "SPARK"
  }
}
```

Semantic selection:

```text
FULL_CHANGES_EVENT
```

Source-controlled intent does not prove real topic mapping, partition/offset ordering, tombstone/delete behavior, replay after outage, credential/network access or Fabric target application. Those require live evidence.

## 10. Semantic selection limits

Keep exactly one reviewed semantic selection per DatasetConfig.

Examples:

```text
FULL + REPLACE -> FULL_SNAPSHOT_CURRENT
WATERMARK      -> WATERMARK_CURRENT
Debezium CDC   -> FULL_CHANGES_EVENT
```

Do not overclaim source fidelity:

- WATERMARK cannot discover a hard delete that disappeared without a delete signal.
- SCD2 cannot reconstruct source changes capture never observed.
- Full snapshot current state does not expose every intermediate source event.

## 11. Validate before Git push

For a project on the applicable Framework contract:

```bash
fabric-framework project-validate . \
  --output build/project-validation.json
```

It should validate DatasetConfig parsing/uniqueness, dependencies/cycles, capture/apply capability compatibility, semantic-selection coverage/agreement, history/delete overclaim guardrails and workload summary.

A PASS means source-controlled static validity, not Fabric deployment certification.

Keep domain tests separate from project validation:

```bash
python scripts/validate_metadata.py
python scripts/validate_docs.py
pytest -q
```

## 12. Git/CI flow

```text
inventory
-> DatasetConfig + semantic selections
-> execution-group policy
-> project-validate
-> domain tests
-> documentation validation
-> feature branch
-> PR
-> required CI
-> merge
```

Do not use long-lived environment branches as deployment state.

## 13. Environment bindings and secrets

Semantic configs use logical references such as:

```json
{"connection_ref": "health_sql_readonly"}
```

Current non-secret environment bindings belong under:

```text
config/environments/dev.json
config/environments/uat.json
config/environments/prod.json
```

Secrets stay outside Git:

```text
passwords
access tokens
client secrets
private keys
raw connection strings
```

Use approved managed/workspace identity and enterprise secret management.

## 14. Normal Fabric item definitions

Normal domain Fabric definitions belong under:

```text
fabric/
```

Use thin Pipelines/Notebooks/Spark Jobs that dispatch into the released Framework. Do not copy generic SCD/DQ/checkpoint algorithms into dozens of notebooks.

Conceptual runtime:

```text
Fabric Pipeline / scheduler
-> dataset_id / execution_group
-> thin domain driver
-> released fabric-data-framework
-> DatasetConfig
-> capture
-> DQ/normalize
-> apply
-> reconcile
-> checkpoint/state
```

Certification-only Fabric items stay under `certification/fabric/` and are not normal domain runtime definitions.

## 15. Prove representative DEV paths first

Do not enable all 100 datasets on the first live proof. Recommended sequence:

```text
1 FULL + REPLACE
1 WATERMARK + SCD1
1 WATERMARK + SCD2
1 Debezium CDC + UPSERT
retry/idempotency drill
reconciliation-failure drill
delete behavior where applicable
small mixed execution group
controlled concurrency increase
then remaining metadata-equivalent datasets
```

Retain exact evidence for each representative path.

## 16. Promotion

Promote the same tested release identity:

```text
PR + CI
-> DEV deployment + representative evidence
-> UAT deployment with UAT bindings
-> validation/approval
-> PROD deployment with PROD bindings
-> smoke + reconciliation
```

Do not build a different PROD-only wheel. Runtime watermarks, run history, quarantine, leases and reprocess state remain environment-local.

## 17. Go-live checklist

Before production confirm:

```text
[ ] repo boundary matches ownership/security/release reality
[ ] immutable Framework release exact-pinned
[ ] every DatasetConfig passes project-validate
[ ] semantic selection reviewed for every dataset
[ ] PK/order/watermark/delete facts confirmed
[ ] SCD2 claims do not exceed capture fidelity
[ ] Debezium profile matches real source path
[ ] secrets are outside Git
[ ] DEV/UAT/PROD have separate runtime state
[ ] representative FULL/SCD1/SCD2/CDC paths have live evidence
[ ] retry/replay/reconciliation behavior tested
[ ] capacity/concurrency measured before full enablement
[ ] promotion approval and rollback procedure exist
```

The 100-table fixture is onboarding/configuration scale proof only; it is not evidence of 100 live integrations or runtime capacity.
