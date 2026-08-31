# Control-plane external evidence review binding

This runbook defines the fail-closed source-control boundary for the real enterprise control-plane evidence required before a Fabric Framework 0.4 candidate may be frozen.

It does **not** create live Fabric evidence, does **not** certify a control plane, and does **not** replace the real enterprise review. It only prevents a complete-looking set of arbitrary strings from being treated as a configured live prerequisite.

## Current release truth

The current source-controlled files remain intentionally incomplete:

- `certification/project/config/certification/integration/control-plane-external-evidence.json` contains the seven external evidence categories and currently retains `null` placeholders.
- `certification/project/config/certification/integration/control-plane-external-evidence-review.json` contains the review binding and currently retains `null` placeholders.
- Customer production remains pinned to `fabric-data-framework==0.3.0`.
- No 0.4 candidate is frozen by this runbook or by the review-binding code.

While the seven evidence references are incomplete, the candidate-input builder must continue to report:

`control_plane_external_evidence_incomplete`

Only after all seven evidence references are populated does the builder evaluate the review binding. A complete evidence set without an exact review binding must fail closed with:

`control_plane_external_evidence_not_review_bound`

## Required review binding

`control-plane-external-evidence-review.json` has exactly five fields:

```json
{
  "environment": "DEV",
  "control_plane_profile": "fabric_sql_database_v1",
  "review_record_reference": "ticket:SEC-1234",
  "evidence_set_reference": "catalog:control-plane-dev-20260831",
  "reviewed_at_utc": "2026-08-31T07:00:00Z"
}
```

The example above is illustrative syntax only. Do not copy those values as evidence.

Rules:

1. `environment` must be the exact protected certification environment: `DEV`, `UAT`, or `PROD`.
2. `control_plane_profile` must be the exact selected production-candidate profile: `fabric_sql_database_v1` or `azure_sql_database_v1`.
3. `review_record_reference` must be a non-secret opaque identifier for the real enterprise approval/review record. Do not put credentials or signed URLs here.
4. `evidence_set_reference` must be a non-secret opaque identifier for the reviewed evidence bundle/catalog entry.
5. `reviewed_at_utc` must be an ISO-8601 timestamp with an explicit UTC offset.
6. The review binding must match the `--environment` and `--control-plane-profile` used to build the exact Customer candidate inputs. Reusing a DEV review for UAT/PROD, or a Fabric SQL review for Azure SQL, is rejected.

## Operator sequence

1. Obtain the real enterprise evidence for all seven categories in `control-plane-external-evidence.json`.
2. Have the appropriate enterprise reviewers approve that evidence for one exact protected environment and one exact control-plane profile.
3. Record only stable, non-secret references in the two source-controlled JSON files. Keep passwords, tokens, database URLs, connection strings, signed URLs, and other secrets in the protected runtime secret store.
4. Open a PR. Review both the evidence references and review-binding metadata. Do not merge merely to make CI green.
5. Run Customer `customer-ci` and `customer-certification-contract` and verify that the candidate-input builder rejects environment/profile mismatches.
6. After merge, verify the same checks on `main`.
7. Even after this blocker clears, do not freeze a Framework candidate until the separate real Warehouse/session ambiguous-COMMIT fault-controller prerequisite is also configured and reviewed.

## What this gate proves — and does not prove

This gate proves only that the exact Customer input producer carries a source-controlled review record bound to the same environment/profile used to build the retained candidate inputs.

It does not independently validate the external ticketing/catalog system, does not contact Microsoft Fabric, does not execute control-plane probes, and does not claim that the referenced controls passed. Those are later live-environment certification responsibilities.
