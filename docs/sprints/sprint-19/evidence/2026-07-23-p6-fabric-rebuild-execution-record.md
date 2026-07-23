# Sprint 19 — PROD Switzerland North rebuild: Fabric (P6) execution record

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-23 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | — (new evidence artefact) |

Execution record for **Phase 6 (Fabric data platform)** of the DR-style
teardown + Switzerland North greenfield rebuild
([ADR-0037](../../../adr/0037-prod-region-switzerland-north-greenfield.md),
issue [#239](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/239)).
Runbook: [`sprint-19-prod-switzerland-north-dr-rebuild-runbook.md`](../../../runbooks/sprint-19-prod-switzerland-north-dr-rebuild-runbook.md).

Approval: `approved-to-apply` granted in-session by repo OWNER @urruegg
(2026-07-23). All commands scoped to `*-prod*` / `rg-ihzhhpf-prod`; no
`rg-ihzhhpf-sit` resource was touched.

## Result summary

PROD Fabric rebuilt greenfield in **switzerlandnorth**. Full medallion
(bronze/silver/gold) regenerated reproducibly from committed synthetic seeds;
semantic models + report published via `fabric-cicd`.

| Artefact | Value |
|----------|-------|
| Capacity | `fabricihzhhpfprod` (F2, `59f0cacf-0516-4b19-bbb0-e760f239f4fd`, **Active**) |
| Workspace | `ws-ihzhhpf-prod-data` (`1c8408f4-6eb7-401f-aee9-77fe4c8a515e`) |
| Lakehouse | `lh_ihzhhpf_prod` (`57bd6e02-5248-439c-9f31-16bf9ee83cb4`, **schemas-enabled**, `defaultSchema=dbo`) |
| Delta tables | **50** (bronze/silver/gold across master-data + eventstream) |
| Semantic models | `capacity-dashboard`, `external-signals` (published) |
| Report | `capacity-dashboard` (published) |
| SQL endpoint | `lh_ihzhhpf_prod` (provisioned) |

## Blockers encountered and fixes

### 1. Schemas-enabled lakehouse required

The first medallion run failed on `01_bronze_master_data` with
`System_Cancelled_Session_Statements_Failed` (fast fail, ~30s). Root cause: the
lakehouse was created without schemas, but the notebooks issue
`CREATE SCHEMA IF NOT EXISTS bronze` and `saveAsTable('bronze.<table>')`, which
require a **schemas-enabled** lakehouse (SIT lakehouse carries
`defaultSchema=dbo`).

Fix: deleted the non-schemas lakehouse and recreated with
`creationPayload.enableSchemas=true` (new id `57bd6e02-...`); re-pointed
`environments.yml` + `parameter.yml`.

### 2. Seed files absent in the fresh lakehouse

Subsequent runs fail-fast because the medallion notebooks read source data from
`Files/`. A greenfield lakehouse has no `Files/`, so the seeds were uploaded via
`data-platform/scripts/upload_to_onelake.py`:

| Target `Files/` folder | Source (repo) | Files |
|------------------------|---------------|-------|
| `master-data/capacity/` | `data/master-data/capacity/*.csv` | 9 CSV |
| `eventstream-seed/` | `data/synthetic/eventstream/eventstream_raw.json` | 1 JSON |
| `or-samples/` | `data/synthetic/or-samples/*.json` | 2 JSON |

## Execution steps (all `--apply` under the approval gate)

1. `POST /workspaces/.../lakehouses` with `enableSchemas=true` → `lh_ihzhhpf_prod`.
2. `upload_to_onelake.py` × 3 (master-data, eventstream-seed, or-samples).
3. `run_medallion.py --environment PROD --apply` — created + ran the 8 reference
   + eventstream notebooks in dependency order; all `[ok]`:
   `01_bronze_master_data → 02_silver_master_data → 03_gold_master_data →
   04_load_or_samples → 00_seed_eventstream_raw → 01_bronze_eventstream →
   02_silver_eventstream → 03_gold_eventstream`.
4. Verified 50 Delta tables via OneLake DFS (`_delta_log` enumeration). Gold
   layer: `bed_assignment`, `bed_state`, `encounter`, `discharge_recommendation`,
   `discharge_score`, `forecast_output`, `or_case`, `or_schedule`, all `dim_*`,
   `fact_capacity_baseline`, `map_disease_treatment_specialty_service`.
5. `deploy_fabric_cicd.py --environment PROD --mode publish` — published
   `capacity-dashboard` + `external-signals` semantic models and the
   `capacity-dashboard` report (Direct Lake source path rewritten SIT→PROD via
   `parameter.yml` `find_replace`). `fabric-cicd` requires Python `<3.14`; run on
   Python 3.11.

## Config changes committed

+ `data-platform/fabric/environments.yml` — PROD block: `workspace_id`,
  `lakehouse_id`, `region=switzerlandnorth`; header region note updated.
+ `data-platform/reports/parameter.yml` — PROD `replace_value` for workspace +
  lakehouse GUIDs.

`fabric-cicd --environment PROD --mode validate`: **PASS**.

## Capacity state

SIT and PROD Fabric capacities are both **Active** — they mirror, so PROD is
left Active (no pause). Direct Lake serving for the dashboard requires an active
capacity.

## Scope assertion

+ Deleted / created: only Fabric items under `ws-ihzhhpf-prod-data` and the
  `fabricihzhhpfprod` capacity (`rg-ihzhhpf-prod`).
+ Untouched: `rg-ihzhhpf-sit` (SIT workspace `f3af9733-...`, lakehouse
  `30594c20-...`, capacity `fabricihzhhpfsit`) and all shared resources.

## Remaining (gated)

+ **P7 (DNS/Entra)** — re-point `app.curavias.ch` in the shared
  `rg-ihzhhpf-sit` DNS zone + Entra `ihzhhpf-app` redirect URI. Touches **shared**
  resources → **STOP; separate approval required.**
+ **P8** — E2E validation incl. live Foundry inference + final PROD evidence doc.
