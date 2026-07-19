# Fabric IQ Layer to Foundry IQ Readiness — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 2.2.0 |
| **Date** | 2026-07-19 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | 2.1.0 (recorded the Phase 1 delivery + Phase 2 PROD data-load pause on the path-based notebook layout, #253). 2.2.0 records that the **Phase 2 stale-notebook blocker is resolved by Curavias P1a** — the operational medallion notebooks are modernized to `saveAsTable('{bronze,silver,gold}.*')`, the OneLake uploader is parameterized, and a gold-schema parity check is added, superseding [#253](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/253). See §8.1. |
| **Anchor triggers** | Sprint 18 completion (Foundry control plane live in eastus2, 8 agents registered, no grounding surface wired); the undesigned Fabric-to-Foundry consumption seam; region split (Foundry+PROD in eastus2 vs. Fabric IQ in westus2) |
| **Runtime posture** | GitHub Copilot coding agent + Superpowers-first execution; Bicep-first infra; Fabric Git integration + `fabric-cicd` for Fabric assets |
| **Related sprints** | [Sprint 17 — Fabric Git CI/CD + lakehouse schema](2026-07-10-sprint-17-fabric-git-cicd-and-lakehouse-schema-design.md); [Sprint 18 — Foundry control plane eastus2](2026-07-17-sprint-18-foundry-eastus2-control-plane-design.md); [Sprint 19 — PROD eastus2 full deploy](2026-07-17-sprint-19-prod-eastus2-full-deployment-design.md); Sprint 21 — trusted external signals (follow-on) |
| **Related ADRs** | [ADR-0014 (Fabric IQ ontology backbone, GA-gated)](../../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md); [ADR-0013 (US demo-scope)](../../adr/0013-temporary-us-region-demo-scope.md); [ADR-0016 (no PHI in demo)](../../adr/0016-no-phi-in-mvp-demo-scope.md); [ADR-0035 (PROD Fabric IQ in westus2)](../../adr/0035-fabric-iq-layer-region-westus2.md); ADR-0026/0027 (Sprint 17); ADR-0032 (Foundry control plane eastus2) |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Context and problem statement](#2-context-and-problem-statement)
3. [Decisions taken (this brainstorm)](#3-decisions-taken-this-brainstorm)
4. [Target-state architecture](#4-target-state-architecture)
5. [The consumption seam contract](#5-the-consumption-seam-contract)
6. [Fabric IQ ready definition](#6-fabric-iq-ready-definition)
7. [Dev/deploy cycle — L3 gated release train](#7-devdeploy-cycle--l3-gated-release-train)
8. [Delivery roadmap](#8-delivery-roadmap)
9. [Governance, degradation, testing, risks](#9-governance-degradation-testing-risks)
10. [Requirements traceability](#10-requirements-traceability)
11. [Definition of done](#11-definition-of-done)

---

## 1. Goal and desired end state

Establish the **Fabric IQ layer** — ontology, OneLake data product, semantic data model, and Fabric Data Agent — as a **collocated, reproducibly deployable, Foundry-consumable** grounding surface in `eastus2`, and wire it into the 8 Foundry agents that Sprint 18 left live but ungrounded.

Two threads are addressed together, per the originating request:

1. **Improve the Fabric development and deployment cycle** — move from hand-rolled `updateDefinition` REST pushes to Git integration + `fabric-cicd` parameterized deployment with validation gates, so the whole layer can be rebuilt in a new region on demand.
2. **Establish the Fabric IQ layer ready for Foundry** — a governed, discoverable, RLS-preserving concept-level query surface that upstream Foundry IQ and the platform agents consume.

**Desired end state:**

- The Fabric IQ layer (Fabric F2 capacity, workspace, lakehouse, semantic model, ontology, Data Agent) runs in `eastus2` alongside the Foundry control plane and PROD.
- Each of the 6 operational copilots (bmca, ooa, dca, orsa, sba, csa) grounds through the Fabric Data Agent as a native **Microsoft Fabric data-agent tool**, with a Foundry IQ knowledge base as secondary context and `fabric-mcp` for actions.
- The layer is published as a **certified OneLake Data Product** inside a Fabric **Domain**, discoverable by Foundry IQ.
- The layer deploys via `fabric-cicd` from GitHub Actions with an **L3 gated release train** (semantic-model verify, ontology-conformance strict, gold-schema, Data-Agent golden tasks).
- A single **"Fabric IQ ready" evidence document** gates Foundry consumption and only goes green when all component gates + the seam golden tasks pass.

---

## 2. Context and problem statement

### 2.1 What each planned sprint touches

| Sprint | Layer touched | Status |
|--------|---------------|--------|
| Sprint 17 | Platform plumbing — Fabric Git integration + `gold.*` schema hardening | Planned |
| Sprint 18 | Consumer — Foundry control plane + 8 agents in eastus2 | Complete |
| Sprint 19 | Region/infra — full PROD fresh build in eastus2 (incl. Fabric F2) | Planned |
| Sprint 21 | Ontology extension — trusted external signals (CAP) to CSA triggers | Planned (follow-on) |

**The gap:** none of these owns the **seam** — how Foundry agents consume the Fabric IQ layer. Sprint 18 registered 8 agents but wired no grounding surface. That seam is the least-proven, highest-risk element and is the centre of this design.

### 2.2 The region split

The Foundry control plane (Sprint 18) and PROD (Sprint 19) target `eastus2`. The Fabric IQ layer is currently pinned to `westus2` per [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md). Left unresolved, every grounded answer incurs a cross-region hop + data egress and two-region governance.

### 2.3 Preview posture

Fabric IQ Ontology remains preview. [ADR-0014 §2](../../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#2-regulated-critical-path-stays-ga-only) permits preview use in the demo scope (synthetic data only, US region) — so the operational ontology layer is usable now for this demo without touching the regulated Swiss critical path.

---

## 3. Decisions taken (this brainstorm)

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Produce **architecture + roadmap** in one spec | The seam is undesigned *and* the sprints need sequencing. |
| D2 | ~~Collocate the Fabric IQ layer in eastus2~~ **RELAXED (2026-07-19, [ADR-0035](../../adr/0035-fabric-iq-layer-region-westus2.md)):** PROD Fabric IQ stays in **westus2** — the subscription's eastus2 Fabric quota is **0 CU** (Sprint 19 §7e). The Foundry(eastus2)→Fabric(westus2) cross-region seam is retained; re-pointing to eastus2 later is a variable-library change, not a rebuild. | Original rationale (remove the hop) is not achievable without an eastus2 Fabric quota-increase; demo scope tolerates the HTTPS hop (ADR-0013). |
| D3 | Seam = **Fabric Data Agent published into Foundry as primary grounding tool**; **Foundry IQ KB secondary**; **`fabric-mcp` for actions** | Preserves the ontology + semantic model + RLS + refusal rules already designed (ADR-0014, Data Agent spec). |
| D4 | "Product Domain" = **Fabric Domain + OneLake Data Product** | Governed, catalog-discoverable bundle Foundry IQ can point at. |
| D5 | Target **L3 gated release train** (`fabric-cicd` + variable libraries + gates), delivered incrementally | A fresh eastus2 build is where reproducible, gated deployment pays off. |
| D6 | **Base layer = "ready"**; Sprint 21 external signals is a **follow-on** that rides the same seam | Bounds scope; external signals extend, they do not block readiness. |
| D7 | **Build the `fabric-cicd` release train first, then deploy PROD reproducibly** (2026-07-19) — before mirroring content into the PROD workspace, land Git integration + `fabric-cicd` + variable libraries (Sprint 17 Phase 1), validated against SIT. PROD then deploys by changing variable-library values (region/workspace/lakehouse). | User decision (2026-07-19): favour a proper, repeatable release train over a one-off portal mirror, so PROD (westus2) and any future eastus2 re-point are push-button. |

---

## 4. Target-state architecture

Foundry control plane + PROD compute in `eastus2`; **Fabric IQ layer in `westus2`**
(eastus2 Fabric quota = 0, [ADR-0035](../../adr/0035-fabric-iq-layer-region-westus2.md)).
The seam crosses regions over HTTPS and is region-agnostic via variable library.
Top to bottom:

```text
CONSUME · Foundry agents (bmca, ooa, dca, orsa, sba, csa, [data-quality, onboarding])
  each operational copilot carries:
    (1) Fabric data-agent tool    -> PRIMARY grounding (concepts + RLS)
    (2) Foundry IQ knowledge base -> SECONDARY unstructured context
    (3) fabric-mcp                -> ACTIONS only (trigger notebooks, data-quality)
        |
        v
SEAM · Fabric Data Agent (read-only NL surface)
  resolves NL -> MVO ontology concepts -> Direct-Lake semantic model; RLS + REFUSE enforced
        |
        v
FABRIC IQ LAYER  (published as a OneLake Data Product inside a Fabric Domain)
  - Ontology (MVO operational layer; preview OK in demo scope per ADR-0014)
  - Semantic Data Model (Direct Lake: capacity-dashboard)
  - gold.* lakehouse tables
        ^
        | build/deploy
BUILD/DEPLOY · fabric-cicd (L3) from GitHub Actions
  variable libraries (region/workspace/lakehouse IDs)
  gates: semantic-model verify | ontology-conformance (strict) | gold-schema | Data-Agent golden tasks
        ^
        |
PLATFORM · Fabric F2 capacity + workspace + lakehouse (westus2 — ADR-0035; Sprint 19 P6.1)
```

Key properties:

- **Concept-preserving:** the primary path resolves to `hcp:*` ontology entities, not raw columns.
- **Discoverable:** Foundry IQ discovers the certified OneLake data product; the Data Agent binds to the same workspace items.
- **Reproducible:** the entire layer is code in `fabric/` deployed by `fabric-cicd`; the region is a variable-library value.

---

## 5. The consumption seam contract

- **Mechanism:** register the read-only Fabric Data Agent as a **Microsoft Fabric data-agent tool/connection** on each consuming Foundry agent.
- **Auth:** agent-host **managed identity to Fabric workspace `Viewer`**; OBO when human-triggered. No secrets, no connection strings (consistent with [Data Agent spec §3](../../../agents/fabric-data-agent/AGENT.md)).
- **Consumers:** the 6 operational copilots — **bmca, ooa, dca, orsa, sba, csa**. `onboarding` (Entra-only) and `data-quality` (contract checks via `fabric-mcp`) do **not** take the seam.
- **Grounding precedence (written into each agent prompt):**
  1. Fabric Data Agent — *primary*, concept-level, RLS-enforced.
  2. Foundry IQ knowledge base — *secondary*, unstructured/doc context.
  3. `fabric-mcp` — *actions only* (trigger notebooks, data-quality).
- **Citation contract:** grounded answers carry the Data Agent's output contract — at least one `hcp:*` ontology entity cited (`FR-ONT-004`, `NFR-AI-002/004`).
- **Guardrail propagation:** RLS, ADR-0016 PHI gate-3, and the Data Agent `REFUSE:` codes flow **through** the Foundry agent verbatim; the Foundry agent may not route around a refusal.
- **Region-agnostic config:** workspace ID + data-agent endpoint come from a **variable library / env var**, so the same seam config lifts from `westus2` (Slice 0) to `eastus2` (Phase 2) unchanged.
- **Verification artefact:** a Foundry-agent-level **grounding golden task** per copilot — happy-path grounded answer + citation, plus a refusal-propagation case.

---

## 6. Fabric IQ ready definition

The layer is Foundry-consumable when all five hold:

1. **Ontology (operational layer)** — MVO entity types generated in Fabric IQ from the semantic model, static + bed-state time-series binding; crosswalk in sync with the reference layer, **ontology-conformance CI flipped to strict**. Preview permitted in demo scope (ADR-0014).
2. **OneLake Data Product** — a Fabric **Domain** + published **data product** bundling the semantic model + `gold.*` + ontology, with rich metadata and **Certified endorsement**, discoverable by Foundry IQ.
3. **Semantic Data Model** — Direct-Lake `capacity-dashboard`, passing the existing verify gate (16 relationships / 27 measures / 6 roles) with RLS roles intact.
4. **Fabric Data Agent** — deployed in-region, workspace `Viewer` identity, three golden tasks green (happy / failure / PHI refusal), published as a Foundry tool.
5. **Readiness gate** — one **"Fabric IQ ready" evidence doc** that only goes green when items 1-4 plus the §5 seam golden tasks pass. This authorizes Foundry consumption.

---

## 7. Dev/deploy cycle — L3 gated release train

Maturity ladder, delivered incrementally:

| Level | What | Delivered in |
|-------|------|--------------|
| **L1** | Fabric Git integration (`fabric-sync` branch, `fabric/` folder), gold schema hardening. Repo-to-Fabric via manual "Update all". | Sprint 17 |
| **L2** | `fabric-cicd` from GitHub Actions deploys item definitions into the target workspace (SIT / PROD-eastus2) with **variable libraries** for region/workspace/lakehouse IDs. Reproducible rebuild. | Sprint 17, used in Sprint 19 |
| **L3** | L2 + validation gates wired into deploy: semantic-model verify, ontology-conformance (**strict**), gold-schema, Data-Agent golden tasks; item-level diff before deploy. Fail-closed. | Phase 2/3 |

L2 is the vehicle that **builds the Fabric IQ layer fresh in eastus2** in Sprint 19 — the same parameterized deploy targets a new region by changing variable-library values.

---

## 8. Delivery roadmap

Approach: **seam-first thin slice** — retire the highest risk (the seam) first; every later phase rides a proven pattern.

| Phase | Timing | Scope | Exit |
|-------|--------|-------|------|
| **Slice 0** | days (independent) | Wire **one** Foundry agent (ooa) to the existing `westus2` Fabric Data Agent as a Fabric data-agent tool. 1 grounding golden task. | Seam proven; ADR (seam pattern) + grounding-contract doc |
| **Phase 1** | Sprint 17 | Git integration + gold schema hardening + introduce `fabric-cicd` + variable libraries (L1 to L2), validated against SIT. **Prerequisite for the PROD build (D7).** | ADR-0026/0027; layer reproducibly deployable |
| **Phase 2** | Sprint 19 | `fabric-cicd` builds the Fabric IQ layer **fresh in westus2** ([ADR-0035](../../adr/0035-fabric-iq-layer-region-westus2.md): PROD Fabric capacity `fabricihzhhpfprod` is westus2) — workspace `ws-ihzhhpf-prod-data`, lakehouse, semantic model, ontology, Data Agent; point the seam variable lib at the PROD workspace; publish OneLake data product + Domain; wire L3 gates. | PROD Fabric IQ live in westus2; seam pointed at PROD |
| **Phase 3** | harden | Flip ontology-conformance to strict; **Certify** data product; run seam golden tasks across all 6 copilots; publish **"Fabric IQ ready" evidence doc**. (No westus2 sunset — westus2 **is** the PROD end-state per ADR-0035; only a future eastus2 quota-increase would re-point the layer.) | Readiness gate green |
| **Phase 4** | Sprint 21 (follow-on) | CAP-based external-signals ontology extension to CSA triggers. Rides the same seam. | Signals extension live |

**Dependencies:** Slice 0 is independent (uses existing westus2). Phase 1 is a prerequisite for Phase 2's `fabric-cicd` build. Phase 2 depends on Sprint 18 (done) + Sprint 19 infra. Phase 3 depends on Phase 2. Phase 4 depends on the Phase 3 seam.

### 8.1 Execution notes (2026-07-19)

- **Phase 1 — delivered.** `fabric-cicd` release train committed (`data-platform/fabric/environments.yml`, `data-platform/reports/parameter.yml`, `data-platform/scripts/fabric/deploy_fabric_cicd.py`, `.github/workflows/fabric-cicd-deploy.yml`, runbook `README-fabric-cicd.md`). Static validate green for SIT + PROD; live `FabricWorkspace` construction + parameter-file validation + item discovery confirmed (no publish). PROD workspace `ws-ihzhhpf-prod-data` (`399b73f6-…`) created; PROD lakehouse `lh_ihzhhpf_prod` recreated **schemas-enabled** (`4f73c480-6c85-4823-bb98-4e66780c527f`, `defaultSchema=dbo`) after the first attempt was non-schema.
- **Phase 2 — PROD data-load PAUSED (user decision).** The as-built SIT gold is a **flat schemas-enabled** layout (`gold.dim_hospital`, `gold.encounter`, `gold.bed_assignment`, `gold.or_case`, …) that the Direct Lake model binds to. The committed **operational** medallion notebooks (`03_gold_master_data`, `03_gold_eventstream`, `04_load_or_samples`) instead write the **old path-based** layout (`Tables/gold/reference/…`, `Tables/gold/patient-flow/…`, `Files/gold/…`) and `04_load_or_samples` reads repo-relative paths absent in Fabric. Only BVA + evidence already use `saveAsTable('gold.*')`. A faithful fresh rebuild therefore requires **notebook modernization first** — tracked in [issue #253](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/253). Phase 1 + the schemas-enabled PROD lakehouse remain in place; Phase 2 resumes once #253 lands (or via an explicit gold-copy decision).
- **Phase 2 blocker — RESOLVED by Curavias P1a (2026-07-19).** The stale-notebook blocker above is delivered by the Curavias shared-master-data design ([spec](2026-07-19-curavias-shared-master-data-and-ontology-design.md) §4.1–4.4) and its [P1a implementation plan](../plans/2026-07-19-curavias-p1a-golden-source-reproducible-medallion.md), tracked as [Sprint 22 / #254](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/254). P1a makes git the single source of truth for the capacity master data (`data/master-data/capacity/` + validator + `master-data.yml` CI gate), rewrites `01_bronze` / `02_silver` / `03_gold_master_data` / `04_load_or_samples` / eventstream `03_gold_eventstream` to `saveAsTable('{bronze,silver,gold}.*')`, parameterizes `upload_to_onelake.py` by workspace/lakehouse (removing the hard-coded SIT GUIDs), and adds a `verify_gold_schema.py` parity check against the `capacity-dashboard` contract. Phase 2 resumes once the P1a live rebuild proof (SIT clone + empty PROD) is captured; #253 is superseded by this work. The unified `dim_hospital`→Curavias-tenant spine + org/skills ontology is the follow-on [Sprint 23 / #255](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/255) (P1b).

---

## 9. Governance, degradation, testing, risks

### 9.1 Approval gates (AGENTS.md §4)

- Phase 2 (PROD westus2 build) and Phase 3 (data-product certification) are `deploy` class to require `approved-to-apply`. (No westus2 Fabric sunset — westus2 is the PROD end-state per [ADR-0035](../../adr/0035-fabric-iq-layer-region-westus2.md).)
- Slice 0 attaches a **read-only** Data Agent to require no approval.
- The Fabric data-agent tool is a **Foundry-native connection, not a new MCP server** to be documented in `AGENTS.md`, no MCP allow-list change.
- **New ADRs:** seam pattern; [ADR-0035](../../adr/0035-fabric-iq-layer-region-westus2.md) (PROD Fabric IQ region = westus2, relaxing D2, annotating ADR-0013/0014); plus Sprint 17's 0026/0027.

### 9.2 Degradation (fail loud, never silent)

- If the Fabric Data Agent is unavailable, the Foundry agent drops to the Foundry IQ KB **and states "grounding degraded"** — it never answers ungrounded.
- RLS / `REFUSE:` outputs surface verbatim.
- A `fabric-cicd` deploy failure **fails the readiness gate closed**.

### 9.3 Testing / verification

Slice 0 grounding golden task, then per-copilot seam golden tasks (happy + refusal-propagation), then existing gates (semantic-model verify, ontology-conformance **strict**, gold-schema, Data-Agent goldens), then Bicep `what-if` for Sprint 19 infra, then the composite **"Fabric IQ ready" evidence doc**.

### 9.4 Key risks

| # | Risk | Mitigation / fallback |
|---|------|----------------------|
| R1 | Fabric IQ preview availability in eastus2 | Verify at build; keep westus2 layer until confirmed |
| R2 | Fabric-data-agent-as-Foundry-tool maturity (preview/GA) | Verify; fallback = `fabric-mcp` query path |
| R3 | Building the layer twice (westus2 then eastus2) | Region-agnostic variable library makes the second build config-only |
| R4 | 3-sprint scope creep | Bounded by phase boundaries + the readiness gate |

---

## 10. Requirements traceability

- Realises: `FR-ONT-001...007`, `FR-CX-001/002/006`, `FR-GOV-ONT-001...003`, `NFR-ONT-001`, `NFR-AI-002/003/004`.
- **New requirement flagged:** one `FR` for the Fabric-to-Foundry consumption seam (grounding precedence + refusal propagation + citation contract). `docs/PRD.md` §7 traceability matrix to be updated in the implementing PR.

---

## 11. Definition of done

- [ ] Slice 0 grounding proven against westus2; seam ADR + grounding-contract doc committed.
- [ ] Sprint 17 delivers Git integration + gold schema hardening + `fabric-cicd` + variable libraries (ADR-0026/0027).
- [ ] Sprint 19 builds the Fabric IQ layer fresh in eastus2 via `fabric-cicd`; seam re-pointed; OneLake data product + Domain published.
- [ ] L3 gates wired into deploy; ontology-conformance flipped to strict.
- [ ] Per-copilot seam golden tasks green (happy + refusal propagation) for the 6 operational copilots.
- [ ] "Fabric IQ ready" evidence doc green; westus2 Fabric sunset (approved-to-apply).
- [ ] `docs/PRD.md` §7 updated with the new seam FR; ADRs merged.
- [ ] Sprint 21 external-signals extension identified as follow-on riding the same seam.
