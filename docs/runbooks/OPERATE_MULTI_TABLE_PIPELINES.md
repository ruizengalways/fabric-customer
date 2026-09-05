# Operate Multi-Table Fabric Pipelines

This runbook is the normal business-operations path for Customer/domain Pipelines. It is not Framework release certification.

Current production dependency remains:

```text
fabric-data-framework==0.3.0
```

The execution-group policy examples under `examples/pipeline_development/framework_0_4/` are forward-looking 0.4 contracts. Do not move them into the production runtime or change the production pin before immutable Framework `v0.4.0` exists and migration is approved.

## 1. Product operating model

A 100-table domain should not be one sequential mega-Pipeline and should not require one bespoke Pipeline per table. Group tables by operational semantics and SLA:

```text
health_full_refresh  50 FULL      -> REPLACE
health_scd2          20 WATERMARK -> SCD2
health_scd1          20 WATERMARK -> SCD1
health_debezium      10 CDC       -> UPSERT (Debezium/external CDC)
```

Each parent Pipeline is thin:

```text
resolve exact execution_group work
-> bounded parallel dispatch
-> reusable Framework-owned dataset execution
-> durable per-dataset terminal outcome
-> dependency-aware BLOCKED propagation
-> wait for all runnable work
-> aggregate parent status
```

The recommended parent policy is `FAIL_AT_END`. A failed table does not cancel independent siblings, but the parent still ends `FAILED` after all runnable work is terminal.

This is the intended production failure boundary:

```text
Dataset = unit of fault isolation and recovery
Execution group / parent Pipeline = unit of scheduling and aggregate status
Domain repo = source of WHAT to run
Framework = source of HOW to execute/recover safely
```

## 2. Source-controlled defaults and overrides

Shared operating defaults belong in one reviewed execution-group policy, not copied into 20 or 50 table configs and not edited ad hoc in the Fabric UI.

Framework 0.4 precedence is:

```text
DatasetConfig
-> execution-group quality defaults
-> execution-group per-dataset quality override
-> audited RuntimeOverride
```

Use per-table override only for a real semantic exception. Examples:

- a regulated table can set `quarantine_enabled=false` so any bad row fails the dataset;
- a high-volume reference table can have a larger approved quarantine budget;
- a sensitive history table can use a much smaller quarantine threshold.

RuntimeOverride is temporary incident control. Once the incident is resolved, put the durable intended value back in Git and retire the temporary override.

## 3. DQ / quarantine production policy

Recommended default is DQ enabled, quarantine enabled, governed full detail, plus an explicit tolerance budget:

```text
enabled = true
quarantine_enabled = true
quarantine_detail_mode = FULL
max_quarantine_rows = approved absolute ceiling
max_quarantine_fraction = approved percentage ceiling
```

A few bad rows can be isolated while good rows continue only while the approved budget is respected. If either ceiling is exceeded:

```text
persist immutable quarantine detail first
-> dataset FAIL
-> do not commit target/state/watermark
-> independent siblings continue
-> parent eventually FAIL
```

Full quarantined business rows may contain PHI/PII. They belong in a governed data-plane location with least-privilege ACL, approved encryption, retention and audit. The Control Plane should retain lineage, counts, reason summary and a stable reference, not duplicate full sensitive rows.

Do not temporarily disable DQ or increase a threshold merely to make a failed batch green. Any emergency exception needs an owner, reason, expiry and subsequent Git correction.

## 4. What to inspect after a failed parent Pipeline

Start with the parent `pipeline_run` and preserve its `pipeline_run_id`.

Read:

```text
status
error_code
error_message
started_at
completed_at
```

Then inspect every `dataset_run` for that parent:

```text
dataset_id
status
attempt
error_code
error_message
retryable
row accounting
mutation counts
```

For failed/quarantined datasets, drill into:

```text
step_run
reconciliation_result
quarantine_batch
dataset_attempt_lineage
target_operation / target_operation_event where applicable
watermark / checkpoint state
```

Do not infer semantic success only because a Fabric activity says `Completed`.

## 5. Failure classification and repair

Use the smallest safe recovery scope.

| Observed condition | Default action | Why |
|---|---|---|
| explicit transient error and `retryable=true` | bounded `RETRY` with backoff | safe automatic recovery contract |
| retry exhausted | investigate provider/capacity/connectivity, then operator-approved `RETRY` | repeated transient failure may no longer be transient |
| DQ threshold exceeded | fix source data or reviewed rule, then quarantine `REPLAY` | retained bad rows are the exact recovery scope |
| DQ failure with quarantine disabled | fix data/rule/config, then audited `RETRY` | no partial clean-subset acceptance is allowed |
| reconciliation failure | compare source, Bronze, target, mapping and invariant before reprocess | retrying unchanged logic can reproduce corruption |
| `BLOCKED_DEPENDENCY` | recover upstream first, then affected dependency chain | blocked child is not the root cause |
| `UNKNOWN_COMMIT` / ambiguous target outcome | reconcile target-operation evidence before any retry | blind retry can duplicate mutation |
| known bounded source/time gap | audited `BACKFILL` | scope should be explicit and reviewable |
| authoritative reset is required | approved `FULL_REBUILD` | destructive/high-blast-radius path |

Never use whole-Pipeline blind retry as the default incident response.

## 6. Unknown commit decision tree

`UNKNOWN_COMMIT` is a special safety boundary.

```text
operation outcome uncertain
        |
        v
read operation journal + target evidence
        |
        +-- COMMITTED ------> mark/converge success; DO NOT write again
        |
        +-- NOT_COMMITTED --> safe bounded retry may proceed
        |
        +-- UNRESOLVED -----> stop automation; operator investigation
```

Do not guess from a client timeout. Do not retry because the Fabric UI looks failed. The mutation may already have committed.

For Warehouse ambiguous-COMMIT testing, only use the approved dedicated DEV evidence path. Never inject faults into a shared or PROD Warehouse.

## 7. RETRY

Use `RETRY` when the original logical scope is still correct and the failure is safe to execute again.

Required characteristics:

- immutable root/previous attempt lineage;
- bounded attempts;
- exponential or provider-appropriate backoff;
- deterministic/idempotent target semantics;
- no checkpoint/watermark advancement from a failed attempt;
- unknown target outcome reconciled before retry.

Do not manually reset watermark just to force a retry.

## 8. REPLAY

Use `REPLAY` for retained quarantine payload after the underlying data or DQ rule has been corrected and reviewed.

Safe sequence:

```text
identify exact quarantine_id(s)
-> validate immutable source_reference / payload identity
-> create audited ReprocessRequest(run_mode=REPLAY)
-> execute current approved mapping/DQ/apply path
-> require target + reconciliation gate PASS
-> only then mark original quarantine rows replayed
```

Original quarantine evidence is retained for audit; replay must not delete history merely because the replay succeeded.

## 9. BACKFILL

Use `BACKFILL` only for a known bounded omission, for example a defined date/time range or known source partition.

Before execution record:

```text
reason
requested_by
approved scope
start/end or source positions
expected target impact
```

After execution reconcile the bounded scope and confirm that normal forward checkpoint semantics remain intact.

## 10. FULL_REBUILD

`FULL_REBUILD` is not a convenient retry mode. Use it only when the target is authoritatively reconstructable and a full reset is the approved repair.

Before a rebuild verify:

- source is complete enough to reconstruct the target;
- delete/history semantics are understood;
- downstream blast radius is known;
- capacity/window is approved;
- restore/rollback path is understood;
- the current failure is not an unresolved ambiguous commit.

For SCD2, a rebuild can change history if the source cannot reproduce historical change fidelity. Never claim historical fidelity the source does not possess.

## 11. FULL / REPLACE specific repair

FULL snapshot ingestion has a destructive-risk guard: an incomplete source snapshot must not silently replace a good target.

When a full-refresh table fails:

1. confirm source extract completeness and expected row-count/order indicators;
2. inspect DQ and reconciliation evidence;
3. confirm target replace did not commit if the gate failed;
4. correct source/connection/rule issue;
5. rerun only the affected table or affected dependency chain.

If the source produced a partial snapshot, fix capture completeness. Do not loosen reconciliation to accept it.

## 12. WATERMARK / SCD1 / SCD2 specific repair

For watermark tables check:

```text
watermark before
captured upper position
tie breaker / overlap semantics
accepted + quarantined rows
target mutation result
reconciliation
watermark after
```

Watermark advances only after the semantic commit gate passes. If a failed run advanced state without proven target + reconciliation success, treat it as a data-integrity incident rather than a normal retry.

For SCD2 additionally verify current-row uniqueness, effective interval ordering and business-key history invariants.

## 13. Debezium / external CDC specific repair

The 10 CDC examples use Debezium/external CDC semantics. Their progress/checkpoint owner is external, so Framework must not invent a second competing offset owner.

Check:

```text
connector/task health
source log retention
partition/order position
last durable external checkpoint
Framework Bronze event identity/dedupe
apply/reconciliation result
```

If source log retention has already removed the missing event range, do not claim lossless replay. Escalate to an approved snapshot/reseed/reconciliation plan and document the fidelity boundary.

## 14. Dependency recovery

A downstream `BLOCKED` dataset should normally not be manually started before its failed prerequisite is recovered.

Example:

```text
patient_master FAIL
encounter_dim BLOCKED (depends on patient_master)
claim_fact PASS (independent)
```

Recover `patient_master`, prove its terminal success, then run the affected dependency chain. Do not rerun `claim_fact` merely because it shared the same parent Pipeline.

## 15. Concurrency and capacity

`max_concurrency` is a safety cap, not a performance target. Tune from measured source throttling, Fabric capacity, Warehouse/Spark concurrency and SLA evidence.

Industry-safe tuning process:

```text
start bounded
-> observe source throttling / CU / queueing / duration
-> change one source-controlled cap
-> test in DEV/UAT
-> promote through Git
```

Never solve capacity pressure by disabling reconciliation or DQ.

## 16. Alerts and operational SLOs

At minimum alert on:

- parent Pipeline `FAILED`;
- critical/high dataset failure;
- retry exhausted;
- `UNKNOWN_COMMIT` unresolved;
- DQ quarantine budget exceeded;
- quarantine payload writer unavailable;
- stale watermark/checkpoint beyond domain SLA;
- abnormal blocked-dataset count;
- reconciliation fail;
- CDC connector/checkpoint lag beyond agreed RPO.

Numeric thresholds belong to the domain SLO and capacity baseline; do not copy arbitrary numbers between domains.

## 17. Incident closure

An incident is not closed merely because the next Pipeline turns green.

Close only after:

```text
root cause identified
repair/reprocess scope recorded
reconciliation PASS for recovered scope
no unresolved commit remains
checkpoint/watermark is semantically correct
quarantine/replay lineage is retained
any temporary RuntimeOverride is removed or promoted to reviewed Git config
monitoring confirms normal forward progress
```

For material incidents, record whether preventive action belongs in domain metadata, source system, Framework generic capability, Fabric infrastructure or enterprise controls.

## 18. New-project checklist

For a new 100-table project:

```text
fabric-framework project-init <repo> --domain <domain>
-> author DatasetConfig / semantic selections
-> assign execution_group by runtime semantics/SLA
-> fabric-framework project-validate <repo>
-> add reviewed execution-group policy when Framework 0.4 is an approved dependency
-> CI
-> DEV/UAT deployment
-> controlled failure/recovery tests
-> PROD promotion only after domain operational acceptance
```

Keep repo boundaries based on ownership, security/compliance and release lifecycle, not on whether a table is FULL, SCD1, SCD2 or Debezium.
