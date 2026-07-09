# Sprint 16 — CSA What-If Scenario Research and Catalogue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended — one subagent per task) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the Sprint 11 CSA scaffold into a working what-if system: Azure Cosmos DB for NoSQL persistence (4 containers) mirrored to Fabric OneLake, an application-hosted `csa-agent` walking users through **Prepare → Run → Evaluate → Recommend**, a Fabric simulation notebook, a tier classifier grounded in Swiss Lage doctrine, and 8 seeded scenarios with 3 end-to-end MVP runs producing merged recommendation PRs.

**Architecture:** Substantial infra + agent + notebook + app wizard split across nine tasks. Reuses Sprint 13 whiteboard framework (cards for scenarios) and Copilot Drawer (for the `csa-agent`). Cosmos DB persistence per Microsoft best practice for AI agents; Fabric Mirroring per the preview guidance (fallback documented). Design contract in [`docs/superpowers/specs/2026-07-09-sprint-16-csa-design.md`](../specs/2026-07-09-sprint-16-csa-design.md).

**Tech Stack:** Bicep (Cosmos + mirroring), Python 3.11+ (seed script + tier classifier + workflows), PySpark (`csa-simulate.ipynb`), Markdown (agent prompt body + golden tasks), React + TypeScript (Sprint 13 wizard surface + role-gated route), MSAL role gate (from Sprint 12 T2), Cosmos MCP + Fabric MCP.

---

## Prerequisites (verify before starting)

- [ ] On `main`, clean: `git switch main; git pull`.
- [ ] Sprint 16 design spec merged at v1.1.0.
- [ ] Sprint 16 plan merged (from the PR that lands this file).
- [ ] **Sprint 11 `csa-agent` scaffold** merged (from PR #149) — the pack shell exists; T4 writes the body.
- [ ] **Sprint 13 T5** (Container Apps agent-host) merged — required for T4 `csa-agent` loading. Track via issue #161 / PR #162.
- [ ] **Sprint 13 T3** (whiteboard framework + card registry) merged — required for T7 wizard. Track via #161.
- [ ] **Sprint 13 T6** (Copilot Drawer) merged — required for T7 wizard. Track via #161.
- [ ] **Sprint 12 T2** (MSAL claim contexts + role switcher) merged — required for T7 role gate. Track via PR #159 (merged).
- [ ] **Sprint 10 Gold capacity data** exists — the simulation notebook reads from it.
- [ ] **Sprint 14 T5/T6** (Evidence tab + presenter whiteboard) merged — nice-to-have for cross-drill; not blocking. Track via #164 / PR #165.
- [ ] Fabric capacity `fabricihzhhpfsit` state = **Active**.
- [ ] `az` CLI authenticated to SIT tenant per ADR-0012.
- [ ] `gh` CLI authenticated.
- [ ] Explicit go-ahead from @urruegg in the Sprint 16 kickoff issue thread.

---

## File Structure

Files created or modified across the nine tasks.

### T1 — Cosmos DB provisioning (4 containers) + MCP allow-list

- Create: `infra/modules/cosmos/csa.bicep` — Cosmos DB for NoSQL account (`cosmos-csa-ihzhhpf-sit`) with 4 containers.
- Create: `infra/modules/cosmos/main.bicep` — subscription-scope wrapper for the module.
- Create: `infra/modules/cosmos/parameters/sit.bicepparam` (+ prod placeholder).
- Modify: `infra/main.bicep` — reference the Cosmos module (optional; Cosmos may be its own top-level deployment).
- Modify: `.github/copilot/mcp.json` — add `cosmos-mcp` server if not already present, with a documented purpose + required permissions + a golden-task pointer.
- Modify: `AGENTS.md` §2 — add `cosmos-mcp` row if newly added.
- Modify: `.github/CODEOWNERS` — add `/infra/modules/cosmos/**` → @urruegg.
- Create: `infra/modules/cosmos/README.md` — RU budget, vector policies, consistency notes.

**Cosmos config per design spec §4:**
- `scenarios` — PK `/scenarioId`, vector `DiskANN` on `descriptionEmbedding`.
- `agent-memory` — PK `/threadId`, vector `DiskANN` on `contentEmbedding` sharded by `/threadId`.
- `response-levers` — PK `/leverId`, vector `quantizedFlat` on `descriptionEmbedding`.
- `simulation-runs` — PK `/runId`, no vector.
- Consistency: Session.

**Deploy gate:** T1 has an `approved-to-apply` gate for the Cosmos provisioning + one for the MCP allow-list PR (CODEOWNERS review).

### T2 — Fabric Mirroring from Cosmos to OneLake

- Create: `data-platform/scripts/csa/enable-cosmos-mirroring.py` (or PowerShell equivalent) — creates the `fabric-mirrored-csa` Fabric item pointing at the T1 Cosmos account.
- Create: `data-platform/scripts/csa/README-mirroring.md` — preview caveats, sovereign-cloud fallback, verification steps.
- Create: `data-platform/scripts/csa/fallback-change-feed-copy.py` — the fallback Spark job if mirroring is blocked at go-live (empty stub with README until fallback triggers).
- Modify: `docs/data-platform/` — add `csa-mirroring-notes.md` documenting the mirrored Delta table names in OneLake.

**Deploy gate:** T2 has an `approved-to-apply` gate for enabling mirroring.

### T3 — Cosmos schema smoke tests + seed the response-lever library

- Create: `data-platform/scripts/csa/schema/{scenarios,agent-memory,response-levers,simulation-runs}.schema.json` — JSON Schemas per container.
- Create: `data-platform/scripts/csa/csa-seed-response-levers.py` — seeds the response-lever library (< 100 items derived from the anchor idea's doctrine table + design spec §6).
- Create: `data-platform/scripts/csa/tests/{test_scenario_upsert,test_vector_search,test_hybrid_search,test_agent_memory_thread}.py` — pytest against a Cosmos emulator or a dev-only Cosmos container. Skip suite when creds unset.
- Create: `data-platform/scripts/csa/README-schema.md`.

### T4 — `csa-agent` full body (Prepare → Run → Evaluate → Recommend)

- Modify: `agents/csa-agent/AGENT.md` — expand the Sprint 11 scaffold into the full body per design spec §5. 8-section shape retained (Identity / Scope / Tools / Refusal Rules / Output Contract / Confirmation Rules / HITL Gates / Provenance) + a new "Phases" section documenting Prepare/Run/Evaluate/Recommend.
- Modify: `agents/csa-agent/manifest.yaml` — bump ceiling from S11 `write` to `deploy` (for simulation-run trigger); add `cosmos-mcp:write`, `fabric-mcp:write` (notebook trigger); HITL-01 (crisis escalation) + HITL-04 (recommendation draft PR).
- Modify: `agents/csa-agent/golden-tasks.md` — expand from S11 scaffold to include one fixture per seeded scenario. Include the RSV-surge Tier 2 canonical fixture and the cyber-attack Tier 2–3 fixture.
- Modify: `AGENTS.md` §1 — update `csa-agent` registry row: side-effect ceiling bumps to `deploy` (gated), tools list expands.

### T5 — Tier classifier + simulation notebook

- Create: `data-platform/scripts/csa/csa-tier-classifier.py` — rules layer over ontology capacity states. Rules version-pinned; every change requires an ADR reference.
- Create: `data-platform/scripts/csa/tests/test_tier_classifier.py` — golden fixtures covering Normallage / Besondere Lage / Ausserordentliche Lage transitions.
- Create: `docs/adr/00XX-csa-tier-classifier-rules.md` — codifies the Lage doctrine rules as an ADR (Accepted).
- Create: `data-platform/notebooks/csa/csa-simulate.py` — PySpark notebook reading synthetic Gold capacity data, running the shock model, writing `DC-SIM-RESULT` back to Fabric.
- Create: `data-platform/notebooks/csa/README.md`.
- Create: `data-platform/notebooks/csa/tests/test_csa_simulate_pure.py` — pure-function tests for the shock model (no Spark session).
- Modify: `data-platform/scripts/csa/deploy-notebook.py` — publishes `csa-simulate.py` to `ws-ihzhhpf-sit-data` and wires the Fabric REST trigger endpoint.

**Deploy gate:** T5 has an `approved-to-apply` gate for the notebook publish.

### T6 — Seed the 8 scenarios

- Create: `data-platform/scripts/csa/csa-seed-scenarios.py` — seeds 8 scenarios from the anchor idea §6.
- Create: `data/csa/scenarios/*.yaml` — one YAML file per scenario for round-tripping (workflow T8 syncs YAML → Cosmos).
- Create: `data/csa/scenarios/README.md`.
- Modify: `.github/CODEOWNERS` — add `/data/csa/**` → @urruegg.

### T7 — App wizard in the Sprint 13 surface

- Create: `apps/hcc-app-fluent/src/workspaces/main/wizards/csa/CsaWizard.tsx` — 4-step wizard (Prepare / Run / Evaluate / Recommend) with progress indicator.
- Create: `apps/hcc-app-fluent/src/workspaces/main/wizards/csa/steps/{Prepare,Run,Evaluate,Recommend}Step.tsx` — one component per phase.
- Create: `apps/hcc-app-fluent/src/workspaces/main/wizards/csa/CopilotDrawerBinding.tsx` — binds the drawer to the current wizard step and streams `csa-agent` responses.
- Create: `apps/hcc-app-fluent/src/data/csa/{useScenarios,useRun,useEvaluate,useRecommendations}.ts` — hooks calling the Sprint 13 agent-host `/agents/csa-agent/*` endpoints.
- Modify: `apps/hcc-app-fluent/src/workspaces/main/WorkspaceRouter.tsx` — add `/main/wizards/csa` route with role gate (`HCC.CrisisManager`, `HCC.OperationsLead`, `HCC.PlatformAdmin`, `HCC.SuperAdmin`).
- Create: `apps/hcc-app-fluent/tests/e2e/csa-wizard.spec.ts` — Playwright: sign in as `crisis.manager` → nav wizard → run RSV-surge → assert Recommend step opens a draft PR link.
- Create: `apps/hcc-app-fluent/tests/e2e/csa-wizard-rbac.spec.ts` — Playwright: sign in as `demo.guest` → nav attempt → assert 403 / route hidden.

### T8 — GitHub delegation (issue templates + sync workflows)

- Create: `.github/ISSUE_TEMPLATE/csa-scenario.yml` — new/updated scenario intake.
- Create: `.github/ISSUE_TEMPLATE/csa-run.yml` — requested simulation run.
- Create: `.github/workflows/csa-scenario-sync.yml` — on merge of `data/csa/scenarios/*.yaml`, validate against schema and upsert into Cosmos.
- Create: `.github/workflows/csa-run-followup.yml` — on merge of `docs/csa/runs/*.md`, close the parent run issue.
- Create: labels `csa`, `csa-scenario`, `csa-recommendation`, `cosmos-provision`.

### T9 — Three MVP end-to-end runs + retro

**The proof:** three seeded scenarios (cyber-attack, RSV surge, heatwave) run through the wizard end-to-end and yield merged recommendation PRs at `docs/csa/runs/`.

- Trigger via the wizard OR via `csa-run.yml` issue template.
- Each produces `docs/csa/runs/YYYY-MM-DD-<scenarioId>.md` — merged into `main` after review.
- Update: `docs/sprints/superpowers-checkpoint-matrix.md` — Sprint 16 row + program close-out summary.
- Update: `docs/superpowers/specs/2026-07-09-sprint-16-csa-design.md` — mark DoD complete + bump MINOR.
- Update: `docs/superpowers/specs/2026-07-09-sprints-11-16-roadmap-design.md` — mark program complete + bump MINOR.
- Close: Sprint 16 kickoff issue with retro comment + program close-out summary.

### Cross-cutting

- Optional: `docs/csa/runs/README.md` — documents the recommendation PR shape + lifecycle.

---

## Common per-task workflow (referenced by T1–T9)

Every task PR follows this skeleton.

- [ ] **Sub-step A: Branch off `main`**

```powershell
git switch main; git pull; git switch -c sprint-16/T<N>-<slug>
```

- [ ] **Sub-step B: Read the design spec section for this task**

Open [`docs/superpowers/specs/2026-07-09-sprint-16-csa-design.md`](../specs/2026-07-09-sprint-16-csa-design.md) and the anchor idea at `docs/superpowers/ideas/CSA-WhatIf-Scenario-Research-and-Catalogue.md`.

- [ ] **Sub-step C: TDD — write the failing test first**

Every code change starts with a failing unit test, notebook assertion, Playwright spec, or `az deployment ... what-if` for Bicep.

- [ ] **Sub-step D: Implement minimal code to pass the test.**

- [ ] **Sub-step E: Run the full task-level test suite**

```powershell
# Cosmos schema (against emulator or dev container)
cd data-platform/scripts/csa; pytest tests/; cd ../../..

# Notebook (pure functions)
cd data-platform/notebooks/csa; pytest tests/; cd ../../..

# App
cd apps/hcc-app-fluent; npm test; npm run test:e2e; cd ../..
```

- [ ] **Sub-step F: For `deploy`-ceiling steps — post plan + wait for `approved-to-apply`**

Applies to T1 (Cosmos Bicep), T2 (Mirroring enable), T5 (notebook publish), and any per-run Fabric REST trigger the wizard demonstrates for the first time.

- [ ] **Sub-step G: Commit + push + open PR**

```powershell
git add infra/ data-platform/ data/ apps/ docs/ .github/ agents/ AGENTS.md
git commit -m "feat(csa): T<N> <slug> — <headline>"
git push -u origin sprint-16/T<N>-<slug>
gh pr create --base main --head sprint-16/T<N>-<slug> --title "feat(csa): T<N> <slug>" --body-file <path> --label sprint-16 --label csa --label superpowers-execute
```

PR body follows [copilot-instructions.md §6](../../../.github/copilot-instructions.md) Output Contract.

- [ ] **Sub-step H: Wait for review + merge**

---

## Task 1 — T1: Cosmos DB provisioning + MCP allow-list

**Branch:** `sprint-16/T1-cosmos-bicep`  
**Depends on:** (none — can start immediately)

### Step 1.1 — MCP allow-list amendment (CODEOWNERS-gated)

- [ ] **Step 1.1.1:** Check `.github/copilot/mcp.json` for existing `cosmos-mcp` entry. If missing, add it with `purpose`, `permissions` (`data-plane read/write for the 4 CSA containers only`), and `_golden_task` pointer at the Sprint 16 CSA golden tasks.
- [ ] **Step 1.1.2:** Add the corresponding row to `AGENTS.md` §2 MCP allow-list.
- [ ] **Step 1.1.3:** Open the MCP amendment as a **separate small PR** so CODEOWNERS review is fast.

### Step 1.2 — Cosmos Bicep

- [ ] **Step 1.2.1:** `az deployment sub what-if` — expected empty diff on first pass (before Bicep exists), then non-empty after.
- [ ] **Step 1.2.2:** Write Bicep: account (`cosmos-csa-ihzhhpf-sit`), 4 containers with the vector policies + partition keys from design spec §4. Session consistency.
- [ ] **Step 1.2.3:** Managed identity assignment — the Sprint 13 agent-host's managed identity gets `Cosmos DB Built-in Data Contributor` role on the account (least privilege).
- [ ] **Step 1.2.4:** `az deployment sub what-if` — review; post as PR comment; wait for `approved-to-apply`.
- [ ] **Step 1.2.5:** `az deployment sub create` — apply.
- [ ] **Step 1.2.6:** Verify: 4 containers exist; vector index policies as specified; RU consumption is 0 idle.

**DoD:**
- [ ] `cosmos-csa-ihzhhpf-sit` provisioned with 4 containers in SIT.
- [ ] `cosmos-mcp` on the allow-list.
- [ ] `az resource show` confirms account state.

---

## Task 2 — T2: Fabric Mirroring from Cosmos to OneLake

**Branch:** `sprint-16/T2-fabric-mirroring`  
**Depends on:** T1 merged.

- Write the Fabric REST call to create the `fabric-mirrored-csa` mirrored database item pointing at the T1 Cosmos account.
- Wait ≤15 min for the initial catch-up; verify Delta tables appear in OneLake.
- Document the preview caveats: Fabric Mirroring for external Cosmos is preview; westus2 (ADR-0013 demo region) accepts previews.
- Fallback stub in `fallback-change-feed-copy.py` — kept empty until we actually need it.

**Deploy gate:** T2 has an `approved-to-apply` gate for enabling mirroring.

**DoD:**
- [ ] `fabric-mirrored-csa` item live in `ws-ihzhhpf-sit-data`.
- [ ] All 4 containers' Delta tables reachable via SQL analytics endpoint.
- [ ] Preview caveat + fallback path documented.

---

## Task 3 — T3: Cosmos schema smoke tests + response-lever seed

**Branch:** `sprint-16/T3-cosmos-schema-levers`  
**Depends on:** T1 merged.

- 4 JSON Schemas — one per container.
- `csa-seed-response-levers.py` — seeds < 100 items derived from the anchor idea's doctrine + response-lever library.
- pytest suite skipping when Cosmos creds are unset (CI can run against a preview emulator OR a dev-only Cosmos container gated behind a workflow secret).

**DoD:**
- [ ] All 4 schemas landed.
- [ ] `response-levers` container has ≥ 20 items (aim for the full ~80 from the library).
- [ ] Smoke tests green locally.

---

## Task 4 — T4: `csa-agent` full body

**Branch:** `sprint-16/T4-csa-agent-body`  
**Depends on:** T1 + T2 merged (Cosmos + mirroring). **Sprint 13 T5 (agent-host) merged.**

- Expand `agents/csa-agent/AGENT.md` to the full body per design spec §5. Retain the 8-section shape; add a "Phases" section for Prepare/Run/Evaluate/Recommend.
- Bump `agents/csa-agent/manifest.yaml`: ceiling to `deploy` (gated), new tools (`cosmos-mcp:write`, `fabric-mcp:write`), HITL-01 + HITL-04 gates.
- Expand `agents/csa-agent/golden-tasks.md` — one fixture per seeded scenario. Include RSV-surge Tier 2 canonical fixture + cyber-attack Tier 2–3 fixture.
- Update `AGENTS.md` §1 row.
- The Sprint 13 agent-host manifest loader should auto-pick up the change — no code change expected; confirm with a Container Apps redeploy trigger.

**Deploy gate:** Container Apps redeploy for agent-host manifest reload (may be automatic — verify).

**DoD:**
- [ ] `csa-agent` full body live in `agents/csa-agent/`.
- [ ] Golden tasks pass on the agent-host (integration test).
- [ ] Registry row updated.

---

## Task 5 — T5: Tier classifier + simulation notebook

**Branch:** `sprint-16/T5-tier-classifier-simulate`  
**Depends on:** T1 merged (needs a place to write `simulation-runs`).

### Step 5.1 — Tier classifier

- [ ] Codify Lage doctrine rules as `docs/adr/00XX-csa-tier-classifier-rules.md` (Accepted).
- [ ] Implement `csa-tier-classifier.py` with pure functions + version pin.
- [ ] Golden-fixture pytests covering Normallage / Besondere Lage / Ausserordentliche Lage transitions.

### Step 5.2 — Simulation notebook

- [ ] Implement `csa-simulate.py` — reads synthetic Gold capacity data, applies the shock model, writes `DC-SIM-RESULT` back to Fabric (Delta) and a `simulation-runs` document to Cosmos.
- [ ] Pure-function tests (no Spark session) for the shock model.
- [ ] Notebook lakehouse smoke run for the RSV surge canonical fixture — asserts Tier 2 + expected KPI band.

### Step 5.3 — Deploy

- [ ] `deploy-notebook.py` — publishes to `ws-ihzhhpf-sit-data`. `approved-to-apply` gate.

**DoD:**
- [ ] Tier-classifier ADR merged.
- [ ] Tier-classifier pytest green.
- [ ] `csa-simulate.py` published; RSV canonical smoke returns Tier 2.

---

## Task 6 — T6: Seed the 8 scenarios

**Branch:** `sprint-16/T6-seed-scenarios`  
**Depends on:** T1 + T3 merged.

- 8 YAML files under `data/csa/scenarios/`, one per scenario from anchor idea §6 with the full schema (`trigger`, `shockVector`, `affectedResources`, `magnitude`, `onset`, `duration`, `cascade`, `scarceCapability`, `defaultTier`, `responseLevers`, `kpis`, `hospitalRelevance`).
- `csa-seed-scenarios.py` — validates YAML against the T3 schema and upserts to Cosmos.
- Manual first run of the seed script (workflow T8 automates future upserts).

**DoD:**
- [ ] 8 YAML files in `data/csa/scenarios/`.
- [ ] `scenarios` container has 8 documents; vector index works (retrieve top-k on a canonical description).

---

## Task 7 — T7: App wizard in the Sprint 13 surface

**Branch:** `sprint-16/T7-csa-wizard`  
**Depends on:** T4 merged (agent body). **Sprint 13 T3, T5, T6, T2** merged.

- 4-step wizard component + Copilot Drawer binding per design spec §8.
- Role gate on `/main/wizards/csa` — `HCC.CrisisManager`, `HCC.OperationsLead`, `HCC.PlatformAdmin`, `HCC.SuperAdmin`.
- Data hooks calling the Sprint 13 agent-host.
- Async run pattern — Run step polls `simulation-runs` document status; user notified when Evaluate is ready.
- Playwright E2E happy path (`crisis.manager` running RSV surge → drafts recommendation PR).
- Playwright RBAC test (`demo.guest` route hidden / 403).

**DoD:**
- [ ] Wizard renders + all 4 steps functional.
- [ ] RBAC test green.
- [ ] Happy path E2E green.

---

## Task 8 — T8: GitHub delegation (issue templates + sync workflows)

**Branch:** `sprint-16/T8-github-delegation`  
**Depends on:** T3 merged (schema) + T6 merged (initial scenarios).

- `csa-scenario.yml` + `csa-run.yml` issue templates.
- `csa-scenario-sync.yml` — validates YAML against schema on merge, upserts to Cosmos.
- `csa-run-followup.yml` — closes parent run issue on `docs/csa/runs/*.md` merge.
- Labels `csa`, `csa-scenario`, `csa-recommendation`, `cosmos-provision`.

**DoD:**
- [ ] Issue templates land + templates render correctly in the UI.
- [ ] Workflows green on dispatch OR on a test scenario YAML edit.

---

## Task 9 — T9: Three MVP end-to-end runs + retro + program close-out

**Branch:** `sprint-16/T9-mvp-runs-retro`  
**Depends on:** T7 + T8 merged.

- Trigger 3 MVP-tagged runs via the wizard: **cyber-attack (F4)**, **RSV surge (F6)**, **heatwave (F8)**.
- Each yields a `docs/csa/runs/YYYY-MM-DD-<scenarioId>.md` recommendation PR — merged into `main` after review.
- Retro entry in `docs/sprints/superpowers-checkpoint-matrix.md` — Sprint 16 row + **program close-out summary** (Sprints 11–16 complete).
- Bump Sprint 16 design spec MINOR + bump the roadmap spec MINOR marking program complete.
- Close Sprint 16 kickoff issue.

**DoD:**
- [ ] 3 recommendation PRs merged into `docs/csa/runs/`.
- [ ] Program close-out summary landed in the checkpoint matrix.
- [ ] Kickoff issue closed with retro comment.

---

## Definition of Sprint 16 done (mirrors design spec §15)

- [ ] Cosmos DB provisioned via Bicep with the 4 containers.
- [ ] Fabric Mirroring live (or documented fallback in place).
- [ ] 8 seeded scenarios in Cosmos with vector search working.
- [ ] `csa-agent` completes Prepare → Run → Evaluate → Recommend for the 3 MVP-tagged scenarios end-to-end.
- [ ] App wizard rendered in Sprint 13 app with role gating verified.
- [ ] 3 recommendation PRs merged into `docs/csa/runs/`.
- [ ] Tier classifier verified against doctrine.
- [ ] `csa-scenario-sync.yml` + `csa-run-followup.yml` workflows green.
- [ ] Sprint 16 retro entry in [`docs/sprints/superpowers-checkpoint-matrix.md`](../../sprints/superpowers-checkpoint-matrix.md) + program close-out summary.
- [ ] This kickoff issue closed with a retro comment.

---

## Parallelism map (for the cloud coding agent's subagent scheduling)

```
T1 (Cosmos + MCP) ──▶ T2 (Mirroring) ──┬──▶ T4 (csa-agent body) ──▶ T7 (wizard) ──┐
                                        │                                            │
                                        ├──▶ T3 (schema + levers) ──▶ T6 (scenarios) ┼─▶ T8 (workflows) ──▶ T9 (runs + retro)
                                        │                                            │
                                        └──▶ T5 (classifier + notebook) ─────────────┘

Sprint 13 T3, T5, T6 (whiteboard, agent-host, drawer) ─▶ T4, T7
Sprint 12 T2 (MSAL claim contexts + role switcher) ─────▶ T7 role gate
Sprint 10 Gold capacity data ────────────────────────────▶ T5 notebook read
Sprint 14 T5/T6 (Evidence tab, presenter whiteboard) ────▶ optional cross-drill from T7
```

**Parallelism opportunities:**
- T3, T4, T5 can start immediately after T1 (T2 not strictly required for T3/T4/T5 development, only for E2E validation).
- T6 depends on T3 (schema).
- T7 depends on T4 (agent body) + Sprint 13 T3/T5/T6.
- T8 depends on T3 (schema) + T6 (initial scenarios).
- T9 depends on T7 + T8.

**External fan-ins:**
- **Sprint 13** — T4/T7 fan-ins for agent-host + wizard surface (issue #161 / PR #162).
- **Sprint 12** — T7 role gate (PR #159 merged).
- **Sprint 10** — T5 notebook data (already merged).
- **Sprint 14** — optional cross-drill from T7 (issue #164 / PR #165).

If Sprint 13 stalls, T7 falls back to a plain HTML wizard rendered inline (no whiteboard-card / drawer reuse). Not ideal but demoable.

---

## Self-Review

**1. Spec coverage.** Every Sprint 16 design-spec §15 DoD bullet maps to a task:
- Cosmos provisioning → T1.
- Mirroring → T2.
- 8 seeded scenarios + vector search → T3 + T6.
- `csa-agent` Prepare/Run/Evaluate/Recommend → T4.
- App wizard + role gate → T7.
- 3 recommendation PRs → T9.
- Tier classifier → T5.
- Workflows → T8.
- Retro + program close-out → T9.

**2. Placeholder scan.** No `TBD` / `TODO`. Deliberate parametrics: `<N>`, `<slug>`, ADR number `00XX` (assigned at ADR creation). One decision deferred to T1 kickoff — whether the MCP allow-list PR lands separately or bundled with the Bicep PR (recommend separate for fast CODEOWNERS review). One deferred to T3 kickoff — Cosmos emulator vs dev-only Cosmos container for CI tests.

**3. Type consistency.** Paths: `infra/modules/cosmos/`, `data-platform/scripts/csa/`, `data-platform/notebooks/csa/`, `data/csa/scenarios/`, `docs/csa/runs/`, `apps/hcc-app-fluent/src/workspaces/main/wizards/csa/`, `agents/csa-agent/`. Branch prefix `sprint-16/T<N>-<slug>`. Resource pattern `cosmos-csa-ihzhhpf-sit` per copilot-instructions §8.

**4. Approval gates.** T1 (Cosmos Bicep + MCP allow-list = 2 gates), T2 (Mirroring enable = 1), T5 (notebook publish = 1), T4 (Container Apps redeploy = maybe 1). Total Sprint 16 gates: **~4–5**.

**5. Dependencies clean.** T1 → { T2, T3, T4, T5 } fan-out. T6 → T3. T7 → T4. T8 → T3 + T6. T9 → T7 + T8. External fan-ins from Sprints 10 / 12 / 13 / 14 documented. No cycles.

**6. Program close-out.** T9 explicitly bumps the roadmap spec and the checkpoint matrix to mark Sprints 11–16 program complete.

---

## Execution Handoff

Plan complete and will be saved to `docs/superpowers/plans/2026-07-09-sprint-16-csa-plan.md`. Two execution options:

1. **GitHub Copilot cloud coding agent (recommended)** — matches Sprints 11–15 pattern. Assign the accompanying kickoff issue to Copilot in the GitHub UI. The cloud agent authors T1–T9 as separate PRs, respecting the dependency graph.
2. **Inline execution here** — the chat session executes one task at a time.

**Which approach?** — my recommendation is the cloud agent again (proven five times now).
