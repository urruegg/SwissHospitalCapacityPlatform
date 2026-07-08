# Sprint 10 M1 — Vertical Slice E2E Plan

> **For agentic workers:** REQUIRED SUB-SKILL — use `superpowers:executing-plans` or `superpowers:subagent-driven-development` to work this plan task-by-task. Steps use checkbox syntax (`- [ ]`) for tracking. Human approval gates are called out with **STOP** markers.

**Milestone:** M1 of the [Sprint 10 Completion Strategy](../specs/2026-07-08-sprint-10-completion-strategy.md).

**Goal:** Prove the full spine end-to-end with a two-event-kind slice (`bed.assigned` + `encounter.admitted`) — closes **Sprint 09 v2 DoD item 4** (E2E pipeline).

**Sub-slices delivered:**

- **S10.2** — 3 eventstream notebooks (`01_bronze_eventstream`, `02_silver_eventstream`, `03_gold_eventstream`) imported into `ws-ihzhhpf-sit-data`
- **S10.3** — 2 of 4 fact tables validated end-to-end (`fact_bed_assignment`, `fact_encounter`); other 2 land as notebook byproducts but not measured
- **S10.4** — 2 measures authored + round-tripped (`Currently Assigned Beds`, `Active Encounters`)
- **S10.8** — 2 visual tiles on Page 1 (KPI cards for the 2 measures)

Non-goals in M1: 6 other measures, all Page 2 visuals, RLS, PHI fixture, agents, verifier CI.

**Architecture:** 4 sequential PRs to `main`, gated by user approval before any Fabric REST write. Full context in the [completion strategy spec §3](../specs/2026-07-08-sprint-10-completion-strategy.md#m1--vertical-slice-e2e).

---

## Prerequisites (verify before Task 1)

- [ ] On `main` branch, clean: `git switch main; git pull`
- [ ] Sprint 10 charter merged; PRs #127, #128, #129, #130 all in `main`
- [ ] Sprint 10 completion strategy spec ([`2026-07-08-sprint-10-completion-strategy.md`](../specs/2026-07-08-sprint-10-completion-strategy.md)) merged
- [ ] T1 supersession annotation ([`2026-07-06-sprint-10-t1-eventstream-plan.md`](2026-07-06-sprint-10-t1-eventstream-plan.md) top of file) merged
- [ ] Fabric F2 SIT `fabricihzhhpfsit` state `Active` — `az resource show --ids /subscriptions/66a9953a-.../resourceGroups/rg-ihzhhpf-sit/providers/Microsoft.Fabric/capacities/fabricihzhhpfsit --query properties.state`
- [ ] Fabric SIT keep-alive workflow running green — `gh run list --workflow "Fabric SIT Keep-Alive" --limit 3` shows successes
- [ ] Container App `ca-sim-capacity-ihzhhpf-sit` running revision `--0000002`, image `cri75lbu5sj4hza.azurecr.io/sim-capacity:sprint10-t1`
- [ ] Fabric Eventstream `es-capacity-events-sit` (`7b65dfa1-c523-412f-93b2-a78eaa2788fa`) published; envelopes visible in Data preview
- [ ] `az` authenticated to SIT tenant: `az account show --query user.name -o tsv` → `admin@mngenvmcap164444.onmicrosoft.com`
- [ ] `gh` authenticated: `gh auth status`

---

## File structure

Files created or modified across the 4 PRs:

### PR-M1-A — Notebook import (S10.2)

- Optionally add: `data-platform/notebooks/eventstream/01_bronze_eventstream.ipynb`, `02_silver_eventstream.ipynb`, `03_gold_eventstream.ipynb` if they do not yet exist in the repo
- No infra changes
- Add: `docs/sprints/sprint-10/evidence/m1-a-notebook-import.md` — evidence for PR-M1-A

### PR-M1-B — Fact table validation (S10.3 partial)

- Add: `docs/sprints/sprint-10/evidence/m1-b-fact-tables.md` — evidence with row counts, DAX outputs, timestamps

### PR-M1-C — Measure authoring (S10.4 partial)

- Modify: `data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/fact_bed_assignment.tmdl` — add `Currently Assigned Beds` measure
- Modify: `data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/fact_encounter.tmdl` — add `Active Encounters` measure
- Modify: `data-platform/reports/capacity-dashboard.SemanticModel/definition/model.tmdl` — measure inventory pointer (if pattern requires)
- Add: `docs/sprints/sprint-10/evidence/m1-c-measures.md` — evidence with TMDL round-trip proof

### PR-M1-D — Visual tiles + M1 close (S10.8 partial)

- Modify: `data-platform/reports/capacity-dashboard.Report/definition/pages/page1-capacity/page.json` — add 2 KPI tile definitions
- Modify: `data-platform/reports/capacity-dashboard.Report/definition/pages/page1-capacity/README.md` — layout note update
- Add: `docs/sprints/sprint-10/evidence/m1-vertical-slice.md` — consolidated M1 close-out evidence (screenshots + all sub-evidence links)
- Modify: `docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md` — flip DoD item 4 to `[x]` + bump to v2.2.0

### GitHub

- Update tracker issue #107 after each PR merges
- Comment on deliverable issues #109 (S10.2) and #110 (S10.3) as M1 slices land
- Do **not** close #109 or #110 in M1 — they close at M2 completion

---

## Task 1 — S10.2 slice: Notebook import (PR-M1-A)

**Branch:** `sprint-10/m1-a-notebook-import`

- [ ] **Step 1 — STOP + human approval**

Confirm prerequisites checklist above. Wait for explicit user "go" before Step 2.

- [ ] **Step 2 — Branch off `main`**

```powershell
git switch main; git pull
git switch -c sprint-10/m1-a-notebook-import
```

- [ ] **Step 3 — Locate or author the 3 eventstream notebooks**

Check if the eventstream notebooks exist:

```powershell
Get-ChildItem data-platform/notebooks/eventstream -Filter "0[1-3]_*.ipynb" -ErrorAction SilentlyContinue
```

Two branches:

- **Branch A (notebooks exist):** proceed to Step 4
- **Branch B (notebooks missing):** they must be authored before import. Author under `data-platform/notebooks/eventstream/` following the pattern of `data-platform/notebooks/reference/01_bronze_master_data.ipynb` etc. Bronze reads from the Fabric-managed Eventstream Delta output (the Custom Endpoint's landing table under `Tables/bronze_eventstream/`); silver cleanses + normalises; gold emits the 4 fact tables. Route by `eventKind` in silver.
  - This is a scope-extension inside PR-M1-A. Keep the notebook logic minimal — the M1 slice only needs 2 fact tables materialised correctly (`fact_bed_assignment`, `fact_encounter`); the other 2 (`fact_bed_state`, `fact_forecast_output`) can be emitted with placeholder logic that will be filled in M2.

- [ ] **Step 4 — Dry-run import**

```powershell
python data-platform/scripts/import_notebooks.py f3af9733-9503-4e92-98f9-a901d96f1c87 "data-platform/notebooks/eventstream/*.ipynb" --lakehouse-id 30594c20-46ba-40ea-91fa-4701b105e0b9 --lakehouse-name lh_ihzhhpf_sit --dry-run
```

Expected: 3 notebook payload sizes printed; no REST calls made. Sanity-check base64 encoding + target paths.

- [ ] **Step 5 — Real import**

```powershell
python data-platform/scripts/import_notebooks.py f3af9733-9503-4e92-98f9-a901d96f1c87 "data-platform/notebooks/eventstream/*.ipynb" --lakehouse-id 30594c20-46ba-40ea-91fa-4701b105e0b9 --lakehouse-name lh_ihzhhpf_sit
```

Expected: 3 POSTs to workspace; each returns 201 or 202 then `state: Succeeded`.

- [ ] **Step 6 — Verify notebooks in workspace**

```powershell
$token = az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv
Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/f3af9733-9503-4e92-98f9-a901d96f1c87/notebooks" -Headers @{Authorization="Bearer $token"} | Select-Object -ExpandProperty value | Where-Object { $_.displayName -match 'eventstream' } | Select-Object displayName, id
```

Expected: 3 notebooks named `01_bronze_eventstream`, `02_silver_eventstream`, `03_gold_eventstream` with valid GUIDs. Capture the GUIDs for evidence.

- [ ] **Step 7 — Author evidence report**

Create `docs/sprints/sprint-10/evidence/m1-a-notebook-import.md` v1.0.0 with:

- Import timestamps
- 3 notebook GUIDs from Step 6
- Branch A/B indicator from Step 3
- If Branch B, brief description of the notebook logic authored (with an M2 pointer for the placeholder facts)

- [ ] **Step 8 — Commit + push + PR**

```powershell
git add data-platform/notebooks/eventstream/ docs/sprints/sprint-10/evidence/m1-a-notebook-import.md
git commit -m "feat(m1-a): import 3 eventstream notebooks into ws-ihzhhpf-sit-data`n`nSprint 10 M1 slice of S10.2. Notebooks emit fact tables consumed by M1-B (fact_bed_assignment, fact_encounter) and M2 (fact_bed_state, fact_forecast_output).`n`nRefs #109. Requirements: partial: FR-DATA-001, FR-DATA-003"
git push -u origin sprint-10/m1-a-notebook-import
gh pr create --base main --title "feat(m1-a): import 3 eventstream notebooks into SIT workspace" --label sprint-10
```

- [ ] **Step 9 — CI green + merge**

```powershell
gh pr checks <PR#>
gh pr merge <PR#> --squash --delete-branch
git switch main; git pull
```

---

## Task 2 — S10.3 slice: Fact table validation (PR-M1-B)

**Branch:** `sprint-10/m1-b-fact-tables`

**Prerequisite:** PR-M1-A merged and green.

- [ ] **Step 1 — STOP + human approval**

Confirm PR-M1-A evidence report is complete and notebooks are visible in the workspace.

- [ ] **Step 2 — Branch off `main`**

```powershell
git switch main; git pull
git switch -c sprint-10/m1-b-fact-tables
```

- [ ] **Step 3 — Confirm producer envelopes are flowing**

```powershell
az containerapp show -g rg-ihzhhpf-sit -n ca-sim-capacity-ihzhhpf-sit --query "properties.runningStatus" -o tsv
```

Expected: `Running`. If not, `./infra/scripts/Resume-FabricCapacity.ps1 -Environment sit` then restart the Container App:

```powershell
az containerapp revision restart -g rg-ihzhhpf-sit -n ca-sim-capacity-ihzhhpf-sit --revision ca-sim-capacity-ihzhhpf-sit--0000002
```

Then wait ~40s and verify envelopes in Fabric Data preview.

- [ ] **Step 4 — Run notebooks in order**

```powershell
python data-platform/scripts/run_notebooks.py f3af9733-9503-4e92-98f9-a901d96f1c87 01_bronze_eventstream 02_silver_eventstream 03_gold_eventstream
```

Expected: 3 sequential runs; each returns `status: Completed`; total wall-clock ~5–10 min. If any step returns `Failed`, open a notebook debug session in the workspace — do NOT retry blindly.

- [ ] **Step 5 — Verify the 2 M1 fact tables are queryable via Direct Lake**

Open the capacity-dashboard semantic model in Fabric web modeling → **Explore** or **Analyze in Excel** → paste:

```dax
EVALUATE ROW("bed_assignments", COUNTROWS(fact_bed_assignment), "encounters", COUNTROWS(fact_encounter))
```

Expected: both columns return positive integers. Capture the values.

- [ ] **Step 6 — Verify the other 2 fact tables landed (byproduct check)**

Same session, run:

```dax
EVALUATE ROW("bed_states", COUNTROWS(fact_bed_state), "forecasts", COUNTROWS(fact_forecast_output))
```

Expected: both return positive integers (may be 0 if placeholder logic was used in Task 1 Branch B — that is OK; M1 does not require these to be populated).

- [ ] **Step 7 — Author evidence report**

Create `docs/sprints/sprint-10/evidence/m1-b-fact-tables.md` v1.0.0 with:

- Notebook run timestamps + `runId`s from Step 4
- DAX result rows from Steps 5 + 6
- Producer sim window: start-of-run Container App revision timestamp + evidence-capture timestamp
- If Step 6 returned 0 for the M2 facts, note that placeholder logic was used and M2 will replace it

- [ ] **Step 8 — Commit + push + PR + merge**

```powershell
git add docs/sprints/sprint-10/evidence/m1-b-fact-tables.md
git commit -m "feat(m1-b): validate fact_bed_assignment + fact_encounter via Direct Lake`n`nSprint 10 M1 slice of S10.3. 2 of 4 fact tables validated end-to-end. fact_bed_state and fact_forecast_output land as notebook byproducts and are validated in M2.`n`nRefs #110. Requirements: partial: FR-DATA-005, NFR-PERF-001"
git push -u origin sprint-10/m1-b-fact-tables
gh pr create --base main --title "feat(m1-b): fact_bed_assignment + fact_encounter validated via Direct Lake" --label sprint-10
gh pr checks <PR#>
gh pr merge <PR#> --squash --delete-branch
git switch main; git pull
```

---

## Task 3 — S10.4 slice: Author 2 measures (PR-M1-C)

**Branch:** `sprint-10/m1-c-measures`

**Prerequisite:** PR-M1-B merged and green.

- [ ] **Step 1 — STOP + human approval**

Confirm both M1 fact tables are queryable and PR-M1-B evidence is complete.

- [ ] **Step 2 — Branch off `main`**

```powershell
git switch main; git pull
git switch -c sprint-10/m1-c-measures
```

- [ ] **Step 3 — Author measure `Currently Assigned Beds`**

In Fabric web modeling, open the `capacity-dashboard` semantic model → select `fact_bed_assignment` table → **New measure**:

```dax
Currently Assigned Beds =
CALCULATE(
    DISTINCTCOUNT(fact_bed_assignment[bed_id]),
    FILTER(
        fact_bed_assignment,
        fact_bed_assignment[assignment_end] = BLANK() || fact_bed_assignment[assignment_end] > NOW()
    )
)
```

Set **Format** to Whole Number, **Home Table** to `fact_bed_assignment`, **Category** to `KPI`.

- [ ] **Step 4 — Author measure `Active Encounters`**

Same modeling session → select `fact_encounter` table → **New measure**:

```dax
Active Encounters =
CALCULATE(
    DISTINCTCOUNT(fact_encounter[encounter_id]),
    FILTER(
        fact_encounter,
        fact_encounter[discharge_at] = BLANK() || fact_encounter[discharge_at] > NOW()
    )
)
```

Same format/category settings, home table `fact_encounter`.

- [ ] **Step 5 — TMDL round-trip**

Locally:

```powershell
./data-platform/scripts/export_semantic_model_tmdl.ps1 -WorkspaceId f3af9733-9503-4e92-98f9-a901d96f1c87 -SemanticModelId 08245059-a6e7-489f-a765-a3114583db4c
```

Expected: script exits 0 and reports the new measure count. Diff should show 2 new measures (one per target table).

- [ ] **Step 6 — Local DAX sanity check**

Same Fabric web modeling session, in Explore:

```dax
EVALUATE
ROW(
    "Currently Assigned Beds", [Currently Assigned Beds],
    "Active Encounters", [Active Encounters]
)
```

Expected: both return positive integers, correlated with the counts from Task 2 Step 5.

- [ ] **Step 7 — Author evidence report**

Create `docs/sprints/sprint-10/evidence/m1-c-measures.md` v1.0.0 with:

- Both DAX definitions
- TMDL diff summary (measures added)
- Sanity-check DAX result from Step 6
- Timestamp of Fabric web modeling save + local export
- Confirmation the local TMDL tree matches the cloud model (round-trip proven)

- [ ] **Step 8 — Commit + push + PR + merge**

```powershell
git add data-platform/reports/capacity-dashboard.SemanticModel/ docs/sprints/sprint-10/evidence/m1-c-measures.md
git commit -m "feat(m1-c): author Currently Assigned Beds + Active Encounters measures`n`nSprint 10 M1 slice of S10.4. 2 of 8 Option D measures authored + round-tripped to TMDL. Remaining 6 land in M2.`n`nRequirements: partial: FR-CX-005, FR-VIZ-001"
git push -u origin sprint-10/m1-c-measures
gh pr create --base main --title "feat(m1-c): 2 M1 measures authored via Fabric web modeling + TMDL round-trip" --label sprint-10
gh pr checks <PR#>
gh pr merge <PR#> --squash --delete-branch
git switch main; git pull
```

---

## Task 4 — S10.8 slice + M1 close (PR-M1-D)

**Branch:** `sprint-10/m1-d-visuals-and-close`

**Prerequisite:** PR-M1-C merged and green.

- [ ] **Step 1 — STOP + human approval**

Confirm both M1 measures visible in the semantic model and PR-M1-C evidence is complete.

- [ ] **Step 2 — Branch off `main`**

```powershell
git switch main; git pull
git switch -c sprint-10/m1-d-visuals-and-close
```

- [ ] **Step 3 — Wire 2 KPI tiles on Page 1**

Open the `capacity-dashboard.pbip` in Power BI Desktop → Page 1 (`page1-capacity`) → add 2 KPI visuals:

- **Tile 1:** KPI card, data field `[Currently Assigned Beds]`, title "Currently Assigned Beds", position per `page1-capacity/README.md` §KPI row column 1
- **Tile 2:** KPI card, data field `[Active Encounters]`, title "Active Encounters", position per `page1-capacity/README.md` §KPI row column 2

Save the report. `.pbip` folder should now contain the visual definitions under `page1-capacity/visualContainers/`.

- [ ] **Step 4 — Local round-trip**

```powershell
git status --short
git diff --stat data-platform/reports/capacity-dashboard.Report/
```

Expected: 2 new visualContainer JSON files under `page1-capacity/visualContainers/`. `page.json` updated to reference them.

- [ ] **Step 5 — Publish to Fabric + verify live render**

Publish via Power BI Desktop or `fabric-cli` (whichever is set up). Open the published report in Fabric browser and verify:

- Both KPI cards render positive integers (no "Blank", no "This visual has encountered an error")
- Values match the DAX sanity check from Task 3 Step 6 within Direct Lake refresh latency (~1 min)

Capture a screenshot of the rendered Page 1.

- [ ] **Step 6 — Flip Sprint 09 v2 DoD item 4**

Edit `docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md`:

- Locate DoD item 4 line "**CARRY-OVER → Sprint 10:** Fabric F2 SIT runs the full pipeline end-to-end..."
- Replace with "[x] Fabric F2 SIT runs the full pipeline end-to-end (delivered by Sprint 10 M1 — see PRs #A #B #C #D)"
- Bump the sprint-09 doc header to v2.2.0, Previous Version 2.1.0 (with the parenthetical hint pattern)

- [ ] **Step 7 — Author M1 close evidence report**

Create `docs/sprints/sprint-10/evidence/m1-vertical-slice.md` v1.0.0 consolidating the M1 slice:

- Screenshot from Step 5
- Links to the 3 sub-PR evidence reports (m1-a, m1-b, m1-c)
- End-to-end pipeline flow summary (Container App → Custom Endpoint → bronze → silver → gold → Direct Lake → visuals)
- Timestamps of the full pipeline round trip: envelope emit → Fabric preview → Direct Lake refresh → visual render
- Sprint 09 v2 DoD item 4 closure evidence
- M1 exit criteria checklist all `[x]`

- [ ] **Step 8 — Commit + push + PR + merge**

```powershell
git add data-platform/reports/capacity-dashboard.Report/ docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md docs/sprints/sprint-10/evidence/m1-vertical-slice.md
git commit -m "feat(m1-d): 2 KPI tiles rendered on Page 1 + M1 close`n`nSprint 10 M1 vertical slice complete. Sprint 09 v2 DoD item 4 (E2E pipeline) delivered.`n`nRefs #107. Requirements: partial: FR-VIZ-001, FR-VIZ-002, NFR-PERF-001"
git push -u origin sprint-10/m1-d-visuals-and-close
gh pr create --base main --title "feat(m1-d): Page 1 KPI tiles render live + M1 close" --label sprint-10
gh pr checks <PR#>
gh pr merge <PR#> --squash --delete-branch
git switch main; git pull
```

---

## Task 5 — M1 close-out (no PR, GitHub-only)

- [ ] **Step 1 — Update tracker #107**

Check off M1 rows for S10.2, S10.3, S10.4, S10.8 (as slices). Comment on tracker with a link to the M1 close evidence report.

- [ ] **Step 2 — Comment on deliverable issues**

- #109 (S10.2): "M1 slice landed — see PR #A + m1-a evidence. Remaining scope in M2."
- #110 (S10.3): "M1 slice landed — 2 of 4 fact tables validated. Remaining 2 in M2."
- (S10.4 issue): "M1 slice — 2 of 8 measures authored. Remaining 6 in M2."
- (S10.8 issue): "M1 slice — 2 KPI tiles rendered on Page 1. Remaining visuals in M2."

Do **not** close #109, #110, or the S10.4 / S10.8 issues — they close at M2 completion.

- [ ] **Step 3 — Announce M1 done + M2 handoff**

Post a summary comment on tracker #107:

- M1 exit criteria all ✅
- Sprint 09 v2 DoD item 4 closed
- Handoff to M2 (thicken the spine): 2 remaining fact tables + 6 remaining measures + all remaining visuals + OR loader

---

## Rollback per task

| Task | Rollback |
| ---- | -------- |
| Task 1 (M1-A notebook import) | `DELETE /v1/workspaces/{ws}/notebooks/{id}` per notebook GUID from Step 6; revert PR-M1-A via `gh pr revert`. |
| Task 2 (M1-B fact validation) | No fact-table state to revert (notebooks emit tables idempotently). Revert PR-M1-B (evidence-only). Optional: `DROP TABLE fact_bed_assignment; DROP TABLE fact_encounter;` via Lakehouse SQL if a clean re-run is needed. |
| Task 3 (M1-C measures) | In Fabric web modeling → delete the 2 new measures; run `export_semantic_model_tmdl.ps1` again to confirm removal; revert PR-M1-C. |
| Task 4 (M1-D visuals + close) | In Power BI Desktop → delete the 2 KPI containers; save; commit revert. Revert DoD item 4 flip on the sprint-09 doc; drop back to v2.1.0. |

## References

- [Sprint 10 completion strategy §3 M1](../specs/2026-07-08-sprint-10-completion-strategy.md#m1--vertical-slice-e2e) — this plan implements that section
- [Sprint 10 charter §6 DoD](../../sprints/sprint-10-e2e-pipeline-and-dashboard-completion.md#6-definition-of-done) — Sprint 09 v2 DoD item 4 closure criteria
- [Sprint 09 v2 sprint doc](../../sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md) — DoD item 4 carry-over annotation to be flipped
- [T1 plan superseded](2026-07-06-sprint-10-t1-eventstream-plan.md) — historical + supersession notice
- [ADR-0019](../../adr/0019-fabric-eventstream-custom-endpoint-entra-id.md) — Custom Endpoint architecture (context for the "bronze reads from Fabric-managed Delta output" pattern in Task 1)
- [`data-platform/scripts/import_notebooks.py`](../../../data-platform/scripts/import_notebooks.py) — Fabric REST notebook import (used in Task 1)
- [`data-platform/scripts/run_notebooks.py`](../../../data-platform/scripts/run_notebooks.py) — Fabric REST notebook run trigger (used in Task 2)
- [`data-platform/scripts/export_semantic_model_tmdl.ps1`](../../../data-platform/scripts/export_semantic_model_tmdl.ps1) — TMDL round-trip (used in Task 3)
- [Live evidence — PR #128 comment](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/128) — 2026-07-08 08:03Z envelope-flow proof
