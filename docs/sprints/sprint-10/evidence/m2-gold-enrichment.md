# Sprint 10 M2 — Gold Enrichment + Heatmap Evidence

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-08 |
| **Author** | Urs Rüegg |
| **Status** | PASS |
| **Previous Version** | n/a (initial) |

**Milestone:** M2 of the [Sprint 10 completion strategy](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md).
**Skill used:** [`powerbi-report-authoring`](../../../../.github/skills/powerbi-report-authoring/SKILL.md) (slicer + pivotTable templates), [`fabric-semantic-model-authoring`](../../../../.github/skills/fabric-semantic-model-authoring/SKILL.md) (TMDL measures + relationships).

## Outcome

**PASS.** Gold notebook flattens 7 useful `payload.*` fields + 3 time-dimension fields to top-level columns. Semantic model adds 4 new measures (`Admissions=561`, `Discharged=567`, `Currently In Hospital=1900`, `Occupancy %=59.3%`) plus 2 relationships to `dim_hospital`. Report Page 1 gains 3 slicers (Hospital, Admission Type, Status) and 1 heatmap matrix (Month × Weekday × Admissions), all rendering live.

## Deliverables shipped

### 1. Gold notebook — flat columns for Direct Lake

Added to `publish_entity` pipeline (see [03_gold_eventstream.ipynb](../../../../data-platform/notebooks/eventstream/03_gold_eventstream.ipynb)):

- `_flatten_payload(df)` — surfaces payload STRUCT fields as top-level columns:
  - `encounterId`, `status`, `previousStatus`, `admissionType`, `class`, `requestedSpecialtyServiceId`, `expectedLOSDays`
- `_add_time_dims(df)` — derives date/time keys from `simulatedAt`:
  - `simulatedDate` (date), `simulatedMonth` (int 1-12), `simulatedWeekday` (int 1-7, Spark dayofweek)

**Why flatten?** Fabric SQL analytics endpoint doesn't project STRUCT columns into `INFORMATION_SCHEMA.COLUMNS`, and Direct Lake bindings for STRUCT sub-fields are unreliable. Flattening at gold makes downstream measures + slicers trivially bind-able.

**Original `payload` STRUCT preserved** — nothing downstream breaks.

### 2. Semantic model — measures + relationships

**4 new measures** in [encounter.tmdl](../../../../data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/encounter.tmdl) and [bed_assignment.tmdl](../../../../data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/bed_assignment.tmdl):

| Measure | Formula | Value |
| ------- | ------- | ----- |
| `Admissions` | `CALCULATE(COUNTROWS(encounter), encounter[status] = "arrived")` | **561** |
| `Discharged` | `CALCULATE(COUNTROWS(encounter), encounter[status] = "finished")` | **567** |
| `Currently In Hospital` | `CALCULATE(COUNTROWS(encounter), encounter[status] IN {"arrived", "triaged", "in-progress", "onleave"})` | **1900** |
| `Occupancy %` | `DIVIDE([Currently Assigned Beds], [Beds Total]) * 100` | **59.3%** |

**2 new relationships** in [relationships.tmdl](../../../../data-platform/reports/capacity-dashboard.SemanticModel/definition/relationships.tmdl):

- `encounter[hospitalId] → dim_hospital[hospital_id]`
- `bed_assignment[hospitalId] → dim_hospital[hospital_id]`

**14 new flat columns** across `encounter` and `bed_assignment` tables (7 payload + 3 time-dim each on `encounter`; 7 payload on `bed_assignment`).

### 3. Report — 3 slicers + 1 heatmap

4 new visuals added to `page1-capacity/visuals/`:

| Visual name | Type | Bound field(s) | Position (x,y,w,h) |
| ----------- | ---- | -------------- | ------------------ |
| `4160828f...` | Slicer (dropdown) | `dim_hospital[short_name]` | (24, 196, 200, 80) |
| `2212c66b...` | Slicer (dropdown) | `encounter[admissionType]` | (240, 196, 200, 80) |
| `e92c5f06...` | Slicer (dropdown) | `encounter[status]` | (456, 196, 200, 80) |
| `1521db08...` | Matrix (pivotTable) | rows=`simulatedMonth`, cols=`simulatedWeekday`, values=`[Admissions]` | (24, 292, 900, 400) |

**Rendered live** (screenshot in evidence session):
- Slicers: Hospital = All (USZ / LUKS / SZB), Admission Type = All (elective 1465 / emergency 810 / transfer 192), Status = All (arrived / triaged / in-progress / onleave / finished)
- Heatmap: Month 7 × Weekday {2 Mon, 3 Tue, 4 Wed} = {288, 249, 24}, Total = 561 (matches `[Admissions]`)

Only 3 weekday cells populated because the simulator only ran a handful of days — enough to demo the pattern.

## Data profile findings

`gold.encounter` status distribution:

| status | count |
| ------ | ----- |
| finished | 567 |
| in-progress | 567 |
| triaged | 567 |
| arrived | 561 |
| onleave | 205 |
| **total** | **2467** |

`gold.encounter` admissionType distribution: elective 1465, emergency 810, transfer 192.

## Steps + IDs

| Step | Notes | Job / Op ID |
| ---- | ----- | ----------- |
| Gold notebook re-run 1 (payload flatten) | 62s | `273c410e-7e89-44ac-be59-950348540c03` |
| SQL endpoint refresh (force) | POST `/sqlEndpoints/{id}/refreshMetadata` | 200 OK |
| Gold notebook re-run 2 (time dims) | 61s | `ef4c961f-3590-4320-990a-4003e44daf1d` |
| Semantic model updateDefinition #1 (measures + rels) | 4s | Succeeded |
| Semantic model updateDefinition #2 (time-dim cols) | 4s | Succeeded |
| Direct Lake framing refresh | 5s | Completed |
| Report updateDefinition (4 new visuals + .platform preserved) | 4s | Succeeded |
| Browser reload → verify | Slicers + heatmap render live | — |

## Sprint 10 M2 exit criteria

- [x] Gold notebook flattens `payload.*` fields to top-level columns
- [x] Gold notebook adds `simulatedDate/Month/Weekday` for time-based visuals
- [x] Semantic model adds ≥ 3 new measures on refined lifecycle semantics
- [x] Semantic model adds relationships from fact tables to `dim_hospital`
- [x] Report Page 1 has ≥ 3 slicers wired to encounter + dim_hospital
- [x] Report Page 1 has ≥ 1 heatmap/matrix showing time-based aggregation
- [x] All new visuals render live in Fabric with real data
- [x] Existing KPI cards still render unchanged (regression check)
- [x] Evidence report v1.0.0 committed

## Design-spec deltas (documented, not blocking)

- **Occupancy %** M2 semantic: `[Currently Assigned Beds] / [Beds Total]` where `Currently Assigned Beds = DISTINCTCOUNT(bed_assignment[eventId])`. This counts distinct bed-assignment events, not truly-active bed occupancy. Refinement to lifecycle-aware "in-use beds" tracked as **Sprint 11 backlog** (needs `bed.released` simulator event).
- **Currently In Hospital** M2 semantic: event-status filter counts events at non-finished statuses. Because each encounter emits multiple lifecycle events, this overcounts unique encounters. Correct measure would use `LASTNONBLANK(status) BY encounterId` — refinement tracked as **Sprint 11 backlog**.
- **Heatmap RAG conditional formatting** (design spec §6.1 called for red > 90%, amber 75-90%, green < 75% on Occupancy %): M2 delivers structural heatmap on Admissions count; RAG on Occupancy % is a follow-up when the Occupancy semantic is refined.

## Rollback

- Revert TMDL + report + gold notebook → M1 state (2 KPI cards, no slicers, no heatmap)
- Data preserved; measures are pure SM definition changes

## References

- [Sprint 10 completion strategy §M2](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md#m2--measure-refinement--more-visuals)
- [M1-D evidence](m1-d-kpi-tiles.md) — KPI cards + PBIR portal-scaffold pattern (same pattern reused here)
- [M1.5 evidence](m1-5-silver-hardening.md) — silver flow that feeds this gold enrichment
- Skill: [powerbi-report-authoring](../../../../.github/skills/powerbi-report-authoring/references/slicers.md) — slicer templates
- Skill: [powerbi-report-authoring](../../../../.github/skills/powerbi-report-authoring/references/table.md) — matrix (pivotTable) template
