# Sprint 33 — Curavias BVA Agent — Plan 3: WS-B `bva.simulate` engine + agent pack

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |
| **Sprint** | Sprint 33 — Curavias BVA Agent |
| **Issue** | [#501](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/501) (WS-B); [#489](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/489) (tracker) |

> **For agentic workers:** REQUIRED SUB-SKILL — use `superpowers:subagent-driven-development` (fresh subagent + spec review + quality review per task) with `superpowers:test-driven-development`. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Build the deterministic `bva.simulate` computation engine and the `agents/bva-agent/` pack against the WS-G0 frozen contracts. The engine turns a baseline + a new-hospital delta into `ROI %`, payback, 3-year TCO, NPV, and a low/base/high band — as a `BvaSimulationResult` whose every figure is a Class-C `GroundedChunk`. **No LLM arithmetic.**

**Architecture:** A new pure-stdlib package `data-platform/bva/` mirroring `data-platform/quality/` (package + `tests/`), in the style of `data-platform/notebooks/bva/bva_kpi.py` (deterministic, documented synthetic constants, `_safe_div`). The engine is baseline-injectable: baseline defaults come from the `docs/BVA.md` ROM (CHF); in WS-A wiring they are replaced by `sm_bva` gold measures without changing the contract. Output validates against the frozen `data/synthetic/schema/bva-simulation-result-v1.schema.json`. The agent pack mirrors `agents/csa-agent/` but at side-effect ceiling **`write`** (no deploy; cloud reads only).

**Tech stack:** Python 3 stdlib only (+ `jsonschema` in tests), `pytest`. Runtime interpreter `python` (not `python3`). Markdown for the agent pack.

**Out of scope (governance close-out plan):** `AGENTS.md` §1 registry row, the new BVA ADR, and `docs/PRD.md` §7 `FR-BVA-*` / `NFR-BVA-*` promotion. This plan does **not** edit `AGENTS.md`, `docs/PRD.md`, or `docs/adr/`.

---

## File structure (created by this plan)

- `data-platform/bva/__init__.py`
- `data-platform/bva/models.py` — `BvaBaseline`, `HospitalDelta`, `InsufficientInputError` dataclasses/types.
- `data-platform/bva/archetypes.py` — synthetic acute/rehab/spitex benchmark defaults + the ROM baseline constants (CHF), each documented.
- `data-platform/bva/simulate.py` — `simulate(baseline, delta) -> dict` (a `BvaSimulationResult`), pure + deterministic.
- `data-platform/bva/tests/__init__.py`
- `data-platform/bva/tests/test_simulate.py` — deterministic formula/sensitivity/insufficient-input unit tests.
- `data-platform/bva/tests/test_output_contract.py` — engine output validates against `bva-simulation-result-v1.schema.json`.
- `evals/bva-agent/fixtures/bva-simulation-result-whatif.json` — a second fixture: the engine's own output for a canonical what-if (regression anchor).
- `agents/bva-agent/AGENT.md`, `agents/bva-agent/manifest.yaml`, `agents/bva-agent/golden-tasks.md`.

Reuse (do NOT redefine): `data/synthetic/schema/bva-simulation-result-v1.schema.json`, `data/synthetic/schema/grounded-chunk-v1.schema.json`.

---

## Deterministic model (frozen for this plan)

All figures CHF. Constants are **synthetic** (documented in `archetypes.py`); ROM band is **±30%** per `docs/BVA.md`.

Baseline (defaults from `docs/BVA.md` ROM): `oneTimeChf = 1_300_000`, `annualRunChf = 1_250_000`, `hospitals = 3`, `totalCostChf = oneTimeChf + annualRunChf`.

Archetype per-hospital benchmark defaults (synthetic; `acute` shown, `rehab`/`spitex` scaled down):

- `base_onboarding_chf`, `onboarding_per_bed_chf`
- `base_run_delta_chf`, `run_delta_per_bed_chf`
- `benefit_per_bed_chf`
- `scope_factor`: `{ "full": 1.0, "phased": 0.6, "pilot": 0.35 }`

Given a `HospitalDelta(hospital_name, archetype, beds, occupancy_target, onboarding_scope)`:

```text
onboardingOneTimeChf = (base_onboarding_chf + onboarding_per_bed_chf * beds) * scope_factor[scope]
annualRunDeltaChf    = base_run_delta_chf + run_delta_per_bed_chf * beds
annualBenefitChf     = benefit_per_bed_chf * beds * occupancy_factor      # provisional (ADR-0025)
    where occupancy_factor = occupancy_target / 0.85   # 0.85 = target OR utilisation baseline

netAnnualChf   = annualBenefitChf - annualRunDeltaChf
tco3yChf       = onboardingOneTimeChf + 3 * annualRunDeltaChf
net3yChf       = 3 * annualBenefitChf - tco3yChf
roiPct         = _safe_div(net3yChf, tco3yChf) * 100
paybackMonths  = _safe_div(onboardingOneTimeChf, netAnnualChf) * 12   # 0 if netAnnual <= 0 -> mark provisional
npvChf         = sum_{y=1..3} netAnnualChf / (1 + DISCOUNT_RATE)**y - onboardingOneTimeChf   # DISCOUNT_RATE = 0.05
sensitivity    = roiPct recomputed with annualBenefitChf * {0.7, 1.0, 1.3}  -> {low, base, high}
```

Rules: no floating-point surprises in tests — round money to 2 dp and percentages to 1 dp in the emitted result. `beds` must be a positive int and `archetype` one of the enum; otherwise raise `InsufficientInputError` (the agent's slot-filling turns this into a question). Every emitted headline figure is a Class-C `GroundedChunk` with `citation.sourceRef` naming the baseline source + the input slots, `status: "requires-validation"` for modelled benefit-derived figures, `liveness: "snapshot"` (baseline is ROM), `language` echoing the caller.

---

## Task B1: Deterministic engine + unit tests

**Files:** create `data-platform/bva/{__init__.py,models.py,archetypes.py,simulate.py}`, `data-platform/bva/tests/{__init__.py,test_simulate.py}`.

- [ ] **Step 1 (TDD):** write `test_simulate.py` FIRST covering: a canonical acute what-if (assert exact rounded ROI/payback/TCO/NPV against hand-computed values), the low<base<high sensitivity ordering, `scope_factor` effect, and `InsufficientInputError` on `beds<=0` / bad archetype / missing archetype. Run it; confirm it FAILS (module missing).
- [ ] **Step 2:** implement `models.py`, `archetypes.py`, `simulate.py` per the model above. `simulate()` returns a dict shaped as `BvaSimulationResult` (do NOT validate schema here — that is B2). Pure stdlib, `_safe_div` like `bva_kpi.py`.
- [ ] **Step 3:** run `python -m pytest data-platform/bva -v`; all green.
- [ ] **Step 4:** commit (`feat(bva): deterministic bva.simulate engine + unit tests (WS-B)`), hook bypass, trailers.

## Task B2: Output-contract conformance + regression fixture

**Files:** create `data-platform/bva/tests/test_output_contract.py`, `evals/bva-agent/fixtures/bva-simulation-result-whatif.json`.

- [ ] **Step 1 (TDD):** write `test_output_contract.py` that calls `simulate(...)` for the canonical what-if and `jsonschema.validate`s the result against `bva-simulation-result-v1.schema.json`; also assert `currency == "CHF"`, `len(chunks) >= 1`, every chunk `classId == "C"` with non-empty `citation.sourceRef`. Run; confirm it fails if the engine omits any required field.
- [ ] **Step 2:** make the engine output complete; serialize the canonical what-if result to `evals/bva-agent/fixtures/bva-simulation-result-whatif.json` (ASCII-safe, "Hopital" no accent) so `evals/bva-agent/tests/test_bva_schema_conformance.py` still passes and this becomes a regression anchor. Extend that existing test only if needed to include the new fixture (keep its style).
- [ ] **Step 3:** run `python -m pytest data-platform/bva evals/bva-agent -v`; all green.
- [ ] **Step 4:** commit (`test(bva): engine output conforms to bva-simulation-result-v1 (WS-B)`).

## Task B3: `agents/bva-agent/` pack

**Files:** create `agents/bva-agent/{AGENT.md,manifest.yaml,golden-tasks.md}`.

- [ ] **Step 1:** `manifest.yaml` mirroring `agents/csa-agent/manifest.yaml` but: `agent: bva-agent`, `runtime: agent-host`, `ceiling: write`; `mcpTools` = github-mcp (get-issue, add-issue-comment, create-pull-request; write), fabric-mcp (query; **read**), cosmos-mcp (read-item, upsert-item; write — opportunity SoR); `grounding` = `fabric:gold-bva`, `cosmos:opportunities`, `adr:0025-bva-kpi-catalog`; `goldenTasksRef: ./golden-tasks.md`; no HITL deploy gate.
- [ ] **Step 2:** `AGENT.md` with the fixed structure (Identity, Scope, Tools, Refusal Rules, Output Contract, Confirmation Rules) mirroring `agents/csa-agent/AGENT.md`. Identity = read-only BVA/ROI-TCO advisory agent; advisory-only, never mutates cloud spend/resources, never auto-advances an opportunity past `qualified`; does slot-filling then calls `bva.simulate`; narrates cited `GroundedChunk` results DE/EN. Version header per §9.
- [ ] **Step 3:** `golden-tasks.md` (front-matter `agent: bva-agent`, `requirement: FR-BVA-001, FR-BVA-002`) with ≥4 fixtures: (a) happy-path baseline TCO-to-date query, (b) new-hospital what-if (slot-fill → `bva.simulate` → cited result), (c) insufficient-input refusal (missing beds → asks, does not guess), (d) spend-mutation refusal (a "reduce our Azure spend" ask → refuses; read-only). Each: Input issue body / Expected MCP tool calls / Expected PR/comment shape / Forbidden behaviors.
- [ ] **Step 4:** doc gates on the two markdown files: `python scripts/lint/check_mojibake.py <files>` (OK) + `npx --yes markdownlint-cli2 "agents/bva-agent/*.md"` (0 issues). Commit (`feat(bva): agents/bva-agent pack - engine-backed advisory agent (WS-B)`).

## Task B4: Final verification + PR

- [ ] **Step 1:** `python -m pytest data-platform/bva evals/bva-agent -v` green; mojibake + markdownlint clean on all new markdown.
- [ ] **Step 2:** confirm no edits to `AGENTS.md`, `docs/PRD.md`, `docs/adr/`, `.github/copilot/mcp.json` (`git show --stat`); confirm `manifest.yaml` uses only allow-listed MCP servers (github-mcp, fabric-mcp, cosmos-mcp — all already present).
- [ ] **Step 3:** open one squash PR (branch `sprint-33/ws-b-engine`) → issue #501 / tracker #489 with the PR Output Contract. **Never self-merge; human merges on green.**

---

## Definition of Done (Plan 3 / WS-B)

- [ ] `data-platform/bva/` engine + deterministic unit tests green (`python -m pytest data-platform/bva -v`).
- [ ] Engine output validates against the frozen `bva-simulation-result-v1` schema; regression fixture committed; `evals/bva-agent` green.
- [ ] `agents/bva-agent/` pack (AGENT.md + manifest.yaml + golden-tasks.md) with happy + what-if + insufficient-input refusal + spend-mutation refusal fixtures; docs gate-clean.
- [ ] One small squash PR linked to #501/#489; human-merged on green. Registry row + ADR + PRD deferred to the governance close-out plan.
