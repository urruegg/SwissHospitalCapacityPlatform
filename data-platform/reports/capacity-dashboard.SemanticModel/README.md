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
