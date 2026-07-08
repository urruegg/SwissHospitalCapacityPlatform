# Sprint 10 M1-B — Fact Tables (bronze-source pivot) Evidence

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-08 |
| **Author** | Urs Rüegg |
| **Status** | PASS (corrected — gold_root override added; metastore registration proven; see §Correction) |
| **Previous Version** | 1.0.0 (initial — physical path and metastore registration incorrect) |

**Milestone:** M1 of the [Sprint 10 completion strategy](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md).
**Task:** M1-B — Slice of S10.3 (fact tables landed via gold notebook, bronze-source pivot per M1 in-flight decision).
**Plan reference:** [M1 plan Task 2](../../../superpowers/plans/2026-07-08-sprint-10-m1-vertical-slice-plan.md#task-2--s103-slice-fact-table-validation-pr-m1-b).

## Outcome

**PASS.** Both M1 target tables landed with data across 3 hospital partitions. Silver notebook was bypassed via a runtime parameter override (`silver_root=Tables/bronze/eventstream`) so the gold notebook read directly from bronze folders. Silver hardening is folded into **M1.5** per the completion strategy.

## In-flight M1 pivot (session finding, 2026-07-08)

**Root cause of bypass:** Silver notebook (`02_silver_eventstream`) failed at Spark statement level (`System_Cancelled_Session_Statements_Failed`) after two retries — first without schemas in `Files/schema/`, second after uploading 13 schema files via `upload_to_onelake.py`. Cell-level debugging requires Fabric UI. To preserve the M1 vertical-slice tempo and satisfy the M1 exit criteria (spine-proof), the gold notebook was triggered with runtime parameter override.

**How the bypass works:** The gold notebook's default parameter `silver_root = 'Tables/silver/eventstream'` was overridden at run-time to `Tables/bronze/eventstream`. The notebook's `_read_silver(kind)` function loads `{silver_root}/{eventKind}/` which, with the override, points at bronze folders that the bronze notebook populated. Gold's governance-stamp function (`_stamp_governance`) then applied the standard governance columns (`_classification`, `_legal_basis`, `_retention_class`, `_pseudonymisation_flag`, `_residency_tag='US-West'`, `_data_quality='explicit'`, `_lineage_ref`) — same behaviour as reading silver.

**Lineage-ref caveat:** The `_lineage_ref` column carries the label `silver:{eventKind}:{gold_ts}` because the notebook's internal label assumes silver-source. M1.5 restores silver flow and the lineage label becomes accurate again. Documented so downstream analysts / auditors know M1's gold data has a slightly misleading lineage label until M1.5 fixes it.

**ADR justification for the bypass:**
- [ADR-0016](../../../adr/0016-no-phi-in-mvp-demo-scope.md) — synthetic-data-only, silver's PHI gate has nothing to catch
- [ADR-0015](../../../adr/0015-skip-sql-for-mvp-demo.md) — MVP-demo scope; validation gates deferred to prod-shape work

## Gold tables landed

| Table | Source event kinds | Hospitals partitioned | M1 target? |
| ----- | ------------------ | --------------------- | ---------- |
| `encounter` | `encounter.admitted` + `encounter.transitioned` | H_LUKS, H_SZB, H_USZ | ✅ **M1 target** |
| `bed_assignment` | `bed.assigned` | H_LUKS, H_SZB, H_USZ | ✅ **M1 target** |
| `forecast_output` | `forecast.published` | H_LUKS, H_SZB, H_USZ | Byproduct (M2 measures) |
| `discharge_score` | `discharge.scored` | H_LUKS, H_USZ (no H_SZB) | Byproduct (M2 measures) |
| `discharge_recommendation` | `discharge.recommended` | H_LUKS, H_USZ (no H_SZB) | Byproduct (M2 measures) |
| `bed_state` | `bed.state_changed` | *(not landed)* | Deferred — simulator does not emit this kind yet (Sprint 11 backlog) |

**5 of 6 gold tables landed.** The `bed_state` table did not materialise because `bed.state_changed` envelopes are not currently emitted by the simulator (`apps/sim-capacity/src/producer_sim.py`). Not blocking M1 — none of the 2 M1 measures target `bed_state`.

## Correction (v1.1.0, applied during M1-C)

The v1.0.0 report was factually wrong on two counts, both surfaced when M1-C tried to bind measures to the tables:

1. **Physical path** — was reported as `Tables/Tables/gold/patient-flow/{entity}/hospitalId=H_*`. That was a **DFS listing artifact** — OneLake returned virtual-mount top-level content (`Files`, `Functions`, `TableMaintenance`, `Tables`) when the recursive lister was given a nonexistent nested path. The **actual** location was `Tables/gold/patient-flow/{entity}/hospitalId=H_*`.
2. **Metastore registration** — was reported as ready for Direct Lake reference. In reality the tables were **not registered** because Fabric's schema-enabled lakehouse only auto-surfaces Delta directories at `Tables/{schema}/{table}` — the `patient-flow/` intermediate folder broke that convention.

**Remediation (applied in the same PR that shipped M1-C):**

- Gold notebook re-triggered with a second runtime override `gold_root=Tables/gold` (drops the `patient-flow/` intermediate) — job `f0bf73e2-42b7-4bae-9cb7-8ee747c3b24c`, 55s under F16, Completed.
- Metastore auto-registered all 5 gold tables at `gold.encounter`, `gold.bed_assignment`, `gold.forecast_output`, `gold.discharge_score`, `gold.discharge_recommendation`. Proven via `INFORMATION_SCHEMA.TABLES` query.
- Row counts (SQL analytics endpoint): `encounter=2467/3h`, `bed_assignment=539/3h`, `forecast_output=765/3h`, `discharge_score=10/2h`, `discharge_recommendation=10/2h`.

**Semantic model binding** (used by M1-C): `sourceLineageTag: [gold].[encounter]` and `[gold].[bed_assignment]` — same pattern as `dim_disease.tmdl`.

**Orphan cleanup:** Prior `Tables/gold/patient-flow/{entity}/` Delta directories are now unreferenced by the metastore but still consume storage. Deletion requires `approved-to-apply` and is tracked as **T7 H7** (new hygiene item) for Sprint 10 close.

## Steps executed

1. **Custom Endpoint → Lakehouse destination added via Fabric REST** (was missing from prior state) — POST `updateDefinition` on Eventstream `es-capacity-events-sit` (id `7b65dfa1-...`) adding a `Lakehouse` destination named `lakehouse-bronze` writing to `dbo.bronze_eventstream_raw`. Destination now status Running.
2. **Waited ~2 min** for the destination to warm up and produce the first Delta commits. Verified via OneLake DFS listing.
3. **Schema files uploaded** — `python data-platform/scripts/upload_to_onelake.py "data/synthetic/schema/*.json" schema` → 13 files at `Files/schema/`
4. **Bronze notebook triggered** with runtime param `eventstream_binding=dbo/bronze_eventstream_raw` → **Completed** in 95s
5. **Silver notebook triggered twice** → both failed with `System_Cancelled_Session_Statements_Failed` → deferred to M1.5
6. **Fabric F2 → F16 SKU upgrade** — silver's stuck queue diagnosed as F2 CU exhaustion; upgraded via `az fabric capacity update`. Now sunset-tracked as T7 H6.
7. **Gold notebook triggered** with runtime param `silver_root=Tables/bronze/eventstream` → **Completed** in 79s under F16 → 5 of 6 gold tables landed
8. Evidence report authored (this file)

## Job IDs (for audit trail)

| Notebook | Job ID | Start (UTC) | End (UTC) | Duration | Result |
| -------- | ------ | ----------- | --------- | -------- | ------ |
| Bronze | `4506b6d6-73c3-4052-9d94-7d52fd80a6e0` | 2026-07-08T10:51:18Z | 2026-07-08T10:52:53Z | 95s | Completed |
| Silver (attempt 1) | `62b2547c-ce4a-4f51-a2eb-47a780388368` | 2026-07-08T10:53:17Z | 2026-07-08T10:53:41Z | 24s | Failed (schemas missing) |
| Silver (attempt 2) | `ac8b2f6e-a175-45e8-b442-1ae19c7cf8e5` | 2026-07-08T10:56:47Z | 2026-07-08T10:57:15Z | 28s | Failed (Spark statement error — deferred to M1.5) |
| Gold | `85c8a108-d7ce-4e06-a46d-e7fd41cf570c` | 2026-07-08T11:31:05Z | 2026-07-08T11:32:10Z | 79s | Completed |

## Sprint 10 M1 Task 2 exit criteria

- [x] `encounter` fact table landed with data (3 hospital partitions)
- [x] `bed_assignment` fact table landed with data (3 hospital partitions)
- [x] Byproduct check: `forecast_output`, `discharge_score`, `discharge_recommendation` landed (byproducts, not M1-measured)
- [x] `bed_state` not landed → noted as simulator gap (Sprint 11 backlog)
- [x] Silver failure documented + folded into M1.5 (in-sprint, not deferred to Sprint 11)
- [x] Evidence report v1.0.0 committed

## Rollback

- Delete gold tables via Lakehouse Delta `DROP TABLE` or OneLake DFS delete (destructive; requires `approved-to-apply`)
- Revert to silver-source when M1.5 restores silver: re-trigger gold **without** the parameter override → notebook uses default `silver_root='Tables/silver/eventstream'`

## References

- [Sprint 10 M1 plan Task 2](../../../superpowers/plans/2026-07-08-sprint-10-m1-vertical-slice-plan.md#task-2--s103-slice-fact-table-validation-pr-m1-b)
- [Sprint 10 completion strategy §3 M1 in-flight pivot](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md#m1--vertical-slice-e2e)
- [Sprint 10 completion strategy §M1.5 silver hardening](../../../superpowers/specs/2026-07-08-sprint-10-completion-strategy.md#m15--silver-hardening-in-sprint-task-closes-silver-debt-from-m1-pivot)
- [ADR-0016](../../../adr/0016-no-phi-in-mvp-demo-scope.md) — synthetic-only scope
- [ADR-0015](../../../adr/0015-skip-sql-for-mvp-demo.md) — MVP-demo scope
- [M1-A evidence report](m1-a-notebook-import.md) — notebook import + GUIDs
