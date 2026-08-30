# Runbook — Build a New Enterprise Fabric Domain Project

Status: executable project bootstrap and deployment procedure

Last updated: 2026-08-30

This runbook describes how to use `fabric-customer` as the reference shape for a new enterprise Microsoft Fabric data-engineering domain repository such as `fabric-health`.

The worked scale example is 100 datasets:

- 50 full-refresh datasets;
- 20 watermark datasets materialized as SCD2;
- 20 watermark datasets materialized as SCD1;
- 10 Debezium/CDC datasets materialized as current-state UPSERT.

The patterns are deliberately modeled on two independent axes:

```text
capture semantics              target/apply semantics
-----------------              ----------------------
FULL                           REPLACE
WATERMARK                      SCD1
CDC                            SCD2
...                            UPSERT
```

Do not create separate repositories just because capture/apply strategies differ. Repository boundaries should follow data-product ownership, security/compliance boundaries and independent release lifecycles.

## 1. What this repo owns

The domain repository owns WHAT:

- which datasets exist;
- source system/object and logical connection reference;
- capture/apply selection;
- business/merge keys;
- watermark/event ordering columns;
- domain DQ/reconciliation policy references;
- execution groups, dependencies, criticality and operational settings;
- domain code, fixtures and tests;
- domain-owned Fabric items once those items are introduced.

`fabric-data-framework` owns HOW:

- generic capture/runtime contracts;
- Bronze normalization;
- generic SCD/apply algorithms;
- state/checkpoint semantics;
- audit/reconciliation contracts;
- release/deployment contracts;
- reusable Fabric adapters.

Do not copy generic framework algorithms into the domain repo.

## 2. Current released baseline

This reference currently exact-pins:

```text
fabric-data-framework==0.3.0
```

Use the immutable released wheel, not Framework `main`. Framework `main` can contain source version features that have not yet been published as an immutable release.

The repo-level bulk scaffold command introduced here is:

```bash
python scripts/scaffold_from_manifest.py ...
```

It is local developer tooling. It is not a Fabric runtime command and is not the framework CLI.

The released framework CLI is:

```bash
fabric-framework
```

and is used for released framework operations such as release-manifest/deployment-plan generation.

## 3. Prerequisites

Before onboarding a real project, obtain:

- a company-managed GitHub repository;
- a company jumpbox/VDI/developer machine with Git and Python 3.11+;
- access to the approved internal Python package registry or immutable framework wheel release;
- a Fabric capacity and separate DEV/TEST/PROD workspaces;
- approved Fabric source connections/identities;
- source-owner answers for PK, ordering, deletes, late arrivals and history requirements;
- approval for any PHI/PII/security boundary relevant to the domain.

Never put passwords, tokens, private keys, connection strings or production Fabric IDs in semantic dataset metadata.

## 4. Bootstrap the domain repository on the jumpbox

Preferred enterprise option: create the new repo from the approved `fabric-customer` template/reference snapshot, then work in a feature branch.

If a GitHub template is not configured, use the reference repo explicitly:

```bash
git clone https://github.com/ruizengalways/fabric-customer.git fabric-health
cd fabric-health

git remote rename origin reference
git remote add origin <company-github-url>/fabric-health.git

git checkout -b bootstrap/health
```

Before the first production release, rename the package/domain-specific Customer names in `pyproject.toml`, `src/`, docs and workflows. Do not publish a Health project with a Customer package identity.

Expected architectural shape:

```text
fabric-health/
  .github/workflows/
  config/datasets/
  deploy/
  docs/runbooks/
  examples/
  scripts/
  src/
  tests/
  pyproject.toml
```

## 5. Create and activate a local Python environment

Using `venv`:

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Or use the company's approved Conda environment.

Upgrade packaging tools:

```bash
python -m pip install --upgrade pip setuptools
```

Install the exact approved framework release and the domain repo. In a company environment, prefer the internal package registry. For this public reference release, CI demonstrates download + SHA-256 verification of the immutable v0.3.0 wheel.

```bash
python -m pip install fabric-data-framework==0.3.0
python -m pip install -e ".[dev]"
python -m pip check
```

## 6. Collect the 100-table intake manifest

Do not start by creating 100 notebooks.

Collect one row per dataset with at least:

```text
dataset_id
source_system
source_object
connection_ref
target_object
capture_strategy
apply_strategy
primary_key
watermark_column
event_time_column
tracked_columns
delete_policy
execution_group
criticality
```

Use `|` inside CSV fields for multi-column lists, for example:

```text
customer_id|source_id
```

The checked-in scale example is:

```text
examples/enterprise_100_table/health_100_tables.csv
```

Its distribution is:

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
```

The 10 CDC rows use `source_system=debezium` and a logical Kafka connection reference. This is an onboarding contract example, not proof that this Customer repo has executed Debezium against a real Fabric workspace.

## 7. Dry-run the manifest locally

Run validation without writing files:

```bash
python scripts/scaffold_from_manifest.py \
  --manifest examples/enterprise_100_table/health_100_tables.csv \
  --output build/health-preview \
  --expect-count 100
```

Expected summary:

```text
datasets=100
capture: CDC=10, FULL=50, WATERMARK=40
apply: REPLACE=50, SCD1=20, SCD2=20, UPSERT=10
execution_groups: health_debezium=10, health_full_refresh=50, health_scd1=20, health_scd2=20
dry_run=true no_files_written=true
```

This dry-run validates manifest shape and strategy requirements. It does not connect to a source, Fabric workspace, OneLake or production secret store.

## 8. Generate the real dataset metadata

In a NEW domain repository, generate the real source-controlled dataset configs into `config/datasets`:

```bash
python scripts/scaffold_from_manifest.py \
  --manifest manifests/health_datasets.csv \
  --output config/datasets \
  --expect-count 100 \
  --write
```

The result is one deterministic framework `DatasetConfig` JSON per dataset.

Examples:

```text
config/datasets/health.reference_001.json
config/datasets/health.history_001.json
config/datasets/health.current_001.json
config/datasets/health.cdc_001.json
...
```

Do not blindly accept generated defaults. Review each dataset family and amend domain-specific fields/policies as required.

Important review rules:

- `WATERMARK` must have a watermark column and deterministic tie-breaker/overlap safety;
- stateful apply (`UPSERT`, `SCD1`, `SCD2`, `SNAPSHOT_DIFF`) requires merge keys;
- `SCD2` requires a business key and only claims history that the capture fidelity can actually observe;
- hard-delete claims must match the source's real delete visibility;
- Debezium/CDC delete semantics must be defined and tested;
- physical workspace/lakehouse/warehouse IDs belong in environment bindings, not semantic dataset metadata.

## 9. Keep 100 datasets in one repo unless the boundary is organizational

One repo is the default for the 100-table Health example.

Do NOT split because of:

```text
FULL vs WATERMARK vs CDC
SCD1 vs SCD2
number of tables
number of execution groups
```

Consider separate repos only when there is a real boundary such as:

- different owning teams with independent release authority;
- different security/PHI/compliance boundaries;
- different lifecycle and approval chains;
- genuinely independent data products/workspaces.

For example, `fabric-health-clinical` and `fabric-health-public-reference` can be separate if their access, approval and release boundaries are materially different. They should not be separate merely because one uses SCD2 and the other uses full refresh.

## 10. Validate locally before Git push

Run the dependency-free source contract:

```bash
python scripts/validate_metadata.py
```

Run tests against the exact framework release:

```bash
pytest -q
```

Build the domain wheel:

```bash
python -m pip wheel . --no-deps --no-build-isolation -w dist
```

The 100-table scale test in `tests/test_bulk_onboarding.py` proves that the bulk manifest can generate 100 distinct configs and that every generated config validates against the released framework `DatasetConfig` schema.

This is different from runtime scale/performance proof. Runtime concurrency, throughput and provider integration must be proven in an approved Fabric environment.

## 11. Commit and open a pull request

```bash
git status
git add .
git commit -m "bootstrap health domain metadata"
git push -u origin bootstrap/health
```

Open a PR.

The repository CI should block merge unless at least these checks pass:

- exact framework dependency pin;
- semantic metadata validation;
- bulk onboarding manifest validation;
- source compile;
- domain wheel build;
- exact released framework wheel download/checksum/install;
- cross-package tests;
- release-manifest generation;
- DEV/TEST(or UAT)/PROD deployment-plan generation.

Use branch protection in the company repo so CI and required review cannot be bypassed for production branches.

## 12. Create Fabric DEV / TEST / PROD workspaces

Create separate workspaces, for example:

```text
health-dev
health-test
health-prod
```

Use company naming/tagging/capacity conventions.

Microsoft's current Fabric CI/CD guidance is to connect the developer workspace to Git and promote tested content through deployment pipelines or an equivalent API-driven release process.

Keep runtime state environment-local. Do not copy DEV watermarks/run history/quarantine state into PROD as release artifacts.

## 13. Connect the DEV workspace to Git

In Fabric DEV workspace settings:

1. Open Git integration / source control.
2. Connect the approved GitHub organization/repository.
3. Select the approved integration branch/folder.
4. Sync the workspace only after the PR-controlled source is ready.
5. Review conflicts before applying updates.

The Git repository is the review/audit boundary. Do not use ad-hoc portal edits as the only copy of production logic.

Reference: Microsoft Learn, "Introduction to CI/CD in Microsoft Fabric" and "CI/CD workflow options in Fabric".

## 14. Create the Fabric Environment and install immutable wheels

In the DEV workspace:

1. Create a Fabric Environment item, for example `env-health-dev`.
2. Select the approved Fabric Spark runtime.
3. Add approved public dependencies if needed.
4. Add the immutable `fabric-data-framework` wheel as a custom library.
5. Add the immutable domain wheel built by CI as a custom library.
6. Publish the Environment changes.
7. Attach the Environment to domain notebooks and/or Spark Job Definitions.

Do not make every production notebook execute `%pip install` for the framework. The Environment is the normal production dependency boundary for Spark notebooks/jobs.

Fabric environments can be versioned/synchronized through Git integration and promoted through deployment pipelines. Changes synced from Git must be published before they become the live Environment state.

Reference: Microsoft Learn, "Create, configure, and use an Environment in Fabric", "Manage libraries in Fabric environments", and "Use Git integration and deployment pipelines for environments".

## 15. Configure source connections and secrets

The semantic dataset config contains logical references such as:

```json
{
  "connection_ref": "health_sql_readonly"
}
```

Create/bind the actual Fabric connection/identity in the target environment using the company-approved mechanism.

Keep secrets out of Git. Prefer managed/workspace identity or approved secret management over embedded credentials.

The exact mapping from `connection_ref` to a Fabric connection is environment-specific and belongs in deployment bindings/configuration, not in the semantic dataset hash.

## 16. Create or bind Lakehouse/Warehouse targets

Provision the required DEV target items according to the platform/infrastructure standard.

The domain release should keep logical target semantics stable while `deploy/bindings.dev.json`, `deploy/bindings.uat.json` and `deploy/bindings.prod.json` resolve environment-specific physical targets.

Do not place DEV/PROD workspace IDs directly in `config/datasets/*.json`.

## 17. Use thin Fabric drivers, not 100 copied notebooks

The target runtime shape is metadata-driven:

```text
Fabric Pipeline / scheduler
        |
        +-- dataset_id / execution_group
        v
thin Notebook or Spark Job Definition
        |
        v
fabric-data-framework runtime
        |
        +-- read DatasetConfig
        +-- capture
        +-- normalize / DQ
        +-- apply
        +-- reconcile
        +-- commit checkpoint/state
```

For 100 tables, prefer a small number of driver items plus execution groups rather than 100 copies of the same ingestion/SCD code.

A sensible first grouping for the example is:

```text
health_full_refresh   50
health_scd2           20
health_scd1           20
health_debezium       10
```

These are scheduling/concurrency groups, not separate repositories.

## 18. DEV integration sequence

Do not switch all 100 datasets on at once on the first real Fabric proof.

Recommended sequence:

1. one FULL + REPLACE representative;
2. one WATERMARK + SCD1 representative;
3. one WATERMARK + SCD2 representative;
4. one Debezium/CDC representative;
5. retry/idempotency/reconciliation failure drills;
6. a small mixed execution group;
7. controlled concurrency ramp;
8. then onboard the remaining datasets by metadata once the patterns are proven.

For each representative, retain evidence for:

- source row/change boundary;
- target row/state result;
- checkpoint/watermark result;
- DQ/quarantine result;
- reconciliation result;
- retry/rerun idempotency;
- delete behavior where applicable;
- run/audit identity and released framework/domain versions.

This separates "100 configs validate" from "the provider/runtime path is production proven".

## 19. Debezium/CDC boundary

For the ten Debezium rows, `capture_strategy=CDC` expresses the semantic contract. The real provider integration must also prove:

- topic/source mapping;
- key extraction;
- ordering/offset semantics;
- update before/after payload handling;
- tombstone/delete handling;
- duplicate/replay behavior;
- checkpoint ownership;
- outage/recovery behavior.

Framework source after v0.3.0 contains newer execution/capability-profile concepts, but this domain must not depend on unpublished framework source. Upgrade only after the relevant framework release is immutable and CI has switched the exact pin.

## 20. Produce the immutable release/deployment plan

After domain tests pass, build the framework release contract using the released CLI. Example:

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

Then plan each environment with the SAME release manifest:

```bash
fabric-framework deployment-plan \
  --manifest release-manifest.json \
  --bindings deploy/bindings.dev.json \
  --output dev-plan.json

fabric-framework deployment-plan \
  --manifest release-manifest.json \
  --bindings deploy/bindings.uat.json \
  --output test-plan.json

fabric-framework deployment-plan \
  --manifest release-manifest.json \
  --bindings deploy/bindings.prod.json \
  --output prod-plan.json
```

The domain Git SHA/config bundle/framework version is immutable across promotion. Only approved environment binding values differ.

## 21. Promote DEV -> TEST -> PROD

Use Fabric Deployment Pipelines or an approved API-driven equivalent.

Recommended promotion gate:

```text
PR merged
  -> CI green
  -> immutable domain/framework artifacts
  -> sync/deploy DEV
  -> DEV integration evidence green
  -> deploy TEST
  -> automated + business/UAT checks
  -> release approval
  -> deploy PROD
  -> production smoke + reconciliation
```

Do not rebuild the package separately for PROD. Promote the same tested immutable artifact/release identity.

## 22. Go-live checklist

Before production enablement confirm:

- [ ] repo ownership/security boundary is correct;
- [ ] exact framework version is pinned;
- [ ] all dataset configs pass framework schema validation;
- [ ] PK/watermark/order semantics are source-owner confirmed;
- [ ] delete fidelity is documented for every pattern;
- [ ] SCD2 claims do not exceed source history fidelity;
- [ ] secrets are outside Git;
- [ ] DEV/TEST/PROD use separate environment-local runtime state;
- [ ] Environment contains immutable framework/domain wheels and is published;
- [ ] thin runtime driver uses metadata, not copied per-table algorithm code;
- [ ] representative FULL/SCD1/SCD2/CDC paths have approved Fabric integration evidence;
- [ ] retry/replay/reconciliation failure behavior is tested;
- [ ] concurrency/capacity limits are measured before enabling all 100 tables;
- [ ] release manifest and environment deployment plans are retained;
- [ ] production promotion has approval and rollback procedure.

## 23. Current reference limitation

As of 2026-08-30, this repository itself still has not executed a real Customer deployment into a Fabric workspace. The checked-in deployment bindings are reference values and no production Pipeline/Notebook item is yet proven here.

This runbook defines the procedure to perform that proof; it must not be cited as evidence that the external Fabric integration has already happened.

When a real approved Fabric integration is executed, update `docs/CURRENT_STATUS.md` with the exact workspace/environment proof, release identity and retained evidence references.
