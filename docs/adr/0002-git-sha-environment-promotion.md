# ADR 0002 — Promote the same Git SHA through environments

Status: Accepted
Date: 2026-08-28

## Context

Deploying the latest branch state independently to DEV, UAT and PROD makes it impossible to prove that a tested revision is the revision that reached production.

## Decision

Use trunk-based delivery: feature branch -> PR -> CI -> merge -> immutable Customer Git SHA. Promote that same SHA/artifact through DEV -> UAT -> PROD.

Environment-specific values are resolved at deployment/runtime through approved configuration/infrastructure contracts; they do not require environment branches.

Do not use long-lived `dev`, `uat` and `prod` branches as environment state.

Deployment provenance will record Customer Git SHA and exact framework version, with Customer release version when releases are introduced.

## Consequences

- Promotion is auditable and reproducible.
- Environment drift is reduced.
- Delivery tooling must distinguish immutable application revision from environment-specific configuration.
