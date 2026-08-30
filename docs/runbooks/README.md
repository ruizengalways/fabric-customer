# Runbooks

Runbooks in this directory describe domain-repository procedures that can be executed without duplicating generic framework runtime semantics.

## Available

### `BUILD_NEW_DOMAIN_PROJECT.md`

End-to-end enterprise project bootstrap and deployment runbook covering:

- jumpbox/VDI local environment setup;
- exact framework release installation;
- bulk 100-table manifest onboarding;
- local dry-run/config generation/tests;
- GitHub PR/CI/release flow;
- Fabric DEV/TEST/PROD workspace model;
- Fabric Environment + custom wheel setup;
- logical connection/secret boundary;
- metadata-driven thin driver pattern;
- representative FULL/SCD1/SCD2/Debezium integration proof;
- immutable release/deployment-plan creation;
- DEV -> TEST -> PROD promotion and go-live checklist.

## Future operational runbooks

Add source-outage handling, reconciliation investigation, backfill/replay and smoke-test procedures only when the corresponding deployed behaviours have real retained evidence.

Generic framework recovery/state semantics remain documented in `fabric-data-framework`.
