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

The machine-readable pin is `certification/framework-executable.json`. It selects exact bytes for testing; it does not freeze a candidate or authorize release.

Framework 0.4 is development/unreleased. Stop on every real FAIL. Never invent UUIDs, evidence or PASS state.

## 1. Prepare DEV once

See `DEPLOY_CERTIFICATION_FABRIC_ITEMS.md`.

Create the real non-secret environment config from:

```text
certification/config/environments/DEV.example.json
```

and commit:

```text
certification/config/environments/DEV.json
```

Then run:

```powershell
az login
gh auth status
python certification/bootstrap.py --apply --environment DEV
```

No normal operator SQL server/database flags are required; bootstrap discovers SQL targets from the exact Fabric items selected by the environment config.

Successful preparation must end with:

```text
bootstrap_status = READY
certification_result = NOT_RUN
release_authorized = false
```

If bootstrap fails, **stop**. Do not fabricate files, UUIDs or evidence.

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
exact Framework files in OneLake
exact Customer input bundle in OneLake
Control Plane schema + exact certification semantic metadata
```

The setup seed job created provider source tables. That setup execution is **not** certification evidence.

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

Repository labels:

```text
fabric_rest = azure-cli
sql_runtime = fabric-user
```

Key Vault is optional. Ordinary Fabric SQL access does not imply Warehouse admin/session-control authority.

## 4. Bounded/read-safe first run

Open/run:

```text
framework-certification-runner
```

Its source equivalent invokes:

```python
from fabric_data_framework.certification import certify, print_certification_summary
```

The runner verifies the staged exact Framework wheel and Customer input bundle. Live mutation authorizations default to `False`:

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

A real bounded `FAIL` is a hard stop. A legitimate `BLOCKED`/`NOT_RUN` is correct when a strict prerequisite is not authorized/configured.

## 5. Explicit later live stages

Only after bounded checks pass and required reviews/permissions exist should exact live stages be enabled:

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

Repository ownership makes deployment identity reproducible; provider `Completed` alone is not PASS. Framework evidence gates remain authoritative.

Never infer Warehouse session-termination authority from normal Fabric SQL access.

## 6. Current strict blockers

Source intentionally remains fail-closed for:

```text
control_plane_external_evidence_incomplete
control_plane_external_evidence_not_review_bound
warehouse_real_fault_controller_not_configured
```

Therefore bootstrap READY can coexist with release blockers.

## 7. Retain only genuine evidence

Keep non-secret facts only:

```text
exact Framework SHA/main-CI/artifact/wheel SHA
exact Customer source/input identity
bootstrap result with real resource/item UUIDs + definition hashes
seed setup job ID/status clearly labeled setup-only
Framework-generated PASS/FAIL/BLOCKED/NOT_RUN output
review-bound external evidence when it actually exists
```

Do not retain tokens/passwords. Update `docs/CURRENT_STATUS.md` only with facts actually evidenced by a real run.
