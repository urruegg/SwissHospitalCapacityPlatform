# Sprints 11-16 + PBI Demoable v2 — DoD Review Checklist

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-10 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | n/a (new — Phase 1b of the 2026-07-10 sprint-review push) |
| **Purpose** | Track evidence + gap-fill for every Definition-of-Done item across Sprints 11-16 and PBI Demoable v2 M2-M6. Feeds Phase 2 (per-sprint audit) and Phase 3 (Sprint 17 kickoff on a stabilised base). |
| **Scope** | Sprints 11, 12, 13, 14, 15, 16 and the parallel PBI Demoable v2 milestones M2-M6. Sprints 01-10 explicitly out of scope. |
| **Related** | [`docs/sprints/superpowers-checkpoint-matrix.md`](superpowers-checkpoint-matrix.md); [`docs/superpowers/specs/2026-07-09-sprints-11-16-roadmap-design.md`](../superpowers/specs/2026-07-09-sprints-11-16-roadmap-design.md) |

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
| S11.1 | Task 1 (foundation) merged. | ⏳ audit-pending | PR #149 (foundation Task 1 batched into agent PR per plan §Task 1) | |
| S11.2 | Tasks 2-8 (7 MVP agents) merged, each with prompt file + golden-tasks + AGENTS.md row. | ⏳ audit-pending | PR #149 | Walk `agents/{bmca,ooa,dca,orsa,sba,csa,data-quality}-agent/` for AGENT.md + golden-tasks.md presence + AGENTS.md §1 row |
| S11.3 | Model-selection ADR (0020-*) merged and referenced by each agent. | ⏳ audit-pending | `docs/adr/0020-sprint11-agent-model-selection.md` | Grep each `agents/*/AGENT.md` for `ADR-0020` reference |
| S11.4 | `eval-goldens.yml` green across all fixtures. | ⏳ audit-pending | `.github/workflows/eval-goldens.yml` (post-PR-#177 hygiene) | Run `gh workflow run eval-goldens.yml` for each of the 7 agents; capture pass/fail |
| S11.5 | `agent-build.yml` and `sprint-kickoff.yml` templates in place. | ⏳ audit-pending | `.github/ISSUE_TEMPLATE/agent-build.yml`, `sprint-kickoff.yml` | Check file presence |
| S11.6 | `fabric-mcp` entry added to `.github/copilot/mcp.json` and `AGENTS.md` §2. | ⏳ audit-pending | | Read both files and grep for `fabric-mcp` |
| S11.7 | For each user-facing agent: prompt manifest + tool contract + HITL gate declaration ready for Sprint 13 runtime loading. | ⏳ audit-pending | `agents/*/manifest.yaml` | Verify every user-facing agent folder has `manifest.yaml` |
| S11.8 | Sprint 11 retro entry in `docs/sprints/superpowers-checkpoint-matrix.md`. | ⏳ audit-pending | | Grep matrix for "Sprint 11" |
| S11.9 | Kickoff issue #146 closed with summary comment. | ⏳ audit-pending | | `gh issue view 146 --json state,comments` |

---

## Sprint 12 — Org (Entra demo-org IaC + MSAL + role-switcher + adoption telemetry)

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-12-org-plan.md`](../superpowers/plans/2026-07-09-sprint-12-org-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-12-org-design.md`](../superpowers/specs/2026-07-09-sprint-12-org-design.md) |
| **Primary merged PRs** | #159 (T1-T7) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S12.1 | Tasks T1-T7 all merged. | ⏳ audit-pending | PR #159 | Walk PR #159 for each of T1-T7 |
| S12.2 | 15 app roles + 15 security groups + 23 personas provisioned in SIT (or documented deferral). | ⏳ audit-pending | Bicep + CSV under `infra/modules/entra-org/` | Verify seed CSVs exist and match counts; check SIT via `az ad app show` / `az ad group list` |
| S12.3 | `super.admin` and `demo.guest` sign-in verified against Sprint 13 app shell (or dry auth callback). | ⏳ audit-pending | | Requires app shell running; verify by inspection of test evidence in PR #159 |
| S12.4 | Adoption telemetry pipeline emitting nightly files within 24h of T5 merge. | ⏳ audit-pending | `.github/workflows/adoption-refresh.yml` | Check last successful workflow run: `gh run list --workflow adoption-refresh.yml --limit 5` |
| S12.5 | `env`-scoping smoke test green (same identity, two slots, two Bronze paths). | ⏳ audit-pending | | Find test script/output in PR #159 |
| S12.6 | `entra-whatif.yml` + `adoption-refresh.yml` operational. | ⏳ audit-pending | `.github/workflows/entra-whatif.yml` | `gh run list --workflow entra-whatif.yml` |
| S12.7 | `entra-provisioning.yml` issue template selectable. | ⏳ audit-pending | `.github/ISSUE_TEMPLATE/entra-provisioning.yml` | File presence check |
| S12.8 | Retro row in checkpoint matrix. | ⏳ audit-pending | | Grep matrix for "Sprint 12" |
| S12.9 | Kickoff issue closed. | ⏳ audit-pending | | Find + check issue |
| S12.10 | PROD promotion tracked as follow-up issue. | ⏳ audit-pending | | `gh issue list --label sprint-12-prod` |

---

## Sprint 13 — App (Fluent baseline + Container Apps agent-host + Rayfin PoC + drawer + whiteboard)

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-13-app-plan.md`](../superpowers/plans/2026-07-09-sprint-13-app-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-13-app-design.md`](../superpowers/specs/2026-07-09-sprint-13-app-design.md) |
| **Primary merged PRs** | #162 (T1-T8) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S13.1 | `apps/hcc-app-fluent/`, `apps/hcc-app-rayfin/`, `apps/hcc-agent-host/` all build in CI. | ⏳ audit-pending | `.github/workflows/app-build.yml`, `agent-host-build.yml` | `gh run list --workflow app-build.yml` |
| S13.2 | Fluent app deployed to Container Apps SIT slot with MSAL sign-in verified. | ⏳ audit-pending | | Check deployed container app in `rg-ihzhhpf-sit` via `az containerapp list` |
| S13.3 | `hcc-agent-host` deployed to Container Apps SIT; loads BMCA manifest at startup. | ⏳ audit-pending | | Same as S13.2 + check startup logs for manifest load |
| S13.4 | BedManager whiteboard renders 6 card types with mock data. | ⏳ audit-pending | `apps/hcc-app-fluent/src/whiteboard/CardRegistry.tsx` | Read registry + run app locally |
| S13.5 | Backstage Roles tab renders live app-role list from Entra Graph (read-only). | ⏳ audit-pending | | Find Roles-tab component + test |
| S13.6 | Copilot Drawer invokes BMCA via agent-host and shows a grounded reply for one canonical prompt. | ⏳ audit-pending | | Read drawer implementation + smoke test |
| S13.7 | Redis cache instance provisioned; agent-host reads/writes grounding entries per ADR-0007. | ⏳ audit-pending | `infra/modules/redis/` | Bicep presence + `az redis show` |
| S13.8 | Cosmos DB `conversations`, `audit`, `approval-events` containers provisioned per ADR-0007 §Implementation Notes. | ⏳ audit-pending | | `az cosmosdb sql container list` on the app-host Cosmos account |
| S13.9 | HITL-01..HITL-05 gate scaffolding in place with deny-by-default. | ⏳ audit-pending | `apps/hcc-agent-host/src/gates/` (expected) | Find gate middleware + verify deny-by-default posture |
| S13.10 | `app-build.yml`, `app-e2e.yml`, `app-a11y.yml` green. | ⏳ audit-pending | | `gh run list --workflow app-e2e.yml --limit 3` |
| S13.11 | Decision ADR merged recommending one stack for Sprint 14+. | ⏳ audit-pending | `docs/adr/0023-app-stack-fluent-vs-rayfin-decision.md` | Read ADR + confirm status Accepted |
| S13.12 | Sprint 13 retro entry in checkpoint matrix. | ⏳ audit-pending | | Grep matrix |

---

## Sprint 14 — Showcase Evidence data product

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-14-evidence-plan.md`](../superpowers/plans/2026-07-09-sprint-14-evidence-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-14-evidence-design.md`](../superpowers/specs/2026-07-09-sprint-14-evidence-design.md) |
| **Primary merged PRs** | #165 (T1-T3 + T7 retro) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S14.1 | `evidence-publish.yml` runs on push and produces `data/evidence/*.json` on `evidence-latest` branch. | ⏳ audit-pending | `.github/workflows/evidence-publish.yml` | `gh run list --workflow evidence-publish.yml --limit 3` |
| S14.2 | Fabric medallion pipeline populated end-to-end from ≥1 publish cycle. | ⏳ audit-pending | | Verify `evidence-latest` branch has ≥1 commit + Fabric side |
| S14.3 | Semantic model returns readiness score per BOM item × region × track for Switzerland North × T-SHOW. | ⏳ audit-pending | Semantic model measures | Run DAX query via SQL endpoint |
| S14.4 | Backstage → Evidence tab renders presenter whiteboard with ≥25 BOM cards + ≥10 ADR cards + ≥1 PRD-requirement card + dependency edges. | ⏳ audit-pending | `apps/hcc-app-fluent/src/workspaces/main/tabs/evidence/` (expected) | Find Evidence tab + run app |
| S14.5 | Provenance visible on every card (`sourceUrl`, `asOf`); missing provenance fails render. | ⏳ audit-pending | | Read card component; check contract test |
| S14.6 | Golden readiness-rule regression test green. | ⏳ audit-pending | `data-platform/notebooks/evidence/tests/` (expected) | Find + run pytest |
| S14.7 | Sprint 14 retro entry in checkpoint matrix. | ⏳ audit-pending | | Grep matrix |

**Note:** PR #165 title says "T1-T3 foundation + T7 retro" — T4-T6 status unclear from PR title alone; audit needs to reconcile against plan §Task list.

---

## Sprint 15 — BVA Evidence Data Product (T1-T9)

| Field | Value |
|-------|-------|
| **Plan** | [`docs/superpowers/plans/2026-07-09-sprint-15-bva-plan.md`](../superpowers/plans/2026-07-09-sprint-15-bva-plan.md) |
| **Design spec** | [`docs/superpowers/specs/2026-07-09-sprint-15-bva-design.md`](../superpowers/specs/2026-07-09-sprint-15-bva-design.md) |
| **Primary merged PRs** | #168 (T1 generator), #173 (T2-T9) |

| # | DoD item | Status | Evidence | Gap |
|---|------|--------|----------|-----|
| S15.1 | `bva-sim-refresh.yml` green nightly. | ⏳ audit-pending | `.github/workflows/bva-sim-refresh.yml` | `gh run list --workflow bva-sim-refresh.yml --limit 5` |
| S15.2 | Medallion + semantic model produce all headline KPIs from KPI table §6 (design spec). | ⏳ audit-pending | `data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/bva_measures.tmdl` | Count measures vs. §6 catalog; 28 measures now merged (verified in Sprint 16 fix) |
| S15.3 | Five C-suite Power BI pages rendered with RLS verified. | ⏳ audit-pending | `data-platform/reports/bva-boardroom.Report/definition/pages/{ceo,cfo,cio,coo,cto,board}/` (6 folders present) | Reconcile 5 vs. 6 — walk pages + verify RLS pill |
| S15.4 | BVA card cluster visible on Sprint 14 presenter whiteboard (BVA filter/tab). | ⏳ audit-pending | `apps/hcc-app-fluent/src/cards/bva/` (present) + `apps/hcc-app-fluent/src/whiteboard/CardRegistry.tsx` | Read registry integration |
| S15.5 | FOCUS shape validation green. | ⏳ audit-pending | `data-platform/scripts/tests/test_bva_upload_bronze.py` | Run pytest |
| S15.6 | Cost calibration within ±15% of ROM baseline (CHF 760k/yr). | ⏳ audit-pending | ADR-0025 (KPI catalog) | Compute total from BVA measures |
| S15.7 | Stretch `bva-agent` drafts one board pack PR OR explicit "not attempted" note in retro. | ⏳ audit-pending | | Check retro for note; check for `agents/bva-agent/` |
| S15.8 | Sprint 15 retro entry in checkpoint matrix. | ⏳ audit-pending | | Grep matrix |

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
| S16.2 | Fabric Mirroring live (or documented fallback in place). | ➖ not applicable | Deferred with rationale in [PR #174 comment](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/174); Sprint 17 T1 supersedes mirroring for BI parity | Deferred to Sprint 19+ if real-time analytics becomes a genuine requirement |
| S16.3 | 8 seeded scenarios in Cosmos with vector search working. | ⏳ audit-pending | Sprint 16 T3 in PR #171; the v6 verification notebook proves the seed path works with 1 RSV scenario | Seeding of the full 8 scenarios in SIT not yet verified (only 1 was proven via v6 notebook) |
| S16.4 | `csa-agent` completes Prepare → Run → Evaluate → Recommend for 3 MVP-tagged scenarios end-to-end. | ⏳ audit-pending | `agents/csa-agent/AGENT.md` (has full body per PR #171) | Runtime execution of the 3 MVP runs not yet independently verified |
| S16.5 | App wizard rendered in Sprint 13 app with role gating verified. | ⏳ audit-pending | | Find wizard component in `apps/hcc-app-fluent/src/workspaces/main/wizards/csa/` |
| S16.6 | 3 recommendation PRs merged into `docs/csa/runs/`. | ⏳ audit-pending | | `ls docs/csa/runs/` |
| S16.7 | Tier classifier verified against doctrine. | ⏳ audit-pending | `data-platform/scripts/csa/csa-tier-classifier.py` + tests | Run `data-platform/notebooks/csa/tests/test_csa_simulate_pure.py` |
| S16.8 | `csa-scenario-sync.yml` + `csa-run-followup.yml` workflows green. | ⏳ audit-pending | `.github/workflows/csa-scenario-sync.yml`, `csa-run-followup.yml` | `gh run list --workflow csa-scenario-sync.yml` |
| S16.9 | Sprint 16 retro entry in checkpoint matrix + program close-out summary. | ⏳ audit-pending | | Grep matrix |
| S16.10 | Kickoff issue closed with retro comment. | ⏳ audit-pending | | Find + check issue |
| S16.11 | **[Post-merge, this session]** SIT go-live evidence via v6 verification notebook. | ✅ done | [PR #175](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/175); notebook run 2026-07-10 10:43 CET: 8/8 Spark jobs green, tier=2 canonical output, Delta parity write to lakehouse | This is beyond the original DoD but confirms Cosmos data plane + Fabric MPE + notebook workflow end-to-end |

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
| PBI.2 | Helvion theme applied to every page; visual-regression snapshots clean. | ⏳ audit-pending | | Reload PBIP + check theme; find snapshot test if any |
| PBI.3 | Landing + 3 persona + grounding pages all rendered with content (no empty visualContainers). | ✅ done | `data-platform/scripts/report_structure_check.py` → PASS: 5 visible + 6 hidden pages, all populated (verified 2026-07-10 in PR #172 fix session) | |
| PBI.4 | All headline KPIs wired to `tooltip-kpi-delta`, contributor charts wired to `tooltip-contributor`. | ⏳ audit-pending | | Read visual.json bindings for `.tooltip` refs |
| PBI.5 | All 3 drill-through pages roundtrip correctly. | ⏳ audit-pending | Pages `drill-ward`, `drill-theatre`, `drill-discharge` exist | Test roundtrip in PBI Desktop |
| PBI.6 | RLS-proof pill returns expected values across 6 test identities. | ⏳ audit-pending | `data-platform/scripts/rls_test.py` (expected) | Run script or find test evidence |
| PBI.7 | Field parameters swap without formatting loss. | ⏳ audit-pending | `bva_measures.tmdl` + `param_capacity_measure` + `param_or_measure` tables | Verify param tables + test swap in PBI |
| PBI.8 | Smart-narrative measures return substantive text for 3 personas. | ⏳ audit-pending | M5 narrative measures in `bed_assignment.tmdl` + `fact_capacity_baseline.tmdl` | Run DAX or find test |
| PBI.9 | Grounding-card strip on every visible page; `page-grounding` matrix populated. | ⏳ audit-pending | Grounding buttons visible in visuals + `page-grounding` page exists | Screenshot verification |
| PBI.10 | Perf-benchmark hero scenario cold < 4000ms, warm < 500ms. | ⏳ audit-pending | `data-platform/scripts/perf_hero.py` (per Copilot review) | Run perf script + capture output |
| PBI.11 | `powerbi-report-author validate` returns clean. | ⏳ audit-pending | | Run validator |
| PBI.12 | `capacity-dashboard.Report/README.md` updated. | ✅ done | README updated in PR #172 (page count fix landed as part of session hardening) | |
| PBI.13 | Retro entry in checkpoint matrix. | ⏳ audit-pending | | Grep matrix |

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
