# Runbook — Build a New Enterprise Fabric Domain Project

Status: canonical domain bootstrap and promotion procedure

Last updated: 2026-08-30

This runbook answers the practical workflow:

```text
I received a new Microsoft Fabric data-engineering domain.
How do I build the repo on a developer machine/jumpbox,
organize tens or hundreds of datasets,
validate it before Git push,
and then prove it safely in Fabric?
```

The worked example is one `health` domain with 100 datasets:

```text
50  FULL      -> REPLACE
20  WATERMARK -> SCD2
20  WATERMARK -> SCD1
10  CDC       -> UPSERT using Debezium/Kafka
```

Capture and apply are separate axes. Repository boundaries do not follow SCD type or capture technology.

---

## 1. Non-negotiable repository model

Use one repository for one coherent ownership/security/release boundary.

For the Health example, the default is:

```text
fabric-health
```

Do **not** create separate `full`, `scd1`, `scd2`, and `debezium` repositories merely because the datasets use different technical patterns.

Split only for a real boundary such as:

- independent owning teams/release authority;
- different PHI/PII/security/compliance boundary;
- genuinely independent data products;
- different approval/promotion lifecycle;
- materially different blast radius that cannot be managed as one product.

Inside one repo, use `orchestration.execution_group` for operational grouping.

---

## 2. Framework vs domain ownership

The domain repository owns WHAT:

- dataset inventory;
- source system/object and logical connection reference;
- business/merge keys;
- source ordering/watermark facts;
- delete visibility;
- history requirement;
- capture/apply selection;
- semantic capture declaration and known limitations;
- execution group/dependency/criticality;
- domain-specific transformations and DQ rules;
- environment-local non-secret bindings;
- domain tests/docs/Fabric content.

`fabric-data-framework` owns HOW:

- DatasetConfig schema;
- `project-init` / `project-validate`;
- capability resolution;
- generic capture/runtime semantics;
- Bronze contracts;
- generic SCD/apply implementations;
- checkpoint/state/reconciliation semantics;
- provider adapters/recovery/evidence contracts;
- release/deployment contracts.

Do not copy generic framework source into a customer/domain repository.

---

## 3. Current framework lanes in this reference

### Released production lane

`fabric-customer` exact-pins:

```text
fabric-data-framework==0.3.0
```

CI downloads the immutable v0.3.0 wheel and `SHA256SUMS`, verifies the checksum, installs Customer, runs the cross-package tests and builds the release/deployment-plan contracts.

### Exact framework-next compatibility lane

A separate CI job checks the exact framework development SHA:

```text
148e02e3fff7861f238296e7554815a6fd49dd0a
```

That source snapshot contains the framework-owned project bootstrap and project dry-run contracts used here before v0.4.0 is published.

The adoption was merged through Customer PR #8:

```text
Customer merge SHA: d05f06d3a2f8d9e31f4c7d9459c8e55df44460ff
validation workflow: 33308362061
```

The PR validation proved all three Customer CI jobs green. The released lane recorded **8 tests passed**. The framework-next lane validated the Customer project and the generated 100-dataset Health project.

This exact-SHA lane is compatibility evidence only. It is **not** an immutable public framework release and must not silently replace the production dependency.

When v0.4.0 becomes immutable, replace the transition with one exact released v0.4.0 dependency through a reviewed migration PR.

---

## 4. Prepare the developer machine or jumpbox

Required local tools:

```text
Git
Python 3.11+
company-approved credentials for Git/package access
```

Create an isolated environment:

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools
```

A company-managed Conda environment is also acceptable.

The framework CLI runs on a developer machine, jumpbox, CI runner or approved operator environment. Normal scheduled Fabric execution does not require an interactive Fabric terminal.

---

## 5. Preferred bootstrap after Framework v0.4.0 is released

After installing the immutable approved framework wheel:

```bash
python -m pip install fabric-data-framework==0.4.0

fabric-framework project-init ./fabric-health --domain health
cd fabric-health
```

Expected skeleton:

```text
fabric-health/
├─ fabric-project.json
├─ README.md
├─ config/
│  ├─ datasets/
│  ├─ capture/
│  └─ environments/
├─ deploy/
├─ docs/
│  └─ dataset-inventory.csv
├─ src/
└─ tests/
```

`project-init` is deliberately non-destructive. It does not guess PKs, watermarks, delete visibility, history fidelity, SCD strategy, provider capability, physical Fabric IDs or secrets.

For an existing corporate repo:

```bash
fabric-framework project-init . --domain health --allow-existing
```

Existing files are never overwritten. Review the adopted layout before committing.

---

## 6. What to do before v0.4.0 is published

Do **not** replace the released v0.3.0 dependency with Framework `main` for production.

Use `fabric-customer` as the reference/template and let CI perform the exact-SHA framework-next compatibility proof.

Typical bootstrap:

```bash
git clone https://github.com/ruizengalways/fabric-customer.git fabric-health
cd fabric-health

git remote rename origin reference
git remote add origin <company-github-url>/fabric-health.git

git checkout -b bootstrap/health
```

Rename Customer package/domain identities before any real release.

The reference repo already contains `fabric-project.json`, so the framework-next CI job can run `project-validate` without changing the production framework dependency pin.

---

## 7. Start with source inventory, not JSON or notebooks

Before generating configs, get source-owner answers for every dataset.

At minimum record:

```text
dataset_id
source system/object
logical connection reference
business/primary key
source change shape
ordering signal
watermark column and tie-breaker
hard/soft delete signal
late/back-dated update risk
history requirement
capture strategy
apply strategy
target object
execution group
criticality
```

Unknown is an acceptable temporary answer. A guessed semantic claim is not.

Do not start by writing 100 notebooks.

---

## 8. Use the checked-in 100-table intake example

Reference manifest:

```text
examples/enterprise_100_table/health_100_tables.csv
```

Distribution:

```text
Capture
  FULL       50
  WATERMARK  40
  CDC        10

Apply
  REPLACE    50
  SCD2       20
  SCD1       20
  UPSERT     10

Execution groups
  health_full_refresh  50
  health_scd2          20
  health_scd1          20
  health_debezium      10
```

The ten CDC rows explicitly declare:

```text
source_system = debezium
connection_ref = health_debezium_kafka
```

This is source-controlled provider intent, not live connectivity proof.

---

## 9. Run the dependency-free intake dry run first

```bash
python scripts/scaffold_from_manifest.py \
  --manifest examples/enterprise_100_table/health_100_tables.csv \
  --output build/health-preview \
  --expect-count 100
```

Expected result:

```text
datasets=100
capture: CDC=10, FULL=50, WATERMARK=40
apply: REPLACE=50, SCD1=20, SCD2=20, UPSERT=10
execution_groups: health_debezium=10, health_full_refresh=50, health_scd1=20, health_scd2=20
dry_run=true no_files_written=true
```

This validates intake shape/key/watermark requirements. It does not validate the complete framework semantic/capability contract.

---

## 10. Generate released-v0.3-compatible configs when required

The default generator mode remains compatible with the current released Customer dependency:

```bash
python scripts/scaffold_from_manifest.py \
  --manifest manifests/health_datasets.csv \
  --output config/datasets \
  --expect-count 100 \
  --write
```

This keeps the v0.3.0 release lane stable during the transition.

Do not blindly accept generated values. Every real dataset still needs source-owner/data-engineer review.

---

## 11. Exercise the exact 0.4-next project contract

This is the CI-proven compatibility flow for framework SHA `148e02e3fff7861f238296e7554815a6fd49dd0a`.

Create an isolated temporary project:

```bash
fabric-framework project-init build/health-project --domain health
```

Generate DatasetConfig and semantic selections:

```bash
python scripts/scaffold_from_manifest.py \
  --manifest examples/enterprise_100_table/health_100_tables.csv \
  --output build/health-project/config/datasets \
  --expect-count 100 \
  --framework-next \
  --semantic-selections-output build/health-project/config/capture/semantic-selections.json \
  --write
```

Run project validation:

```bash
fabric-framework project-validate build/health-project \
  --output build/health-project-validation.json
```

PR #8 validated this exact workload contract:

```text
dataset_count = 100
semantic_selection_count = 100
capture strategies = FULL 50 / WATERMARK 40 / CDC 10
apply strategies = REPLACE 50 / SCD2 20 / SCD1 20 / UPSERT 10
execution groups = health_full_refresh 50 / health_scd2 20 / health_scd1 20 / health_debezium 10
capture engines = SPARK 90 / EXTERNAL_CDC 10
apply engines = SPARK 100
```

The 90 non-Debezium datasets use framework AUTO capture resolution, which conservatively resolves to Spark in the pinned 0.4 development profile. A real domain can later select explicit certified Fabric capture engines per dataset where appropriate.

---

## 12. Debezium contract

In framework-next mode, a manifest row declaring `source_system=debezium` emits:

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

Its semantic selection is:

```text
FULL_CHANGES_EVENT
```

This fixes the prior reference gap where the documentation called those rows Debezium but the generated config only declared generic `CDC`.

It still does not prove real topic mapping, partition/offset order, tombstone/delete behavior, replay after outage, credential/network access or live Fabric target application.

---

## 13. Semantic selections are mandatory project truth in the 0.4 contract

For each DatasetConfig, keep exactly one semantic selection under:

```text
config/capture/semantic-selections.json
```

The framework validator checks coverage and semantic consistency.

Examples for this Health fixture:

```text
FULL + REPLACE       -> FULL_SNAPSHOT_CURRENT
WATERMARK            -> WATERMARK_CURRENT
Debezium CDC         -> FULL_CHANGES_EVENT
```

Generated defaults are a bootstrap aid, not authority. Review them before production promotion.

Important limits:

- WATERMARK cannot discover hard deletes that have already disappeared unless the source provides a delete signal.
- SCD2 cannot reconstruct source changes capture never observed.
- Full snapshot current state does not expose every intermediate source change.

---

## 14. Run `project-validate` before Git push

For a v0.4+ project, the normal developer gate is:

```bash
fabric-framework project-validate . \
  --output build/project-validation.json
```

It checks the whole repository contract:

```text
DatasetConfig parsing/uniqueness
dependency references
dependency cycles
capture capability compatibility
apply capability compatibility
semantic-selection completeness
unknown semantic-selection dataset IDs
semantic pattern/capture agreement
history/delete overclaim guardrails
workload summary
```

A PASS means source-controlled static validity. It is not a Fabric deployment certification.

---

## 15. Keep domain tests separate from project validation

Project validation does not replace domain tests.

Run tests for mappings, DQ rules, domain extensions, representative runtime slices, fixtures and deployment assumptions.

Current Customer v0.3 release lane:

```bash
python scripts/validate_metadata.py
pytest -q
```

PR #8 recorded:

```text
8 passed
```

Once Customer upgrades to immutable v0.4.0, canonical Python imports/tests must be migrated in one reviewed dependency-upgrade PR.

---

## 16. Documentation is also a CI contract

Run:

```bash
python scripts/validate_docs.py
```

The validator derives the released framework version from `pyproject.toml` and the exact framework-next SHA from `.github/workflows/ci.yml`, then checks the canonical documentation set for agreement.

PR #8 recorded:

```text
released_framework=0.3.0
framework_next_sha=148e02e3fff7861f238296e7554815a6fd49dd0a
documents=5
```

This protects against common drift such as changing the package pin but forgetting the runbook/status/README. Human review is still required for semantic accuracy.

---

## 17. GitHub PR and CI gates

Normal flow:

```text
local/jumpbox
  -> inventory
  -> DatasetConfig + semantic selections
  -> project-validate
  -> domain tests
  -> documentation validation
  -> git commit
  -> push feature branch
  -> PR
  -> required CI
  -> merge
```

The reference CI has three distinct jobs:

### `source-metadata-and-wheel`

- exact released dependency/source metadata validation;
- canonical documentation consistency;
- 100-row intake dry run;
- source compile;
- Customer wheel build.

### `exact-framework-integration`

- immutable v0.3.0 wheel download;
- SHA-256 verification;
- Customer install/tests;
- release manifest;
- DEV/UAT/PROD deployment plans.

### `framework-next-project-contract`

- exact pinned 0.4-development source checkout;
- Customer root `project-validate`;
- temporary `project-init` Health repo;
- 100 configs + 100 semantic selections;
- Health `project-validate`;
- retained JSON validation reports.

Do not collapse these evidence labels in documentation or release notes.

---

## 18. Environment bindings and secrets

Semantic DatasetConfig files use logical references such as:

```json
{
  "connection_ref": "health_sql_readonly"
}
```

Physical workspace/item IDs and non-secret bindings are environment-local deployment configuration.

Secrets must remain outside Git:

```text
passwords
access tokens
client secrets
private keys
raw connection strings
```

Prefer approved managed/workspace identity and corporate secret management.

This reference keeps existing non-secret bindings under:

```text
deploy/bindings.dev.json
deploy/bindings.uat.json
deploy/bindings.prod.json
```

`fabric-project.json` points `environment_binding_dir` to `deploy/` to avoid creating a second source of truth during adoption. New project-init repositories can use the framework default `config/environments/` layout.

---

## 19. Build immutable release artifacts

Do not rebuild a different package for each environment.

The release identity must include the exact domain Git SHA/config bundle and exact released framework version.

Current v0.3 example:

```bash
fabric-framework release-manifest \
  --domain health \
  --domain-release-version 1.0.0 \
  --domain-git-sha <git-sha> \
  --framework-version 0.3.0 \
  --config-dir config/datasets \
  --build-id <ci-build-id> \
  --output release-manifest.json
```

Then plan each environment with the same release manifest and different approved bindings.

When v0.4.0 becomes the Customer runtime dependency, change the framework version only through the reviewed dependency-upgrade/release process.

---

## 20. Fabric DEV setup

After source/CI gates are green:

1. create/select the approved DEV workspace;
2. create/select the domain Fabric Environment;
3. install the immutable approved framework wheel;
4. install the immutable domain wheel;
5. publish the Environment;
6. bind approved source connections/identity;
7. provision/bind Lakehouse/Warehouse targets;
8. deploy/sync thin domain driver items;
9. keep runtime state environment-local.

Do not make every production notebook execute ad-hoc `%pip install` commands.

Do not put generic framework algorithms into 100 copied notebooks.

---

## 21. Thin-driver runtime shape

Target design:

```text
Fabric Pipeline / scheduler
        |
        +-- dataset_id / execution_group
        v
thin Notebook or Spark Job Definition
        |
        v
released fabric-data-framework
        |
        +-- DatasetConfig
        +-- capture
        +-- normalize / DQ
        +-- apply
        +-- reconcile
        +-- checkpoint/state
```

For the Health example, execution groups are the operational unit:

```text
health_full_refresh   50
health_scd2           20
health_scd1           20
health_debezium       10
```

They are not separate repositories.

---

## 22. Prove representative live paths before enabling all 100

Do not switch all 100 datasets on during the first Fabric proof.

Recommended DEV sequence:

1. one FULL + REPLACE dataset;
2. one WATERMARK + SCD1 dataset;
3. one WATERMARK + SCD2 dataset;
4. one Debezium CDC + UPSERT dataset;
5. retry/idempotency drill;
6. reconciliation failure drill;
7. delete behavior where applicable;
8. small mixed execution group;
9. controlled concurrency increase;
10. only then enable remaining metadata-equivalent datasets.

Retain exact evidence for each representative path.

---

## 23. Debezium live evidence checklist

For a real Debezium dataset prove:

```text
source/table -> topic mapping
key extraction
partition/offset ordering
before/after update handling
tombstone/delete handling
duplicate/replay behavior
checkpoint ownership
consumer outage/restart recovery
source outage recovery
schema evolution behavior
Fabric target apply result
reconciliation/checkpoint result
exact released framework/domain identity
```

The source-controlled capability profile is necessary, but it is not sufficient evidence.

---

## 24. DEV -> TEST/UAT -> PROD promotion

Promotion model:

```text
PR + CI green
  -> immutable domain/framework artifacts
  -> DEV deployment
  -> representative integration evidence
  -> TEST/UAT deployment
  -> automated/business validation
  -> approval
  -> PROD deployment
  -> smoke + reconciliation
```

Promote the same tested release identity. Do not build a new PROD-only wheel.

Runtime watermarks, run history, quarantine, leases and reprocess state remain environment-local.

---

## 25. Go-live checklist

Before production enablement confirm:

- [ ] repository boundary matches ownership/security/release reality;
- [ ] immutable framework release is exact-pinned;
- [ ] every DatasetConfig passes project validation;
- [ ] every dataset has a reviewed semantic selection;
- [ ] PK/business key is source-owner confirmed;
- [ ] watermark/order/replay assumptions are confirmed;
- [ ] delete visibility is explicitly documented;
- [ ] SCD2 claims do not exceed capture fidelity;
- [ ] Debezium provider profile matches the real source path;
- [ ] secrets are outside Git;
- [ ] DEV/TEST/PROD keep separate runtime state;
- [ ] immutable framework/domain wheels are installed/published;
- [ ] representative FULL/SCD1/SCD2/CDC live paths have retained evidence;
- [ ] retry/replay/reconciliation failure behavior is tested;
- [ ] capacity/concurrency has been measured before full enablement;
- [ ] release manifest/deployment plans are retained;
- [ ] promotion approval and rollback procedure exist.

---

## 26. Evidence boundary of this reference repository

As of 2026-08-30:

```text
v0.3.0 released-wheel integration         PROVEN IN CI
100-row manifest/config generation         PROVEN IN CI
canonical documentation consistency        PROVEN IN CI
exact 0.4-next Customer project contract   PROVEN IN CI FOR PINNED SHA
exact 0.4-next Health 100-table contract   PROVEN IN CI FOR PINNED SHA
real Customer Fabric workspace execution   NOT YET RETAINED
live Debezium/Kafka execution               NOT YET RETAINED
100-table runtime capacity                  NOT YET RETAINED
Customer production release                NOT YET CREATED
```

Exact source/CI baseline for the 0.4-next adoption:

```text
Customer PR #8
Customer merge SHA d05f06d3a2f8d9e31f4c7d9459c8e55df44460ff
workflow 33308362061
framework-next SHA 148e02e3fff7861f238296e7554815a6fd49dd0a
```

Do not cite this runbook itself as evidence that a live integration happened.

When real approved Fabric proof is executed, update `docs/CURRENT_STATUS.md` with exact release/workspace/evidence references and keep the claims narrowly scoped to what was actually observed.
