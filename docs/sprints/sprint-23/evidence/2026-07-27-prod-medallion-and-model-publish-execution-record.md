# Sprint 23 — PROD Switzerland North: org/skills medallion + semantic-model publish execution record

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-27 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | n/a (new evidence artefact) |

Execution record for the **live PROD materialization** of the Sprint 23 unified
Curavias organisation spine + org/skills medallion, and the subsequent
**semantic-model + report publish**, into the Switzerland North PROD Fabric
workspace ([issue #255](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/255)).

Builds on the Sprint 19 greenfield PROD rebuild
([`prod-evidence-switzerlandnorth.md`](../../sprint-19/prod-evidence-switzerlandnorth.md),
[ADR-0037](../../../adr/0037-prod-region-switzerland-north-greenfield.md)): that
sprint materialized the *pre-Sprint-23* 50-table medallion; this record captures
the **re-run with the Sprint 23 org/skills notebooks** (Curavias re-brand +
org spine + skills domain) and the model publish over the refreshed gold.

**Approval:** `approved-to-apply` granted in-session by repo OWNER @urruegg
(2026-07-26 for the medallion run; 2026-07-27 for the semantic-model publish). All
commands scoped to `*-prod*` / `rg-ihzhhpf-prod` and the PROD Fabric workspace;
no `rg-ihzhhpf-sit` resource was touched.

**Environment:** subscription `66a9953a-df37-4c51-856c-9971b9bf3e03`, tenant
`1337187a-4c41-4da9-8fca-731bba7a4329` (MngEnvMCAP164444), short name `ihzhhpf`,
region **switzerlandnorth**. Synthetic data only, no PHI
([ADR-0013](../../../adr/0013-temporary-us-region-demo-scope.md),
[ADR-0016](../../../adr/0016-no-phi-in-mvp-demo-scope.md); `NFR-SKILL-002`).

## Requirements evidenced

Deployment coverage (live PROD) for `FR-ORG-001` (Curavias org spine + re-keyed
facts), `FR-SKILL-001` to `FR-SKILL-008` + `FR-SKILL-ONT-001` (org/skills gold
domain), `FR-DATA-005` (governed semantic models published for dashboard/copilot
consumption), and `NFR-SKILL-002` (synthetic, no-PHI, git-owned generator).

## Result summary

PROD org/skills medallion materialized reproducibly from committed synthetic
seeds; `capacity-dashboard` + `external-signals` semantic models and the
`capacity-dashboard` report published via `fabric-cicd` (Direct Lake over the
refreshed PROD gold).

| Artefact | Value |
|----------|-------|
| Capacity | `fabricihzhhpfprod` (F2, `59f0cacf-0516-4b19-bbb0-e760f239f4fd`, **Active**) |
| Workspace | `ws-ihzhhpf-prod-data` (`1c8408f4-6eb7-401f-aee9-77fe4c8a515e`) |
| Lakehouse | `lh_ihzhhpf_prod` (`57bd6e02-5248-439c-9f31-16bf9ee83cb4`, schemas-enabled) |
| Delta tables | **49** total, **28 gold** |
| SemanticModel `capacity-dashboard` | Published (**id `7d8b4b76-1470-47e2-8e1f-c47e6af68c8a`**) |
| SemanticModel `external-signals` | Published (`3855b539-2dcb-47ed-bd02-9c86087a627c`) |
| Report `capacity-dashboard` | Published |

## Phase 1 — medallion run (2026-07-26, `approved-to-apply` @urruegg)

### Seeds uploaded to OneLake `Files/`

`data-platform/scripts/upload_to_onelake.py` (33 files across 5 folders):

| Target `Files/` folder | Source (repo) | Files |
|------------------------|---------------|-------|
| `master-data/curavias-org-skills/` | `data/master-data/curavias-org-skills/*.csv` | 21 CSV |
| `skills-evidence/` | `data-platform/notebooks/skills-evidence/*.py` | 3 PY |
| `master-data/capacity/` | `data/master-data/capacity/*.csv` | 9 CSV |
| `or-samples/` | `data/synthetic/or-samples/*.json` | 2 JSON |
| `eventstream-seed/` | `data/synthetic/eventstream/*.json` | 1 JSON |

### Notebook run

`python data-platform/scripts/fabric/run_medallion.py --environment PROD --apply`
— created/updated + ran the 9 notebooks in dependency order; all `[ok]`:
`01_bronze_master_data → 02_silver_master_data → 03_gold_master_data →`
**`05_gold_org_skills`** `→ 04_load_or_samples → 00_seed_eventstream_raw →`
`01_bronze_eventstream → 02_silver_eventstream → 03_gold_eventstream`.
"Medallion rebuild complete."

### Gold layer verified (28 tables)

OneLake DFS `_delta_log` enumeration. New Sprint 23 org/skills gold:
`dim_org_unit`, `dim_department`, `dim_skill`, `dim_occupation_role`,
`dim_care_setting`, `dim_capacity_unit`, `fact_skill_assertion`,
`fact_skill_demand`, `fact_skill_gap`, `bridge_worker_unit_eligibility`,
`bridge_role_skill_demand_template`. Retained patient-flow/capacity gold:
`bed_assignment`, `bed_state`, `encounter`, `discharge_recommendation`,
`discharge_score`, `forecast_output`, `or_case`, `or_schedule`, the capacity
`dim_*`, `fact_capacity_baseline`, `map_disease_treatment_specialty_service`.

`python data-platform/scripts/verify_gold_schema.py --produced <list>` →
**PASS** ("gold parity (21 contract tables covered)", exit 0).

## Phase 2 — semantic-model + report publish (2026-07-27, `approved-to-apply` @urruegg)

Run on **Python 3.11** (`fabric-cicd` requires Python `<3.14`; the workstation
default is 3.14). `fabric-cicd 1.2.0` + `azure-identity` in a dedicated venv.

1. `deploy_fabric_cicd.py --environment PROD --mode validate` → OK (network-free;
   variable library + `parameter.yml` agree, Direct Lake monikers rewritten
   SIT→PROD).
2. `--mode publish` → **complete (exit 0)** after clearing two operational
   blockers (below). `capacity-dashboard` + `external-signals` semantic models
   and the `capacity-dashboard` report published; `evidence` / `bva-boardroom`
   excluded by regex as designed.

### Blockers encountered and fixes

1. **F2 capacity was Paused.** First publish failed with
   `Dataset_Import_FailedToImportDataset` / "Premium capacity connection health
   issue" (Fabric auto-paused the capacity after the overnight medallion run).
   Fix: `az resource invoke-action --action resume` on `fabricihzhhpfprod` →
   Active.
2. **Broken unbound Direct Lake dataset.** `capacity-dashboard` (dataset
   `84ac3f92-…`, created during the paused attempt) was stuck
   `DMTS_MonikerWithUnboundDataSources` (unbound OneLake source) while
   `external-signals` bound cleanly from the identical source. Fix: deleted the
   broken dataset (Fabric REST `DELETE /workspaces/{ws}/semanticModels/{id}`) →
   republished clean; `capacity-dashboard` re-created with a fresh id
   `7d8b4b76-…` and bound successfully.

## Capacity state

The F2 capacity was **resumed** for the publish and **left Active** — Direct Lake
serving for the published dashboard requires an active capacity. Re-pausing for
cost is an operational decision tracked in the session handoff; it does not
affect the committed artefacts.

## Scope assertion

+ Created / updated: only Fabric items under `ws-ihzhhpf-prod-data` and the
  `fabricihzhhpfprod` capacity (`rg-ihzhhpf-prod`). The broken
  `capacity-dashboard` dataset shell was deleted and re-created within the same
  publish operation (no committed artefact affected; the model definition lives
  in git).
+ Untouched: `rg-ihzhhpf-sit` (SIT workspace `f3af9733-…`, lakehouse
  `30594c20-…`, capacity `fabricihzhhpfsit`) and all shared resources.

## Remaining (gated / parked)

+ **EventHub live source bind** for the skills-events lane — parked on Fabric
  workspace-identity GA for Event Hubs sources
  ([ADR-0043 Update 2026-07-26](../../../adr/0043-preview-tier-permitted-in-prod-swn-for-demo.md#update-2026-07-26--live-eventhub-bind-deferred-platform-gap)).
  The synthetic `CustomEndpoint` lane remains the live demo transport.
+ **Live skills publisher** (HRIS/LMS connector) — not built; simulators feed the
  lane per `NFR-SKILL-001`.
