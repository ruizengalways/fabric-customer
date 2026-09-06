# Runbook — Test the current Framework in company Fabric

Audience: a data engineer validating the current Framework 0.4 executable in an isolated company Fabric DEV workspace.

This is the **current** real-Fabric operator path. It intentionally excludes superseded manual/PR-history recovery procedures.

## 1. Hard boundary

Production remains:

```text
fabric-data-framework==0.3.0
```

Framework 0.4 is development/unreleased. This runbook does not freeze a candidate or authorize release.

For every run:

- use an isolated or explicitly approved DEV workspace;
- use the exact Framework artifact recorded in `docs/CURRENT_STATUS.md`;
- stop on any real bounded FAIL;
- never invent missing UUIDs, evidence or PASS state;
- never paste tokens, passwords or secret values into Git, Notebook source, Pipeline JSON, retained evidence or chat.

## 2. Exact Framework bytes

Current executable identity:

```text
Framework SHA       17fbbd8ed2afb14771748a25d3e12d9bf63fe986
Framework CI run    34010629765
artifact ID         9982333832
artifact name       framework-wheel-17fbbd8ed2afb14771748a25d3e12d9bf63fe986
wheel               fabric_data_framework-0.4.0-py3-none-any.whl
wheel SHA256        0d7d351548712db3293b00a3b8eb968387f573b542d8fe506c9436a1b9b0a834
```

Keep the artifact's `CANDIDATE.json`, `SHA256SUMS` and wheel together. Verify the wheel bytes before semantic testing.

If Framework executable source changes, do not reuse this identity. Re-read `fabric-data-framework/docs/machine/STATE.md` and resolve the new exact artifact first.

## 3. Default authentication model

The ordinary data-engineer path is Fabric-native:

```text
Fabric REST API -> current Azure CLI signed-in user
Fabric SQL DB   -> signed-in Fabric Notebook user via Microsoft Entra
Warehouse       -> signed-in Fabric Notebook user via Microsoft Entra for ordinary SQL work
```

Defaults:

```text
--auth-mode azure-cli
--runtime-auth-mode fabric-user
```

Key Vault is optional enterprise integration, not a prerequisite. Environment-token auth is an optional automation lane.

Warehouse administrator/session-termination authority is separate from normal Fabric user SQL access and remains explicitly gated.

## 4. Prepare local/jumpbox access

From the machine where `fabric-customer` is cloned:

```powershell
az login
```

If the corporate identity has Fabric access but no Azure subscription:

```powershell
az login --allow-no-subscriptions
```

Confirm you can read the target Fabric workspace/items before mutating anything. You do not need to print or copy the Fabric access token.

The canonical deployment procedure is:

```text
docs/runbooks/DEPLOY_CERTIFICATION_FABRIC_ITEMS.md
```

## 5. Deploy the repository-owned Notebook and Pipeline

Have these non-secret values ready:

```text
DEV certification workspace UUID
Control Plane Fabric SQL server hostname
Control Plane database name
Warehouse SQL server hostname
Warehouse database name
```

Default command:

```powershell
python certification/fabric_items/deploy_fabric_items.py `
  --apply `
  --environment DEV `
  --workspace-id <CERTIFICATION_WORKSPACE_UUID> `
  --control-plane-server <CONTROL_PLANE_FABRIC_SQL_HOSTNAME> `
  --control-plane-database <CONTROL_PLANE_DATABASE_NAME> `
  --warehouse-server <WAREHOUSE_SQL_HOSTNAME> `
  --warehouse-database <WAREHOUSE_DATABASE_NAME>
```

The deployer must produce:

```text
build/fabric-items/deployment-result.json
```

Retain the real Notebook/Pipeline UUIDs and definition hashes from that file. A successful deployment deliberately remains:

```text
certification_result = NOT_RUN
```

**Stop** if deployment exits non-zero, duplicate display names are found, authentication fails, a binding is rejected, Fabric REST fails or a long-running operation fails/times out.

## 6. Put the exact Framework artifact in the certification Lakehouse

Use the conventional location:

```text
Files/framework_cert/
```

Expected files:

```text
CANDIDATE.json
SHA256SUMS
fabric_data_framework-0.4.0-py3-none-any.whl
```

Keep exactly one Framework wheel for the run.

## 7. Run bounded certification first

Install the exact wheel in the certification Notebook/session, restart the session if Fabric requires it, then run:

```python
from fabric_data_framework.certification import certify, print_certification_summary

report = certify(spark=spark)
print_certification_summary(report)
```

The bounded suite covers the current core checks, including exact identity, Lakehouse smoke, FULL/REPLACE, WATERMARK/SCD1, WATERMARK/SCD2, retry/idempotency and reconciliation fail-closed behavior.

Expected output root:

```text
Files/framework_cert/certification-output/
```

A legitimate `PARTIAL` can be correct when environment-specific live stages are not configured. A real bounded `FAIL` is a hard stop.

## 8. Add exact Customer certification inputs for live stages

Only after bounded checks pass, use the exact Customer input artifact generated for the intended Customer source and Framework executable.

Source producer:

```text
.github/workflows/candidate-business-path-inputs.yml
```

Extract the retained bundle under:

```text
/lakehouse/default/Files/framework_cert/customer-inputs/
```

Expected shape:

```text
customer-inputs/
  INPUTS.json
  runner-config.json
  release-manifest.json
  project/
  dist/
```

Use real physical bindings. The Notebook/Pipeline deployment result supplies the real certification Pipeline UUID; Copy/Spark/item-read bindings remain separate real item IDs. Do not edit an exact retained bundle by hand to swap hashes or fabricate identifiers.

## 9. Live certification remains fail-closed

Proceed only for explicitly approved mutations. The full path can cover:

```text
bounded suite
-> Fabric item read
-> real Fabric SQL Control Plane conformance/evidence
-> repository-owned Pipeline + durable Framework outcome
-> Copy
-> Spark
-> Warehouse normal commit
-> separately approved Warehouse fault/recovery drill
-> live FULL/SCD1/SCD2/retry/reconciliation business paths
-> strict evidence merge
```

Missing configuration, review or authority remains `BLOCKED` / `NOT_RUN`. Ordinary Fabric user access must never be promoted into Warehouse session-control authority.

Current strict release blockers remain documented in `docs/CURRENT_STATUS.md` and `fabric-data-framework/docs/machine/STATE.md`.

## 10. After the run

Retain only non-secret evidence:

- exact Framework SHA, CI run, artifact ID and wheel SHA256;
- exact Customer source/input identity;
- real workspace/item UUIDs;
- deployment definition hashes;
- Framework-generated certification/evidence output;
- explicit PASS / FAIL / BLOCKED / NOT_RUN results.

Then update `docs/CURRENT_STATUS.md` only with facts actually evidenced by the run. Do not add another PR-number recovery-history section.
