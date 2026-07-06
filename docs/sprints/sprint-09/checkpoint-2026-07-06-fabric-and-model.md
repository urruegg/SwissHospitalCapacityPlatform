# Sprint 09 v2.0.0 — Data-model authoring checkpoint (2026-07-06)

| Field | Value |
| ----- | ----- |
| Version | 1.2.0 |
| Date | 2026-07-06 |
| Author | Urs Rüegg |
| Status | In progress — Direct Lake semantic model authoring |
| Previous Version | 1.1.0 (recorded Option A measure inventory — 5 authored, 8 deferred; added Sprint 10 handoff for Option D) |

> Durable handoff snapshot written before a system + VS Code restart. Captures Fabric SIT config, PROD-replication checklist, current local repo state, and next actions to resume the semantic-model authoring flow.

---

## 1. Where we are

The Sprint 09 v2.0.0 data pipeline is **partially materialised** in the SIT Fabric lakehouse:

- **`Tables/bronze/*`** — 9 master-data tables (Delta, registered under `bronze` schema)
- **`Tables/silver/*`** — 9 validated tables (Delta, registered under `silver` schema)
- **`Tables/gold/*`** — 11 registered tables under `gold` schema:
  - 9 reference dims/facts: `dim_disease`, `dim_drg`, `dim_hospital` (3 rows: USZ / LUKS / SZB, HSL deferred), `dim_hospital_service`, `dim_specialty`, `dim_treatment`, `dim_ward_capacityunit`, `fact_capacity_baseline`, `map_disease_treatment_specialty_service`
  - 2 OR facts (T5.5 fixture): `or_schedule` (1 950 rows), `or_case` (13 802 rows)
- **Missing** (needs Eventstream pipeline — deferred): `fact_encounter`, `fact_bed_state`, `fact_bed_assignment`, `fact_forecast_output`

The Direct Lake semantic model **`capacity-dashboard`** (id `08245059-a6e7-489f-a765-a3114583db4c`) exists in workspace `f3af9733-9503-4e92-98f9-a901d96f1c87` and Power BI Desktop can enumerate the tables (screenshot confirmed). Relationship authoring was blocked by capacity XMLA read-only + tenant settings — resolution steps documented in §5.

---

## 2. Fabric F2 SIT — current configuration (source-of-truth for PROD replication)

### 2.1 Azure ARM properties (via `az resource show`)

```text
name        : fabricihzhhpfsit
location    : West US 2 (ADR-0013 demo scope; Swiss-region GA target = switzerlandnorth)
sku.name    : F2
sku.tier    : Fabric
state       : Active
adminMembers: admin@mngenvmcap164444.onmicrosoft.com
tags:
  env         : sit
  owner       : platform-team
  costCenter  : ihzhhpf-sit
  workload    : hospital-capacity
```

### 2.2 Fabric REST identifiers

| Property | Value |
| -------- | ----- |
| Fabric capacity ID | `23c32d0d-f5ab-430a-ac3f-97ec985e953f` |
| Fabric workspace ID | `f3af9733-9503-4e92-98f9-a901d96f1c87` |
| Lakehouse ID (`lh_ihzhhpf_sit`) | `30594c20-46ba-40ea-91fa-4701b105e0b9` |
| Semantic model ID (`capacity-dashboard`) | `08245059-a6e7-489f-a765-a3114583db4c` |
| SQL analytics endpoint | `pimdoe2bjsuu3d6komn3u6sdfe-gol274ydswje5ghzvea5s3y4q4.datawarehouse.fabric.microsoft.com` |
| Lakehouse mode | schema-enabled (defaultSchema = `dbo`) |

### 2.3 Registered gold tables (final flat paths, schema-enabled convention)

Every table is at exactly `Tables/<schema>/<table>` — no nested `master-data/` or `reference/` or `patient-flow/` prefixes. Registration only works at 2-level depth in a schema-enabled lakehouse.

## 3. Fabric F2 PROD replication checklist

The PROD F2 capacity is not yet deployed. When it is (currently `enableFoundryHostedAgents = false` in `infra/environments/prod.bicepparam`), mirror this:

### 3.1 ARM shape

```text
name             : fabricihzhhpfprod
location         : westus2 (deferred to switzerlandnorth once Fabric IQ GA lands)
sku.name         : F2         (can scale up to F4/F8 for real prod loads)
sku.tier         : Fabric
adminMembers     : admin@mngenvmcap164444.onmicrosoft.com (+ additional PROD admin if defined)
tags:
  env         : prod
  owner       : platform-team
  costCenter  : ihzhhpf-prod
  workload    : hospital-capacity
```

The tags + SKU are governed by [`infra/environments/prod.bicepparam`](../../../infra/environments/prod.bicepparam). Nothing to change in that file to get parity.

### 3.2 Capacity-level (delegated) settings — must be flipped after PROD F2 creation

Path: **Fabric Admin Portal → Capacity settings → `fabricihzhhpfprod` → Delegated settings**

| Setting | SIT value | Set PROD to |
| ------- | --------- | ----------- |
| **XMLA endpoint** (under Semantic Model workload) | Read Write | **Read Write** |
| **Users can edit data models in the Power BI service** | Enabled | Enabled |
| **Users can create Graph** (Ontology dependency) | Enabled | Enabled |
| **Users can create and share data agent item types** | Enabled | Enabled |
| **Users can use Copilot and other features powered by Azure OpenAI** | Enabled | Enabled |
| **Data sent to Azure OpenAI can be processed outside your capacity's geographic region** | Enabled (westus2) | Depends: enable in demo, DISABLE for Swiss-region PROD |

⚠ Last row: PROD compliance decision. In demo scope (westus2 per ADR-0013) it must be On because Azure OpenAI runs outside the capacity's own region. In future Swiss-region PROD (switzerlandnorth), disable it and wait for Azure OpenAI availability in Swiss region.

### 3.3 Tenant-level settings — global, already flipped for SIT, auto-inherit to PROD

Path: **Fabric Admin Portal → Tenant settings**. Already enabled during this session (2026-07-06):

- [x] **Users can edit data models in the Power BI service**
- [x] **Allow XMLA endpoints and Analyze in Excel with on-premises datasets**
- [x] **Users can create Graph**
- [x] **Users can create and share data agent item types**
- [x] **Users can use Copilot and other features powered by Azure OpenAI**
- [x] **Data sent to Azure OpenAI can be processed outside your capacity's geographic region** (demo-scope tolerance per ADR-0016 — synthetic, no-PHI)

Skipped (not needed):

- [ ] ArcGIS GeoAnalytics for Fabric Runtime — no geospatial visuals in scope

---

## 4. Root causes learned this session

Chronological — save for troubleshooting future setups:

1. **F2 auto-pause between sessions** — Fabric F2 does **not auto-pause**, but we suspended it via `Suspend-FabricCapacity.ps1` on 2026-07-03. Direct Lake semantic model was unreachable on 2026-07-06 until Resume. **Rule: keep F2 Active while any Power BI Desktop session is open on the model.**

2. **Schema-enabled lakehouse requires 2-level paths** — the notebooks originally wrote to `Tables/bronze/master-data/dim_hospital` (nested folders). In a schema-enabled lakehouse, tables must be exactly `Tables/<schema>/<table>` to auto-register; anything deeper shows under an "Unidentified" node and is not queryable via the SQL endpoint or Direct Lake. **Fix committed in the 4 modified notebooks** (see §6).

3. **`H_HSL` (Hirslanden) breaks FK integrity** — CSVs from the AMA review included 4 hospitals but Sprint 09 v2 MVP scope is 3 (USZ / LUKS / SZB per ADR-0002). Silver gate 5 drops H_HSL rows (missing beds/staff → `_data_quality != explicit`), which cascades to gate 6 FK integrity failures on every downstream table. **Fix: filter CSVs to the 3-hospital scope before uploading** (see `.filter-hsl.py` pattern in session history; ephemeral script — recreate if needed).

4. **OR loader in Fabric context** — the T5.5 notebook was written for local-mode `Path.cwd()` repo paths. In Fabric it must read from lakehouse mount `/lakehouse/default/Files/or-samples/` and use `spark.read.json` (not `spark.createDataFrame(list)`) to survive cancelled-case columns with all-null values. **Fix committed in `04_load_or_samples.ipynb`**.

5. **XMLA Read-Only default** — Fabric F2 capacities default the XMLA endpoint to Read Only. Direct Lake "Edit" flow needs Read-Write on both the capacity AND the tenant setting. **Fixed in-portal 2026-07-06.**

6. **Missing user role for EH send** — Local `producer_sim.py` needed `Azure Event Hubs Data Sender` on the hub. Granted to admin user OID `7b9830a6-989b-4edd-b720-0d4bff7ffb2e` on 2026-07-03. Reversible.

7. **Silent-exit subagent pattern** — during Sprint 09 execution, subagents occasionally "completed with no output" while having done real work. Recovery pattern: `git status --short` + inspect filesystem + commit manually.

---

## 5. What's blocking the semantic-model authoring — RESOLVED

The `PFE_SEC_PERM_DISCOVER` error on Direct Lake Edit was caused by:

1. XMLA endpoint = Read Only on the capacity — flipped to Read Write ✅
2. Tenant settings for XMLA + model editing not enabled — flipped ✅

Post-restart validation:

1. Reopen `data-platform/reports/capacity-dashboard.pbip` in Power BI Desktop.
2. Model view should load with all 11 tables under `gold` schema (Direct Lake mode banner at bottom-right).
3. Retry relationship #1 (`dim_hospital` → `fact_capacity_baseline`).

If it still errors, the residual causes to check (in order of likelihood): (a) F2 got Paused again — resume via `./infra/scripts/Resume-FabricCapacity.ps1 -Environment sit`; (b) workspace access lost — verify `admin@mngenvmcap164444.onmicrosoft.com` has **Contributor** on `ws-ihzhhpf-sit-data`; (c) capacity delegated setting reverted — re-check portal.

---

## 6. Local uncommitted changes to preserve across restart

Verify with `git status --short` after restart. Expected untracked / modified files:

**My additions** (uncommitted improvements, worth committing later):

- `apps/sim-capacity/src/producer_sim.py` — streaming producer entrypoint
- `data-platform/scripts/upload_to_onelake.py` — OneLake file upload helper
- `data-platform/scripts/import_notebooks.py` — Fabric REST notebook import (+ lakehouse binding injection)
- `data-platform/scripts/run_notebooks.py` — Fabric REST notebook run + status polling
- `data-platform/notebooks/reference/01_bronze_master_data.ipynb` — path flattened to `Tables/bronze/`
- `data-platform/notebooks/reference/02_silver_master_data.ipynb` — path flattened to `Tables/bronze/` + `Tables/silver/`
- `data-platform/notebooks/reference/03_gold_master_data.ipynb` — path flattened to `Tables/silver/` + `Tables/gold/`
- `data-platform/notebooks/reference/04_load_or_samples.ipynb` — Fabric mount detection + `spark.read.json` + `Tables/gold/` target + diagnostic logging

**User's Power BI Desktop artefacts** (from PBIP round-trip; DO NOT touch until portal work is done):

- `data-platform/reports/capacity-dashboard.Report/.pbi/`
- `data-platform/reports/capacity-dashboard.Report/.platform`
- `data-platform/reports/capacity-dashboard.Report/StaticResources/`
- `data-platform/reports/capacity-dashboard.Report/definition/pages/ad8d9cbb00d05e04d371/` (new page ID)
- `data-platform/reports/capacity-dashboard.Report/definition/version.json`
- `data-platform/reports/capacity-dashboard.SemanticModel/.platform`
- `data-platform/reports/capacity-dashboard.SemanticModel/definition.pbism`
- `data-platform/reports/capacity-dashboard.SemanticModel/definition/cultures/`
- `data-platform/reports/capacity-dashboard.SemanticModel/definition/database.tmdl`
- Modified: `.pbip`, `.pbir`, `pages.json`, `report.json`, `model.tmdl`

**Junk** (can clean up post-commit):

- `.vscode/`, `.pytest_cache/`, `apps/sim-capacity/src/sim_capacity.egg-info/`

---

## 7. Post-restart resume workflow

Do these in order:

### Step 1 — restore environment

```powershell
cd C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform
git status --short   # verify the uncommitted files listed in §6 are still there
az login             # re-auth if needed
az account set --subscription 66a9953a-df37-4c51-856c-9971b9bf3e03
```

### Step 2 — verify F2 SIT is Active

```powershell
az resource show --ids /subscriptions/66a9953a-df37-4c51-856c-9971b9bf3e03/resourceGroups/rg-ihzhhpf-sit/providers/Microsoft.Fabric/capacities/fabricihzhhpfsit --query "properties.state" -o tsv
```

Expect `Active`. If `Paused`:

```powershell
./infra/scripts/Resume-FabricCapacity.ps1 -Environment sit
```

### Step 3 — open Power BI Desktop

`File → Recent → capacity-dashboard.pbip`. Model view should populate with 11 tables. If load error re-appears, check §5 troubleshooting.

### Step 4 — resume relationship authoring

Author these 14 relationships in Model view — all **1:*, cross-filter Single, no RI**. **12 Active + 2 Inactive** (see "Option B decisions" below):

**Hospital hub — `dim_hospital[hospital_id]` (1) → many (7)**

| # | Child table | FK column | Status |
| --- | ---------------------------------------- | -------------- | ------ |
| 1 | `fact_capacity_baseline` | `hospital_id` | Active |
| 2 | `dim_specialty` | `hospital_id` | **Inactive** — Option B |
| 3 | `dim_hospital_service` | `hospital_id` | Active |
| 4 | `dim_ward_capacityunit` | `hospital_id` | Active |
| 5 | `map_disease_treatment_specialty_service` | `hospital_id` | Active |
| 6 | `or_schedule` | `hospitalId` (camelCase, from OR source JSON) | Active |
| 7 | `or_case` | `hospitalId` (camelCase) | Active |

**Specialty sub-hub — `dim_specialty[specialty_id]` (1) → many (3)**

| # | Child table | FK column | Status |
| --- | ---------------------------------------- | -------------- | ------ |
| 8 | `dim_hospital_service` | `specialty_id` | Active |
| 9 | `dim_ward_capacityunit` | `specialty_id` | Active |
| 10 | `map_disease_treatment_specialty_service` | `specialty_id` | Active |

#### Cross-domain map — 3 dims → map

| # | From (dim) → | To (map) FK | Status |
| --- | ----------------------- | ---------------- | ------ |
| 11 | `dim_disease[disease_id]` → | `disease_id` | Active |
| 12 | `dim_treatment[treatment_id]` → | `treatment_id` | Active |
| 13 | `dim_drg[drg_code]` → | `drg_code` | Active |

#### OR self-join

| # | From (fact) → | To (fact) FK | Status |
| --- | -------------------- | ------------- | ------ |
| 14 | `or_schedule[orSlotId]` → | `or_case[orSlotId]` | **Inactive** — Option B |

#### Option B decisions (rows #2 and #14 inactive)

Rows #2 and #14 were saved as **inactive** to resolve ambiguous filter paths that Power BI rejects at Save:

- **Row #2 conflict:** Active #2 (`dim_specialty → dim_hospital`) together with active #3 / #4 / #5 (hospital → child) and #8 / #9 / #10 (specialty → child) creates two parallel paths from any of `dim_hospital_service` / `dim_ward_capacityunit` / `map_...` to `dim_hospital` — one direct, one via `dim_specialty`. Chose to keep the direct star-schema paths active and mark the snowflake arm inactive.
- **Row #14 conflict:** Active #14 (`or_case → or_schedule`) together with active #6 (`or_schedule → dim_hospital`) and #7 (`or_case → dim_hospital`) creates two paths from `or_case` to `dim_hospital` — one direct, one via `or_schedule`. Chose to keep the direct path active.

**Measure-author recipe** — when a measure needs the inactive path, wrap it in `USERELATIONSHIP`:

```dax
-- Example: count specialties available at the currently-selected hospital,
-- activating the snowflake #2 relationship for this measure only
SpecialtiesAtHospital :=
    CALCULATE(
        DISTINCTCOUNT(dim_specialty[specialty_id]),
        USERELATIONSHIP(dim_specialty[hospital_id], dim_hospital[hospital_id])
    )

-- Example: count cases per planned OR slot via inactive #14
CasesPerSlot :=
    CALCULATE(
        COUNTROWS(or_case),
        USERELATIONSHIP(or_case[orSlotId], or_schedule[orSlotId])
    )
```

### Step 5 — paste 13 DAX measures

Once relationships are saved, open [`data-platform/reports/capacity-dashboard.SemanticModel/definition/model.tmdl`](../../../data-platform/reports/capacity-dashboard.SemanticModel/definition/model.tmdl) — copy the 13 pre-authored DAX measures into Model view (Home → New measure). Each measure carries an `annotation Grounds = "hcp:..."` line — preserve it as Description.

### Step 6 — save + verify

`File → Save`. Power BI Desktop pushes the semantic model + report to the Fabric workspace via XMLA. `.pbip` and `.SemanticModel/` folder in the local repo get updated with authoritative TMDL. Then commit.

---

## 8. Cost hygiene

While F2 SIT stays Active during dev, budget ~USD 0.36/hour ≈ USD 8.60/day. When you close for the day:

```powershell
./infra/scripts/Suspend-FabricCapacity.ps1 -Environment sit
```

To resume next day: `./infra/scripts/Resume-FabricCapacity.ps1 -Environment sit`.

---

## 9. Deferred items (do NOT block model authoring)

- Fabric Eventstream setup (needs Fabric-managed EH connection — portal step in `configure-eventstream.ps1` prerequisites)
- 4 missing fact tables (`fact_encounter`, `fact_bed_state`, `fact_bed_assignment`, `fact_forecast_output`) — depend on Eventstream + running simulator
- Column-level PHI tagging in TMDL (RLS scaffold present at row-level `_data_quality="phi"` proxy)
- Full PBIP visuals (Sprint 09 T5.1 / T5.2 layout READMEs are canonical spec)
- Commit the local script + notebook fixes as a follow-up PR
- Register the modified notebooks + new scripts in the git tree (see §6)

### 9.1 Sprint 10 handoff — capacity-dashboard measures (Option D)

Sprint 09 v2 lands **5 of 13** measures ("Option A" — what the current gold schema supports). The remaining **8 measures** require schema/loader work planned for Sprint 10.

**Objective for Sprint 10 ("Option D catch-up"):** materialise the missing fact tables and add the missing `or_case` columns so all 13 spec §6.3 measures can be authored without workarounds.

| Block | Requires | Measures unblocked |
| ----- | -------- | ------------------ |
| 1. Materialise 3 missing fact tables via Eventstream + simulator | `fact_bed_state`, `fact_forecast_output`, `fact_encounter` in `lh_ihzhhpf_sit/gold/` | `Occupancy %`, `Beds Free`, `Required Capacity`, `Forecast Peak (72h)`, `ED Arrivals/hr` (5) |
| 2. Extend silver→gold OR loader to derive 5 columns from event stream | Add `isFirstCase`, `actualStart`, `plannedStart`, `cancellationLeadTimeHours`, `turnoverMinutes` on `or_case`; add `slotDurationMinutes` on `or_schedule` (or rename `plannedDurationMinutes`) | `First-Case On-Time %`, `Short-Notice Cancellation %`, `Avg Turnover Minutes` (3) |
| 3. Loader status-vocabulary alignment | Emit `status="available"` for unbooked `or_schedule` rows (currently only `blocked` / `planned`) | Restores fidelity of `Idle-Slot Minutes` (spec-exact); today's Sprint 09 authoring uses `status="blocked"` as proxy |

**Sprint 10 exit criteria for capacity-dashboard:**

- All 13 spec §6.3 measures authored and passing `-VerifyOnly` on `export_semantic_model_tmdl.ps1` (verifier must be extended in the same sprint to assert measure count).
- No red-X measures in Model view; Page 1 (bed/capacity) renders real values instead of blanks.
- Retire the Sprint 09 `Idle-Slot Minutes` proxy formula in favour of the spec-exact one.

**Reference:** measure inventory + current DAX in [`data-platform/reports/capacity-dashboard.SemanticModel/README.md` §"Measures"](../../../data-platform/reports/capacity-dashboard.SemanticModel/README.md).

---

## 10. References

- Design spec: [`docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md`](../../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md)
- Plan: [`docs/superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md`](../../superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md)
- ADR-0002 (execution runtime + 3-hospital scope)
- ADR-0013 (westus2 demo scope)
- ADR-0016 (no PHI in MVP demo)
- Sprint doc: [`docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md`](../sprint-09-master-data-simulation-and-capacity-dashboard.md)
- TMDL skeleton README: [`data-platform/reports/capacity-dashboard.SemanticModel/README.md`](../../../data-platform/reports/capacity-dashboard.SemanticModel/README.md)
