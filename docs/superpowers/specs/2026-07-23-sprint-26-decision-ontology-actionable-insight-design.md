# Sprint 26 — Decision Ontology & Actionable-Insight Layer — Design Spec

| Field | Value |
| ----- | ----- |
| **Version** | 1.9.0 |
| **Date** | 2026-07-27 |
| **Author** | @urruegg |
| **Status** | Complete — all workstreams delivered (WS-A done; WS-B/C/D vertical slice merged #369; fan-out merged #376; WS-C live-apply tooling merged #382/#388; job enabled in SIT #403; WS-B Cosmos seed live-applied; WS-C Foundry registration live-applied + re-verified per §9.11/§9.14; WS-B barrier Gold materialised per §9.12; prescriptive terms `hcp:Recommendation`/`hcp:Lever` landed per §9.13 — all three originally-deferred items closed; live Cosmos/Foundry apply verified complete per §9.14) |
| **Previous Version** | 1.8.0 (added §9.13 prescriptive ontology terms `hcp:Recommendation`/`hcp:Lever`) |
| **Related** | [Fabric IQ to Foundry readiness design](2026-07-17-fabric-iq-foundry-readiness-design.md), [Fabric IQ ready evidence](../../architecture/fabric-iq-ready-evidence.md), [Curavias clickable prototype](../ideas/curavias-ux-ideas/prototype/index.html), Sprint 21 (#247) external signals, Sprint 23 (#255) org/skills ontology, Sprint 19 (#239) PROD Switzerland North |

---

## Table of Contents

1. [Why — the gap](#1-why--the-gap)
2. [Locked decisions (this brainstorm)](#2-locked-decisions-this-brainstorm)
3. [Target architecture](#3-target-architecture)
4. [Work-stream decomposition](#4-work-stream-decomposition)
5. [Delivery — vertical slice then fan-out](#5-delivery--vertical-slice-then-fan-out)
6. [Definition of done](#6-definition-of-done)
7. [Open items](#7-open-items)
8. [References](#8-references)
9. [Status & next step](#9-status--next-step)

---

## 1. Why — the gap

The current Fabric IQ / Foundry IQ grounding layer is **descriptive**: it answers
*"what is the occupancy now"*. The locked Curavias prototype demands that each of the
6 copilots be **predictive, prescriptive, and coordinated**.

### 1.1 What exists today

| Layer | Artefact | Character |
| ----- | -------- | --------- |
| Ontology | `ont_hospital_capacity` (10 entity types, 11 relationships): `hcp:Ward/Bed/BedAssignment` | Descriptive bed-state graph |
| Semantic model | `capacity-dashboard` Direct Lake — 27 tables, 27 measures, 16 relationships, 6 RLS roles | Current-state occupancy / OR / value |
| Data Agent | `da_hospital_capacity` — read-only NL -> concept, RLS + PHI-refuse, cites `hcp:*` | Answers "what is" |
| Foundry | 8 agents in eastus2; only `ooa` wired to the Fabric Data Agent (gpt-5) | Retrieval only |
| Signals | Sprint 21 external-signals (MeteoSwiss / BAG / Alertswiss / SED, trust tiers) | Separate gold surface, partly wired to CSA |

### 1.2 What the prototype demands — the 5-beat actionable-insight pattern

Every role surface in the prototype follows the **same five beats**; today's layer
serves only beat 1:

```text
(1) SIGNAL          -> (2) UNDERSTANDING     -> (3) RECOMMENDATION       -> (4) ACTION          -> (5) COORDINATION
    KPI + breach         driver / "Warum"        ranked levers +             one-click, owner,      golden thread,
    (102%, -16 beds)     (+6 flu vs 2 disch.)    expected impact (d-beds)    deadline, HITL         live forecast delta
```

Evidence from the surfaces (`docs/superpowers/ideas/curavias-ux-ideas/prototype/surfaces/`):

- **OOA** — *"+6 admissions forecast (flu season) vs. only 2 planned discharges in 72h"*
  (beat 2) and *"Expedite 6 discharge-ready before 17:00 / Divert 3 low-acuity to
  Medicine B"* (beat 3): **forecast + driver decomposition + quantified levers**.
- **DCA** — *"8 candidates collapse into 5 systemic barriers"* with owner / age /
  clear-time / bed-impact: a **barrier model**.
- **BMCA / ORSA / SBA** — one-click actions with expected bed/staff impact and
  `-> hand to sba-agent`: **Recommendation/Lever + Action with cross-role handoff**.
- **CSA** — *"6 shocks pressure-tested"*, certainty 68% / 31%, Trust-A, source badges:
  **scenario + probability + trust-tier**.
- **Golden thread** — *"Medicine A 102% -> 94%"* live-syncing across roles: the
  coordinated **Plan/Episode** as a first-class object, not a UI narrative.

### 1.3 The core gap

Three semantic tiers are missing on top of the Gold Direct Lake model:

1. **Foresight tier** — `Forecast` (72h occupancy/admissions), `Driver` (why), `Signal`
   (Sprint 21, with trust + probability). Turns beat 1 into beats 1+2.
2. **Decision tier** — the highest-leverage missing concept: `Recommendation`/`Lever`
   = a proposed action carrying **quantified expected impact (d-beds, d-%), owner,
   deadline, status, HITL gate**; plus `Barrier` and `Action`. Powers beats 3+4.
3. **Coordination tier** — `CapacityEpisode`/`Plan` = the golden thread as a first-class
   object linking role actions and live forecast deltas. Powers beat 5.

The Foresight-signal feed is owned by Sprint 21, SBA's skills inputs by Sprint 23, and
regional collocation by Sprint 19 — but the **forecast + driver + recommendation + plan
spine is owned by no current sprint**. This sprint fills that gap.

---

## 2. Locked decisions (this brainstorm)

| # | Decision | Rationale |
| - | -------- | --------- |
| **D1** | **Hybrid production/persistence.** Foresight tier is **precomputed in the Gold medallion + Fabric IQ ontology**; the Decision + Coordination tiers are **generated at runtime** by the agents and **persisted to Cosmos** (reuse the CSA `cosmos-mcp` account `cosmos-csa-ihzhhpf-sit`). | Forecast/driver are naturally batch, testable, auditable. Recommendations/plan are per-conversation and must live-sync, which fits a runtime store. |
| **D2** | **Synthetic deterministic Foresight generator** in the medallion, mirroring the Sprint 21/22 simulators: forecast + driver decomposition computed from synthetic admission/discharge series as Gold tables, with a clean seam to swap in a real forecasting model later. | No-PHI demo scope; reproducible; fast; keeps the "real model" as a drop-in. |
| **D3** | **Vertical golden-thread slice first: OOA -> DCA** (the prototype headline 102% -> 94%), proving all 5 beats end-to-end including cross-role Plan sync; the **sprint doc covers all 6 roles** for end-to-end coverage, fanned out in follow-on slices. | Reviewable slice discipline; proves the pattern before scaling. |
| **D4** | **Curated lever catalog + deterministic impact.** Each role has typed action templates (e.g. "expedite N discharge-ready", "divert N low-acuity"); the agent **selects and parameterizes** them, and expected impact (d-beds / d-%) is computed by a **deterministic tool over the semantic model**, not guessed by the LLM. | Auditability, testability, trust; keeps numbers defensible. |
| **D5** | **Advisory-only + HITL.** Selecting a lever writes a **proposed-action record to Cosmos** and requires **human approval**; on approval the deterministic impact tool **recomputes the forecast delta** and updates the Plan (102% -> 94%). **No writeback to any source/EHR** — the "live sync" is the recomputed Foresight number. | Matches the platform's advisory-only + `approved-to-apply` governance and no-PHI scope. |

---

## 3. Target architecture

### 3.1 The actionable-insight contract (`DC-INSIGHT-v1`)

A grounded copilot answer is a **5-beat tuple**, not a free-form sentence:

```json
{
  "signal":         { "metric": "occupancy_pct", "value": 102, "unit": "%", "threshold": 100, "breach": true, "scope": "hcp:Ward/Medicine A", "horizon_h": 72 },
  "understanding":  { "drivers": [ { "factor": "forecast_admissions", "delta": +6, "note": "flu season" }, { "factor": "planned_discharges", "delta": -2 } ] },
  "recommendation": [ { "lever_id": "OOA-EXPEDITE-DISCHARGE", "params": { "n": 6, "before": "17:00" }, "expected_impact": { "metric": "beds", "delta": +6 }, "owner_role": "dca", "deadline": "2026-..." } ],
  "action":         { "status": "proposed", "hitl": "required", "cosmos_id": "..." },
  "coordination":   { "plan_id": "...", "golden_thread": "Medicine A 102% -> 94%", "handoff": "dca" },
  "provenance":     { "concepts": ["hcp:Ward","hcp:Bed"], "confidence": 0.0, "source_trust": "A" }
}
```

The Fabric Data Agent output contract (today: "cite >= 1 `hcp:*` concept") is **extended**
to require the `signal`, `understanding`, and `provenance` blocks; the Decision +
Coordination blocks are assembled at runtime by the agent-host.

### 3.2 Foresight tier — Gold medallion + ontology (WS-A)

- New Gold Delta tables (synthetic deterministic generator, D2):
  - `gold.fact_occupancy_forecast` — per ward x horizon (0..72h) forecast occupancy %/beds.
  - `gold.fact_forecast_driver` — decomposition rows (admissions +N, discharges -N, transfers, seasonality) per forecast point.
  - `gold.fact_signal` — Sprint 21 external-signal feed joined in with `trust_tier`, `probability` (deny-by-default; reuse `DC-EXT-SIGNAL-v1`).
- New ontology concepts + relationships on `ont_hospital_capacity`:
  - `hcp:Forecast` (bound to `fact_occupancy_forecast`), `hcp:Driver`, `hcp:Signal`.
  - `hcp:Forecast --forWard--> hcp:Ward`, `hcp:Forecast --explainedBy--> hcp:Driver`, `hcp:Driver --evidencedBy--> hcp:Signal`.
- Semantic-model additions: forecast + driver tables + measures (e.g. `[Forecast Occupancy 72h]`, `[Bed Gap 72h]`, `[Driver Net Admissions]`), RLS extended to the new tables. Verify-gate counts rebaselined in the **same PR** (per the Sprint 22 exact-count rule).

### 3.3 Decision tier — runtime + Cosmos (WS-B + WS-C)

- **Lever catalog** (git-owned config, versioned): `data-platform/decision/levers/<role>.yaml` —
  typed templates `{ lever_id, role, title_i18n, preconditions, params_schema, impact_formula_ref, owner_role, hitl: true }`.
  All 6 roles seeded; OOA + DCA fully specified for the vertical slice.
- **Deterministic impact tool** — an agent-host / `fabric-mcp` tool
  `compute_expected_impact(lever_id, params)` that runs a bounded query over the
  semantic model and returns `{ metric, delta, assumptions[] }`. Pure function, unit-tested
  with golden fixtures; **never** an LLM estimate.
- **Barrier model** (DCA) — `gold.fact_discharge_barrier` (or runtime-derived) with
  `barrier_type, owner_role, aged_h, clears_at, bed_impact`; ranked, not a flat list.
- **Proposed-action** — Cosmos container `proposed_actions` `{ id, plan_id, role, lever_id, params, expected_impact, status: proposed|approved|rejected|applied, hitl_approver, approved_at }`.

### 3.4 Coordination tier — runtime + Cosmos (WS-C)

- **Plan / CapacityEpisode** — Cosmos container `plans`
  `{ id, episode_key: "Medicine A / 102% / 72h", baseline, current, target, actions[], forecast_deltas[], handoffs[] }`.
- **Golden-thread live-sync** — on `approved-to-apply`, the deterministic impact tool
  recomputes the forecast delta, appends to `plans.forecast_deltas`, and updates
  `current` (102% -> 94%). The OOA surface reads `plans.current` for the "live sync".
- **Cross-role handoff** — a proposed-action with `owner_role != role` records a handoff
  edge; the receiving copilot picks it up from `plans.handoffs`.

### 3.5 Consumption — Data Agent contract + 6 Foundry agents (WS-D)

- Upgrade `da_hospital_capacity` output contract to `DC-INSIGHT-v1` (signal +
  understanding + provenance); keep RLS + PHI-refuse golden tasks green.
- Extend all 6 Foundry agent instructions (bmca/ooa/dca/orsa/sba/csa) to speak the
  decision vocabulary and assemble the Decision + Coordination blocks; only `ooa` is
  wired today, so this widens grounding to the full set.
- **Governance:** advisory-only; every action is HITL-gated (`approved-to-apply`); no
  EHR/source writeback; synthetic/no-PHI; deny-by-default on signals. New **ADR** records
  the descriptive -> prescriptive ontology extension and the runtime/Cosmos decision store.

### 3.6 Region + reuse

Deploys into the same Fabric IQ workspace/lakehouse and the CSA Cosmos account; follows
Sprint 19 to Switzerland North when that lands. No new MCP server required (`fabric-mcp`,
`cosmos-mcp`, `github-mcp` already allow-listed).

---

## 4. Work-stream decomposition

| WS | Lane | Scope | Key outputs |
| -- | ---- | ----- | ----------- |
| **WS-A** | Data | Foresight tier | Synthetic forecast+driver generator; `gold.fact_occupancy_forecast` / `fact_forecast_driver` / `fact_signal`; ontology `hcp:Forecast/Driver/Signal`; semantic-model + verify-gate rebaseline |
| **WS-B** | Data/AI | Lever catalog + deterministic impact | `decision/levers/<role>.yaml` (6 roles; OOA+DCA full); `compute_expected_impact` tool + unit tests; barrier model |
| **WS-C** | AI/Experience | Decision + Coordination runtime | Cosmos `proposed_actions` + `plans` containers; HITL approve -> recompute -> plan update; handoff edges; golden-thread live-sync |
| **WS-D** | AI/Governance | Consumption + governance | `DC-INSIGHT-v1` Data Agent contract; 6 agent instruction upgrades; ADR + PRD FR/NFR + traceability; golden tasks (happy / failure / PHI-refuse) |

---

## 5. Delivery — vertical slice then fan-out

1. **Slice 1 (OOA -> DCA, all 5 beats).** WS-A forecast+driver for Medicine A; WS-B OOA
   ("expedite discharge", "divert low-acuity") + DCA (barrier unblock) levers + impact tool;
   WS-C Plan `Medicine A / 102% / 72h`, proposed-action -> HITL -> recompute to 94%,
   OOA->DCA handoff; WS-D `DC-INSIGHT-v1` on OOA + DCA, golden tasks. **Proves the pattern.**
2. **Fan-out slices** — BMCA, ORSA, SBA (reuse Sprint 23 skills inputs), CSA (reuse Sprint 21
   signals + scenario/probability). Each a small PR reusing WS-A..D primitives.

Each slice is one short-lived branch -> one squash PR -> human review. No self-merge.

---

## 6. Definition of done

- [ ] Foresight Gold tables + ontology concepts live; semantic-model verify-gate green (rebaselined in-PR).
- [ ] Lever catalog for all 6 roles committed; OOA + DCA fully specified; `compute_expected_impact` unit-tested with golden fixtures.
- [ ] Cosmos `proposed_actions` + `plans` containers; HITL approve -> deterministic recompute -> Plan `current` updates (102% -> 94%) proven end-to-end for the OOA->DCA slice.
- [ ] `da_hospital_capacity` emits `DC-INSIGHT-v1`; RLS + PHI-refuse golden tasks still green.
- [ ] OOA + DCA Foundry agents assemble the 5-beat tuple; happy / failure / PHI-refuse golden tasks pass.
- [ ] ADR (descriptive -> prescriptive extension + runtime decision store) Accepted; PRD FR/NFR + traceability updated.
- [ ] Advisory-only + HITL enforced; no EHR/source writeback; synthetic/no-PHI; deny-by-default signals.
- [ ] Doc gates green (markdownlint + mojibake + link check); all edited docs version-bumped per copilot-instructions Section 9.

## 7. Open items

- ~~Whether the barrier model (`fact_discharge_barrier`) is precomputed in Gold or derived at
  runtime~~ **Resolved (WS-B follow-up, #335):** *both* — the pure `derive_barriers`
  builder serves the runtime path, and `build_gold_barrier` materialises the **same** ranked
  barriers to `gold.fact_discharge_barrier` (contract `DC-DISCHARGE-BARRIER-v1`; grounds
  `hcp:Barrier`), reusing `derive_barriers` verbatim so the two paths never diverge.
- Exact new semantic-model measure/relationship/role counts for the verify-gate rebaseline
  (WS-A confirms and updates `export_semantic_model_tmdl.ps1` + `verify-semantic-model.yml` in the same PR).
- Confirm the CSA Cosmos account can host `proposed_actions` + `plans` containers under the
  existing RBAC scope, or whether a new container-level role assignment is needed.
- i18n: lever `title_i18n` covers DE/EN/FR/IT to match the app + Sprint 24 posture.

## 8. References

- [Fabric IQ to Foundry readiness design](2026-07-17-fabric-iq-foundry-readiness-design.md)
- [Fabric IQ ready evidence](../../architecture/fabric-iq-ready-evidence.md)
- [Curavias clickable prototype](../ideas/curavias-ux-ideas/prototype/index.html) (6 role surfaces = the steering artefact)
- Sprint 21 (#247) external signals; Sprint 23 (#255) org/skills ontology; Sprint 19 (#239) PROD Switzerland North
- [ADR-0014 (Fabric IQ ontology backbone, GA-gated)](../../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md); [ADR-0034 (Fabric IQ demo scope)](../../adr/0034-fabric-iq-demo-scope-artefacts.md)

---

## 9. Status & next step

> Delivery status as of **2026-07-25**. WS-A (Foresight) and the WS-B/C/D
> **vertical slice** (OOA -> DCA, all 5 beats) are merged to `main` (#369); the
> fan-out to BMCA/ORSA/SBA/CSA is merged (#376). The current slice adds the
> **WS-C live-apply tooling** — a Cosmos-backed `PlanStore`, a HITL-gated live
> seed, and a Foundry decision-tier registration tool (see §9.8).

### 9.1 Work-stream progress

| WS | Status | Evidence / notes |
| -- | ------ | ---------------- |
| **WS-A — Foresight tier** | ✅ **Done, merged to `main`** | Deterministic forecast+driver+signal generator, 3 Gold tables, `hcp:Forecast/Driver` + `hcp:ExternalSignal` reuse, 2 contracts (`DC-OCCUPANCY-FORECAST-v1`, `DC-FORECAST-DRIVER-v1`), 16 unit tests. Live SIT evidence captured. |
| **WS-B — Lever catalog + deterministic impact** | ✅ **Vertical slice merged (#369); fan-out merged; barrier Gold materialised (#335, §9.12)** | OOA+DCA levers, `compute_expected_impact`, `DC-INSIGHT-v1` contract, and the pure `derive_barriers` builder landed via #369; the four fan-out levers merged. **WS-B follow-up (#335):** the `DC-DISCHARGE-BARRIER-v1` contract, the `hcp:Barrier` ontology term, and the `gold.fact_discharge_barrier` materialization (`build_gold_barrier`, reusing `derive_barriers` verbatim) landed — closing the deferred Gold-materialization item (§9.12). |
| **WS-C — Decision + Coordination runtime (Cosmos)** | ✅ **Vertical slice (#369) + fan-out (#376) merged; live-apply tooling in delivery** | `Store`/`plan_runtime` (102%→94% recompute + OOA→DCA handoff) landed via #369; `seed_fanout.py` via #376. Current slice adds the Cosmos-backed `CosmosStore(PlanStore)`, the HITL-gated `coordination/seed_live.py`, and the Foundry `foundry/register_decision_tier.py` tool (§9.8). Live infra deploy + in-VNet apply still pending the `sit` environment approval + an in-VNet run. |
| **WS-D — Consumption + governance** | ✅ **Vertical slice merged (#369); fan-out in delivery** | `DC-INSIGHT-v1` Data Agent contract + OOA/DCA agent upgrades + ADR-0040 + PRD `FR-DEC-*`/`NFR-DEC-*` landed via #369. Current slice upgrades the BMCA/ORSA/SBA/CSA agent packs + golden tasks. |

### 9.2 WS-A — what landed (merged PRs, issue #335)

- **#346** — WS-A core: `data-platform/notebooks/foresight/build_gold_forecast.py` + `build_gold_signal.py`, tests, `DC-OCCUPANCY-FORECAST-v1` + `DC-FORECAST-DRIVER-v1` schemas, ontology (`reference-layer.ttl` + `crosswalk.md`), `docs/DATA.md`, WS-A plan doc.
- **#351 / #353** — Live **Fabric SIT evidence**: self-contained evidence notebook + verify script + tests + [`docs/architecture/foresight-fabric-evidence.md`](../../architecture/foresight-fabric-evidence.md). Materialized under an `approved-to-apply` gate in `ws-ihzhhpf-sit-data` / `lh_ihzhhpf_sit` (westus2), notebook `50159429-bc58-4c3e-82ff-89871a2fbc1d` run Completed:
  - `fact_occupancy_forecast` **73 rows** · `fact_forecast_driver` **292 rows** (= 4× forecast) · `fact_signal` **4 rows** (all Trust-A).
  - Medicine A: h0 51 beds/102% → h72 55/110% breach; h72 drivers +6 −2 +0 +0 reconcile to +4.
- **Deferred out of WS-A** (tracked, not regressions): the semantic-model TMDL measures/RLS + `verify-semantic-model.yml` count rebaseline (design §3.2) were split to a **WS-A2** stacked slice so the generator PR stayed reviewable; §6 DoD line 1 is therefore **partially** met (Gold tables + ontology live; verify-gate rebaseline pending WS-A2).

### 9.3 WS-B — next slice (locked scope + decisions)

One cohesive squash PR off `main` (branch `sprint-26/ws-b-levers`), Data/AI lane, TDD-first, **no Cosmos / no agent wiring** (those are WS-C / WS-D):

1. **Lever catalog** — `data-platform/decision/levers/<role>.yaml` (6 roles; **OOA + DCA fully specified**), JSON-schema-validated (model on `data-platform/scripts/csa/schema/response-levers.schema.json`); `title_i18n` de/en/fr/it.
2. **Deterministic impact tool** — pure, unit-tested `compute_expected_impact(lever_id, params, ctx)` — formula registry, **never an LLM estimate** (D4).
3. **DCA barrier model** — deterministic pure builder + `dc-discharge-barrier-v1.schema.json`; **Gold materialization deferred** to a follow-up (confirmed). *(Follow-up landed #335 — see §9.12: the schema, `hcp:Barrier`, and `gold.fact_discharge_barrier` materialization were completed in a WS-B follow-up; the pure builder alone shipped with #369.)*
4. **Ontology** — add **only `hcp:Barrier`** (+ crosswalk MVO row, STRICT conformance); defer `hcp:Recommendation`/`hcp:Lever` to WS-C runtime (confirmed).
5. **Docs** — `data-platform/decision/README.md`; PRD `FR-DEC-*` / `NFR-DEC-*` + §7 traceability; SemVer bumps.

**Confirmed decisions (@urruegg, 2026-07-24):** barrier builder+schema now / defer Gold materialization · add only `hcp:Barrier` now · one cohesive PR.

### 9.4 Resume checklist (next run — fan-out)

- [ ] Re-read this §9 + the design §3.3 / §4 (WS-B) + [`docs/AI.md`](../../AI.md), [`docs/DATA.md`](../../DATA.md), [`docs/COMPLIANCE.md`](../../COMPLIANCE.md).
- [ ] On branch `sprint-26/ws-b-levers` (already off `main`): TDD — schemas + failing tests first, then lever yaml + impact tool + barrier builder.
- [ ] Validate: `pytest`, catalog schema-validate, `check_crosswalk_conformance.py --strict`, mojibake + markdownlint. Commit hooks-off; open one squash PR, base `main`, refs #335, **no self-merge**.

### 9.5 Fan-out slice — BMCA / ORSA / SBA / CSA (current)

One cohesive squash PR off `main` (branch `sprint-26/ws-b-levers`), 3-lane
(Data/AI + Governance), TDD-first. Reuses the merged #369 pattern; **no new
Cosmos container, no live `apply`** (the `proposed_actions` / `plans` containers
already exist as role-agnostic IaC).

| Role | Lever | `metric` | `params` | `formula_ref` |
| ---- | ----- | -------- | -------- | ------------- |
| BMCA | `BMCA-REBALANCE-CENSUS` | `rebalanced_beds` | `n`, `to_ward` | `rebalance_census_beds` |
| ORSA | `ORSA-DEFER-ELECTIVE` | `elective_slots` | `n`, `before` | `defer_elective_slots` |
| SBA | `SBA-FLEX-STAFF-BEDS` | `staffed_beds` | `n`, `shift` | `flex_staff_beds` |
| CSA | `CSA-ACTIVATE-SURGE` | `surge_beds` | `n`, `scope` | `activate_surge_beds` |

1. **Levers** — replace the four `*-PLACEHOLDER` stubs with fully-specified,
   schema-valid catalogs (one self-owned lever each; `description_i18n` de/en/fr/it).
2. **Impact** — four new pure formulas in `compute_expected_impact.py`
   (registry now 7), each reusing `_bounded_bed_impact` with a role-specific
   `metric` label but a bed-relief `delta` so the coordination recompute is
   unchanged; `mechanism` carried in `assumptions`. Unit-tested.
3. **Coordination** — `coordination/seed_fanout.py` mirrors `seed_slice1.py`
   with a self-owned golden thread per role (BMCA 105→97, ORSA 105→95, SBA
   104→98, CSA 120→80). Unit-tested.
4. **Agent packs** — BMCA/ORSA/SBA/CSA `AGENT.md` gain the Sprint 26 extension
   (§1), in-scope bullet (§2), `fabricated-impact` + `self-approval` refusals
   (§5), the `DC-INSIGHT-v1` 5-beat subsection (§6), and the decision-tier
   confirmation note (§7). CSA's note complements its existing Run/HITL gating.
5. **Golden tasks** — one `DC-INSIGHT-v1` breach fixture per role + FR-DEC
   front-matter + SemVer bumps.

**Confirmed decisions (@urruegg, 2026-07-25):** one self-owned lever per role ·
role-specific metric names with bed-relief delta · include Cosmos (WS-C) seed +
agent (WS-D) wiring · reuse existing containers (no new IaC) · one cohesive PR.

**Still deferred (not this branch):** live Cosmos/Foundry `apply`; DCA barrier
Gold materialization; ontology `hcp:Recommendation` / `hcp:Lever`.

### 9.6 Slice 1 — what landed (merged PR #369, follow-up #370; issue #335)

Vertical Slice 1 moved OOA + DCA from **descriptive → prescriptive** end-to-end on one
golden thread (Medicine A, 102% → 94% at 72h, OOA→DCA handoff):

- **Decision lane** — `DC-INSIGHT-v1` JSON-schema contract + conformance test; lever catalog (OOA + DCA fully specified, other 4 stubbed); pure `compute_expected_impact` (`delta = min(n, max(0, round(forecastOccupiedBeds)))`, **never an LLM estimate**); runtime-derived DCA barrier model.
- **Coordination lane** — pure runtime `open_plan → propose_action → HITL approve → deterministic recompute (102→94) → OOA→DCA handoff`; HITL refuses bot/self/non-proposed approvers. Cosmos `proposed_actions` (pk `/plan_id`) + `plans` (pk `/episode_key`) added to `infra/modules/cosmos/csa.bicep` (+ recompiled `infra/main.json`) — **definitions only, no live deploy.**
- **Consumption lane** — `da_hospital_capacity` emits signal/understanding/provenance beats (RLS + PHI-refuse preserved); OOA + DCA agents assemble the 5-beat tuple, agent-host mediates the Cosmos write so OOA/DCA keep `write` ceiling with **no `cosmos-mcp` grant**; golden tasks added (happy 5-beat / HITL self+bot refusal / OOA→DCA handoff).
- **Governance + CI** — `docs/adr/0040-prescriptive-decision-ontology-and-runtime-store.md` (Accepted); new `.github/workflows/decision-lane.yml` gate (75 decision-lane tests + contract conformance); PRD `FR-FC-007`, `FR-DEC-001/002/003`, `NFR-DEC-001` + §7 traceability.
- **Test evidence at merge** — 75 decision-lane tests OK · `az bicep build` exit 0 (`infra/main.json` byte-identical) · mojibake clean · markdownlint 0 new violations.
- **Follow-up #370** (open, CI green) — MD040 fenced-code language + regenerated app evidence fixture to green `main` after #369.
- **Explicitly deferred (fan-out, not regressions):** BMCA / ORSA / SBA / CSA lever specs + agent upgrades; live Cosmos/Foundry `apply`; DCA barrier Gold materialization.

### 9.7 Superseded plan — original WS-B-first sequencing

> Retained for history. The original §9.3 planned WS-B as a standalone next slice on
> branch `sprint-26/ws-b-levers`. That was superseded by the **vertical-slice** decision
> (@urruegg): deliver OOA→DCA across WS-B+C+D in one cohesive PR (#369) to prove all 5
> beats end-to-end before fanning out. Locked decisions from that plan still hold — barrier
> builder+schema now / defer Gold materialization · add only `hcp:Barrier` now · one
> cohesive PR.

### 9.8 WS-C live-apply tooling — Cosmos store + Foundry registration (current)

One cohesive squash PR off `main` (branch `sprint-26/ws-c-live-apply`),
Data/AI lane, TDD-first. Turns the "definitions-only" decision store into
**gated, executable apply tooling** without mutating cloud from CI. Confirmed
scope A+B+C (@urruegg, 2026-07-25).

1. **CosmosStore** — `coordination/cosmos_store.py`: a `CosmosStore(PlanStore)`
   over the `plans` (`/episode_key`) + `proposed_actions` (`/plan_id`)
   containers, RBAC-only (`DefaultAzureCredential`, no keys), lazy SDK import,
   injectable container clients. Swap-compatible with `InMemoryStore` (contract
   parity test). 12 unit tests.
2. **Gated live seed** — `coordination/seed_live.py`: replays all six roles
   (Slice-1 OOA→DCA + four fan-out threads) through the pure `plan_runtime`
   into an injected store. `--action plan` prints the exact documents (dry run,
   no cloud); `--action apply` requires a non-bot `--approved-to-apply` handle
   AND a reachable Cosmos account, refusing a silent no-op. 13 unit tests.
3. **Foundry registration** — `foundry/register_decision_tier.py`: mirrors
   `register_fabric_data_agent_tool.py`; deterministic per-agent plan for the
   six decision-tier agents (each pointed at its own role lever catalog + the
   Cosmos containers + the deterministic impact tool), apply HITL-gated behind a
   live registration factory. 15 unit tests.

**Network reality (constrains "live").** The SIT Cosmos account is
`publicNetworkAccess = Disabled` + private-endpoint only
([ADR-0029](../../adr/0029-agent-host-cosmos-reachability.md)) and the Foundry
project is eastus2 ([ADR-0032](../../adr/0032-foundry-control-plane-eastus2.md)),
so neither is reachable from a laptop or a hosted CI runner. The real apply runs
from inside the VNet (the agent-host). This branch therefore delivers the gated
tooling + tests + dry-run evidence; the two remaining live steps are operational:

- **(A) infra deploy** — the `proposed_actions` / `plans` container definitions
  merged in #369 are still `waiting` on the `sit` GitHub environment reviewer
  gate; @urruegg approving the pending `cd-infra-deploy-sit` run materializes
  them (blast radius = the whole `infra/main.bicep` on latest `main`).
- **(B/C) in-VNet apply** — once containers exist, run
  `python -m coordination.seed_live --action apply --approved-to-apply <handle>`
  and `python -m foundry.register_decision_tier --action apply --role <role>
  --approved-to-apply <handle>` from the agent-host.

**Still deferred (not this branch):** DCA barrier Gold materialization;
ontology `hcp:Recommendation` / `hcp:Lever`.

### 9.9 WS-C follow-up — in-VNet apply job + live Foundry factory (current)

One squash PR off `main` (branch `sprint-26/ws-c-apply-runbook`), Infra +
Data/AI + Governance lanes, TDD-first. Closes the "how does the live apply
actually run" gap left open by §9.8 by delivering the in-VNet runner and the
missing live Foundry seam. Confirmed scope: reuse the hcc-agent-host image/MI
for both B and C **and** wire a live Foundry factory now (@urruegg, 2026-07-25).

1. **Live Foundry factory** — `foundry/live_factory.py`:
   `make_registration_factory(...)` speaks the Foundry Agents (Assistants
   protocol) REST API in eastus2 — resolves the assistant by name, appends a
   native **function** tool (`decision_tier_coordination_<role>`) idempotently,
   sets the `decision_tier_role` metadata, POSTs the modify. Injectable
   `token_provider` (scope `https://cognitiveservices.azure.com/.default`) +
   `http_request`, so the whole sequence is unit-tested without cloud (mirrors
   `fabric_data_agent_client.py`). `register_decision_tier.main --action apply`
   now builds this factory from `FOUNDRY_PROJECT_ENDPOINT` / `FOUNDRY_PROJECT_NAME`
   (ADR-0032 SIT defaults). 10 unit tests.
2. **Image + CI** — `apps/hcc-agent-host/Dockerfile` bakes in
   `data-platform/decision/`; the `.dockerignore` allowlist + `ci-build-agent-host.yml`
   trigger paths add `data-platform/decision/**` so the apply CLIs ship in the
   `hcc-agent-host` image alongside the `azure-identity` / `azure-cosmos`
   runtime deps.
3. **In-VNet job** — `infra/modules/decision-apply-job/main.bicep`: a
   manual-trigger `Microsoft.App/jobs` on the **agent-host CAE**
   (VNet-integrated → Cosmos PE reachable) reusing the agent-host MI (already a
   Cosmos Built-in Data Contributor). Plan-first by default (both CLIs run
   `--action plan`); a live apply is an operator-driven `az containerapp job
   start` command override that supplies `--approved-to-apply <handle>`
   (AGENTS.md §4). Wired into `infra/main.bicep` behind
   `enableDecisionApplyJobModule` (SIT-gated). `az bicep build` clean.
4. **Runbook** — [`docs/runbooks/decision-tier-live-apply.md`](../../runbooks/decision-tier-live-apply.md):
   the exact prerequisites (incl. the one-time `Cognitive Services User` grant
   for the agent-host MI on the eastus2 Foundry account), the plan-first + live
   apply `az containerapp job start` invocations, verification, and rollback.

**Verified (2026-07-25).** Cosmos containers already live (§9.8 A done via
`cd-infra-deploy-sit` #379/#381). The live apply itself remains an operational,
human-gated step run through the new job per the runbook.

**Still deferred (not this branch):** DCA barrier Gold materialization;
ontology `hcp:Recommendation` / `hcp:Lever`.

### 9.10 WS-C enablement — job turned on in SIT (current)

One squash PR off `main` (branch `sprint-26/ws-c-enable-apply-job`), Infra +
Governance lanes. Turns the §9.9 job on in SIT so the human-gated live apply can
run. The blocker that deferred this (the Sprint 28 PO-Agent OpenAI-at-SIT quota
failure) was resolved on `main` (#392/#394/#397/#398 — SIT + PROD deploys green).

1. **Job image (Option B, low blast radius)** — the §9.9 job inherited
   `agentHostImage`, still pinned to the pre-decision `:b796961` (2026-07-18). A
   new `decisionApplyJobImage` param (`infra/main.bicep`, default empty →
   inherits `agentHostImage`) lets SIT pin the **job only** to the
   decision-CLI-enabled `:2b83a49` (built by `ci-build-agent-host` on the #388
   merge) without redeploying the running agent-host Container App.
2. **SIT params** — `sit.bicepparam` sets `enableDecisionApplyJobModule = true`
   and `decisionApplyJobImage = '…/hcc-agent-host:2b83a49'`. No coordinator-owned
   main-health pin is touched.
3. **Human gates** — @urruegg merges the PR and approves the `cd-infra-deploy-sit`
   environment gate (creates the job); the live apply is then run plan-first and
   applied only with `--approved-to-apply <handle>` per the runbook (AGENTS.md §4).

### 9.11 WS-C live apply — guided run outcome + Foundry Agents-API fix (current)

The 2026-07-26 guided live apply (job `caj-decision-apply-ihzhhpf-sit`, image
`:2b83a49`, `--approved-to-apply urruegg`) produced a **split result** that this
fix branch (`sprint-26/ws-c-foundry-agents-api`, Platform-control + AI lanes)
resolves.

1. **WS-B Cosmos seed — ✅ LIVE APPLIED.** `coordination.seed_live --action
   apply` wrote the six-role `plans` + `proposed_actions` documents to
   `cosmos-csa-ihzhhpf-sit` / `csa` (job stdout `{"applied": true, "approvedBy":
   "urruegg", "planCount": 5}`). Re-runs are idempotent.
2. **WS-C Foundry registration — ❌ blocked by a code bug, now fixed.**
   `foundry/live_factory.py` targeted the wrong Foundry surface and returned
   **401**, aborting the run before any agent was mutated. Root cause, proven
   empirically against the live project:
   - **Wrong API object.** The eight platform agents are **Foundry Agent
     Service** *agents* (`/agents`, count 8), not OpenAI *Assistants*
     (`/assistants`, count 0). Agents are immutable-versioned; an update is a
     `POST /agents/{name}` carrying the **complete** definition, which the
     service turns into a new version and auto-promotes to `latest`.
   - **Wrong scope.** The data plane requires a bearer token for
     `https://ai.azure.com/.default` (200), not `cognitiveservices.azure.com`
     (401) — so the RBAC role is `Foundry User` /`Foundry Project Manager`, not
     `Cognitive Services User`.
   - **Wrong tool shape.** The Agent Service uses the **flat** Responses-API
     function-tool shape (`{type,name,description,parameters}`), not the nested
     Assistants `{type:"function", function:{…}}`.
3. **The fix (this branch).** `live_factory.py` + `test_live_factory.py` rewritten
   against the Agents API: `FOUNDRY_SCOPE = https://ai.azure.com/.default`; flat
   function tool; factory flow = `GET /agents/{name}` → deep-copy
   `versions.latest.definition` → append the `decision_tier_coordination_<role>`
   function tool idempotently → merge version `metadata` (`decision_tier_role`,
   `decision_tier_lever_catalog`, string values only) → `POST /agents/{name}`.
   The complete existing definition (model, instructions, reasoning, existing
   tools such as `ooa-agent`'s `fabric_dataagent`) is echoed verbatim so no agent
   capability is lost. 13 factory tests + the full 147-test decision suite pass.
4. **Operational follow-up (human-gated, after merge) — ✅ COMPLETE (2026-07-26,
   re-verified 2026-07-27; see §9.14).** Rebuild the
   `hcc-agent-host` image (CI watches `data-platform/decision/**`), bump
   `decisionApplyJobImage` in `sit.bicepparam` to the new merge-SHA tag, redeploy
   SIT, grant the job MI `Foundry User` on `ai-ihzhhpf-sit-eastus2`, then re-run
   the Foundry apply via the `az containerapp job update --yaml` template-swap
   method (ooa first, then fan out) per the runbook. `az containerapp job start
   --command/--args` overrides are ignored in this environment.

### 9.12 WS-B follow-up — DCA barrier Gold materialization (current)

One squash PR off `main` (branch `sprint-26/ws-b-barrier-gold`), **Data +
Governance** lanes, TDD-first. Closes the barrier **Gold materialization** item
deferred at §9.3 item 3 (and historically listed under "Still deferred" in §9.8 /
§9.9) and resolves the §7 open item on precompute-vs-runtime. Of the three
originally-deferred trio, only the ontology `hcp:Recommendation` / `hcp:Lever`
terms then remained deferred (WS-C runtime concern) — **now landed in §9.13.**

Discovered on pickup: the `dc-discharge-barrier-v1.schema.json` contract and the
`hcp:Barrier` ontology term — described in §9.3 items 3-4 as part of Slice 1 —
were **never actually landed on disk** (only the pure `derive_barriers` builder
shipped with #369). This follow-up lands all three together so the Gold fact is
contract- and ontology-conformant like every WS-A Gold fact.

1. **Contract** — `data/synthetic/schema/dc-discharge-barrier-v1.schema.json`
   (`DC-DISCHARGE-BARRIER-v1`, draft-07, `additionalProperties:false`,
   envelope + records, `_pseudonymisation_flag: true`), 1:1 with the Gold row.
2. **Gold builder** — `data-platform/decision/barriers/build_gold_barrier.py`:
   `build_discharge_barriers(candidates, produced_at)` projects the pure
   `derive_barriers` ranked barriers onto flat `gold.fact_discharge_barrier`
   rows (deterministic `barrierId`, 1-based `rank`, run metadata, camelCase
   contract keys); `discharge_barrier_envelope` for validation; the
   `_empty_schema` and `run()` Fabric entrypoints are `# pragma: no cover`.
   **`derive_barriers` is
   reused verbatim** — the collapse/rank logic is never duplicated. Orchestrated
   by `data-platform/notebooks/decision/run_decision_medallion.ipynb`.
3. **Ontology** — `hcp:Barrier` ICE (`subClassOf hcp:InformationContent`) +
   `hcp:barrierForWard` added to `reference-layer.ttl` (v0.5.0) with a crosswalk
   MVO row referencing `DC-DISCHARGE-BARRIER-v1` (`crosswalk.md` v0.6.0); STRICT
   two-layer conformance gate green (0 WARN / 0 FAIL).
4. **Tests** — 14 new offline tests (row shape / determinism / no-PHI / nullable
   / ranking / schema-conformance) in `barriers/tests/test_gold_barrier.py`;
   full decision-lane suite **161 tests OK**.
5. **Docs** — new `notebooks/decision/README.md`; `data-platform/decision/README.md`
   barrier row; `docs/DATA.md` (v0.12.0) Gold registry + WS-B subsection; §7 open
   item resolved; SemVer bumps on every edited doc.

**Guardrails held:** synthetic + deterministic only, no PHI (opaque
`candidate_key` + ontology ward IDs → aggregate Gold rows), **no LLM-guessed
numbers** (D2/D4). No infra / MCP / runtime change; Fabric lakehouse only.

### 9.13 WS-C follow-up — prescriptive ontology terms `hcp:Recommendation` / `hcp:Lever` (current)

One squash PR off `main` (branch `sprint-26/ws-c-recommendation-lever-ontology`),
**Governance (ontology) + Docs** lanes, TDD-first. Lands the **last** of the
three originally-deferred Sprint 26 items — the two prescriptive-tier ontology
terms. The runtime artefacts they name already shipped (the `DC-INSIGHT-v1`
recommendation beat via #369; the git-owned lever catalog
`data-platform/decision/levers/<role>.yaml` + `lever.schema.json`); this
follow-up gives them their reference-layer classes so beat 4 (the actionable
recommendation) is ontology-conformant like beats 1-3.

1. **Ontology** — `reference-layer.ttl` (v0.6.0): `hcp:Recommendation` and
   `hcp:Lever` ICE classes (`subClassOf hcp:InformationContent`) + the
   `hcp:recommendsLever` object property (Recommendation → Lever). The existing
   `hcp:DischargeRecommendation` is **re-parented** under `hcp:Recommendation`
   (a discharge-specific recommendation; still transitively an
   `InformationContent`, so no reasoner impact — additive refinement, no ID
   renamed or removed).
2. **Crosswalk** — `crosswalk.md` (v0.7.0): a `hcp:Recommendation` MVO row bound
   to `DC-INSIGHT-v1` (the recommendation beat; no batch Gold binding — runtime
   tuple) and a `hcp:Lever` row bound to the git-owned lever catalog
   (`lever.schema.json`, **no `DC-*` data contract** — a versioned config
   artefact, not dataset data).
3. **Tests** — 4 new offline assertions in
   `scripts/ontology/tests/test_contract_existence.py` (both classes + the
   relation declared; both have crosswalk rows; `hcp:Recommendation` → `DC-INSIGHT-v1`;
   `hcp:DischargeRecommendation` re-parented; STRICT gate exits 0). STRICT
   two-layer conformance green (0 WARN / 0 FAIL; 38 reference classes,
   35 crosswalk classes, 14 contracts).
4. **Docs** — this §9.13; §9.12 "only … remain deferred" line corrected; SemVer
   bumps on `reference-layer.ttl`, `crosswalk.md`, and this spec.

**Guardrails held:** ontology-only + docs; **no LLM-guessed numbers** (the
`expected_impact` on a recommendation is deterministic per D2/D4). No new
`DC-*` contract, no schema file, no infra / MCP / runtime change. With this
slice **all three originally-deferred Sprint 26 items are closed**; the live
Cosmos/Foundry `apply` (§9.11 step 4) was completed live 2026-07-26 and
re-verified 2026-07-27 (§9.14), so it is no longer an open operational step.

### 9.14 WS-C live apply — verified complete (current)

Documentation-only closeout (branch `sprint-26/ws-c-live-apply-closeout`,
**Platform-control + AI + Docs** lanes). Records the verified live state of the
§9.11 step-4 operational follow-up. No live mutation was performed — re-seeding
Cosmos would `409` (seed is not idempotent per the runbook) and Foundry
re-registration is unnecessary; this section captures the read-only evidence.

Live SIT ground truth re-verified 2026-07-27 (subscription
`66a9953a-…`, tenant `1337187a-…` MCAP164444):

1. **Decision-apply job** — `caj-decision-apply-ihzhhpf-sit` deployed on the
   VNet-integrated `cae-ihzhhpf-sit`, image `:a071fbe` (the Agents-API-fixed
   build pinned per §9.11), plan-first default command.
2. **RBAC** — the agent-host MI `id-ca-agent-host-ihzhhpf-sit` holds both
   `Cognitive Services User` and `Foundry User` on `ai-ihzhhpf-sit-eastus2`.
3. **Foundry registration** — all six decision-tier agents carry the
   `decision_tier_coordination_<role>` function tool + `decision_tier_role`
   metadata (csa/sba/orsa/bmca/dca at version 3, ooa at version 5); `ooa-agent`
   retains its `fabric_dataagent_preview` tool (no capability lost); the two
   non-decision agents (onboarding, data-quality) correctly carry no decision
   tool.
4. **Cosmos** — `plans` (pk `/episode_key`) and `proposed_actions`
   (pk `/plan_id`) containers live in `cosmos-csa-ihzhhpf-sit` / `csa`; seed
   applied 2026-07-26 (`{"applied": true, "approvedBy": "urruegg",
   "planCount": 5}`).

**Guardrails held:** read-only verification + docs only; no LLM-guessed numbers;
no infra / MCP / code change. Sprint 26 (Decision Ontology & Actionable-Insight
Layer, #335) is now functionally **complete** — all workstreams delivered and
all originally-deferred items closed and verified.
