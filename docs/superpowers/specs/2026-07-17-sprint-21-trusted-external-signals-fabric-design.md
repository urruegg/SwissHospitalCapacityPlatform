# Sprint 21 — Trusted External Signals: Fabric Ingestion, Ontology, Semantic Model & Event Triggering — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-07-21 |
| **Author** | Urs Rueegg |
| **Status** | Approved — v1.1.0 extension |
| **Previous Version** | 1.0.0 (added §20 forecast-overlay + SIT IQ-layer proof extension; FR-EXT-010..014) |
| **Anchor triggers** | AMA review `docs/reviews/2026-07-17-ama-trusted-external-signals-review.md`; source design `docs/reviews/2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md`; review session with a Hospital Data Scientist (2026-07-17) |
| **Runtime posture** | GitHub Copilot coding agent + Superpowers-first execution; advisory/HITL unchanged; agents realised as Markdown packs + MCP config (ADR-0002); Fabric items authored via skills + REST post-deploy (no live deploy from repo) |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Context and problem statement](#2-context-and-problem-statement)
3. [Scope](#3-scope)
4. [Architecture — end-to-end dual-binding flow](#4-architecture--end-to-end-dual-binding-flow)
5. [Product domain and medallion data product](#5-product-domain-and-medallion-data-product)
6. [Data contract DC-EXT-SIGNAL-v1](#6-data-contract-dc-ext-signal-v1)
7. [Ontology extension](#7-ontology-extension)
8. [Semantic model](#8-semantic-model)
9. [Event triggering (dual-path)](#9-event-triggering-dual-path)
10. [Agents and conflict resolution](#10-agents-and-conflict-resolution)
11. [Governance, compliance and residency](#11-governance-compliance-and-residency)
12. [Requirements (FR-EXT-*) and traceability](#12-requirements-fr-ext--and-traceability)
13. [Component boundaries](#13-component-boundaries)
14. [Testing and CI gates](#14-testing-and-ci-gates)
15. [Implementation plan (milestones)](#15-implementation-plan-milestones)
16. [Risk register](#16-risk-register)
17. [Dependencies](#17-dependencies)
18. [Definition of done](#18-definition-of-done)
19. [References](#19-references)
20. [v1.1.0 extension — forecast overlay & SIT IQ-layer proof](#20-v110-extension--forecast-overlay--sit-iq-layer-proof)

---

## 1. Goal and desired end state

Establish a **Trusted External Signals** capability in Microsoft Fabric that ingests
Trust-tier-A Swiss authority hazard feeds into the data lake, normalizes them to a
single CAP-aligned data contract, exposes them as a governed data product +
semantic model + ontology domain, and fires **advisory** Capacity Simulation
Agent (CSA) runs through a dual-path event trigger — all well-integrated with the
existing platform ecosystem.

**Desired end state:**

* Four Trust-A source connectors (MeteoSwiss, Alertswiss/Polyalert, SED, BAG/FOPH)
  normalize to `DC-EXT-SIGNAL-v1`.
* Normalized signals land dual-bound: **Eventhouse KQL** (hot/real-time) and the
  **OneLake Lakehouse medallion** (bronze -> silver -> gold Delta) for history,
  dedup, provenance and semantics.
* A separate Direct Lake **`external-signals.SemanticModel`** exposes signal,
  trigger, severity and Lage-tier measures.
* The ontology gains `TrustedSource`, `HazardType`, `ExternalSignal`,
  `HazardEvent`, `TriggerRule` classes (reference plane now; Fabric IQ operational
  binding GA-gated per ADR-0014).
* A new **`signal-triage-agent`** owns dedup, conflict arbitration and trigger
  routing, then hands off to `csa-agent`; the `data-quality-agent` gate is extended
  for the new contract.
* Triggering targets **Fabric Activator/Reflex** (GA-gated) with a working
  **GitHub-workflow + agent-host poller** GA-bridge.

## 2. Context and problem statement

The CSA today runs crisis/scenario simulations (families F1-F8) from human-filed
issues. The 2026-07-17 review with a Hospital Data Scientist established that
Switzerland publishes authoritative, machine-readable hazard feeds (heat, floods,
earthquakes, epidemic surge, civil-protection alerts) that should **automatically
pre-seed** CSA runs, without weakening the advisory / human-in-the-loop posture.

The platform has no external-signal ingestion, no `ExternalSignal` ontology class,
and no `FR-EXT-*` requirements. This sprint fills that gap using existing
conventions (medallion, separate semantic model, three-plane ontology,
scheduled-workflow triggers, agent packs).

## 3. Scope

### In scope

* Four source connectors + extensible connector pattern for all Trust-A sources.
* `DC-EXT-SIGNAL-v1` contract + JSON Schema + offline synthetic seeder.
* Medallion notebooks (bronze/silver/gold) + Eventhouse route.
* `external-signals.SemanticModel` (Direct Lake, separate model).
* Ontology extension (reference TTL + crosswalk rows; operational binding GA-gated).
* Dual-path triggering (Activator/Reflex config authored + GA-gated; poller bridge live).
* `signal-triage-agent` pack + `data-quality-agent` extension + AGENTS.md registry.
* `ADR-0033`, `FR-EXT-*` PRD additions, CI gates.

### Out of scope (explicitly deferred)

* Trust-tier B/C source onboarding (human-curated only; pattern documented, not built).
* Full CAP-Suisse federal integration (target ~2027; bridged via pollable feeds today).
* Live Azure/Fabric deployment (artefacts are authored + CI-gated; deploy is a
  separate `approved-to-apply` step via the usual skill/REST flow).
* Any change to the CSA simulation engine beyond consuming pre-seeded triggers.

## 4. Architecture — end-to-end dual-binding flow

```text
Trusted Swiss sources (Trust-A)
  MeteoSwiss STAC/Open-Meteo | Alertswiss/Polyalert JSON | SED FDSN | BAG/FOPH
        | (4 source connectors — scheduled poll today; Logic App/Function target)
        v
  Normalize -> DC-EXT-SIGNAL-v1 envelope (CAP-aligned)
        |
        v
  Event Hub (evh-ihzhhpf) --> Fabric Eventstream (es-ihzhhpf-events; +route eventKind=ext-signal)
        |                                   |
        |                                   +--> Eventhouse KQL DB (HOT: real-time, Activator source)
        v
  OneLake Lakehouse medallion (COLD: history, dedup, provenance, semantics)
    Files/Bronze/external-signals/<source>/<date>/*.json
      -> silver.ext_signal (typed, normalized, deduped; Test/Exercise quarantined)
        -> gold.ext_dim_source | ext_dim_hazard_type | ext_dim_region
           gold.ext_fact_signal | ext_fact_trigger_event
        |
        v
  external-signals.SemanticModel (Direct Lake, separate model, role SignalsReadOnly)
        |
        v   TRIGGER (dual-path)
   Fabric Activator/Reflex (GA-target) ----+
   GH-workflow + agent-host poller (bridge) +--> signal-triage-agent
        |                                        (dedup + conflict arbitration + TriggerRule)
        v                                        |
   hands off ----------------------------------> csa-agent (Prepare/Run/Evaluate/Recommend, HITL)
        |
        v
   Advisory proposal on Whiteboard "Krisen & Szenarien" card (approved-to-apply)
```

Rationale for **dual-binding (Approach A)**: it is the only realisation that
satisfies both real-time triggering (Eventhouse hot path feeding Activator) and a
governed data product + Direct Lake semantic model + provenance history (Lakehouse
cold path). It reuses the exact dual time-series binding pattern already documented
in `docs/ontology/crosswalk.md` for `Bed` / `bed-state`.

## 5. Product domain and medallion data product

New data product domain **`external-signals`**, beside `bva`, `evidence`,
`reference`, `csa`.

* Notebooks: `data-platform/notebooks/external-signals/`
  * `ingest_bronze_signals.py` -> `Files/Bronze/external-signals/<source>/<date>/*.json`
    (raw payload + `rawHash` provenance).
  * `build_silver_signals.py` -> `silver.ext_signal` (typed, normalized to contract,
    deduped on the derived key; `status != Actual` routed to
    `silver.ext_signal_quarantine`).
  * `build_gold_signals.py` ->
    * dims: `gold.ext_dim_source`, `gold.ext_dim_hazard_type`, `gold.ext_dim_region`
    * facts: `gold.ext_fact_signal` (one row per active normalized signal — severity,
      `defaultLageTier`, `mappedScenarioTemplate`), `gold.ext_fact_trigger_event`
      (audit row per trigger evaluation/fire -> CSA `runId`, for provenance + eval).
* Gold tables are **`ext_`-prefixed** to avoid colliding with operational
  `gold.dim_*` / `gold.fact_*` (same anti-collision rule as `bva_`).
* Scripts: `data-platform/scripts/external-signals/`
  * `connectors/base_connector.py`, `connectors/{meteoswiss,alertswiss,sed,bag}.py`
  * `normalize.py` (source payload -> `DC-EXT-SIGNAL-v1`)
  * `trigger_rules.yaml` (TriggerRule definitions + arbitration precedence)
  * `signals_synth.py` (dependency-free synthetic seeder; optional `requests`/`pyarrow`)
  * `tests/` (offline unit tests, `unittest`)

Connector inventory:

| Connector | Endpoint | Cadence | Hazard | Primary scenario |
|-----------|----------|---------|--------|------------------|
| `meteoswiss` | STAC `data.geo.admin.ch/api/stac/v1` + Open-Meteo heat thresholds | 15 min | heat / flood | F8 heatwave |
| `alertswiss` | Polyalert / Alertswiss JSON (CAP) | 5 min | govt catch-all | maps by CAP hazard |
| `sed` | FDSN `eida.ethz.ch/fdsnws/event/1/query` | 5 min | earthquake | F1 infra / F3 MCI |
| `bag` | FOPH/BAG surveillance (RSV/respiratory) | daily | epidemic surge | F6 RSV surge |

## 6. Data contract DC-EXT-SIGNAL-v1

Authored as `data/synthetic/schema/dc-ext-signal-v1.schema.json` and documented in
`docs/DATA.md` (family `DC-EXT-*`). CAP-Suisse (OASIS CAP Swiss profile) aligned.

```yaml
signalId:            string   # stable dedup identity
sourceId:            string   # FK -> ext_dim_source
sourceAuthority:     string   # MeteoSwiss | BABS/FOCP | SED-ETH | FOPH/BAG | ...
trustTier:           enum     # A | B | C  (this sprint: A only auto-evaluated)
capIdentifier:       string   # CAP <identifier> when present
hazardType:          string   # FK -> ext_dim_hazard_type
severity:            enum     # Minor | Moderate | Severe | Extreme
certainty:           enum     # Observed | Likely | Possible | Unlikely
urgency:             enum     # Immediate | Expected | Future | Past
dangerLevel:         integer  # 1..5 (Swiss warning scale where applicable)
region:
  cantons:           [string] # ISO canton codes
  nuts:              [string] # NUTS region codes
  geoPolygon:        object   # optional GeoJSON
effective:           datetime
onset:               datetime
expires:             datetime
uri:                 string   # source deep-link
status:              enum     # Actual | Test | Exercise | System
mappedScenarioTemplate: string  # -> reuse ScenarioTemplate (F1..F8)
defaultLageTier:     integer  # 1 | 2 | 3  (pre-seeds ADR-0024 Lage tier)
provenance:
  ingestedAt:        datetime
  connectorVersion:  string
  licence:           string   # source licence / attribution obligation
  rawHash:           string   # sha256 of raw payload
```

* **Dedup key** (derived): `sourceId + capIdentifier + hazardType + region + onset`
  bucketed to a time window; collapses overlapping re-publishes.
* **Noise governance:** `status in {Test, Exercise, System}` is quarantined and
  **never** triggers CSA (`FR-EXT-005`).
* **Severity -> Lage:** `defaultLageTier` pre-seeds Normallage/Besondere/
  Ausserordentliche (Tier 1/2/3) per ADR-0024; the CSA tier classifier remains
  authoritative.

## 7. Ontology extension

Three-plane pattern per `docs/ontology/crosswalk.md` + ADR-0014. New reference-layer
classes authored now in `docs/ontology/reference-layer.ttl`; Fabric IQ **operational**
binding is GA-gated/deferred exactly like the existing entities.

| Reference class (new) | BFO/OBO anchor | Fabric IQ entity (GA-gated) | Data contract | Time-series binding |
|-----------------------|----------------|-----------------------------|---------------|---------------------|
| `hcp:TrustedSource` | IAO ICE / OOSTT org | `TrustedSource` | `DC-EXT-SIGNAL-v1` (sourceId) | static (dim) |
| `hcp:HazardType` | environmental-hazard align | `HazardType` | contract enum | static (dim) |
| `hcp:ExternalSignal` | IAO information content entity | `ExternalSignal` | `DC-EXT-SIGNAL-v1` | **dual: silver/gold Delta + Eventhouse** |
| `hcp:HazardEvent` | BFO occurrent | `HazardEvent` | derived | time-series |
| `hcp:TriggerRule` | IAO directive information entity | `TriggerRule` | `trigger_rules.yaml` | static |
| `hcp:AffectedRegion` | reuse existing Location | (reuse) | region block | — |
| reuse `ScenarioTemplate`, `LageTier` | — | (reuse) | — | — |

Relations: `hcp:signalFromSource`, `hcp:signalIndicatesHazard`,
`hcp:signalAffectsRegion`, `hcp:triggerRuleMapsScenario` (-> `ScenarioTemplate`),
`hcp:signalPreseeds` (-> `LageTier`). The `ontology-conformance.yml` gate covers the
new TTL; every ontology PR updates `crosswalk.md` in the same PR.

## 8. Semantic model

New **`external-signals.SemanticModel`** (Direct Lake) as a **separate** model,
mirroring the evidence-model decision (ADR-0026) so it stays outside the
`capacity-dashboard` exact-count CI gate (`verify-semantic-model.yml`).

* Tables: `ext_fact_signal`, `ext_fact_trigger_event`, `ext_dim_source`,
  `ext_dim_hazard_type`, `ext_dim_region`.
* Role: `SignalsReadOnly`.
* Measures: `Active Signals`, `Signals by Severity`, `Highest Lage Tier`,
  `Triggers Fired (24h)`, `Mean Time Source->Trigger`, `Signals Quarantined`.
* Unlike `capacity-dashboard` (no date dim), the signal facts carry native
  `effective/onset/expires` timestamps, so time-intelligence measures are
  authorable without a shared `dim_time`.

## 9. Event triggering (dual-path)

* **Target — Fabric Activator/Reflex:** a severity/`TriggerRule` rule on the
  Eventhouse `ExternalSignal` stream; config authored at
  `data-platform/external-signals/activator/reflex-rule.json` and **GA-gated** per
  the ADR-0014 preview-resource ledger.
* **Bridge (works today):** `.github/workflows/ext-signal-poll.yml` scheduled
  workflow reads `gold.ext_fact_signal` (via agent-host / `fabric-mcp`) and invokes
  `signal-triage-agent`. Mirrors the existing `csa-scenario-sync.yml` /
  `bva-sim-refresh.yml` scheduled-workflow pattern.

Both paths converge on the same `signal-triage-agent` entry contract, so the switch
from bridge to Activator at GA is configuration, not redesign.

## 10. Agents and conflict resolution

### `signal-triage-agent` (new)

* **Registry:** AGENTS.md §1 row; MCP `github-mcp` (write), `fabric-mcp` (read).
* **Side-effect ceiling:** `write` (opens issues/PRs + hands off; never runs simulations).
* **Trigger:** Activator/Reflex webhook (GA) or poller bridge (today);
  `@signal-triage-agent` mention for manual.
* **Responsibilities:**
  1. **Dedup** — collapse overlapping signals on the derived key into one
     `HazardEvent` (e.g. MeteoSwiss + Alertswiss both firing heat over ZH).
  2. **Conflict arbitration** — when distinct hazards overlap, rank by
     `defaultLageTier` (Ausserordentliche > Besondere > Normallage), then severity,
     then certainty; pick the primary `mappedScenarioTemplate`, record secondaries
     as context.
  3. **TriggerRule match** — evaluate threshold (severity/dangerLevel) +
     `status=Actual` + `trustTier=A`. Below threshold -> log to
     `ext_fact_trigger_event` as `evaluated-no-trigger`; never escalate.
  4. **Handoff** — open a CSA issue/PR referencing the `HazardEvent`, pre-seeded
     `ScenarioTemplate` and `LageTier`. CSA remains the runner; Run stays gated by
     `approved-to-apply`.
* **Golden tasks:** >=1 happy-path (heat dual-source dedup -> F8 handoff) and
  >=1 failure-mode (Exercise-status signal -> quarantined, no trigger).

### `data-quality-agent` extension

Add `DC-EXT-SIGNAL-v1` to its Bronze/Silver/Gold gate: schema conformance,
dedup-key uniqueness, quarantine of Test/Exercise/System, provenance completeness,
licence field present. Golden-task updated.

### Conflict-resolution rules

`data-platform/scripts/external-signals/trigger_rules.yaml` holds TriggerRule
definitions + arbitration precedence; unit-tested offline like the CSA scenario tests.

## 11. Governance, compliance and residency

* **ADR-0033 — external-trigger governance** records: Trust-A signals as **advisory**
  triggers; dual-path triggering with Activator GA-gating; trust-tier policy
  (A auto-evaluated, B/C human-curated only); Test/Exercise/System quarantine;
  licence/attribution obligations (opendata.swiss / authority terms); non-PHI,
  synthetic-only demo residency (ADR-0013). Cross-links ADR-0014, ADR-0024, ADR-0026.
* **Residency:** demo scope `westus2`, synthetic fixtures only, no PHI (ADR-0013).
  External feeds are public authority data; no personal data ingested.
* **HITL preserved:** no external signal auto-mutates capacity/roster/bed state; the
  only automatic action is opening an advisory CSA proposal for human approval.

## 12. Requirements (FR-EXT-*) and traceability

Added to `docs/PRD.md` (MINOR bump) with traceability-matrix rows:

| ID | Requirement |
|----|-------------|
| `FR-EXT-001` | Ingest Trust-A Swiss authority hazard feeds into the data lake. |
| `FR-EXT-002` | Normalize every source to `DC-EXT-SIGNAL-v1`. |
| `FR-EXT-003` | Activate advisory CSA runs from qualifying signals (dual-path trigger). |
| `FR-EXT-004` | Persist provenance + trigger audit (`ext_fact_trigger_event`). |
| `FR-EXT-005` | Noise governance: quarantine Test/Exercise/System; threshold gating. |
| `FR-EXT-006` | Align to CAP-Suisse standard; bridge with pollable feeds until federal GA. |
| `FR-EXT-ONT-001` | Add ExternalSignal/TrustedSource/HazardType/HazardEvent/TriggerRule classes. |
| `FR-EXT-ONT-002` | Maintain reference<->operational<->contract crosswalk for the new classes. |
| `NFR-EXT-ONT-001` | Operational (Fabric IQ) binding GA-gated per ADR-0014. |
| `FR-EXT-GOV-001` | Enforce trust-tier + HITL + advisory-only trigger policy. |
| `NFR-EXT-GOV-001` | Record source licence/attribution for every ingested signal. |
| `NFR-EXT-GOV-002` | No PHI/personal data; public authority feeds + synthetic fixtures only. |

Golden-task fixtures carry `requirement:` front-matter referencing these IDs.

## 13. Component boundaries

| Unit | Responsibility | Depends on | Consumers |
|------|----------------|------------|-----------|
| connectors | fetch + emit `DC-EXT-SIGNAL-v1` | source endpoints / fixtures | normalize |
| normalize | payload -> contract envelope | contract schema | bronze notebook |
| medallion notebooks | bronze->silver->gold Delta | Lakehouse, contract | semantic model, agent |
| eventstream route | append envelope to Eventhouse | Eventstream, Event Hub | Activator |
| semantic model | Direct Lake measures | gold tables | dashboards |
| trigger_rules | TriggerRule + arbitration | gold facts | signal-triage-agent |
| signal-triage-agent | dedup/arbitrate/route/handoff | gold, rules, github | csa-agent |
| csa-agent | scenario run (unchanged) | handoff issue/PR | Whiteboard card |

Each unit is independently testable; connectors and rules run fully offline in CI.

## 14. Testing and CI gates

* **New** `.github/workflows/external-signals.yml` — runs connector/normalize/
  trigger-rules `unittest` suite offline (pattern from `bva-generator.yml` /
  `csa-checks.yml`).
* `ontology-conformance.yml` — covers new TTL classes.
* `eval-goldens.yml` — replays `signal-triage-agent` + updated `data-quality-agent`
  fixtures.
* `verify-semantic-model.yml` — **untouched** (new model is separate, ADR-0026).
* markdownlint + link-check + mojibake gates on all docs; every edited doc bumps
  SemVer per copilot-instructions §9.
* Fixture-first / TDD: contract + rules tests authored before notebook/agent logic.

## 15. Implementation plan (milestones)

Milestone-by-milestone TDD tasks. Detailed task breakdown to be expanded in
`docs/superpowers/plans/2026-07-17-sprint-21-trusted-external-signals-fabric-plan.md`
(writing-plans step). High-level shape:

| # | Milestone | Deliverable | DoD |
|---|-----------|-------------|-----|
| M0 | Baseline + scaffolding | domain folders, empty test harness, baseline suite green | folders committed; CI green |
| M1 | Contract + governance | `dc-ext-signal-v1.schema.json`, `docs/DATA.md` entry, ADR-0033, `FR-EXT-*` in PRD | schema validates; PRD matrix updated; ADR Accepted-ready |
| M2 | Connectors + normalize | 4 connectors, `normalize.py`, `signals_synth.py`, offline tests | `external-signals.yml` green offline |
| M3 | Medallion notebooks | bronze/silver/gold notebooks + dedup + quarantine | gold `ext_*` tables produced from synthetic seed |
| M4 | Ontology extension | reference TTL classes + crosswalk rows | `ontology-conformance.yml` green |
| M5 | Semantic model | `external-signals.SemanticModel` TMDL + role + measures | model validates; `verify-semantic-model.yml` untouched/green |
| M6 | Triggering | `trigger_rules.yaml`, `reflex-rule.json` (GA-gated), `ext-signal-poll.yml` | rules unit-tested; poller invokes agent |
| M7 | Agents | `signal-triage-agent` pack + golden tasks; `data-quality-agent` extension; AGENTS.md row | `eval-goldens.yml` green |
| M8 | Integration + docs | end-to-end synthetic walk-through; doc version bumps; references reconciled | all gates green; DoD met |

## 16. Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Activator/Reflex still preview at demo time | High | Medium | Poller bridge is the live path; Activator config is GA-gated and additive |
| Source endpoint/schema drift | Medium | Medium | Connectors isolate parsing; synthetic fixtures pin CI; normalize is the single contract seam |
| Eventhouse infra scaffold-only (REST post-deploy) | High | Low | Same pattern as existing eventstream; documented in infra module + ADR-0014 ledger |
| False triggers / alert noise | Medium | High | Test/Exercise quarantine + threshold + trust-tier A + HITL approval gate |
| Licence/attribution non-compliance | Low | High | `licence` mandatory in contract; `NFR-EXT-GOV-001` gate in data-quality-agent |
| Semantic-model CI collision | Low | Medium | Separate model per ADR-0026; `verify-semantic-model.yml` untouched |

## 17. Dependencies

* ADR-0014 (Fabric IQ GA gating), ADR-0024 (Lage tiers), ADR-0026 (separate
  semantic model precedent), ADR-0013 (demo residency).
* Existing Event Hub (`evh-ihzhhpf`) + Eventstream (`es-ihzhhpf-events`).
* `csa-agent` (handoff consumer), `data-quality-agent` (contract gate).
* Skills: `eventstream-authoring`, `spark-authoring`,
  `fabric-semantic-model-authoring`, `e2e-medallion-architecture`.

## 18. Definition of done

* All CI gates green (external-signals, ontology-conformance, eval-goldens,
  markdownlint, link-check, mojibake).
* Synthetic end-to-end walk-through produces `gold.ext_fact_signal` +
  `ext_fact_trigger_event` and a `signal-triage-agent` -> CSA handoff issue/PR.
* ADR-0033 authored; `FR-EXT-*` in PRD + traceability matrix; ontology crosswalk
  updated; AGENTS.md registry row added.
* Advisory/HITL posture preserved end-to-end; no PHI; licence recorded per signal.
* Every edited doc bumped per SemVer §9.

## 19. References

1. AMA review — `docs/reviews/2026-07-17-ama-trusted-external-signals-review.md`
2. Source design — `docs/reviews/2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md`
3. Ontology crosswalk — `docs/ontology/crosswalk.md`
4. ADR-0014 — `docs/adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md`
5. ADR-0024 — `docs/adr/0024-csa-tier-classifier-rules.md`
6. ADR-0026 — `docs/adr/0026-evidence-readiness-measure-ownership.md`
7. ADR-0013 — `docs/adr/0013-temporary-us-region-demo-scope.md`
8. CSA agent — `agents/csa-agent/AGENT.md`
9. Data contracts — `docs/DATA.md`
10. PRD — `docs/PRD.md`

---

## 20. v1.1.0 extension — forecast overlay & SIT IQ-layer proof

> **Why this extension.** v1.0.0 routes Trust-A signals to **one** consumer —
> advisory CSA crisis runs. This extension adds a **second** consumer (the
> 72-hour occupancy/demand forecast) and makes the sprint **prove the full
> IQ-layer loop live in SIT**, where the Fabric IQ Ontology feature works
> (SIT create = `202`) while PROD stays gated behind issue **#270**
> (`FeatureNotAvailable`). The two consumers share the same `gold.ext_*`
> data product; the forecast path is a deterministic medallion job, so it is
> auditable and offline-testable exactly like the trigger path.

### 20.1 Revised end state (delta over §1)

* External signals feed **two** SIT consumers: (A) a **forecast overlay** that
  shifts the `ooa-agent` 72-hour forecast, and (B) the existing **CSA pre-seed**.
* The **SIT IQ layer is really exercised**: a live Fabric IQ Ontology extension
  (5 new classes) + the SIT data agent `da_hospital_capacity`
  (`b2e53c23-182a-452d-9321-e63f6009e80b`) grounded on the new `gold.ext_*`
  tables + the adjusted-forecast view + new measures, consumed by the Foundry
  `ooa-agent`.
* **PROD** IQ binding is explicitly deferred (reference plane only) behind #270;
  the SIT→PROD REST replication script is ready for when the capacity gate lifts.
  No scope loss — SIT is the proof surface.

### 20.2 Dual-consumer architecture (delta over §4)

```text
gold.ext_fact_signal  (Trust-A, deduped, status=Actual, trustTier=A)
   |
   +-- Path A (forecast overlay — deterministic notebook job):
   |     build_gold_forecast_adjustment.py
   |       join gold.forecast_output (base required_capacity, per hospital/ward/date)
   |       x hazard-uplift on {ward->specialty, hospital->canton, onset..expires}
   |         -> gold.ext_fact_forecast_adjustment   (audit + provenance + rationale)
   |         -> gold.vw_forecast_adjusted           (base + adjusted + attribution)
   |            -> external-signals.SemanticModel (adjusted-forecast measures)
   |            -> SIT data agent grounding -> Foundry ooa-agent
   |
   +-- Path B (crisis — unchanged from v1.0.0):
         signal-triage-agent -> CSA pre-seed (advisory, HITL, approved-to-apply)
```

* The overlay is a **medallion notebook job in the data lane**, *not* an agent
  action — keeps it deterministic, provenance-complete, and CI-testable.
* `signal-triage-agent` scope is unchanged (CSA routing only). The
  `data-quality-agent` gate is extended to the adjustment table as well.
* Base forecast source is the existing eventstream gold table
  `gold.forecast_output` (`hospital, ward_id, date, required_capacity`), the
  same table the `ooa-agent` and `[Required Capacity]` / `[Forecast Peak (72h)]`
  measures already read.

### 20.3 Forecast-overlay data model

* **`data-platform/scripts/external-signals/forecast_uplift.yaml`** — the
  governed uplift map: `hazardType x severity -> {specialties[], multiplier,
  decay}`. Example: `heat/Severe -> geriatrics +0.25, cardiology +0.15,
  emergency +0.20`. Offline unit-tested like `trigger_rules.yaml`.
* **`gold.ext_fact_forecast_adjustment`** — one row per
  (signal x affected specialty x affected date-bucket):
  `signalId, hazardType, severity, specialty_id, canton, effective, onset,
  expires, date, upliftFactor, baseRequiredCapacity, adjustedRequiredCapacity,
  rationale, provenance{rawHash, connectorVersion, ingestedAt}`.
* **`gold.vw_forecast_adjusted`** — for each base
  `gold.forecast_output` row: `adjusted = base_required_capacity x
  PROD(applicable upliftFactors)`, **clamped** to a documented ceiling, carrying
  **both** `base_required_capacity` and `adjusted_required_capacity` plus an
  `attribution[]` list (which `signalId`s moved the value) for explainability.
* **Anti-double-counting:** uplift is **incremental over the seasonal baseline**
  already in `gold.forecast_output` (the map encodes only the hazard-driven
  delta), is clamped, and is documented in ADR-0033. `status in {Test, Exercise,
  System}` signals are excluded from the overlay just as they are from triggering.
* **Multi-signal overlap:** multiple applicable upliftFactors combine
  **multiplicatively** with the same clamp; every contributing signal is listed
  in `attribution[]`.

### 20.4 SIT IQ-layer proof (the "integrated into IQ" deliverable)

1. **Real SIT ontology extension** — create the 5 new classes
   (`TrustedSource, HazardType, ExternalSignal, HazardEvent, TriggerRule`) as an
   actual Fabric IQ `Ontology` item in the SIT workspace
   `f3af9733-9503-4e92-98f9-a901d96f1c87` (create verified working: `202`),
   with DataBindings to the SIT lakehouse `gold.ext_*` tables. This is the live
   counterpart of the §7 reference plane.
2. **Extend the SIT data agent grounding** — add `gold.ext_fact_signal`,
   `gold.ext_fact_forecast_adjustment`, `gold.vw_forecast_adjusted`, and the new
   semantic-model measures to `da_hospital_capacity`
   (`b2e53c23-...`) grounding.
3. **Foundry `ooa-agent` consumption** — the agent answers e.g. *"given the ZH
   heat warning, what is the adjusted 72-hour geriatrics occupancy?"* returning
   the adjusted curve **with signal attribution**.
4. **Evidence** — a SIT E2E evidence doc under `docs/sprints/` captures the loop
   signal -> overlay -> semantic model -> ontology -> data agent -> ooa-agent
   answer (screenshots + REST/DAX transcripts), and links issue #270 as the
   documented reason PROD parity is deferred.

### 20.5 New requirements (added to PRD §7, MINOR bump)

| ID | Requirement |
|----|-------------|
| `FR-EXT-010` | Build `gold.ext_fact_forecast_adjustment` from base `gold.forecast_output` x governed hazard-uplift, joined on specialty + canton + onset..expires window. |
| `FR-EXT-011` | Govern the hazard-uplift map (`forecast_uplift.yaml`) as versioned, offline-unit-tested data; uplift is incremental over baseline and clamped. |
| `FR-EXT-012` | Expose `gold.vw_forecast_adjusted` carrying both base and adjusted values plus a per-row signal `attribution[]` list for explainability. |
| `FR-EXT-013` | Prove the external-signals IQ loop end-to-end in SIT: live Fabric IQ ontology extension + SIT data-agent grounding + Foundry `ooa-agent` consumption, captured as evidence. |
| `FR-EXT-014` | Record full provenance (`rawHash`, `connectorVersion`, `ingestedAt`, licence) on every forecast adjustment row; `Test/Exercise/System` signals excluded from the overlay. |

### 20.6 New milestones (detailed tasks in the implementation plan)

* **M9** — forecast uplift map + overlay pure transforms + notebook + offline tests.
* **M10** — `external-signals.SemanticModel` adjusted-forecast measures.
* **M11** — live SIT Fabric IQ ontology create + SIT data-agent grounding extension.
* **M12** — `ooa-agent` grounding extension + SIT E2E evidence doc.

M9–M10 depend on M3 (`gold.ext_*`) and M5 (semantic model); M11 depends on M4
(reference ontology) + M9/M10; M12 depends on M11.

### 20.7 Risks / guardrails (delta over §16)

| Risk | Mitigation |
|------|-----------|
| Double-counting hazard demand already in the seasonal baseline | Uplift map encodes only the incremental hazard delta; clamp; documented in ADR-0033; unit-tested. |
| Runaway multiplicative uplift when many signals overlap | Multiplicative with a documented clamp ceiling; full `attribution[]` for audit. |
| PROD parity expectation | Explicitly out of scope behind #270; SIT is the declared proof surface; SIT→PROD REST replication ready. |
| Overlay perceived as auto-acting on capacity | Overlay only changes a **forecast view**; no capacity/roster/bed mutation; HITL unchanged. |

### 20.8 Definition of done (delta over §18)

* `gold.ext_fact_forecast_adjustment` + `gold.vw_forecast_adjusted` produced by
  the offline synthetic end-to-end walk-through with attribution + provenance.
* `external-signals.SemanticModel` exposes the adjusted-forecast measures.
* Live SIT ontology extension created + SIT data agent grounded + `ooa-agent`
  returns an attributed adjusted forecast — captured in the SIT evidence doc.
* `FR-EXT-010..014` added to PRD §7; ADR-0033 records the anti-double-counting
  and clamp rules; #270 linked as the PROD-deferral reason.
