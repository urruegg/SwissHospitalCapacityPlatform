# Sprint 10 M1-C — Measures (Direct Lake) Evidence

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-08 |
| **Author** | Urs Rüegg |
| **Status** | PASS |
| **Previous Version** | n/a (initial) |

**Milestone:** M1 of the [Sprint 10 completion strategy](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md).
**Task:** M1-C — Author 2 measures in the `capacity-dashboard` semantic model (Direct Lake, TMDL programmatic path).
**Plan reference:** [M1 plan Task 3](../../../superpowers/plans/2026-07-08-sprint-10-m1-vertical-slice-plan.md#task-3--s103-slice-measures-pr-m1-c).

## Outcome

**PASS.** Two DAX measures added to the semantic model via TMDL + Fabric REST `updateDefinition`, framed via a Direct Lake refresh, and proven via `POST /datasets/{id}/executeQueries` returning live counts.

## Measures shipped

| Measure | Table | Formula | Result |
| ------- | ----- | ------- | ------ |
| `Active Encounters` | `encounter` | `DISTINCTCOUNT(encounter[eventId])` | **2467** |
| `Currently Assigned Beds` | `bed_assignment` | `DISTINCTCOUNT(bed_assignment[eventId])` | **539** |
| `Beds Total` (regression) | `dim_ward_capacityunit` | `SUM(dim_ward_capacityunit[bed_count])` | **909** — unchanged, proves no regression |

**M1 demo semantics:** Both measures count distinct events (each simulator emission = 1 event, each event has a unique `eventId`). This is intentionally simple for M1 — it proves the E2E pipeline (simulator → Eventstream → bronze → gold → Direct Lake → DAX) is live. M2 refines to true "active" (admissions minus discharges) and "currently assigned" (assignments minus releases) once the simulator emits paired lifecycle events.

## Path: TMDL programmatic (path B per M1 plan)

1. Discovered actual gold table registration state via SQL analytics endpoint → surfaced the **M1-B path bug** (see Corrections section)
2. Re-ran gold notebook with `gold_root=Tables/gold` runtime override → 5 gold tables now correctly at `Tables/gold/{entity}/`
3. Authored 2 new TMDL files following the `dim_disease.tmdl` pattern:
   - [`data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/encounter.tmdl`](../../../../data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/encounter.tmdl)
   - [`data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/bed_assignment.tmdl`](../../../../data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/bed_assignment.tmdl)
4. Updated `model.tmdl` to add `ref table encounter` and `ref table bed_assignment`
5. Pushed via Fabric REST `POST /workspaces/{ws}/items/{smId}/updateDefinition` — operation `762701e9-8e7d-47ab-9b2a-3244bfb55018` succeeded in ~4s
6. Direct Lake **framing refresh** required — first DAX query failed with `table 'encounter' is not refreshed`. Triggered enhanced refresh via `POST /datasets/{id}/refreshes` targeting the 2 new tables — refresh `188364b6-ae20-45be-8c34-7dafdedfa633` completed in 5s
7. Re-ran DAX query — returned real values

## Job / operation IDs

| Step | ID | Duration | Result |
| ---- | -- | -------- | ------ |
| Gold re-run (bronze-source + gold_root override) | `f0bf73e2-42b7-4bae-9cb7-8ee747c3b24c` | 55s | Completed |
| Semantic model `updateDefinition` | `762701e9-8e7d-47ab-9b2a-3244bfb55018` | 4s | Succeeded |
| Direct Lake framing refresh | `188364b6-ae20-45be-8c34-7dafdedfa633` | 5s | Completed |

## Metastore state (Fabric SQL analytics endpoint verification)

Registered `gold.*` tables (base tables, `INFORMATION_SCHEMA.TABLES` query):

- 9 dims / mapping (unchanged: `dim_disease`, `dim_drg`, `dim_hospital`, `dim_hospital_service`, `dim_specialty`, `dim_treatment`, `dim_ward_capacityunit`, `fact_capacity_baseline`, `map_disease_treatment_specialty_service`)
- 2 OR (unchanged: `or_case`, `or_schedule`)
- **5 new patient-flow facts** (M1-B re-run): `encounter`, `bed_assignment`, `forecast_output`, `discharge_score`, `discharge_recommendation`

## Row counts (M1-B corrected)

| Table | Rows | Hospitals |
| ----- | ---- | --------- |
| `encounter` | 2467 | H_LUKS + H_SZB + H_USZ |
| `bed_assignment` | 539 | H_LUKS + H_SZB + H_USZ |
| `forecast_output` | 765 | H_LUKS + H_SZB + H_USZ |
| `discharge_score` | 10 | H_LUKS + H_USZ |
| `discharge_recommendation` | 10 | H_LUKS + H_USZ |

## Sprint 10 M1 Task 3 exit criteria

- [x] `Active Encounters` measure authored + framed + returns real value
- [x] `Currently Assigned Beds` measure authored + framed + returns real value
- [x] Existing measures unaffected (`Beds Total` regression check passes)
- [x] Semantic model definition round-trips cleanly (TMDL → base64 parts → `updateDefinition` → operation Succeeded)
- [x] Direct Lake pipeline proven end-to-end (simulator → Custom Endpoint → Eventstream → bronze → gold → framing → DAX)
- [x] Evidence report v1.0.0 committed

## Reusable one-liners

**Push semantic model updateDefinition:**

```powershell
$fabTok = az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv
$ws = "f3af9733-9503-4e92-98f9-a901d96f1c87"
$smId = "08245059-a6e7-489f-a765-a3114583db4c"
$smRoot = "data-platform/reports/capacity-dashboard.SemanticModel"
$parts = @()
Get-ChildItem $smRoot -Recurse -File | Where-Object { $_.Extension -in '.pbism','.tmdl' } | ForEach-Object {
  $rel = $_.FullName.Substring((Resolve-Path $smRoot).Path.Length + 1).Replace('\','/')
  $parts += @{ path=$rel; payload=[Convert]::ToBase64String([IO.File]::ReadAllBytes($_.FullName)); payloadType='InlineBase64' }
}
$body = @{ definition = @{ parts = $parts } } | ConvertTo-Json -Depth 10 -Compress
Invoke-WebRequest -Uri "https://api.fabric.microsoft.com/v1/workspaces/$ws/items/$smId/updateDefinition" -Method Post -Headers @{ Authorization="Bearer $fabTok"; 'Content-Type'='application/json' } -Body $body -UseBasicParsing
```

**Query DAX (executeQueries):**

```powershell
$pbiTok = az account get-access-token --resource https://analysis.windows.net/powerbi/api --query accessToken -o tsv
$body = '{"queries":[{"query":"EVALUATE ROW(\"Active Encounters\", [Active Encounters])"}]}'
Invoke-RestMethod -Uri "https://api.powerbi.com/v1.0/myorg/groups/$ws/datasets/$smId/executeQueries" -Method Post -Headers @{ Authorization="Bearer $pbiTok"; 'Content-Type'='application/json' } -Body $body
```

## Rollback

- Rollback measures: revert the 2 TMDL files + `model.tmdl` change + re-push via `updateDefinition`
- Rollback gold table locations: re-run gold notebook without `gold_root` override — new writes go back to `Tables/gold/patient-flow/{entity}/` (also leaves current `Tables/gold/{entity}/` files as orphans until cleanup)

## Corrections — M1-B evidence

The [M1-B evidence report v1.0.0](m1-b-fact-tables.md) contains two factual errors surfaced during M1-C. Both are patched in the sibling `m1-b-fact-tables.md` bump to v1.1.0 in this same PR:

1. **Physical path** — reported as `Tables/Tables/gold/patient-flow/{entity}/hospitalId=H_*` (a DFS listing artifact from OneLake returning virtual mount content when given nonexistent paths). **Actual location was `Tables/gold/patient-flow/{entity}/hospitalId=H_*`.**
2. **Metastore registration** — reported as ready for Direct Lake reference via `sourceLineageTag: [gold].[encounter]`. **In reality the tables were NOT registered** because schema-enabled lakehouses only auto-surface tables at `Tables/{schema}/{table}` — the `patient-flow/` intermediate folder broke that convention.

**Remediation applied in this M1-C PR:** Gold notebook re-triggered with runtime override `gold_root=Tables/gold` (drops the `patient-flow/` intermediate). Tables now correctly at `Tables/gold/{entity}/` and auto-registered — proven by the M1-C DAX result.

**Orphan cleanup:** The prior `Tables/gold/patient-flow/{entity}/` Delta directories are now unreferenced files in the lakehouse's `Files` view — they don't appear in the metastore and cannot be queried, but they consume storage. Cleanup requires `approved-to-apply` per the deletion policy — tracked as **T7 H7** (new hygiene item) at Sprint 10 close.

## References

- [Sprint 10 M1 plan Task 3](../../../superpowers/plans/2026-07-08-sprint-10-m1-vertical-slice-plan.md#task-3--s103-slice-measures-pr-m1-c)
- [Sprint 10 completion strategy](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md)
- [ADR-0016](../../../adr/0016-no-phi-in-mvp-demo-scope.md) — synthetic-only scope
- [M1-A evidence](m1-a-notebook-import.md), [M1-B evidence](m1-b-fact-tables.md) (v1.1.0 corrected in this PR)
- Existing table pattern: [`data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/dim_disease.tmdl`](../../../../data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/dim_disease.tmdl)
