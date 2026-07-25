# ADR-0006: Preview Features Are Non-Production for Regulated Data

- Status: Accepted
- Date: 2026-06-01
- Deciders: Architecture Working Group
- Related Decision ID: AR-D-006
- Related Requirements: NFR-COMP-001, NFR-SEC-001, FR-GOV-004, NFR-MAINT-002

## Context

Regulated healthcare workloads require predictable support and lifecycle
commitments. Preview features can change behavior, availability, and support
boundaries before GA.

## Decision

Any preview-only feature is classified as non-production for regulated data
unless an explicit exception is approved through governance review.

## Consequences

- Release gates must check feature maturity before production promotion.
- Exception process must capture owner, risk, compensating controls, and expiry.
- Governance evidence quality improves for audits and compliance reviews.

## Exception Rule

No exception is valid without written approval from security and compliance
owners and a documented rollback path.

The first governance-approved standing exception under this rule is recorded in
[ADR-0042](0042-prod-switzerland-north-ga-target-standing-preview-exception.md)
(PROD Switzerland North Curavias demo, synthetic/no-PHI).
