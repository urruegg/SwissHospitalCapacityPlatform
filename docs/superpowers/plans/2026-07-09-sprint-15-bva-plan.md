# Sprint 15 — BVA Evidence Data Product (synthetic seed) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended — one subagent per task) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the BVA (Business Value Assessment) live data product on **synthetic FOCUS-shaped** consumption data per the design spec — from a nightly generator through the Fabric medallion into a semantic model with 20+ headline KPIs, five C-suite Power BI pages with RLS, and a BVA card cluster on the Sprint 14 presenter whiteboard.

**Architecture:** Sequential-ish with three fan-in points from Sprint 12 (adoption telemetry) and Sprint 14 (whiteboard framework + Evidence tab). Reuses Sprint 14's whiteboard `CardRegistry` — Sprint 15 adds 3 new BVA card types; the framework is **not** forked. Design contract in [`docs/superpowers/specs/2026-07-09-sprint-15-bva-design.md`](../specs/2026-07-09-sprint-15-bva-design.md). ROM baseline in [`docs/BVA.md`](../../BVA.md).

**Tech Stack:** Python 3.11+ (`bva-synth-focus.py` generator with reproducible seed + pytest + pandas + pyarrow for Parquet), YAML (KPI catalog), GitHub Actions workflow, Fabric notebooks (PySpark) for the medallion, Fabric semantic model TMDL edits, Power BI report authoring (`powerbi-report-authoring` skill), React + TypeScript (3 whiteboard card types), Playwright (E2E + RLS regression), optional Python (application-hosted `bva-agent` stretch loaded by Sprint 13 agent-host).

---

## Prerequisites (verify before starting)

- [ ] On `main`, clean: `git switch main; git pull`.
- [ ] Sprint 15 design spec merged at v1.1.0.
- [ ] **Sprint 12 T5/T6** (adoption telemetry emission from sign-in events) merged — blocks T4 join. Track via issue #158 / PR #159.
- [ ] **Sprint 14 T4** (semantic model extension pattern) merged — reference for T5 measures. Track via issue #164.
- [ ] **Sprint 14 T5/T6** (whiteboard framework + Evidence tab) merged — blocks T7 cards. Track via issue #164.
- [ ] Fabric capacity `fabricihzhhpfsit` state = **Active** (needed for T3 pipeline + T5 semantic model publish + T6 Power BI report publish).
- [ ] Fabric workspace `ws-ihzhhpf-sit-data` (id `f3af9733-9503-4e92-98f9-a901d96f1c87`) + lakehouse `lh_ihzhhpf_sit` (id `30594c20-46ba-40ea-91fa-4701b105e0b9`) reachable.
- [ ] `az` CLI authenticated to SIT tenant per ADR-0012.
- [ ] Python 3.11+ available.
- [ ] `gh` CLI authenticated.
- [ ] Explicit go-ahead from @urruegg in the Sprint 15 kickoff issue thread.

---

## File Structure

Files created or modified across the eight tasks (T8 is the optional stretch).

### T1 — Synthetic FOCUS-shaped generator

- Create: `data-platform/scripts/bva-synth-focus.py` — deterministic (`--seed` arg) 90-day daily-partitioned Parquet generator.
- Create: `data-platform/scripts/pyproject.toml` (or extend existing) — dev dependencies (`pytest`, `pandas`, `pyarrow`, `python-dateutil`).
- Create: `data-platform/scripts/tests/test_bva_synth_focus.py` — determinism + FOCUS-column-shape + cost-calibration (±15% of CHF 760k/yr baseline) tests.
- Create: `data-platform/scripts/tests/fixtures/focus_schema.json` — FOCUS column contract used by the shape validator.
- Create: `data-platform/scripts/README-bva.md` — generator invocation + tuning notes.
- Modify: `.github/CODEOWNERS` — add `/data-platform/scripts/bva-synth-focus.py` → @urruegg.

### T2 — BVA sim-refresh workflow

- Create: `.github/workflows/bva-sim-refresh.yml` — nightly schedule + `workflow_dispatch`; runs generator, uploads to `Bronze/consumption/` in the lakehouse, triggers Fabric pipeline.
- Create: `data-platform/scripts/bva-upload-bronze.py` — small helper that uploads Parquet to OneLake (via `fabric-mcp` or direct REST).
- Create: `.github/ISSUE_TEMPLATE/bva-kpi.yml` — issue template for KPI additions.
- Create: `.github/ISSUE_TEMPLATE/bva-report-page.yml` — issue template for report-page work.
- Create: labels via `gh label create` — `bva`, `focus-sim`, `dax`, `rls`.

### T3 — Fabric medallion (Bronze → Silver → Gold BVA schema)

- Create: `data-platform/notebooks/bva/{ingest_bronze_consumption,ingest_bronze_adoption,build_silver_bva,build_gold_bva_dims,build_gold_bva_facts}.py`.
- Create: `data-platform/notebooks/bva/README.md`.
- Create: `data-platform/notebooks/bva/tests/` — pytest for pure-function transforms + a small lakehouse smoke test.
- Create: `data-platform/scripts/bva/deploy-pipeline.py` — publishes notebooks + wires the daily Fabric pipeline schedule.
- Create: `docs/data-platform/bva-gold-schema.md` — star schema doc (mirrors design spec §5).

**Naming:** snake_case + gold-schema prefix (`gold.fact_azure_consumption`, `gold.fact_value_realization`, `gold.dim_service`, etc.) per PR #153 reconciliation.

### T4 — Adoption-telemetry join

- Modify: `data-platform/notebooks/bva/build_gold_bva_facts.py` — join Sprint 12 adoption telemetry (`Bronze/adoption/*.json`) into `gold.fact_value_realization`.
- Create: `data-platform/notebooks/bva/tests/test_adoption_join.py` — row count + user coverage assertions against synthetic adoption fixture.
- Create: `data-platform/notebooks/bva/tests/fixtures/adoption_sample.json` — small deterministic fixture for pytest.
- Document: cross-reference to Sprint 12 telemetry emission source.

### T5 — Direct Lake semantic model + 20+ KPI measures

- Modify: `data-platform/reports/capacity-dashboard.SemanticModel/` — extend the existing PBIP semantic model with BVA facts/dims + measures per design spec §5–§6. (Design spec calls this a shared semantic model with the evidence + operational schemas.)
- Create OR modify: DAX measures — one per KPI in §6. Each measure has a target constant + cadence tag + RLS profile in its display folder.
- Create: `data-platform/reports/capacity-dashboard.SemanticModel/README-bva.md` — measure catalog + calibration notes.
- Create: `data-platform/reports/tests/bva-measure-tests.md` — DAX golden-value regression tests.
- Create: `docs/adr/00XX-bva-kpi-catalog.md` — codifies the 20+ headline KPIs + their formulas as an ADR (Accepted).

**Approval:** semantic-model publish is `deploy`-ceiling. `approved-to-apply` gate.

### T6 — Five C-suite Power BI pages + RLS + Board-summary

- Create: `data-platform/reports/bva-boardroom.Report/` (or extend `capacity-dashboard.Report/`) — 5 personalised landing pages: **CEO**, **CFO**, **CIO**, **COO**, **CTO** + a shared **Board-summary**.
- Create: `data-platform/reports/bva-boardroom.Report/definition/rls-roles.md` — role catalog + expected filter DAX.
- Create: `data-platform/reports/bva-boardroom.Report/README.md` — page layout, theme reuse (Helvion tokens from Power BI M1), audit posture.
- Create: `data-platform/reports/tests/bva-rls-test-plan.md` — expected row counts per persona × hospital.

**Uses skills:** `powerbi-report-authoring` + `powerbi-optimization` per design spec §10.

**Approval:** report publish + RLS role assignment are both `deploy`-ceiling. `approved-to-apply` gate.

### T7 — Three BVA card types on the presenter whiteboard

- Create: `apps/hcc-app-fluent/src/cards/bva/{HeadlineKpiCard,PlanVsActualCard,TrendCard}.tsx` — 3 new card types per design spec §7.
- Modify: `apps/hcc-app-fluent/src/whiteboard/CardRegistry.tsx` — register 3 BVA card types.
- Create: `apps/hcc-app-fluent/src/data/bva/{useHeadlineKpi,usePlanVsActual,useTrend}.ts` — SWR/React Query hooks that call the semantic model via the Direct Lake / XMLA pattern used by the operational + evidence whiteboards.
- Modify: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/evidence/EvidenceTab.tsx` — add "BVA" filter/tab per design spec §7. If Sprint 14 Evidence tab isn't yet merged, the tab-level filter change slides into T7's follow-up; card types themselves land regardless.
- Create: `apps/hcc-app-fluent/tests/unit/cards/bva/*.test.tsx` — one per card type. Each card MUST render source + `asOf` provenance (mirrors Sprint 14 rule).
- Create: `apps/hcc-app-fluent/tests/e2e/backstage-evidence-bva.spec.ts` — Playwright: sign in as CFO persona → Evidence tab → BVA filter → asserts CEO/CFO/CIO/COO/CTO card cluster visible + drill-in opens the corresponding Power BI page.

### T8 — Stretch: `bva-agent` (application-hosted per ADR-0008)

**Only start if T1–T7 land with ≥3 days of buffer in the sprint window.** Otherwise record explicit "not attempted" note in the retro per design spec §16.

- Create: `agents/bva-agent/AGENT.md` — 8-section prompt file (Identity, Scope, Tools, Refusal Rules, Output Contract, Confirmation Rules, HITL Gates, Provenance).
- Create: `agents/bva-agent/manifest.yaml` — runtime manifest matching Sprint 11 shape: `agent`, `version`, `runtime: agent-host`, `modelDeploymentRef`, `systemPromptRef`, `refusalRulesRef`, `mcpTools` (`github-mcp` write, `fabric-mcp` read), `hitl.gates`, `grounding`, `goldenTasksRef`.
- Create: `agents/bva-agent/golden-tasks.md` — happy-path + refusal fixtures (speculative-claim refusal test).
- Modify: `AGENTS.md` — add `bva-agent` registry row per §1 shape.
- Create: `.github/workflows/bva-monthly-boardpack.yml` — 1st business day of each month; opens issue that triggers the agent-host.
- Modify: Sprint 13 agent-host manifest loader — should already pick up the new pack automatically; confirm.

### T9 — Retro + checkpoint matrix

- Update: `docs/sprints/superpowers-checkpoint-matrix.md` — Sprint 15 row.
- Update: `docs/superpowers/specs/2026-07-09-sprint-15-bva-design.md` — mark DoD complete; bump MINOR.
- Close: Sprint 15 kickoff issue with retro comment.

### Cross-cutting

- No changes to `.github/copilot/mcp.json` expected (T8 uses existing `github-mcp` + `fabric-mcp`).

---

## Common per-task workflow (referenced by T1–T9)

Every task PR follows this skeleton.

- [ ] **Sub-step A: Branch off `main`**

```powershell
git switch main; git pull; git switch -c sprint-15/T<N>-<slug>
```

- [ ] **Sub-step B: Read the design spec section for this task**

Open [`docs/superpowers/specs/2026-07-09-sprint-15-bva-design.md`](../specs/2026-07-09-sprint-15-bva-design.md), the anchor idea at `docs/superpowers/ideas/Swiss-Hospital-Capacity-Live-Business-Value-Assessment-(BVA)-Dashboard.md`, and the ROM baseline in [`docs/BVA.md`](../../BVA.md) v1.0.1.

- [ ] **Sub-step C: TDD — write the failing test first**

Every code change starts with a failing unit test, notebook assertion, DAX golden test, or Playwright spec.

- [ ] **Sub-step D: Implement minimal code to pass the test**

Prefer smaller files with one clear responsibility.

- [ ] **Sub-step E: Run the full task-level test suite**

```powershell
# Generator
cd data-platform/scripts; pytest tests/; cd ../..

# Notebooks (pure functions)
cd data-platform/notebooks/bva; pytest tests/; cd ../../..

# App (Sprint 13/14 workflows apply)
cd apps/hcc-app-fluent; npm test; npm run test:e2e; cd ../..
```

- [ ] **Sub-step F: For `deploy`-ceiling steps — post plan + wait for `approved-to-apply`**

Applies to T3 (Fabric pipeline publish), T5 (semantic model publish), T6 (Power BI report + RLS role assignment), and T8 (bva-agent Container Apps redeploy — if attempted).

- [ ] **Sub-step G: Commit + push + open PR**

```powershell
git add data-platform/ apps/ docs/ .github/ agents/
git commit -m "feat(bva): T<N> <slug> — <headline>"
git push -u origin sprint-15/T<N>-<slug>
gh pr create --base main --head sprint-15/T<N>-<slug> --title "feat(bva): T<N> <slug>" --body-file <path> --label sprint-15 --label bva --label superpowers-execute
```

PR body follows [copilot-instructions.md §6](../../../.github/copilot-instructions.md) Output Contract.

- [ ] **Sub-step H: Wait for review + merge**

---

## Task 1 — T1: Synthetic FOCUS-shaped generator

**Branch:** `sprint-15/T1-focus-sim`  
**Depends on:** (none — can start immediately)

### Step 1.1 — Scaffold + failing tests

- [ ] **Step 1.1.1: Branch + init.**
- [ ] **Step 1.1.2: Create `focus_schema.json`** with the FOCUS columns from design spec §4 + custom `x_env`, `x_hospital`, `x_capability`.
- [ ] **Step 1.1.3: Write failing pytests:**
  - `test_deterministic_seed` — same `--seed` → identical Parquet bytes.
  - `test_focus_shape` — output validates against `focus_schema.json`.
  - `test_calibration` — annualised total within ±15% of CHF 760k baseline.
  - `test_cost_distribution` — Fabric + Cosmos + Container Apps dominate the top-3 share (matches Sprint 14 BOM).
  - `test_tag_completeness` — every row has non-null `x_env`, `x_hospital`, `x_capability`.

### Step 1.2 — Implement generator

- [ ] **Step 1.2.1: `bva-synth-focus.py`** — CLI args: `--seed`, `--days`, `--out-dir`. Emits daily Parquet at `out-dir/BillingPeriod=YYYY-MM/ChargePeriodStart=YYYY-MM-DD/part-00000.parquet`.
- [ ] **Step 1.2.2: Cost distribution model** — weighted per Sprint 14 BOM + design spec §4 §6 (Fabric ~40%, Cosmos ~10%, Container Apps ~15%, Storage ~5%, Foundry ~15%, remainder split among Monitor/Log Analytics/App Insights/Service Bus/Key Vault/Redis).
- [ ] **Step 1.2.3: Noise model** — ±15% per-row Gaussian around plan value.
- [ ] **Step 1.2.4: Tag distribution** — 3 hospitals + Aggregated; 3 envs (dev/sit/prod); 6 capabilities (BMCA/OOA/DCA/ORSA/SBA/CSA).

### Step 1.3 — PR

- [ ] Commit, push, open PR. Labels `sprint-15`, `bva`, `focus-sim`, `superpowers-execute`.

**DoD:**
- [ ] Generator tests all green.
- [ ] `python -m data_platform.scripts.bva_synth_focus --seed 42 --days 90 --out-dir /tmp/bva` produces 90 daily partitions.
- [ ] Total cost within ±15% of ROM baseline.

---

## Task 2 — T2: BVA sim-refresh workflow

**Branch:** `sprint-15/T2-sim-refresh-workflow`  
**Depends on:** T1 merged.

- Nightly workflow (`cron: '0 2 * * *'`) + `workflow_dispatch`.
- Steps: checkout → setup Python → run generator with `--seed $(date +%Y%j)` → upload to lakehouse `Bronze/consumption/` → trigger Fabric pipeline (T3 wires this).
- Issue templates `bva-kpi.yml` + `bva-report-page.yml` land here.
- Labels created via `gh label create`.

**Tests:** dry-run the workflow via `workflow_dispatch` — asserts artefacts land in Bronze without error.

**DoD:**
- [ ] Workflow runs green via `workflow_dispatch`.
- [ ] Bronze partition for today's date visible after run.
- [ ] Labels + issue templates live.

---

## Task 3 — T3: Fabric medallion (Bronze → Silver → Gold BVA schema)

**Branch:** `sprint-15/T3-bva-medallion`  
**Depends on:** T2 merged (needs real Bronze data).

Follow the [Common per-task workflow](#common-per-task-workflow-referenced-by-t1t9). Task-specific specifics:

- 5 notebooks per medallion layer (see File Structure T3).
- Silver preserves provenance (`_ingest_utc`, `_source_seed`).
- Gold star schema per design spec §5 — snake_case naming per PR #153 reconciliation.
- Fabric pipeline runs daily at 03:00 CET (after T2's 02:00 refresh).
- Uses `spark-authoring` + `e2e-medallion-architecture` skills.

**Deploy gate:** Fabric pipeline publish is `deploy`-ceiling.

**DoD:**
- [ ] All 5 notebooks live + pytest passing on pure-function transforms.
- [ ] Fabric pipeline published to SIT and one successful end-to-end run.
- [ ] Gold tables populated for 90-day slice.

---

## Task 4 — T4: Adoption-telemetry join

**Branch:** `sprint-15/T4-adoption-join`  
**Depends on:** T3 merged + **Sprint 12 T5/T6** (adoption emission).

- Extend `build_gold_bva_facts.py` to join `Bronze/adoption/*.json` into `gold.fact_value_realization`.
- Row-count + user-coverage regression test against synthetic adoption fixture.
- If Sprint 12 T5/T6 not yet merged: backfill 30 days of synthetic sign-ins per design spec §14 mitigation. Document the switchover point.

**DoD:**
- [ ] Adoption join returns non-empty result on real Sprint 12 emission OR synthetic backfill.
- [ ] Coverage regression test green.

---

## Task 5 — T5: Direct Lake semantic model + 20+ KPI measures

**Branch:** `sprint-15/T5-semantic-model-kpis`  
**Depends on:** T3 merged (Gold tables exist). Reference Sprint 14 T4 patterns.

- Extend `capacity-dashboard.SemanticModel/` with BVA facts + dims + relationships + 20+ measures.
- KPI catalog codified as ADR `docs/adr/00XX-bva-kpi-catalog.md` (Accepted).
- DAX golden-value tests per measure — byte-stable output on fixed synthetic seed.
- Uses `fabric-semantic-model-authoring` + `powerbi-optimization` skills.

**Deploy gate:** semantic model publish (`approved-to-apply`).

**DoD:**
- [ ] All 20+ measures return expected values on golden inputs.
- [ ] KPI catalog ADR merged.
- [ ] Semantic model published to SIT.

---

## Task 6 — T6: Five C-suite Power BI pages + RLS + Board-summary

**Branch:** `sprint-15/T6-boardroom-report`  
**Depends on:** T5 merged.

- 5 landing pages (CEO/CFO/CIO/COO/CTO) + shared Board-summary.
- RLS roles per design spec §8 — CEO/CFO/CIO/COO/CTO landing routing, hospital filter, env filter, SuperAdmin bypass, GuestReadOnly Aggregated-only.
- RLS test plan in `bva-rls-test-plan.md` — expected row counts per persona × hospital.
- Uses `powerbi-report-authoring` + `powerbi-optimization` skills.
- Reuses Helvion theme tokens from Power BI M1 (PR #152).

**Deploy gates:** report publish + RLS role assignment (`approved-to-apply`).

**DoD:**
- [ ] 5 C-suite pages + Board-summary rendered.
- [ ] RLS enforced per persona.
- [ ] `demo.guest` sees Aggregated + Board-summary only.
- [ ] Each landing shows the headline KPI per design spec §6.

---

## Task 7 — T7: Three BVA card types on the presenter whiteboard

**Branch:** `sprint-15/T7-bva-cards`  
**Depends on:** T5 merged (measures exist). **Sprint 14 T5/T6 merged** (whiteboard framework + Evidence tab).

- 3 new card types under `apps/hcc-app-fluent/src/cards/bva/`.
- Register in Sprint 14 `CardRegistry` — extension not fork.
- Add BVA filter/tab in Sprint 14 `EvidenceTab.tsx`.
- Data hooks under `apps/hcc-app-fluent/src/data/bva/` — same DAX-over-XMLA / Direct Lake REST pattern the operational + evidence whiteboards use.
- Provenance rule inherited from Sprint 14: every card renders source + `asOf`; missing = visible error state.
- Playwright E2E: CFO persona sees CFO landing → BVA filter → CEO/CFO/CIO/COO/CTO card cluster → drill-in opens Power BI page.

**Fallback:** if Sprint 14 T5/T6 not merged, cards render in a plain Power BI embed fallback (design spec §14 mitigation).

**DoD:**
- [ ] 3 BVA card types render with provenance.
- [ ] BVA filter/tab operational.
- [ ] Playwright E2E green.

---

## Task 8 — T8 (STRETCH): `bva-agent` application-hosted per ADR-0008

**Branch:** `sprint-15/T8-bva-agent`  
**Depends on:** T5 + T6 merged. **Sprint 13 T5** (agent-host) merged.

**Only attempt if T1–T7 land with ≥3 days sprint buffer.** Otherwise record "not attempted" in retro.

- 8-section `AGENT.md` matching Sprint 11 pack shape.
- `manifest.yaml` — `runtime: agent-host`, `modelDeploymentRef: sprint11-chat`, `mcpTools: [github-mcp:write, fabric-mcp:read]`, `hitl.gates: [HITL-04]` (draft-PR review gate).
- Golden tasks: happy path (draft board pack for last month) + refusal (speculative claim without KPI grounding).
- Registry row in `AGENTS.md`.
- Workflow `bva-monthly-boardpack.yml` — 1st business day monthly cron; opens issue that triggers the agent-host.
- Confirm the Sprint 13 agent-host loader auto-picks up the new manifest (no code change expected).

**Deploy gate:** Container Apps redeploy for agent-host to reload manifests (may be automatic — verify).

**DoD (only if attempted):**
- [ ] `bva-agent` registered in AGENTS.md.
- [ ] Agent drafts one board pack PR against a synthetic month.
- [ ] Refusal test green.

**DoD (if skipped):**
- [ ] Retro entry documents "not attempted" with reason.

---

## Task 9 — T9: Retro + checkpoint matrix

**Branch:** `sprint-15/T9-retro`  
**Depends on:** T7 merged (and T8 landed or explicitly skipped).

- Update `docs/sprints/superpowers-checkpoint-matrix.md` — Sprint 15 row.
- Update `docs/superpowers/specs/2026-07-09-sprint-15-bva-design.md` — mark DoD complete + bump MINOR.
- Close Sprint 15 kickoff issue with retro comment.

**DoD:**
- [ ] Checkpoint matrix entry landed.
- [ ] Design spec DoD checked off.
- [ ] Kickoff issue closed.

---

## Definition of Sprint 15 done (mirrors design spec §16)

- [ ] `bva-sim-refresh.yml` green nightly.
- [ ] Medallion + semantic model produce all headline KPIs from KPI table §6.
- [ ] Five C-suite Power BI pages rendered with RLS verified.
- [ ] BVA card cluster visible on Sprint 14 presenter whiteboard (BVA filter/tab).
- [ ] FOCUS shape validation green.
- [ ] Cost calibration within ±15% of ROM baseline (CHF 760k/yr).
- [ ] Stretch `bva-agent` drafts one board pack PR OR explicit "not attempted" note in retro.
- [ ] Sprint 15 retro entry in [`docs/sprints/superpowers-checkpoint-matrix.md`](../../sprints/superpowers-checkpoint-matrix.md).

---

## Parallelism map (for the cloud coding agent's subagent scheduling)

```text
T1 (generator) ──▶ T2 (workflow) ──▶ T3 (medallion) ──┬──▶ T4 (adoption join) ──┐
                                                       │                          │
                                                       └──▶ T5 (KPIs) ──▶ T6 (Power BI) ──┐
                                                                                            │
                                                                          T7 (cards) ◀─────┤
                                                                                            │
                                                                     T8 (stretch bva-agent) │
                                                                                            │
                                                                     T9 (retro) ◀──────────┘

Sprint 12 T5/T6 (adoption emission) ────────────▶ T4
Sprint 14 T5/T6 (whiteboard + Evidence tab) ────▶ T7
Sprint 13 T5 (agent-host) ──────────────────────▶ T8 (stretch)
```

**Parallelism opportunities:**
- T4 and T5 can run in parallel after T3 (they touch different modules of the same notebook stack).
- T7 can start speculatively against mocked measure outputs once Sprint 14 T5/T6 lands, but full completion needs T5+T6.
- T8 (stretch) can begin any time after T6, gated on the T1–T7 buffer criterion.

**Sprint 12/13/14 dependencies flagged (per task):**
- T4 blocks on Sprint 12 T5/T6 (adoption emission).
- T7 blocks on Sprint 14 T5/T6 (whiteboard framework + Evidence tab).
- T8 blocks on Sprint 13 T5 (agent-host).

If Sprint 14 stalls, T7 falls back to Power BI embed rendering per design spec §14.

---

## Self-Review

**1. Spec coverage.** Every Sprint 15 design-spec §16 DoD bullet maps to a task:
- `bva-sim-refresh.yml` nightly → T2.
- Medallion + KPIs → T3 + T5.
- 5 C-suite pages + RLS → T6.
- BVA card cluster on whiteboard → T7.
- FOCUS shape validation → T1.
- Cost calibration ±15% → T1.
- Stretch bva-agent → T8.
- Retro → T9.

**2. Placeholder scan.** No `TBD` / `TODO`. Deliberate parametrics: `<N>`, `<slug>`, ADR number `00XX` (assigned at ADR creation). One decision deferred to T5 kickoff — whether BVA measures share the operational/evidence semantic model or split into a dedicated BVA model (design spec §5 implies shared; task kickoff to confirm no perf regression).

**3. Type consistency.** Paths: `data-platform/scripts/`, `data-platform/notebooks/bva/`, `data-platform/reports/capacity-dashboard.SemanticModel/`, `data-platform/reports/bva-boardroom.Report/`, `apps/hcc-app-fluent/src/cards/bva/`, `agents/bva-agent/` (stretch). Branch prefix `sprint-15/T<N>-<slug>`.

**4. Approval gates.** T3 (Fabric pipeline) + T5 (semantic model) + T6 (report + RLS assignment) each carry one `approved-to-apply` gate. T8 optional agent-host redeploy. Total Sprint 15 SIT gates: **~3 (+1 stretch)**.

**5. Dependencies clean.** T1 → T2 → T3 → { T4, T5 } → T6 → T7 → T9. T8 optional between T6 and T9. External fan-ins from Sprint 12 (T4), Sprint 14 (T7), Sprint 13 (T8 stretch). No cycles. Fallback documented for Sprint 14 delay.

**6. Provenance + RLS.** Enforced at generator level (`_source_seed` provenance), semantic-model level (RLS DAX roles), Power BI report level (persona routing), whiteboard card level (source + asOf), and Playwright E2E level (row-count + persona regression).

---

## Execution Handoff

Plan complete and will be saved to `docs/superpowers/plans/2026-07-09-sprint-15-bva-plan.md`. Two execution options:

1. **GitHub Copilot cloud coding agent (recommended)** — matches Sprint 11 / 12 / 13 / 14 pattern. Assign the accompanying kickoff issue to Copilot in the GitHub UI. The cloud agent authors T1–T9 as separate PRs, respecting the dependency graph.
2. **Inline execution here** — the chat session executes one task at a time.

**Which approach?** — my recommendation is the cloud agent again (proven four times: PR #149, #152, #156, #159 completed; #162, #165 in flight).
