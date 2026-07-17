# AMA Review — Trusted External Signals as CSA Triggers & Ontology Extension

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-17 |
| **Author** | Urs Rüegg |
| **Status** | Draft for Review |
| **Previous Version** | — (initial version) |
| **Session date** | 2026-07-17 |
| **Session type** | Architecture Maturity Assessment (AMA) — outcome consolidation |
| **Subject** | Trusted Swiss external hazard signals as automatic triggers for the Capacity Simulation Agent (CSA), and the ontology + architecture extension required to consume them |
| **Session participant** | Hospital Data Scientist (domain subject-matter expert) |
| **Reviewer role** | Senior Azure Cloud Architect and Governance Reviewer (CAF, WAF, Zero Trust, Swiss public-sector compliance) |
| **Primary input** | [CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) (Draft v1.0) |
| **Builds on** | [2026-07-01 HCC & North Star Ontology AMA](./2026-07-01-ama-hcc-northstar-review.md); the CSA what-if design ([Sprint 16 CSA design](../superpowers/specs/2026-07-09-sprint-16-csa-design.md)); [ADR-0024 CSA tier classifier](../adr/0024-csa-tier-classifier-rules.md); [ADR-0014 Fabric IQ ontology backbone (GA-gated)](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Context Overview](#2-context-overview)
3. [Key Findings from Review Session](#3-key-findings-from-review-session)
4. [Deviation Analysis — Best Practice vs Current State](#4-deviation-analysis--best-practice-vs-current-state)
5. [New & Emerging Requirements](#5-new--emerging-requirements)
6. [Risk Assessment](#6-risk-assessment)
7. [Architecture & Governance Alignment Review](#7-architecture--governance-alignment-review)
8. [Compliance Evaluation — Swiss Public-Sector Context](#8-compliance-evaluation--swiss-public-sector-context)
9. [Recommendations & Next Steps](#9-recommendations--next-steps)
10. [Traceability Matrix](#10-traceability-matrix)
11. [Sprint Implementation Handoff](#11-sprint-implementation-handoff)
12. [Appendix A — Source Materials](#appendix-a--source-materials)

> **Reviewer prompt template:** the standard prompt used to conduct this review is maintained centrally in [docs/reviews/README.md — Standard Reviewer Prompt](./README.md#standard-reviewer-prompt-template) and reused across all AMA review sessions.

---

## 1. Executive Summary

The AMA session on 2026-07-17, held with a **Hospital Data Scientist**, evaluated a design proposal to let **official, trusted Swiss authority signals trigger the Capacity Simulation Agent (CSA) automatically**. Today the CSA runs what-if scenarios **on demand** (a duty manager asks). The proposal extends this so that when MeteoSwiss issues a heat warning, Alertswiss/Polyalert raises a civil-protection alert, or SED reports an earthquake, the CSA **proactively** simulates the matching capacity scenario and proposes doctrine-aligned response levers — **advisory only, human-in-the-loop**.

The proposal has three parts: (1) a **catalogue of trusted Swiss sources** grouped by hazard family and mapped to the existing CSA scenario families; (2) an **API / event-feed evaluation** identifying which feeds are event-ready today; and (3) an **ontology + architecture extension** that adds an external-signal domain plugging into the existing `ScenarioTemplate` + Swiss *Lage*-tier classifier seams established in Sprint 16.

The design is **well-aligned with the platform's existing patterns**: it reuses the CSA scenario families, the *Lage* tier classifier ([ADR-0024](../adr/0024-csa-tier-classifier-rules.md)), the Fabric IQ ontology backbone ([ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md)), the advisory/HITL discipline, and the platform's event-trigger model — it simply substitutes an **external, trusted, public authority feed** for an internal system event. Because the signals are **public and non-PHI**, they carry **light residency constraints** and can run in both the showcase (T-SHOW) and production (T-PROD) tracks. The main risks are **feed maturity** (CAP Suisse is officially maturing toward ~2027), **endpoint volatility** (many feeds are flagged "verify at build"), and **trigger-noise governance** (test/exercise/all-clear filtering and false-positive control).

### 1.1 Key risks (H = High, M = Medium, L = Low)

| # | Risk | Category | Severity |
| --- | --- | --- | --- |
| R-01 | **CAP Suisse — the strategic unifying standard — is still maturing** (full federal integration targeted ~2027); the design's primary alert channel is not yet a single stable endpoint | Technical | **H** |
| R-02 | **Endpoint / licence volatility** — most feeds (BAFU, BAG, ASTRA, SLF, NABEL, Swissgrid, NCSC, MeteoSwiss per-item API) are flagged "verify at build"; time-sensitive availability | Technical | **M** |
| R-03 | **Trigger-noise / false-positive governance** — without disciplined `status=Test\|Exercise` and all-clear filtering plus certainty/urgency thresholds, the CSA fires on non-actionable signals | Operational | **M** |
| R-04 | **Auto-activation without HITL discipline** could let the CSA act on an unverified external signal, breaching the advisory-only contract | Operational / Compliance | **M** |
| R-05 | **Ontology drift** — a new `ExternalSignal` domain that is not governed against the two-layer reference↔operational crosswalk repeats the drift risk raised in the North Star review | Technical / Governance | **M** |
| R-06 | **Provenance loss** — a signal consumed without `sourceAuthority` + `capIdentifier` + `trustTier` produces a recommendation that cannot be audited or cited | Compliance | **M** |
| R-07 | **Third-party proxy dependence** (Open-Meteo for MeteoSwiss ICON) may carry commercial-licence limits in production | Compliance / Commercial | **L** |
| R-08 | **Cantonal region scoping** — signals must be scoped to cantons containing the provider or the CSA fires on irrelevant regional hazards | Operational | **L** |

### 1.2 Overall maturity assessment

| Dimension | Maturity | Trend |
| --- | --- | --- |
| CSA on-demand what-if simulation (Sprint 16 baseline) | **Emerging** | Stable |
| Swiss *Lage* tier classifier (ADR-0024) | **Mature** | Stable |
| Advisory / HITL + region-pinned inference discipline | **Mature** | Stable |
| Event-trigger pattern (internal system events) | **Emerging** | Stable |
| **External trusted-signal ingestion** | **Absent** | New workstream (this review) |
| **External-signal ontology domain** (`ExternalSignal`, `TrustedSource`, `HazardType`, `TriggerRule`) | **Absent** | New workstream (this review) |
| CAP-standard alert consumption | **Absent** | New workstream — gated on CAP Suisse maturity |
| Trigger-noise / provenance governance | **Nascent** | To be defined (this review) |

### 1.3 Top 5 recommendations

1. **Design ingestion to the CAP standard now, bridge with source-specific APIs.** Model the ingestion contract around CAP fields (source, event, severity, certainty, urgency, area, onset/expires) so every future CAP-Suisse-emitting agency plugs in without a new parser. Until MeteoSwiss's CAP warning feed is live, bridge with the **pollable Alertswiss/Polyalert feed** plus **STAC/Open-Meteo-derived heat thresholds**.
2. **Ship the four highest-signal sources first.** Prioritise **MeteoSwiss** (heat — the flagship demo), **Alertswiss/Polyalert** (the government catch-all), **SED FDSN** (clean real-time earthquake API), and **BAG** (RSV/respiratory surge). These four cover the most compelling CSA demonstrations at the lowest integration effort.
3. **Adopt `DC-EXT-SIGNAL-v1` as the single normalisation contract** and enforce **mandatory provenance** (`sourceAuthority` + `capIdentifier` + `trustTier`) on every signal, surfaced in the CSA recommendation.
4. **Codify trigger-noise governance and HITL as first-class rules** — filter `status = Test\|Exercise` and all-clear; apply certainty/urgency thresholds; scope per-canton to the provider; keep the CSA strictly advisory with a human running/accepting the proposal. Back this with an **ADR for external-trigger governance**.
5. **Add the `FR-EXT-*` requirement family to the PRD** and register the `ExternalSignal` domain against the two-layer ontology crosswalk so the new entities are governed exactly like the North Star MVO.

---

## 2. Context Overview

### 2.1 Purpose of this document

Produce a structured, evidence-based **solution review** of the AMA session outcome for the *trusted external signals as CSA triggers* topic. The document identifies gaps, risks and inconsistencies; assesses alignment with Azure best practices, the platform's existing patterns, and Swiss governance models; and hands off a traceable brief to the sprint(s) that will implement the external-trigger workstream.

### 2.2 Inputs reviewed

| # | Input | Path / Reference | Role |
| --- | --- | --- | --- |
| 1 | *Curavias CSA — Trusted External Signals as Simulation Triggers & Ontology Extension* (Draft v1.0) | [CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) | **Primary** — source catalogue, API evaluation, ontology + architecture extension |
| 2 | HCC & North Star Ontology AMA review | [2026-07-01-ama-hcc-northstar-review.md](./2026-07-01-ama-hcc-northstar-review.md) | Baseline — CSA/ontology target state, two-layer ontology governance |
| 3 | Capacity metadata framework AMA review | [2026-06-29-ama-capacity-metadata-review.md](./2026-06-29-ama-capacity-metadata-review.md) | Baseline — 4-layer master-data model, external forecasting features (BAG/MeteoSwiss) |
| 4 | CSA what-if design spec (Sprint 16) | [2026-07-09-sprint-16-csa-design.md](../superpowers/specs/2026-07-09-sprint-16-csa-design.md) | Baseline — `ScenarioTemplate`, scenario families, CSA agent shape |
| 5 | CSA agent pack | [agents/csa-agent/AGENT.md](../../agents/csa-agent/AGENT.md) | Baseline — CSA Prepare/Run/Evaluate/Recommend contract, side-effect ceiling |
| 6 | ADR — CSA tier classifier (Swiss *Lage* doctrine) | [ADR-0024](../adr/0024-csa-tier-classifier-rules.md) | Constraint — the tier classifier external signals pre-seed |
| 7 | ADR — Fabric IQ ontology target backbone (GA-gated) | [ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) | Constraint — ontology realisation seam |
| 8 | ADRs — Swiss-region inference & PHI blocks | [ADR-0003](../adr/0003-swiss-regional-inference-for-phi.md), [ADR-0004](../adr/0004-block-global-and-data-zone-for-phi.md) | Constraint — residency posture for any combined data |
| 9 | Repository baseline | [PRD.md](../PRD.md), [ARCHITECTURE.md](../ARCHITECTURE.md), [DATA.md](../DATA.md), [AI.md](../AI.md), [COMPLIANCE.md](../COMPLIANCE.md), [SECURITY.md](../SECURITY.md) | Current design of record |

### 2.3 Baseline solution

The baseline is the **Swiss AI-Powered Patient Flow & Hospital Capacity Platform**, and specifically the **Sprint 16 CSA what-if system**: a `ScenarioTemplate` + discrete-event simulation with a **Swiss *Lage* tier classifier** (normale / besondere / ausserordentliche Lage) codified in [ADR-0024](../adr/0024-csa-tier-classifier-rules.md). The CSA runs **on demand**, is **advisory / HITL**, uses **region-pinned inference**, and grounds on the Fabric IQ ontology backbone ([ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md)). Scenario families are defined in the CSA catalogue (F1 infrastructure · F3 mass-casualty · F4 cyber · F5 supply · F6 surge/epidemic · F7 security · F8 environmental).

### 2.4 Scope of this review

The four AMA dimensions defined in the reviewer work instructions:

1. **Product Requirements (PRD)** — completeness, traceability, alignment with business and regulatory needs of the proposed `FR-EXT-*` family.
2. **Solution Design (SD)** — the external-signal ingestion, normalisation, streaming, ontology binding, and trigger architecture.
3. **Architecture** — Fabric Real-Time Intelligence (Eventhouse), Activator/Reflex trigger, connector pattern, and how they extend (not redraw) the existing architecture.
4. **Compliance & Security** — provenance, residency of public non-PHI signals, licence terms, HITL discipline, and trigger-noise governance in a Swiss public-sector context.

### 2.5 Assumptions

| # | Assumption | Basis |
| --- | --- | --- |
| A-01 | The Sprint 16 CSA (`ScenarioTemplate` + *Lage* classifier) is the target CSA runtime this extension plugs into | Source §4, §5; [ADR-0024](../adr/0024-csa-tier-classifier-rules.md) |
| A-02 | External hazard signals from federal authorities are **public and non-PHI** | Source §1, §5.7 |
| A-03 | CAP Suisse is the strategic unifying standard but full federal integration is targeted ~2027; today the pollable Alertswiss/Polyalert feed + source-specific APIs bridge the gap | Source §3.1, §7 (Caveats) |
| A-04 | Endpoint availability is **time-sensitive** — the source's confirmed items reflect documentation as of mid-July 2026 and must be re-verified at build | Source header note; §7 step 6; Appendix |
| A-05 | The Fabric IQ ontology backbone (ADR-0014) is the realisation target for the new `ExternalSignal` entity types (subject to the same Switzerland-region GA gating) | Source §5.6; [ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) |
| A-06 | The CSA remains **advisory / HITL**; external triggers propose but never auto-act on outbound coordination | Source §5.4, §5.7; [agents/csa-agent/AGENT.md](../../agents/csa-agent/AGENT.md) |
| A-07 | The proposed `FR-EXT-001…004` family is **not yet** in the PRD and is treated as new/emerging here | PRD review (no `FR-EXT-*` present); Source §5.7 |

---

## 3. Key Findings from Review Session

Findings are grouped by the AMA review dimensions. Every finding is traced to its source paragraph or artefact.

### 3.1 Product & Business Findings

**F-P-01 — External signals convert the CSA from reactive to proactive.** The core value move is that **official Swiss authority signals fire the CSA automatically** instead of waiting for a duty manager to ask. When MeteoSwiss issues a heat warning, the CSA proactively simulates *elderly heat surge → ED* (F8) and proposes doctrine-aligned levers. — *Source §1.*

**F-P-02 — Four sources carry the showcase.** The highest signal-to-effort set for the demo is **MeteoSwiss** (heat — flagship), **Alertswiss/Polyalert** (government catch-all), **SED** (clean real-time earthquake API) and **BAG** (RSV surge). These four cover the most compelling CSA demonstrations. — *Source §2 (priority note).*

**F-P-03 — Non-PHI, dual-track usability broadens the demo surface.** Because the signals are public and non-PHI, they carry light residency constraints and can run in **both** the showcase (T-SHOW) and production (T-PROD) tracks — unlike PHI-bound features. — *Source §1, §5.7.*

### 3.2 Architecture & Design Findings

**F-A-01 — The extension plugs into existing seams; it does not redraw the architecture.** The design adds an **external-signal domain** that feeds the *existing* `ScenarioTemplate` + *Lage* classifier. The trigger pattern mirrors the platform's internal event-trigger model, substituting an external trusted authority feed for an internal system event. — *Source §1, §4, §5.*

**F-A-02 — CAP Suisse is the unifying ingestion standard.** Two native alert channels exist today — **CAP Suisse via Alertswiss/Polyalert** (canton-scoped, severity-typed, government catch-all) and **SED FDSN** (clean, filterable, real-time). Designing ingestion around **CAP** (source, event, severity, certainty, urgency, area, onset/expires) future-proofs the CSA: as more agencies publish CAP, they plug in without new parsers. — *Source §3.1.*

**F-A-03 — A derive-vs-native split governs each feed.** Native alert feeds (CAP, FDSN) are **event-ready** and drive triggers directly. Model/observation feeds (MeteoSwiss STAC, Open-Meteo) are **threshold-derived** (poll forecast/obs, compute threshold crossing — e.g. apparent-temp ≥ warning level for N days). Secondary feeds (BAG, BAFU, NABEL, ASTRA, SLF, Swissgrid, NCSC) are enrichment, added iteratively. — *Source §3, §3.1.*

**F-A-04 — Live-event flow uses Fabric Real-Time Intelligence end-to-end.** Trusted sources → ingestion connectors (Logic Apps / Azure Functions) → normalise to `DC-EXT-SIGNAL-v1` → Event Grid / Eventstream → Fabric Eventhouse (KQL) + OneLake → `ExternalSignal` ontology entity (time-series binding) → Fabric Activator/Reflex (severity + `TriggerRule`) → CSA runs `ScenarioTemplate` → advisory proposal on the Whiteboard "Krisen & Szenarien" card (HITL). — *Source §5.4.*

**F-A-05 — The Fabric Activator is the Fabric-native equivalent of the platform's event trigger.** A Data Activator/Reflex rule watches the Eventhouse stream; when severity crosses a `TriggerRule` threshold for a region containing the provider, it invokes the CSA — reusing the platform's established event-trigger discipline. — *Source §5.4.*

### 3.3 Data & Ontology Findings

**F-D-01 — Seven new ontology classes extend the North Star model (BFO/OBO-aligned).** `TrustedSource` (organisation bearing an authority role), `HazardType` (taxonomy), `ExternalSignal`/`PublicWarning` (IAO information content entity — the concrete alert instance), `HazardEvent` (occurrent), `Severity`/`DangerLevel` (quality/scalar), `AffectedRegion` (reuse Location), `TriggerRule` (directive information entity), reusing/extending `ScenarioTemplate` and `LageTier`. — *Source §5.1.*

**F-D-02 — Relationships are RO-aligned and connect cleanly to the CSA.** `TrustedSource` **emits** `ExternalSignal`; `ExternalSignal` **has_hazard_type / has_severity / affects_region / valid_during**; `TriggerRule` **matches** (HazardType × Severity × Location) and **activates** `ScenarioTemplate`; `ExternalSignal` **raises** `LageTier` via rule; `Hospital` **located_in** `Location` **affected_by** `ExternalSignal`. — *Source §5.2.*

**F-D-03 — `DC-EXT-SIGNAL-v1` is the single normalisation contract.** All sources map to one contract carrying CAP-aligned fields (`signalId`, `sourceId`, `sourceAuthority`, `trustTier`, `capIdentifier`, `hazardType`, `severity`, `certainty`, `urgency`, `dangerLevel`, `region`, `effective/onset/expires`, `uri`, `status`, `mappedScenarioTemplate`, `defaultLageTier`). — *Source §5.5.*

**F-D-04 — Severity mapping pre-seeds the existing *Lage* tier.** CAP severity / Swiss danger levels map to the existing Swiss *Lage* classifier so external signals **pre-seed** the CSA tier already defined in [ADR-0024](../adr/0024-csa-tier-classifier-rules.md) (e.g. Heat L3→Tier 1–2, L4→Tier 2; earthquake M≥5→Tier 3; civil-protection alert→Tier 3). — *Source §5.3.*

**F-D-05 — `ExternalSignal` uses a dual binding in Fabric IQ.** A **static lakehouse table** (source, capId, headline, region, uri) **plus a time-series binding** from the Eventhouse `external_signals` stream (severity/validity over time) — the same mechanism the platform already uses for bed-state/vitals. The CSA Data Agent grounds on this subgraph so its proposals cite the exact source, CAP id and severity. — *Source §5.6.*

### 3.4 AI & Agent Findings

**F-AI-01 — The CSA remains advisory / HITL for external triggers.** The CSA **proposes**; a human runs/accepts; any outbound coordination (e.g. flag KSD/KATAMED) stays gated. The CSA never auto-acts on an external signal. — *Source §5.4, §5.7; consistent with [agents/csa-agent/AGENT.md](../../agents/csa-agent/AGENT.md).*

**F-AI-02 — Provenance is mandatory and surfaced in the answer.** Every `ExternalSignal` carries `sourceAuthority` + `capIdentifier` + `trustTier`; the CSA answer shows it. This strengthens explainability and regulatory acceptance. — *Source §5.7.*

**F-AI-03 — The worked heat example demonstrates the full advisory loop.** MeteoSwiss apparent-temp crosses L3 for ZH for 3 days (and/or Alertswiss issues a *Hitzewellen* CAP warning) → normalise → Eventhouse → Activator → CSA runs *Elderly heat surge → ED* → classifies *Lage* Tier 1–2 → **proposes** HHAP triggers, surge medical beds, summer staffing with the source cited → human accepts/adjusts. — *Source §6.*

### 3.5 Governance & Operating-Model Findings

**F-G-01 — Trigger-noise governance is explicit.** Filter `status = Test\|Exercise` and all-clear messages (as community CAP clients do); apply `certainty`/`urgency` thresholds; per-canton scope to the provider. — *Source §5.7.*

**F-G-02 — An ADR for external-trigger governance is proposed.** The source explicitly calls for an ADR to govern external triggers, alongside the `FR-EXT-*` family. — *Source §5.7.*

**F-G-03 — Trust tiers grade source authority.** A = official federal authority · B = para-federal / cantonal / research · C = aggregator/proxy (verify provenance). Priority triggers are Tier-A native-alert channels. — *Source §2, §3.1.*

### 3.6 Explicitly Open Questions Raised

Captured from the source so downstream sprints treat them as validation items rather than assumptions. All are marked **"Requires validation"**.

1. Confirm live **CAP-Suisse warning endpoints** (MeteoSwiss / BAFU) — direction confirmed, live endpoint to verify. *(Source §3, §7 step 6, Appendix)*
2. Confirm **Open-Meteo production licence** for the MeteoSwiss ICON proxy (non-commercial tier today). *(Source §3, Appendix)*
3. Confirm current **BAG dataset IDs** for respiratory/Sentinella surveillance. *(Source §3, §7 step 6)*
4. Confirm **ASTRA / DATEX II** dataset registration & auth. *(Source §3, §7 step 6)*
5. Confirm **SLF / NABEL / Swissgrid / NCSC** endpoints and terms. *(Source §3, §7 step 6)*
6. Decide the **threshold logic** for derive-type feeds (e.g. apparent-temp ≥ level for N days). *(Source §5.4)*
7. Confirm **CAP Suisse maturity timeline** (~2027) and the interim bridge strategy's lifespan. *(Source §7 Caveats)*

---

## 4. Deviation Analysis — Best Practice vs Current State

Best-practice references: **Microsoft Cloud Adoption Framework (CAF)**, **Azure Well-Architected Framework (WAF)**, **Zero Trust architecture**, **OASIS CAP (Common Alerting Protocol) / CAP Suisse**, **FDSN seismology web-service standard**, **BFO/OBO Foundry ontology principles**, **Fabric Real-Time Intelligence best practice**.

| # | Area | Best Practice | Observed Current State | Deviation / Gap | Impact |
| --- | --- | --- | --- | --- | --- |
| D-01 | **Trigger source** | Steering informed by **external authoritative early-warning** feeds (weather, civil protection, seismology, epidemiology) | CSA triggers on internal, on-demand requests only | External trusted-signal ingestion absent | **H** |
| D-02 | **Alert standardisation** | Consume alerts via a **single standard (CAP)** so new agencies plug in without new parsers | No CAP ingestion; no external-alert parser | CAP-standard consumption absent; gated on CAP Suisse maturity | **H** |
| D-03 | **Real-time ingestion** | Event-driven ingestion (Eventstream/Eventhouse/Activator) for time-sensitive hazard signals | Batch/forecast features only (BAG/MeteoSwiss as day/week features per 2026-06-29 review §1.4) | Real-time external-signal path not built | **M** |
| D-04 | **Ontology coverage** | Model external hazards/signals as first-class entities bound to live streams | Ontology covers capacity units; no `ExternalSignal`/`TrustedSource`/`HazardType`/`TriggerRule` | Four+ new entity types to author | **M** |
| D-05 | **Provenance & trust grading** | Every consumed signal carries source authority, identifier, and a trust tier, surfaced to the user | No trust-tier model for external inputs | Provenance/trust model to be added | **M** |
| D-06 | **Trigger-noise control** | Filter test/exercise/all-clear; certainty/urgency thresholds; geo-scoping | No external-trigger noise governance | Noise/false-positive governance absent | **M** |
| D-07 | **HITL on auto-triggers** | Automatic detection, **human-approved** action; never auto-act on outbound coordination | Advisory/HITL exists for on-demand CSA; not yet extended to auto-triggered runs | Extend HITL contract to auto-triggers | **M** |
| D-08 | **Feed reliability (WAF)** | Redundant / verified endpoints; graceful degradation when a feed is down | Single-source per hazard; many endpoints "verify at build" | Reliability & fallback per feed unassessed | **M** |
| D-09 | **Licence / terms compliance** | Confirmed production licence + attribution per source ("Source: MeteoSwiss") | Proxy (Open-Meteo) non-commercial tier; several terms unverified | Licence verification per feed required | **M** |
| D-10 | **Governance record (ADR)** | Cross-cutting trigger behaviour recorded in an ADR | No ADR for external-trigger governance yet | ADR to be authored | **M** |
| D-11 | **Two-layer ontology sync** | New domain governed against reference↔operational crosswalk + CI check | Crosswalk not yet extended to the external-signal domain | Extend crosswalk & CI conformance | **M** |
| D-12 | **Zero Trust — ingress** | Least-privilege, workload-identity connectors; validate untrusted external input at the boundary | Connectors not yet built; external input is untrusted by definition | Boundary validation + workload identity for connectors | **M** |

---

## 5. New & Emerging Requirements

Every requirement below is proposed **new** or **implied** by the AMA outcome. The source proposes the `FR-EXT-*` family (§5.7); this review formalises it and adds governance/NFR anchoring. Each row states the source and the validation still required. **None are yet present in [PRD.md](../PRD.md).**

### 5.1 External-signal ingestion requirements (new family `FR-EXT-*`)

| ID | Requirement | Anchored to | Source | Validation Needed |
| --- | --- | --- | --- | --- |
| `FR-EXT-001` | Ingest trusted external hazard signals and normalise them to `DC-EXT-SIGNAL-v1` (CAP-aligned fields) | extends FR-DATA | Source §5.5, §5.7 | Live CAP-Suisse endpoints; BAG/ASTRA/SLF dataset IDs & auth |
| `FR-EXT-002` | Map signal → scenario → *Lage* tier via `TriggerRule` (HazardType × Severity × Region) | extends `FR-ONT-005`; [ADR-0024](../adr/0024-csa-tier-classifier-rules.md) | Source §5.2, §5.3, §5.7 | Threshold logic for derive-type feeds |
| `FR-EXT-003` | Activate the CSA **advisory / HITL** when severity crosses a `TriggerRule` threshold for a region containing the provider | extends FR-CX / `NFR-AI-*` | Source §5.4, §5.7 | HITL contract extension for auto-triggers; Activator rule design |
| `FR-EXT-004` | Attach **provenance & trust tier** (`sourceAuthority` + `capIdentifier` + `trustTier`) to every signal and surface it in the CSA answer | extends `NFR-AI-003` | Source §5.7 | Provenance rendering in CSA output |
| `FR-EXT-005` | Apply **trigger-noise governance** — filter `status = Test\|Exercise` + all-clear; certainty/urgency thresholds; per-canton geo-scoping | new | Source §5.7 | Threshold + geo-scoping policy per hazard family |
| `FR-EXT-006` | Consume alerts via the **CAP standard** so additional CAP-emitting agencies plug in without new parsers | extends FR-DATA | Source §3.1 | CAP Suisse maturity timeline (~2027); interim bridge lifespan |

### 5.2 External-signal ontology requirements (extends `FR-ONT-*`)

| ID | Requirement | Anchored to | Source | Validation Needed |
| --- | --- | --- | --- | --- |
| `FR-EXT-ONT-001` | Add `TrustedSource`, `HazardType`, `ExternalSignal`, `HazardEvent`, `Severity/DangerLevel`, `TriggerRule` as BFO/OBO-aligned entity types; reuse `AffectedRegion` (Location), `ScenarioTemplate`, `LageTier` | extends `FR-ONT-001/003` | Source §5.1, §5.2 | Subtype/relationship review against provider data |
| `FR-EXT-ONT-002` | Bind `ExternalSignal` with a **static lakehouse table + time-series Eventhouse binding**; ground the CSA Data Agent on the subgraph | extends `FR-ONT-002/004`; [ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) | Source §5.6 | Fabric IQ Switzerland-region GA gating (same as ADR-0014) |
| `NFR-EXT-ONT-001` | Govern the external-signal domain against the **reference↔operational crosswalk** with a CI conformance check | `NFR-ONT-001` | Source §5.1; North Star review §5.4 | Crosswalk artefact + CI extension |

### 5.3 Governance & compliance requirements

| ID | Requirement | Source | Validation Needed |
| --- | --- | --- | --- |
| `FR-EXT-GOV-001` | Author an **ADR for external-trigger governance** (trust tiers, HITL, noise filtering, provenance) | Source §5.7 | CODEOWNERS review |
| `NFR-EXT-GOV-001` | Maintain a **build-time endpoint/licence verification list** (Appendix) and re-verify before production | Source §7 step 6, Appendix | Owner + cadence |
| `NFR-EXT-GOV-002` | Confirm **production licence + attribution** per source (e.g. "Source: MeteoSwiss"); Open-Meteo prod tier | Source §7 Caveats, Appendix | Legal / licence review |

---

## 6. Risk Assessment

Risks are categorised **Technical**, **Compliance / Regulatory**, or **Operational**. Impact = business impact if the risk materialises. Likelihood = current-state assessment.

### 6.1 Technical risks

| # | Description | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- | --- |
| T-01 | **CAP Suisse still maturing (~2027)** — the strategic single-standard channel is not a stable endpoint yet | Fallback to per-source parsers; rework when CAP goes live | **H** | Design to CAP now; bridge with pollable Alertswiss/Polyalert + STAC/Open-Meteo thresholds; isolate parsers behind `DC-EXT-SIGNAL-v1` |
| T-02 | **Endpoint / licence volatility** — most secondary feeds flagged "verify at build" | Broken ingestion; silent trigger loss | **M** | Build-time verification list (`NFR-EXT-GOV-001`); health-check + alert per connector |
| T-03 | **Threshold-derive complexity** for MeteoSwiss/Open-Meteo (compute crossing over N days) | False or missed heat triggers | **M** | Explicit, versioned threshold rules; validate against historical heat episodes |
| T-04 | **Ontology over-modelling** of external hazards before access patterns stabilise | Semantic churn, latency | **L** | Start with the four priority sources; add secondary feeds iteratively |
| T-05 | **Fabric IQ preview / Switzerland-region GA** gating the operational `ExternalSignal` binding | Delivery delay for the ontology binding | **M** | Same gate as [ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md); keep a property-graph fallback; static binding usable pre-GA |

### 6.2 Compliance / regulatory risks

| # | Description | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- | --- |
| C-01 | **Provenance loss** — a signal consumed without authority/id/trust-tier yields an un-citable recommendation | Regulatory acceptance risk | **M** | Mandatory provenance (`FR-EXT-004`); render in CSA answer |
| C-02 | **Licence breach** — Open-Meteo non-commercial tier used in production; missing source attribution | Terms-of-use finding | **M** | `NFR-EXT-GOV-002`; confirm prod licence; enforce "Source: X" attribution |
| C-03 | **Combined data residency** — external non-PHI signals joined with provider capacity data inherit the stricter controls | Residency mis-handling | **L** | Signals stay non-PHI; any joined provider data keeps its own controls (ADR-0003/0004 unchanged) |
| C-04 | **Cantonal scope leakage** — signals not scoped to the provider's cantons | Irrelevant/false activation | **L** | Per-canton geo-scoping (`FR-EXT-005`) |

### 6.3 Operational risks

| # | Description | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- | --- |
| O-01 | **Trigger noise** — test/exercise/all-clear or low-certainty signals fire the CSA | Alert fatigue; eroded trust | **M** | `FR-EXT-005` noise governance; certainty/urgency thresholds |
| O-02 | **HITL bypass** — auto-trigger path acts without human approval on outbound coordination | Advisory-only contract breach | **M** | Keep CSA strictly advisory; human runs/accepts; gate outbound coordination (`FR-EXT-003`) |
| O-03 | **Feed outage** — a single-source hazard channel goes dark without fallback | Missed real hazard | **M** | Health-checks; redundant channel where available (MeteoSwiss + Alertswiss for heat) |
| O-04 | **False positives from derive-thresholds** | Unnecessary CSA runs / recommendations | **M** | Tune thresholds; require sustained crossing (N days) before trigger |

---

## 7. Architecture & Governance Alignment Review

Evaluates alignment between the **governance framework** (ADRs, data contracts, advisory/HITL, Swiss-region posture) and the **technical implementation** (connectors, Eventhouse, Activator, ontology bindings, CSA).

### 7.1 Well-aligned areas

| # | Area | Evidence |
| --- | --- | --- |
| WA-01 | **Extends, does not redraw** — the design plugs into the existing `ScenarioTemplate` + *Lage* classifier and event-trigger pattern | Source §1, §4, §5; [ADR-0024](../adr/0024-csa-tier-classifier-rules.md) |
| WA-02 | **Advisory / HITL preserved** — CSA proposes; human accepts; outbound coordination gated | Source §5.4, §5.7; [agents/csa-agent/AGENT.md](../../agents/csa-agent/AGENT.md) |
| WA-03 | **Fabric-native real-time path** — Eventstream/Eventhouse/Activator matches platform RTI direction | Source §5.4 |
| WA-04 | **Non-PHI residency posture** — public signals ease residency; ADR-0003/0004 unchanged for any joined data | Source §5.7; [ADR-0003](../adr/0003-swiss-regional-inference-for-phi.md), [ADR-0004](../adr/0004-block-global-and-data-zone-for-phi.md) |
| WA-05 | **Ontology reuse** — new classes are BFO/OBO-aligned and reuse Location/ScenarioTemplate/LageTier | Source §5.1, §5.2; North Star review §3.3 |

### 7.2 Misalignments / areas requiring validation

| # | Area | Misalignment | Action |
| --- | --- | --- | --- |
| MA-01 | **No governing ADR** for external triggers | Cross-cutting trigger behaviour is not yet recorded | Author external-trigger ADR (`FR-EXT-GOV-001`) |
| MA-02 | **Crosswalk not extended** to `ExternalSignal` domain | Two-layer ontology drift risk | Extend crosswalk + CI check (`NFR-EXT-ONT-001`) |
| MA-03 | **Connector identity / boundary validation** undefined | Untrusted external input reaches the stream | Workload-identity connectors; validate at ingest (Zero Trust) |
| MA-04 | **PRD lacks `FR-EXT-*`** | Requirements not yet traceable | Add `FR-EXT-*` family + traceability rows |
| MA-05 | **Endpoint/licence terms unverified** for most feeds | Build/compliance risk | Build-time verification list; licence review |

---

## 8. Compliance Evaluation — Swiss Public-Sector Context

### 8.1 Data residency & sovereignty

External hazard signals are **public, non-PHI** federal-authority outputs and carry **light residency constraints** — they are usable in both T-SHOW and T-PROD. The moment they are **joined with provider capacity data**, the combined dataset inherits that provider data's classification, residency, and legal-basis controls (nDSG/KVG/EPDG per the master-data model, 2026-06-29 review §1.5). ADR-0003/0004 (Swiss-region PHI inference; global/data-zone blocks) remain unchanged. *(Source §5.7.)*

### 8.2 Provenance, auditability & attribution

Every `ExternalSignal` must carry `sourceAuthority` + `capIdentifier` + `trustTier`, and the CSA must **surface the source in its recommendation**. Each authority's attribution terms (e.g. "Source: MeteoSwiss") must be honoured. This directly supports regulatory acceptance and auditability in a public-sector deployment. *(Source §5.7, §7 Caveats.)*

### 8.3 Regulatory fragmentation (federal vs cantonal)

Signals are **canton-scoped** (Alertswiss/Polyalert levels are canton-scoped; CAP `area`). Per-canton geo-scoping to the provider (`FR-EXT-005`) both reduces noise and respects cantonal operating boundaries. The Swiss *Lage* doctrine (Normallage / Besondere / Ausserordentliche Lage, [ADR-0024](../adr/0024-csa-tier-classifier-rules.md)) is the correct escalation frame, and external-signal severity **pre-seeds** that tier rather than inventing a parallel scale.

### 8.4 Security & Zero Trust posture

External input is **untrusted by definition**. Connectors (Logic Apps / Functions) must use **workload identity**, validate and sanitise every payload at the ingest boundary before it reaches the stream, and never elevate an external signal to an action without HITL. This mirrors the platform's "treat MCP/LLM output as untrusted" discipline. *(Repository SECURITY.md posture; Source §5.4.)*

### 8.5 Licence & terms compliance

Confirm **production licence + attribution** for each source before production; the Open-Meteo MeteoSwiss ICON proxy is a **non-commercial tier** today and needs a prod-licence decision (`NFR-EXT-GOV-002`). Maintain the source's build-time verification list (Appendix) as a living compliance artefact. *(Source §3, §7, Appendix.)*

---

## 9. Recommendations & Next Steps

Prioritised **H / M / L**; quick wins vs strategic changes.

### 9.1 High priority (next sprint)

| # | Recommendation | Type |
| --- | --- | --- |
| H-01 | **Author the external-trigger governance ADR** (trust tiers, HITL, noise filtering, provenance) — new cross-cutting record | Quick win |
| H-02 | **Add the `FR-EXT-*` family to [PRD.md](../PRD.md)** + traceability-matrix rows | Quick win |
| H-03 | **Build the CAP-Suisse connector (Alertswiss/Polyalert)** — the government catch-all trigger, pollable today | Strategic |
| H-04 | **Implement `DC-EXT-SIGNAL-v1`** + mandatory provenance fields | Strategic |
| H-05 | **Codify trigger-noise governance** (`status=Test\|Exercise` + all-clear filtering, certainty/urgency thresholds, per-canton scoping) | Quick win |

### 9.2 Medium priority (following sprint)

| # | Recommendation | Type |
| --- | --- | --- |
| M-01 | **Add SED FDSN (earthquake)** + **MeteoSwiss heat threshold** (STAC/Open-Meteo bridge) | Strategic |
| M-02 | **Author the `ExternalSignal` entity types** + time-series Eventhouse binding; ground the CSA Data Agent | Strategic |
| M-03 | **Wire Fabric Activator → CSA** advisory proposal (HITL) on the Whiteboard "Krisen & Szenarien" card | Strategic |
| M-04 | **Extend the reference↔operational crosswalk + CI check** to the external-signal domain | Strategic |
| M-05 | **Confirm production licences** (Open-Meteo) + build-time endpoint verification list as a governed artefact | Quick win |

### 9.3 Low priority (later / iterative)

| # | Recommendation | Type |
| --- | --- | --- |
| L-01 | **Add secondary feeds iteratively** — BAG, BAFU, ASTRA, SLF, NABEL, NCSC, Swissgrid | Strategic |
| L-02 | **Add redundant channels** per high-value hazard (e.g. MeteoSwiss + Alertswiss for heat) for reliability | Strategic |
| L-03 | **Re-platform onto native CAP Suisse** once the federal warning feed is live (~2027) and retire interim bridges | Strategic |

---

## 10. Traceability Matrix

Each row links a **requirement** (new or existing) to the **control**, the **architecture decision**, the **source**, and the current **status**.

| Requirement | Control | Architecture Decision | Source | Status |
| --- | --- | --- | --- | --- |
| `FR-EXT-001` (Ingest + normalise to `DC-EXT-SIGNAL-v1`) | Data-contract governance; provenance | New external-trigger ADR proposed (H-01) | [Source §5.5, §5.7](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) | **Proposed** |
| `FR-EXT-002` (Signal→scenario→tier via `TriggerRule`) | *Lage* classifier ([ADR-0024](../adr/0024-csa-tier-classifier-rules.md)) | Extends `FR-ONT-005` | [Source §5.2, §5.3](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) | **Proposed** |
| `FR-EXT-003` (Advisory/HITL CSA activation) | Advisory / HITL; region-pinned inference | Extends [AI.md](../AI.md); [csa-agent](../../agents/csa-agent/AGENT.md) | [Source §5.4](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) | **Proposed** |
| `FR-EXT-004` (Provenance & trust tier) | Auditability; `NFR-AI-003` | New external-trigger ADR (H-01) | [Source §5.7](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) | **Proposed** |
| `FR-EXT-005` (Trigger-noise governance) | Operational governance | New external-trigger ADR (H-01) | [Source §5.7](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) | **Proposed** |
| `FR-EXT-006` (CAP-standard consumption) | Interoperability | Design element (CAP Suisse) | [Source §3.1](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) | **Proposed — gated on CAP Suisse maturity** |
| `FR-EXT-ONT-001` (External-signal entity types) | OBO governance; two-layer crosswalk | Extends `FR-ONT-001/003` | [Source §5.1, §5.2](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) | **Proposed** |
| `FR-EXT-ONT-002` (Static + time-series binding) | Fabric IQ GA-gate ([ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md)) | Extends `FR-ONT-002/004` | [Source §5.6](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) | **Proposed — GA-gated** |
| `NFR-EXT-ONT-001` (Crosswalk + CI check) | `FR-GOV-ONT-003` CI conformance | Extends `NFR-ONT-001` | [Source §5.1](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md); North Star review §5.4 | **Proposed** |
| `FR-EXT-GOV-001` (External-trigger ADR) | Governance record; CODEOWNERS | New ADR | [Source §5.7](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) | **Proposed** |
| `NFR-EXT-GOV-001` (Endpoint verification list) | Build-time compliance | Living artefact (Appendix) | [Source §7, Appendix](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) | **Proposed** |
| `NFR-EXT-GOV-002` (Licence + attribution) | Terms-of-use compliance | Legal review | [Source §7 Caveats, Appendix](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) | **Proposed** |
| Existing `NFR-AI-003` (Traceable, grounded AI) | Advisory / HITL; ADR-0003/0004 | [AI.md](../AI.md) | Repository baseline | **In force — strengthened by signal provenance** |
| Existing *Lage* tier classifier | ADR-0024 doctrine rules | [ADR-0024](../adr/0024-csa-tier-classifier-rules.md) | Repository baseline | **In force — pre-seeded by external severity** |

---

## 11. Sprint Implementation Handoff

The external-trigger workstream is a **CSA follow-on** (post-Sprint 16). This section calls out the subset of the AMA outcome a sprint should absorb directly. Sequencing follows the source's roadmap (§7).

### 11.1 High-priority handoffs

| # | Handoff | Track | Reference |
| --- | --- | --- | --- |
| H-01 | Author the **external-trigger governance ADR** (trust tiers, HITL, noise filtering, provenance) | Governance / ADR | This review §9.1 (H-01); Source §5.7 |
| H-02 | Add the **`FR-EXT-*` family** to [PRD.md](../PRD.md) + traceability rows | Product / PRD | This review §5; Source §5.7 |
| H-03 | Build the **CAP-Suisse connector** (Alertswiss/Polyalert) — the government catch-all trigger | Integration / RTI | This review §9.1 (H-03); Source §7 step 1 |
| H-04 | Implement **`DC-EXT-SIGNAL-v1`** with mandatory provenance | Data contracts | This review §9.1 (H-04); Source §5.5 |
| H-05 | Codify **trigger-noise governance** (filter test/exercise/all-clear; certainty/urgency thresholds; per-canton scoping) | Governance | This review §9.1 (H-05); Source §5.7 |

### 11.2 Roadmap (source §7) mapped to sprint tracks

1. **CAP-Suisse connector** (Alertswiss/Polyalert) — government catch-all trigger.
2. **SED FDSN** (earthquake) + **MeteoSwiss** heat threshold (STAC/Open-Meteo bridge).
3. **`DC-EXT-SIGNAL-v1`** + `ExternalSignal` entity + time-series binding + `TriggerRule`.
4. **Fabric Activator → CSA** advisory proposal (HITL) on the Whiteboard.
5. **Secondary feeds** (BAG, BAFU, ASTRA, SLF, NABEL, NCSC, Swissgrid) added iteratively.
6. **Build-time verification** of every endpoint + licence before production.

### 11.3 Acceptance evidence (proposed)

- External-trigger ADR merged; `FR-EXT-*` family + traceability rows merged in [PRD.md](../PRD.md).
- CAP-Suisse connector normalising to `DC-EXT-SIGNAL-v1` with provenance populated.
- One end-to-end path proven on the **heat worked example** (Source §6): MeteoSwiss/Alertswiss → Eventhouse → Activator → CSA advisory proposal, source cited, *Lage* tier pre-seeded, HITL accept.
- Trigger-noise governance demonstrably filters a `status=Test` message.
- Endpoint/licence verification list merged as a living artefact.

### 11.4 Out of scope for the first slice (explicit)

- Secondary feeds beyond the four priority sources — later iterations.
- Native CAP-Suisse re-platform (the ~2027 target) — interim bridge stands until then.
- Any change to the CSA's advisory-only contract — HITL is non-negotiable.
- Joining external signals with PHI — signals remain non-PHI; joined provider data keeps its own controls.

---

## Appendix A — Source Materials

Under [docs/reviews/2026-07-17-ama-trusted-external-signals-review/](./2026-07-17-ama-trusted-external-signals-review/):

| File | Type | Description |
| --- | --- | --- |
| [CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md](./2026-07-17-ama-trusted-external-signals-review/CSA-External-Trusted-Source-Triggers-and-Ontology-Extension.md) | Markdown analysis | Trusted Swiss source catalogue, API/event-feed evaluation, ontology + architecture extension for live external signals as CSA triggers (Draft v1.0) |

### Confirmed source endpoints (as-of mid-July 2026 — treat as a build-time verification list, not a guarantee)

| Source | Endpoint / standard | As-of |
| --- | --- | --- |
| MeteoSwiss OGD (STAC) | `https://data.geo.admin.ch/api/stac/v1/` (e.g. `ch.meteoschweiz.ogd-smn`) | 2026-07 |
| MeteoSwiss ICON (proxy) | `https://open-meteo.com/en/docs/meteoswiss-api` (JSON REST) | 2026-07 |
| Alertswiss / Polyalert (BABS) | Polyalert JSON feed + CAP Suisse (OASIS CAP Swiss profile) | 2026-07 |
| SED earthquakes | `https://eida.ethz.ch/fdsnws/event/1/query` (FDSN; QuakeML/text/JSON) | 2026-07 |
| opendata.swiss | `https://ckan.opendata.swiss/api/3/` (CKAN) | 2026-07 |
| CAP Suisse spec | FOCP/BABS Common Alerting Protocol — Swiss profile | 2023 spec, integration ~2027 |

### Reused evidence base (cited for traceability)

- **OASIS CAP / CAP Suisse** — Common Alerting Protocol (Swiss profile).
- **FDSN** — International seismology web-service standard (SED / ETH Zürich).
- **STAC** — OGC SpatioTemporal Asset Catalog (MeteoSwiss FSDI).
- **BFO / OBO Foundry** — realist upper ontology + principles (reused for the external-signal classes).
- **Swiss *Lage* doctrine** — Normallage / Besondere / Ausserordentliche Lage ([ADR-0024](../adr/0024-csa-tier-classifier-rules.md)).
- **Microsoft Fabric Real-Time Intelligence** — Eventstream / Eventhouse / Data Activator.
- **Trusted Swiss authorities** — MeteoSwiss, Alertswiss/Polyalert (BABS/FOCP), SED (ETH), FOEN/BAFU, FOPH/BAG, NCSC/BACS, ASTRA, SLF/WSL, Swissgrid/OSTRAL, KSD/KATAMED/NAZ, opendata.swiss.

---

> The reviewer prompt used to produce this document is maintained centrally as the **standard reviewer prompt** for all AMA review sessions in [docs/reviews/README.md](./README.md#standard-reviewer-prompt-template).
