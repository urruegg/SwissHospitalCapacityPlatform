# Sprint 26 — Decision Ontology & Actionable-Insight Layer — Design Spec

| Field | Value |
| ----- | ----- |
| **Version** | 1.2.0 |
| **Date** | 2026-07-25 |
| **Author** | @urruegg |
| **Status** | Approved — in delivery (WS-A done; WS-B/C/D vertical slice merged #369; fan-out to BMCA/ORSA/SBA/CSA in delivery) |
| **Previous Version** | 1.1.0 (added §9 delivery status & next step) |
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

- Whether the barrier model (`fact_discharge_barrier`) is precomputed in Gold or derived at
  runtime — decide in WS-B against the DCA lever formulas.
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
> **vertical slice** (OOA -> DCA, all 5 beats) are merged to `main` (#369). The
> current slice **fans the proven pattern out** to the remaining four roles
> (BMCA, ORSA, SBA, CSA) — one curated lever each, deterministic impact, and
> agent-pack + golden-task upgrades (see §9.5).

### 9.1 Work-stream progress

| WS | Status | Evidence / notes |
| -- | ------ | ---------------- |
| **WS-A — Foresight tier** | ✅ **Done, merged to `main`** | Deterministic forecast+driver+signal generator, 3 Gold tables, `hcp:Forecast/Driver` + `hcp:ExternalSignal` reuse, 2 contracts (`DC-OCCUPANCY-FORECAST-v1`, `DC-FORECAST-DRIVER-v1`), 16 unit tests. Live SIT evidence captured. |
| **WS-B — Lever catalog + deterministic impact** | ✅ **Vertical slice merged (#369); fan-out in delivery** | OOA+DCA levers, `compute_expected_impact`, `DC-INSIGHT-v1` contract, barrier model + `hcp:Barrier` landed via #369. Current slice adds the four fan-out levers (`BMCA-REBALANCE-CENSUS`, `ORSA-DEFER-ELECTIVE`, `SBA-FLEX-STAFF-BEDS`, `CSA-ACTIVATE-SURGE`) + formulas + tests. |
| **WS-C — Decision + Coordination runtime (Cosmos)** | ✅ **Vertical slice merged (#369); fan-out in delivery** | `Store`/`plan_runtime` (102%→94% recompute + OOA→DCA handoff) landed via #369. Current slice adds `coordination/seed_fanout.py` (self-owned golden thread per fan-out role). Live Cosmos/Foundry `apply` still deferred. |
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
3. **DCA barrier model** — deterministic pure builder + `dc-discharge-barrier-v1.schema.json`; **Gold materialization deferred** to a follow-up (confirmed).
4. **Ontology** — add **only `hcp:Barrier`** (+ crosswalk MVO row, STRICT conformance); defer `hcp:Recommendation`/`hcp:Lever` to WS-C runtime (confirmed).
5. **Docs** — `data-platform/decision/README.md`; PRD `FR-DEC-*` / `NFR-DEC-*` + §7 traceability; SemVer bumps.

**Confirmed decisions (@urruegg, 2026-07-24):** barrier builder+schema now / defer Gold materialization · add only `hcp:Barrier` now · one cohesive PR.

### 9.4 Resume checklist

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
