# Runbooks

Runbooks in this directory describe domain-repository procedures while linking to generic Framework runtime semantics where appropriate.

## Available

### `TEST_FRAMEWORK_IN_COMPANY_FABRIC.md`

**Use this next for the current project state.** Customer-side recovery wrapper for the first bounded company-Fabric Notebook validation. It records the exact Framework main run/artifact to use, the corporate DEV/Lakehouse setup, the PASS/FAIL/NOT RUN boundary, Admin Override policy, and the link to the Framework executable Notebook cells.

This first test deliberately does not require candidate freeze and does not pretend unavailable Warehouse fault-injection coverage passed.

### `CERTIFY_FRAMEWORK_0_4.md`

Framework 0.4 certification/release runbook. It now distinguishes:

```text
Lane A — bounded company Fabric Notebook/manual validation
Lane B — full automated evidence-based release certification
```

Use Lane A now. Lane B remains blocked until the real reviewed control-plane evidence/review binding and approved real Warehouse ambiguous-COMMIT fault controller exist.

### `BUILD_NEW_DOMAIN_PROJECT.md`

Canonical end-to-end enterprise project runbook covering:

- jumpbox/VDI Python/Git setup;
- released framework dependency vs exact framework-next compatibility lane;
- framework-owned `project-init` adoption;
- source inventory before DatasetConfig authoring;
- 100-table Health manifest onboarding;
- semantic selections and `project-validate`;
- explicit Debezium `EXTERNAL_CDC / debezium_kafka_v1` contract;
- local tests and GitHub PR/CI gates;
- immutable release artifacts and non-secret environment bindings;
- Fabric DEV/TEST/PROD setup;
- thin metadata-driven runtime drivers;
- representative FULL/SCD1/SCD2/Debezium live evidence sequence;
- DEV -> TEST -> PROD promotion and go-live checklist.

The runbook deliberately distinguishes:

```text
released dependency proof
static project-contract proof
runtime correctness proof
real Fabric/provider proof
capacity/performance proof
```

Do not treat one proof class as another.

## Recovery order for a new conversation

For Framework 0.4 work, read:

```text
1. docs/CURRENT_STATUS.md
2. docs/runbooks/TEST_FRAMEWORK_IN_COMPANY_FABRIC.md
3. fabric-data-framework/docs/machine/STATE.md
4. fabric-data-framework/docs/human/FIRST_FABRIC_NOTEBOOK_TEST.md
```

Those files together contain the exact current artifact identity, release boundaries, bounded test procedure and the later strict release lane.

## Future operational runbooks

Add source-outage handling, reconciliation investigation, backfill/replay and deployed smoke-test procedures only when the corresponding deployed behaviors have real retained evidence.

Generic Framework recovery/state semantics remain documented in `fabric-data-framework`.
