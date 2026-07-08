# Sprint 10 — Retrospective

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-08 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | 0.1.0 (stub) |

> Sprint 10 shipped **7 milestone PRs (#136–#143)** covering M1 (vertical slice), M1.5 (silver hardening), M2 (gold enrichment + heatmap), M3-A (RLS roles), M4-A (verifier + workflows), M4-B (T7 hygiene), M4-C (CI gate + this retrospective). All 4 Sprint 09 v2 CARRY-OVER items advanced: DoD 4 (E2E pipeline) fully closed; DoD 6 (RLS PHI) partial closure; DoD 6 (agent evals) + `switzerlandnorth` migration remain Sprint 11 scope. The Fabric Custom Endpoint pivot ([ADR-0019](../adr/0019-fabric-custom-endpoint-eventstream-ingestion.md)) unblocked ingestion despite the MCAPS tenant's Modify-policy blocking Azure Event Hubs SAS.

## 1. What went well

- **Vertical-slice-first execution held from M1 to M4**. Each of the 7 PRs was a single reviewable slice, ≤5-9 files, all merged without cross-slice rework. Slicing pattern (M1-A/B/C/D → M1.5 → M2 → M3-A → M4-A/B/C) matched the completion strategy verbatim.
- **`spark-operations` skill delivered on its first real use** (M1.5). Spark Advisor + driver stdout triage identified 3 sequential silver defects in ~30 min each: (1) `TypeError: cannot pickle 'rpds.HashTrieMap'` (jsonschema>=4.18 validator not pickleable), (2) envelope-mode Gate 1 gap when payload STRUCT hidden from SQL endpoint, (3) batch-contract vs per-event schema mismatch on `dc-demand-encounter-v1`. Each defect was masking the next.
- **Fabric Custom Endpoint pivot ([ADR-0019](../adr/0019-fabric-custom-endpoint-eventstream-ingestion.md)) fully validated**. The pivot from Azure Event Hubs (blocked by tenant Modify policy re-enabling SAS) to Fabric Custom Endpoint + Entra ID auth landed T1 without rework. `sim-capacity` container writes via AMQP, Eventstream materialises to `dbo.bronze_eventstream_raw`, and 3791 rows flow to gold every run.
- **TMDL round-trip finally durable** (M3-A). Sprint 09's blocker was "portal round-trip drops RLS role scaffolds". M3-A resolves this by never touching the portal — API-first `updateDefinition` → `getDefinition` preserves TMDL byte-for-byte. 4 roles + 2 PHI annotations proven to survive.
- **Portal-scaffold + API-overlay pattern for reports** (M1-D). Fabric API-created reports render 405 in this MCAPS tenant regardless of endpoint (`/items` vs `/reports`). The workaround — create scaffold via portal, then `updateDefinition` overlay — preserves ACLs while replacing all content. Documented as reusable pattern.
- **Semantic model verifier prevents Sprint 09-class silent drift** (M4-A + M4-C). `Test-MeasureAndRoleContract` asserts 11 measures + 4 roles at every PR touching the model. If Sprint 09's portal round-trip had been protected by this gate, the RLS drop would have blocked the merge.
- **T7 hygiene executed inside the sprint** (M4-B). H1 branch delete, H2 keep-alive sunset, H6 F16→F4 downscale (saves ~USD 1,300/mo) all done. H5 deferred to Sprint 11 with a concrete D+30 checklist — no dangling loose ends.
- **Cost trajectory well-managed**. F16 was temporary (raised for M1-B queueing), downscaled back to F4 immediately after M1.5 validated silver on lower CU. Actual capacity cost impact for Sprint 10: F16 for ~6 hours + F4 baseline = ~USD 20 total.

## 2. What went less well

- **Fabric API-created reports have a persistent ACL bootstrap defect in the MCAPS `wabi-us-central-b` cluster** — surfaces as `405 Failed to get access request info`. Both `/items` (generic) and `/reports` (Report-specific) endpoints fail. Cost us 2 delete-recreate cycles (approved-to-apply each) before landing on the portal-scaffold workaround. Cluster-wide issue, not a payload defect. Documented in [M1-D evidence](sprint-10/evidence/m1-d-kpi-tiles.md) as a reusable pattern.
- **DAX role emulation via REST `executeQueries` is blocked by service-principal-only constraint**. M3-A could not programmatically validate that role filters actually apply — only that the filter grammar compiles + persists. Deferred full per-role rejection proof to M3-B (needs SP registration + isolated PHI fixture lakehouse).
- **Silver notebook editing via `edit_notebook_file` corrupted cell structure once** (M1.5 mid-session). Root cause: VS Code notebook editor held changes in memory + reordered cell IDs when I did successive edits. Recovery: `git checkout` the file + apply patches via a Python JSON-level script (`_tmp_patch_silver.py` pattern). Future rule: for notebook edits with >1 change, use a `python -c "json.load ... .replace ..."` script rather than iterative `edit_notebook_file`.
- **SQL analytics endpoint metadata cache lags Delta commits by 5-15 min**. M2 and M1.5 both hit this — flat columns landed at Delta level but weren't visible via `INFORMATION_SCHEMA.COLUMNS` for several minutes. Manual refresh via `POST /sqlEndpoints/{id}/refreshMetadata` works but isn't scriptable inline. Docs need to call this out for future M-work.
- **Gold `payload` STRUCT hidden from SQL endpoint by design** was misread by me (M2) as "payload not preserved" — burned ~30 min of investigation before finding it via Delta `_delta_log/*.json` schema inspection. Rule: for Fabric SQL endpoint absence-of-column diagnoses, always confirm at Delta level before assuming upstream pipeline issue.
- **`dc-*-v1` batch-contract schemas were misapplied to per-event streaming validation** (M1.5 defect 3). Silver rejected all 3791 rows because the contract schema requires top-level `datasetId, contractId, records[]` but the streaming payload is a single `records[]` item. Fix was permissive fallback with T7 H8 tracking issue for future per-event schema derivation.

## 3. Deliverable outcome

| Track | Planned | Delivered | Deferred | Notes |
| ----- | -------: | ---------: | --------: | ----- |
| **M1 — Vertical slice E2E** | 4 tasks (M1-A/B/C/D) | 4 | 0 | 4 PRs #132/#136/#137/#138 |
| **M1.5 — Silver hardening** | 1 (in-sprint interstitial) | 1 | 0 | PR #139; 3 sequential defects diagnosed with `spark-operations` skill |
| **M2 — Gold enrichment + heatmap** | 1 | 1 | 0 | PR #140; 4 new measures + 3 slicers + Month × Weekday matrix |
| **M3 — Governance (parallel)** | 4 (S10.6, S10.7, S10.9, S10.10) | 1 (M3-A = partial S10.6) | 3 (M3-B S10.7 fixture, S10.9 eval harness, S10.10 agent hosts) | PR #141; RLS role authoring + PHI annotations proven, fixture deferred to Sprint 11 |
| **M4 — Tooling + close-out + T7** | 2 tasks + 6 T7 items | 2 tasks + 4 T7 items | 1 T7 item (H5) + agent-eval work | PRs #142/#143 + this PR |
| **Cross-cutting** | T7 hygiene backlog | H1 ✅ H2 ✅ H3 ✅ H4 ✅ H6 ✅ H5 → Sprint 11 issue | | H5 deferred by ADR-0019 30-day observation criterion |
| **Total** | ~14 discrete slices | **11 shipped** | **3 formal deferrals** | **~79% delivered fully-scoped**; 21% deferred with concrete Sprint 11 tracking |

## 4. Evidence pointers

| Milestone | Evidence file | Status |
| --------- | ------------- | ------ |
| M1-A notebook import | [`m1-a-notebook-import.md`](evidence/m1-a-notebook-import.md) | PASS |
| M1-B fact tables (bronze-source pivot) | [`m1-b-fact-tables.md`](evidence/m1-b-fact-tables.md) | PASS (v1.1.0 with path correction) |
| M1-C measures via Direct Lake | [`m1-c-measures.md`](evidence/m1-c-measures.md) | PASS (`Active Encounters=2467`, `Currently Assigned Beds=539`) |
| M1-D KPI tiles + M1 close | [`m1-d-kpi-tiles.md`](evidence/m1-d-kpi-tiles.md) | PASS (rendered live; MCAPS ACL workaround documented) |
| M1.5 silver hardening | [`m1-5-silver-hardening.md`](evidence/m1-5-silver-hardening.md) | PASS (3 defects fixed, 3791/3791 rows promoted) |
| M2 gold enrichment + heatmap | [`m2-gold-enrichment.md`](evidence/m2-gold-enrichment.md) | PASS (7 flat cols + 3 time-dim + 4 measures + 3 slicers + 1 heatmap) |
| M3-A RLS roles + PHI annotations | [`m3-a-rls-roles.md`](evidence/m3-a-rls-roles.md) | PASS (round-trip proven; per-role DAX deferred to M3-B) |
| M4-A verifier + CI workflows | [`m4-a-verifier-and-ci.md`](evidence/m4-a-verifier-and-ci.md) | PASS |
| M4-B T7 hygiene | [`m4-b-hygiene.md`](evidence/m4-b-hygiene.md) | PASS (3 executed + H5 deferred) |
| M4-C CI gate + this retrospective | this file + `.github/workflows/verify-semantic-model.yml` | PASS |

## 5. Sprint 09 v2 DoD carry-over resolution

| Sprint 09 CARRY-OVER | Sprint 10 outcome | Evidence |
| -------------------- | ----------------- | -------- |
| **DoD 4** — Fabric SIT E2E pipeline: sim → EH → Eventstream → bronze → silver → gold → SM → Page 1 + Page 2 | **✅ FULLY CLOSED** in Sprint 09 v2.2.0 update (M1-D). Full pipeline live including silver after M1.5. | [M1-D](evidence/m1-d-kpi-tiles.md) + [M1.5](evidence/m1-5-silver-hardening.md) |
| **DoD 6** — All 9 agent eval fixtures replay green via automation | **⚠️ CARRY-OVER → Sprint 11** — no work in Sprint 10; harness + runtime hosts (S10.9 + S10.10) still deferred | (no Sprint 10 evidence) |
| **DoD 8** — RLS PHI gate verified: no PHI column visible to any role | **⚠️ PARTIAL** — M3-A resolved blockers (a) portal-drop and (b) column annotations; blocker (c) synthetic PHI fixture in isolated lakehouse remains M3-B scope | [M3-A](evidence/m3-a-rls-roles.md) |
| **Fabric F2 SIT paused at sprint close** (pending user action) | **✅ RESOLVED** — capacity Active on F4 (raised to F16 mid-sprint for M1-B, downscaled to F4 for cost). H6 evidence covers rationale + rollback | [M4-B](evidence/m4-b-hygiene.md) |

## 6. Follow-ups (Sprint 11 backlog)

| # | Item | Origin | Priority |
| - | ---- | ------ | -------- |
| **1** | **M3-B**: synthetic PHI fixture design + injection into isolated test lakehouse (NOT `lh_ihzhhpf_sit`) + per-role DAX rejection proof (needs spec first per kickoff design §8) | M3 carry (S10.7) | High — closes ADR-0016 gate 4 |
| **2** | **S10.9**: automated agent-eval harness extending `eval-goldens.yml` (needs spec first) | M3 carry | High — Sprint 09 DoD 6 dependency |
| **3** | **S10.10**: deploy 3 agent runtime hosts (BM-Copilot Foundry, Fabric Data Agent, CSA Foundry) to SIT | M3 carry | Medium — pairs with S10.9 |
| **4** | **T7 H5**: delete `evh-ihzhhpf-sit-y26y` + namespace + consumer groups + `id-sim-capacity-eh-sender-sit` MI role assignments after ADR-0019 D+30 observation (delete-ready date **2026-08-07**) | T7 carry | Low — USD 11/mo hold cost |
| **5** | **T7 H8**: derive per-event JSON schemas from `dc-*-v1.records[].items` sub-schemas + restore strict Gate 1 validation | M1.5 finding | Medium — silver hardening real fix |
| **6** | **Lifecycle-aware measure refinement**: `Currently In Hospital` should use `LASTNONBLANK(status) BY encounterId` (event-status is over-inclusive); `Currently Assigned Beds` needs `bed.released` simulator event | M2 finding | Medium — improves demo accuracy |
| **7** | **Heatmap RAG conditional formatting** on `Occupancy %` per design spec §6.1 (red > 90%, amber 75–90%, green < 75%) | M2 finding | Low — cosmetic |
| **8** | **`switzerlandnorth` region lift-and-shift** once Fabric IQ + Direct Lake reach Swiss GA (ADR-0013 expires **2026-09-30**) | Sprint 09 carry | High — hard deadline, ADR governance |
| **9** | **Teardown of frozen `MngEnvMCAP228255` tenant** (Sprint 00 follow-up) | Sprint 09 carry | Low — safety window |
| **10** | **Nightly HCC MAPE re-validation harness** ([`docs/OPERATIONS.md`](../../OPERATIONS.md) OPS-RISK-05) | Sprint 09 carry | Medium — regression detection |
| **11** | **`bed.state_changed` simulator event** — currently not emitted, so `bed_state` gold entity is empty. Blocks true `Occupancy %` semantics. | M1-B finding | Medium |
| **12** | **Orphan `Tables/gold/patient-flow/*` cleanup** — M1's failed first attempt left orphan Delta directories. Non-blocking but wastes storage | M1-B (M1-C correction) | Low — needs approved-to-apply |
| **13** | **Downstream measure refinement / more page-2 (OR) visuals** — Page 2 remains scaffold-only | Sprint 09 carry (D5.1–D5.2 partial) | Medium |

## 7. Risk register outcome

| Risk | Sprint 10 outcome | Status heading into Sprint 11 |
| ---- | ----------------- | ------------------------------ |
| **OPS-RISK-01** — Fabric IQ Ontology CH-GA + DPA equivalence | Monitoring only; no CH-GA news | **High** (unchanged) |
| **OPS-RISK-02** — Fabric preview features stability (Custom Endpoint, Direct Lake) | Both worked reliably across ~30 pipeline runs in-sprint; SQL endpoint metadata lag documented | **Medium** (was High) |
| **OPS-RISK-03** — Direct Lake preview stability | Framing refresh consistently worked; 0 reported queries returning stale data | **Medium** (was Medium) |
| **OPS-RISK-04** — Fabric capacity cost hygiene | ✅ CLOSED — F16→F4 executed with validation. F4 baseline confirmed as adequate for current workload | **Closed** |
| **OPS-RISK-05** — HCC MAPE regression | No re-validation harness yet — Sprint 11 backlog #10 | **Medium** (unchanged) |
| **OPS-RISK-06** — Sprint 09 style RLS silent drop | ✅ CLOSED — CI merge gate (M4-C) now blocks any measure/role count drift on PRs to semantic model | **Closed** |
| **NEW: MCAPS report ACL bootstrap defect** — Fabric API-created reports fail 405 in this tenant | Documented pattern (portal-scaffold + updateDefinition overlay) works reliably. **May recur in other Fabric report scenarios** | **Low** (documented mitigation exists) |
| **NEW: DAX role emulation via REST requires SP** — blocks scripted per-role verification | Documented; M3-B will use SP path or XMLA | **Low** |
| **NEW: SQL endpoint metadata cache lag** — 5-15 min after Delta commit | Manual refresh REST call works. Should be scripted or documented for future M-work | **Low** |

## 8. Charter mapping — final Sprint 10 outcome

| Charter ID | Track | Planned outcome | Actual outcome | Notes |
| ---------- | ----- | --------------- | -------------- | ----- |
| S10.1 Eventstream provisioning | T1 | Bicep + portal | **ADR-0019 pivot** to Custom Endpoint + Entra ID | Full success; Fabric-managed EH connection wasn't feasible in MCAPS |
| S10.2 Eventstream notebooks | T1 | Import + first-run | 3 notebooks live + all 3 exercised | Silver went through 3 defect cycles |
| S10.3 4 fact tables | T1 | 2 of 4 M1 + 2 M2 | **5 of 6** landed (`bed_state` deferred — simulator gap) | Better than plan |
| S10.4 8 Option D measures | T2 | 2 M1 + 6 M2 | **11 measures total** (5 pre-existing + 2 M1 + 4 M2) | Naming differs from Option D but functional coverage equivalent |
| S10.5 OR loader extension | T2 | Full M2 | Not touched in Sprint 10 | Not needed for demo; carried to Sprint 11 backlog if surfaced |
| S10.6 RLS re-authoring | T3 | Full M3 | **Partial (M3-A)** — roles + annotations shipped, per-role DAX rejection deferred | Sprint 09 blocker 1 resolved |
| S10.7 Synthetic PHI fixture | T3 | Full M3 | **Deferred to Sprint 11 (M3-B)** — needs spec first | Per kickoff design §8 |
| S10.8 PBIP visuals | T3 | 2 M1 + more M2 | 2 KPI cards (M1-D) + 3 slicers + heatmap (M2) = **6 visuals** | Page 2 (OR) still scaffold-only |
| S10.9 Agent eval harness | T3 | Full M3 | **Deferred to Sprint 11** — needs spec first | |
| S10.10 Agent runtime hosts | T3 | Full M3 | **Deferred to Sprint 11** | Requires infra + Foundry work |
| S10.11 Verifier extension | T4 | Full M4 | ✅ Shipped M4-A + wired to CI in M4-C | 11 measures + 4 roles asserted |
| S10.12 CI merge gate | T4 | Full M4 | ✅ Shipped M4-C (this PR) | Blocks drift on PRs to `capacity-dashboard.SemanticModel/**` |

## 9. Meta-observations (process)

- **Skill discovery rule** (introduced in AGENTS.md v1.14.0, [PR #135](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/135)) was validated live twice in Sprint 10: the `spark-operations` skill for M1.5 silver debug and the `powerbi-report-authoring` skill for M1-D/M2 visual authoring. Both installed with concrete trigger justification. Rule is working — no speculative installs.
- **`approved-to-apply` gate discipline** held across 6 destructive actions this sprint (2 report deletes, 2 branch deletes, 1 capacity change, 1 workflow file delete). Zero accidental destructive changes.
- **Session-persistent context** (via user memory + workspace state) let the sprint continue smoothly across multiple long turns — the "user requires explicit approval before delete" rule was surfaced automatically each time.
- **Portal-scaffold + updateDefinition overlay** as a Fabric-native pattern is a real innovation from this sprint — worth writing up as an ADR or cookbook entry for future sprints.

## 10. What to do differently

1. **Notebook edits via JSON script, not `edit_notebook_file`** for anything touching >1 cell. Loss cost in M1.5: ~30 min for cell-corruption recovery.
2. **Confirm Fabric SQL endpoint schema at Delta `_delta_log/*.json` level first** before assuming missing columns = upstream pipeline defect. Loss cost in M2: ~30 min investigating "missing" payload column that was actually a hidden STRUCT.
3. **Assume MCAPS tenant has ACL bootstrap issues on API-created items** — go portal-scaffold first for any new Fabric item type. Loss cost in M1-D: 2 delete-recreate cycles.
4. **When silver-style multi-gate validation notebook fails, always fetch Spark Advisor + driver stdout in the same call.** M1.5 defect 3 (schema mismatch) would have been visible on defect 1's stdout if I'd inspected it deeper.
5. **Document capacity-change validation runs immediately** — the F16→F4 downscale in M4-B was validated in the same session but should have a companion re-run on next-day cold-start to confirm F4 handles cold-cache queries.
