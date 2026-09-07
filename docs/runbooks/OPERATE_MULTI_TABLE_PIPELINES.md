# Runbook — Operate multi-table Fabric Pipelines

This is the normal customer/domain operations path, not Framework release certification.

Production remains pinned to:

```text
fabric-data-framework==0.3.0
```

Current source-controlled execution-group policy lives under:

```text
config/orchestration/execution-groups/
```

Do not create Framework-version policy directories. Upgrade the current contract in place through reviewed Git changes.

## 1. Product operating model

A 100-table domain should not be one sequential mega-Pipeline and should not require one bespoke Pipeline per table. Group datasets by runtime semantics/SLA, for example:

```text
health_full_refresh  50 FULL      -> REPLACE
health_scd2          20 WATERMARK -> SCD2
health_scd1          20 WATERMARK -> SCD1
health_debezium      10 CDC       -> UPSERT (Debezium/external CDC)
```

Each parent Pipeline stays thin:

```text
resolve exact execution_group work
-> bounded parallel dispatch
-> reusable Framework-owned dataset execution
-> durable per-dataset terminal outcome
-> dependency-aware BLOCKED propagation
-> wait for all runnable work
-> aggregate parent status
```

Default parent policy is `FAIL_AT_END`: one failed dataset does not cancel independent siblings, but the parent ends `FAILED` after all runnable work reaches terminal state.

```text
Dataset                     = fault-isolation/recovery unit
Execution group/Pipeline    = scheduling + aggregate-status unit
Customer repo               = WHAT to run
Framework                   = HOW to execute/recover safely
```

## 2. Configuration precedence

Shared defaults belong in reviewed execution-group policy, not copied into dozens of DatasetConfig files and not maintained as hidden Fabric UI state.

Framework 0.4 contract precedence is:

```text
DatasetConfig
-> execution-group quality defaults
-> execution-group per-dataset quality override
-> audited RuntimeOverride
```

Use per-dataset override only for a real semantic exception. RuntimeOverride is temporary incident control; durable intended behavior returns to Git.

## 3. DQ and quarantine

Recommended default:

```text
enabled = true
quarantine_enabled = true
quarantine_detail_mode = FULL
max_quarantine_rows = reviewed absolute ceiling
max_quarantine_fraction = reviewed percentage ceiling
```

When either budget is exceeded:

```text
persist immutable quarantine detail
-> dataset FAIL
-> do not commit target/state/watermark
-> independent siblings continue
-> parent eventually FAIL
```

Full PHI/PII quarantine payloads belong in governed data-plane storage. The Control Plane retains lineage/count/reason/reference metadata, not duplicate sensitive rows.

Do not disable DQ or inflate a threshold just to make a failed batch green.

## 4. First inspection after parent failure

Preserve the `pipeline_run_id`, then inspect:

```text
pipeline_run:
  status
  error_code
  error_message
  started_at
  completed_at

dataset_run:
  dataset_id
  status
  attempt
  error_code
  error_message
  retryable
  row accounting
  mutation counts
```

For failed/quarantined datasets inspect as applicable:

```text
step_run
reconciliation_result
quarantine_batch
dataset_attempt_lineage
target_operation / target_operation_event
watermark / checkpoint
```

A Fabric activity showing `Completed` is not enough to prove semantic success.

## 5. Recovery classification

Use the smallest safe recovery scope.

| Condition | Default action |
|---|---|
| explicit transient error + `retryable=true` | bounded `RETRY` with backoff |
| retry exhausted | investigate provider/capacity/connectivity, then approved `RETRY` |
| DQ threshold exceeded | fix data/rule, then quarantine `REPLAY` |
| DQ failure with quarantine disabled | fix data/rule/config, then audited `RETRY` |
| reconciliation failure | investigate source/Bronze/target/mapping/invariants first |
| `BLOCKED_DEPENDENCY` | recover upstream first |
| `UNKNOWN_COMMIT` | reconcile target-operation evidence before any retry |
| bounded known source/time gap | audited `BACKFILL` |
| authoritative reset required | approved `FULL_REBUILD` |

Whole-Pipeline **blind retry** is not the default incident response.

## 6. `UNKNOWN_COMMIT`

This is a special safety boundary:

```text
operation outcome uncertain
-> read operation journal + target evidence

COMMITTED
  -> converge success; DO NOT write again

NOT_COMMITTED
  -> safe bounded retry may proceed

UNRESOLVED
  -> stop automation; operator investigation
```

Never infer target outcome from a client timeout or Fabric UI activity status.

## 7. `RETRY`

Use `RETRY` when the original logical scope remains correct and execution is safe to repeat.

Required properties:

```text
immutable root/previous attempt lineage
bounded attempts
provider-appropriate backoff
deterministic/idempotent target semantics
failed attempt does not advance checkpoint/watermark
unknown target outcome reconciled first
```

Do not manually reset a watermark simply to force retry.

## 8. `REPLAY`

Use `REPLAY` for retained quarantine payload after data/rule correction:

```text
identify exact quarantine_id(s)
-> validate immutable payload/source identity
-> audited ReprocessRequest(run_mode=REPLAY)
-> current approved mapping/DQ/apply
-> target + reconciliation PASS
-> mark original quarantine rows replayed
```

Original quarantine evidence remains for audit.

## 9. `BACKFILL`

Use only for a known bounded omission such as a date range, partition or source-position interval. Record reason/requestor/approved scope/expected impact before execution and reconcile exactly that scope afterward.

## 10. `FULL_REBUILD`

`FULL_REBUILD` is destructive/high blast radius, not a convenient retry mode. Before use verify source reconstructability, delete/history semantics, downstream impact, capacity/window, rollback path and absence of unresolved ambiguous commit.

For SCD2, never claim historical fidelity the source cannot reproduce.

## 11. FULL / REPLACE repair

A partial source snapshot must not replace a good target.

```text
verify extract completeness
-> inspect DQ/reconciliation
-> prove target replace did not commit when gate failed
-> correct source/connection/rule
-> rerun only affected dataset/dependency chain
```

Do not loosen reconciliation to accept an incomplete snapshot.

## 12. WATERMARK / SCD1 / SCD2 repair

Inspect:

```text
watermark before
captured upper position
tie-breaker/overlap semantics
accepted + quarantined rows
target mutation result
reconciliation
watermark after
```

Watermark advances only after semantic commit gate PASS. A failed run that advanced state without proven target + reconciliation success is a data-integrity incident.

For SCD2 also validate current-row uniqueness, effective interval ordering and business-key history invariants.

## 13. Debezium / external CDC repair

External CDC owns its own progress/checkpoint. Framework must not invent a competing offset owner.

Check:

```text
connector/task health
source-log retention
partition/order position
last durable external checkpoint
Framework Bronze event identity/dedupe
apply/reconciliation result
```

If source-log retention has removed the missing range, do not claim lossless replay. Use an approved snapshot/reseed/reconciliation plan and document the fidelity boundary.

## 14. Dependency recovery

Example:

```text
patient_master FAIL
encounter_dim BLOCKED (depends on patient_master)
claim_fact PASS (independent)
```

Recover `patient_master`, prove success, then run the affected dependency chain. Do not rerun independent `claim_fact` just because it shared the same parent.

## 15. Concurrency and capacity

`max_concurrency` is a safety cap, not a performance target:

```text
start bounded
-> observe source throttling / Fabric capacity / queueing / duration
-> change one source-controlled cap
-> test in DEV/UAT
-> promote through Git
```

Never solve capacity pressure by disabling DQ or reconciliation.

## 16. Minimum alerts

Alert on at least:

```text
parent Pipeline FAILED
critical/high dataset failure
retry exhausted
UNKNOWN_COMMIT unresolved
DQ quarantine budget exceeded
quarantine writer unavailable
stale watermark/checkpoint beyond SLA
abnormal BLOCKED count
reconciliation failure
CDC lag beyond agreed RPO
```

Numeric thresholds are domain SLO/capacity decisions, not global copy-paste defaults.

## 17. Incident closure

An incident is not closed merely because the next Pipeline is green. Close only after:

```text
root cause identified
repair/reprocess scope recorded
reconciliation PASS for recovered scope
no unresolved commit remains
checkpoint/watermark is semantically correct
quarantine/replay lineage retained
temporary RuntimeOverride removed or promoted to reviewed Git config
monitoring confirms normal forward progress
```

## 18. New-domain reminder

```text
fabric-framework project-init <repo> --domain <domain>
-> DatasetConfig + semantic selections
-> config/orchestration/execution-groups
-> fabric-framework project-validate <repo>
-> domain CI
-> DEV/UAT failure/recovery tests
-> PROD only after operational acceptance
```

Repository boundaries follow ownership/security/compliance/release lifecycle, not FULL/SCD1/SCD2/Debezium technique.
