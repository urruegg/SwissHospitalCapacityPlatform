# AMA Review — Hospital Command Center (HCC) & North Star Ontology

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.1 |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüeegg |
| **Status** | Draft for Review |
| **Previous Version** | 1.1.0 (added realisation pointers on §9.1 H-01 and §11.1 H-01 to [ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md)) |
| **Session date** | 2026-07-01 |
| **Session type** | Architecture Maturity Assessment (AMA) — outcome consolidation |
| **Subject** | Hospital Command Center (HCC) operating model and North Star ontology for integral capacity management |
| **Reviewer role** | Senior Azure Cloud Architect and Governance Reviewer (CAF, WAF, Zero Trust, Swiss public-sector compliance) |
| **Primary inputs** | Two companion analyses under [docs/reviews/2026-07-01-ama-hcc-northstar-review/](./2026-07-01-ama-hcc-northstar-review/) plus three visualisation exports (HCC OR overview, capacity utilisation pattern, sim-box capacities) |
| **Consumed by** | [docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md](../sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md) — Sprint 9 will implement the North Star MVO scope grounded on this review |

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
11. [Sprint 09 Implementation Handoff](#11-sprint-09-implementation-handoff)
12. [Appendix A — Source Materials](#appendix-a--source-materials)

> **Reviewer prompt template:** the standard prompt used to conduct this review is maintained centrally in [docs/reviews/README.md — Standard Reviewer Prompt](./README.md#standard-reviewer-prompt-template) and reused across all AMA review sessions.

---

## 1. Executive Summary

The AMA session on 2026-07-01 consolidated two companion analyses prepared for the Swiss AI-Powered Patient Flow & Hospital Capacity Platform: an **IKM/HCC vs. current-platform gap analysis** (based on Vetterli Roth & Partners' Integrales Kapazitätsmanagement and the Kispi case study) and a **North Star ontology design** grounded in BFO/OBO best practice and Microsoft Fabric IQ. The session's outcome is a coherent target state and an evidence-based path from the current three-use-case MVP (ED forecast + bed state + discharge) to an **integral, multi-resource, ontology-driven Hospital Command Center**.

The platform is **architecturally ahead** on cloud engineering, Swiss residency, MLOps, grounded GenAI, and auditability — the areas that a boutique consultancy typically does not build itself. It is **materially behind on scope and operating model**: operating-room capacity, staffing/rooms/equipment as managed dimensions, cross-resource ("integral") optimisation, tactical/strategic what-if simulation, and the HCC operating model (roles, cadences, playbooks, Lean/Gemba method) are all absent today. The North Star ontology is the semantic backbone that keeps those new domains consistent across dashboards, models, simulation and the copilot.

### 1.1 Key risks (H = High, M = Medium, L = Low)

| # | Risk | Category | Severity |
| --- | --- | --- | --- |
| R-01 | Fabric IQ Ontology is in preview with no confirmed Switzerland-region GA date, blocking any critical-path commitment to the operational layer | Technical | **H** |
| R-02 | Widening MVP scope from three use cases to full integral capacity management risks destabilising the MVP timeline (Kispi lesson: value comes from process + tool together) | Delivery | **H** |
| R-03 | Absent OR / staffing / rooms / equipment domains create a large integration and data-contract build-out before the integral tier is credible | Technical | **H** |
| R-04 | Operating-model layer (HCC roles, cadences, playbooks, Lean/Gemba discovery) is not in scope of any current sprint — technology alone will not deliver Kispi-class outcomes | Operational | **H** |
| R-05 | Two-layer ontology (reference OWL/RDF ↔ operational Fabric IQ) can drift without a governed crosswalk and CI conformance check | Technical / Governance | **M** |
| R-06 | Scenario Simulation Engine is a genuinely new capability class (skills, validation, data) with no current sprint owner | Technical / Delivery | **M** |
| R-07 | Cantonal fragmentation of the buyer landscape (Swiss federal vs cantonal regulation, provider-specific data ownership) increases onboarding cost per provider without a provider-extension pattern | Compliance / Commercial | **M** |
| R-08 | Ontology skills are scarce; without a semantic owner and OBO-style change workflow the model will rot | Operational | **M** |

### 1.2 Overall maturity assessment

| Dimension | Maturity | Trend |
| --- | --- | --- |
| Cloud architecture (CAF/WAF alignment, IaC, DEV/SIT/PROD) | **Mature** | Stable |
| Swiss residency & compliance engineering (DSG, KVG, EPDG, region-pinned inference) | **Mature** | Stable |
| Responsible AI (advisory/HITL, grounding, audit trace) | **Mature** | Stable |
| Data platform (Fabric OneLake, curated domains, contracts) | **Emerging** | Improving (Sprint 08/09) |
| Semantic layer & ontology | **Nascent** | To be elevated (this review) |
| Resource scope (beds only vs. integral beds + OR + staff + rooms + equipment) | **Partial** | Widening required |
| HCC operating model (roles, cadences, playbooks, Lean/Gemba) | **Absent** | New workstream |
| Scenario / what-if simulation (tactical/strategic) | **Absent** | New workstream |
| Business-outcome KPI framework (OR utilisation, discharge-by-noon, etc.) | **Absent** | New workstream |

### 1.3 Top 5 recommendations

1. **Elevate the Fabric IQ Ontology decision from "deferred" to "target semantic backbone — GA-gated"** — supersede or amend the current ADR-0002 stance, keep the reference layer (BFO/OBO in OWL/RDF) portable so the operational realisation is de-risked against Fabric IQ preview status and Switzerland-region GA timing.
2. **Ship a Minimum Viable Ontology (MVO) in Sprint 09** — Facility → Ward → Room → Bed → Encounter → Patient → Care team → Equipment **plus OR slot** — auto-generated from the Sprint-09 Power BI semantic model (per the Fabric IQ lab pattern), grounded on the reference layer for traceability.
3. **Add operating-room capacity as the first integral domain** — new data contracts (`DC-OR-SCHEDULE-v1`, `DC-OR-CASE-v1`), OR-steering command view, OR Steering Agent (ORSA, advisory/HITL). This is the highest-value, most visible gap-close and directly mirrors the Kispi flagship outcome.
4. **Stand up the HCC operating-model layer alongside the technology** — decision cadences (daily/tactical/strategic), capacity RACI, bottleneck playbooks, and a Lean/Gemba discovery method delivered via a partner-led services wrap. Kispi's results came from process + tool together; the platform must not repeat the classic "great dashboard, no adoption" failure mode.
5. **Introduce a business-outcome KPI framework** (OR utilisation, short-notice cancellation rate, first-case on-time start, discharge-before-noon, staffing demand-to-roster match) with baseline capture in a T0-style potential-analysis step — this is what makes the business case measurable and underpins the managed-service (T3+) SKU.

---

## 2. Context Overview

### 2.1 Purpose of this document

Produce a structured, evidence-based **solution review** of the AMA session outcomes for the HCC + North Star Ontology topic. The document identifies gaps, risks and inconsistencies; assesses alignment with Azure best practices and governance models; and hands off a high-granularity brief to Sprint 09 so implementation is grounded, traceable and reviewable.

### 2.2 Inputs reviewed

| # | Input | Path / Reference | Role |
| --- | --- | --- | --- |
| 1 | *IKM/HCC vs Swiss Capacity Platform — Analysis* (Draft v1.0) | [IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md) | Primary — gap map, incorporation blueprint, tiered SKUs |
| 2 | *A North Star Ontology Model for the Hospital Command Center (HCC)* (Draft v1.0) | [HCC-North-Star-Ontology-Model-Analysis.md](./2026-07-01-ama-hcc-northstar-review/HCC-North-Star-Ontology-Model-Analysis.md) | Primary — reference & operational ontology design |
| 3 | HCC operating-room overview (image) | [hcc-operation-room-overview.png](./2026-07-01-ama-hcc-northstar-review/hcc-operation-room-overview.png) | Visual anchor for OR steering scope |
| 4 | HCC capacities utilisation-pattern overview (image) | [hcc-apacities-utilization-pattern-overview.png](./2026-07-01-ama-hcc-northstar-review/hcc-apacities-utilization-pattern-overview.png) | Visual anchor for integral resource utilisation |
| 5 | HCC sim-box capacities overview (image) | [hcc-simboxcapacities-overview.png](./2026-07-01-ama-hcc-northstar-review/hcc-simboxcapacities-overview.png) | Visual anchor for scenario-simulation surface |
| 6 | Prior AMA — capacity metadata framework | [2026-06-29-ama-capacity-metadata-review.md](./2026-06-29-ama-capacity-metadata-review.md) | Baseline (4-layer master-data model) |
| 7 | Prior AMA outputs (CSA/CTO/CISO/Design challengers, SD reviews) | `docs/reviews/2026-06-08 … 2026-06-10*.md` | Historical baseline |
| 8 | Repository baseline | [PRD.md](../PRD.md), [ARCHITECTURE.md](../ARCHITECTURE.md), [DATA.md](../DATA.md), [AI.md](../AI.md), [INFRASTRUCTURE.md](../INFRASTRUCTURE.md), [SECURITY.md](../SECURITY.md), [COMPLIANCE.md](../COMPLIANCE.md), [OPERATIONS.md](../OPERATIONS.md), [SD.md](../SD.md) | Current design of record |
| 9 | ADRs | [adr/0001-ga-only-mvp-critical-path.md](../adr/0001-ga-only-mvp-critical-path.md), [adr/0002-defer-fabric-iq-ontology-from-mvp.md](../adr/0002-defer-fabric-iq-ontology-from-mvp.md), [adr/0003-swiss-regional-inference-for-phi.md](../adr/0003-swiss-regional-inference-for-phi.md), [adr/0004-block-global-and-data-zone-for-phi.md](../adr/0004-block-global-and-data-zone-for-phi.md) | Current architectural constraints |
| 10 | Sprint 08/09 plan | [sprint-09-master-data-simulation-and-capacity-dashboard.md](../sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md) | Downstream implementation lane |

### 2.3 Baseline solution

The baseline is the **Swiss AI-Powered Patient Flow & Hospital Capacity Platform** as documented in this repository at commit-of-record for this branch: a provider-internal, GA-only MVP built on Microsoft Fabric + Azure ML + Azure OpenAI + Azure Health Data Services, with Swiss-region PHI inference (per ADR-0003/0004), IaC-first Bicep landing zone, three AI use cases (ED forecast, discharge coordination, GenAI bed-management copilot), and a React command-center + Power BI channel.

### 2.4 Scope of this review

The four dimensions defined in the reviewer work instructions (Appendix B):

1. **Product Requirements (PRD)** — completeness, traceability, alignment with business and regulatory needs.
2. **Solution Design (SD)** — logical architecture, service selection, design patterns, scalability, resilience, maintainability.
3. **Architecture** — Azure landing zones, subscription model, tenant strategy, environment separation, identity/access.
4. **Compliance & Security** — Swiss federal vs cantonal requirements, data residency & sovereignty, security controls, Zero Trust alignment, policy-as-code enforcement.

### 2.5 Assumptions

| # | Assumption | Basis |
| --- | --- | --- |
| A-01 | Fabric IQ Ontology remains in preview and its Switzerland-region GA date is not committed publicly by Microsoft | Companion "North Star Ontology" §2 (confidence note); ADR-0002 |
| A-02 | The GA-only MVP critical-path constraint (ADR-0001) still applies to Sprint 09 | ADR-0001 |
| A-03 | PHI inference remains restricted to Switzerland North/West with Standard/Regional deployments only (ADR-0003/0004 not superseded) | ADR-0003, ADR-0004 |
| A-04 | The Sprint 09 master-data foundation and Power BI semantic model are the intended base for Fabric IQ ontology auto-generation | Sprint-09 plan; Fabric IQ lab pattern |
| A-05 | No production PHI is present in the reference ontology — the ontology schema/metadata is not itself PHI | Companion "North Star Ontology" §7.2 |
| A-06 | The two companion papers are internal drafts (v1.0) and their inferences (e.g. discrete-event simulation, VR&P partner stack) are flagged as "to be validated" and treated as such here | Companion papers §2 (evidence base and confidence note) |
| A-07 | VR&P's software-partner stack, internal data model, and algorithms remain undisclosed at time of writing | Companion "IKM/HCC vs. Platform" §2 |

---

## 3. Key Findings from Review Session

Findings are grouped by the dimensions defined in the reviewer work instructions. Every finding is traced to its source paragraph or artefact.

### 3.1 Product & Business Findings

**F-P-01 — Positioning shift from point solution to system-of-record.** The current platform is positioned as a "provider-internal AI operational copilot for ED, beds and discharge"; the AMA outcome recommends re-positioning as *"a Swiss-resident Integral Capacity Management platform and Hospital Command Center — AI-driven planning and real-time steering of beds, OR, staff, rooms and equipment, from the 72-hour operational horizon to strategic what-if planning, delivered with a proven command-center operating model."* This expands the addressable value from ED/discharge efficiency to OR throughput and moves the buyer from operations teams to CFO/COO/medical-director level. — *Source: IKM/HCC vs Platform §6.1.*

**F-P-02 — Tiered adoption journey ("Reiseroute").** The session endorses a five-tier commercial model that mirrors VR&P's maturity ladder: T0 Potential Analysis · T1 Decision Support · T2 Operational HCC (current MVP + OR module) · T3 Integral HCC (staffing/rooms/equipment + simulation) · T3+ Managed Steering. — *Source: IKM/HCC vs Platform §6.3.*

**F-P-03 — Target scenarios unlocked.** Three concrete buyer scenarios are named: (a) **new-building/campus commissioning** (Kispi pattern), (b) **brownfield efficiency turnaround** (e.g. Zollikerberg "Agenda 2027"), (c) **elective-surgery-led providers** (Hirslanden, OR-heavy). Each maps to a different tier entry point. — *Source: IKM/HCC vs Platform §6.2.*

**F-P-04 — Partnering with VR&P is a viable co-sell model.** VR&P's Lean/Design-Thinking/Gemba capability and clinical-operations credibility complement platform engineering. Co-delivery (VR&P owns process transformation + operating model; platform owns compliant Azure + AI) accelerates market entry — but channel-conflict management is required. — *Source: IKM/HCC vs Platform §6.5.*

**F-P-05 — Business risks are non-trivial.** Scope creep, change-management dependency, buyer complexity (multi-stakeholder), and channel conflict are enumerated. The Kispi lesson is explicit: IKM value depends on process adoption, not just software; under-investing in the operating model is the classic failure mode. — *Source: IKM/HCC vs Platform §6.6.*

### 3.2 Architecture & Design Findings

**F-A-01 — Extend the reference architecture, do not redraw it.** The AMA outcome adds three capability blocks to the existing layered architecture *without changing its shape*: new source/event feeds (OR/anaesthesia/rostering/room booking/biomedical), new curated Fabric domains (OR/Staffing/Room/Equipment/Simulation + a Capacity Ontology semantic layer), and new AI/agent surfaces (ORSA/CSA/SBA). — *Source: IKM/HCC vs Platform §7.1.*

**F-A-02 — "Integral capacity unit" is the key modelling move.** The North Star introduces a single generalisation — **Capacity unit** — a material entity (or time-bounded slot) that bears a **capacity function** and has a **capacity state** (available/occupied/blocked/planned). Beds, OR slots, rooms, staff shifts and devices are all subtypes. One set of relations, states, KPIs, forecasts and simulation logic then applies across all five resource dimensions. — *Source: North Star Ontology §4.5.*

**F-A-03 — Two-layer ontology split is intentional and de-risks Fabric IQ preview status.** The design deliberately separates the **reference layer** (BFO/OBO in OWL/RDF, rigorous axioms, portable) from the **operational layer** (Fabric IQ property graph, generated from the Power BI semantic model, live bindings). A governed crosswalk between them is a first-class deliverable, with a CI conformance check. — *Source: North Star Ontology §5.4.*

**F-A-04 — Reuse mature published ontologies, do not invent.** The reference layer imports and specialises: **BFO (ISO/IEC 21838-2:2021)** as upper ontology; **OMRSE** for facilities and function typology; **OGMS** for clinical-encounter terms; **OOSTT** for organisational/capacity structure; **Goyer et al. ICBO 2022** for healthcare-organisation and role classes; and a **process-ontology overlay from Jerjas & Hall (KTH 2017)** for simulation-readiness. — *Source: North Star Ontology §2, §4.1–4.3.*

**F-A-05 — Fabric IQ auto-generation matches the Sprint 09 semantic model almost 1:1.** The Fabric IQ lab's sample domain (Hospitals→Departments→Rooms→Patients→VitalSignEquipment→VitalSignReadings) is *almost a literal template* for the MVO. Path: curate lakehouse (static) + eventhouse (time-series) → build Power BI semantic model → "Generate Ontology" → enrich with keys, relationship bindings, time-series bindings. — *Source: North Star Ontology §5.1.*

**F-A-06 — New agents extend the existing OOA/DCA/BMCA family.** Three new agents are proposed with the same advisory/HITL, retrieval-grounded, audit-traceable, region-pinned inference discipline as today's agents: **ORSA** (OR Steering Agent), **CSA** (Capacity Simulation Agent), **SBA** (Staffing Balance Agent). — *Source: IKM/HCC vs Platform §7.4.*

**F-A-07 — Scenario Simulation Engine is a distinct workstream.** Realisation shape (Azure ML + a SimPy-class discrete-event library running as Azure Container Apps jobs, reading Fabric curated capacity data, writing `DC-SIM-RESULT-v1`) is an **inference to validate** — not established fact. Treat as its own workstream with its own acceptance criteria. — *Source: IKM/HCC vs Platform §7.3 (item 3), §9.*

### 3.3 Data & Ontology Findings

**F-D-01 — Nine new data contracts extend the existing `DC-*` family.** Beyond the Sprint-09 `DC-MASTER-01…09` reference contracts, the AMA outcome adds: `DC-OR-SCHEDULE-v1`, `DC-OR-CASE-v1`, `DC-STAFF-ROSTER-v1`, `DC-STAFF-DEMAND-v1`, `DC-ROOM-STATE-v1`, `DC-DEVICE-STATE-v1`, `DC-SIM-SCENARIO-v1`, `DC-SIM-RESULT-v1`, plus a clinical reference `DC-REF-DISEASE-v1`. — *Sources: IKM/HCC vs Platform §7.2; 2026-06-29 metadata review §5.2.*

**F-D-02 — Reference-layer classes crosswalk to Fabric IQ operational constructs.** BFO/OBO classes map to Fabric IQ entity types; object properties to relationship types; qualities/data properties to entity properties (static bindings); live measurements to time-series bindings (eventhouse); information content entities (forecast, score, plan) to entity types bound to AI-output tables. Axioms/rules that Fabric IQ cannot enforce natively are enforced in curation + validated in data contracts. — *Source: North Star Ontology §5.2.*

**F-D-03 — Clinical-standards crosswalk keeps the ontology interoperable.** FHIR resource mapping: Facility/Ward/Room/Bed ↔ `Location`, `HealthcareService`; Encounter/admission/discharge ↔ `Encounter`, `EncounterStatusHistory`; Health worker/role ↔ `Practitioner`, `PractitionerRole`; Procedure ↔ `Procedure`, `ServiceRequest`, `Appointment`/`Slot` (OR); Device/equipment ↔ `Device`. Terminology binding: SNOMED CT for sites, encounters, roles, procedures, devices. — *Source: North Star Ontology §7.3.*

**F-D-04 — Ontology sits above the existing data-contract family.** Rather than replacing contracts, the ontology gives them **shared meaning**. Hospital organisation → `DC-SUPPLY-ORGANIZATION-v1`; Facility/Ward/Room/Bed → `DC-SUPPLY-LOCATION-v1`; Encounter/Patient role → `DC-DEMAND-ENCOUNTER-v1`; Match/recommendation → `DC-MATCH-RECOMMENDATION-v1`; OR slot/Staffing/Room/Equipment → the new `DC-OR-*`, `DC-STAFF-*`, `DC-ROOM-*`, `DC-DEVICE-*`; Forecast/Discharge score/Scenario → `DC-AI-FORECAST-v1` + `DC-SIM-*`. — *Source: North Star Ontology §5.3.*

**F-D-05 — Reference ontology is *not* PHI; live bindings still read Swiss-resident data.** The ontology's schema/metadata is metadata about concepts, not personal data. PHI remains in Swiss-resident stores under existing controls (ADR-0003/0004 unchanged). This *eases* residency handling — much of the new OR/staffing/room/equipment data is operational-confidential, not deep PHI. — *Source: North Star Ontology §7.2.*

**F-D-06 — Minimum Viable Ontology (MVO) scope is disciplined.** MVO scope = Facility → Ward → Room → Bed → Encounter → Patient → Care team → Equipment **+ OR slot**, generated from the Sprint-09 semantic model with a first time-series binding on bed state. The reference-layer skeleton is authored in parallel. Later phases add staffing/rooms/equipment capacity units, capacity-unit abstraction, Data Agents, provider extensions, and finally the process-ontology overlay + full FHIR/SNOMED crosswalk. — *Source: North Star Ontology §7.5.*

### 3.4 AI & Agent Findings

**F-AI-01 — Copilot grounds on the ontology for concept-level traceability.** The bed-management copilot and proposed OR/simulation agents ground on ontology entities/relationships, so answers are consistent and traceable to defined concepts — directly supporting `NFR-AI-002/003/004`. Fabric Data Agents can reason over the ontology for anomaly detection and semantic query assistance. — *Source: North Star Ontology §5.5.*

**F-AI-02 — Advisory/HITL and Swiss-region inference are preserved.** All new agents (ORSA, CSA, SBA) inherit today's controls: advisory only, human-in-the-loop, retrieval-grounded with citations, model/version/timestamp traceability, Swiss-region prompt governance, no relaxation of ADR-0003/0004. — *Source: IKM/HCC vs Platform §7.4, §7.8.*

**F-AI-03 — Explainability improves through concept-level lineage.** With the ontology in place, copilot answers cite defined concepts rather than opaque table/column references — strengthening regulatory acceptance for a Swiss public-sector deployment. — *Source: North Star Ontology §3.2, §6.1.*

### 3.5 Operating-Model & Process Findings

**F-O-01 — HCC is an operating capability, not a screen.** VR&P defines the HCC as the "heart" of an IKM initiative that combines real-time steering with ongoing coaching on everyday, tactical and strategic questions. Kispi's reported outcomes (OR-steering dashboard to avoid short-notice cancellations; reduced OR idle time; more efficient anaesthesia consultations; 24/7 discharge process; unified capacity management across beds and OR) were achieved by **process + tool together**, not tool alone. — *Sources: IKM/HCC vs Platform §3.2, §3.4.*

**F-O-02 — Lean / Design-Thinking / Gemba is the pre-platform layer.** Adding a "**pre-platform discovery and standardisation method**" — Gemba walks, data-based analysis, process harmonisation to a standard base model, clear responsibility rules and interface harmonisation — is what makes multi-provider reusability real (`NFR-MAINT-004`). Best delivered via a partner-led services wrap. — *Source: IKM/HCC vs Platform §7.7.*

**F-O-03 — Decision cadences are governed Power BI/semantic surfaces.** Daily operational huddle · weekly tactical · monthly/quarterly strategic. Each is a distinct, governed surface with a defined horizon (real-time → 72h → simulation), capacity RACI, and standardised bottleneck playbooks ("acute bed shortage", "OR over-run", "staffing gap"). — *Source: IKM/HCC vs Platform §7.6.*

### 3.6 KPI & Value-Case Findings

**F-K-01 — Operational-outcome KPIs are distinct from technical SLOs.** A new KPI layer is required alongside today's technical SLOs, structured by resource domain and outcome. — *Source: IKM/HCC vs Platform §6.4.*

| KPI family | Metrics |
| --- | --- |
| **OR** | Utilisation %, short-notice cancellation rate, first-case on-time start %, turnover time, idle-slot minutes |
| **Beds / flow** | Occupancy %, ED boarding time, admission-to-bed time, elective cancellations due to no bed |
| **Discharge** | Discharge-before-noon %, discharge-delay hours, blocker resolution time |
| **Staffing** | Demand-to-roster match %, agency/overtime hours avoided |
| **System** | LOS vs. benchmark, patient and staff satisfaction |

**F-K-02 — Baseline capture is a T0 activity.** Each KPI needs baseline measurement in a potential-analysis (T0) step so value is measurable — this is the foundation of both the business case and managed-service (T3+) renewal. — *Source: IKM/HCC vs Platform §6.4.*

### 3.7 Governance & Ownership Findings

**F-G-01 — Ontology must be a versioned, Git-tracked platform asset.** Manage the ontology with **DEV/SIT/PROD promotion gates**, mirroring existing IaC-first and data-contract discipline; record lineage and classification in Purview. — *Source: North Star Ontology §7.2.*

**F-G-02 — OBO-inspired governance model.** Principles: **realism, univocity** (one term / one meaning), **orthogonality / reuse** (import; don't duplicate external ontologies), **semantic change workflow** (proposals → domain-owner review → versioned release → downstream impact check, mirroring the data-contract breaking-change control), and a nominated **ontology/semantic owner** in the data-governance RACI. — *Source: North Star Ontology §7.6.*

**F-G-03 — Reference-to-operational crosswalk is a governed artefact.** The crosswalk between the OWL/RDF reference layer and the Fabric IQ operational layer is itself a versioned artefact with a **CI conformance check**. — *Source: North Star Ontology §5.4, §7.6.*

### 3.8 Explicitly Open Questions Raised

Captured verbatim from the two source papers so Sprint 09 (and downstream sprints) can treat them as blockers/validation items rather than assumptions.

1. Confirm Fabric IQ Ontology GA date and Switzerland-region availability before any critical-path commitment. *(North Star §8)*
2. How much OWL-DL reasoning do we actually need operationally, versus rules enforced in curation/contracts? *(North Star §8)*
3. Which reference ontologies to import wholesale vs. cherry-pick — OOSTT organisational structure is the strongest candidate for full reuse. *(North Star §8)*
4. Author the reference layer in-house or with an OBO-experienced partner? *(North Star §8)*
5. Which provider is the best OR-module pilot — Hirslanden (elective/OR-heavy) is the strongest fit per our own provider analysis. *(IKM/HCC §9)*
6. Simulation fidelity required (strategic annual planning vs. weekly tactical) — drives the modelling approach. *(IKM/HCC §9)*
7. VR&P's actual software-partner stack and data model — where would we integrate vs. replace vs. co-sell? *(IKM/HCC §9)*
8. KPI baseline availability at each target provider (needed for the value case). *(IKM/HCC §9)*

All eight are marked **"Requires validation"** in this review and must not be treated as decided.

---

## 4. Deviation Analysis — Best Practice vs Current State

Best-practice references: **Microsoft Cloud Adoption Framework (CAF)**, **Azure Well-Architected Framework (WAF)**, **Zero Trust architecture**, **BFO/OBO Foundry ontology principles**, **FHIR / SNOMED CT clinical standards**, **Kispi/UCSF PCMC real-world HCC operating practice**.

| # | Area | Best Practice | Observed Current State | Deviation / Gap | Impact |
| --- | --- | --- | --- | --- | --- |
| D-01 | **Resource scope** | Integral steering of **all** hospital resources — beds, OR, staff, rooms, equipment — with cross-resource balance | Single-resource lens: beds + patient flow; staffing as *interpretation signal* only; OR/rooms/equipment absent | Missing four of five managed resource dimensions | **H** |
| D-02 | **Time horizon** | Operational (real-time / 72h) **+** tactical (weekly) **+** strategic (annual / new-building) | Operational only (72h ED forecast; real-time bed state) | Tactical and strategic planning capability absent | **H** |
| D-03 | **Semantic layer** | Shared, machine-reasonable ontology (realist BFO/OBO, reuse OMRSE/OGMS/OOSTT/Goyer/KTH); grounds AI, dashboards, simulation on one meaning | No ontology; data contracts fix payload schemas per producer→consumer boundary; semantic model exists only in Power BI | Concept-level semantics are implicit and per-surface; ADR-0002 defers Fabric IQ Ontology | **H** |
| D-04 | **Ontology governance (OBO principles)** | Realism, univocity, orthogonality/reuse, versioned change workflow, named semantic owner | None (no ontology owner, no crosswalk artefact, no CI conformance check) | Nascent — build alongside the ontology itself | **H** |
| D-05 | **Operating model (HCC)** | Roles, decision cadences (daily/tactical/strategic), bottleneck playbooks, coaching/managed service (Kispi/UCSF pattern) | React command-center UI + Power BI views only; no cadence library, no RACI, no playbooks | Operating-model layer missing | **H** |
| D-06 | **Process method** | Lean / Design-Thinking / Gemba discovery and standardisation as a pre-platform step | Not in scope | Method absent | **H** |
| D-07 | **Simulation / what-if** | Discrete-event simulation on a shared object model (KTH pattern) for tactical/strategic planning | Predictive 72h forecast only | Capability class absent | **H** |
| D-08 | **Business-outcome KPIs** | OR utilisation, cancellation rate, discharge-before-noon, staffing match — baselined per provider | Technical SLOs dominate; no operational-outcome KPI catalogue | New KPI layer required | **M** |
| D-09 | **Clinical-standards binding** | FHIR + SNOMED CT crosswalk for interoperability (Azure Health Data Services in-stack) | Partial (FHIR normalisation exists; no ontology-level crosswalk to SNOMED CT / FHIR resources per concept) | Crosswalk to be authored | **M** |
| D-10 | **Provider extensibility** | Reference model + provider extensions (specialisations), not per-site re-modelling | Onboarding is per-provider; no ontology-level specialisation pattern | Multi-provider reuse pattern still ad hoc | **M** |
| D-11 | **CAF landing-zone alignment** | Landing zone with management-group hierarchy, subscription model, policy set, network, identity, monitoring | Landing zone exists (Bicep-first) but the *new* domains (OR, staffing, rooms, equipment, simulation) have no explicit landing-zone extension | Landing-zone extension needed for new domains and simulation compute | **M** |
| D-12 | **WAF — Reliability** | Multi-region failover posture; recovery classes documented per capability | Documented for current MVP; **not** re-assessed for the new domains (OR sources, rostering, biomedical asset feeds) | Reliability re-assessment required as scope widens | **M** |
| D-13 | **WAF — Performance** | Real-time performance of time-series bindings validated at production event volumes | Not yet validated for Fabric IQ time-series bindings | Performance spike required | **M** |
| D-14 | **Zero Trust — data plane** | Least-privilege access to *every* new domain; conditional access; workload identity for MCP callers | Applied to current MVP; **not** extended to new domain identities/scopes | Extension of Zero Trust posture to new domains | **M** |
| D-15 | **Fabric IQ maturity** | GA services on the MVP critical path (ADR-0001) | Fabric IQ Ontology in preview; no Switzerland-region GA date | Preview status must be gated | **H** |
| D-16 | **Ontology skills** | Named semantic owner; OBO-experienced authoring capacity | Not present today | Skill gap — reuse published ontologies + partner | **M** |
| D-17 | **Two-layer synchronisation** | Explicit reference↔operational crosswalk; CI check prevents drift | Not defined | Design and enforce in Sprint 09/10 | **M** |
| D-18 | **New-building commissioning offer** | Package process standardisation + simulation for the new footprint + HCC stand-up (Kispi pattern) | Not packaged | Product-marketing gap; drives T3/T3+ SKUs | **M** |

---

## 5. New & Emerging Requirements

Every requirement below is proposed **new** or **implied** by the AMA outcome. Existing FR/NFR IDs (`FR-DATA-*`, `FR-FC-*`, `FR-CX-*`, `NFR-AI-*`, `NFR-MAINT-*`, etc.) are referenced where anchoring applies. Each row states the source, the validation still required, and the sprint slot (where already known).

### 5.1 Ontology requirements (new family `FR-ONT-*` / `NFR-ONT-*`)

| ID | Requirement | Anchored to | Source | Validation Needed |
| --- | --- | --- | --- | --- |
| `FR-ONT-001` | Maintain a **reference ontology** grounded in BFO, reusing OMRSE / OGMS / OOSTT / Goyer et al. healthcare-system classes | extends FR-DATA | North Star §7.4 | Confirm OBO import list (esp. OOSTT wholesale vs. selective); nominate semantic owner |
| `FR-ONT-002` | Realise the **operational ontology in Fabric IQ**, generated from the governed semantic model with static + time-series bindings | extends FR-DATA / FR-FC | North Star §7.4 | Requires Fabric IQ Switzerland-region GA (blocker) |
| `FR-ONT-003` | Model **all five resource dimensions as capacity-unit subtypes** with shared states and relations (integral abstraction) | integral scope | North Star §4.5, §7.4 | Validate subtype set (bed, OR slot, room, staff shift, device) against provider data |
| `FR-ONT-004` | **Ground copilot and Data Agents** on the ontology with concept-level traceability | extends FR-CX / `NFR-AI-003/004` | North Star §5.5, §7.4 | Validate grounding accuracy against fixture set |
| `FR-ONT-005` | Provide a **process-ontology overlay** to support what-if simulation | supports `FR-SIM-*` | North Star §7.4 | Simulation fidelity (weekly vs strategic) still open (Open Q #6) |
| `FR-ONT-006` | Crosswalk ontology to **FHIR / SNOMED CT** for clinical interoperability | extends FR-DATA-002 | North Star §7.3, §7.4 | Terminology-server dependency (Azure Health Data Services scope) |
| `FR-ONT-007` | Support **provider-specific ontology extensions** without re-architecture | `NFR-MAINT-004` | North Star §7.4 | Extension pattern to be defined; Hirslanden OR-heavy is candidate pilot |
| `NFR-ONT-001` | **Version, govern and promote** the ontology as a first-class asset with an explicit reference↔operational crosswalk (CI-checked) | `NFR-MAINT-002` | North Star §5.4, §7.6 | Semantic owner named; crosswalk artefact designed |

### 5.2 OR / surgical capacity requirements (new family `FR-OR-*`)

| ID | Requirement | Anchored to | Source | Validation Needed |
| --- | --- | --- | --- | --- |
| `FR-OR-001` | Ingest **OR slate** (theatre, slot, case, planned duration, status) with a versioned data contract `DC-OR-SCHEDULE-v1` | extends FR-DATA | IKM/HCC §7.2, §7.3 | Source-system access per provider (Hirslanden pilot candidate) |
| `FR-OR-002` | Ingest **OR case events** (start, over-run, cancellation, turnover) via `DC-OR-CASE-v1` | extends FR-DATA | IKM/HCC §7.2 | Latency and event-order guarantees per source system |
| `FR-OR-003` | Predict **case duration and cancellation risk**; surface idle slots and over-runs; propose early day-plan adjustments (advisory / HITL) | extends FR-FC / FR-CX | IKM/HCC §7.3 | Model class selection, evaluation harness |
| `FR-OR-004` | Deliver an **OR-steering command view** (dashboard) that mirrors the Kispi flagship | extends FR-CX | IKM/HCC §7.1, §8 | UX design; visual anchor: [hcc-operation-room-overview.png](./2026-07-01-ama-hcc-northstar-review/hcc-operation-room-overview.png) |
| `FR-OR-005` | Provide an **OR Steering Agent (ORSA)** — advisory / HITL, retrieval-grounded, region-pinned inference | extends FR-CX / `NFR-AI-*` | IKM/HCC §7.4 | Agent contract + golden tasks |
| `FR-OR-006` | Represent **anaesthesia-consultation status** as a first-class state feeding OR readiness | new | IKM/HCC §3.4 | Provider workflow validation |

### 5.3 Staffing requirements (new family `FR-STAFF-*`)

| ID | Requirement | Source | Validation Needed |
| --- | --- | --- | --- |
| `FR-STAFF-001` | Ingest **staff rosters** (role, shift, skill tags, availability) via `DC-STAFF-ROSTER-v1` | IKM/HCC §7.2 | Rostering-system integration |
| `FR-STAFF-002` | Represent **staffing demand** (predicted demand from forecast + OR slate + census) via `DC-STAFF-DEMAND-v1` | IKM/HCC §7.2, §7.3 | Feature design; demand aggregation window |
| `FR-STAFF-003` | Compute and surface **staffing demand-to-roster match** with under/over-staffing windows | IKM/HCC §7.3 | Model / rule engine choice |
| `FR-STAFF-004` | Provide a **Staffing Balance Agent (SBA)** — advisory / HITL | IKM/HCC §7.4 | Agent contract + golden tasks |

### 5.4 Room & equipment requirements (new family `FR-CAP-*`)

| ID | Requirement | Source | Validation Needed |
| --- | --- | --- | --- |
| `FR-CAP-001` | Ingest **room availability** and biomedical **device availability / PM windows** via `DC-ROOM-STATE-v1` and `DC-DEVICE-STATE-v1` | IKM/HCC §7.2 | Asset-management integration |
| `FR-CAP-002` | Represent rooms and devices as **capacity-unit subtypes** with shared state semantics | North Star §4.5 | Ontology alignment |

### 5.5 Simulation requirements (new family `FR-SIM-*`)

| ID | Requirement | Source | Validation Needed |
| --- | --- | --- | --- |
| `FR-SIM-001` | Provide a **Scenario Simulation Engine** that models future states (patient-mix growth, schedule changes, new-building footprints) and surfaces resulting bottlenecks *and* over-capacity | IKM/HCC §7.3 (item 3) | Realisation shape (SimPy + Azure Container Apps) is an **inference to validate** |
| `FR-SIM-002` | Persist scenario definitions and results via `DC-SIM-SCENARIO-v1` and `DC-SIM-RESULT-v1` | IKM/HCC §7.2 | Contract schema |
| `FR-SIM-003` | Provide a **Capacity Simulation Agent (CSA)** — natural-language what-if querying grounded in `DC-SIM-*` outputs | IKM/HCC §7.4 | Agent contract + golden tasks |
| `FR-SIM-004` | Support **cross-resource ("integral") optimisation** so a recommended OR plan is checked against downstream bed and staff capacity | IKM/HCC §7.3 (item 4) | Optimisation objective / constraint design |

### 5.6 HCC operating-model requirements (new family `FR-HCC-*`)

| ID | Requirement | Source | Validation Needed |
| --- | --- | --- | --- |
| `FR-HCC-001` | Publish **decision-cadence surfaces**: daily operational huddle, weekly tactical, monthly/quarterly strategic — each with a defined data horizon | IKM/HCC §7.6 | Surface design per cadence |
| `FR-HCC-002` | Define a **capacity RACI** extending the existing operations RACI (OR steering, staffing balance, discharge escalation) | IKM/HCC §7.6 | Owner alignment per provider |
| `FR-HCC-003` | Publish **bottleneck playbooks** (acute bed shortage, OR over-run, staffing gap) with standardised responses | IKM/HCC §7.6 | Content authoring with clinical operations |
| `FR-HCC-004` | Package a **Lean / Design-Thinking / Gemba discovery method** as a pre-platform services-layer deliverable | IKM/HCC §7.7 | Partner vs. build decision (Open Q #7) |

### 5.7 Operational-outcome KPI requirements (new family `NFR-KPI-*`)

| ID | Requirement | Source | Validation Needed |
| --- | --- | --- | --- |
| `NFR-KPI-001` | Capture **OR outcome KPIs** (utilisation, cancellation rate, on-time start, turnover, idle-slot minutes) with per-provider baseline | IKM/HCC §6.4 | Baseline availability per provider (Open Q #8) |
| `NFR-KPI-002` | Capture **bed/flow KPIs** (occupancy, ED boarding, admission-to-bed, cancellations due to no bed) | IKM/HCC §6.4 | Baseline availability per provider |
| `NFR-KPI-003` | Capture **discharge KPIs** (discharge-before-noon %, delay hours, blocker resolution) | IKM/HCC §6.4 | Baseline availability per provider |
| `NFR-KPI-004` | Capture **staffing KPIs** (demand-to-roster match %, agency/overtime hours avoided) | IKM/HCC §6.4 | Baseline availability per provider |
| `NFR-KPI-005` | Capture **system KPIs** (LOS vs. benchmark, patient and staff satisfaction) | IKM/HCC §6.4 | Instrumentation source |

### 5.8 Governance & product-packaging requirements

| ID | Requirement | Source | Validation Needed |
| --- | --- | --- | --- |
| `FR-GOV-ONT-001` | Nominate a **semantic / ontology owner** in the data-governance RACI | North Star §7.6 | Named individual |
| `FR-GOV-ONT-002` | Implement an **OBO-style semantic change workflow** (proposal → domain-owner review → versioned release → downstream impact check) | North Star §7.6 | Aligns to `NFR-MAINT-002` |
| `FR-GOV-ONT-003` | Enforce a **CI conformance check** that operational entities map to reference classes | North Star §5.4 | CI pipeline design |
| `FR-PKG-001` | Publish the **tiered SKU framework** T0 → T3+ as a product-marketing artefact | IKM/HCC §6.3 | Sales enablement scope |
| `FR-PKG-002` | Package a **new-building commissioning** offer (process standardisation + simulation + HCC stand-up) | IKM/HCC §6.2 | Kispi pattern reference |

---

## 6. Risk Assessment

Risks are categorised **Technical**, **Compliance / Regulatory**, or **Operational**. Impact = business impact if the risk materialises. Likelihood = current-state assessment.

### 6.1 Technical risks

| # | Description | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- | --- |
| T-01 | **Fabric IQ Ontology preview + no Switzerland-region GA date** blocks a critical-path commitment to the operational layer | Delivery delay; forced fallback to bespoke property graph | **H** | Keep reference layer portable in OWL/RDF; gate operational realisation on GA; MVO uses GA semantic model + curated views as an intermediate |
| T-02 | **Two-layer drift** between OWL/RDF reference and Fabric IQ operational graph | Semantic inconsistency; loss of the exact benefit the ontology exists to deliver | **M** | Governed crosswalk artefact; CI conformance check (`FR-GOV-ONT-003`); named semantic owner |
| T-03 | **Time-series binding performance** at production event volumes (bed state, OR status, monitoring devices) unvalidated | Real-time surfaces degrade under load | **M** | Performance spike in Sprint 09/10; document baseline; consider materialised semantic views for real-time paths |
| T-04 | **Simulation Engine** is a new capability class (skills, validation, data, compute pattern) | Missed SKU (T3), stalled strategic-planning use case | **M** | Distinct workstream with own acceptance criteria; label current shape assumptions (SimPy + ACA jobs) as "to be validated" |
| T-05 | **OR / anaesthesia / rostering integration** is provider-specific and complex | Integration cost per provider inflates T2 rollout | **M** | Discovery-led, contract-first; template `DC-OR-*` + `DC-STAFF-*` with provider-extension mechanism (`DC-ONB-CAPACITY-*` pattern) |
| T-06 | **OWL-DL reasoning need** at operational scale unclear (Fabric IQ is property-graph, not full OWL) | Rework if operational reasoning proves insufficient | **L** | Enforce most rules in curation + data contracts; treat OWL-DL as reference-layer artefact only until proven need |
| T-07 | **Ontology over-modelling before access patterns stabilise** | Wasted effort, latency, semantic churn | **M** | MVO first; bound to bed + OR + encounter; materialise views for real-time paths |

### 6.2 Compliance / regulatory risks

| # | Description | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- | --- |
| C-01 | **Fabric IQ preview** may not carry equivalent contractual data-residency / DPA guarantees as GA services | Blocks Swiss-region deployment | **M** | Do not use preview services in PROD PHI paths; ADR-0001 stands; operational layer gated on GA |
| C-02 | **New domains (OR, staffing, rooms, equipment)** may contain identifiable staff data (rostering) or patient-adjacent data (surgical schedules) | Classification and legal-basis mis-tag | **M** | Extend the `_classification` + `_legal_basis` + `_residency_tag` regime from the master-data model (2026-06-29 metadata review §1.5) to every new contract |
| C-03 | **Cantonal fragmentation** — cantons may impose stronger controls (binding instructions, moratoria) than federal law | Multi-provider onboarding drag | **M** | Provider-extension pattern (`FR-ONT-007`); cantonal control matrix in `docs/COMPLIANCE.md` |
| C-04 | **DSG / KVG / EPDG** obligations for surgical / anaesthesia data streams unassessed | Regulatory finding | **M** | Legal review of `DC-OR-CASE-v1` and `DC-STAFF-ROSTER-v1` before ingestion |
| C-05 | **SNOMED CT licensing** for terminology binding at scale | Cost / usage-scope finding | **L** | Confirm Swiss SNOMED CT licensing status; Azure Health Data Services terminology-service scope |
| C-06 | **Simulation outputs** (`DC-SIM-RESULT-v1`) may reveal capacity-planning intent that is commercially sensitive | Leakage across providers in a shared platform tier | **L** | Provider-internal boundary enforced; no shared-tenant simulation |

### 6.3 Operational risks

| # | Description | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- | --- |
| O-01 | **Operating-model layer not delivered alongside technology** — repeats the classic "great dashboard, no adoption" failure mode | Missed Kispi-class outcomes; managed-service (T3+) SKU cannot land | **H** | Fund `FR-HCC-001…004` as a peer workstream to the platform build; partner-led services wrap |
| O-02 | **Scope creep** dilutes the MVP | Delivery timeline slip | **H** | Contain via tiered SKUs (T2 = MVP + OR first; T3 = integral; T3+ = managed) |
| O-03 | **Scarce ontology skills** in-house | Ontology rot; two-layer drift | **M** | Reuse published ontologies (build only the capacity-unit abstraction + OR/staff/equipment/room specialisations + Fabric IQ realisation); consider OBO-experienced authoring partner |
| O-04 | **Change-management dependency** — IKM value depends on process adoption, not software | Under-realised value even if platform works | **H** | Explicit Lean / Design-Thinking / Gemba workstream (`FR-HCC-004`); executive sponsorship at each provider |
| O-05 | **KPI baseline not available at each target provider** | Business case unmeasurable | **M** | Include baseline capture in T0; documented method with per-metric source-system requirement |
| O-06 | **Channel conflict** if VR&P is partner in one deal and competitor in another | Sales friction | **M** | Explicit co-sell / co-deliver charter; IP and data-governance boundaries defined up front |
| O-07 | **Buyer complexity** — surgical, anaesthesia, nursing, HR, finance stakeholders | Longer sales cycles | **M** | Tiered SKUs; executive sponsor per deal |

---

## 7. Architecture & Governance Alignment Review

Evaluates alignment between the **governance framework** (policies, principles, ADRs, data contracts, Zero Trust, DSG/KVG/EPDG posture) and the **technical implementation** (landing zone, IaC, semantic layer, agents, Fabric domains, MCP allow-list).

### 7.1 Well-aligned areas

| # | Area | Evidence |
| --- | --- | --- |
| WA-01 | **GA-only critical path** for the MVP is preserved: Fabric IQ Ontology stays gated on Switzerland-region GA, reference layer authored in parallel to avoid vendor lock-in | ADR-0001, ADR-0002; North Star §7.2, §7.5 |
| WA-02 | **Swiss residency for PHI** unchanged: ontology schema/metadata is not PHI; live bindings still read Swiss-resident data; ADR-0003/0004 stand | North Star §7.2 |
| WA-03 | **Managed-identity + workload-identity federation** for all new integrations (OR, anaesthesia, rostering, biomedical assets) — inherits the current identity model | Extends [SECURITY.md](../SECURITY.md); no new secrets required |
| WA-04 | **Data-contract discipline extends cleanly** — `DC-OR-*`, `DC-STAFF-*`, `DC-ROOM-*`, `DC-DEVICE-*`, `DC-SIM-*`, `DC-REF-DISEASE-v1` reuse `_classification / _residency_tag / _legal_basis / _retention_class / _data_quality / _lineage_ref / _pseudonymisation_flag` from the master-data governance contract | 2026-06-29 metadata review §1.5; Sprint-09 §1.2 |
| WA-05 | **IaC-first** — new landing-zone extensions (simulation compute, new curated domains) fit the Bicep module pattern under `infra/modules/` | [INFRASTRUCTURE.md](../INFRASTRUCTURE.md); Sprint-09 track structure |
| WA-06 | **Advisory / HITL AI + concept-level grounding** — new agents (ORSA, CSA, SBA) inherit `NFR-AI-001…004` and gain *more* traceability once ontology-grounded | North Star §5.5; [AI.md](../AI.md) |
| WA-07 | **Purview lineage** extends to ontology-level lineage — a strict superset of today's schema-level lineage | North Star §6.1 |

### 7.2 Misalignments

| # | Misalignment | Impact |
| --- | --- | --- |
| MA-01 | **ADR-0002 currently defers Fabric IQ Ontology as optional** — the AMA outcome elevates it to the target semantic backbone for the integral tier. The ADR must be amended or superseded to reflect the new "GA-gated target backbone" stance while preserving the critical-path constraint | Decision record must not lag design; supersede in Sprint 09/10 |
| MA-02 | **PRD family coverage** — the FR/NFR catalogue does not yet include `FR-ONT-*`, `FR-OR-*`, `FR-STAFF-*`, `FR-CAP-*`, `FR-SIM-*`, `FR-HCC-*`, `NFR-KPI-*`, `NFR-ONT-*`. Traceability breaks until [PRD.md](../PRD.md) §7 (traceability matrix) is extended | Breaks the PR Output Contract's requirement-ID rule (repo `copilot-instructions.md` §6) |
| MA-03 | **No named semantic owner** — the governance RACI has data-platform, security and compliance owners but no ontology/semantic owner | Cannot enforce `NFR-ONT-001` |
| MA-04 | **Reference-to-operational crosswalk** is not yet an artefact — the reviewable object doesn't exist | Two-layer drift risk unmitigated |
| MA-05 | **Zero Trust posture** has not been re-assessed against new domains (OR sources, rostering, biomedical asset feeds) — new identities and network paths | Extension work item |
| MA-06 | **Reliability profile** ([OPERATIONS.md](../OPERATIONS.md) recovery classes) not extended to OR / staffing / simulation surfaces | Extension work item |

### 7.3 Areas requiring validation

| # | Area | Question |
| --- | --- | --- |
| RV-01 | Fabric IQ **operational reasoning depth** vs. OWL-DL | Do we need real-time reasoning, or are curation-time rules + contracts sufficient? |
| RV-02 | **Time-series binding performance** at production event volumes | Performance spike required |
| RV-03 | **Simulation realisation shape** | Confirm SimPy + Azure Container Apps as the target; validate against required fidelity (weekly tactical vs strategic annual) |
| RV-04 | **OOSTT wholesale reuse** vs cherry-pick | Ontology-authoring decision |
| RV-05 | **Reference-layer authoring** — in-house or OBO-experienced partner | Skills + cost decision |
| RV-06 | **OR-module pilot provider** — Hirslanden the strongest fit per prior provider analysis; confirmation required | Pilot selection |
| RV-07 | **KPI baselines** at target providers | Baseline availability + measurement method |
| RV-08 | **VR&P partner stack** — where to integrate vs. replace vs. co-sell | Commercial and technical decision |

---

## 8. Compliance Evaluation — Swiss Public-Sector Context

### 8.1 Data residency

- **Ontology schema/metadata is not PHI** — safe to author in any Microsoft-hosted region. *(North Star §7.2)*
- **Live bindings** (static + time-series) continue to read from Swiss-resident lakehouse / eventhouse under existing controls. **No change to ADR-0003/0004**.
- **Fabric IQ Ontology preview status is a hard blocker for a Swiss-region PROD critical path** until Microsoft confirms Switzerland-region GA and DPA equivalence with GA Fabric components. *(ADR-0001, ADR-0002)*
- **New domain data classification** — OR schedules, anaesthesia consultations, staff rosters, room state and device state — is largely **operational-confidential**, not deep PHI. This *eases* residency handling for these domains, but the classification-first discipline (`_classification`, `_legal_basis`, `_retention_class`) applies unchanged. *(IKM/HCC §7.8; 2026-06-29 metadata review §1.5)*
- **Simulation outputs** (`DC-SIM-RESULT-v1`) can contain provider-competitive planning intent; the platform's provider-internal single-tenant boundary is sufficient — no cross-provider aggregation on this path.

### 8.2 Federal vs cantonal fragmentation

- **DSG (federal data-protection law)** governs the personal-data baseline for staff-roster and patient-linked capacity data.
- **KVG / LAMal** governs healthcare-insurance / cost-related data flows (relevant to DRG, case-mix and cost-weight attributes on the reference layer).
- **EPDG / EPDV** governs the Swiss electronic patient record; FHIR-based crosswalks (`FR-ONT-006`) keep the ontology interoperable with EPDG obligations.
- **Cantonal instructions** may add binding constraints beyond federal law. The **provider-extension pattern** (`FR-ONT-007`) is the ontological equivalent of the cantonal-overlay governance principle recorded in the 2026-06-10 design-challenger review (§3.6): a canonical reference model + canton- or provider-specific specialisations, without re-architecture.

### 8.3 Zero Trust posture

- **Identity**: managed identities + WIF for every new source integration (OR/anaesthesia/rostering/biomedical); no long-lived secrets. *(No relaxation of current model.)*
- **Device**: unchanged; new domains do not introduce end-user devices beyond today's operator surface.
- **Workload**: least-privilege per new MCP scope; every new MCP server (if any) must be added to `.github/copilot/mcp.json` under CODEOWNERS approval and paired with a golden task.
- **Network**: private endpoints for Fabric-side ingress/egress apply to new curated domains; simulation compute (ACA jobs) inherits current VNet posture.
- **Data**: classification-first + residency-tag on every new contract; no PHI in preview services; no cross-region PHI failover.
- **Monitoring**: extend Application Insights + Log Analytics coverage to new agents and simulation runners.
- **Conditional access**: extend to new operator/planner roles introduced by the HCC operating model (bed manager, OR steering, staffing balance) as they surface.

### 8.4 Policy-as-code enforcement

- Existing Azure Policy pack applies to new resources; add policy assignments for simulation compute (ACA), new lakehouse curated tiers, and any new managed-identity role assignments.
- **CI conformance check** (`FR-GOV-ONT-003`) verifying reference↔operational crosswalk is a policy-adjacent control expressed in the delivery pipeline, not Azure Policy — but it is auditable.
- **Data-contract validation** (existing `policy/policy_gate.py` + `policy/schema/`) must be extended to the new `DC-*` families in Sprint 09/10.

---

## 9. Recommendations & Next Steps

Prioritised as **H = High (act now / Sprint 09)**, **M = Medium (Sprint 10–12)**, **L = Low (strategic — after Sprint 12)**. Each recommendation notes whether it is a **quick win** (low-effort, high-visibility) or a **strategic change**.

### 9.1 High priority (Sprint 09 scope)

| # | Recommendation | Type | Owner |
| --- | --- | --- | --- |
| H-01 | **Draft a superseding ADR** (`docs/adr/0005-fabric-iq-ontology-target-backbone-ga-gated.md`) amending ADR-0002: ontology becomes the target semantic backbone for the integral/HCC tier, hard Switzerland-region GA gate, portable reference layer in the interim. **Realised 2026-07-02 as [ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md)** *(Proposed)* — renumbered because `docs/adr/0005-*` was already assigned. | Strategic | Architecture |
| H-02 | **Stand up the Minimum Viable Ontology (MVO)** — auto-generated from the Sprint-09 Power BI semantic model per the Fabric IQ lab pattern; scope: Facility→Ward→Room→Bed→Encounter→Patient→Care team→Equipment **+ OR slot**; first time-series binding on bed state; reference-layer skeleton authored in parallel | Quick win | Data Platform |
| H-03 | **Extend the PRD** — add `FR-ONT-*`, `FR-OR-*`, `FR-STAFF-*`, `FR-CAP-*`, `FR-SIM-*`, `FR-HCC-*`, `NFR-KPI-*`, `NFR-ONT-*` to [PRD.md](../PRD.md) with traceability-matrix rows in §7 | Strategic | Product |
| H-04 | **Nominate a semantic / ontology owner** in the data-governance RACI; document in [OPERATIONS.md](../OPERATIONS.md) | Quick win | Governance |
| H-05 | **Design the reference↔operational crosswalk artefact** and its CI conformance check | Strategic | Data Platform |
| H-06 | **Confirm Fabric IQ Ontology GA date and Switzerland-region availability** with Microsoft — track as a risk with an explicit go/no-go date | Quick win | Product |
| H-07 | **Draft OR data contracts** `DC-OR-SCHEDULE-v1` and `DC-OR-CASE-v1` (schema + governance tags) even ahead of the OR module — enables Sprint 10 discovery with providers | Quick win | Data Platform |
| H-08 | **Add the HCC operating-model layer as a peer workstream** to the platform build — RACI, cadence surfaces, playbooks — not just a tail-end delivery item | Strategic | Product + Operations |

### 9.2 Medium priority (Sprint 10–12)

| # | Recommendation | Type |
| --- | --- | --- |
| M-01 | Deliver **OR module (T2)** — ingestion, prediction, OR-steering dashboard, ORSA agent | Strategic |
| M-02 | Deliver **HCC decision cadences** — daily/tactical/strategic surfaces + capacity RACI + bottleneck playbooks | Strategic |
| M-03 | Add **staffing** domain and SBA agent | Strategic |
| M-04 | Add **rooms & equipment** capacity units | Strategic |
| M-05 | **Extend Zero Trust posture** and reliability profile to new domains | Strategic |
| M-06 | **Publish the tiered SKU framework** T0 → T3+ as a product artefact | Quick win |
| M-07 | **Package the new-building commissioning offer** (Kispi pattern) | Strategic |
| M-08 | **Time-series binding performance spike** — validate production-scale bindings | Quick win |
| M-09 | **OBO-experienced authoring partner** decision (or in-house upskilling) | Strategic |
| M-10 | **VR&P partnership charter** — co-sell / co-deliver boundaries + IP model | Strategic |

### 9.3 Low priority (post-Sprint 12 / strategic)

| # | Recommendation | Type |
| --- | --- | --- |
| L-01 | Deliver the **Scenario Simulation Engine** (T3) — Azure ML + SimPy-class discrete-event + `DC-SIM-*` + CSA agent | Strategic |
| L-02 | Deliver **cross-resource ("integral") optimisation** — OR-plan feasibility against downstream beds and staff | Strategic |
| L-03 | Deliver the **managed steering** (T3+) SKU — ongoing coaching, tactical/strategic decision support | Strategic |
| L-04 | Publish the **process-ontology overlay** and simulate-grade ontology (Phase 3) | Strategic |
| L-05 | Full **FHIR / SNOMED CT crosswalk** at concept level | Strategic |
| L-06 | Publish an **OBO-quality reference layer** externally (positioning + academic credibility) | Strategic |

---

## 10. Traceability Matrix

Each row links a **requirement** (new or existing) to the **control** (governance / policy / architecture control), the **architecture decision** (ADR or design element), the **source** (transcript / paper / repo artefact), and the current **status**.

| Requirement | Control | Architecture Decision | Source | Status |
| --- | --- | --- | --- | --- |
| `FR-ONT-001` (Reference ontology BFO/OBO) | OBO governance workflow; semantic-owner RACI (`FR-GOV-ONT-001`) | New ADR proposed (H-01) | [North Star §7.4](./2026-07-01-ama-hcc-northstar-review/HCC-North-Star-Ontology-Model-Analysis.md) | **Proposed** |
| `FR-ONT-002` (Fabric IQ operational ontology) | GA-only critical path (ADR-0001); residency (ADR-0003/0004) | New ADR proposed (H-01) supersedes ADR-0002 | [North Star §7.4](./2026-07-01-ama-hcc-northstar-review/HCC-North-Star-Ontology-Model-Analysis.md) | **Proposed — GA-gated** |
| `FR-ONT-003` (Capacity-unit abstraction) | Data-contract governance | Design element (integral scope) | [North Star §4.5, §7.4](./2026-07-01-ama-hcc-northstar-review/HCC-North-Star-Ontology-Model-Analysis.md) | **Proposed** |
| `FR-ONT-004` (Ontology-grounded agents) | `NFR-AI-002/003/004`; advisory / HITL | Extends [AI.md](../AI.md) | [North Star §5.5](./2026-07-01-ama-hcc-northstar-review/HCC-North-Star-Ontology-Model-Analysis.md) | **Proposed** |
| `FR-ONT-005` (Process-ontology overlay for simulation) | Simulation acceptance criteria | Design element | [North Star §7.4](./2026-07-01-ama-hcc-northstar-review/HCC-North-Star-Ontology-Model-Analysis.md); [IKM/HCC §7.3](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md) | **Proposed** |
| `FR-ONT-006` (FHIR / SNOMED CT crosswalk) | Clinical-standards binding; DSG/EPDG interoperability | Extends [DATA.md](../DATA.md) | [North Star §7.3](./2026-07-01-ama-hcc-northstar-review/HCC-North-Star-Ontology-Model-Analysis.md) | **Proposed** |
| `FR-ONT-007` (Provider extension pattern) | `NFR-MAINT-004` | Extends [ARCHITECTURE.md](../ARCHITECTURE.md) | [North Star §7.4](./2026-07-01-ama-hcc-northstar-review/HCC-North-Star-Ontology-Model-Analysis.md) | **Proposed** |
| `NFR-ONT-001` (Two-layer versioning + CI check) | `FR-GOV-ONT-003` CI conformance check | New ADR proposed (H-01) | [North Star §5.4, §7.6](./2026-07-01-ama-hcc-northstar-review/HCC-North-Star-Ontology-Model-Analysis.md) | **Proposed** |
| `FR-OR-001…002` (OR data contracts) | Data-contract governance; residency | Extends [DATA.md](../DATA.md) | [IKM/HCC §7.2](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md) | **Proposed** |
| `FR-OR-003` (Case-duration / cancellation model) | Advisory / HITL; region-pinned inference | Extends [AI.md](../AI.md) | [IKM/HCC §7.3](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md) | **Proposed** |
| `FR-OR-004` (OR steering dashboard) | UX + KPI governance | Extends [SD.md](../SD.md) | [IKM/HCC §7.1, §8](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md); visual anchor [`hcc-operation-room-overview.png`](./2026-07-01-ama-hcc-northstar-review/hcc-operation-room-overview.png) | **Proposed** |
| `FR-OR-005` (ORSA agent) | Agent contract; MCP allow-list; advisory / HITL | Extends [AI.md](../AI.md); AGENTS.md registry | [IKM/HCC §7.4](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md) | **Proposed** |
| `FR-OR-006` (Anaesthesia consultation state) | Data-contract governance | Extends [DATA.md](../DATA.md) | [IKM/HCC §3.4](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md) | **Proposed** |
| `FR-STAFF-001…003` (Staffing domain) | DSG for staff data; classification-first | Extends [DATA.md](../DATA.md), [SECURITY.md](../SECURITY.md) | [IKM/HCC §7.2, §7.3](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md) | **Proposed** |
| `FR-STAFF-004` (SBA agent) | Agent contract | Extends AGENTS.md registry | [IKM/HCC §7.4](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md) | **Proposed** |
| `FR-CAP-001…002` (Rooms & equipment) | Data-contract governance | Extends [DATA.md](../DATA.md) | [IKM/HCC §7.2](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md); visual anchor [`hcc-apacities-utilization-pattern-overview.png`](./2026-07-01-ama-hcc-northstar-review/hcc-apacities-utilization-pattern-overview.png) | **Proposed** |
| `FR-SIM-001…004` (Simulation engine + CSA agent + cross-resource optimisation) | Advisory / HITL; provider-internal boundary | Extends [ARCHITECTURE.md](../ARCHITECTURE.md), [AI.md](../AI.md) | [IKM/HCC §7.3, §7.4](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md); visual anchor [`hcc-simboxcapacities-overview.png`](./2026-07-01-ama-hcc-northstar-review/hcc-simboxcapacities-overview.png) | **Proposed — realisation shape to validate** |
| `FR-HCC-001…004` (Decision cadences, RACI, playbooks, Lean/Gemba method) | Operations RACI; change-management workstream | Extends [OPERATIONS.md](../OPERATIONS.md) | [IKM/HCC §7.6, §7.7](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md) | **Proposed** |
| `NFR-KPI-001…005` (Operational-outcome KPIs) | KPI governance; baseline in T0 | Extends [OPERATIONS.md](../OPERATIONS.md) | [IKM/HCC §6.4](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md) | **Proposed** |
| `FR-GOV-ONT-001…003` (Semantic owner, OBO change workflow, CI conformance) | Governance RACI; CI policy | Extends `NFR-MAINT-002` | [North Star §7.6](./2026-07-01-ama-hcc-northstar-review/HCC-North-Star-Ontology-Model-Analysis.md) | **Proposed** |
| `FR-PKG-001…002` (Tiered SKUs + new-building commissioning offer) | Product-marketing artefact | Extends product playbook | [IKM/HCC §6.2, §6.3](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md) | **Proposed** |
| Existing `NFR-AI-002/003/004` (Grounded, traceable, region-pinned AI) | Advisory / HITL; ADR-0003/0004 | [AI.md](../AI.md) | Repository baseline | **In force — strengthened by ontology grounding** |
| Existing `NFR-MAINT-004` (Multi-provider reusability) | Provider-extension pattern | [ARCHITECTURE.md](../ARCHITECTURE.md) | Repository baseline | **In force — reinforced by `FR-ONT-007`** |

---

## 11. Sprint 09 Implementation Handoff

Sprint 09 is scoped as *Master Data Foundation, Simulation Enhancement & Capacity Dashboard* — see [sprint-09-master-data-simulation-and-capacity-dashboard.md](../sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md). This section calls out the **subset of the AMA outcome** that Sprint 09 should absorb directly.

### 11.1 Add to Sprint 09 scope (High-priority handoffs)

| # | Handoff | Sprint 09 track | Reference |
| --- | --- | --- | --- |
| H-01 | Draft superseding ADR 0005 (Fabric IQ ontology as target backbone — GA-gated). **Realised 2026-07-02 as [ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md)** *(Proposed)* — renumbered because ADR-0005 was already taken. | Governance / ADR track | This review §9.1 (H-01) |
| H-02 | **Stand up the MVO** in the Sprint-09 Power BI semantic model + Fabric IQ ontology generation (bounded to bed + OR slot + encounter + facility hierarchy) | Track 1 (data model extensions) | This review §9.1 (H-02); [Sprint-09 §1](../sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md#sprint-scope) |
| H-03 | Extend PRD with `FR-ONT-*` (minimum) — even if OR/STAFF/CAP/SIM/HCC/KPI families land in a later sprint | Product / PRD track | This review §5.1 |
| H-04 | Nominate the **semantic / ontology owner** in [OPERATIONS.md](../OPERATIONS.md) | Governance track | This review §9.1 (H-04) |
| H-05 | Design the **reference↔operational crosswalk** artefact + CI conformance check (design only in Sprint 09; enforcement can slip to Sprint 10) | Governance + Data Platform | This review §9.1 (H-05) |
| H-06 | Confirm Fabric IQ Ontology GA + Switzerland-region availability with Microsoft — track a go/no-go date | Product | This review §9.1 (H-06) |
| H-07 | Draft `DC-OR-SCHEDULE-v1` + `DC-OR-CASE-v1` schemas (contract only; ingestion in Sprint 10) | Data contracts | This review §9.1 (H-07) |

### 11.2 MVO scope for Sprint 09 (proposed)

Aligned to [Sprint-09 §1.1](../sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md#11-new-data-tier-goldreference) `gold/reference/` tier:

**Entity types (Fabric IQ auto-generated from the semantic model):**

- `Hospital` — from `dim_hospital`
- `Specialty` — from `dim_specialty`
- `HospitalService` — from `dim_hospital_service`
- `Ward` — new (facility→ward hierarchy)
- `Room` — new (ward→room hierarchy)
- `Bed` — new (room→bed hierarchy)
- `Encounter` — from `HospitalisationEpisode` (pseudonymised)
- `Patient` role — attached to `Encounter`
- `CareTeam` — object aggregate of health workers (KTH pattern)
- `Equipment` — from `dim_device` (proposed extension)
- **`ORSlot` — new (OR steering anchor)**

**Relationship types:**

`is_part_of` (bed⊑room⊑ward⊑hospital); `bearer_of` (facility → function; person → role); `has_role`; `realizes` (process→role); `participates_as_recipient`; `participates_as_performer`; `occurs_in` (encounter→facility); `assigned_to` (staff/equipment→unit).

**Bindings:**

- **Static** (lakehouse): all reference dimensions from `gold/reference/`.
- **Time-series** (eventhouse): **first target = bed-state changes** (occupied / available / blocked / cleaning). OR-status and monitoring-device time series follow in Sprint 10/11.

**Reference-layer skeleton (parallel):**

- Import: BFO (ISO/IEC 21838-2:2021), OMRSE (facility function typology), OGMS (encounter/patient/provider terms), OOSTT (organisational structure), Goyer et al. healthcare-system classes.
- Author: `CapacityUnit` abstraction + subtypes (Bed, ORSlot, Room, StaffShift, Device).
- Artefact: `docs/ontology/` (new folder) — OWL/RDF file(s) versioned as a first-class asset per `NFR-ONT-001`.
- Crosswalk artefact: `docs/ontology/crosswalk.md` — reference-layer class ↔ Fabric IQ entity type ↔ data contract.

### 11.3 Sprint 09 acceptance evidence (proposed)

- MVO ontology generated in Fabric IQ **or** an equivalent property-graph fallback if Switzerland-region GA is not confirmed by sprint mid-point.
- Reference-layer OWL/RDF skeleton merged under `docs/ontology/`.
- Crosswalk artefact merged; CI conformance check *at least in dry-run* on the pipeline.
- ADR 0005 (superseding ADR-0002) merged.
- PRD `FR-ONT-*` family + traceability-matrix rows merged.
- Semantic owner named in [OPERATIONS.md](../OPERATIONS.md).
- Fabric IQ GA + Switzerland-region status tracked as a live risk in [OPERATIONS.md](../OPERATIONS.md).

### 11.4 Out of scope for Sprint 09 (explicit)

- Full OR module (data ingestion, prediction models, ORSA agent, OR-steering dashboard) — Sprint 10.
- Staffing / rooms / equipment domains — Sprint 10/11.
- Scenario Simulation Engine + CSA agent — Sprint 11/12+ (workstream initiation only).
- HCC operating-model layer (cadences, RACI, playbooks, Lean/Gemba method) — peer workstream starting Sprint 10 with Product + Operations.
- Full FHIR / SNOMED CT concept-level crosswalk — Phase 3 (post-Sprint 12).

---

## Appendix A — Source Materials

All under [docs/reviews/2026-07-01-ama-hcc-northstar-review/](./2026-07-01-ama-hcc-northstar-review/):

| File | Type | Description |
| --- | --- | --- |
| [IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md](./2026-07-01-ama-hcc-northstar-review/IKM-HCC-vs-Swiss-Capacity-Platform-Analysis.md) | Markdown analysis | VR&P IKM/HCC vs current platform — gap map, business + technical incorporation blueprint, tiered SKUs |
| [HCC-North-Star-Ontology-Model-Analysis.md](./2026-07-01-ama-hcc-northstar-review/HCC-North-Star-Ontology-Model-Analysis.md) | Markdown analysis | Two-layer North Star ontology (BFO/OBO reference + Fabric IQ operational), MVO scope, governance model |
| [hcc-operation-room-overview.png](./2026-07-01-ama-hcc-northstar-review/hcc-operation-room-overview.png) | Image | HCC operating-room / OR steering overview |
| [hcc-apacities-utilization-pattern-overview.png](./2026-07-01-ama-hcc-northstar-review/hcc-apacities-utilization-pattern-overview.png) | Image | HCC capacities utilisation pattern (integral scope visualisation) |
| [hcc-simboxcapacities-overview.png](./2026-07-01-ama-hcc-northstar-review/hcc-simboxcapacities-overview.png) | Image | HCC sim-box capacities overview (scenario-simulation visualisation) |

### Reused evidence base (from the two companion papers, cited here for traceability)

- **BFO** — ISO/IEC 21838-2:2021 — upper ontology.
- **OMRSE** — Ontology for Modeling Health Care Facilities.
- **OGMS** — Ontology for General Medical Science — clinical-encounter terms.
- **OOSTT** — Ontology of Organizational Structures of Trauma centers and Trauma systems.
- **Goyer, Fabry, Barton & Ethier** — *An ontology for healthcare systems* (ICBO 2022).
- **Jerjas & Hall** — *Specifying an ontology framework to model processes in hospitals* (KTH, 2017).
- **OBO Foundry principles** — realism, univocity, orthogonality, reuse.
- **SNOMED CT** — clinical terminology.
- **FHIR** — resource model.
- **Microsoft Fabric IQ — "Build an ontology from a semantic model"** — Microsoft Learn lab (preview).
- **UCSF PCMC / Epic** — Hospital Command Center operating-practice benchmark.
- **VR&P** — Integrales Kapazitätsmanagement (IKM) service page; Universitäts-Kinderspital Zürich (Kispi) case study; Klinikum Ernst von Bergmann and LKH-Univ. Klinikum Graz references.

---

> The reviewer prompt used to produce this document is maintained centrally as the **standard reviewer prompt** for all AMA review sessions in [docs/reviews/README.md](./README.md#standard-reviewer-prompt-template).
