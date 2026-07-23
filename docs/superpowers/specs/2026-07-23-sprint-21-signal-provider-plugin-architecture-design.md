# Sprint 21 Refactor — Signal-Provider Plugin Architecture & Trust Badges — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.0.1 |
| **Date** | 2026-07-23 |
| **Author** | Urs Rueegg |
| **Status** | Implemented (all 17 plan tasks landed on `sprint-21/refactor-signals`; scripts 43 + notebook 13 suites green) |
| **Previous Version** | 1.0.0 (initial design, approved in brainstorm) |
| **Sprint** | [Sprint 21 - Trusted External Signals](../../sprints/SPRINT_PLAN.md) |
| **Issue** | [#247](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/247) |
| **Epic** | [sprint-21-refactor-epic.md](../ideas/sprint-21-refactor-epic.md) |
| **Extends** | [2026-07-17-sprint-21-trusted-external-signals-fabric-design.md](./2026-07-17-sprint-21-trusted-external-signals-fabric-design.md) (v1.1.0) |
| **Anchor triggers** | Epic requirements 1-5; AMA review `docs/reviews/2026-07-17-ama-trusted-external-signals-review.md` (source-readiness, F-A-04) |
| **Runtime posture** | GitHub Copilot coding agent + Superpowers-first execution; advisory/HITL unchanged; agents realised as Markdown packs + MCP config (ADR-0002). **Refactor:** signal ingestion + simulation run as Azure Container Apps services publishing to Event Hub/Eventstream, **not** GitHub Actions. |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Scope](#2-scope)
3. [Approaches considered](#3-approaches-considered)
4. [Refactored runtime topology](#4-refactored-runtime-topology)
5. [The SignalProvider plugin contract](#5-the-signalprovider-plugin-contract)
6. [Provider manifest and binding model](#6-provider-manifest-and-binding-model)
7. [Trust-badge propagation](#7-trust-badge-propagation)
8. [Provider inventory](#8-provider-inventory)
9. [Impact on the v1.1.0 design (refactor delta)](#9-impact-on-the-v110-design-refactor-delta)
10. [Governance, requirements and ADR](#10-governance-requirements-and-adr)
11. [Component boundaries](#11-component-boundaries)
12. [Testing and CI gates](#12-testing-and-ci-gates)
13. [Implementation milestones](#13-implementation-milestones)
14. [Risk register](#14-risk-register)
15. [Definition of done](#15-definition-of-done)
16. [Follow-on subsystems B and C (stubs)](#16-follow-on-subsystems-b-and-c-stubs)
17. [References](#17-references)

---

## 1. Goal and desired end state

Refactor the Sprint 21 external-signals ingestion (today: a `BaseConnector` ABC +
per-source `parse()` functions + a single global synthetic seeder, bridged by a
scheduled GitHub Actions poller) into a **signal-provider plugin architecture**
where every channel is a self-describing provider that can run as a **real API
adapter**, a **simulator**, or an **internal** signal source, and whose live-vs-
simulated state is surfaced as a **trust badge** on the CSA and OCA boards.

**Desired end state:**

* A single, manifest-driven **provider plugin** model. Onboarding a new signal
  source = drop a folder with a schema-validated manifest + binding(s); no changes
  to the runtime or the data contract.
* Each provider holds **one swappable binding**: `LiveBinding` (real API adapter),
  `SimulatorBinding` (synthetic), or `InternalBinding` (reads our own gold tables),
  with automatic **live -> simulated fallback** for external channels.
* Ingestion and simulation run as **Azure Container Apps services** (part of the
  Curavias platform), publishing `DC-EXT-SIGNAL-v1` to **Event Hub -> Fabric
  Eventstream -> Eventhouse (hot) + OneLake medallion (cold)**. **No GitHub Actions
  workflow ingests or simulates signal data.**
* Every emitted signal carries `provenance.activeBinding`, which is the single
  source of truth for a **3-state trust badge** (Live / Simulated / Internal) that
  flows `ext_dim_source.dataMode` -> semantic-model measures -> board channel cards.
* **SED** and **Alertswiss/Polyalert** run **live in the demo** (confirmed-ready,
  public non-PHI feeds); all other external channels run on simulators; internal
  channels read gold tables. Every channel is **honestly badged from data**.
* Switching any channel Simulated -> Live is a **manifest change** gated by the
  build-time endpoint/licence verification list and `approved-to-apply`.

## 2. Scope

### In scope (Subsystem A, epic items 1-5)

* `SignalProvider` plugin contract: manifest schema, binding interfaces
  (`LiveBinding` / `SimulatorBinding` / `InternalBinding`), shared `parse`.
* Registry with auto-discovery + manifest-schema validation.
* Refactor of existing `connectors/` + `signals_synth.py` into `providers/`.
* Real API adapters for confirmed-ready channels (SED, Alertswiss); adapters
  authored-but-dormant for MeteoSwiss/BAG (licence / dataset-ID caveats).
* Simulator plugins for unconfirmed channels (BAFU, ASTRA, SLF, NABEL, Swissgrid,
  NCSC).
* Internal providers reading gold tables (occupancy-breach, roster-shortfall,
  supply-stock).
* Trust-badge data contract: `ext_dim_source.dataMode` + semantic-model measures +
  board badge states (styling owned by `ux-design-agent`).
* Azure Container Apps **provider-runner** hosting model (Bicep scaffold, deploy
  gated); retirement of the runtime poller workflow.
* `data-quality-agent` gate extension; ADR + `FR-EXT-*` PRD additions; CI gates.

### Out of scope (this spec)

* **Subsystem B** - probabilistic risk exposure -> proactive CSA scenario
  generation + simulation (epic items 6-7). Own spec.
* **Subsystem C** - closed CSA learning loop via Fabric IQ (epic item 8). Own spec.
* Any change to the CSA simulation engine or the `signal-triage-agent`
  responsibilities beyond its trigger source.
* Live Azure/Fabric deployment (artefacts authored + CI-gated; deploy is a separate
  `approved-to-apply` step).
* Trust-tier B/C source onboarding (pattern documented, not built).

## 3. Approaches considered

| # | Approach | Verdict |
|---|----------|---------|
| A | **Manifest-driven provider plugins with swappable bindings, hosted as Azure Container Apps services publishing to Eventstream.** | **Chosen.** Data-driven onboarding, one badge source of truth, live/sim/internal unified, offline-testable, ingestion off the CI plane. |
| B | Keep the v1.1.0 GH-workflow poller + `BaseConnector` ABC, add a `mode` flag. | Rejected - ingestion/simulation must be Azure eventstream services, not Actions; a bare flag does not give a plugin onboarding contract. |
| C | Per-source Azure Logic Apps + shared normaliser. | Rejected - low-code sprawl, weaker offline testability; the AMA lets us bridge with code adapters that unit-test cleanly. |

## 4. Refactored runtime topology

```text
Provider services (Azure Container Apps - part of the Curavias platform)
  provider-runner loads manifest-declared providers, each on its cadence:
    +- LiveBinding      (real API adapter)  -> SED FDSN, Alertswiss/Polyalert [live in demo]
    +- SimulatorBinding (synthetic)         -> BAFU, ASTRA, SLF, NABEL, Swissgrid, NCSC ...
    +- InternalBinding  (reads gold)        -> occupancy-breach, roster-shortfall, supply-stock
        |  each emits DC-EXT-SIGNAL-v1 (+ provenance.activeBinding / fellBackFrom / channelKind)
        v
  Event Hub (evh-ihzhhpf) -> Fabric Eventstream (es-ihzhhpf-events; route eventKind=ext-signal)
        |                                          |
        |  HOT                                     |  COLD
        v                                          v
  Eventhouse KQL DB                         OneLake Lakehouse medallion
        |                                    bronze -> silver -> gold ext_*
        v                                          (+ ext_dim_source.dataMode)
  Activator/Reflex rule (GA-target)                v
        |                                    external-signals.SemanticModel
        v                                    (+ Channel Data Mode measures)
  signal-triage-agent (agent-host)                 v
        |  dedup + arbitrate + TriggerRule    CSA / OCA board channel cards
        v                                    -> Live / Simulated / Internal badge
  csa-agent (Prepare/Run/Evaluate/Recommend, HITL, approved-to-apply)

GitHub Actions = CI only: offline unit tests (adapters mocked / simulators /
internal / parse / normalize), manifest-schema validation, badge-propagation test,
golden-task replay, markdownlint / link-check / mojibake. No runtime ingestion.
```

**Key change vs v1.1.0:** the `ext-signal-poll.yml` poller bridge is **retired from
the runtime path**. Triggering is Fabric-native (Activator/Reflex -> agent-host).
Provider *logic* lives in-repo and is unit-tested offline; the *hosting* is the
Container Apps provider-runner deployed via Bicep + `approved-to-apply`. Live
bindings are always mocked in CI - no external network calls in Actions.

## 5. The SignalProvider plugin contract

One **provider per channel**. A provider = a schema-validated **manifest** plus a
small code surface, and holds exactly one **active binding** selected at runtime.

Code surface under `data-platform/external-signals/providers/<sourceId>/`:

| File | Responsibility | Applies to |
|------|----------------|-----------|
| `provider.yaml` | Declarative manifest (see §6) | all |
| `live.py` | `LiveBinding.poll() -> list[raw]` (real API) | external channels with a confirmed endpoint |
| `simulator.py` | `SimulatorBinding.generate(seed) -> list[raw]` (deterministic synthetic) | every external channel (fallback + demo) |
| `internal.py` | `InternalBinding.read(gold) -> list[raw]` | internal channels only |
| `parse.py` | `parse(raw) -> list[DC-EXT-SIGNAL-v1]` (shared by live + simulator) | all |

Contract rules:

* `parse()` is the **single contract seam**: both live and simulator bindings emit
  the *same* raw shape so `parse()` produces identical `DC-EXT-SIGNAL-v1` records
  regardless of binding. This preserves the existing "normalize is the single
  contract seam" property from the v1.1.0 risk register.
* A binding never writes to the lake directly. It returns records; the
  provider-runner publishes them to Event Hub. This keeps bindings pure and
  offline-testable.
* Every record is stamped with provenance before publish (see §6.3).

## 6. Provider manifest and binding model

### 6.1 Manifest schema

Authored at `providers/_schema/provider.schema.json`; every `provider.yaml` is
validated in CI.

```yaml
sourceId: sed                 # unique; FK -> ext_dim_source
authority: SED-ETH            # sourceAuthority
trustTier: A                  # A | B | C  (this sprint: A auto-evaluated)
channelKind: external         # external | internal
hazardTypes: [earthquake]
defaultMode: live             # live | simulated | internal
fallbackMode: simulated       # external only; what live falls back to
cadenceSeconds: 300
endpoint: https://eida.ethz.ch/fdsnws/event/1/query   # omitted for simulated-only / internal
licence: SED-ETH-open-data    # mandatory (NFR-EXT-GOV-001)
providerVersion: sed-2.0.0
scenarioMap:                  # hazard -> ScenarioTemplate + default Lage tier
  earthquake: { template: F1, lageTier: 3 }
```

Validation rules enforced by the schema + a manifest linter:

* `channelKind: external` requires a `simulator.py`; `defaultMode: live` requires a
  `live.py` + `endpoint`; `channelKind: internal` requires `internal.py` and forbids
  `endpoint`.
* `licence` is mandatory for every provider.
* `sourceId` is unique across the registry.

### 6.2 Binding selection and fallback (provider-runner)

1. `active = defaultMode`.
2. For `defaultMode: live`, if `LiveBinding.poll()` raises or times out, switch
   `active = fallbackMode` (`simulated`) and set `provenance.fellBackFrom = "live"`.
3. `provenance.activeBinding = active` on every emitted record - the **single
   source of truth** for the trust badge.
4. Internal providers are always `active = internal` (no fallback).

### 6.3 Provenance additions to `DC-EXT-SIGNAL-v1`

`normalize.build_record()` (existing) gains three provenance fields (additive,
backwards-compatible):

* `provenance.activeBinding`: `live | simulated | internal`
* `provenance.fellBackFrom`: `live | null`
* `provenance.channelKind`: `external | internal`

No other contract field changes; the CAP-aligned envelope is unchanged.

### 6.4 Registry and auto-discovery

`providers/registry.py`:

* Discovers every `providers/<sourceId>/provider.yaml`, validates against the
  schema, and builds an in-memory catalogue.
* Exposes `load_providers()` for the provider-runner and `catalog_rows()` for
  seeding `gold.ext_dim_source`.
* Fails closed: a malformed / schema-invalid manifest fails CI and is excluded
  from the runtime catalogue (never silently ingested).

## 7. Trust-badge propagation

The badge is fully data-driven - no hard-coded UI state:

1. **Envelope** - `provenance.activeBinding` on every record.
2. **Silver -> Gold** - `gold.ext_dim_source` gains: `dataMode`
   (`Live | Simulated | Internal`), `trustTier`, `lastLiveAt`, `fellBackFrom`. One
   row per provider; `dataMode` = latest observed active binding (so a fallen-back
   live channel correctly reads **Simulated**).
3. **Semantic model** - new measures on `external-signals.SemanticModel`:
   `[Channel Data Mode]`, `[Channels Live]`, `[Channels Simulated]`,
   `[Channels Internal]`, `[Last Live Signal]`.
4. **Boards** - CSA "Krisen & Szenarien" + OCA channel cards render a badge bound to
   `dataMode`: Live (green) / Simulated (amber) / Internal (blue). Styling, tokens
   and accessibility are owned by the [`ux-design-agent`](../../../agents/ux-design-agent/AGENT.md);
   this spec defines the **data contract + states**, not the pixels.

## 8. Provider inventory

| Provider | channelKind | Default binding (this sprint) | Basis (AMA readiness) |
|----------|-------------|-------------------------------|-----------------------|
| `sed` | external | **Live** (FDSN; live in demo) | clean real-time API |
| `alertswiss` | external | **Live** (Polyalert / CAP poll; live in demo) | pollable government catch-all |
| `meteoswiss` | external | **Simulated** (live adapter authored; dormant) | threshold-derive; Open-Meteo non-commercial licence caveat |
| `bag` | external | **Simulated** (adapter authored; dormant) | daily; dataset IDs "verify at build" |
| `bafu` | external | **Simulated** (simulator only; endpoint contract documented) | flood; "verify at build" |
| `astra` | external | **Simulated** | traffic/DATEX II; "verify at build" |
| `slf` | external | **Simulated** | avalanche; "verify at build" |
| `nabel` | external | **Simulated** | air quality; "verify at build" |
| `swissgrid` | external | **Simulated** | power; "verify at build" |
| `ncsc` | external | **Simulated** | cyber; "verify at build" |
| `occupancy-breach` | internal | **Internal** (reads occupancy gold) | new (epic item 2) |
| `roster-shortfall` | internal | **Internal** (reads roster gold) | new |
| `supply-stock` | internal | **Internal** (reads supply/blood gold) | new |

**Live in demo = SED + Alertswiss** (confirmed-ready, public non-PHI). Everything
else runs on simulators / internal bindings, honestly badged. Promoting any
Simulated -> Live is a manifest change gated by the build-time verification list
(`NFR-EXT-GOV-001`) + `approved-to-apply`.

## 9. Impact on the v1.1.0 design (refactor delta)

* **Retire** `.github/workflows/ext-signal-poll.yml` from the runtime path;
  ingestion/simulation move to the Container Apps provider-runner.
* **New infra (UC-output Bicep, scaffold + `approved-to-apply`):** provider-runner
  Container App module + config; **reuse** `evh-ihzhhpf` / `es-ihzhhpf-events`.
* **New folders:** `data-platform/external-signals/providers/<sourceId>/`,
  `providers/_schema/provider.schema.json`, `providers/registry.py`.
* **Refactor:** `connectors/` -> `providers/` (existing `parse()` bodies preserved,
  tests carried); `signals_synth.py` -> per-provider `simulator.py` + thin shared
  helper; `normalize.py` gains provenance fields; `ext_dim_source` schema +
  silver/gold notebooks updated; semantic-model measures added.
* **`data-quality-agent`** gate extended: manifest-schema conformance,
  `activeBinding` present, `dataMode` populated, `licence` present per provider.
* **`signal-triage-agent`** responsibilities unchanged; its trigger source is
  Activator/Reflex (not a GH workflow).
* **Semantic model** `external-signals.SemanticModel` remains **separate**
  (ADR-0026) - `verify-semantic-model.yml` untouched.

## 10. Governance, requirements and ADR

* **ADR:** extend **ADR-0036** (external-trigger governance) or author a new ADR to record: (a) provider-plugin
  architecture + binding/fallback, (b) trust-badge data contract + 3 states,
  (c) Azure Container Apps-hosted ingestion (ingestion/simulation **off** the CI
  plane; no Actions), (d) internal-signal channels. CODEOWNERS review required.
* **New requirements** (PRD MINOR bump; IDs reconciled against existing `FR-EXT-*`
  incl. v1.1.0 §20 `FR-EXT-010..014` now present in PRD §K, so this spec proposes
  `FR-EXT-015+` - verified free against `docs/PRD.md` v1.9.0):

  | ID (proposed) | Requirement |
  |----|-------------|
  | `FR-EXT-015` | Onboard new signal sources as manifest-driven provider plugins emitting `DC-EXT-SIGNAL-v1`. |
  | `FR-EXT-016` | Provide real API adapters (`LiveBinding`) for confirmed-ready channels (SED, Alertswiss). |
  | `FR-EXT-017` | Provide simulator plugins (`SimulatorBinding`) for channels without a confirmed API. |
  | `FR-EXT-018` | Support internal signal channels (`InternalBinding`) derived from platform gold tables. |
  | `FR-EXT-019` | Surface a data-driven live/simulated/internal trust badge per channel on the CSA/OCA boards. |
  | `FR-EXT-020` | Host ingestion + simulation as Azure Container Apps services publishing to Event Hub/Eventstream (not GitHub Actions). |
  | `NFR-EXT-PLG-001` | Live bindings are always mocked in CI; no external network calls in Actions. |
  | `NFR-EXT-PLG-002` | A schema-invalid manifest fails CI and is excluded from the runtime catalogue (fail-closed). |

* **Residency / HITL:** unchanged. Public non-PHI feeds; live calls to SED /
  Alertswiss are permitted (A-02, F-P-03). No external signal auto-mutates state;
  the only automatic action remains an advisory CSA proposal for human approval.

## 11. Component boundaries

| Unit | Responsibility | Depends on | Consumers |
|------|----------------|------------|-----------|
| `provider.yaml` + schema | declare channel metadata | schema | registry, ext_dim_source |
| `LiveBinding` | fetch raw from real API | endpoint | parse |
| `SimulatorBinding` | deterministic synthetic raw | seed | parse |
| `InternalBinding` | derive raw from gold | gold tables | parse |
| `parse` | raw -> `DC-EXT-SIGNAL-v1` | contract schema | provider-runner |
| `registry` | discover + validate manifests | manifests | provider-runner, ext_dim_source |
| provider-runner (Container App) | select binding, fallback, stamp provenance, publish | Event Hub, registry | Eventstream |
| medallion notebooks | bronze->silver->gold ext_* + dataMode | Lakehouse, contract | semantic model |
| semantic model | Direct Lake + badge measures | gold tables | boards |
| `signal-triage-agent` | dedup/arbitrate/route (unchanged) | gold, rules, Activator | csa-agent |

Each unit is independently testable; bindings, parse, registry, and internal
providers run fully offline in CI (live bindings mocked).

## 12. Testing and CI gates

Fixture-first / TDD - contract + manifest schema + parse tests authored before
binding/runtime logic.

* **`external-signals.yml`** extended: manifest-schema validation; per-provider
  `parse` tests; `SimulatorBinding` determinism tests; `InternalBinding` tests
  (against synthetic gold fixtures); `LiveBinding` tests with **mocked** transport;
  **fallback test** (live raises -> `activeBinding=simulated`, `fellBackFrom=live`);
  **badge-propagation test** (envelope `activeBinding` -> `ext_dim_source.dataMode`).
* **`eval-goldens.yml`**: `signal-triage-agent` + `data-quality-agent` fixtures,
  including a fallback -> Simulated-badge case and an Internal-channel case.
* **`verify-semantic-model.yml`**: untouched (separate model, ADR-0026).
* **`ontology-conformance.yml`**: unchanged for A (ontology classes already covered
  by v1.1.0; no new classes here).
* markdownlint + link-check + mojibake on all docs; every edited doc bumps SemVer.
* **No live network calls in CI**; live bindings always mocked.

## 13. Implementation milestones

Detailed task breakdown expanded in the writing-plans step
(`docs/superpowers/plans/2026-07-23-sprint-21-signal-provider-plugin-architecture-plan.md`).

| # | Milestone | Deliverable | DoD |
|---|-----------|-------------|-----|
| M0 | Manifest schema + registry | `provider.schema.json`, `registry.py`, schema tests | schema validates; registry discovery green offline |
| M1 | Refactor connectors -> providers | move `parse()` bodies; carry tests; `normalize` provenance fields | existing tests green under new layout |
| M2 | Simulators + internal bindings | per-provider `simulator.py`; 3 internal providers | determinism + internal tests green |
| M3 | Live adapters | `live.py` for SED + Alertswiss (mocked transport); dormant MeteoSwiss/BAG | live tests (mocked) + fallback test green |
| M4 | Trust badge data path | `ext_dim_source.dataMode` cols; silver/gold notebooks; semantic-model measures | badge-propagation test green; measures validate |
| M5 | Provider-runner + infra | Container App Bicep (scaffold, deploy gated); retire `ext-signal-poll.yml` | Bicep builds; `what-if` clean; poller removed |
| M6 | Governance + agents | ADR update; `FR-EXT-*` in PRD + matrix; `data-quality-agent` gate; AGENTS.md note | eval-goldens green; docs bumped |
| M7 | Integration + docs | end-to-end synthetic walk-through (sim + internal + one mocked-live); doc bumps | all gates green; DoD met |

## 14. Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Live endpoint/schema drift (SED, Alertswiss) | Medium | Medium | Live bindings isolate parsing; `parse()` is the single seam; automatic fallback to simulator; build-time verification list |
| Open-Meteo / BAG licence + dataset-ID caveats | Medium | Medium | MeteoSwiss/BAG live adapters authored but **dormant** (Simulated default) until licence/IDs confirmed |
| Container Apps provider-runner scaffold-only at demo | High | Low | Simulators + internal bindings run the demo deterministically; live is additive and gated |
| Badge misrepresents state (shows Live while on fallback) | Low | High | `dataMode` derives from `activeBinding` at emit time; fallback stamps `Simulated`; badge-propagation test enforces it |
| Manifest sprawl / silent bad manifest | Low | Medium | Fail-closed schema validation in CI; malformed manifest excluded from catalogue |
| Ingestion accidentally re-added to Actions | Low | Medium | ADR records the boundary; CI has no ingestion job; poller workflow removed |

## 15. Definition of done

* All offline CI gates green (external-signals, eval-goldens, markdownlint,
  link-check, mojibake); `verify-semantic-model.yml` untouched/green.
* Provider-runner Bicep authored (deploy gated); `ext-signal-poll.yml` removed from
  the runtime path.
* SED + Alertswiss live-capable (mocked in CI); MeteoSwiss/BAG dormant-live; other
  external channels simulated; 3 internal channels implemented - **all badged from
  data**.
* End-to-end synthetic walk-through produces `gold.ext_*` rows with correct
  `dataMode` and a `signal-triage-agent` -> CSA handoff.
* ADR authored/extended; `FR-EXT-*` in PRD + traceability matrix;
  `data-quality-agent` gate extended; AGENTS.md reconciled.
* Advisory/HITL + non-PHI posture preserved; licence recorded per provider.
* Every edited doc bumped per SemVer (copilot-instructions §9).

## 16. Follow-on subsystems B and C (stubs)

Referenced here for sequencing; each gets its own brainstorm -> spec -> plan cycle.

* **Subsystem B - probabilistic risk exposure -> proactive CSA** (epic items 6-7):
  score risk exposure against the 72-hour capacity forecast, auto-onboard a
  scenario, and run the CSA simulation pre-emptively to recommend mitigations
  before the risk materialises. Consumes `gold.ext_fact_signal` + the v1.1.0 §20
  forecast overlay. Keeps the CSA Board as-is; extends it with Foundry IQ / Fabric
  IQ data.
* **Subsystem C - closed CSA learning loop via Fabric IQ** (epic item 8): learn /
  improve / act from CSA run outcomes using the Fabric IQ ontology model
  end-to-end.

## 17. References

1. Epic - `docs/superpowers/ideas/sprint-21-refactor-epic.md`
2. v1.1.0 design - `docs/superpowers/specs/2026-07-17-sprint-21-trusted-external-signals-fabric-design.md`
3. AMA review - `docs/reviews/2026-07-17-ama-trusted-external-signals-review.md`
4. ADR-0036 - external-trigger governance (to extend)
5. ADR-0026 - separate semantic model precedent
6. ADR-0014 - Fabric IQ ontology backbone (GA-gated)
7. ADR-0013 - demo residency (westus2, synthetic-only, no PHI)
8. ADR-0002 - runtime is GitHub Copilot coding agent
9. CSA agent - `agents/csa-agent/AGENT.md`
10. signal-triage-agent - `agents/signal-triage-agent/AGENT.md`
11. data-quality-agent - `agents/data-quality-agent/AGENT.md`
12. PRD - `docs/PRD.md`; Data contracts - `docs/DATA.md`
