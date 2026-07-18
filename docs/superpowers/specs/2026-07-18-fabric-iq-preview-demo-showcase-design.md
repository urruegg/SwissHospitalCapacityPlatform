# Fabric IQ (Preview) Demo Showcase — Design

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-18 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | — (new) |

> Companion plan: [`docs/superpowers/plans/2026-07-18-fabric-iq-preview-demo-showcase.md`](../plans/2026-07-18-fabric-iq-preview-demo-showcase.md).
> Parent readiness design: [`2026-07-17-fabric-iq-foundry-readiness-design.md`](2026-07-17-fabric-iq-foundry-readiness-design.md).
> Seam already shipped (Slice 0): [ADR-0033](../../adr/0033-fabric-data-agent-as-foundry-grounding-tool.md).

## Table of contents

1. [Goal and demo narrative](#1-goal-and-demo-narrative)
2. [Current state and gap](#2-current-state-and-gap)
3. [Target artefact inventory (Tier 3)](#3-target-artefact-inventory-tier-3)
4. [Architecture and data flow](#4-architecture-and-data-flow)
5. [Prerequisites and tenant-admin gates](#5-prerequisites-and-tenant-admin-gates)
6. [Guardrails](#6-guardrails)
7. [Region and cross-region posture](#7-region-and-cross-region-posture)
8. [Build sequence (milestones)](#8-build-sequence-milestones)
9. [Demo script (the golden path)](#9-demo-script-the-golden-path)
10. [Risks and mitigations](#10-risks-and-mitigations)
11. [Requirements traceability](#11-requirements-traceability)
12. [Definition of done](#12-definition-of-done)

---

## 1. Goal and demo narrative

**Goal.** Stand up the missing **Fabric IQ (Preview)** artefacts in the existing
`westus2` workspace so the Fabric → Foundry grounding seam runs **live** (not
synthetic), and package it as a repeatable **demo showcase**: a Swiss hospital
capacity copilot whose answers are grounded on a governed **ontology + data
product**, cite `hcp:*` concepts, and refuse re-identification — driven from
**both** the Foundry-hosted `ooa` agent and our Container Apps agent-host.

**Narrative (what the audience sees).** "Ask the occupancy copilot a question →
the answer is grounded on a certified OneLake **Data Product** in the **Hospital
Capacity Domain**, reasoned over the **Fabric IQ ontology** (`CapacityUnit`,
`Bed`, `Ward`), returned by a governed **Fabric Data Agent**, and consumed by a
**Foundry agent** — with RLS and the PHI refusal flowing through verbatim."

**Scope decisions (locked with @urruegg, 2026-07-18).**

| Decision | Choice |
| --- | --- |
| Depth | **Tier 3** — operational ontology + OneLake Data Product + Domain + Data Agent + live Foundry consumption |
| Region | **`westus2`** existing workspace `f3af9733-9503-4e92-98f9-a901d96f1c87` (ADR-0013 synthetic-only) |
| Admin | User holds **Fabric tenant-admin** rights (can flip the three toggles) |
| Surfaces | **Both** — Foundry `ooa` agent (native Fabric connection) **and** agent-host `ooa` (adapter live `ask_fn`) |

Out of scope: any PHI, any `switzerlandnorth` PROD path, the eastus2 Phase 2
rebuild (that stays Sprint 19), and certifying the data product for production
governance (demo endorsement only).

---

## 2. Current state and gap

Verified live against workspace `f3af9733-…` on 2026-07-18 (`az` + Fabric REST).

| Layer | Artefact | State |
| --- | --- | --- |
| Reference ontology | `docs/ontology/reference-layer.ttl`, `crosswalk.md`, `CI_DESIGN.md` | ✅ exists |
| Gold data | Lakehouse `lh_ihzhhpf_sit` (Delta gold tables) | ✅ exists |
| Semantic model | `capacity-dashboard` (Direct Lake; `dim_ward_capacityunit`, `bed_assignment`, `encounter`, `fact_capacity_baseline`, …) | ✅ exists |
| **Operational ontology** | **Fabric IQ ontology built from the semantic model** | ❌ **missing** |
| **Data Agent** | **Fabric Data Agent over semantic model + lakehouse + ontology** | ❌ **missing** |
| **Data Product** | **OneLake curated Data Product** | ❌ **missing** |
| **Domain** | **OneLake catalog Domain (Hospital Capacity)** | ❌ **missing** |
| Foundry consumption | Foundry `ooa` Fabric connection/tool | ❌ **missing** (adapter runs synthetic) |
| Agent-host live client | `FabricDataAgentAdapter(ask_fn=…)` live | ❌ **missing** (adapter runs synthetic) |

The seam **code** (adapter, orchestrator primary-grounding, refusal
short-circuit, register script) is done and proven E2E **synthetically** (Slice
0 / ADR-0033). This design fills the **Fabric-side artefacts** + **live wiring**.

---

## 3. Target artefact inventory (Tier 3)

1. **Operational Fabric IQ ontology** — built from `capacity-dashboard`, mapped
   to `reference-layer.ttl` via `crosswalk.md`. Entity types: `CapacityUnit`
   (+ `Bed`, `ORSlot`, `Room`, `StaffShift`, `Device`), `Ward`, `Hospital`,
   `Specialty`, `HospitalService`, `Encounter`, `CareTeam`, `Equipment`. First
   time-series binding: **bed state** (occupied / available / blocked /
   cleaning). Realises gate **G-A** (ADR-0014 §5).
2. **OneLake Data Product** — curated bundle (gold Delta tables, the semantic
   model, and the ontology) published for discovery, with a description, owner,
   and demo endorsement (Promoted).
3. **OneLake Domain** — "Hospital Capacity" business domain; the workspace is
   assigned to it so the data product is discoverable in the catalog.
4. **Fabric Data Agent** — sources = semantic model + lakehouse + ontology;
   instructions enforce concept-level answers with `hcp:*` citations, RLS, and
   the ADR-0016 PHI refusal (`REFUSE: re-identification-risk`); published to get
   a workspace + data-agent id + consumption endpoint.
5. **Foundry Fabric connection** — an Azure AI Foundry connection to the
   published Data Agent, attached as a grounding tool on the `ooa` Foundry agent.
6. **Agent-host live client** — a `FabricDataAgentClient.ask()` (`ask_fn`) that
   calls the published Data Agent, injected into `FabricDataAgentAdapter` when
   `FABRIC_DATA_AGENT_ENDPOINT` + `FABRIC_WORKSPACE_ID` + `FABRIC_DATA_AGENT_ID`
   env are set (synthetic fallback otherwise).

---

## 4. Architecture and data flow

```text
                    OneLake Domain: "Hospital Capacity"
                    └── Data Product (endorsed: Promoted)
                          ├── Lakehouse  lh_ihzhhpf_sit  (gold Delta)
                          ├── Semantic model  capacity-dashboard (Direct Lake)
                          └── Fabric IQ ontology  (CapacityUnit/Bed/Ward …)
                                        │  (grounds)
                                        ▼
                            Fabric Data Agent  (RLS + PHI refusal, hcp:* cites)
                                        │  published endpoint (workspace + agentId)
                    ┌───────────────────┴───────────────────┐
                    ▼ (native Fabric connection)             ▼ (data-plane REST ask_fn)
        Foundry ooa agent (eastus2)              Container Apps agent-host ooa (westus2)
                    │                                        │  FabricDataAgentAdapter(ask_fn=live)
                    ▼                                        ▼
             grounded answer + hcp:* citation  |  REFUSE: re-identification-risk
```

- **Precedence** (unchanged, per ADR-0033 / `orchestrator/dispatch.py`): Data
  Agent is **primary** grounding; table grounding is the loud-degradation
  fallback.
- **Refusal**: the Data Agent's `REFUSE:` propagates verbatim; neither surface
  routes around it.
- **Auth**: Workload Identity Federation (OIDC) for autonomous runs; OBO when
  human-triggered. Read ceiling only (`FR-ONT-008`, AGENTS.md §3).

---

## 5. Prerequisites and tenant-admin gates

**Admin toggles (M0, user performs; ~1 h propagation).**

1. Admin portal → Tenant settings → **Copilot and Azure OpenAI Service** →
   enabled for the tenant (or a security group covering the demo users).
2. **Designate the SIT F2 capacity as a Fabric Copilot capacity** (capacity
   settings). F2 is sufficient for the Data Agent; F64 only adds free viewers.
3. **Cross-geo processing and storage** enabled (Copilot may process outside
   `westus2`). Permitted for demo/synthetic per ADR-0013; **must not** be used
   for PHI (ADR-0016 keeps data synthetic).

**Data prerequisites (already met).** Read access to `capacity-dashboard` +
`lh_ihzhhpf_sit`; both live in the target workspace.

**Governance prerequisite.** Confirm the ADR-0013 demo exception window
(`EX-2026-07-02-westus2-demo`, expiry 2026-09-30) still covers the demo date; if
the demo is after expiry, renew the exception first.

---

## 6. Guardrails

| Guardrail | Source | How this design honours it |
| --- | --- | --- |
| Synthetic data only in westus2 | ADR-0013 | No PHI ingested; ontology + data agent operate on synthetic gold |
| No PHI in demo scope | ADR-0016 | Data Agent instructions refuse re-identification; agent-host + Foundry propagate `REFUSE:` |
| Preview not on regulated critical path | ADR-0006 / ADR-0014 §2 | Fabric IQ ontology used **only** in demo scope; regulated path untouched |
| Gate G-A (MVO in demo) | ADR-0014 §5 | M1 delivers operational ontology + bed-state binding in westus2 |
| Reference↔operational conformance | ADR-0014 §4 / `docs/ontology/CI_DESIGN.md` | M1 validates crosswalk; CI conformance check runs |
| Read-only grounding | ADR-0033 / AGENTS.md §3 | Data Agent + both adapters are `read` ceiling |
| Approval for live registration | AGENTS.md §4 | M4 `_apply` runs only after `approved-to-apply` |

---

## 7. Region and cross-region posture

- Fabric IQ layer stays in **`westus2`** (existing workspace, fastest, ADR-0013
  compliant). Foundry control plane is in **`eastus2`** (ADR-0032).
- The Foundry `ooa` agent therefore consumes the Data Agent **cross-region**
  (eastus2 → westus2). Acceptable for a demo: adds a little latency, no data
  residency issue (synthetic). Documented as a known demo-scope trade-off; the
  Phase 2 eastus2 rebuild (Sprint 19) removes the hop.
- The agent-host (`westus2`) consumes the Data Agent **in-region**.

---

## 8. Build sequence (milestones)

| Milestone | Outcome | Gate |
| --- | --- | --- |
| **M0** | Tenant toggles on; capacity is Copilot-capacity; exception window confirmed | admin |
| **M1** | Operational Fabric IQ ontology built from `capacity-dashboard`; bed-state time series; crosswalk conforms | **G-A** |
| **M2** | OneLake "Hospital Capacity" Domain + endorsed Data Product published | — |
| **M3** | Fabric Data Agent created, instructed (RLS + PHI refusal + hcp:* cites), tested in playground, **published** | — |
| **M4** | Foundry Fabric connection on `ooa`; `_apply` implemented + run (`approved-to-apply`); Foundry E2E green; **closes #251** | AGENTS.md §4 |
| **M5** | Agent-host live `ask_fn` wired + env injected; redeployed; E2E re-proof returns **live** hcp:* citations | — |
| **M6** | Demo script + "Fabric IQ ready" evidence doc + ADR-0034 + registry/PRD updates | — |

Dependency order: M0 → M1 → M2 → M3 → (M4 ∥ M5) → M6. M4 and M5 are independent
once M3 publishes the Data Agent.

---

## 9. Demo script (the golden path)

1. **Catalog** — open OneLake catalog → "Hospital Capacity" Domain → the endorsed
   Data Product (show lineage: lakehouse + semantic model + ontology).
2. **Ontology** — show the Fabric IQ ontology graph (`CapacityUnit → Bed`,
   `Ward`, bed-state time series).
3. **Data Agent** — in the Fabric Data Agent playground: ask "current bed
   occupancy for ward B?" → concept-level answer citing `hcp:CapacityUnit` /
   `hcp:Bed`; ask "patient name + DOB for bed 3?" → `REFUSE:
   re-identification-risk`.
4. **Foundry surface** — same two prompts against the Foundry `ooa` agent → same
   grounded answer + citation, same refusal (proves cross-region consumption).
5. **App surface** — same two prompts against the deployed agent-host `ooa`
   (`POST /agents/ooa-agent/chat`) → **live** hcp:* citations (no longer
   synthetic) + refusal.
6. **Evidence** — show the "Fabric IQ ready" evidence doc mapping each of the 5
   readiness points (readiness §6 of the parent design) to a live artefact.

---

## 10. Risks and mitigations

| # | Risk | Mitigation |
| --- | --- | --- |
| R1 | Tenant toggle propagation delay (~1 h) or blocked by tenant policy | M0 first; verify with a smoke Data Agent before building the rest |
| R2 | Fabric IQ ontology (Preview) API/portal changes or is unavailable in westus2 | Fallback: Data Agent grounds on semantic model + lakehouse only; ontology becomes a "concept map" slide — seam still live |
| R3 | Foundry native Fabric-connection shape differs from expectation | M4 spikes the connection in the portal first; script the `_apply` to the confirmed shape |
| R4 | Cross-region latency (eastus2→westus2) hurts demo | Pre-warm; acceptable for demo; note Phase 2 removes it |
| R5 | Data Agent answers leak a synthetic identifier that looks like PHI | Defence-in-depth `contains_sensitive` redaction already in `dispatch.py`; Data Agent instructions forbid row-level identifiers |
| R6 | Cost of Copilot-capacity + cross-geo | F2 stays; suspend capacity after demo (existing lifecycle workflow) |

---

## 11. Requirements traceability

- Realises: `FR-ONT-002` (operational ontology in Fabric IQ), `FR-ONT-004`
  (ground on ontology entities), `FR-ONT-008` (Fabric→Foundry consumption seam,
  live), `FR-ONT-001` (reference↔operational crosswalk), `FR-GOV-ONT-003` (CI
  conformance), `NFR-AI-002/004`.
- Advances gate **G-A** (ADR-0014 §5) to "met" in demo scope.
- Closes issue **#251** (live Fabric Data Agent registration).
- New ADR **ADR-0034** records the demo-scope Fabric IQ artefacts + live wiring
  decision (supplements ADR-0033; honours ADR-0013/0014/0016).

---

## 12. Definition of done

- [ ] M0 tenant toggles verified; ADR-0013 exception window confirmed.
- [ ] M1 operational Fabric IQ ontology built + bed-state binding; crosswalk conformance green (gate G-A evidence captured).
- [ ] M2 "Hospital Capacity" Domain + endorsed Data Product published and discoverable.
- [ ] M3 Fabric Data Agent published; playground shows grounded hcp:* answer + PHI refusal.
- [ ] M4 Foundry `ooa` consumes the Data Agent live (native connection); `_apply` implemented + run with `approved-to-apply`; #251 closed.
- [ ] M5 agent-host `ooa` returns **live** hcp:* citations after redeploy; refusal still verbatim.
- [ ] M6 demo script rehearsed; "Fabric IQ ready" evidence doc green; ADR-0034 merged; AGENTS.md fabric-data-agent row + PRD traceability updated.
