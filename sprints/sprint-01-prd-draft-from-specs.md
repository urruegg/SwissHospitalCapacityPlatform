# Sprint 1 — Draft PRD from docs/specs

**Sprint goal:** Analyze `docs/specs` with the spec-parser approach and produce
an initial PRD draft that identifies MVP scope for the Swiss AI-Powered Patient
Flow and Hospital Capacity Platform.

**Execution model:** GitHub Issues + `@copilot` trigger the Sprint 1 run.

- **Tracking issue:** [Sprint 1] Draft PRD from docs/specs (#3)
- **Source docs:**
  - [`docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform.md`](../docs/specs/Swiss%20AI-Powered%20Patient%20Flow%20and%20Hospital%20Capacity%20Platform.md)
  - [`docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform analysis.md`](../docs/specs/Swiss%20AI-Powered%20Patient%20Flow%20and%20Hospital%20Capacity%20Platform%20analysis.md)
- **Traceability target:** [`docs/PRD.md`](../docs/PRD.md)

## Scope of this sprint

| # | Deliverable | Status |
| --- | --- | --- |
| 1 | Source specification documents under `docs/specs/` | ✅ Done |
| 2 | Spec analysis (layers, requirement themes, MVP recommendation) | ✅ Done |
| 3 | Initial PRD draft (`docs/PRD.md`) with MVP scope | ✅ Done |
| 4 | Traceability: specs → PRD requirements → MVP scope | ✅ Done |

## Approach (spec-parser)

1. **Parse** the source scenario (S1) and analysis (S2) documents.
2. **Extract** functional (F1–F5) and non-functional (N1–N4) requirement themes.
3. **Map** each requirement to its source section for traceability (PRD §5).
4. **Identify MVP** as the smallest end-to-end slice (PRD §6), deferring
   forecasting, optimization and Copilot to fast-follow.

## Outcome

- The PRD draft (`docs/PRD.md`) is established as the traceability target, with
  each requirement linked back to source spec sections.
- **MVP scope** is defined as a single-provider pilot: capacity visibility (M1),
  FHIR ingestion (M2), a read-only dashboard (M3) and baseline governance (M4).

## Open items carried to next sprint

- Validate MVP scope with operations and compliance stakeholders.
- Confirm pilot provider and in-scope FHIR resources.
- Turn near-real-time freshness (N3) into measurable SLOs.

See PRD §8–§9 for the full list of risks and open questions.
