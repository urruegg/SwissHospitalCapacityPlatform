# ADR-0018: Formalise `FR-VIZ-*` and `NFR-GOV-*` requirement IDs in PRD

| Field | Value |
| ----- | ----- |
| Status | Accepted |
| Date | 2026-07-06 |
| Deciders | @urruegg |
| Consulted | n/a |

## Context

Sprint 09 v2.0.0 design spec [`docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md`](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md) §7.7 T5 Dashboard traceability row references four requirement IDs that **do not exist in [`docs/PRD.md`](../PRD.md)**:

```text
| T5 Dashboard | `FR-CX-005`, `FR-VIZ-001..002`, `NFR-GOV-003`, `NFR-GOV-006`, ADR-0016 gate 4 |
```

- `FR-VIZ-001`, `FR-VIZ-002` — no `FR-VIZ-*` family exists in PRD.md.
- `NFR-GOV-003`, `NFR-GOV-006` — no `NFR-GOV-*` family exists in PRD.md (FR-GOV-* exists, but `NFR-GOV-003` is a different ID space).

This drift was surfaced during the Sprint 09 close PR #101 review. It affects three downstream artefacts:

1. **PR #101 body** used substitute IDs (`FR-DATA-005`, `FR-DATA-008`, `FR-GOV-001`, `FR-GOV-003`, `FR-GOV-004`) — accurate for the semantic-model work, but does not close the design-spec loop.
2. **Sprint 10 charter** [`docs/sprints/sprint-10-e2e-pipeline-and-dashboard-completion.md`](../sprints/sprint-10-e2e-pipeline-and-dashboard-completion.md) §8 flags this drift as a scope-clarification task.
3. **Sprint 09 retrospective** [`docs/sprints/sprint-09/retrospective.md`](../sprints/sprint-09/retrospective.md) does not enumerate the drift as a Sprint 10 backlog item.

## Decision

**Formalise the four IDs in PRD.md.** Add two new PRD sub-sections at the end of their respective (FR / NFR) top-level sections so no existing anchors break:

- **New FR section "I) Visualization And Dashboards (Sprint 09 T5)"** containing:
  - `FR-VIZ-001` — The platform shall provide an operational **bed-capacity dashboard page** exposing current occupancy, forecast pressure windows, and data-quality signals, aligned with `FR-CX-005`.
  - `FR-VIZ-002` — The platform shall provide an operational **OR-steering dashboard page** exposing case-level utilisation, first-case on-time performance, cancellation, and idle-slot metrics, aligned with `FR-CX-005`.
- **New NFR section "I) Governance and Audit (Sprint 09 T5)"** containing:
  - `NFR-GOV-001` — The platform shall record change-management traceability for semantic-model, dashboard, and agent artefacts (aligns with `FR-GOV-001`).
  - `NFR-GOV-002` — The platform shall support audit-review workflows for governance evidence artefacts (aligns with `FR-GOV-004`).
  - `NFR-GOV-003` — The dashboard consumption path shall enforce role-scoped filtering that prevents PHI-tagged column exposure to any non-owner role (extends [ADR-0016](0016-no-phi-in-mvp-demo-scope.md) gate 4).
  - `NFR-GOV-004` — Semantic-model and dashboard artefacts shall be round-trippable to source-controlled TMDL/PBIP such that any deployed state can be replayed from repository content alone.
  - `NFR-GOV-005` — Governance evidence artefacts shall be co-located with the sprint or ADR that produced them under `docs/sprints/*/evidence/` or `docs/adr/*.md`.
  - `NFR-GOV-006` — Every dashboard visual shall carry per-visual traceability back to its underlying semantic-model measure and its ontology-grounded source (`hcp:*` entities), aligned with `FR-CX-006` and `FR-ONT-004`.

**Bump PRD.md version 1.4.0 → 1.5.0** (MINOR per [`.github/copilot-instructions.md` §9 Document Versioning](../../.github/copilot-instructions.md#9-document-versioning) — additive; no anchors broken).

**Retain the design-spec §7.7 references as-is** — after this ADR merges, they resolve against real PRD entries. Add a footer note to design-spec §7.7 pointing to this ADR for provenance.

## Alternatives considered

- **A1: Fix the design-spec to use existing IDs.** Rejected — the design-spec is authored and merged; forcing rewrites of its traceability rows would incur a MAJOR doc-version bump for a rename that only masks the underlying gap. Additive IDs on PRD are simpler.
- **A2: Add only the two IDs referenced (`NFR-GOV-003`, `NFR-GOV-006`) and skip the numbering gap.** Rejected — introducing `NFR-GOV-003` without `-001` and `-002` violates the "sequential IDs within a family" convention observed across all other PRD sub-sections. Filled the range 001–006 so future references are unambiguous.
- **A3: Reject the drift and leave PRD.md unchanged.** Rejected — this leaves the Sprint 09 v2 design spec citing non-existent IDs indefinitely, degrading the traceability contract in copilot-instructions §6.

## Consequences

**Positive:**

- Sprint 09 v2 design-spec §7.7 references now resolve.
- Sprint 10 T3 dashboard closure (S10.6 RLS re-authoring + S10.8 visuals) has authoritative NFR anchors (`NFR-GOV-003`, `NFR-GOV-006`) to cite in future PR traceability rows.
- Fills a legitimate PRD gap: prior to this ADR, PRD.md had no explicit dashboard or governance-of-artefacts NFR family, despite dashboards being a first-class user-facing surface since Sprint 06.

**Negative:**

- 6 new IDs increase PRD size and require Sprint 10 T5.11 (verifier extension) and future PRs to update the traceability matrix if any of these are advanced.
- ID semantics are the ADR author's best inference from design-spec context — if the design-spec author intended different semantics, this ADR should be superseded by ADR-0019 with a MINOR PRD bump.

**Neutral:**

- No code impact. Additive PRD change only.

## Migration

- Existing PRs authored before this ADR (PR #101, PR #102) that used substitute IDs are **not** retroactively edited — their traceability rows remain historically accurate; the ADR closes the loop going forward.
- Sprint 10 PRs SHOULD prefer the newly-added IDs when advancing dashboard or governance-of-artefacts scope.
- The design-spec §7.7 footer will link to this ADR so downstream readers understand the provenance of the four IDs.

## References

- [Sprint 09 v2 design spec §7.7](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#77-traceability)
- [`docs/PRD.md`](../PRD.md) — target for the additive changes
- [Sprint 10 charter §8](../sprints/sprint-10-e2e-pipeline-and-dashboard-completion.md#8-traceability) — flagged the drift
- [PR #101](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/101) — Sprint 09 close PR that surfaced the drift
- [`.github/copilot-instructions.md` §9 Document Versioning](../../.github/copilot-instructions.md#9-document-versioning) — governs the PRD MINOR bump
- [ADR-0016 gate 4](0016-no-phi-in-mvp-demo-scope.md) — referenced by `NFR-GOV-003`
- [ADR-0017 Sprint 09 v2 track restructure](0017-sprint-09-v2-track-restructure.md) — precedent for additive Sprint-scoped ADRs
