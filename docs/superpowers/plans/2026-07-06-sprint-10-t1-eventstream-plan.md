# Sprint 10 T1 — Eventstream + Facts Implementation Plan

| Field | Value |
| ----- | ----- |
| **Status** | **Superseded (2026-07-08)** — see supersession notice below |
| **Superseded by** | [`docs/superpowers/specs/2026-07-08-sprint-10-completion-strategy.md`](../specs/2026-07-08-sprint-10-completion-strategy.md) (design) + [`docs/superpowers/plans/2026-07-08-sprint-10-m1-vertical-slice-plan.md`](2026-07-08-sprint-10-m1-vertical-slice-plan.md) (execution) |

## Supersession notice — 2026-07-08

This plan was authored on 2026-07-06 for the **Fabric Azure Event Hubs source connector** ingest path. Between 2026-07-06 and 2026-07-08 the architecture pivoted to **Fabric Custom Endpoint + Entra ID** per [ADR-0019](../../adr/0019-fabric-eventstream-custom-endpoint-entra-id.md). The original plan is retained below for audit purposes; do **not** follow its steps.

### What was achieved (Task 1 equivalent — S10.1 delivered under the new architecture)

- Fabric Eventstream `es-capacity-events-sit` (id `7b65dfa1-c523-412f-93b2-a78eaa2788fa`) provisioned in workspace `ws-ihzhhpf-sit-data` (`f3af9733-9503-4e92-98f9-a901d96f1c87`)
- Custom Endpoint source `capacity-events-source` published — endpoint FQDN `esehmwhyivddgq8acv3ghwv.servicebus.windows.net`, hub `esehmwhyivddgq8acv3ghwv_eh`
- Producer identity `id-ca-sim-capacity-ihzhhpf-sit` (Entra objectId `b646f093-cbbc-496f-8a65-376b39ff04d3`) assigned Contributor on the workspace via Fabric REST
- sim-capacity Container App revision `--0000002` running the real Python producer image (`cri75lbu5sj4hza.azurecr.io/sim-capacity:sprint10-t1`) with MI-based ACR pull
- Envelopes verified end-to-end in Fabric Data preview 2026-07-08 08:03Z: `forecast.published`, `bed.assigned`, `encounter.transition`, `encounter.admitted` for hospital `H_SZB` (sim run `run-bee8588bac3c`)
- Fabric SIT keep-alive workflow live and running green (Sprint 10 T1 temporary override per [runbook §Sprint 10 T1](../../runbooks/fabric-capacity-lifecycle.md#sprint-10-t1-keep-alive-override-temporary))

### What pivoted (why this plan is now superseded)

- **MCAPS tenant Modify policy** auto-reverts `disableLocalAuth=true` on all Event Hubs namespaces. Confirmed via activity log; cannot be exempted (Microsoft owns the definition).
- **Fabric Azure EH source connector** only supports Shared Access Key auth today (verified against [Microsoft Learn](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-source-azure-event-hubs) and portal testing with hub-scope Data Receiver + admin OAuth token).
- Intersection: SAS impossible in this tenant, OAuth unsupported by the connector → only viable path is **Fabric Custom Endpoint** with Entra ID producer auth.
- Steps 3–9 of this plan's Task 1 (bicepparam fill, Azure-EH portal connection, post-deploy REST script) are no longer applicable. Replacement work: [`PR #128`](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/128), [`PR #129`](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/129), [`PR #130`](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/130).

### Where the remaining work goes

Task 2 (S10.2 — notebook import) and Task 3 (S10.3 — fact-table validation) of this plan are **partially superseded** — they still need to happen, but under the Custom Endpoint architecture and re-sequenced into the vertical-slice M1..M4 approach documented in [`2026-07-08-sprint-10-completion-strategy.md`](../specs/2026-07-08-sprint-10-completion-strategy.md).

Execution instructions for the M1 slice (which covers `bed.assigned` + `encounter.admitted` end-to-end): [`2026-07-08-sprint-10-m1-vertical-slice-plan.md`](2026-07-08-sprint-10-m1-vertical-slice-plan.md).

Remaining charter deliverables map as follows:

| Charter ID | Status | Where |
| ---------- | ------ | ----- |
| S10.1 Eventstream provisioning | ✅ done under ADR-0019 architecture | PR #128, #129, #130 + this file's *What was achieved* section |
| S10.2 Eventstream notebooks | Pending — M1 sub-slice covers import; M2 covers full validation | M1 plan Task 1 |
| S10.3 4 fact tables | Pending — M1 validates 2 of 4 (bed_assignment + encounter); M2 validates the remaining 2 | M1 plan Task 2; M2 covers the rest |

### Cleanup

- Local branch `sprint-10/t1-s10.1-eventstream-deploy` has dangling commits `40cfc61` + `d35ce00` from mid-session workflow issues; tracked as **T7 H1** in the completion strategy — requires `approved-to-apply` before deletion.

---

> **Historical content below — do not follow these steps.** Retained for audit trail per [copilot-instructions §9](../../../.github/copilot-instructions.md#9-document-versioning). All active guidance moved to the M1 plan linked above.

---

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship deliverables **S10.1 + S10.2 + S10.3** — operationalise the Sprint 09 T2.2 Eventstream scaffolding so 4 gold fact tables (`fact_encounter`, `fact_bed_state`, `fact_bed_assignment`, `fact_forecast_output`) are queryable via Direct Lake from the capacity-dashboard semantic model.

**Architecture:** 3 sequential PRs to `main` (one per deliverable), gated by user approval before any Azure/Fabric REST call. Full design in [`docs/superpowers/specs/2026-07-06-sprint-10-t1-eventstream-design.md`](../specs/2026-07-06-sprint-10-t1-eventstream-design.md).

**Tech Stack:** Bicep (existing module), PowerShell 5.1 (existing post-deploy script), Python + Fabric REST (existing helper scripts), Fabric portal (1 interactive step).

---

## Prerequisites (verify before starting)

- [ ] On `main` branch, clean: `git switch main; git pull`
- [ ] Sprint 10 kickoff planning trio merged (PRs #103–#106)
- [ ] Sprint 10 T1 design brief merged (this planning PR)
- [ ] Sprint 10 tracker issue #107 exists; deliverable issues #108–#110 exist
- [ ] `az` authenticated to SIT tenant: `az account show --query name` → `ME-MngEnvMCAP164444-urruegg-1`
- [ ] `gh` authenticated: `gh auth status`
- [ ] Fabric F2 SIT capacity `fabricihzhhpfsit` in state `Active` — `az resource show --ids /subscriptions/66a9953a-.../resourceGroups/rg-ihzhhpf-sit/providers/Microsoft.Fabric/capacities/fabricihzhhpfsit --query properties.state`
- [ ] Fabric workspace + lakehouse exist: workspace `f3af9733-9503-4e92-98f9-a901d96f1c87`, lakehouse `30594c20-46ba-40ea-91fa-4701b105e0b9` (per checkpoint §2.2)
- [ ] Event Hub `evh-capacity-events-sit` in namespace `evh-ihzhhpf-sit` exists with consumer group `cg-fabric-eventstream`

---

## File Structure

Files created or modified across the 3 PRs:

#### PR-T1-A — S10.1 Eventstream provisioning

- Modify: `infra/environments/sit.bicepparam` — fill 2 empty params
- Modify: `infra/modules/data-platform/fabric-eventstream/post-deploy/configure-eventstream.ps1` — replace `<REQUIRES-FABRIC-MANAGED-CONNECTION-ID>` after portal step returns
- Add: `docs/sprints/sprint-10/evidence/t1-eventstream-provisioning.md` — evidence report for S10.1

#### PR-T1-B — S10.2 Notebook import

- Add: `docs/sprints/sprint-10/evidence/t1-notebook-import.md` — evidence report for S10.2
- Possibly modify: `data-platform/notebooks/eventstream/*.ipynb` — only if R1 (fact-table gap) requires notebook authoring (in which case a scope-extension PR is opened)

#### PR-T1-C — S10.3 Fact-table registration + verification

- Add: `docs/sprints/sprint-10/evidence/t1-fact-tables-registered.md` — evidence report for S10.3
- Possibly add: `data-platform/notebooks/eventstream/04_gold_facts.ipynb` — if R1 requires (scope extension)

#### Local-tree ops (interactive)

- Portal step: create Fabric-managed connection to `evh-ihzhhpf-sit` — no repo files, records connection GUID for use in Step 2

#### GitHub

- Update issue #107 (tracker) after each PR merges
- Close issues #108, #109, #110 as each deliverable completes

---

## Task 1 — S10.1: Eventstream provisioning (PR-T1-A)

**Branch:** `sprint-10/t1-s10.1-eventstream-provision`

**Files:** see PR-T1-A file structure above.

- [ ] **Step 1: STOP + user confirmation before any Azure/Fabric call**

Per Sprint 10 kickoff decision, all deploys pause for user approval. Reviewer confirms:

- ✅ F2 SIT is active and F2 has capacity headroom for an Eventstream (included in F2, no extra cost)
- ✅ User understands: this creates a live Fabric Eventstream item that will begin consuming from the EH consumer group `cg-fabric-eventstream` immediately after wiring — cost billed against F2 SIT capacity (already active)
- ✅ Portal step is understood + user is ready to perform it interactively (design brief §5.3)

Wait for explicit user "go" before Step 2.

- [ ] **Step 2: Branch off `main`**

```powershell
git switch main; git pull
git switch -c sprint-10/t1-s10.1-eventstream-provision
```

- [ ] **Step 3: Fill 2 empty bicepparams**

Edit `infra/environments/sit.bicepparam`. Locate the T2.2 block (~line 82) and update:

```bicep
param fabricEventstreamWorkspaceId = 'f3af9733-9503-4e92-98f9-a901d96f1c87'
param fabricEventstreamDestinationLakehouseId = '30594c20-46ba-40ea-91fa-4701b105e0b9'
```

Then `az bicep build --file infra/main.bicep` to catch any compile errors.

- [ ] **Step 4: Run `what-if` — DO NOT DEPLOY YET**

```powershell
az deployment group what-if --resource-group rg-ihzhhpf-sit --template-file infra/main.bicep --parameters infra/environments/sit.bicepparam
```

Expected: shows the eventstream module deployment; no existing resources affected because Fabric items are provisioned by the post-deploy script, not ARM. If `what-if` fails, fix Bicep issues in a small dedicated PR before continuing.

- [ ] **Step 5: PORTAL STEP — create Fabric-managed EH connection (user interactive)**

Per design brief §5.3:

1. Open [Fabric workspace connections](https://app.fabric.microsoft.com/groups/f3af9733-9503-4e92-98f9-a901d96f1c87/managementhub/connections)
2. **New connection → Cloud → Azure Event Hubs**
3. Namespace: `evh-ihzhhpf-sit.servicebus.windows.net`
4. Authentication: **Organizational Account** (admin@mngenvmcap164444) or **Service Principal**
5. Privacy level: **Organizational**
6. **Capture the connection GUID** (from URL bar or connection details) — needed in Step 6.

Record the GUID for the evidence report.

- [ ] **Step 6: Update `configure-eventstream.ps1` with connection GUID**

Edit `infra/modules/data-platform/fabric-eventstream/post-deploy/configure-eventstream.ps1`. Locate `<REQUIRES-FABRIC-MANAGED-CONNECTION-ID>` (approx line 85) and replace with the connection GUID from Step 5. Commit as a separate file change so the connection wiring is auditable.

- [ ] **Step 7: Deploy Bicep (real)**

```powershell
az deployment group create --resource-group rg-ihzhhpf-sit --template-file infra/main.bicep --parameters infra/environments/sit.bicepparam --name eventstream-t1
```

Capture the manifest output:

```powershell
$manifest = az deployment group show -g rg-ihzhhpf-sit -n eventstream-t1 --query "properties.outputs.eventstreamManifest.value" -o json
$manifest | Out-File -Encoding utf8 eventstream-manifest.json
```

Expected: deployment succeeds; `moduleStatus` output reads `fabric-eventstream-scaffold-only-see-post-deploy-script`.

- [ ] **Step 8: Run post-deploy REST script**

```powershell
./infra/modules/data-platform/fabric-eventstream/post-deploy/configure-eventstream.ps1 -ManifestPath ./eventstream-manifest.json
```

Expected: script POSTs to Fabric REST; returns success + Eventstream item GUID. Capture for evidence.

- [ ] **Step 9: Verify Eventstream provisioned**

```powershell
$token = az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv
Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/f3af9733-9503-4e92-98f9-a901d96f1c87/eventstreams" -Headers @{Authorization="Bearer $token"} | ConvertTo-Json -Depth 5
```

Expected: 1 item returned with `displayName` = `es-ihzhhpf-events` and source + destination configured.

- [ ] **Step 10: Author S10.1 evidence report**

Create `docs/sprints/sprint-10/evidence/t1-eventstream-provisioning.md` v1.0.0 with:

- Timestamps of Steps 5, 7, 8, 9
- Portal-step connection GUID (redacted last 4 chars)
- Eventstream item GUID
- Manifest JSON (attached inline)
- Verification query output (`GET /v1/workspaces/{ws}/eventstreams`)
- Cleanup of local `eventstream-manifest.json` (don't commit — contains connection reference)

- [ ] **Step 11: Delete local manifest file (contains connection GUID)**

```powershell
Remove-Item eventstream-manifest.json
```

- [ ] **Step 12: Commit + push + PR**

```powershell
git add infra/environments/sit.bicepparam infra/modules/data-platform/fabric-eventstream/post-deploy/configure-eventstream.ps1 docs/sprints/sprint-10/evidence/t1-eventstream-provisioning.md
git commit -m "feat(s10.1): provision Fabric Eventstream in SIT + fill bicepparam+connection GUID`n`nS10.1 delivered. Eventstream item es-ihzhhpf-events created in workspace`nf3af9733-...; source cg-fabric-eventstream on evh-capacity-events-sit;`ndestination Tables/bronze_eventstream on lh_ihzhhpf_sit.`n`nCloses #108`n`nRefs FR-DATA-001, FR-DATA-003, FR-DATA-005, NFR-PERF-001, NFR-GOV-004"
git push -u origin sprint-10/t1-s10.1-eventstream-provision
gh pr create --base main --title "feat(s10.1): provision Fabric Eventstream in SIT" --body-file <path>
```

- [ ] **Step 13: Wait for CI green + merge**

```powershell
gh pr checks <PR#>
gh pr merge <PR#> --merge --delete-branch
git switch main; git pull
```

---

## Task 2 — S10.2: Notebook import (PR-T1-B)

**Branch:** `sprint-10/t1-s10.2-notebook-import`

- [ ] **Step 1: STOP + user confirmation**

Confirm S10.1 verified green. If Task 1 Step 9 didn't return the expected Eventstream item, do not proceed — debug via issue #108.

- [ ] **Step 2: Branch off `main`**

```powershell
git switch main; git pull
git switch -c sprint-10/t1-s10.2-notebook-import
```

- [ ] **Step 3: Dry-run import first**

```powershell
python data-platform/scripts/import_notebooks.py f3af9733-9503-4e92-98f9-a901d96f1c87 "data-platform/notebooks/eventstream/*.ipynb" --lakehouse-id 30594c20-46ba-40ea-91fa-4701b105e0b9 --lakehouse-name lh_ihzhhpf_sit --dry-run
```

Expected: prints 3 notebook payload sizes; no REST calls made. Sanity-check the base64 encoding + target paths.

- [ ] **Step 4: Real import**

```powershell
python data-platform/scripts/import_notebooks.py f3af9733-9503-4e92-98f9-a901d96f1c87 "data-platform/notebooks/eventstream/*.ipynb" --lakehouse-id 30594c20-46ba-40ea-91fa-4701b105e0b9 --lakehouse-name lh_ihzhhpf_sit
```

Expected: 3 notebooks POSTed to workspace; each returns HTTP 201 or 202; script polls until each shows `state: Succeeded`.

- [ ] **Step 5: Verify notebooks in workspace**

```powershell
$token = az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv
Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/f3af9733-9503-4e92-98f9-a901d96f1c87/notebooks" -Headers @{Authorization="Bearer $token"} | Select-Object -ExpandProperty value | Where-Object { $_.displayName -match 'eventstream' } | Select-Object displayName, id
```

Expected: 3 notebooks named `01_bronze_eventstream`, `02_silver_eventstream`, `03_gold_eventstream`.

- [ ] **Step 6: Discovery check for R1 (fact-table gap)**

**Critical:** grep each notebook for the 4 target fact table names + `saveAsTable` calls:

```powershell
foreach ($nb in Get-ChildItem data-platform/notebooks/eventstream/*.ipynb) {
    Write-Host "=== $($nb.Name) ==="
    Select-String -Path $nb -Pattern 'fact_encounter|fact_bed_state|fact_bed_assignment|fact_forecast_output|saveAsTable|CREATE TABLE'
}
```

**Two branches:**
- **Branch A — All 4 fact tables produced:** proceed to Task 3.
- **Branch B — Fact tables NOT produced:** the eventstream notebooks land bronze-only. R1 triggered. Open `S10.3-extension` issue for a new `04_gold_facts.ipynb` notebook + defer Task 3 until that ships. Document the discovery on issue #109 as an S10.2 addendum. This adds ~1 day of scope.

- [ ] **Step 7: Author S10.2 evidence report**

Create `docs/sprints/sprint-10/evidence/t1-notebook-import.md` v1.0.0 with:

- 3 notebook GUIDs from workspace
- Import timestamps
- Result of R1 discovery check (Branch A or B)
- Link to S10.3-extension issue if Branch B

- [ ] **Step 8: Commit + push + PR + merge**

```powershell
git add docs/sprints/sprint-10/evidence/t1-notebook-import.md
git commit -m "feat(s10.2): import 3 eventstream notebooks to SIT workspace`n`nCloses #109. R1 discovery result: <Branch A|B>."
git push -u origin sprint-10/t1-s10.2-notebook-import
gh pr create --base main --title "feat(s10.2): import 3 eventstream notebooks to SIT"
gh pr checks <PR#>
gh pr merge <PR#> --merge --delete-branch
git switch main; git pull
```

---

## Task 3 — S10.3: Fact-table registration + verification (PR-T1-C)

**Branch:** `sprint-10/t1-s10.3-fact-tables`

**Prerequisite:** Task 2 Step 6 returned Branch A (fact tables produced by notebooks). If Branch B, this task is blocked until `S10.3-extension` PR merges.

- [ ] **Step 1: STOP + user confirmation**

Confirm Task 2 evidence report + Branch A verified.

- [ ] **Step 2: Branch off `main`**

```powershell
git switch main; git pull
git switch -c sprint-10/t1-s10.3-fact-tables
```

- [ ] **Step 3: Seed events via producer_sim**

Run for 1 hour of simulated time at 60x acceleration = 1 minute wall-clock:

```powershell
$env:EVENT_HUB_NAMESPACE = 'evh-ihzhhpf-sit'
$env:EVENT_HUB_NAME = 'evh-capacity-events-sit'
python apps/sim-capacity/src/producer_sim.py --duration-hours 1 --rate 60 --seed 42 --dry-run
```

**Dry-run first** to verify envelope shapes + counts. Expected: ~thousands of events across 6 kinds × 3 hospitals.

- [ ] **Step 4: Producer real run**

Same command without `--dry-run`:

```powershell
python apps/sim-capacity/src/producer_sim.py --duration-hours 1 --rate 60 --seed 42
```

Expected: producer publishes; Eventstream ingests; bronze `Tables/bronze_eventstream/*` starts filling.

- [ ] **Step 5: Wait ~2 min for Eventstream ingestion lag**

Fabric Eventstream typically has a 60–90s ingestion window. Verify bronze table sizes:

```powershell
$token = az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv
Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/f3af9733-9503-4e92-98f9-a901d96f1c87/lakehouses/30594c20-46ba-40ea-91fa-4701b105e0b9/tables" -Headers @{Authorization="Bearer $token"} | Select-Object -ExpandProperty data | Where-Object { $_.name -match 'bronze_eventstream' }
```

Expected: at least 1 table exists at the bronze prefix.

- [ ] **Step 6: Run notebooks in order via `run_notebooks.py`**

```powershell
python data-platform/scripts/run_notebooks.py f3af9733-9503-4e92-98f9-a901d96f1c87 01_bronze_eventstream 02_silver_eventstream 03_gold_eventstream
```

Expected: 3 sequential runs; each returns `status: Completed`; total wall-clock ~5–10 min.

- [ ] **Step 7: Verify 4 fact tables registered**

```powershell
$tables = Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/f3af9733-9503-4e92-98f9-a901d96f1c87/lakehouses/30594c20-46ba-40ea-91fa-4701b105e0b9/tables" -Headers @{Authorization="Bearer $token"} | Select-Object -ExpandProperty data
$expected = @('fact_encounter', 'fact_bed_state', 'fact_bed_assignment', 'fact_forecast_output')
foreach ($t in $expected) {
    $found = $tables | Where-Object { $_.name -eq $t }
    if ($found) { Write-Host "OK: $t" } else { Write-Host "FAIL: $t missing" }
}
```

Expected: all 4 print `OK`. If any print `FAIL`, debug via issue #110.

- [ ] **Step 8: Verify Direct Lake queryability (smoke test)**

Open the capacity-dashboard semantic model in Fabric web modeling; use "Explore" or "Analyze in Excel" to run a trivial DAX against `fact_encounter`:

```dax
EVALUATE ROW("cnt", COUNTROWS(fact_encounter))
```

Expected: returns a positive integer.

- [ ] **Step 9: Author S10.3 evidence report**

Create `docs/sprints/sprint-10/evidence/t1-fact-tables-registered.md` v1.0.0 with:

- Table names + row counts from Step 7
- Screenshot or output of Step 8 DAX result
- Notebook run timestamps + `runId`s from Step 6
- Producer sim window (start + end timestamps)

- [ ] **Step 10: Commit + push + PR + merge**

```powershell
git add docs/sprints/sprint-10/evidence/t1-fact-tables-registered.md
git commit -m "feat(s10.3): 4 fact tables registered in gold, Direct Lake verified`n`nCloses #110. T1 track complete. Sprint 09 v2 DoD item 4 (E2E pipeline)`nnow satisfied for 4 of 6 event kinds."
git push -u origin sprint-10/t1-s10.3-fact-tables
gh pr create --base main --title "feat(s10.3): 4 fact tables registered + Direct Lake verified"
gh pr checks <PR#>
gh pr merge <PR#> --merge --delete-branch
git switch main; git pull
```

---

## Task 4 — T1 track close (no PR, GitHub-only)

- [ ] **Step 1: Update tracker #107 to check off T1 deliverables**

```powershell
gh issue view 107 --json body -q .body | Out-File -Encoding utf8 tracker.md
# Edit tracker.md — check [x] for S10.1, S10.2, S10.3
gh issue edit 107 --body-file tracker.md
Remove-Item tracker.md
```

- [ ] **Step 2: Verify all 3 deliverable issues closed**

```powershell
gh issue view 108 --json state -q .state  # expect closed
gh issue view 109 --json state -q .state  # expect closed
gh issue view 110 --json state -q .state  # expect closed
```

- [ ] **Step 3: Sprint 09 v2 DoD item 4 status update**

Edit `docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md` DoD row 4: change `[ ] **CARRY-OVER → Sprint 10:** Fabric F2 SIT runs the full pipeline end-to-end` to `[x] Fabric F2 SIT runs the full pipeline end-to-end (delivered by Sprint 10 T1 — see PRs #<A>, #<B>, #<C>)`. Small doc-only PR; bumps sprint-09 doc to v2.2.0.

- [ ] **Step 4: T1 track exit criteria met**

Verify all items in design brief §Sprint 10 T1 exit criteria are green.

---

## Rollback per task

- **Task 1 rollback:** delete Eventstream item via `DELETE /v1/workspaces/{ws}/eventstreams/{id}`; revert bicepparam edits via `gh pr revert`; portal-side connection can be left for future use (no cost impact).
- **Task 2 rollback:** delete imported notebooks via `DELETE /v1/workspaces/{ws}/notebooks/{id}`; revert evidence doc PR.
- **Task 3 rollback:** delete fact tables via Fabric Explorer or Lakehouse SQL DROP TABLE; producer_sim doesn't need explicit rollback (bounded run window).
- **Full T1 rollback (if T1 turns out infeasible in this sprint):** all 3 PRs reverted; Eventstream + notebooks deleted; sprint-09 DoD row 4 stays as CARRY-OVER; T1 track reopened in the next sprint or with revised scope.

---

## Estimation

- Task 1 (S10.1): 30–60 min (portal step interactive; user pace)
- Task 2 (S10.2): 15–30 min (dry-run + real import + discovery check)
- Task 3 (S10.3): 45–90 min (producer sim run + notebook chain + verification); +1 day if R1 Branch B triggered
- Task 4 (close): 10 min

**Total for T1 track (Branch A):** 100–190 min in-session + user portal interaction.
**Total for T1 track (Branch B, R1 triggered):** add 1 full day for `S10.3-extension` notebook authoring + review.

---

## References

- Sprint 10 T1 design brief: [`docs/superpowers/specs/2026-07-06-sprint-10-t1-eventstream-design.md`](../specs/2026-07-06-sprint-10-t1-eventstream-design.md)
- Sprint 10 charter §5 rows S10.1, S10.2, S10.3
- Sprint 10 kickoff plan (precedent for 3-PR + local-op pattern): [`2026-07-06-sprint-10-kickoff-plan.md`](2026-07-06-sprint-10-kickoff-plan.md)
- Sprint 09 checkpoint §9 (deferred items origin): [`docs/sprints/sprint-09/checkpoint-2026-07-06-fabric-and-model.md`](../../sprints/sprint-09/checkpoint-2026-07-06-fabric-and-model.md#9-deferred-items-do-not-block-model-authoring)
- Related issues: #107 tracker, #108 S10.1, #109 S10.2, #110 S10.3
