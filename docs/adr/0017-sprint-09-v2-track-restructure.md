# ADR-0017: Sprint 09 v2.0.0 Track Restructure

| Field | Value |
| ----- | ----- |
| Status | Accepted |
| Date | 2026-07-02 |
| Deciders | @urruegg |
| Consulted | n/a |

## Context

Sprint 09 v1.3.0 ([`docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md`](../sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md)) reflected a pre-Fabric-IQ-preview scope with different track boundaries (loosely: Track 1 Data Model Extensions, Track 2 Master Data Loading, Track 3 Simulation Extensions, Track 4 Fabric Data Platform + Power BI, Track 5 Minimum Viable Ontology). The 2026-07-02 design spec ([`docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md`](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md)) refines the sprint into 5 execution tracks aligned to the `westus2` demo scope ([ADR-0013](0013-temporary-us-region-demo-scope.md)) and the no-PHI constraint ([ADR-0016](0016-no-phi-in-mvp-demo-scope.md)):

- **T1 Foundation** — ADRs + ontology extension + data contracts + strict-mode CI + CODEOWNERS
- **T2 Ingestion** — Event Hubs → Fabric Eventstream → bronze/silver/gold notebooks
- **T3 Simulator** — calibration modules + 6 event generators + Event Hub emitter + ACA hosting
- **T4 Semantic Model + Agents** — TMDL semantic model + 3 runtime agents (BM-Copilot / Fabric Data Agent / CSA) + RBAC
- **T5 Dashboard** — 2-page PBIP + OR sample data + RLS PHI gate + deploy script

The new structure restructures track names and boundaries, which breaks anchor links from external documents that reference the v1.x scope headings (`#track-1-data-model-extensions`, `#track-2-master-data-loading-pipeline`, etc.).

## Decision

Bump [`docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md`](../sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md) from **1.3.0 → 2.0.0** (MAJOR per [`.github/copilot-instructions.md` §9 Document Versioning](../../.github/copilot-instructions.md#9-document-versioning)). Old track headings are removed; the migration path is: readers consult the design spec §7.2 deliverable table for the authoritative mapping from the v1.x scope to the v2 track structure.

## Consequences

**Positive:**

- Sprint doc aligns 1:1 with design spec and implementation plan.
- Traceability from deliverable → task → PR is unambiguous.
- Sprint close checklist is executable (DoD in one place).
- Cross-cutting DX.1–DX.4 deliverables land against a coherent structure.

**Negative:**

- External references to v1.x track names break. Mitigation: this ADR + design spec §7.2 mapping table.
- Retrospective template must accommodate the new track boundaries.

**Neutral:**

- No code impact — sprint doc is prose only.

## Migration

Consumers referencing `docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md#<old-anchor>`:

- **Old scope → new track mapping** is in [design spec §7.2 deliverables](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#72-deliverables-35-items). Roughly: v1.x Track 1 Data Model Extensions → v2 T1 Foundation (contracts + ontology); v1.x Track 2 Master Data Loading → v2 T2 Ingestion; v1.x Track 3 Simulation Extensions → v2 T3 Simulator; v1.x Track 4 Fabric + Power BI → v2 T4 Semantic Model + Agents + v2 T5 Dashboard; v1.x Track 5 MVO → v2 T1 Foundation ontology deliverables.
- **FR / NFR IDs unchanged** — [`docs/PRD.md`](../PRD.md) is preserved. Traceability rows in the v2 sprint doc reference the same requirement IDs.
- **Earlier ADRs unchanged** — this ADR only adds context; no supersession of prior ADRs.

## References

- [Design spec §7 Track structure, deliverables, DoD](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#7-track-structure-deliverables-dod)
- [Implementation plan](../superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md)
- [ADR-0013 temporary US region demo scope](0013-temporary-us-region-demo-scope.md)
- [ADR-0014 Fabric IQ Ontology target backbone GA-gated](0014-fabric-iq-ontology-target-backbone-ga-gated.md)
- [ADR-0015 skip SQL for MVP demo](0015-skip-sql-for-mvp-demo.md)
- [ADR-0016 no PHI in MVP demo scope](0016-no-phi-in-mvp-demo-scope.md)
- [.github/copilot-instructions.md §9 Document Versioning](../../.github/copilot-instructions.md#9-document-versioning)
