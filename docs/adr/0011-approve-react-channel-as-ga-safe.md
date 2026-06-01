# ADR-0011: Approve Dedicated React Web App as GA-Safe Copilot Channel

- Status: Accepted
- Date: 2026-06-01
- Deciders: Architecture Working Group
- Related Decision ID: AR-D-005
- Related Requirements: FR-CX-001, FR-CX-002, FR-GOV-006, NFR-MAINT-001

## Context

Operations teams need a reliable copilot experience channel even when Microsoft
365 Copilot readiness, licensing, or rollout constraints are present.

## Decision

A dedicated React web app is approved as a GA-safe copilot experience channel,
provided backend data and AI services follow Swiss residency and governance
constraints.

## Consequences

- Experience delivery is decoupled from Microsoft 365 Copilot readiness.
- Additional application security, telemetry, and maintenance controls are
  required.
- Shared grounding and audit APIs are needed to prevent channel drift.

## Operational Notes

The web app is an experience surface and does not replace repository control-plane
agent runtime decisions defined in ADR-0002.
