# Page 1 — Capacity Utilization Pattern

Replica of the HCC utilization pattern PNG (`docs/architecture/hcc-apacities-utilization-pattern-overview.png` reference).

## Layout (per [design spec §6.1](../../../../../../docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#61-page-1--capacity-utilization-pattern-replica-of-hcc-apacities-utilization-pattern-overviewpng))

| Zone | Visual | Fields | DAX / measures |
|---|---|---|---|
| Header | 4 KPI cards | Current Occupancy %, Beds Free, ED Arrivals/hr, Forecast Peak (72h) | `[Occupancy %]`, `[Beds Free]`, `[ED Arrivals/hr]`, `[Forecast Peak (72h)]` |
| Slicers row | 3 slicer visuals | Hospital, Specialty, Time window | `dim_hospital.short_name` (USZ / LUKS / SZB / All), `dim_specialty.name`, `dim_time.date` range |
| Main chart | Time-series line — capacity used vs required (12-month rolling, daily granularity) | X: `dim_time.date`, Y1: `gold.bed_state → Occupancy %`, Y2: `gold.forecast_output → Required Capacity` | `[Occupancy %]` + `[Required Capacity]` |
| Below-main | Month × Weekday RAG heatmap (R > 90%, A 75–90%, G < 75%) | Matrix visual, rows=Month, cols=Weekday, values=avg Occupancy % | Conditional formatting on `[Occupancy %]` |
| Right rail | Data-quality badge | Explicit% / Inferred% / Missing% per hospital | `[Data Quality Score]` |
| Footer | Ontology tooltip | Static text: "Grounded on: `hcp:Bed`, `hcp:hasState`, `hcp:ForecastOutput`" | n/a |

**USZ inferred bed-count**: right-rail data-quality badge must show `⚠ Inferred` for USZ (per design spec §4.5 documented delta).

## Portal authoring workflow

1. Open [`../../../capacity-dashboard.pbip`](../../../../capacity-dashboard.pbip) in Power BI Desktop.
2. Confirm connection to the sibling `../../../../capacity-dashboard.SemanticModel/` (auto-loaded via `.pbir`).
3. Author Page 1 per the table above.
4. Save + export via Fabric REST `getDefinition` per [Sprint 00 pattern](../../../../../../docs/sprints/sprint-00-tenant-migration.md).
5. Commit the exported `visualContainers[]` — replacing this empty skeleton.

## Grounding contract

All visuals cite `hcp:*` ontology entities via crosswalk annotations on the semantic model measures (see [`../../../../capacity-dashboard.SemanticModel/definition/model.tmdl`](../../../../capacity-dashboard.SemanticModel/definition/model.tmdl)).
