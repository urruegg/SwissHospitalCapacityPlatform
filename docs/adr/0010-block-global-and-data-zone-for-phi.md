# ADR-0010: Block Global and Data Zone Inference Modes for PHI Flows

- Status: Accepted
- Date: 2026-06-01
- Deciders: Architecture Working Group
- Related Decision ID: AR-D-004
- Related Requirements: NFR-COMP-001, NFR-COMP-004, NFR-SEC-002

## Context

Global and Data Zone deployment types can process requests outside a specific
Swiss region boundary. For PHI-sensitive workflows, this conflicts with strict
residency expectations.

## Decision

Global and Data Zone inference deployment types are prohibited for
PHI-sensitive copilot traffic in MVP and production scope.

## Consequences

- Architecture and policy must enforce regional-only deployment for PHI paths.
- Validation gates must detect and block non-compliant deployment modes.
- Non-PHI workloads may be evaluated separately under explicit governance.

## Governance Notes

Any exception requires formal compliance approval and explicit risk acceptance.
