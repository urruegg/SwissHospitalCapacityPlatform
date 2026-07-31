# ADR-0058: Sim-outcome contract, lever effect schema, and sim-as-ground-truth

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-31 |
| **Author** | Urs Rueegg |
| **Decision-makers** | @urruegg |
| **Related** | [Sprint 38 design](../superpowers/specs/2026-07-31-sprint-38-epic-closed-loop-simulation-engine-design.md), [ADR-0040](0040-prescriptive-decision-ontology-and-runtime-store.md), [ADR-0055](0055-closed-loop-learning-capture-and-eval.md), [ADR-0007](0007-mvp-agent-runtime-and-hitl-release-gates.md), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md), `NFR-AI-001` |

## Context

Sprint 38 closes the operational loop: the EPIC simulator applies HITL-approved
agent actions back to patient-flow state. Three cross-cutting decisions underpin
every milestone and any future lever that joins the loop, so they are fixed here.

## Decision

1. **`DC-SIM-OUTCOME-v1` (ratified).** One PHI-free record per applied action,
   capturing pre/post state delta and predicted-vs-realised `divergence`, linked
   by `plan_id` / `golden_thread` / `cosmos_id`. Validated by
   `data/synthetic/schema/dc-sim-outcome-v1.schema.json`. Retained R3 alongside
   `DC-AGENT-INTERACTION-v1` (ADR-0055).
2. **Declarative lever `effect` schema.** Each lever may declare an `effect`
   block (state mutation) alongside its `impact_formula_ref` (metric prediction).
   The `apps/sim-capacity` effect interpreter executes it; adding a lever is a
   YAML change, not new Python.
3. **Sim-as-ground-truth, human-gated.** The simulator is the ground truth agents
   are graded against, but it applies **only** actions a human moved to
   `approved-to-apply` (ADR-0007, `NFR-AI-001`). Every outcome is stamped
   `provenance: simulated`; this is not clinical actuation.

## Consequences

Predicted-vs-realised divergence becomes the operational signal the Sprint 30
learning loop (ADR-0055) consumes in Sprint 38 M5. No PHI, no autonomous action.
