# capacity-dashboard.SemanticModel

Direct Lake semantic model for the Sprint 09 v2.0.0 dashboard (design spec §6).

## Status

**Skeleton only.** Full TMDL is authored via **Fabric portal / Power BI Desktop**
following Sprint 00 Approach A (portal-authored TMDL export via REST `getDefinition`).

The `definition/model.tmdl` file in this folder contains **pre-authored DAX measures**
from design spec §6.3 that must be wired into the portal-authored model.

## Authoring workflow

1. **Connect Power BI Desktop** to the Fabric workspace lakehouse:
   - Workspace: `ws-ihzhhpf-<env>` (westus2)
   - Lakehouse: `lh-ihzhhpf-<env>`
   - Mode: **Direct Lake** (not Import)
2. **Add gold tables** as fact and dim tables per design spec §6.4 star schema:
   - **Facts:** `fact_encounter`, `fact_bed_state`, `fact_bed_assignment`,
     `fact_forecast_output`, `fact_or_schedule`, `fact_or_case`
   - **Dims:** `dim_hospital`, `dim_specialty`, `dim_ward_capacityunit`,
     `dim_disease`, `dim_drg`, `dim_time`
3. **Copy the 13 DAX measures** from [`definition/model.tmdl`](definition/model.tmdl)
   into the portal model (edit in Power BI Desktop → Model view).
4. **Publish** to workspace as `capacity-dashboard`.
5. **Export TMDL** via Fabric REST `getDefinition` (Sprint 00 pattern):

   ```powershell
   .\data-platform\scripts\export_semantic_model_tmdl.ps1 `
     -WorkspaceId <ws-id> `
     -SemanticModelName capacity-dashboard `
     -OutputPath .\data-platform\reports\capacity-dashboard.SemanticModel\
   ```

6. **Commit the exported TMDL** — overwriting this skeleton.

## Grounding contract

Every measure grounds on MVO ontology entities per [design spec §6.3](../../../docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#63-dax-measures) and [crosswalk](../../../docs/ontology/crosswalk.md).

## Relationship contract (14 total — 12 Active + 2 Inactive)

Authored in the Fabric web modeling editor over the 11 gold tables listed in step 2. Full table and rationale in [`docs/sprints/sprint-09/checkpoint-2026-07-06-fabric-and-model.md` §7 step 4](../../../docs/sprints/sprint-09/checkpoint-2026-07-06-fabric-and-model.md). Summary:

- All 14: **Many-to-one (`*:1`), Cross-filter direction Single, Assume RI OFF**.
- **12 Active:** direct filter paths in the star schema.
- **2 Inactive** (Option B — resolves ambiguous filter paths that Power BI rejects at Save):
  - `dim_specialty[hospital_id] → dim_hospital[hospital_id]` — snowflake arm.
  - `or_case[orSlotId] → or_schedule[orSlotId]` — OR self-join arm.

**Measure-author rule:** whenever a measure needs one of the inactive paths, invoke `USERELATIONSHIP` inside a `CALCULATE`. Concrete examples for both inactive relationships are in the checkpoint doc §7 step 4 → "Option B decisions".

**Column-name note (source of truth):** the OR fact tables use **`orSlotId`** on **both** `or_schedule` and `or_case` (matching the source JSON in [`data/synthetic/or-samples/`](../../../data/synthetic/or-samples/)). Any spec that says `or_case[slotId]` is a misprint — always author against `orSlotId` on both sides.

## Measures — Sprint 09 v2 authoring status (Option A)

Design spec [§6.3](../../../docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#63-dax-measures) defines **13 measures**. Sprint 09 v2 authors the **5** that the current gold schema supports (Option A); the other **8** are deferred to Sprint 10 (Option D — see [checkpoint §9.1](../../../docs/sprints/sprint-09/checkpoint-2026-07-06-fabric-and-model.md#91-sprint-10-handoff--capacity-dashboard-measures-option-d)).

### Authored now (5)

| # | Measure | Home table | DAX (as saved in the model) | Notes |
| --- | ------- | ---------- | --------------------------- | ----- |
| 1 | `Beds Total` | `dim_ward_capacityunit` | `SUM(dim_ward_capacityunit[bed_count])` | Spec-exact |
| 2 | `Over-Run Minutes` | `or_case` | `SUM(or_case[overrunMinutes])` | Spec-exact |
| 3 | `OR Utilization %` | `or_case` | `DIVIDE(SUM(or_case[actualDurationMinutes]), SUM(or_schedule[plannedDurationMinutes])) * 100` | Spec-adjusted: `or_schedule[plannedDurationMinutes]` replaces spec's `[slotDurationMinutes]` (column doesn't exist under that name) |
| 4 | `Data Quality Score (Cases)` | `or_case` | `DIVIDE(CALCULATE(COUNTROWS(or_case), or_case[_data_quality] = "explicit"), COUNTROWS(or_case)) * 100` | Spec-adjusted: single per-table variant (spec's generic `COUNT([id])` needs a concrete table); returns 100 today because the OR loader sets `_data_quality = "explicit"` for every row |
| 5 | `Idle-Slot Minutes` | `or_schedule` | `CALCULATE(SUM(or_schedule[plannedDurationMinutes]), or_schedule[status] = "blocked")` | Spec-adjusted proxy: spec filters on `status = "available"` but the loader emits only `blocked` / `planned`. Sprint 10 loader work restores spec-exact semantics |

### Deferred to Sprint 10 (8)

Blocked by missing fact tables or missing `or_case`/`or_schedule` columns; see [checkpoint §9.1](../../../docs/sprints/sprint-09/checkpoint-2026-07-06-fabric-and-model.md#91-sprint-10-handoff--capacity-dashboard-measures-option-d) for the unblock plan.

| # | Measure | Blocker |
| --- | ------- | ------- |
| 6 | `Occupancy %` | needs `fact_bed_state` |
| 7 | `Beds Free` | needs `fact_bed_state` |
| 8 | `Required Capacity` | needs `fact_forecast_output` |
| 9 | `Forecast Peak (72h)` | needs `fact_forecast_output` |
| 10 | `ED Arrivals/hr` | needs `fact_encounter` |
| 11 | `First-Case On-Time %` | needs `or_case[isFirstCase]`, `or_case[actualStart]`, `or_case[plannedStart]` |
| 12 | `Short-Notice Cancellation %` | needs `or_case[cancellationLeadTimeHours]`, `or_case[status]` |
| 13 | `Avg Turnover Minutes` | needs `or_case[turnoverMinutes]` (derivable from `turnover-*` event pairs) |

## Row-Level Security (T5.6 — ADR-0016 gate 4)

`definition/model.tmdl` also carries four pre-authored RLS role scaffolds — `BedOps`,
`ORPlanner`, `Analyst`, `SemanticOwner` — per plan §T5.6 and design spec §6.5. Each
role declares `modelPermission: read` plus a table-filter placeholder
(`IF([_data_quality]="phi", FALSE, TRUE)`) that will be finalised on portal-authored
TMDL export once individual PHI columns carry the `[phi]="true"` annotation. See the
"Manual step" block at the bottom of `model.tmdl` for the conversion recipe.
