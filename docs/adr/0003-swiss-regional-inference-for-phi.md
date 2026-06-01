# ADR-0003: Swiss Regional Inference for PHI-Sensitive Copilot Traffic

- Status: Accepted
- Date: 2026-06-01
- Deciders: Architecture Working Group
- Related Decision ID: AR-D-003
- Related Requirements: NFR-COMP-001, NFR-COMP-004, NFR-SEC-003, NFR-AI-004

## Context

Copilot requests and responses can include PHI-sensitive operational context.
Data residency and healthcare controls require strict processing boundaries for
regulated scenarios.

## Decision

PHI-sensitive copilot inference must use Azure OpenAI Standard or Regional
Provisioned deployment types in Switzerland regions only.

PHI cross-region failover is disabled by default, including Switzerland North
to Switzerland West failover, unless a compliance-approved runbook exists.

## Consequences

- Deployment architecture must pin inference resources to Swiss regions.
- Operational runbooks must enforce residency-safe routing.
- Any PHI failover runbook must be explicitly approved before activation.
- Some model choices may be constrained by regional availability.

## Compliance Notes

This decision establishes a default Swiss-processing posture for regulated
inference workloads.
