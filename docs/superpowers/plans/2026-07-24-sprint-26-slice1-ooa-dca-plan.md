# Sprint 26 — Slice 1 (OOA→DCA) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL — implement task-by-task with
> `superpowers:test-driven-development` (tests first) and
> `superpowers:verification-before-completion` (no completion claim without fresh
> command evidence). Steps use checkbox (`- [ ]`) syntax.

**Issue:** #335 · **Branch:** `sprint-26/slice1-ooa-dca` (off `main`) · **Lanes:** Data / AI /
Experience / Governance · **Design SoT:**
[`docs/superpowers/specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md`](../specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md)
§3.1–§3.5, §4 (WS-B/C/D), §5 Slice 1.

---

## Goal

Prove the 5-beat actionable-insight pattern end-to-end for **one** golden thread
(**Medicine A / 102% / 72h**, OOA→DCA) as one human-reviewed squash PR: lever catalog +
deterministic impact tool + barrier model (WS-B), Cosmos `proposed_actions`/`plans`
container definitions + a pure coordination runtime with HITL recompute + handoff +
golden-thread sync (WS-C), and the `DC-INSIGHT-v1` Data-Agent contract + OOA/DCA agent
instruction upgrades + ADR/PRD + golden tasks (WS-D). Fan-out to the other 4 roles is a
later run.

## Scope — in / out

**In (this PR):**
1. `DC-INSIGHT-v1` JSON-schema contract (5-beat tuple) + conformance test.
2. Lever catalog: `lever.schema.json` + 6 role YAMLs (OOA + DCA fully specified; other 4 stubbed) + validation test.
3. `compute_expected_impact(lever_id, params)` — pure deterministic tool over the WS-A gold forecast/driver data + golden-fixture unit tests. **Never an LLM estimate.**
4. DCA barrier model — runtime-derived pure function (ranked barriers) + unit tests.
5. Cosmos `proposed_actions` + `plans` **container definitions** in `csa.bicep` (+ README). IaC only; no live deploy.
6. Coordination runtime — pure module: build Plan/CapacityEpisode, proposed-action → HITL approve → deterministic recompute (102%→94%) → append `forecast_deltas` + update `current` → OOA→DCA handoff. In-memory-store unit tests + seed scripts.
7. `da_hospital_capacity` contract upgraded to `DC-INSIGHT-v1` (signal + understanding + provenance) keeping RLS + PHI-refuse.
8. OOA + DCA agent instruction upgrades (5-beat assembly) + golden tasks (happy / failure / PHI-refuse).
9. ADR-0040 (descriptive→prescriptive + runtime decision store) + PRD FR/NFR rows + §7 traceability.
10. Doc updates + SemVer bumps (`docs/DATA.md`, `docs/AI.md`, AGENTS.md note as needed).

**Out (later slices / gated):**
- Live Cosmos/Foundry `apply` — deferred behind `approved-to-apply` (AGENTS.md §4).
- New semantic-model measures/relationships (would force verify-gate rebaseline) — impact tool reads gold data instead.
- Fan-out roles BMCA/ORSA/SBA/CSA.

## Architecture decisions (Slice 1)

- **Impact tool reads WS-A gold** (`gold.fact_occupancy_forecast`, `gold.fact_forecast_driver`) via a pure function fed fixtures offline; the Fabric `run()` I/O is `# pragma: no cover`. Keeps the semantic-model verify-gate untouched.
- **Barrier model runtime-derived** (design open item Q): pure `derive_barriers(candidates)` — no new gold table, no semantic-model change.
- **Coordination runtime is storage-agnostic**: a `Store` protocol with an in-memory impl for tests; the Cosmos impl is thin and gated. HITL recompute calls `compute_expected_impact` (single source of truth for deltas).
- **DC-INSIGHT-v1 envelope** mirrors existing `dc-*-v1` schemas (draft-07, `additionalProperties:false`).

## Hard constraints (every task)

- Runtime **`python`**, not `python3`.
- **Commit hooks disabled** (Windows mojibake false-fail): `git -c core.hooksPath=/dev/null commit -m "..."` after manual `python scripts/lint/check_mojibake.py` passes.
- **Synthetic / no-PHI**; advisory-only; **no source/EHR writeback**; HITL-gated; deny-by-default signals.
- Every edited doc bumps SemVer header (§9) + `Previous Version`; run `markdownlint` + mojibake.
- Ontology/crosswalk discipline if `reference-layer.ttl` touched (not expected in Slice 1).
- **Trunk-based:** one short-lived branch → **one squash PR** linked to #335. **Human reviews + merges. Never self-merge.**

## File structure (new unless noted)

```text
data/synthetic/schema/dc-insight-v1.schema.json
data-platform/decision/levers/lever.schema.json
data-platform/decision/levers/{ooa,dca,bmca,orsa,sba,csa}.yaml
data-platform/decision/impact/compute_expected_impact.py
data-platform/decision/impact/tests/test_impact_pure.py
data-platform/decision/barriers/derive_barriers.py
data-platform/decision/barriers/tests/test_barriers_pure.py
data-platform/decision/coordination/plan_runtime.py
data-platform/decision/coordination/store.py            # Store protocol + in-memory impl
data-platform/decision/coordination/tests/test_plan_runtime.py
data-platform/decision/README.md
data-platform/scripts/csa/csa-seed-proposed-actions.py  # mirrors existing seed scripts
data-platform/scripts/csa/csa-seed-plans.py
data-platform/decision/tests/test_contract_conformance.py
infra/modules/cosmos/csa.bicep                          # MODIFIED: +2 containers
infra/modules/cosmos/README.md                          # MODIFIED
data-platform/scripts/fabric/create_data_agent.md       # MODIFIED: DC-INSIGHT-v1
agents/fabric-data-agent/{AGENT.md,golden-tasks.md}     # MODIFIED
agents/ooa-agent/{AGENT.md,golden-tasks.md}             # MODIFIED
agents/dca-agent/{AGENT.md,golden-tasks.md}             # MODIFIED
docs/adr/0040-descriptive-to-prescriptive-decision-ontology.md  # NEW
docs/PRD.md                                             # MODIFIED: FR/NFR + §7
docs/DATA.md, docs/AI.md, AGENTS.md                     # MODIFIED as needed
```

## Tasks (TDD order — tests before implementation)

- [ ] **T1 — DC-INSIGHT-v1 contract.** Add `dc-insight-v1.schema.json` (draft-07: `signal`, `understanding`, `recommendation[]`, `action`, `coordination`, `provenance`; `additionalProperties:false`). Add `test_contract_conformance.py` with a valid + invalid fixture (red until schema exists). WS-D foundation. **Files:** schema + test. **Model:** cheap.
- [ ] **T2 — Lever catalog.** `lever.schema.json` (`lever_id, role, title_i18n{de,en,fr,it}, preconditions, params_schema, impact_formula_ref, owner_role, hitl:true`) + 6 role YAMLs (OOA + DCA fully specified: OOA `OOA-EXPEDITE-DISCHARGE`, `OOA-DIVERT-LOW-ACUITY`; DCA `DCA-UNBLOCK-BARRIER`; other 4 one stub each) + `test_levers_valid.py` validating every YAML against the schema. **Depends:** none. **Model:** standard.
- [ ] **T3 — Impact tool.** `compute_expected_impact(lever_id, params, gold)` pure fn: looks up lever `impact_formula_ref`, computes `{metric, delta, assumptions[]}` deterministically from injected gold forecast/driver rows. Golden-fixture tests (expedite 6 discharges ⇒ +6 beds; divert 3 ⇒ +3). No randomness, no LLM. **Depends:** T2. **Model:** standard.
- [ ] **T4 — Barrier model.** `derive_barriers(candidates)` pure fn ⇒ ranked list `{barrier_type, owner_role, aged_h, clears_at, bed_impact}` collapsing candidates into systemic barriers (design: 8 candidates → 5 barriers). Unit tests (ranking order, collapse, empty input). **Depends:** none. **Model:** standard.
- [ ] **T5 — Cosmos containers (IaC).** Add `proposed_actions` (pk `/plan_id`) + `plans` (pk `/episode_key`) to `infra/modules/cosmos/csa.bicep` mirroring existing containers; update README. No live deploy — `what-if` gated. **Depends:** none. **Model:** standard.
- [ ] **T6 — Coordination runtime.** `store.py` (`Store` protocol + `InMemoryStore`), `plan_runtime.py`: `open_plan(episode_key, baseline, current, target)`, `propose_action(...)`, `approve_action(action_id, approver)` → recompute via `compute_expected_impact` → append `forecast_deltas` + set `current` (102→94) + record OOA→DCA handoff. Refuse apply if approver is bot/self (mirror AGENTS.md §4). Unit tests end-to-end on InMemoryStore. Seed scripts mirror `csa-seed-*.py`. **Depends:** T3. **Model:** standard.
- [ ] **T7 — Data-Agent contract upgrade.** In `create_data_agent.md` extend output contract to `DC-INSIGHT-v1` (require `signal`+`understanding`+`provenance`; keep cite-≥1-`hcp:*`, RLS, PHI-refuse). Update `agents/fabric-data-agent/{AGENT.md,golden-tasks.md}` — keep RLS + PHI-refuse fixtures green, add a DC-INSIGHT happy fixture. SemVer bumps. **Depends:** T1. **Model:** standard.
- [ ] **T8 — OOA + DCA agent upgrades.** Extend `agents/ooa-agent/AGENT.md` + `agents/dca-agent/AGENT.md` to speak the decision vocabulary and assemble the 5-beat tuple (referencing levers + impact + handoff). Update each `golden-tasks.md` with happy / failure / PHI-refuse fixtures + `requirement:` keys. SemVer bumps. **Depends:** T1,T2,T6. **Model:** standard.
- [ ] **T9 — ADR + PRD.** `docs/adr/0040-...md` (descriptive→prescriptive ontology extension + runtime decision store; Status Accepted). Add PRD FR rows (e.g. `FR-DEC-001..00n` levers/impact/plan/handoff, `FR-INSIGHT-001` DC-INSIGHT-v1) + NFR (advisory-only/HITL) + §7 traceability rows pointing at the new artefacts + ADR-0040. SemVer bumps. **Depends:** T1–T8 (IDs reference them). **Model:** most capable.
- [ ] **T10 — Docs + final verification.** `data-platform/decision/README.md`; update `docs/DATA.md` (decision containers + DC-INSIGHT) + `docs/AI.md` (decision vocabulary + HITL) + AGENTS.md note if a registry line changes; SemVer bumps. Run all gates (below) and paste evidence. **Depends:** all. **Model:** standard.

## Verification (smallest targeted commands)

```bash
# Decision-lane unit tests (contract, levers, impact, barriers, coordination)
python -m unittest discover -s data-platform/decision -p "test_*.py" -v

# Contract validity of the new schema against fixtures (if wired into validate_datasets)
python data/synthetic/validate_datasets.py

# Bicep build for the modified Cosmos module (no deploy)
az bicep build --file infra/main.bicep

# Doc gates
python scripts/lint/check_mojibake.py
npx --yes markdownlint-cli2 "docs/**/*.md" "agents/**/*.md" "data-platform/decision/**/*.md" "#node_modules"
```

## Definition of done (this slice)

- [ ] DC-INSIGHT-v1 schema + conformance test green.
- [ ] Lever catalog validates; OOA+DCA fully specified; impact tool golden-fixture tests green.
- [ ] Barrier model ranked + unit-tested.
- [ ] Cosmos `proposed_actions`+`plans` container defs in `csa.bicep`; `az bicep build` clean.
- [ ] Coordination runtime proves 102%→94% + OOA→DCA handoff on InMemoryStore end-to-end.
- [ ] Data Agent emits DC-INSIGHT-v1; RLS + PHI-refuse golden tasks still green.
- [ ] OOA + DCA agents assemble the 5-beat tuple; happy/failure/PHI-refuse golden tasks pass.
- [ ] ADR-0040 Accepted; PRD FR/NFR + §7 updated; all edited docs SemVer-bumped.
- [ ] Mojibake + markdownlint clean. PR lists FR/NFR, lane impact, test evidence, references #335. **Not self-merged.**

## Open items (carry to fan-out)
- Fan-out levers for BMCA/ORSA/SBA (reuse Sprint 23 skills) + CSA (reuse Sprint 21 signals).
- Live Cosmos container + Foundry agent deploy under `approved-to-apply`.
- Whether to promote the runtime-derived barrier model to a `gold.fact_discharge_barrier` table if fan-out needs it.
