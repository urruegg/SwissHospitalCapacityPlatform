# Sprint 33 — Curavias BVA Agent (ROI/TCO reasoning + opportunity capture) — Design Spec

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft for review |
| **Previous Version** | n/a (initial version) |
| **Sprint** | Sprint 33 — Curavias BVA Agent |
| **Issue** | [#489](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/489) (tracker); [#490](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/490) (WS-G0) |
| **Builds on** | [Curavias BVA Agent proposal](../ideas/Curavias-BVA-Agent-Proposal.md); [BVA ROM baseline](../../BVA.md); [Sprint 15 BVA data product](2026-07-09-sprint-15-bva-design.md); [agent cost evidence](../../agent_cost.md) + [BOM annex](../../agent-cost-bom.md); [Sprint 28 PO Agent design](2026-07-25-sprint-28-product-owner-agent-design.md) + [PO Agent frozen contracts](2026-07-25-sprint-28-po-agent-contracts.md); [Curavias shared master data + ontology](2026-07-19-curavias-shared-master-data-and-ontology-design.md); [Fabric IQ to Foundry readiness](2026-07-17-fabric-iq-foundry-readiness-design.md) |
| **Related ADRs** | ADR-0013 (US demo scope); ADR-0014 (Fabric IQ ontology backbone, GA-gated); ADR-0016 (no PHI in demo); ADR-0025 (BVA KPI catalog); ADR-0032 (Foundry control plane eastus2); ADR-0043 (PO Agent Foundry IQ domain); a **new ADR** (BVA Agent computation posture) is a deliverable of this spec |
| **Runtime posture** | GitHub Copilot coding agent + Superpowers-first execution; git = single source of truth for master data; Fabric Git integration for Fabric assets; every Azure apply gated by `approved-to-apply`; human-performed PR merges; advisory-only, HITL |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Context and problem statement](#2-context-and-problem-statement)
3. [Decisions taken (brainstorm outcomes)](#3-decisions-taken-brainstorm-outcomes)
4. [Workstream decomposition](#4-workstream-decomposition)
5. [WS-A — Cost/BOM data product](#5-ws-a--costbom-data-product)
6. [WS-B — BVA reasoning agent + `bva.simulate` engine](#6-ws-b--bva-reasoning-agent--bvasimulate-engine)
7. [WS-C — Orchestration and PO linkage](#7-ws-c--orchestration-and-po-linkage)
8. [WS-D — Opportunity capture](#8-ws-d--opportunity-capture)
9. [Governance, requirements, registry, DoD](#9-governance-requirements-registry-dod)
10. [Risks and open questions](#10-risks-and-open-questions)
11. [Sequencing summary](#11-sequencing-summary)

---

## 1. Goal and desired end state

Deliver a Curavias **BVA (Business Value Assessment) Agent** that answers **ROI
and TCO questions in detail**, grounded on real actuals — Azure/BOM cost, the
GitHub Copilot cost of building and running the platform, and the human elective
cost of the implementation team — and the **three targeted hospitals**. The
agent can run an **interactive what-if simulation** for onboarding a new
hospital, is surfaced in the **Curavias App Start/Backstage copilot rail** as a
peer sub-agent alongside the **Product Owner (PO) Agent**, and captures **every
ask as an opportunity** to drive and onboard a new hospital.

Desired end state:

- A git-owned, CI-gated **cost/BOM data product** loaded identically into SIT and
  PROD Fabric IQ through a bronze -> silver -> gold medallion, a Direct Lake
  semantic model, and ontology + Data Agent grounding — reusing the established
  master-data-via-file pattern.
- A **deterministic ROI/TCO computation engine** exposed as a typed
  `bva.simulate` tool, with baseline actuals expressed as gold semantic measures.
  The LLM never does arithmetic; every number is citeable.
- A **BVA agent pack** (`agents/bva-agent/`) that does interactive slot-filling,
  calls `bva.simulate`, and narrates cited `GroundedChunk` results in DE/EN.
- **Orchestration** under the App copilot: onboarding/value questions fan out to
  BVA (numbers) and PO (go/no-go verdict), composed into one cited answer.
- **Opportunity capture**: a Cosmos DB system-of-record projected to a gold
  `bva_opportunity` table, surfaced on Start (inline) and Backstage (pipeline).

Non-goals (this sprint):

- No change to any Azure resource or spend (side-effect ceiling `write`; cloud
  reads only). The agent reads, models, and recommends.
- No real / PHI data — synthetic and anonymized only (ADR-0016), demo region
  (ADR-0013).
- No autonomous progression of an opportunity past `qualified`; humans advance
  the pipeline.

## 2. Context and problem statement

Three forces converge (see the [proposal](../ideas/Curavias-BVA-Agent-Proposal.md)
§1 for detail): the 2026-07-24 COO review framed a defensible ROI/TCO narrative
as a first-class deliverable; we now hold **real cost evidence**
([`docs/agent_cost.md`](../../agent_cost.md) — weekly Azure spend USD 491.11 over
2026-06-29 -> 2026-07-27, snapshot 2026-07-28, plus a full 144-resource
[BOM](../../agent-cost-bom.md) and Copilot AIU/token telemetry); and the Sprint
15 BVA data product already parks a stretch `bva-agent`.

The gap: today this evidence is refreshed by hand, the ROM plan
([`docs/BVA.md`](../../BVA.md), CHF) and the actuals (USD) do not reconcile, there
is no interactive way to test the value case for a **new** hospital, and there is
no captured **pipeline** of onboarding opportunities. The PO Agent already names
a **Class C (cost)** knowledge source but has no deep ROI/TCO engine behind it.
This sprint fills that gap.

## 3. Decisions taken (brainstorm outcomes)

These were resolved with @urruegg during the 2026-07-28 brainstorm and are
**binding** for this spec:

- **D1 — Sprint shape.** One BVA Agent sprint, decomposed into parallel
  workstreams (Sprint-28 shape), not a flat single-slice sprint and not two
  separate sprints.
- **D2 — Cost basis + currency.** Team cost = Copilot AIU/token spend
  (`agent_cost.md`) **plus** human elective hours × a configured role rate.
  **Standardize everything in CHF**, converting Azure/BOM USD actuals via an
  explicit FX line.
- **D3 — Agent topology.** The Curavias App copilot is the **orchestrator**; PO
  and BVA are **peer** typed sub-agents. For an onboarding question the
  orchestrator invokes **both** — BVA computes ROI/TCO, PO owns the **go/no-go
  verdict** informed by BVA's numbers.
- **D4 — Opportunity persistence.** **Cosmos DB** operational store (reuse
  `cosmos-mcp`) is the system-of-record, **projected** into a gold
  `bva_opportunity` table for analytics/reporting.
- **D5 — Simulation model.** **Parametric** model benchmarked from the three
  existing hospitals; BVA interactively asks only the **key deltas** (size/beds,
  occupancy target, case-mix archetype, onboarding scope) with archetype
  defaults.
- **D6 — Computation posture.** **Deterministic Python calc engine** exposed as
  a typed `bva.simulate` tool; baseline as gold semantic measures. **No LLM
  arithmetic.** (New ADR records this.)
- **D7 — Ingestion pattern.** Reuse the **master-data-via-file** pattern
  end-to-end (git CSVs -> CI gate -> medallion -> Direct Lake semantic model ->
  ontology + Fabric IQ Data Agent grounding), incorporated into the Fabric IQ /
  Foundry IQ layer.

## 4. Workstream decomposition

One sprint, five workstreams (mirrors the Sprint 28 WS-G0 -> parallel -> integrate
model that mitigated integration risk R6):

| WS | Name | Owns | Depends on |
| --- | --- | --- | --- |
| **WS-G0** | Frozen contracts | The `bva.simulate` tool signature, the `Opportunity` record shape, the CHF cost-basis normalization contract, JSON Schemas + eval fixtures | — (runs first) |
| **WS-A** | Cost/BOM data product | Git master-data CSVs -> medallion -> gold `bva_*` -> Direct Lake `sm_bva` -> ontology + Data Agent grounding | WS-G0 (cost-basis contract) |
| **WS-B** | BVA reasoning + engine | `bva.simulate` deterministic engine + `agents/bva-agent/` pack (slot-filling, golden tasks) | WS-G0, WS-A (gold measures) |
| **WS-C** | Orchestration + PO linkage | App copilot fan-out to BVA + PO; composed cited answer; PO consumes BVA output | WS-B, PO agent (Sprint 28) |
| **WS-D** | Opportunity capture | Cosmos SoR + `bva_opportunity` gold projection + Start/Backstage surfacing | WS-G0, WS-A |

**Dependency order:** WS-G0 -> (WS-A, WS-B, WS-D in parallel) -> WS-C integrates.

## 5. WS-A — Cost/BOM data product

Reuses the master-data-via-file pattern from the
[shared master data + ontology design](2026-07-19-curavias-shared-master-data-and-ontology-design.md)
end to end.

### 5.1 Source (git-owned, CI-gated) under `data/master-data/bva/`

| File | Content |
| --- | --- |
| `bva_azure_cost_weekly.csv` | Weekly Azure spend by service / RG / resource (ServiceName, ResourceGroup, ResourceId, iso_week, cost_usd) — from the `agent_cost.md` extract |
| `bva_bom.csv` | The 144-resource BOM (resource_type, resource_group, env, resource_id) from `agent-cost-bom.md` |
| `bva_copilot_usage_weekly.csv` | Copilot AIU + tokens per ISO week (session-store telemetry) |
| `bva_team_effort.csv` | Human elective hours × role rate (configured, CHF) |
| `bva_fx_rate.csv` | USD -> CHF rate per period (explicit FX line for deterministic normalization) |
| `bva_hospital_profile.csv` | The three targeted hospitals' benchmark drivers (beds, occupancy, case-mix archetype), re-pointed to the Curavias org spine (`dim_tenant`) |

### 5.2 Medallion -> semantic -> IQ

- **Notebooks:** `bronze_bva` (raw load) -> `silver_bva` (typed, FX-normalized to
  CHF, schema/PHI/FK gates via the `e2e-medallion-architecture` skill) ->
  `gold_bva` producing `bva_cost_fact`, `bva_bom_dim`, `bva_effort_fact`,
  `bva_hospital_profile_dim`, `bva_baseline_kpi`.
- **Semantic model** `sm_bva` (Direct Lake) exposes the ROI/TCO **baseline
  measures**: total cost CHF, one-time vs run split, cost-per-bed,
  cost-per-hospital, cost-per-forecast-run. These are the values the calc engine
  reads for the baseline.
- **Ontology + Fabric IQ Data Agent grounding** extended so `bva_*` is queryable
  as a knowledge domain, feeding PO **Class C** and the Foundry IQ layer.

### 5.3 Governance

Synthetic / actuals only, no PHI (ADR-0016); **SIT + PROD parity** (identical
load per the shared master-data design); the `data-quality-agent` contract-checks
the `bva_*` gold tables (schema, FK, provenance).

## 6. WS-B — BVA reasoning agent + `bva.simulate` engine

### 6.1 Agent pack `agents/bva-agent/`

Repo convention (`AGENT.md` + `manifest.yaml` + `golden-tasks.md`): **Identity,
Scope, Tools, Refusal Rules, Output Contract, Confirmation Rules**. MCP:
`github-mcp`, `fabric-mcp` (read gold measures), `cosmos-mcp` (opportunity
read/write). **Side-effect ceiling `write`** (no deploy/delete; cloud reads
only). Loaded at runtime by the Sprint 13 agent-host, like the other Sprint 11
packs. DE/EN parity per the PO contract.

### 6.2 Deterministic calc engine (`bva.simulate`)

Versioned Python, unit-tested, exposed as the frozen typed tool (WS-G0):

- **Inputs:** baseline (from `sm_bva` gold measures) + slot-filled deltas for the
  new hospital (beds, occupancy target, case-mix archetype, onboarding scope),
  with archetype defaults benchmarked from the three existing hospitals.
- **Model:** one-time onboarding cost (BOM increment + team elective effort in
  CHF) + annual run delta; benefit from the [ADR-0025](../../adr/0025-bva-kpi-catalog.md)
  BVA KPI catalog (capacity gain, LoS / bed-blocking avoidance) -> **ROI %,
  payback period, 3-year TCO, NPV**, with a **low / base / high sensitivity
  band**.
- **Output:** structured result rendered as **`GroundedChunk`s** (Sprint 28
  contract) — every number carries `citation.sourceRef` back to a gold measure or
  an input slot; `status` / `confidence` / `asOf` / `liveness` populated. **No LLM
  arithmetic.**

### 6.3 Interaction

The agent does **slot-filling**: asks only missing key deltas one at a time,
applies archetype defaults, echoes assumptions, then calls `bva.simulate` and
narrates the cited result.

### 6.4 Testing

Golden fixtures — a happy-path baseline query, a new-hospital what-if, and a
refusal / insufficient-input case. The calc engine has **deterministic unit
tests independent of the LLM**.

## 7. WS-C — Orchestration and PO linkage

### 7.1 Answer-time topology

The Curavias App copilot (Start + Backstage rail) is the **orchestrator**; PO and
BVA are peer typed sub-agents. Reuses the Sprint 28 orchestrator +
`GroundedChunk` composition. BVA plugs in as a **deepening of the existing Class
C (cost)** knowledge source rather than a new front door.

### 7.2 Onboarding-evaluation flow (`"should we onboard hospital X?"`)

1. Orchestrator detects an onboarding / value intent -> fans out to **both**
   sub-agents.
2. **BVA** runs slot-filling + `bva.simulate` -> returns ROI %, payback, 3-year
   TCO, NPV (± sensitivity) as cited chunks.
3. **PO** consumes BVA's numbers as Class-C evidence, applies strategic-fit
   criteria, and owns the **go / no-go / conditional verdict** — cited, DE/EN.
4. Orchestrator composes one grounded answer: PO verdict on top, BVA financials
   as supporting evidence, all citations rendered by the shared citation layer.
5. The ask + result is written as an **opportunity** (Section 8).

### 7.3 Routing

Pure-financial questions (`"what's our TCO to date?"`) route to **BVA alone**;
pure-strategic questions route to **PO alone**; only onboarding / value-fit
questions **fan out to both**.

### 7.4 Contract source of truth

WS-G0 freezes the `bva.simulate` signature + the PO <-> BVA hand-off (the BVA
output shape PO consumes), mirroring
[`2026-07-25-sprint-28-po-agent-contracts.md`](2026-07-25-sprint-28-po-agent-contracts.md),
with a matching JSON Schema + eval fixtures.

## 8. WS-D — Opportunity capture

### 8.1 System-of-record

**Cosmos DB** (reuse `cosmos-mcp`, same account pattern as CSA). Every value /
onboarding ask creates or updates an **`Opportunity`** document.

### 8.2 `Opportunity` shape (frozen by WS-G0)

- `id`, `hospitalName`, `archetype`, `createdAt`, `createdBy`, `status`
  (`new` -> `evaluating` -> `qualified` / `disqualified` -> `onboarding` ->
  `won` / `lost`).
- `askText` (the originating question), `language` (de/en).
- `bvaResult` — the cited `bva.simulate` output snapshot (ROI %, payback, 3-year
  TCO, NPV, sensitivity, `asOf`).
- `poVerdict` — go / no-go / conditional + rationale + citations.
- `inputs` — the slot-filled deltas used (beds, occupancy, case-mix, onboarding
  scope).
- `history[]` — append-only audit of re-simulations / verdict changes.

### 8.3 Lifecycle

The orchestrator **upserts** the opportunity after each answer; re-asking about
the same hospital **updates the same record** (append to `history`, do not fork).
Human progression of `status` is app-driven; **agents never auto-advance past
`qualified`** (write ceiling, no deploy).

### 8.4 Analytics projection

A `gold.bva_opportunity` table (Direct Lake) mirrors Cosmos for pipeline
reporting — a Backstage "opportunity pipeline" view (count by status, weighted
ROI) reads it. Projection is **one-way** (Cosmos -> gold), refreshed by a
notebook; Cosmos stays the SoR.

### 8.5 Surfacing

Start rail shows the latest opportunity + verdict inline in the answer; Backstage
shows the full pipeline list + a drill-in to any opportunity's cited BVA / PO
detail.

## 9. Governance, requirements, registry, DoD

### 9.1 Requirements (promote into `docs/PRD.md` §7)

Functional:

- **FR-BVA-001** — Grounded ROI/TCO answers computed over `bva_*` gold measures,
  standardized in CHF.
- **FR-BVA-002** — Interactive new-hospital what-if via the deterministic
  `bva.simulate` tool (parametric, benchmarked from the three hospitals).
- **FR-BVA-003** — PO <-> BVA fan-out: BVA numbers + PO go/no-go verdict composed
  into one cited answer.
- **FR-BVA-004** — Opportunity capture (Cosmos SoR) + `bva_opportunity` gold
  projection + Backstage pipeline view.
- **FR-BVA-005** — Surfacing in the Curavias App Start (inline) and Backstage
  (pipeline) copilot rail.

Non-functional:

- **NFR-BVA-001** — Deterministic, reproducible math; **no LLM arithmetic**.
- **NFR-BVA-002** — Every figure cited via `GroundedChunk` (query / gold measure /
  input slot, snapshot date, currency).
- **NFR-BVA-003** — CHF normalization with an explicit FX line; settling weeks
  marked provisional.
- **NFR-BVA-004** — SIT / PROD data parity, no PHI (ADR-0016), demo figures
  labelled PoT (ADR-0013).
- **NFR-BVA-005** — DE / EN parity in all agent output.

### 9.2 ADR

New ADR (next genuinely-free number after the #378 collision cleanup): **"BVA
Agent — deterministic ROI/TCO computation as a typed tool; cost data product via
the master-data pattern; peer to PO under the App orchestrator."** Records the
no-LLM-math decision (D6), Cosmos SoR (D4), and Class-C deepening (D3).

### 9.3 Registry

New `AGENTS.md` §1 row: `bva-agent` | owner @urruegg | trigger
`agent-build.yml` / `@bva-agent` | MCP `github-mcp`, `fabric-mcp`, `cosmos-mcp` |
ceiling `write` | prompt + golden-tasks paths. **No MCP allow-list change** — all
three servers already exist.

### 9.4 Definition of Done (per workstream)

- **WS-G0** — `bva.simulate` signature, `Opportunity` shape, and cost-basis
  contract frozen + JSON Schema + eval fixtures published.
- **WS-A** — `bva_*` gold builds **identically** in SIT and PROD; `data-quality-agent`
  gates green; `sm_bva` baseline measures live.
- **WS-B** — calc-engine unit tests + agent golden-tasks (happy + what-if +
  refusal) green.
- **WS-C** — orchestrator fan-out eval (onboarding question composes BVA + PO)
  green.
- **WS-D** — Cosmos upsert + gold projection + Backstage pipeline view working.
- **All** — docs gate-clean (mojibake + markdownlint), doc versions bumped, PRD
  §7 updated; **human-merged PRs only**; no infra apply beyond gated,
  `approved-to-apply` Fabric/data loads.

## 10. Risks and open questions

- **R1 — GitHub billing rate unknown.** Copilot cost uses AIU/token telemetry as
  a proxy; the `$`/AIU (and CHF) rate needs a `Plan:read` PAT to be authoritative.
  *Mitigation:* the FX + rate assumptions live in `bva_fx_rate.csv` /
  `bva_team_effort.csv` and are cited; refine when the token exists.
- **R2 — Benefit KPIs are ROM.** Capacity-gain / LoS-avoidance benefit values are
  planning estimates (ADR-0025). *Mitigation:* sensitivity band (low/base/high)
  and `status: requires-validation` on modelled benefits.
- **R3 — PO contract coupling.** The PO <-> BVA hand-off depends on the frozen
  Sprint 28 `GroundedChunk`. *Mitigation:* WS-G0 freezes the shared shape before
  the parallel workstreams start.
- **R4 — Cosmos <-> gold consistency.** One-way projection can lag Cosmos.
  *Mitigation:* Cosmos is the SoR for the app; gold is analytics-only and
  timestamped `asOf`.
- **Q1 (open)** — Should the weekly cost close (the Tier A repo-native
  evidence-refresh journey from the proposal) be **in this sprint** or a fast
  follow-on? *Default:* fold the manual-refresh reproducibility check into WS-A
  DoD; automate the scheduled workflow in a follow-on.

## 11. Sequencing summary

1. **WS-G0** — freeze `bva.simulate` + `Opportunity` + cost-basis contracts,
   schemas, fixtures.
2. **WS-A / WS-B / WS-D in parallel** — data product; calc engine + agent pack;
   opportunity store + projection.
3. **WS-C** — integrate the orchestrator fan-out (BVA + PO) and Start/Backstage
   surfacing.
4. **Governance** — new ADR, `AGENTS.md` row, PRD §7 requirements, DoD sign-off.

Each workstream lands as its own human-reviewed squash PR off the latest `main`
(trunk-based per ADR-0038); a human merges every PR; deploys / live data loads
gated by `approved-to-apply`.
