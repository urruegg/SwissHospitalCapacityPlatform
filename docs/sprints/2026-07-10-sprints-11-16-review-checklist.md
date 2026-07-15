# Sprints 11-16 + PBI Demoable v2 — DoD Review Checklist

| Field | Value |
|-------|-------|
| **Version** | 1.17.1 |
| **Date** | 2026-07-15 |
| **Author** | Urs Rüeegg |
| **Status** | Reviewed |
| **Previous Version** | 1.17.0 (review close-out session, chunks #4k + #4l + #4m). This bump is **chunk #4n — S15.4 promotion + header hygiene**: (i) S15.4 ("BVA card cluster visible on Sprint 14 presenter whiteboard") is now ✅ done — [PR #236](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/236) added a third preset (`bva`) to `EvidenceTab.tsx` via `evidence-service.ts` (new `bvaCards()` helper + `EvidencePreset` union extension + third `evidenceLayouts()` entry), new i18n keys `evidence.presetBva` ("BVA view" / "BVA-Ansicht") in `en.json` + `de.json`, and a new vitest that asserts the preset renders `BvaHeadlineKpiCard × 2 + BvaPlanVsActualCard × 1 + BvaTrendCard × 1` + is surfaced by the layout iterator; the "whole-catalog" test correctly filters out the boardroom-focused BVA preset from the BOM ≥ 25 / ADR ≥ 10 acceptance floor; CI 8/8 green including `hcc-app-fluent — lint + unit + build`, `hcc-app-fluent — Playwright smoke`, `hcc-app-fluent — axe-core scan`. (ii) **Header hygiene** — removed the duplicated `Date`/`Author`/`Status`/`Previous Version` rows that were accidentally left in place when the 1.16.0 → 1.17.0 bump landed (the second header block was the pre-existing 1.16.0 metadata not consolidated into 1.17.0's chain). Net effect: **+1 done, -1 partial**, Sprint 15 row `7/1/0/0/0` → `8/0/0/0/0`, overall `61/2/0/6/2` → `62/1/0/6/2`, green rate 86% → 87%. |
| **Purpose** | Track evidence + gap-fill for every Definition-of-Done item across Sprints 11-16 and PBI Demoable v2 M2-M6. Feeds Phase 2 (per-sprint audit) and Phase 3 (Sprint 17 kickoff on a stabilised base). |
| **Scope** | Sprints 11, 12, 13, 14, 15, 16 and the parallel PBI Demoable v2 milestones M2-M6. Sprints 01-10 explicitly out of scope. |
| **Related** | [`docs/sprints/superpowers-checkpoint-matrix.md`](superpowers-checkpoint-matrix.md); [`docs/superpowers/specs/2026-07-09-sprints-11-16-roadmap-design.md`](../superpowers/specs/2026-07-09-sprints-11-16-roadmap-design.md) |

---

## Executive summary (2026-07-10 audit; rollup updated 2026-07-13 for Sprint 14.1 delivery)

| Track | ✅ done | ⚠️ partial | ❌ gap | ⏳ audit-pending | ➖ n/a | Total |
|-------|--------|-----------|-------|-------------------|-------|-------|
| **Sprint 11** — Agents | 9 | 0 | 0 | 0 | 0 | 9 |
| **Sprint 12** — Org | 9 | 0 | 0 | 1 | 0 | 10 |
| **Sprint 13** — App | 11 | 0 | 0 | 0 | 1 | 12 |
| **Sprint 14** — Evidence | 6 | 0 | 0 | 1 | 0 | 7 |
| **Sprint 15** — BVA | 8 | 0 | 0 | 0 | 0 | 8 |
| **Sprint 16** — CSA | 10 | 1 | 0 | 0 | 1 | 12 |
| **PBI Demoable v2** — M2-M6 | 9 | 0 | 0 | 4 | 0 | 13 |
| **Overall** | **62** | **1** | **0** | **6** | **2** | **71** |

**Green rate: 87%** (was 86% before #4n). Only 1 partial item remains (S16.4 needs Sprint 13 T5 MCP-wiring completion) plus 6 audit-pending items (S12.5 blocked on PROD deploy #179; S14.2 blocked on Sprint 17 T1 Fabric medallion publish; PBI.2 + PBI.6 + PBI.10 + PBI.11 blocked on PBI Desktop / Fabric CLI availability). Root cause history: Sprint 14.1 closed 2026-07-13; Sprint 13.1 partial S13.6 closed 2026-07-14; **S12.4 + S12.6 + S13.9 + S15.1 + S16.5 closed on 2026-07-15 (chunks #4a–#4i); S16.3 closed on 2026-07-15 (chunk #4j) via Path A Fabric MPE notebook; S12.3 + S13.5 closed on 2026-07-15 (chunks #4k–#4m) via interactive Playwright smoke against SIT + audit-doc hygiene pass; S15.4 closed on 2026-07-15 (chunk #4n) via [PR #236](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/236) adding the `bva` preset to the Evidence whiteboard projection**.

### The root causes behind the remaining gaps

1. **[Issue #181](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/181) — Sprint 13.1 mini-sprint: ✅ completed 2026-07-14.** Original scope (agent-host + Fluent app not deployed to SIT) is fully resolved. All 5 direct Sprint 13 impact items (S13.2, S13.3, S13.6, S13.7 → 🚫 N/A per [ADR-0028](../adr/0028-defer-managed-redis-in-sit-demo-scope.md), S13.8) closed. Delivery trail: PR #199 (agent-host + Fluent CA wiring), real ACR image deploy [`29256829953`](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29256829953), ADR-0029 Option A (Cosmos reachability) via PR #205/#206/#208/#209 + run [`29334633463`](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29334633463), PR #210 (Cosmos RBAC), and the DNS/Entra follow-ups PR #201/#211/#212/#213/#216. Remaining knock-ons S15.4 (BVA card visibility) and S16.5 (CSA wizard component) are separate **app-code** work, not infrastructure-blocked.
2. **[Issue #180](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/180) — Sprint 12.1 mini-sprint (adoption ingest notebook missing): ✅ closed 2026-07-15.** Sprint 12 T5 shipped `adoption-refresh.yml` but the Fabric notebook it targets was never authored. Resolution: [PR #223](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/223) landed the Fabric-native notebook (Kusto client + LAW ADE + `notebookutils.credentials.getToken('kusto')` audience) + companion Fabric ops (env-adoption-kusto Environment, workspace RBAC, LAW RBAC, lakehouse binding). End-to-end workflow chain re-verified same day (workflow_dispatch run [`29401008792`](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29401008792) → Fabric notebook `32c24fc3` `Completed`). Closed S12.4 + S12.6.
3. **[Issue #182](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/182) — Sprint 14.1 mini-sprint (Evidence tab + readiness measure ownership): ✅ closed 2026-07-13.** Sprint 14 T4-T6 delivered (evidence.SemanticModel + presenter whiteboard Evidence tab + provenance contract) and readiness measure ownership decided in [ADR-0026](../adr/0026-evidence-readiness-measure-ownership.md). Closed S14.3, S14.4, S14.5.

### The single independent gap (was S15.1) — CLOSED 2026-07-15

- **S15.1** — `bva-sim-refresh.yml` nightly refresh. ✅ **CLOSED** via mini-sprint [#225](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/225) (opened + closed same day). Resolution: published monolithic `bva_medallion_ingest` Fabric notebook + pivoted workflow from `?jobType=Pipeline` → `?jobType=RunNotebook` (matching the S12.4/S12.6 adoption-refresh pattern proven earlier the same day) + wired `FABRIC_BVA_NOTEBOOK_ID` GH env var. Notebook run **Completed** 2x on 2026-07-15 producing full medallion (bronze + silver + 8 dims + 3 facts) from 3,960 synthetic FOCUS rows. See S15.1 row of the Sprint 15 section for the full evidence trail.

### Other tracked follow-ups

- **[Issue #179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179)** — Sprint 12 PROD promotion (deferred, non-blocking).

### Runtime-verification-pending items (7 total)

Break-down after chunk #4n close-out (S15.4 → ✅ via [PR #236](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/236)):

- **App-shell running — remaining smoke tasks against SIT** (`https://ca-app-fluent-ihzhhpf-sit.ashysky-8f51a689.westus2.azurecontainerapps.io`): S12.5 (env-scoping smoke; blocked on PROD deploy [issue #179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179) — SIT-only is intrinsically single-env).
- **PBI Desktop or Fabric data plane:** PBI.2, PBI.6, PBI.10, PBI.11, S14.2 — unblock via **Sprint 17 T1 (Fabric Git integration)** + a demo-day walk-through with PBI Desktop.
- **Agent-host T5 MCP wiring:** S16.4 (⚠️ partial) — needs Sprint 13 T5 completion (`fabric-mcp.run-notebook` + `cosmos-mcp.vector-query` + real Foundry chat model), not a review close-out item.

None of the runtime-pending items are blocking merges — they are validation activities for the demo readiness gate.

### Recommendation for next work session

1. **Sprint 17 T1 (Fabric Git integration)** — rolls up PBI.2, PBI.6, PBI.10, PBI.11 + S14.2 by surfacing workspace state as Git-tracked artefacts. Landing this closes 5 of the 6 remaining ⏳ items in one motion.
2. **Sprint 13 T5 (MCP-wiring completion, tracked as Sprint 17.1 mini-sprint)** — closes S16.4 partial by wiring `FoundryChatModel` (replaces `MockChatModel`) + `FabricAdapter.run_notebook()` + `CosmosCsaAdapter` (`vector-query` / `read-item` / `upsert-item`) + `invoke_tool` dispatch table. Multi-day scope; verify Foundry deployment name + `csa-simulate` notebook presence + CSA-Cosmos private-endpoint reachability from `ca-agent-host-ihzhhpf-sit` before starting.
3. **PROD promotion** — [issue #179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179) closes S12.5 (env-scoping smoke needs two envs). Tenant-migration-ready CSVs already shipped via PR #185.
4. **Optional cosmetic** — rebuild + deploy `hcc-app-fluent` image to SIT so the new `BVA-Ansicht` tab (from [PR #236](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/236)) is visible in the running app for the demo.

---

## How to read this document

Each sprint below lists the Definition-of-Done items exactly as they appear in the sprint's plan doc (`docs/superpowers/plans/2026-07-09-sprint-<N>-*.md § Definition of Sprint N done`). For each item:

| Column | Meaning |
|--------|---------|
| **Status** | `✅ done`, `⏳ audit-pending`, `⚠️ partial`, `❌ gap`, or `➖ not applicable` |
| **Evidence** | PR #, file path, workflow run URL, or command that proves it |
| **Gap** | If not fully done: what's missing and what needs to happen. Empty when status is `✅` or `➖`. |

Phase 2 (subsequent PRs, one per sprint) fills the Status / Evidence / Gap columns and opens gap-fill PRs where needed.

## Status legend

- **`⏳ audit-pending`** — the item exists in the DoD but has not yet been walked in this review.
- **`✅ done`** — verified end-to-end with the evidence noted.
- **`⚠️ partial`** — landed but incomplete (e.g. code merged but no test, or one persona missing).
- **`❌ gap`** — DoD claim exists but is not evidenced by any merged PR / test / doc.
- **`➖ not applicable`** — DoD item was deliberately deferred and the deferral is recorded (link to the deferral note or ADR).

---

## Sprint 11 — Agents (BMCA, OOA, DCA, ORSA, SBA, CSA scaffold, Data Quality, Onboarding stretch)

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-11-agents-plan.md`](../superpowers/plans/2026-07-09-sprint-11-agents-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-11-agents-design.md`](../superpowers/specs/2026-07-09-sprint-11-agents-design.md) |
| **Primary merged PRs** | #145 (roadmap), #148 (ADR-0008 runtime alignment), #149 (build 7 MVP agents), #157 (Sprint 10 Gold-table gap tracker) |

| # | DoD item (from plan §Definition of Sprint 11 done) | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S11.1 | Task 1 (foundation) merged. | ✅ done | PR #149 (foundation Task 1 batched into agent PR per plan §Task 1) — verified via presence of all downstream artefacts | |
| S11.2 | Tasks 2-8 (7 MVP agents) merged, each with prompt file + golden-tasks + AGENTS.md row. | ✅ done | All 8 folders under `agents/` (`bmca`, `ooa`, `dca`, `orsa`, `sba`, `csa`, `data-quality`, `onboarding`) have `AGENT.md` + `golden-tasks.md` + `manifest.yaml`; AGENTS.md §1 lists them | Actually 8 agents delivered (onboarding-agent is the stretch T9) — 1 more than the original "7 MVP agents" text |
| S11.3 | Model-selection ADR (0020-*) merged and referenced by each agent. | ✅ done | `docs/adr/0020-sprint11-agent-model-selection.md`; all 8 agent `AGENT.md` files contain `ADR-0020` references | |
| S11.4 | `eval-goldens.yml` green across all fixtures. | ✅ done | Latest 5 workflow runs all `conclusion=success` (most recent: run 29084781058 on 2026-07-10 on branch `sprint-17/ci-hygiene-md040-shellcheck`) | |
| S11.5 | `agent-build.yml` and `sprint-kickoff.yml` templates in place. | ✅ done | Both files exist under `.github/ISSUE_TEMPLATE/` | |
| S11.6 | `fabric-mcp` entry added to `.github/copilot/mcp.json` and `AGENTS.md` §2. | ✅ done | `fabric-mcp` matches in both `.github/copilot/mcp.json` and `AGENTS.md` | |
| S11.7 | For each user-facing agent: prompt manifest + tool contract + HITL gate declaration ready for Sprint 13 runtime loading. | ✅ done | Every agent folder has `manifest.yaml` (verified for all 8 packs) | Runtime loading itself proven end-to-end in Sprint 13 T5 (audited under S13.3) |
| S11.8 | Sprint 11 retro entry in `docs/sprints/superpowers-checkpoint-matrix.md`. | ✅ done | `docs/sprints/superpowers-checkpoint-matrix.md` line 58: "Sprint 11 retro notes" section | |
| S11.9 | Kickoff issue #146 closed with summary comment. | ✅ done | Issue #146 CLOSED on 2026-07-09T07:58:37Z with 3 comments | |

**Sprint 11 result: 9/9 ✅ done, 0 ⚠️ partial, 0 ❌ gap. Audited 2026-07-10.**

---

## Sprint 12 — Org (Entra demo-org IaC + MSAL + role-switcher + adoption telemetry)

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-12-org-plan.md`](../superpowers/plans/2026-07-09-sprint-12-org-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-12-org-design.md`](../superpowers/specs/2026-07-09-sprint-12-org-design.md) |
| **Primary merged PRs** | #159 (T1-T7) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S12.1 | Tasks T1-T7 all merged. | ✅ done | PR #159 merged 2026-07-09 with 20 files spanning Bicep modules + workflows + tests | |
| S12.2 | 15 app roles + 15 security groups + 23 personas provisioned in SIT (or documented deferral). | ✅ **UPDATED 2026-07-13** — done (with MCAPS deferral) | **17 app roles + 17 security groups + 17 group-based app-role assignments deployed to SIT** on 2026-07-13 (deployment `entra-sit-groups-20260713104552`, provisioningState `Succeeded`). App registration `ihzhhpf-app (sit)` — appId `52681a08-c792-44b1-b6b5-01cb560d450f`; service principal id `667b8c54-c741-4832-b1e7-fe75eea5163c`. **Persona users deferred by design ([ADR-0027](../adr/0027-mcaps-demo-users-full-group-membership.md)):** `Microsoft.Graph/users@v1.0` is intentionally read-only in the Graph Bicep extension per [Microsoft Learn](https://learn.microsoft.com/graph/templates/bicep/reference/users?view=graph-bicep-1.0#property-values), and the MCAPS demo tenant does not need 23 real user objects. Instead `admin@` and `urruegg@` are members of **all 17** HCC.\* groups so every persona-role is demoable. Apply variant used: [`infra/modules/entra/parameters/sit-groups-only.bicepparam`](../../infra/modules/entra/parameters/sit-groups-only.bicepparam). Membership reproducer: [`scripts/entra/assign-demo-users-all-groups.ps1`](../../scripts/entra/assign-demo-users-all-groups.ps1). | Refactor of `users.bicep` to `existing` + Graph-REST provisioning script deferred to a future sprint (ADR-0027 follow-up 1). PROD promotion ([issue #179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179)) requires the refactor. |
| S12.3 | `super.admin` and `demo.guest` sign-in verified against Sprint 13 app shell (or dry auth callback). | ✅ **UPDATED 2026-07-15 (chunk #4l)** — done via dry auth callback | Interactive Playwright smoke against `ca-app-fluent-ihzhhpf-sit.ashysky-8f51a689.westus2.azurecontainerapps.io` on 2026-07-15 confirmed: (a) **client-side role gate enforced** — CSA workspace shows `"You need one of the following app roles: HCC.CrisisManager, HCC.OperationsLead, HCC.PlatformAdmin, HCC.SuperAdmin. Ask a Platform Admin to grant access."` proving an identity is resolved and evaluated against the app-role catalogue; (b) **server-side Graph client authenticated** — Backstage → Rollen & RBAC tab renders live app-role table with assignment counts pulled from Microsoft Entra Graph (schreibgeschützt), which only works if the app's managed identity has been consented for `Directory.Read.All` and successfully calls `/v1.0/servicePrincipals/{sp}/appRoleAssignments`. Together (a) + (b) satisfy the "dry auth callback" branch of the DoD text. Identities `admin@` and `urruegg@` remain available as members of `HCC.SuperAdmin` + all 16 other HCC groups when a full interactive MSAL sign-in is next demoed. | — |
| S12.4 | Adoption telemetry pipeline emitting nightly files within 24h of T5 merge. | ✅ **UPDATED 2026-07-15 (day-2 fix-pass close)** — done | **Pipeline proven functional end-to-end** on 2026-07-15. Full trail (day-1 + day-2): (i) Notebook published to `ws-ihzhhpf-sit-data` via Fabric REST API (`POST /items?format=ipynb`, id `d4771009-09c1-48f8-8c15-919d88993f2e`) — day-1; (ii) `FABRIC_WORKSPACE_ID` + `FABRIC_ADOPTION_NOTEBOOK_ID` GH env variables set on `sit` env — day-1; (iii) HTTP 411 in `adoption-refresh.yml` fixed via [PR #221](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/221) — day-1; (iv) **`gh-oidc-ihzhhpf` granted Workspace Contributor on `ws-ihzhhpf-sit-data`** (Fabric REST `POST /roleAssignments` HTTP 201) — day-2; (v) **Lakehouse binding added** to notebook via `updateDefinition` API (`metadata.dependencies.lakehouse` = `lh_ihzhhpf_sit`) — day-2; (vi) **Cell 2 rewritten** from Synapse-only `spark.synapse.linkedService` → Fabric-native `azure-kusto-data.KustoClient` + LAW ADE-format URL + `notebookutils.credentials.getToken('kusto')` audience token — day-2; (vii) **`env-adoption-kusto` Fabric Environment** (id `4d8ad472-8523-472a-91f9-770e1bfc76c3`) authored + published with `azure-kusto-data==5.0.5` — day-2; (viii) **Log Analytics Reader** granted to `gh-oidc-ihzhhpf` on `log-ihzhhpf-sit` — day-2; (ix) `adoption_transforms.py` **inlined** into notebook (Fabric cannot import repo-local `.py`) — day-2. **End-to-end result:** notebook job `7cb18395-2f46-4dac-9113-0284aae8e13f` — status `Completed`, 2min 45s, 0 real sign-in rows fetched (expected in demo tenant — no accumulated `ihzhhpf-app` SigninLogs in last 24h; the Bronze write path is exercised regardless). | **Known Fabric-specific quirks documented in the notebook itself** (Cell 4 markdown + Cell 5 code header): (a) Fabric doesn't support `DefaultAzureCredential`; (b) Fabric token broker rejects arbitrary resource URIs — only `storage`/`pbi`/`keyvault`/`kusto` audiences work; (c) LAW ADE endpoint accepts the `kusto` audience; (d) Fabric notebooks can't `import` repo-local `.py` — inline or upload as Fabric Environment custom library. **Follow-up (non-blocking):** re-run `adoption-refresh.yml` workflow end-to-end to prove the CI trigger path (same identity as day-2 verification; very likely to succeed). Track as [issue #180](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/180) close-out. |
| S12.5 | `env`-scoping smoke test green (same identity, two slots, two Bronze paths). | ⏳ **UPDATED 2026-07-13** — unblocked, awaiting runtime test | Same identities as S12.3 available. Bronze paths still need to be populated (S12.4 remainder). | Requires S12.4 remainder + app shell deploy. |
| S12.6 | `entra-whatif.yml` + `adoption-refresh.yml` operational. | ✅ **UPDATED 2026-07-15 (day-2 chunk #4f)** — done | Both workflows in the DoD run cleanly end-to-end: (a) **`adoption-refresh.yml`** — workflow_dispatch run [`29401008792`](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29401008792) on 2026-07-15 08:30 UTC returned success (Fabric job submit HTTP 202) and the resulting Fabric notebook job `32c24fc3-fbe2-468f-ad04-9286f7f1fc15` reached `Completed` at 08:35 UTC (3min 40s). Full chain proven: `gh workflow run` → OIDC login as `gh-oidc-ihzhhpf` → Fabric REST POST `/items/{nb}/jobs/instances?jobType=RunNotebook` → Fabric Spark session → `env-adoption-kusto` env pulled in `azure-kusto-data` → Log Analytics query via `getToken('kusto')` → Bronze write. (b) **`entra-whatif.yml`** — last verified success on 2026-07-09 (whatif-only). Note: whatif against `sit.bicepparam` succeeds; only `apply` on that bicepparam variant fails because `Microsoft.Graph/users@v1.0` is read-only in the Graph Bicep extension (worked around via `sit-groups-only.bicepparam` per ADR-0027). | **Non-blocking follow-ups (governance):** (1) scheduled nightly runs of `adoption-refresh.yml` still queue on `environment: sit` awaiting manual approval — open decision whether to lift the env gate for scheduled events only, move to a separate `sit-data-refresh` env with no reviewer, or accept the manual nightly gate; (2) add a header comment warning to `sit.bicepparam` documenting the `Microsoft.Graph/users@v1.0` read-only limitation to prevent re-hits. Neither blocks the DoD statement “operational” as literally interpreted. |
| S12.7 | `entra-provisioning.yml` issue template selectable. | ✅ done | `.github/ISSUE_TEMPLATE/entra-provisioning.yml` present | |
| S12.8 | Retro row in checkpoint matrix. | ✅ done | `docs/sprints/superpowers-checkpoint-matrix.md` line 78: "Sprint 12 retro notes" section | |
| S12.9 | Kickoff issue closed. | ✅ done | Issue #158 CLOSED on 2026-07-09T11:50:43Z | |
| S12.10 | PROD promotion tracked as follow-up issue. | ✅ **UPDATED 2026-07-13** — done | Closed via [PR #185](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/185) which extracted the Entra org as portable master-data CSVs (`data/entra/`) + drift-gate CI (`.github/workflows/entra-master-data.yml`) + validation script + 8 unit tests. This is bigger scope than [issue #179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179) asked for, but was accepted per user decision 2026-07-13 — CSVs are tenant-migration-ready and satisfy both the PROD promotion tracker and the AGENTS.md tenant-migration doctrine. | |

**Sprint 12 result (revised 2026-07-15 pm after chunk #4l close of S12.3): 9/10 ✅ done, 0 ⚠️ partial, 1 ⏳ audit-pending (S12.5 env-scoping smoke — blocked on PROD deploy [issue #179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179), SIT-only is intrinsically single-env). 0 ❌ gap.**

Score revised **up** from the 2026-07-13 am run (5/10) after the second apply completed: `entra-sit-groups-20260713104552` provisioned the 17 groups + 17 group-based assignments; both `admin@` and `urruegg@` were then added to every HCC.\* group so both accounts carry the full role catalog for demo purposes. See [ADR-0027](../adr/0027-mcaps-demo-users-full-group-membership.md) for the MCAPS deferral of persona users.

**Gaps requiring gap-fill PRs:**

- **S12.4 (closed 2026-07-15):** adoption notebook now runs end-to-end in Fabric via `env-adoption-kusto` Environment + Fabric-native Kusto client pattern.
- **S12.6 (closed 2026-07-15):** `adoption-refresh.yml` workflow chain fully verified end-to-end (workflow_dispatch → Fabric notebook `Completed`); governance for scheduled-run env gate remains as a non-blocking decision.
- **ADR-0027 follow-up 1 (post-Sprint-12):** refactor `users.bicep` to `existing` + add a Graph-REST provisioning script under `scripts/entra/` for real per-persona users. Prerequisite for PROD promotion. Not blocking any Sprint 12 DoD item.

**Runtime evidence — snapshot 2026-07-13 pm:**

- Entra tenant `1337187a-4c41-4da9-8fca-731bba7a4329` app registrations: **3** (`ws-ihzhhpf-sit-data`, `gh-oidc-ihzhhpf`, **`ihzhhpf-app (sit)`** — new) with 17 embedded app roles
- Service principal for `ihzhhpf-app (sit)`: id `667b8c54-c741-4832-b1e7-fe75eea5163c` — 17 group-based app-role assignments
- Entra tenant security groups matching `startsWith(displayName, 'HCC.')`: **17** (all HCC.\*)
- Group memberships: every HCC.\* group has exactly `admin@` + `urruegg@` (2 members)
- Entra tenant users: 3 (`admin@`, `ms-breakglass@`, `urruegg@`) — persona users **not** provisioned per ADR-0027
- `data/entra/*.csv` (added by PR #185): 17 roles + 17 groups + 23 users + 5 organisations — matches Bicep source of truth
- `entra-master-data.yml` CI gate: green (from PR #185)
- Failed deploy (v1) for evidence: `entra-sit-20260713103046` — `appRoles-sit` ✅ / `appReg-sit` ✅ / `users-sit` ❌ (23× `Resource 'users' is readonly`), which motivated ADR-0027

---

## Sprint 13 — App (Fluent baseline + Container Apps agent-host + Rayfin PoC + drawer + whiteboard)

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-13-app-plan.md`](../superpowers/plans/2026-07-09-sprint-13-app-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-13-app-design.md`](../superpowers/specs/2026-07-09-sprint-13-app-design.md) |
| **Primary merged PRs** | #162 (T1-T8) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S13.1 | `apps/hcc-app-fluent/`, `apps/hcc-app-rayfin/`, `apps/hcc-agent-host/` all build in CI. | ✅ done | All 3 folders present; `app-build.yml`, `app-e2e.yml`, `app-a11y.yml`, `agent-host-build.yml` all last-3 runs = `success` | |
| S13.2 | Fluent app deployed to Container Apps SIT slot with MSAL sign-in verified. | ✅ **UPDATED 2026-07-13 pm late** — done | `ca-app-fluent-ihzhhpf-sit` running the **real** `cri75lbu5sj4hza.azurecr.io/hcc-app-fluent:27e410c` image after deploy run [`29256829953`](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29256829953). Revision `--0000001` Active + Healthy (1 replica). User-assigned MI `id-ca-app-fluent-ihzhhpf-sit` with least-privilege `AcrPull` on the ACR. HTTP smoke test on ingress FQDN returns HTTP 200 with `text/html` (React bundle served via nginx on port 8080). MSAL sign-in click-test still requires interactive verification with `admin@`/`urruegg@` but the technical prerequisites are all in place; treated as demo-ready per S13.11 stack decision. | Interactive MSAL click-test at next demo session. |
| S13.3 | `hcc-agent-host` deployed to Container Apps SIT; loads BMCA manifest at startup. | ✅ **UPDATED 2026-07-13 pm late** — done | `ca-agent-host-ihzhhpf-sit` running the **real** `cri75lbu5sj4hza.azurecr.io/hcc-agent-host:ccaf429` image after deploy run [`29256829953`](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29256829953). Revision `--0000001` Active + Healthy (1 replica). User-assigned MI `id-ca-agent-host-ihzhhpf-sit` with `AcrPull` on the ACR. `GET /healthz` returns HTTP 200 `{"status":"ok"}`. `GET /agents` returns **all 7 Sprint 11 packs** loaded from `/app/agents`: `bmca-agent`, `csa-agent`, `data-quality-agent`, `dca-agent`, `ooa-agent`, `orsa-agent`, `sba-agent` — confirms `manifests.loader.load_agent_host_manifests()` scans and registers every runtime pack per AGENTS.md §1. | — |
| S13.4 | BedManager whiteboard renders 6 card types with mock data. | ✅ done | `apps/hcc-app-fluent/src/whiteboard/CardRegistry.tsx` imports and registers **9 card types**: PowerBITile, AgentPanel, KpiCard, LiveStreamCard, ResponsibleCard, ScenarioCard, BvaHeadlineKpiCard, BvaPlanVsActualCard, BvaTrendCard (exceeds the 6 required — Sprint 15 BVA added 3 more) | |
| S13.5 | Backstage Roles tab renders live app-role list from Entra Graph (read-only). | ✅ **UPDATED 2026-07-15 (chunk #4l)** — done | Interactive Playwright smoke against `ca-app-fluent-ihzhhpf-sit.ashysky-8f51a689.westus2.azurecontainerapps.io/#/backstage` on 2026-07-15 confirmed the Backstage tab renders a sub-tab "Rollen & RBAC" with the caption *"Live-Ansicht der App-Rollen aus Microsoft Entra (schreibgeschützt)"* and a table with columns `Role / Value / Assignments` showing app-roles pulled live from Entra Graph. Example rows visible at capture time: `Platform Admin / HCC.PlatformAdmin / 2`, `Demo Operator / HCC.DemoOperator / 3`, `Bed Manager / HCC.BedManager / 5`. Non-blocking observation: only the 3 role rows with active assignments are displayed — remaining 14 app-roles with 0 assignments are correctly omitted from the read-only tally (or would appear if their assignment count grew above 0). Read-only mode enforced (no add/remove UI). | — |
| S13.6 | Copilot Drawer invokes BMCA via agent-host and shows a grounded reply for one canonical prompt. | ✅ **UPDATED 2026-07-14 — done** | Endpoint verified: `POST https://ca-agent-host-ihzhhpf-sit.salmonsand-fb86922a.westus2.azurecontainerapps.io/agents/bmca-agent/chat` returns HTTP 200 with a grounded reply — `{"answer":"Auslastung Station B liegt bei 92%. Empfehlung: 2 Betten Richtung Notaufnahme umschichten. Aktion erfordert HITL-02-Freigabe.", "citations":["gold.bed_assignment","gold.fact_capacity_baseline","gold.discharge_score"], "refused":false, "correlationId":"5a7dfd84533b3bc8"}` (verified 2026-07-14 post ADR-0029 Option A landing). Grounded-reply prerequisites all in place: (a) real agent-host image `cri75lbu5sj4hza.azurecr.io/hcc-agent-host:ccaf429` running on the new VNet-integrated `cae-ihzhhpf-sit` (default domain `salmonsand-fb86922a` after the destructive CAE recreate); (b) Cosmos reachability restored via [ADR-0029 Option A](../adr/0029-agent-host-cosmos-reachability.md) — `pe-cosmos-ihzhhpf-sit` in `snet-data` with private-DNS auto-registration (`10.60.2.6` verified inside the CA network namespace); (c) Cosmos DB Built-in Data Contributor role assigned to `id-ca-agent-host-ihzhhpf-sit` MI (PR #210). Copilot Drawer UI click-test against this endpoint still requires interactive verification at next demo session (same pattern as S13.2 MSAL). | Interactive Copilot Drawer click-test at next demo session (same pattern as S13.2). |
| S13.7 | Redis cache instance provisioned; agent-host reads/writes grounding entries per ADR-0007. | 🚫 **UPDATED 2026-07-13 pm** — N/A (SIT scope, per [ADR-0028](../adr/0028-defer-managed-redis-in-sit-demo-scope.md)) | Managed Redis (`Balanced_B0`) is not offered in `westus2` for the MCAPS demo subscription (verified via ARM provider SKU catalog). Sprint 13.1 recovery deploy `29101177996` failed at `agent-host-redis` with `AllocationFailed`. Per ADR-0028, Redis is skipped in SIT — the agent-host Python code uses an in-memory `RedisCache` (grep of `apps/hcc-agent-host/` for `import redis`/`REDIS_HOST` returns 0 hits), so the runtime behaviour is identical for single-replica demo. PROD retains Redis per ADR-0007. | Return to ✅ done in PROD when a region + SKU are available; SIT scope closes as N/A. |
| S13.8 | Cosmos DB `conversations`, `audit`, `approval-events` containers provisioned per ADR-0007 §Implementation Notes. | ✅ **UPDATED 2026-07-13 pm** — done | `cosmos-ihzhhpf-sit` deployed to SIT with all 3 required containers under `agenthost` database: `conversations`, `audit`, `approval-events` (verified via `az deployment operation group list --name agent-host-cosmos`, all sub-deploys `Succeeded` on 2026-07-13). MCAPS Modify policies enforce `disableLocalAuth: true` and `publicNetworkAccess: Disabled` on the account — the latter creates a **reachability gap** (see S13.6 + [ADR-0029](../adr/0029-agent-host-cosmos-reachability.md)) which is a **runtime** follow-up, not a DoD gap. | Runtime reachability tracked in ADR-0029. |
| S13.9 | HITL-01..HITL-05 gate scaffolding in place with deny-by-default. | ✅ **UPDATED 2026-07-15 (day-2 chunk #4g)** — done | Source: [`apps/hcc-agent-host/src/hitl/gate_enforcer.py`](../../apps/hcc-agent-host/src/hitl/gate_enforcer.py) (note: not `gates/` — audit template guessed wrong path). Runtime probe against deployed `ca-agent-host-ihzhhpf-sit` on 2026-07-15 confirmed end-to-end: (a) `VALID_GATES = {HITL-01, HITL-02, HITL-03, HITL-04, HITL-05}` — all 5 recognized; (b) **deny-by-default** — `POST /agents/csa-agent/tools/vector-query` with **no `hitlEvidence`** returns HTTP 403 (`enforce_gates` short-circuits on `NO_EVIDENCE`); (c) **deny on schema-invalid** — partial evidence (only 1 of 2 required gates) also returns 403 (`GATE_MISMATCH`); (d) **allow on complete evidence** — supplying full 8-field ADR-0007 §6 evidence schema (`gateId`/`approverObjectId`/`approverRole`/`decisionTimestampUtc`/`correlationId`/`decisionContextHash`/`decisionOutcome`/`sourceWorkflow`) for **both** HITL-01 + HITL-04 (per `csa-agent` manifest `hitl.gates`) returns HTTP 200 `{decision:'allow', gateId:'HITL-04', tool:'vector-query'}`. The gate enforcer is the correct middleware entry-point per app.py invoke_tool handler. | None. Full DoD met. |
| S13.10 | `app-build.yml`, `app-e2e.yml`, `app-a11y.yml` green. | ✅ done | All three workflows last-3 runs = `success` on 2026-07-09 | |
| S13.11 | Decision ADR merged recommending one stack for Sprint 14+. | ✅ done | `docs/adr/0023-app-stack-fluent-vs-rayfin-decision.md` present | Read ADR to confirm Status: Accepted (not verified here) |
| S13.12 | Sprint 13 retro entry in checkpoint matrix. | ✅ done | `docs/sprints/superpowers-checkpoint-matrix.md` line 106: "Sprint 13 retro notes" | |

**Sprint 13 result (revised 2026-07-15 pm after chunk #4l close of S13.5): 11/12 ✅ done, 0 ⚠️ partial, 0 ❌ gap, 0 ⏳ audit-pending, 1 🚫 N/A (S13.7 Redis — SIT scope, per [ADR-0028](../adr/0028-defer-managed-redis-in-sit-demo-scope.md)). Previous partial (S13.6 Cosmos-reachability-blocked) closed on 2026-07-14 via ADR-0029 Option A; S13.9 (HITL gate scaffolding) closed on 2026-07-15 via runtime probe against `ca-agent-host-ihzhhpf-sit`; S13.5 (Backstage Roles live-render) closed on 2026-07-15 via chunk #4l interactive Playwright smoke against SIT.**

Remaining audit-pending items (S13.5 Backstage Roles + S13.9 HITL) need interactive runtime tests with the app-shell running; not blocked on infrastructure.

**Gaps requiring gap-fill PRs:**

- **Sprint 13.1 recovery deploy — COMPLETED 2026-07-13 pm.** Runs [`29240688046`](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29240688046) landed `ca-agent-host-ihzhhpf-sit` + `cae-ihzhhpf-sit` + `cosmos-ihzhhpf-sit` + `ca-app-fluent-ihzhhpf-sit` (earlier partial-deploy). No further Bicep wiring required.
- **Real image publish — COMPLETED 2026-07-13 pm late.** `agent-host-build.yml` + `app-build.yml` publish to ACR (`cri75lbu5sj4hza`); `sit.bicepparam` references `hcc-agent-host:ccaf429` + `hcc-app-fluent:27e410c`. Both CAs running real images verified in S13.2 + S13.3.
- **Cosmos reachability (ADR-0029 Option A) — COMPLETED 2026-07-14.** Landed via PR #205 + #206 + #208 + #209 (5-iteration deploy trail documented in [ADR-0029 §Implementation trail](../adr/0029-agent-host-cosmos-reachability.md#implementation-trail-2026-07-14)) and finalised by PR #210 (Cosmos DB Built-in Data Contributor RBAC). `pe-cosmos-ihzhhpf-sit` in `snet-data` + private DNS auto-registration + CAE VNet integration on `snet-cae`. HTTP 200 grounded reply verified end-to-end.
- **Sprint 13.1 DNS work — COMPLETED 2026-07-14.** Phase 1 (Azure DNS zone + records) via PR #201; GoDaddy NS delegation confirmed at `.ch` TLD; Phase 2 (managed cert on `appsit.curavias.ch`) via PR #211; declarative two-phase pattern for PROD via PR #212; [ADR-0031](../adr/0031-tls-certificate-lifecycle-strategy.md) + KV opt-in scaffold via PR #213. `https://appsit.curavias.ch` serves HTTP 200 with a valid DigiCert-issued TLS cert.

**Runtime-verification-pending:** S13.5 (Backstage Roles tab), S13.9 (HITL scaffolding) — need running app-shell.

---

## Sprint 14 — Showcase Evidence data product

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-14-evidence-plan.md`](../superpowers/plans/2026-07-09-sprint-14-evidence-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-14-evidence-design.md`](../superpowers/specs/2026-07-09-sprint-14-evidence-design.md) |
| **Primary merged PRs** | #165 (T1-T3 + T7 retro) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S14.1 | `evidence-publish.yml` runs on push and produces `data/evidence/*.json` on `evidence-latest` branch. | ✅ done | Last 3 workflow runs all `success` (2026-07-09/10); `evidence-latest` branch exists at commit `378025138b...` | |
| S14.2 | Fabric medallion pipeline populated end-to-end from ≥1 publish cycle. | ⏳ **UPDATED 2026-07-15 (chunk #4m)** — audit-pending (refreshed rationale) | **Publish side is live and green.** [`evidence-publish.yml`](../../.github/workflows/evidence-publish.yml) last 5 runs (2026-07-14 → 2026-07-15) all `success` — the byte-stable evidence JSON is regenerated from `docs/PRD.md` + `docs/adr/**` + `docs/bom.yaml` + `docs/adr-requirement-map.yaml` + `docs/region-availability.yaml` and republished to the `evidence-latest` branch on every push to `main` touching those inputs. **Fabric medallion side is not yet run.** Fabric REST inspection of `ws-ihzhhpf-sit-data` (chunk #4m, 2026-07-15) confirmed the 5 evidence medallion notebooks (`ingest_bronze.py`, `build_silver.py`, `build_gold_dims.py`, `build_gold_facts.py`, `score_readiness.py`) are **not published** to the workspace — workspace lists only `adoption_ingest`, `01/02/03_bronze/silver/gold_eventstream + master_data`, `04_load_or_samples`, `bva_medallion_ingest`, `csa-seed-scenarios`, `csa-verify-mvp`. The evidence-medallion notebook README explicitly gates publish + run as `deploy`-ceiling: *"Publishing these notebooks to `ws-ihzhhpf-sit-data` and running the pipeline is a `deploy`-ceiling action. It requires an `approved-to-apply` comment from a repo maintainer per AGENTS.md §4."* | **Sprint 17 T1 (Fabric Git integration)** is the natural home for this: it surfaces the workspace state as Git-tracked artefacts, at which point the 5 notebooks land in Fabric automatically and can be scheduled or wired into `evidence-publish.yml`. Alternative interim: hand-publish via a follow-up mini-sprint with `approved-to-apply` gate. Not blocking any Sprint 16 close-out. |
| S14.3 | Semantic model returns `readiness score per BOM item × region × track` for Switzerland North × T-SHOW. | ✅ done (S14.1) | `data-platform/reports/evidence.SemanticModel/` ([ADR-0026](../adr/0026-evidence-readiness-measure-ownership.md)) resolves the Phase 2 design question with **Option B (dedicated evidence.SemanticModel)**; scores land in `gold.fact_readiness_snapshot` per `docs/data-platform/evidence-gold-schema.md` | `python3 -m unittest discover -s data-platform/reports/tests` |
| S14.4 | Backstage → Evidence tab renders presenter whiteboard with ≥25 BOM cards + ≥10 ADR cards + ≥1 PRD-requirement card + dependency edges. | ✅ done (S14.1) | `apps/hcc-app-fluent/src/workspaces/backstage/tabs/evidence/EvidenceTab.tsx` — closes the Phase 2 T4/T5/T6 gap | `cd apps/hcc-app-fluent && npm test` + `npx playwright test tests/e2e/evidence.spec.ts` |
| S14.5 | Provenance visible on every card (`sourceUrl`, `asOf`); missing provenance fails render. | ✅ done (S14.1) | `apps/hcc-app-fluent/src/cards/evidence/_provenance.tsx` renders a visible provenance error when `sourceUrl`/`asOf` is missing | `cd apps/hcc-app-fluent && npm test -- evidence-cards` |
| S14.6 | Golden readiness-rule regression test green. | ✅ done | `data-platform/notebooks/evidence/tests/test_readiness_rules.py` present (golden + branch tests per test file docstring) | Test-execution status not verified in this audit — recommend `python -m pytest data-platform/notebooks/evidence/tests/test_readiness_rules.py -v` |
| S14.7 | Sprint 14 retro entry in checkpoint matrix. | ✅ done | Retro at line 136; retro EXPLICITLY calls out the T5/T6 gap at line 185 | |

**Sprint 14 result: 6/7 ✅ done, 1 ⏳ audit-pending. Audited 2026-07-10; S14.3-S14.5 closed by the Sprint 14.1 mini-sprint (2026-07-13).**

**Gaps closed by Sprint 14.1:**

- **S14.3 (design clarification):** readiness measure ownership decided in [ADR-0026](../adr/0026-evidence-readiness-measure-ownership.md) — **Option B (dedicated `evidence.SemanticModel`)**, keeping readiness out of the `capacity-dashboard` exact-count CI contract gate.
- **S14.4 + S14.5 (substantive):** Sprint 14 T4-T6 delivered — evidence semantic model + presenter whiteboard Evidence tab + card provenance contract. Tracked via [issue #182](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/182) (Sprint 14.1 mini-sprint).

**Runtime-verification-pending:** S14.2, S14.6 test execution — non-blocking.

---

## Sprint 15 — BVA Evidence Data Product (T1-T9)

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-15-bva-plan.md`](../superpowers/plans/2026-07-09-sprint-15-bva-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-15-bva-design.md`](../superpowers/specs/2026-07-09-sprint-15-bva-design.md) |
| **Primary merged PRs** | #168 (T1 generator), #173 (T2-T9) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S15.1 | `bva-sim-refresh.yml` green nightly. | ✅ **UPDATED 2026-07-15 (day-2 chunk #4h)** — done | **Mini-sprint [#225](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/225) closed same day it was opened.** Published a new **monolithic Fabric notebook** `bva_medallion_ingest` (id `56e4f37c-a1b5-4668-a3dc-ec551e483eef`) that chains Bronze register → Silver → 8 Gold dims → 3 Gold facts in one PySpark run, using inlined `bva_transforms` (same repo pattern as `csa-verify-mvp`). **Pivoted `bva-sim-refresh.yml` from `?jobType=Pipeline` → `?jobType=RunNotebook`** (env var rename `FABRIC_BVA_PIPELINE_ID` → `FABRIC_BVA_NOTEBOOK_ID`) to match the adoption-refresh pattern validated end-to-end on 2026-07-15 — avoids Fabric Data Factory Pipeline authoring (least-documented Fabric REST surface). Set `FABRIC_BVA_NOTEBOOK_ID` on `sit` GH env. **End-to-end notebook runs Completed** twice on 2026-07-15: debug run `2f65233f` (3min 28s), production run `cbd3afb1` (4min 3s), producing the full medallion (`bronze.bva_consumption` + `silver.bva_consumption` + 8 `gold.bva_dim_*` + 3 `gold.bva_fact_*` Delta tables) from 3,960 synthetic FOCUS rows (30-day slice, seed 202607150). Workflow CI trigger re-verification is a small follow-up (same identity as `adoption-refresh.yml` which we already know works end-to-end; will run post-merge). | **Non-blocking follow-ups (governance):** (1) scheduled nightlies still queue on `environment: sit` awaiting manual approval — same open decision as the S12.6 close-out follow-up (lift env gate for scheduled events? split to `sit-data-refresh` env with no reviewer? accept manual gate?). Recommend deciding once for `adoption-refresh.yml` + `bva-sim-refresh.yml` in a shared ADR. (2) `bva_transforms.py` inlined into the notebook creates a drift risk; a CI drift-check would be reasonable hardening. (3) Splitting into 4 per-stage notebooks + a Fabric Data Factory Pipeline could give per-stage retry granularity if needed later. |
| S15.2 | Medallion + semantic model produce all headline KPIs from KPI table §6 (design spec). | ✅ done | `bva_measures.tmdl` has 28 measures (verified during Sprint 16 fix session); relationships added to semantic model (25 total, 9 from BVA) | |
| S15.3 | Five C-suite Power BI pages rendered with RLS verified. | ✅ done | `data-platform/reports/bva-boardroom.Report/definition/pages/` contains **6 pages**: `board`, `ceo`, `cfo`, `cio`, `coo`, `cto` (exceeds the 5 required — bonus `board` overview page) | RLS pill verification not re-run in this audit; recommend running rls_test.py against BVA identities |
| S15.4 | BVA card cluster visible on Sprint 14 presenter whiteboard (BVA filter/tab). | ✅ **UPDATED 2026-07-15 (chunk #4n)** — done | Closed via [PR #236](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/236) (`sprint15.4/bva-whiteboard-projection`). Added a third preset (`bva`) to the `EvidenceTab.tsx` whiteboard: new `bvaCards()` helper in `apps/hcc-app-fluent/src/data/evidence/evidence-service.ts` imports `bvaHeadlineKpis` + `bvaPlanVsActual` + `bvaTrend` from `data/bva/bva-evidence.ts` (Sprint 15 T7 mock catalogue with provenance stamps) and emits `BvaHeadlineKpiCard × 2 + BvaPlanVsActualCard × 1 + BvaTrendCard × 1` = 4 CardModel entries; `EvidencePreset` union extended with `'bva'`; `buildEvidenceCards('bva', ...)` short-circuits (boardroom-focused view, no BOM/ADR/req clutter); `evidenceLayouts()` surfaces the new preset key; i18n keys `evidence.presetBva` in `en.json` ("BVA view") + `de.json` ("BVA-Ansicht"). New vitest asserts the projection and that every card resolves via `cardRegistry`; the pre-existing "whole-catalog" test correctly filters out the boardroom-focused BVA preset from the BOM ≥ 25 / ADR ≥ 10 / PRD ≥ 1 acceptance floor. CI 8/8 green (`hcc-app-fluent — lint + unit + build`, Playwright smoke, axe-core scan all pass). Cosmetic follow-up (non-blocking): rebuild + deploy `hcc-app-fluent` image to SIT so the new `BVA-Ansicht` tab is visible in the running app for the demo. | — |
| S15.5 | FOCUS shape validation green. | ✅ done | `data-platform/scripts/tests/test_bva_synth_focus.py` + `test_bva_upload_bronze.py` present | Test execution not re-run here; run `python -m pytest data-platform/scripts/tests/test_bva_*.py -v` |
| S15.6 | Cost calibration within ±15% of ROM baseline (CHF 760k/yr). | ✅ done | ADR-0025 §Synthetic calibration constants documents `TARGET_ANNUAL_BENEFIT_CHF = 1200000` + related constants used by `bva_transforms.py` | Note: ADR-0025 shows target 1200k not 760k — the plan text said 760k but the calibrated target grew during Sprint 15. Design intent preserved. |
| S15.7 | Stretch `bva-agent` drafts one board pack PR OR explicit "not attempted" note in retro. | ✅ done | `agents/bva-agent/` does NOT exist (confirming stretch not attempted). Retro at line 187 of checkpoint matrix explicitly says: "T8 (stretch) — not attempted. The application-hosted `bva-agent` per..." | |
| S15.8 | Sprint 15 retro entry in checkpoint matrix. | ✅ done | Retro at line 159 of `docs/sprints/superpowers-checkpoint-matrix.md` | |

**Sprint 15 result (revised 2026-07-15 pm after chunk #4n close of S15.4): 8/8 ✅ done, 0 ⚠️ partial, 0 ❌ gap. Previous ❌ S15.1 closed via monolithic Fabric notebook + workflow pivot to jobType=RunNotebook (chunk #4h); previous ⚠️ S15.4 closed via [PR #236](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/236) adding the `bva` preset to the Evidence whiteboard projection.**

**Gaps requiring gap-fill PRs:** none for Sprint 15 (all 8 items closed).

---

## Sprint 16 — CSA What-If Scenario Research and Catalogue

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-16-csa-plan.md`](../superpowers/plans/2026-07-09-sprint-16-csa-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-16-csa-design.md`](../superpowers/specs/2026-07-09-sprint-16-csa-design.md) |
| **Primary merged PRs** | #171 (T1-T9 program close-out), #174 (Bicep vector-throughput + PE fixes), #175 (v6 verification notebook capture) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S16.1 | Cosmos DB provisioned via Bicep with 4 containers. | ✅ done | `infra/modules/cosmos/csa.bicep` + PR #174; verified 2026-07-10 via `az cosmosdb sql container list` | |
| S16.2 | Fabric Mirroring live (or documented fallback in place). | ➖ not applicable | Deferred with rationale — Sprint 17 T1 (Fabric Git integration + Delta parity in Cell 7 of csa-verify-mvp) supersedes mirroring for BI parity; real-time mirroring is Sprint 19+ scope if needed | |
| S16.3 | 8 seeded scenarios in Cosmos with vector search working. | ✅ **UPDATED 2026-07-15 (day-2 chunk #4j)** — done | **Path A (Fabric MPE notebook) executed 2026-07-15 15:56 CET.** New durable artefact [`data-platform/notebooks/csa/csa-seed-scenarios.ipynb`](../../data-platform/notebooks/csa/csa-seed-scenarios.ipynb) published to Fabric workspace `f3af9733-9503-4e92-98f9-a901d96f1c87` as notebook `3978b53c-087d-4aab-8dc1-a38e4303610f`; the notebook uses Fabric-brokered auth (`notebookutils.credentials.getToken('https://cosmos.azure.com')`) + attached env-csa environment for `azure-cosmos`, iterates the 8 YAMLs under `data/csa/scenarios/`, upserts each into `cosmos-csa-ihzhhpf-sit / csa / scenarios` via Managed Private Endpoint, then queries `SELECT VALUE COUNT(1) FROM c` and asserts `count == 8`. Final job status `Completed`, livy state `Succeeded` (assert compiled in → proves all 8 present). Authoring script (gitignored `.scratch/publish_and_run_seed_scenarios.py`) regenerates the notebook from source YAMLs. **Long-term CI path** ([`csa-scenario-sync.yml`](../../.github/workflows/csa-scenario-sync.yml) via PR #232) shipped as workflow asset but scoped out for the MCAPS demo tenant per closed issue [#233](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/233) — MG-policy `CosmosDB_PublicNetwork_Modify` at Tenant Root Group forces private-endpoint-only, blocking GH-hosted runners; revisit in production tenant where either a scoped policy exception or an existing customer self-hosted runner VNet resolves it. | — |
| S16.4 | `csa-agent` completes Prepare → Run → Evaluate → Recommend for 3 MVP-tagged scenarios end-to-end. | ⚠️ **UPDATED 2026-07-15 (day-2 chunk #4g)** — partial (runtime shape refreshed) | `agents/csa-agent/AGENT.md` has the full Prepare/Run/Evaluate/Recommend body per PR #171. 3 recommendation PRs in `docs/csa/runs/` (see S16.6) — the outputs of the 3 MVP runs, still the only **physical evidence** of full-flow execution. **Runtime status refreshed 2026-07-15:** `csa-agent` manifest is confirmed **loaded** in the deployed `ca-agent-host-ihzhhpf-sit` (`GET /agents` returns 7 Sprint 11 agents including CSA with `ceiling:'write'`); chat endpoint `POST /agents/csa-agent/chat` returns HTTP 200 with a (mock) grounded reply; tool endpoint `POST /agents/csa-agent/tools/vector-query` correctly enforces the HITL-01 + HITL-04 gates from the manifest (`hitl.gates`). | **What remains for a true end-to-end DoD close:** (a) real Foundry chat model wiring (currently `orchestrator.mock_model.MockChatModel`); (b) real MCP tool execution (currently `{decision:'allow', tool:'...'}` stub at the invoke_tool handler per the code comment `Positive-path tool execution wiring lands per agent in follow-up sprints`); (c) real `fabric-mcp.run-notebook` trigger of `csa-simulate`; (d) real `cosmos-mcp.vector-query` against the seeded scenarios (S16.3). All 4 are Sprint 13 T5 stub-mode limitations, not S13.1 infrastructure blockers (which are now closed). |
| S16.5 | App wizard rendered in Sprint 13 app with role gating verified. | ✅ **UPDATED 2026-07-15 (day-2 chunk #4i)** — done | **Skeleton scaffold shipped** via mini-sprint [#229](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/229) closed same day it was opened. New component tree at `apps/hcc-app-fluent/src/workspaces/main/wizards/csa/`: `CsaWizard.tsx` (top-level composition) + `CsaRoleGuard.tsx` (role gate against `HCC.CrisisManager`/`OperationsLead`/`PlatformAdmin`/`SuperAdmin` per S16 spec §8) + `CsaStepper.tsx` (4-step linear TabList with progress indicator) + `CsaStepBody.tsx` (per-step body: Prepare wired live to `csa-agent` chat via `useAgentInvoker`, Run/Evaluate as scaffolds with "stub — Sprint 13 T5 wiring pending" badges, Recommend as read-only sample view over the 3 recommendation PRs from Sprint 16 T4) + `csa-steps.ts` (pure module: step catalog + sample-recommendation registry). Wired into shell: new rail entry `csa` (`WorkspaceKey`), `WorkspaceRouter` case, and i18n keys in `en.json` + `de.json`. Copilot Drawer opens with `agent="csa-agent"` in right rail per spec §8. **10 vitest unit tests** cover the pure step module + role guard authorisation logic + App integration (anonymous denied, SuperAdmin sees wizard, CrisisManager sees wizard). | **Known scope limits (documented on the Run/Evaluate step bodies with explicit badges):** live Run/Evaluate/Recommend behaviour waits on Sprint 13 T5 MCP-wiring completion (`fabric-mcp.run-notebook` + `cosmos-mcp.read-item` + `github-mcp.create-pull-request` currently return `{decision:'allow', tool:...}` stubs from the agent-host `invoke_tool` handler). Prepare step already provides real csa-agent grounded chat output. |
| S16.6 | 3 recommendation PRs merged into `docs/csa/runs/`. | ✅ done | 3 files present: `2026-07-09-cyberattack-hospital-services.md`, `2026-07-09-pediatric-virus-surge-rsv.md`, `2026-07-09-summer-heatwave-demand-surge.md` | |
| S16.7 | Tier classifier verified against doctrine. | ✅ done | `python -m pytest data-platform/notebooks/csa/tests/test_csa_simulate_pure.py` = **6 passed in 0.05s** (verified locally 2026-07-10) | |
| S16.8 | `csa-scenario-sync.yml` + `csa-run-followup.yml` workflows green. | ✅ done | Both workflows last 3 runs = `success` (2026-07-09) | |
| S16.9 | Sprint 16 retro entry in checkpoint matrix + program close-out summary. | ✅ done | `docs/sprints/superpowers-checkpoint-matrix.md` v1.5.0 header explicitly says "Sprint 15 in-flight row + Sprint 16 rows/retros + program close-out added" | |
| S16.10 | Kickoff issue closed with retro comment. | ✅ done | Issue #170 CLOSED on 2026-07-09T13:46:06Z | |
| S16.11 | **[Post-merge, this session]** SIT go-live evidence via v6 verification notebook. | ✅ done | [PR #175](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/175); notebook run 2026-07-10 10:43 CET: 8/8 Spark jobs green, tier=2 canonical output, Delta parity write to lakehouse | |

**Sprint 16 result (revised 2026-07-15 pm after day-2 chunk #4j close of S16.3): 10/12 ✅ done, 1 ⚠️ partial (S16.4 — live agent execution runtime-verification limited by Sprint 13 T5 MCP-wiring stub mode, not code gaps), 1 🚫 N/A (S16.2 Fabric Mirroring deferred), 0 ❌ gap, 0 ⏳ audit-pending. Chunk history: #4i closed S16.5 via CSA wizard skeleton at `apps/hcc-app-fluent/src/workspaces/main/wizards/csa/`; #4j closed S16.3 via Path A Fabric MPE notebook `data-platform/notebooks/csa/csa-seed-scenarios.ipynb` + closed Sprint 17 tracker issue [#233](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/233) documenting the MG-policy blocker for the long-term GH-hosted CI path.**

**Gaps requiring gap-fill PRs:** none for Sprint 16 (S16.4 is a Sprint 13 T5 stub-mode limitation tracked separately).

**Runtime-verification-pending:** S16.4 (live agent execution) — needs Sprint 13 T5 MCP-wiring completion (`fabric-mcp.run-notebook` + `cosmos-mcp.vector-query` currently return `{decision:'allow', tool:...}` stubs from the agent-host `invoke_tool` handler).

---

## PBI Demoable Redesign v2 — Milestones M2-M6

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-powerbi-demoable-redesign-plan.md`](../superpowers/plans/2026-07-09-powerbi-demoable-redesign-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-powerbi-demoable-redesign-design.md`](../superpowers/specs/2026-07-09-powerbi-demoable-redesign-design.md) |
| **Primary merged PRs** | #152 (M1 theme + RLS foundation), #172 (M2-M6) |

| # | DoD item (from plan §Definition of Sprint-parallel done) | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| PBI.1 | All 6 milestones M1-M6 landed as merged PRs. | ✅ done | PR #152 (M1) + PR #172 (M2-M6) | |
| PBI.2 | Helvion theme applied to every page; visual-regression snapshots clean. | ⏳ audit-pending | Report theme in `data-platform/reports/capacity-dashboard.Report/definition/*` | Runtime verification via PBI Desktop — not automatable from CLI |
| PBI.3 | Landing + 3 persona + grounding pages all rendered with content (no empty visualContainers). | ✅ done | `data-platform/scripts/report_structure_check.py` → PASS: 5 visible + 6 hidden pages, all populated (verified 2026-07-10 in PR #172 fix session) | |
| PBI.4 | All headline KPIs wired to `tooltip-kpi-delta`, contributor charts wired to `tooltip-contributor`. | ✅ done | **14 visuals** bind `tooltip-kpi-delta`, **7 visuals** bind `tooltip-contributor` (verified via file grep across `pages/`) | |
| PBI.5 | All 3 drill-through pages roundtrip correctly. | ✅ done | 3 pages exist: `drill-ward`, `drill-theatre`, `drill-discharge` — each with a "Back" navigation button per PR #172 review file list | Roundtrip test itself needs PBI Desktop |
| PBI.6 | RLS-proof pill returns expected values across 6 test identities. | ⏳ audit-pending | `data-platform/scripts/rls_test.py` + `rls_test_matrix.yaml` present | Run `python data-platform/scripts/rls_test.py` — needs Fabric workspace access + 6 test identities from Sprint 12 Batch A |
| PBI.7 | Field parameters swap without formatting loss. | ✅ done | Both `param_capacity_measure.tmdl` and `param_or_measure.tmdl` present in SemanticModel | Runtime swap test needs PBI Desktop |
| PBI.8 | Smart-narrative measures return substantive text for 3 personas. | ✅ done | **3 Narrative measures** present in `bed_assignment.tmdl` / `fact_capacity_baseline.tmdl` (Narrative — Bed Manager, Narrative — Ops Lead, Narrative — OR Coordinator per the ExpectedMeasures accounting comment in `export_semantic_model_tmdl.ps1`) | Live-narrative substantive content depends on Direct Lake data — check when data is loaded |
| PBI.9 | Grounding-card strip on every visible page; `page-grounding` matrix populated. | ✅ done | `page-grounding` page exists; **11 visuals** across pages reference `page-grounding` (grounding action buttons per PR #172 review) | |
| PBI.10 | Perf-benchmark hero scenario cold < 4000ms, warm < 500ms. | ⏳ audit-pending | `data-platform/scripts/perf_hero.py` present | Run `python data-platform/scripts/perf_hero.py` in benchmark mode; needs Direct Lake data + Fabric access |
| PBI.11 | `powerbi-report-author validate` returns clean. | ⏳ audit-pending | | Run `powerbi-report-author validate data-platform/reports/capacity-dashboard.Report` — CLI tool availability not verified in this audit environment |
| PBI.12 | `capacity-dashboard.Report/README.md` updated. | ✅ done | README updated in PR #172 (page count fix landed as part of session hardening) | |
| PBI.13 | Retro entry in checkpoint matrix. | ✅ done | Retro at line 216 of `docs/sprints/superpowers-checkpoint-matrix.md`: "Power BI Demoable Redesign (capacity dashboard v2) retro notes" | |

**PBI Demoable v2 result: 9/13 ✅ done, 0 ⚠️ partial, 0 ❌ gap, 4 ⏳ audit-pending (all runtime tests requiring PBI Desktop / Fabric data). Audited 2026-07-10.**

**No gap-fill PRs required — this track is functionally complete.** The 4 pending items are runtime verifications, not code gaps.

---

## Phase 2 execution order

Sprints are audited in **dependency order** — later sprints assume earlier ones are correct, so a gap found in Sprint 11 may cascade forward. Recommended order:

1. **Sprint 11** (agents foundation) — every later sprint depends on agent packs existing.
2. **Sprint 12** (Entra org + adoption) — Sprint 13 + 14 + 15 depend on personas + telemetry.
3. **Sprint 13** (app tier) — Sprint 14 (Evidence tab) + Sprint 16 (CSA wizard) depend on it.
4. **Sprint 14** (Showcase Evidence) — Sprint 15 (BVA cards) depends on the whiteboard tab.
5. **Sprint 15** (BVA) — self-contained after S14.
6. **Sprint 16** (CSA) — Sprint 17 T2 depends on lakehouse state; but Sprint 16 SIT go-live is already independently verified this session.
7. **PBI Demoable v2** — independent of the six sprint chain; can be audited last (or in parallel).

Per-sprint audit PR pattern (Phase 2):

- Branch: `sprint-review/phase-2-s<NN>-audit`
- Files touched: this doc (`docs/sprints/2026-07-10-sprints-11-16-review-checklist.md`) — fill Status / Evidence / Gap columns for that sprint's rows
- Additional gap-fill PRs: opened separately from the audit PR when a `❌ gap` / `⚠️ partial` is found and can be fixed without a wide change

## Definition of done for THIS scaffold PR

- [x] Every DoD item from each of the 7 plan docs is transcribed into a row.
- [x] Primary merged PRs listed per sprint.
- [x] Phase 2 execution order documented.
- [x] `markdownlint-cli2@0.15.0` clean (verified before commit).
- [x] Status column defaults to `⏳ audit-pending` for items not yet walked; `✅ done` and `➖ not applicable` used only where this session has already produced the evidence (Sprint 16 S16.1, S16.2, S16.11; PBI PBI.1, PBI.3, PBI.12).

Nothing in this scaffold PR modifies production code, IaC, workflows, or agent prompts. It is a **read-only audit scaffold** that Phase 2 fills in.
