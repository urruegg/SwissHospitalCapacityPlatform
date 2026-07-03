# Page 2 — OR Steering Command Center

Inspired by the HCC operation-room-overview PNG. Uses DC-OR sample data (T5.4 fixtures + T5.5 loader).

**Sample data — live OR ingestion is Sprint 10.**

## Layout (per [design spec §6.2](../../../../../../docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#62-page-2--or-steering-command-center-inspiration-from-hcc-operation-room-overviewpng))

| Zone | Visual | Fields |
|---|---|---|
| Header | 6-KPI panel wall — mirrors HCC control-room aesthetic | (1) First-case on-time %, (2) Short-notice cancellation %, (3) Avg turnover minutes, (4) Idle-slot minutes, (5) Over-run minutes, (6) OR Utilization % |
| Main | OR case timeline (Gantt-style) — one row per theatre × time-of-day | X: time-of-day, rows: `dim_or_theatre`, colours: case status |
| Lower-left | Cancellation reasons breakdown (donut) | `dc-or-case-v1.cancellationReason` enum |
| Lower-right | Block reasons breakdown (bar) | `dc-or-schedule-v1.blockReason` enum |
| Right rail | Anaesthesia consultation funnel | Derived from `dc-or-case-v1.eventType` sequence |
| Footer | Ontology tooltip + sample-data watermark | "Grounded on `hcp:ORSlot` + `hcp:BedAssignment`. **Sample data — live OR ingestion is Sprint 10.**" |

**Synced slicers**: Hospital / Specialty / Time slicers from Page 1 must be synced to Page 2 via Power BI "Sync slicers" feature.

## Portal authoring workflow

Same as Page 1 README — author in Power BI Desktop, export TMDL/PBIR via REST, commit.

## DAX measures

All 6 OR KPI measures already authored in [`../../../../capacity-dashboard.SemanticModel/definition/model.tmdl`](../../../../capacity-dashboard.SemanticModel/definition/model.tmdl) per design spec §6.3.
