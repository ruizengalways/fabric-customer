# Runbook — Test the current Framework in company Fabric

Audience: data engineers validating the current Framework 0.4 executable in an isolated company Fabric DEV workspace.

## Hard boundary

Production remains:

```text
fabric-data-framework==0.3.0
```

Current certification executable:

```text
Framework SHA       17fbbd8ed2afb14771748a25d3e12d9bf63fe986
Framework CI run    34010629765
artifact ID         9982333832
wheel               fabric_data_framework-0.4.0-py3-none-any.whl
wheel SHA256        0d7d351548712db3293b00a3b8eb968387f573b542d8fe506c9436a1b9b0a834
```

The machine-readable pin is `certification/framework-executable.json`. It selects exact bytes for testing; it does not freeze a candidate or authorize a release.

Framework 0.4 is development/unreleased. Stop on every real FAIL. Never invent UUIDs, evidence, or PASS state.

## 1. Prepare the environment once

See `DEPLOY_CERTIFICATION_FABRIC_ITEMS.md`.

Create and commit the real non-secret environment config from the example, then run:

```powershell
az login
gh auth status
python certification/bootstrap.py --apply --environment DEV
```

No normal operator `--control-plane-server`, `--control-plane-database`, `--warehouse-server`, or `--warehouse-database` flags are required. The SQL targets are discovered from the exact Fabric items selected by `certification/environments/DEV.json`.

Successful preparation must end with:

```text
bootstrap_status = READY
certification_result = NOT_RUN
release_authorized = false
```

If bootstrap fails, **stop**. Do not continue by manually fabricating files, UUIDs, or evidence.

## 2. What READY means

Bootstrap has prepared and bound:

```text
schema-enabled dedicated certification Lakehouse
Fabric SQL Database Control Plane
certification Warehouse + fixture tables
repository-owned seed Spark Job Definition
repository-owned real Copy Job
repository-owned real capture Spark Job Definition
framework-certification-runner Notebook
framework-certification-worker Notebook
framework-certification-child Pipeline
exact Framework CANDIDATE.json + SHA256SUMS + wheel in OneLake
exact Customer input bundle in OneLake
Control Plane schema + exact certification semantic metadata
```

The setup seed job has also created the real Lakehouse provider source tables. That setup job is **not** certification evidence.

READY is preparation only.

## 3. Authentication model

Default lane:

```text
local Fabric REST bootstrap -> current Azure CLI signed-in user
local OneLake staging       -> same user, Storage audience token
local SQL bootstrap         -> same user, database.windows.net token + ODBC 18+
Notebook SQL runtime        -> signed-in Fabric Notebook user via Microsoft Entra
Key Vault                   -> optional enterprise integration
```

Default mode labels used by the repository contracts:

```text
fabric_rest = azure-cli
sql_runtime = fabric-user
```

Key Vault is optional enterprise integration; it is not required for the default user lane.

Warehouse Admin/session-control authority remains separate from ordinary Fabric user SQL access.

## 4. Bounded/read-safe first run

Open/run the deployed:

```text
framework-certification-runner
```

Its source equivalent still invokes:

```python
from fabric_data_framework.certification import certify, print_certification_summary
```

The runner verifies the exact staged Framework wheel before installation and supplies the exact Customer input bundle. Live mutation authorizations default to `False`:

```text
Control Plane conformance writes       false
Control Plane migration                false
Pipeline execution                     false
Copy/Spark capture execution           false
Warehouse execution                    false
Warehouse fault injection              false
Warehouse session termination          false
business-path execution/mutation       false
```

A real bounded `FAIL` is a hard stop. A legitimate `BLOCKED`/`NOT_RUN` remains correct when a strict prerequisite has not been authorized/configured.

## 5. Explicit live stages

Only after bounded checks pass and the required reviews/permissions are available should the exact live stages be enabled.

The possible chain remains:

```text
bounded suite
-> Fabric item read
-> real Fabric SQL Control Plane conformance/evidence
-> repository-owned child Pipeline + durable Framework outcome
-> repository-owned Copy Job capture
-> repository-owned Spark Job Definition capture
-> Warehouse normal commit
-> separately authorized Warehouse fault/recovery drill
-> FULL/SCD1/SCD2/retry/reconciliation business paths
-> strict evidence merge
```

The Copy/Spark items being repository-owned means their deployment identity is reproducible. It does **not** mean provider completion alone is PASS: the Framework capture adapter, Customer observer, exact release bindings, durable prerequisites, and evidence merge still decide the certification result.

Never infer Warehouse session-termination authority from ordinary Fabric SQL access.

## 6. Current strict blockers

Source intentionally remains fail-closed for:

```text
control_plane_external_evidence_incomplete
control_plane_external_evidence_not_review_bound
warehouse_real_fault_controller_not_configured
```

Therefore a bootstrap READY is expected to coexist with strict blockers. It does not remove the current release boundary.

## 7. Retain only genuine evidence

Keep only non-secret facts:

```text
exact Framework SHA/main-CI/artifact/wheel SHA
exact Customer source/input identity
bootstrap result with real resource/item UUIDs + definition hashes
real seed setup job ID/status clearly labeled setup-only
Framework-generated PASS/FAIL/BLOCKED/NOT_RUN certification output
review-bound external evidence when it actually exists
```

Do not retain tokens/passwords. Update `docs/CURRENT_STATUS.md` only with facts actually evidenced by the run; do not add PR-number recovery history.
