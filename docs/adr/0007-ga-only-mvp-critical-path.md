# ADR-0007: GA-Only Services for MVP Critical Path

- Status: Accepted
- Date: 2026-06-01
- Deciders: Architecture Working Group
- Related Decision ID: AR-D-001
- Related Requirements: NFR-COMP-001, NFR-COMP-004, NFR-SEC-001, NFR-MAINT-004

## Context

The platform targets regulated Swiss healthcare operations. MVP release cannot
depend on preview capabilities for critical workflows because preview lifecycle,
regional availability, and support commitments can change.

## Decision

For MVP critical-path capabilities, only generally available Azure and Fabric
services are permitted in production scope.

## Consequences

- MVP scope is constrained to GA-ready feature sets.
- Preview features may be explored in non-production only.
- Delivery risk and compliance uncertainty are reduced for regulated workloads.

## Compliance Notes

This decision strengthens control for Swiss residency and operational assurance
requirements by reducing reliance on non-contractual preview behavior.
