# Sprint 10 M1-D — KPI Tiles (PBIR JSON path) Evidence

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.1 |
| **Date** | 2026-07-08 |
| **Author** | Urs Rüegg |
| **Status** | PASS |
| **Previous Version** | 1.0.0 (initial) |

**Milestone:** M1 (final task) of the [Sprint 10 completion strategy](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md).
**Task:** M1-D — 2 KPI card visuals on Page 1 + M1 close.
**Plan reference:** [M1 plan Task 4](../../../superpowers/plans/2026-07-08-sprint-10-m1-vertical-slice-plan.md#task-4--s103-slice-2-kpi-tiles-page-1-pr-m1-d).

## Outcome

**PASS.** 2 KPI card visuals (`Active Encounters=2467`, `Currently Assigned Beds=539`) render live in the Fabric-hosted `capacity-dashboard` report backed by Direct Lake against the `gold.encounter` and `gold.bed_assignment` tables. M1 vertical slice complete end-to-end: simulator → Custom Endpoint → Eventstream → bronze → gold → semantic model → Direct Lake → 2 measures → 2 rendered KPI tiles.

## Key finding — Fabric API-created reports need portal-created ACL scaffold

**Problem:** Reports created via `POST /workspaces/{ws}/items` (generic item creation) OR `POST /workspaces/{ws}/reports` (report-specific) both entered a broken ACL state where the browser render failed with HTTP 405 "Failed to get access request info for this artifact". Two consecutive fresh deploys reproduced the same 405. Semantic model takeover + framing refresh + updateDefinition rebind did not resolve it.

**Root cause hypothesis:** Fabric's `wabi-us-central-b` cluster (which serves this MCAPS demo tenant's ACL cache) does not properly bootstrap the artifact permission record for API-first-created reports. This is a documented recurring issue on Fabric Ideas forums with API-created reports in MCAPS/preview tenants.

**Solution — portal-created ACL scaffold + programmatic overlay:**

1. Delete broken API-created reports (2 iterations, both approved-to-apply)
2. Use Fabric portal `+ New → Report → Pick a published semantic model → capacity-dashboard → Save as "capacity-dashboard"` — creates a **properly-ACL'd** report scaffold (blank canvas, correct baseline schemas, `.platform` metadata, StaticResources theme reference)
3. `getDefinition` on the portal-created report to extract Fabric's preferred PBIR shape (schema versions + file layout)
4. Overlay our 2 KPI card `visual.json` files + updated schemas locally
5. `updateDefinition` on the portal-created report ID (**preserves the good ACL** while replacing definition content)
6. Framing refresh already up-to-date from M1-C
7. Reload — cards render with live data ✅

## Deliverables shipped

### 2 KPI card visuals (PBIR JSON, path B per M1 plan)

| Visual | Measure | Bound table | Position | Value rendered |
| ------ | ------- | ----------- | -------- | -------------- |
| `310e56c5c8960c5f4678` | `[Active Encounters]` | `encounter` | (24, 56, 296×120) | **2K** (2467) |
| `3b77d93a6d6d2a920319` | `[Currently Assigned Beds]` | `bed_assignment` | (340, 56, 296×120) | **539** |

Both cards use `visualType: cardVisual` (schema `visualContainer/2.9.0`) with:
- `outline.show=false` (no internal border)
- `accentBar.show=true` (blue `#0072B2` on Active Encounters, green `#009E73` on Currently Assigned Beds)
- `value.fontSize=36D` (per skill's height-vs-fontSize table for 120px cards)
- `label.text` override for user-friendly labels

Files:
- [`data-platform/reports/capacity-dashboard.Report/definition/pages/page1-capacity/visuals/310e56c5c8960c5f4678/visual.json`](../../../../data-platform/reports/capacity-dashboard.Report/definition/pages/page1-capacity/visuals/310e56c5c8960c5f4678/visual.json)
- [`data-platform/reports/capacity-dashboard.Report/definition/pages/page1-capacity/visuals/3b77d93a6d6d2a920319/visual.json`](../../../../data-platform/reports/capacity-dashboard.Report/definition/pages/page1-capacity/visuals/3b77d93a6d6d2a920319/visual.json)

### PBIR structure upgraded to Fabric-native shape

Fabric-produced PBIR reference extracted via `getDefinition` on the portal-created scaffold set the following contracts. Our local PBIR was updated to match:

| File | Prior schema | Corrected schema | Reason |
| ---- | ------------ | ---------------- | ------ |
| `definition.pbir` | `definitionProperties/1.0.0`, `version: 1.0`, `byPath` reference | `definitionProperties/2.0.0`, `version: 4.0`, `byConnection: semanticmodelid=<GUID>` | Fabric REST rejects `byPath` (portal-only), requires `byConnection` with expanded connectionString |
| `definition/version.json` | (missing) → 4.0.0 | **2.0.0** | Fabric metadata version, distinct from `definition.pbir` `version` field |
| `definition/report.json` | `definitionProperties/1.0.0` with `publicCustomVisuals: []` | `report/3.3.0` with `themeCollection.baseTheme.reportVersionAtImport` + `type` + `resourcePackages` + `settings` | Wrong schema URI (was for `.pbir`) + missing required fields |
| `definition/pages/pages.json` | `pages/1.0.0` | `pagesMetadata/1.1.0` | Correct schema URI |
| `definition/pages/*/page.json` | `page/1.0.0` with invalid `visualContainers: []` | `page/2.1.0` (no inline visuals array) | Modern PBIR uses `visuals/<name>/visual.json` subfolders, not inline arrays |
| `.platform` | (missing) | Added from portal scaffold | Required for Fabric-item Git-integration metadata |
| `StaticResources/SharedResources/BaseThemes/CY26SU05.json` | (missing) | Copied from portal scaffold | Referenced by `report.json.resourcePackages`; missing = broken theme |

### Sprint 09 v2.1.0 → v2.2.0 (DoD item 4 flipped)

Sprint 09 §4 DoD item 4 was carry-over ("full pipeline end-to-end"). Flipped to `[x]` with pointer to this evidence pack. See [sprint-09 doc v2.2.0](../../sprint-09-master-data-simulation-and-capacity-dashboard.md).

## Deploy sequence (chronological)

| Step | Action | Report ID | Result |
| ---- | ------ | --------- | ------ |
| 1 | Deploy via `/items` (generic) | `51c2afd1-...` | Created but 405 on render |
| 2 | Delete (approved-to-apply) | `51c2afd1-...` | Removed |
| 3 | Deploy via `/reports` (Report-specific) | `2d301831-...` | Created but 405 on render |
| 4 | Semantic model takeover + Direct Lake framing refresh | (n/a) | Succeeded but did not fix 405 |
| 5 | updateDefinition rebind | `2d301831-...` | Succeeded but did not fix 405 |
| 6 | Delete (approved-to-apply) | `2d301831-...` | Removed |
| 7 | Portal `+ New → Report → SM picker → Save as capacity-dashboard` | **`9b9c2c4f-...`** | Created + ACL correct + blank canvas renders |
| 8 | `getDefinition` on portal scaffold | `9b9c2c4f-...` | 7 parts extracted (revealed correct schema versions + `.platform` + StaticResources) |
| 9 | Local PBIR migrated to Fabric-native shape + 2 KPI visuals added | (local files) | Ready to push |
| 10 | `updateDefinition` overlay onto portal scaffold | `9b9c2c4f-...` | Succeeded in 4s |
| 11 | Browser reload | (n/a) | **Both KPI cards render with live values** ✅ |

## Sprint 10 M1 Task 4 exit criteria

- [x] `Active Encounters` KPI card visible on Page 1 with real value (2467, format-shortened to "2K" by Fabric)
- [x] `Currently Assigned Beds` KPI card visible on Page 1 with real value (539)
- [x] Cards bound via Direct Lake to `gold.encounter` and `gold.bed_assignment` metastore-registered tables
- [x] PBIR files pass Fabric ingestion (updateDefinition Succeeded)
- [x] Report renders without 405 (portal-scaffold + updateDefinition workaround applied)
- [x] Sprint 09 v2 DoD item 4 flipped from CARRY-OVER to [x] with evidence pointer
- [x] Evidence report v1.0.0 committed

## M1 vertical slice — end-to-end proof

**Full path proven in one live pipeline as of 2026-07-08 15:00 CET:**

```text
sim-capacity (Container App, MI-authenticated)
   ↓ AMQP writes to
Fabric Custom Endpoint (id 6e2e833f-...) — SAS-less Entra ID auth per ADR-0019
   ↓ Eventstream es-capacity-events-sit (id 7b65dfa1-...)
Lakehouse destination lakehouse-bronze → dbo.bronze_eventstream_raw Delta table
   ↓ Bronze notebook (job 4506b6d6-..., 95s) fans out per eventKind to:
Tables/bronze/eventstream/{bed.assigned, encounter.admitted, encounter.transitioned,
                            discharge.recommended, discharge.scored, forecast.published}/
   ↓ Gold notebook (job f0bf73e2-..., 55s) reads bronze directly (silver bypass — M1.5)
   ↓ Publishes to Tables/gold/{encounter, bed_assignment, forecast_output,
                                discharge_score, discharge_recommendation}/
   ↓ Fabric SQL analytics endpoint auto-registers all 5 as gold.* base tables
   ↓ Semantic model capacity-dashboard (id 08245059-...) references via
     sourceLineageTag: [gold].[encounter] + [gold].[bed_assignment]
   ↓ Direct Lake framing refresh (188364b6-...) makes tables queryable
   ↓ 2 DAX measures: Active Encounters + Currently Assigned Beds
   ↓ Report capacity-dashboard (id 9b9c2c4f-...) Page 1 KPI cards render live
```

**Rendered values:** `Active Encounters = 2467` (displayed 2K), `Currently Assigned Beds = 539`, `Beds Total = 909` (regression measure, unchanged).

## Rollback

- Rollback report definition: revert PBIR files + re-push `updateDefinition` on report `9b9c2c4f-...`
- Rollback report entirely: delete report `9b9c2c4f-...` (destructive, needs `approved-to-apply`)
- Rollback M1 slice atomically: revert this branch's merge commit

## Follow-ups (M1.5 + T7)

- **M1.5 silver hardening** (in-sprint per completion strategy) — restore silver flow, remove `silver_root` runtime override on gold notebook. Uses `spark-operations` skill for cell-by-cell debug.
- **T7 H7** (new hygiene item, tracked at Sprint 10 close) — orphan `Tables/gold/patient-flow/*` cleanup, requires `approved-to-apply`.
- **T7 H6** — F16 → F2 downscale at Sprint 10 close.
- **M1 measure refinement (M2)** — replace `DISTINCTCOUNT(eventId)` with lifecycle-aware measures (admissions minus discharges, assignments minus releases) once simulator emits paired events.

## References

- [Sprint 10 M1 plan Task 4](../../../superpowers/plans/2026-07-08-sprint-10-m1-vertical-slice-plan.md#task-4--s103-slice-2-kpi-tiles-page-1-pr-m1-d)
- [Sprint 10 completion strategy §M1](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md#m1--vertical-slice-e2e)
- [Sprint 09 v2.2.0 DoD item 4](../../sprint-09-master-data-simulation-and-capacity-dashboard.md) — flipped in this PR
- [M1-A evidence](m1-a-notebook-import.md) — notebook import
- [M1-B evidence v1.1.0](m1-b-fact-tables.md) — gold table landing + path correction
- [M1-C evidence](m1-c-measures.md) — 2 measures via TMDL
- [ADR-0019](../../../adr/0019-fabric-custom-endpoint-eventstream-ingestion.md) — Custom Endpoint + Entra ID pivot
- [ADR-0016](../../../adr/0016-no-phi-in-mvp-demo-scope.md) — synthetic-only scope
- Card visual reference: [`.github/skills/powerbi-report-authoring/references/card.md`](../../../../.github/skills/powerbi-report-authoring/references/card.md)
- Microsoft Learn: [PBIR format](https://learn.microsoft.com/power-bi/developer/projects/projects-report#pbir-format)
