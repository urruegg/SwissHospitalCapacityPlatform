# Sprint 25 — Trusted Signals to Proactive CSA + App Parity (Sprint 21 Refactor) — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-23 |
| **Author** | Urs Rueegg (with Copilot) |
| **Status** | Draft (brainstorming) |
| **Previous Version** | n/a (new document) |
| **Parent sprint** | Sprint 21 (#247) — this refactor extends and supersedes the S21 scope |
| **Parallel WIP** | #276 — Curavias parity app SIT deploy (sandbox, in flight); coordinate, do not fork |
| **Source idea** | `docs/superpowers/ideas/sprint 21 refactor epic.md` (8 refactor points) |
| **Predecessor designs** | S21 external-signals design v1.1.0; Curavias app parity design v1.0.1 |
| **Workflow** | Trunk-based parallel sprints per `docs/DEV_WORKFLOW.md` v1.0.0 + ADR-0038 |

> **For agentic workers:** This is a design spec (brainstorming output). The
> implementation plan is produced separately via `superpowers:writing-plans` and
> executed via `superpowers:subagent-driven-development` /
> `dispatching-parallel-agents`. The brainstorming HARD-GATE is satisfied: this
> design is approved before any production code. Spec + plan land on `main`
> before execution (DEV_WORKFLOW section 6).

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Context and relationship to existing work](#2-context-and-relationship-to-existing-work)
3. [Refactor epic mapping (8 points)](#3-refactor-epic-mapping-8-points)
4. [Architecture — six layers, frozen seams](#4-architecture--six-layers-frozen-seams)
5. [Contracts and ontology](#5-contracts-and-ontology)
6. [Requirements (FR-EXT-*/NFR-EXT-*)](#6-requirements-fr-ext-nfr-ext-)
7. [Real-vs-simulated source register (evidence)](#7-real-vs-simulated-source-register-evidence)
8. [Decomposition and parallelization (Approach A)](#8-decomposition-and-parallelization-approach-a)
9. [Coordination with parallel sprints](#9-coordination-with-parallel-sprints)
10. [Testing and CI gates](#10-testing-and-ci-gates)
11. [Document and issue update list](#11-document-and-issue-update-list)
12. [Risks](#12-risks)
13. [Open items and assumptions](#13-open-items-and-assumptions)

---

## 1. Goal and desired end state

Refactor the Sprint 21 Trusted External Signals capability into a
**plugin-based signal platform** that feeds a **probability-and-impact
risk-exposure engine**, which **proactively (advisory)** drives the Capacity
Simulation Agent (CSA) to pre-seed and simulate crisis scenarios *before* the
risk materialises, learns from every outcome through a **closed capture loop on
the Fabric IQ ontology**, and surfaces all of it in the Curavias app through
**per-channel live-vs-simulated badges** — with **zero fabricated data and zero
fabricated insights** at the app layer.

**Desired end state:**

* Any signal source onboards as a **plugin** (real API adapter, simulator, or
  internal channel) implementing one `SignalProvider` interface and emitting
  `DC-EXT-SIGNAL-v1`; provenance (`live` | `simulated`) is stamped from the
  plugin kind at ingest.
* External + internal signals join the 72h forecast in a `DC-RISK-EXPOSURE-v1`
  risk-exposure product that scores probability x impact per hazard/scope/window.
* The CSA **auto-detects** candidate crisis scenarios from risk-exposure
  breaches and **auto-runs** the simulation, but **scenario onboarding and every
  mitigation stay human-approved** (`approved-to-apply`) — advisory posture
  preserved per ADR-0033.
* Every `trigger -> scenario -> simulation -> decision -> outcome` is recorded as
  ontology-linked facts + CSA Cosmos agent-memory and fed back as grounding; a
  **trigger-precision / false-positive KPI** measures the loop. No model training.
* The Curavias CSA and Occupancy (OCA) boards show signals by channel with a
  **per-channel indicator badge** (connected-to-real vs simulated), the
  risk-exposure heat, the auto-proposed scenario + probability, and the live
  mitigation recommendation — all via live agent-host round-trips.

## 2. Context and relationship to existing work

Sprint 21 (#247) established the Trust-A external-signal ingestion, the
`DC-EXT-SIGNAL-v1` contract, the medallion + separate semantic model, the
ontology extension (5 classes), dual-path triggering, and the
`signal-triage-agent` + `data-quality-agent` extension. The v1.1.0 extension
added a forecast-overlay consumer proven live in SIT.

This refactor **extends** that base with the plugin architecture, the internal
channels, the risk-exposure engine, the proactive-advisory CSA loop, the closed
learning loop, and the app-layer badge/board wiring requested by the review. It
is a merged spec spanning two lanes:

* **Data + AI lanes** (`data-platform/`, `agents/`, `ai-models/`, `copilot/`,
  ontology, semantic model) — the signal platform and CSA loop.
* **Experience lane** (`apps/hcc-app-fluent`) — the per-channel badge and the CSA
  and OCA board wiring, which **consume** the platform through the parity
  design's already-frozen seams (`live-simulated-badge.ts`,
  `RoleBoardData.provenance`, `golden-source-client`, `agent-host-client`).

**Parallel WIP #276** is the Curavias parity app SIT deploy (sandbox, not
finished). This sprint **coordinates with, does not fork it**: it builds on the
`RoleBoard` / badge / `agent-host-client` seams the parity effort freezes, and
`M0` reconciles the canonical parity base before any app-layer task starts.

## 3. Refactor epic mapping (8 points)

| # | Refactor epic point | Layer | Where addressed |
|---|--------------------|-------|-----------------|
| 1 | Per-channel live-vs-simulated indicator badge on CSA + OCA | Experience | Section 4.6, `FR-EXT-022` |
| 2 | Signal-provider plugin pattern + internal channels | Data | Section 4.1, `FR-EXT-015/018` |
| 3 | Real API adapters for channels that have an API | Data | Section 4.1, Section 7, `FR-EXT-016` |
| 4 | Simulator plugins where no real API exists | Data | Section 4.1, Section 7, `FR-EXT-017` |
| 5 | Review AMA confirmed endpoints -> what is really connectable | Data | Section 7 |
| 6 | Probability risk-exposure -> trigger CSA -> onboard + run scenario | AI | Section 4.3-4.4, `FR-EXT-019/020` |
| 7 | CSA auto-identifies new crisis scenarios + proactive mitigation | AI | Section 4.4, `FR-EXT-020` |
| 8 | Closed learning loop on Fabric IQ ontology | AI | Section 4.5, `FR-EXT-021` |

## 4. Architecture — six layers, frozen seams

### 4.1 SignalProvider plugin layer (points 2, 3, 4, internal)

One `SignalProvider` interface + a registry manifest (`signal-providers.yaml`).
Each provider declares `id`, `kind: real-adapter | simulator | internal`,
`trustTier: A | B | C | internal`, `hazardTypes`, `cadence`, and emits
`DC-EXT-SIGNAL-v1`. **Provenance is derived from `kind` at ingest**
(`real-adapter` and `internal` -> `live`; `simulator` -> `simulated`) and carried
through the medallion so the app badge is enforceable at the data seam, not the
component.

* **Real adapters** where an API exists today (Section 7): SED FDSN, Alertswiss /
  Polyalert (poll), MeteoSwiss via STAC / Open-Meteo (heat).
* **Simulator plugins** for every source flagged "verify at build": deterministic
  offline generators (same shape as `signals_synth.py`), swappable to a real
  adapter later by a one-line manifest change with **no downstream impact**.
* **Internal providers** derive signals from the platform's own occupancy /
  discharge / staffing / OR / ED-arrival data and emit through the **same**
  interface as `trustTier=internal`, so the risk view is unified.

### 4.2 Ingest and medallion (extends `sprint-21/m3-medallion`)

All providers normalize to `DC-EXT-SIGNAL-v1` -> bronze / silver / gold `ext_*`,
adding `providerKind` and `provenance` columns. Test / Exercise / System
quarantine and dedup are unchanged from S21.

### 4.3 Risk-exposure engine (point 6 — NEW)

A deterministic notebook + a **new contract `DC-RISK-EXPOSURE-v1`**. It joins
gold signals (external + internal) with the 72h forecast + the m9 forecast
overlay per hospital / ward / canton / time-window, maps signal
`certainty` / `severity` / `dangerLevel` to a **probability** and forecast
headroom to an **impact**, and emits `gold.ext_fact_risk_exposure`. Threshold
breaches become **candidate crisis scenarios**. Deterministic and offline-testable
like every other medallion job.

### 4.4 Proactive CSA loop (points 6, 7 — fully advisory)

* `signal-triage-agent` (extended) consumes risk-exposure breaches; when no
  existing `ScenarioTemplate` family matches, it **auto-proposes a new
  `ScenarioCandidate`** (point 7's "identify a new crisis scenario"); it hands
  the qualifying event to `csa-agent`.
* `csa-agent` **auto-runs** the simulation and produces a mitigation
  recommendation *before the risk materialises*. **Scenario onboarding into the
  catalogue and every mitigation action stay human-approved** (`approved-to-apply`);
  no capacity / roster / bed / lever state mutates without HITL. The **CSA board
  is unchanged in shape**, extended with Foundry IQ + Fabric IQ-grounded data.

### 4.5 Closed capture / learning loop (point 8 — capture loop, no ML)

Record each `trigger -> scenario -> simulation -> human-decision -> outcome` as
**ontology-linked facts** (`gold.ext_fact_trigger_outcome`) plus CSA Cosmos
agent-memory. Prior outcomes for similar hazards are fed back as **grounding** so
triage suppresses known false-positives and ranks candidate scenarios. The loop
is measured by a **trigger-precision / false-positive-rate KPI** in the semantic
model. The Fabric IQ ontology is the end-to-end spine
(`SignalProvider -> ExternalSignal -> HazardEvent -> RiskExposure ->
ScenarioCandidate -> TriggerOutcome`). No model training in this scope.

### 4.6 App / experience layer (point 1 — parity, coordinates with #276)

* `live-simulated-badge.ts` (parity design) is driven by `provenance`
  **per channel** — a per-channel indicator batch on the **CSA** and **OCA**
  boards.
* **CSA board** (`/main/crisis`): signals-by-channel (each badged), risk-exposure
  heat, the auto-proposed scenario + probability, and the mitigation
  recommendation — all live `agent-host-client` round-trips; no hardcoded domain
  data or insight strings.
* **OCA board** (`/main/occupancy`): the forecast overlay (m9) plus the external
  channels feeding it, each badged.

## 5. Contracts and ontology

| Artefact | Change | Notes |
|----------|--------|-------|
| `DC-EXT-SIGNAL-v1` | **Extend** | Add `providerKind`, `provenance`; backwards-compatible (additive). |
| `DC-RISK-EXPOSURE-v1` | **New** | Probability x impact per hazard / scope / window; provenance + rationale carried for audit. |
| `signal-providers.yaml` | **New** | Registry manifest; schema-validated in CI. |
| Ontology | **Add classes** | `SignalProvider`, `RiskExposure`, `ScenarioCandidate`, `TriggerOutcome` + relationships into existing `ExternalSignal` / `HazardEvent` / `TriggerRule` / `ScenarioTemplate`. Reference plane now; Fabric IQ operational binding GA-gated per ADR-0014. |
| `external-signals.SemanticModel` | **Extend** | Risk-exposure measures + the trigger-precision / false-positive KPI. Separate model per ADR-0026 (verify-semantic-model.yml untouched). |

New ADR (proposed, ADR-0039): **plugin signal-provider architecture +
risk-exposure engine + proactive-advisory CSA loop + closed capture loop** —
records the advisory posture, provenance-integrity rule, and precision KPI.
Cross-links ADR-0033, ADR-0014, ADR-0024, ADR-0026, ADR-0008.

## 6. Requirements (FR-EXT-*/NFR-EXT-*)

Added to `docs/PRD.md` (MINOR bump) with traceability-matrix rows. Golden-task
fixtures carry `requirement:` front-matter referencing these IDs.

| ID | Requirement |
|----|-------------|
| `FR-EXT-015` | Onboard signal sources as plugins via one `SignalProvider` interface + registry manifest. |
| `FR-EXT-016` | Provide real API adapters for every source with a usable API (SED, Alertswiss, MeteoSwiss-bridge). |
| `FR-EXT-017` | Provide deterministic simulator plugins for every source without a usable API. |
| `FR-EXT-018` | Emit internal channels (occupancy / discharge / staffing / OR / ED) through the same interface as `trustTier=internal`. |
| `FR-EXT-019` | Compute a probability-and-impact risk exposure over signals + forecast (`DC-RISK-EXPOSURE-v1`). |
| `FR-EXT-020` | Auto-detect candidate crisis scenarios from risk breaches and auto-run advisory CSA simulations (HITL onboarding + mitigation). |
| `FR-EXT-021` | Record trigger-to-outcome as ontology-linked facts + agent memory; feed back as grounding (closed loop). |
| `FR-EXT-022` | Surface per-channel live-vs-simulated provenance on the CSA and OCA boards. |
| `NFR-EXT-PROV-001` | Provenance is derived at ingest from plugin kind and is immutable through the medallion and the app. |
| `NFR-EXT-ADV-001` | No external or internal signal auto-mutates state; the only automatic action is opening an advisory proposal. |
| `NFR-EXT-KPI-001` | Trigger precision / false-positive rate is measurable in the semantic model. |

## 7. Real-vs-simulated source register (evidence)

From the AMA review `docs/reviews/2026-07-17-ama-trusted-external-signals-review.md`
(confirmed as-of mid-July 2026 — a build-time verification list, not a guarantee).

| Source | Hazard | Plugin kind now | Basis |
|--------|--------|-----------------|-------|
| SED FDSN | Earthquake | **real-adapter** | Clean real-time event API confirmed. |
| Alertswiss / Polyalert | Civil-protection catch-all | **real-adapter (poll)** | Pollable JSON feed confirmed; CAP-Suisse GA ~2027. |
| MeteoSwiss | Heat / weather | **real-adapter (bridge)** | STAC / Open-Meteo-derived thresholds; per-item CAP API "verify at build". |
| BAG / FOPH | Respiratory surge | **simulator** until API confirmed | Feed maturity varies; simulate now. |
| BAFU, SLF, ASTRA, NABEL, Swissgrid, NCSC | Flood, avalanche, road, air, power, cyber | **simulator** | All flagged "verify at build" (risk R-02). |
| Internal (occupancy/discharge/staffing/OR/ED) | Capacity pressure | **internal** | Derived from platform gold tables. |

Swapping any simulator to a real-adapter later is a one-line manifest change; the
contract, medallion, engine, agents, and app are unaffected.

## 8. Decomposition and parallelization (Approach A)

Contract-first spine, then parallel fan-out — the same freeze-then-parallelize
pattern the parity design uses for `RoleBoard`. Each wave is a set of independent
sub-agent tasks, one issue -> one branch off `main` -> one squash PR
(DEV_WORKFLOW).

**M0 — Branch reconciliation + contract freeze (prerequisite, single driver).**
Run the git/gh verification the shell outage deferred (ahead/behind, merged
status of `sprint-21/*` and `curavias/*`); reconcile the stranded
`sprint-21/m3-medallion`; pick the **canonical parity base** among
`curavias/sprint-1-foundation-ooa`, `sprint1/curavias-parity-foundation-ooa`,
`feat/curavias-app-parity-spec`. Freeze `SignalProvider` +
`signal-providers.yaml` schema + `DC-RISK-EXPOSURE-v1` + ontology deltas + the
app badge/board contract additions. **This freeze unlocks the waves below.**

| Wave | Tasks (each an independent sub-agent slice) | Depends on |
|------|---------------------------------------------|-----------|
| **1** | (a) real-adapter plugins; (b) simulator plugins; (c) internal-channel plugins; (d) medallion `providerKind`/`provenance` extension | M0 |
| **2** | (e) risk-exposure engine + `DC-RISK-EXPOSURE-v1`; (f) ontology extension (4 classes); (g) semantic-model measures + precision KPI; (h) triggering (Activator/poller) | M0 (contracts) |
| **3** | (i) `signal-triage-agent` proactive + scenario auto-propose; (j) `csa-agent` closed capture loop + Cosmos memory; (k) app per-channel badge + CSA/OCA board wiring (coordinate #276) | Waves 1-2 |
| **4** | (l) end-to-end synthetic walk-through + precision-KPI evidence; (m) doc/issue reconciliation | Waves 1-3 |

Waves 1 and 2 are fully parallel (no cross-touch); wave 3 needs light chain
integration; wave 4 is closeout. Each slice is offline-testable in CI.

## 9. Coordination with parallel sprints

* **#276 (parity app SIT deploy)** — do not fork. Wave-3 task (k) builds on the
  frozen `RoleBoard` / badge / `agent-host-client` seams; M0 picks the canonical
  base and rebases onto it. If #276 has not frozen those seams when wave 3
  starts, task (k) is blocked and re-sequenced after #276's freeze.
* **`sprint-21/m3-m9` worktrees** — waves 1-2 extend these branches' outputs
  rather than re-authoring; M0 verifies they are current on `main` before
  extension.
* **Control-plane files** (`AGENTS.md`, `.github/copilot/mcp.json`,
  `docs/adr/*`) — no new MCP server is required (reuses `github-mcp`,
  `fabric-mcp`, `cosmos-mcp`); changes go through CODEOWNERS-gated PRs per the
  shared refusal rules.

## 10. Testing and CI gates

* Fixture-first / TDD: `SignalProvider` conformance, simulator determinism,
  risk-exposure math, trigger-rule + scenario-candidate arbitration, and the
  triage-to-CSA handoff are unit-tested offline (pattern from
  `external-signals.yml` / `csa-checks.yml`).
* `ontology-conformance.yml` covers the 4 new classes; `eval-goldens.yml` replays
  `signal-triage-agent` + `csa-agent` + `data-quality-agent` fixtures;
  `verify-semantic-model.yml` stays untouched (separate model, ADR-0026).
* App layer follows the parity design's Vitest + Playwright/axe patterns:
  per-channel badge provenance, CSA/OCA board render, one live agent-host smoke.
* markdownlint + link-check + mojibake gates on every edited doc; SemVer bump per
  copilot-instructions section 9. CI green is the merge proof; a human merges.

## 11. Document and issue update list

Full-scope reflection (each is a wave-4 or per-task doc bump):

| Artefact | Update |
|----------|--------|
| `docs/superpowers/specs/2026-07-23-sprint-25-...-design.md` | This spec (new, v1.0.0). |
| `docs/sprints/sprint-25-...-and-app-parity.md` | Sprint doc + tracker issue body (new). |
| `docs/superpowers/specs/2026-07-17-sprint-21-...-design.md` | MINOR/MAJOR bump: point to this refactor as the superseding scope. |
| `docs/superpowers/specs/2026-07-21-curavias-app-prototype-parity-design.md` | MINOR bump: per-channel badge + CSA/OCA board wiring to the risk-exposure + proactive loop. |
| `docs/PRD.md` | MINOR bump: `FR-EXT-015..022` + NFRs + traceability rows. |
| `docs/adr/0039-*.md` | New ADR (plugin + risk-exposure + proactive-advisory + capture loop). |
| `AGENTS.md` | `signal-triage-agent` + `csa-agent` scope note (proactive advisory); no allow-list change. |
| `docs/DATA.md` | `DC-RISK-EXPOSURE-v1` + `DC-EXT-SIGNAL-v1` extension entries. |
| GitHub issue #247 | Comment: refactor moved to Sprint 25 tracker; link this spec + #276. |
| New Sprint 25 tracker issue | Filed from `sprint-tracker.yml` (Appendix A of the sprint doc). |

## 12. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| #276 parity seams not frozen when wave 3 starts | Medium | Medium | M0 gate; re-sequence task (k) after #276 freeze; keep signal/data waves independent. |
| `sprint-21/m3-medallion` stranded / stale base | Medium | Medium | M0 reconciliation before waves 1-2 extend it. |
| Proactive loop erodes advisory posture | Low | High | HITL onboarding + mitigation; `NFR-EXT-ADV-001`; ADR-0039 records the gate. |
| False-positive trigger noise | Medium | High | Test/Exercise quarantine + thresholds + trust-tier + capture-loop precision feedback. |
| Source endpoint / licence drift | Medium | Medium | Plugin isolation; simulators pin CI; `licence` mandatory; Section 7 is a build-time verification list. |
| Fabric IQ operational binding not GA | High | Low | Reference plane now; SIT proof; PROD gated per ADR-0014 / issue #270. |

## 13. Open items and assumptions

* Exact `SignalProvider` interface fields and `DC-RISK-EXPOSURE-v1` schema are
  finalized in M0 before the freeze.
* The probability mapping (certainty/severity -> probability) and impact mapping
  (forecast headroom -> impact) constants are defined in M0 with the domain SME.
* Canonical parity base branch is selected in M0 (git/gh verification pending the
  shell recovery).
* `ScenarioCandidate` -> `ScenarioTemplate` promotion is a human-approved step;
  the auto-proposal only drafts.
* Internal-channel signal definitions (which derived metrics become signals) are
  confirmed in wave 1 task (c).
