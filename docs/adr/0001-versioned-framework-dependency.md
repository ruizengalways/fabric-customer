# ADR 0001 — Versioned framework package dependency

Status: Accepted
Date: 2026-08-28

## Context

Customer must reuse platform behaviour without allowing framework changes to alter production domain behaviour implicitly. Depending on a mutable branch couples deployments and destroys reproducibility.

## Decision

`fabric-customer` consumes `fabric-data-framework` as an exact immutable released package version using semantic versioning, for example `fabric-data-framework==1.4.2`.

Framework updates reach Customer only through an explicit dependency-upgrade PR with CI. Customer and framework release versions remain independent.

Direct production dependencies on mutable refs such as `@main` are prohibited.

## Consequences

- Customer behaviour is reproducible and framework upgrades are reviewable.
- A framework release does not automatically change Customer PROD.
- CI/release automation must eventually make package publication and dependency provenance straightforward.
