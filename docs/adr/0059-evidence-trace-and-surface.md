# ADR-0059: Evidence-trace contract and per-role evidence surface

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-01 |
| **Author** | Urs Rueegg |
| **Decision-makers** | @urruegg |
| **Related** | [Sprint 39 design](../superpowers/specs/2026-08-01-epic-closed-loop-sit-evidence-e2e-design.md), [ADR-0058](0058-sim-outcome-and-effect-schema.md), [ADR-0007](0007-mvp-agent-runtime-and-hitl-release-gates.md), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md), `NFR-AI-001` |

## Context

Sprint 39 proves the closed loop end-to-end per role on real EPIC-simulator data,
shown as a demo E2E flow and per-role interaction. The proof needs a stable,
PHI-free contract and a provenance discipline.

## Decision

1. **`DC-EVIDENCE-TRACE-v1` (ratified).** One PHI-free record per synthetic
   patient journey; an ordered array of per-role steps (EPIC input, read,
   recommendation, copilot accept/deny, action, outcome), `golden_thread`-linked;
   accept + deny branches. Validated by `data/synthetic/schema/dc-evidence-trace-v1.schema.json`.
2. **Real-gold, seeded, human-gated.** Read/recommendation run on real SIT gold
   (a captured snapshot backs CI); apply/outcome run on an in-host `SimState`
   seeded from that gold. Only a human accept fires an apply (`NFR-AI-001`); deny
   changes nothing. No live write-back to the running sim this sprint.
3. **Provenance honesty.** Every part is badged `simulated` or `live`; a
   `simulated` part is never rendered as `live`. The evidence trace is a derived
   view of the same operational-loop records (validation == user experience).

## Consequences

The per-role evidence surface (Plan 2) renders these records; the operational loop
(Plan 2) produces them. No PHI, no autonomous action, no deploy this sprint.
