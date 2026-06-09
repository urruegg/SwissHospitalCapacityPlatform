# Solution Review Document
## SwissHospitalCapacityPlatform — AMA CTO Mentor Review Session
**Date of Review:** 2026-06-09  
**Document Version:** 1.0  
**Classification:** Internal — Architecture & Governance Review  
**Prepared By:** AI-assisted review synthesis  

> **Note on anonymisation:** Participant names have been replaced with role designators throughout this document. Specific healthcare institutions are referenced in their public capacity as named organisations.

| Role Designator | Description |
|---|---|
| **Solution Architect** | Author of the SwissHospitalCapacityPlatform solution and primary presenter |
| **CTO Mentor** | Senior technical reviewer and programme mentor |
| **Cantonal Health Regulator** | Representative of the cantonal health authority (Canton Zurich) with directive authority |
| **Hospital Digital Transformation Lead** | Hospital-side stakeholder with responsibility for digital implementation |
| **Healthcare Industry Expert** | Microsoft internal healthcare domain expert |
| **Technical Architecture Reviewer** | Peer technical reviewer (non-healthcare specialist) |
| **Programme Mentor** | External AMA programme mentor (based outside Switzerland) |

---

## 1. Executive Summary

The AMA CTO Mentor Review Session of 2026-06-09 evaluated the **SwissHospitalCapacityPlatform** — an AI-powered, agent-based bed management and patient flow platform designed for Swiss cantonal hospital providers. The session produced substantive alignment on three architectural directions and surfaced five follow-up actions requiring resolution before the next review gate.

**Overall assessment:** The solution demonstrates a sound conceptual foundation — infrastructure-as-code, compliance traceability, and data minimisation as a risk-reduction strategy are well-reasoned. However, several critical dimensions remain **incomplete or unvalidated**: hybrid resilience architecture, Sovereign Landing Zone integration, policy-as-code enforcement, and the formal mapping of cantonal-level regulatory obligations. These gaps represent the primary risk surface prior to any production deployment.

**Key outcomes of the review:**

| Theme | Status | Priority |
|---|---|---|
| Data minimisation / capacity-only approach | ✅ Validated | High |
| Compliance traceability (Control IDs, GitHub) | ✅ In progress | High |
| Sovereign Landing Zone (SLZ) alignment | ⚠️ Not yet integrated | Critical |
| Hybrid / offline-resilient architecture | ⚠️ Not yet designed | Critical |
| Cantonal regulatory mapping | ⚠️ Requires verification | High |
| Agent design (Demand / Discharge / Bed / Integration) | ⚠️ Under review | Medium |
| AHV number / PID access controls | ⚠️ Approach defined, not implemented | High |
| Policy-as-code enforcement | ⚠️ Planned, not in production | High |
| Azure Foundry regional availability | ❌ Dependency risk identified | Medium |
| Confidential computing applicability | ❓ Not evaluated | Low |

---

## 2. Context Overview

### 2.1 Solution Background

The SwissHospitalCapacityPlatform (referenced as Case Study 26 adapted to Switzerland) is an AI-powered platform for patient flow optimisation and hospital capacity management, targeting Swiss cantonal hospital providers. The solution is publicly documented on GitHub under a MIT licence, with an explicit commitment to anonymisation and non-referenceability of any involved persons or institutions.

The conceptual analogy driving the design is a **hotel operations model**: patients are treated as guests with specific requirements that determine which room and services they receive. Capacity management is orchestrated across this demand landscape by AI agents.

### 2.2 Review Session Format

- **Duration:** 43 minutes 43 seconds  
- **Participants:** Solution Architect, CTO Mentor  
- **Format:** Live screen-share review with verbal discussion (mixed German/English)  
- **Artefacts shared:** GitHub repository, Sovereign Landing Zone documentation  
- **Recording transcription:** AI-generated (Teams auto-transcription); transcript quality is partially degraded — some passages are phonetically transcribed and require contextual interpretation.

### 2.3 Key Reference Documents

| Artefact | Status | Notes |
|---|---|---|
| GitHub: SwissHospitalCapacityPlatform | Active (MIT) | Infrastructure-as-code in progress; architecture design in early stage |
| Azure Sovereign Landing Zone (SLZ) | Active reference | Shared during session; deprecation announced for H1 2026 (repo archival) |
| SLZ — Microsoft Learn documentation | Active | Controls and principles reference |
| Swiss nDSG (Data Protection Act) | Referenced | Federal-level |
| KVG (Federal Health Insurance Act) | Referenced | Federal-level |
| EPR (Electronic Patient Record) | Referenced | Federal framework, implementation in progress |
| Cantonal health data regulations | Unverified | Follow-up required |

---

## 3. Key Findings from Review Session

### 3.1 Regulatory Framework — Federal vs. Cantonal Distinction

**Finding:** The Solution Architect identified that **Swiss healthcare data regulations are not uniformly enforced at the federal level.** The primary legislative framework (KVG, nDSG, EPR) is national, but implementation authority and enforcement is delegated to the cantons. Within cantons, individual health authority representatives may carry either binding directive authority or only advisory capacity — the risk ownership ultimately rests with the implementing institution (hospital).

**Transcript reference:**
> *"Das Ganze ist nicht auf Bundesebene geregelt, sondern auf kantonsspezifischer Ebene geregelt … der Kanton gibt etwas vor und dann nachher macht das Gesundheitswesen im Kanton oder ein Spital, das das betreibt …"* — Solution Architect, ~4:52

The CTO Mentor confirmed this interpretation, noting that the **Cantonal Health Regulator** (Canton Zurich representative) holds signature authority over healthcare technology deployments, while the **Hospital Digital Transformation Lead** operates in an advisory capacity, over-documenting to achieve implied consent where no formal objection is raised.

**Implication:** The compliance architecture must model two distinct authority layers: (a) the national legislative baseline and (b) the cantonal implementation governance layer. These require separate control mappings.

---

### 3.2 Data Residency Strategy

**Finding:** Switzerland data residency is a central requirement for patient data. The current strategy deliberately **excludes personally identifiable health data (PHI/PII) from the system's primary processing scope**. When the system operates in a purely capacity-oriented mode (no patient-level data), data residency requirements are substantially relaxed.

**Transcript reference:**
> *"Wenn wir aber dort sprechen, sind nicht die Schweiz machen, aber wir haben keinen PH in Daten. Dann spielt es keine Rolle mehr."* — Solution Architect, ~3:39
>
> *"Ich kann die Komplexität reduzieren und bin rein kapazitätsorientiert unterwegs."* — Solution Architect, ~3:50

The CTO Mentor noted that **Dragon Copilot** is already used at reference hospitals (e.g., Inselspital Bern) despite data residency not being guaranteed in Switzerland — illustrating the pragmatic tension between regulatory intent and current practice in the sector.

---

### 3.3 Identity and PID Handling Strategy

**Finding:** Swiss hospital identification is currently based on the Krankenkassenkarte (health insurance card), which exposes the AHV number (Swiss social security number) — a sensitive personally identifiable datum traceable back to a specific individual.

The Solution Architect proposed a **dual-layer identity model**:
- AHV number access is restricted to authorised roles only
- Capacity-oriented processes use internal running numbers (pseudonymisation)
- Patient-data linkage occurs only at the system endpoint (at the point of integration with core clinical systems), not within the platform itself

**Transcript reference:**
> *"AV Nummer schützen, dass nur die Leute dürfen das sehen, wo sie auch die Rechte dazu haben … alle anderen, die nicht das sehen dürfen, welche rein kapazitätsorientiert unterwegs sind, die müssen eigentlich nur wissen es ist die Nummer, eine interne Laufnummer."* — Solution Architect, ~24:03
>
> *"Das müsste nachher immer durch andere Systeme durch die andere Domäne sichergestellt werden."* — Solution Architect, ~25:48

The CTO Mentor raised the risk of **secondary re-identification**: even without the AHV number, a combination of quasi-identifiers (blood group, age, gender, diagnosis category) may be sufficient to uniquely re-identify a patient. This risk is not yet formally addressed in the solution design.

---

### 3.4 Zero Trust and Sovereign Landing Zone

**Finding:** The CTO Mentor **strongly recommended** adoption of the Microsoft Sovereign Landing Zone (SLZ) as the foundation for the platform's Azure infrastructure. The SLZ, as deployed for Swissmedic (Switzerland's medicines regulatory authority, equivalent to the FDA), provides a four-level security model:

| Level | Controls |
|---|---|
| Level 1 | Data Residency |
| Level 2 | Data Residency + Global Services |
| Level 3 | Level 2 + Encryption at Rest |
| Level 4 | Level 3 + Encryption in Use |

The SLZ is implemented as a **Terraform script** (fully customisable), incorporates Azure Policy-based controls, and provides a flat management group hierarchy with Public, Confidential Corp, and Confidential Online workload tiers.

**Transcript reference:**
> *"Die Microsoft Landing Zone bietet verschiedene Security Levels, von Data Residency bis zu Verschlüsselung im Ruhezustand und in Benutzung, und ist als Terraform-Skript vollständig anpassbar."* — Meeting Summary
>
> *"Wenn du das am Ende ist hast eigentlich durch den Zero Trust hast du nicht jetzt 100% alles gelöst, aber einen grossen Teil hast du recht hast von Anfang an ausgeklammert."* — CTO Mentor, ~38:48

The Solution Architect confirmed that a Landing Zone structure (Dev/Test/Prod) is partially in place and acknowledged the SLZ as the next integration target.

> **Critical note:** The Azure Sovereign Landing Zone GitHub repository has been announced for archival in H1 2026. The canonical path forward is the Microsoft Learn documentation and the Sovereign Public Cloud governance model. This transition must be tracked.

---

### 3.5 Hybrid Architecture Requirement

**Finding:** The CTO Mentor explicitly flagged that **all Swiss hospitals are legally required to maintain 24/7 operational availability**, which mandates a hybrid architecture. Critical services must remain operational even without connectivity to the hyperscaler.

**Transcript reference:**
> *"Spitäler in der Schweiz haben 7×24 Betriebe Auflage. Das bedeutet jede IT Infrastruktur … ganz sicher eine hybride Architektur … du musst vielleicht auch noch das irgendwo in deine Lösung einbauen, dass vitalen Services von diesem Hotel auch zur Verfügung gestellt werden müssen, falls keine Verbindung zum Hyperscanner da sein würde."* — CTO Mentor, ~39:19 / ~39:48

This requirement was **not yet incorporated** in the current solution design. The Solution Architect confirmed it as a new follow-up point ("dann nehme ich das als fünften Punkt noch auf").

Azure Local (formerly Azure Stack HCI) was mentioned as a potential integration option for private cloud capacity at the hospital edge.

---

### 3.6 Agent Architecture

**Finding:** The platform is designed around a **modular agent architecture** with one orchestrator and four specialised agents:

1. **Orchestrator / Planner** — top-level orchestration and routing
2. **Demand Forecasting Agent** — may be a simple event-driven model rather than an AI agent
3. **Discharge Coordination Agent** — patient readiness assessment for bed reallocation
4. **Bed Management Copilot** — AI-assisted bed assignment
5. **Integration Flow Agent** — capacity data from external providers (e.g., Spitex)

The Solution Architect noted that **Azure Foundry is not available in the required Swiss regions**, creating a dependency constraint. Whether each component must be a full AI agent or can be a simpler event-driven model is still under review.

---

### 3.7 Traceability and Documentation Approach

**Finding:** The Solution Architect has implemented a **Control ID / label-based traceability model** linking regulatory requirements to technical controls and architecture decisions. Everything is documented in the public GitHub repository. An AI agent is used to read review session transcripts, extract decisions, and identify deviations from the landing zone baseline ("drift analysis").

**Transcript reference:**
> *"Die Tracerility wird durch Labels und Control IDs sichergestellt, um die Nachvollziehbarkeit der Umsetzung zu gewährleisten."* — Meeting Summary
>
> *"Ich habe angefangen ein Compliance Aufbau … alles in GitHub … das ist die ganze Traceability mit dem Evidence Modell."* — Solution Architect, ~10:47 / ~13:37

---

## 4. Deviation Analysis

### 4.1 Deviations from Microsoft Cloud Adoption Framework (CAF)

| # | CAF Best Practice | Current Status | Gap |
|---|---|---|---|
| 4.1.1 | Landing Zone — Management Group hierarchy with Public/Confidential tiers | Partial | SLZ management group structure not yet aligned to SLZ spec (Confidential Corp / Confidential Online layers absent) |
| 4.1.2 | Identity baseline — Entra ID with defined guest/B2C separation | Conceptual only | B2C identity model discussed but not designed in detail |
| 4.1.3 | Policy-as-code — Azure Policy applied at management group level | Planned | Controls as code mentioned but not yet in production |
| 4.1.4 | Network topology — Hub & Spoke or Virtual WAN | Not mentioned | Network architecture not discussed; assumed default |
| 4.1.5 | Dev/Test/Prod environment separation | Referenced | Topology tested in SIT then production; full 3-tier separation not confirmed |

### 4.2 Deviations from Microsoft Well-Architected Framework (WAF)

| # | WAF Pillar | Current Status | Gap |
|---|---|---|---|
| 4.2.1 | Reliability — defined RTO/RPO, multi-region or hybrid failover | Not addressed | 24/7 hybrid requirement identified but not designed |
| 4.2.2 | Security — Zero Trust, least-privilege, data classification | Partially addressed | Zero Trust intended; access control for AHV/PID not yet implemented |
| 4.2.3 | Operational Excellence — IaC, idempotent deployments, rollback | In progress | Idempotent deployment and rollback mentioned as requirements, not yet implemented |
| 4.2.4 | Performance Efficiency — scalability design | Not discussed | No capacity / load design documented |
| 4.2.5 | Cost Optimisation | Not discussed | No cost model or optimisation strategy documented |

### 4.3 Deviations from Zero Trust Principles

| # | Zero Trust Principle | Current Status | Gap |
|---|---|---|---|
| 4.3.1 | Verify explicitly — all access requests authenticated and authorised | Partially addressed | AHV/PID access restriction planned; no formal policy engine yet |
| 4.3.2 | Use least-privilege access — JIT, JEA | Not yet addressed | No RBAC / PIM design documented |
| 4.3.3 | Assume breach — segmentation, monitoring, analytics | Not addressed | No breach response or monitoring design documented |
| 4.3.4 | Data classification and labelling | Partially addressed | Capacity data vs. PHI data segregation conceptualised but not formally classified |

---

## 5. New and Emerging Requirements

The following requirements are **not explicitly stated in the existing PRD or solution design** but emerged from the review session discussion. They must be formally captured and incorporated.

| ID | Requirement | Source | Priority |
|---|---|---|---|
| NEW-01 | The solution must operate all vital services in a **local/edge mode** without connectivity to the hyperscaler, supporting the Swiss 24/7 hospital availability obligation | CTO Mentor, ~39:19 | Critical |
| NEW-02 | The compliance architecture must model **both the national legislative baseline AND the cantonal implementation governance layer** as distinct control families | Solution Architect, ~4:52 / CTO Mentor, ~11:27 | High |
| NEW-03 | The SLZ security level applicable to this solution must be formally selected (Level 1–4) and the choice documented with rationale | CTO Mentor, ~37:04 | High |
| NEW-04 | The solution must formally address **secondary re-identification risk**: even capacity-only data combined with quasi-identifiers may enable re-identification of patients | CTO Mentor, ~27:16 | High |
| NEW-05 | Azure Foundry regional unavailability must be formally documented as an **architectural constraint** and a mitigating hosting approach confirmed for Swiss regions | Solution Architect, ~15:08 | Medium |
| NEW-06 | An **EPR integration strategy** must be defined: the Electronic Patient Record is a federal framework now in early deployment; the platform's approach to EPR linkage must be designed | Referenced, ~11:04 | Medium |
| NEW-07 | The **KYC / patient admission identification gap** should be explicitly scoped in or out of the platform's responsibility boundary: current Swiss admission process has no strong identity verification beyond the health insurance card | CTO Mentor, ~21:22 / ~22:08 | Medium |
| NEW-08 | A **confidential computing applicability assessment** should be conducted to determine if any computation on anonymised data warrants this approach | CTO Mentor, ~29:18 | Low |

---

## 6. Risk Assessment

### 6.1 Technical Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| T-01 | Hybrid/offline architecture not designed — vital services unavailable during connectivity outage | High | Critical | Design Azure Local / edge pattern; define which agents must run locally |
| T-02 | Azure Foundry not available in Swiss regions — AI orchestration layer may require alternative hosting | Medium | High | Document constraint; evaluate Azure AI Services regional availability; consider AKS-hosted agents |
| T-03 | Policy-as-code not yet in production — control enforcement relies on manual processes | High | High | Prioritise policy deployment pipeline; adopt SLZ Terraform baseline as starting point |
| T-04 | Agent design not finalised — risk of over-engineering (AI where simple event models suffice) or under-engineering (capacity without intelligence) | Medium | Medium | Complete agent design review; document decision rationale per agent |
| T-05 | IaC rollback mechanism not yet implemented — failed deployments in production may be unrecoverable | Medium | High | Implement idempotent IaC with explicit rollback targets |

### 6.2 Compliance Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| C-01 | Cantonal-level regulations exist but have not been verified — compliance gaps may exist below federal level | Medium | High | Follow up with Hospital Digital Transformation Lead and cantonal health authority |
| C-02 | EPR integration not yet designed — EPR rollout may create new data flow obligations the platform must satisfy | Medium | High | Engage Swiss EPR programme office; design integration boundary now |
| C-03 | AHV number handling is defined conceptually but not implemented — risk of uncontrolled PID exposure | High | Critical | Implement RBAC-based AHV access control before any pilot deployment |
| C-04 | Secondary re-identification via quasi-identifiers not formally addressed — capacity data may carry latent identifiability | Medium | High | Conduct formal data minimisation analysis; document quasi-identifier policy |
| C-05 | Data residency for AI model inference — if AI services run outside Switzerland, inference on capacity data may implicitly include indirect patient signals | Medium | High | Confirm all AI inference endpoints are within Swiss Azure regions |

### 6.3 Operational Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| O-01 | Stakeholder engagement with cantonal health authority is pending — regulatory approval pathway unclear | Medium | High | Prioritise contact with Cantonal Health Regulator |
| O-02 | Dragon Copilot reference deployment (Inselspital Bern) uses non-Swiss data residency — creates a precedent that may undermine the platform's stronger controls as a differentiator or create regulatory confusion | Low | Medium | Document explicitly why this platform takes a stronger approach; do not reference as a compliance model |
| O-03 | SLZ GitHub repository scheduled for archival H1 2026 — Terraform scripts may not be maintained | High (imminent) | Medium | Migrate to Microsoft Sovereign Public Cloud governance documentation as primary reference; fork SLZ Terraform if needed |
| O-04 | Public GitHub repository with MIT licence — risk of institutional data inadvertently included | Low | High | Maintain strict anonymisation review before each commit; enforce pre-commit validation |

---

## 7. Architecture and Governance Alignment Review

### 7.1 Current Architecture Summary

Based on the review session and GitHub repository description, the current architecture state is:

```text
┌─────────────────────────────────────────────────────────────────┐
│              SwissHospitalCapacityPlatform (Conceptual)          │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Azure Fabric (Primary Data Platform)                      │  │
│  │  • All operational data stored here                        │  │
│  │  • Capacity-oriented data only (no PHI in primary tier)    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  Agent Orchestration Layer                               │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │     │
│  │  │ Demand   │ │Discharge │ │  Bed Mgmt│ │Integration│  │     │
│  │  │Forecasting│ │Coord.   │ │  Copilot │ │   Flow    │  │     │
│  │  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │     │
│  │       ↑            ↑            ↑              ↑         │     │
│  │                 Orchestrator (Planner)                    │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  UI Layer                                                │     │
│  │  • Native application (chat interface)                   │     │
│  │  • M365 integration: OPTIONAL                            │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  Integration Boundary (Endpoint only)                    │     │
│  │  • PHI/AHV linkage occurs HERE, not in platform          │     │
│  │  • Delegates to hospital core systems for identity       │     │
│  └─────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Governance Model Alignment

The current governance approach maps to the following alignment status against the recommended SLZ model:

| Governance Layer | Recommended (SLZ / CAF) | Current State | Alignment |
|---|---|---|---|
| Management Group hierarchy | Public / Confidential Corp / Confidential Online tiers | Partial Dev/Test/Prod separation | ⚠️ Partial |
| Policy enforcement | Azure Policy applied at MG level, policy-as-code | Planned, not deployed | ⚠️ Planned |
| Identity baseline | Entra ID, Conditional Access, B2C for external | B2C discussed conceptually | ⚠️ Conceptual |
| Data residency controls | SLZ Level 1+ enforced via policy | Not yet configured | ❌ Missing |
| Encryption at rest | SLZ Level 3 (recommended for health data) | Not confirmed | ❓ Unknown |
| Encryption in use | SLZ Level 4 (optional, for highest sensitivity) | Not evaluated | ❓ Unknown |
| Network segmentation | Hub & Spoke / Private Endpoints | Not discussed | ❓ Unknown |
| Monitoring / SIEM | Microsoft Sentinel or equivalent | Not discussed | ❓ Unknown |
| Hybrid connectivity | Azure Local / ExpressRoute | Not yet designed | ❌ Missing |

### 7.3 Tenant Strategy

No multi-tenant or cross-cantonal tenant strategy was discussed. If the platform is intended to serve multiple cantonal hospital providers, the following questions must be answered:

- Is each hospital a separate Azure subscription within a shared management group hierarchy?
- Or is this a SaaS model with logical tenant isolation within a single subscription?
- How are cross-hospital capacity queries handled (e.g., overflow to Spitex)?

These are **unresolved architecture decisions** that will materially affect the compliance and isolation model.

---

## 8. Compliance Evaluation — Swiss Public Sector Context

### 8.1 Applicable Regulatory Framework

| Regulation | Scope | Applicability | Status in Solution |
|---|---|---|---|
| **nDSG** (Bundesgesetz über den Datenschutz, Sept 2023) | National data protection | High — any processing of personal data | Referenced; compliance structure started |
| **KVG** (Krankenversicherungsgesetz) | Federal health insurance obligations | High — patient capacity managed under KVG-funded care | Referenced; not fully mapped |
| **EPR** (Elektronisches Patientendossier) | Federal interoperability framework | Medium — EPR integration boundary undefined | Referenced; integration not designed |
| **Swissmedic regulations** | Medical device / software as medical device (SaMD) | Potentially applicable if the system supports clinical decisions | Not evaluated |
| **Cantonal health data laws** | Canton-specific | Requires verification — may add obligations above nDSG | Not verified (follow-up required) |
| **AI Act (EU)** | EU AI regulation (Swiss alignment TBD) | Medium — AI systems in healthcare may be classified as high-risk | Not evaluated |

### 8.2 Key Compliance Strengths

1. **Data minimisation by design** — the capacity-only approach that excludes PHI from primary processing is an excellent risk-reducing strategy that directly implements the nDSG principle of purpose limitation and data minimisation.

2. **Traceability architecture** — Control IDs, label-based tagging, and GitHub evidence documentation provide an audit trail capability aligned with nDSG accountability requirements and CAF governance.

3. **PHI/AHV access restriction design** — the proposed RBAC model where only authorised roles can access the AHV number, with all other processes using pseudonymous internal running numbers, is the correct architectural pattern.

### 8.3 Key Compliance Gaps

1. **AHV number as sensitive PID**: The AHV number (Swiss social security / AVS number) has historically encoded date of birth and has long-term persistence. It must be classified as a **special category personal identifier** and handled under the most restrictive nDSG controls. The current design acknowledges this but does not yet have an implemented control.

2. **EPR framework**: Switzerland's EPR (electronic patient dossier, EPD) programme is in early national rollout (via Post, as noted in the transcript). The platform's relationship to EPR-structured data must be formally defined: is the platform a consumer, a contributor, or isolated from EPR entirely?

3. **Software as Medical Device (SaMD)**: If any agent (particularly Discharge Coordination or Bed Management Copilot) influences clinical decisions — even in an advisory capacity — the system may be subject to Swissmedic SaMD classification. This has not been evaluated. The solution explicitly aims for **advisory, non-clinical decision support**, but the boundary must be precisely defined and documented.

4. **AI governance / Swiss AI Act alignment**: The EU AI Act categories high-risk AI as including AI systems that assist in hospital capacity and patient triage decisions. Switzerland's alignment with the EU AI Act is evolving. The solution should document its AI risk classification now.

5. **Confidentiality tier assignment**: Under the SLZ model, patient-adjacent capacity data should be classified. Even capacity-only data (if it could be combined with externally available data for re-identification) may warrant **Confidential Corp** tier rather than the Public tier.

### 8.4 Regulatory Decision Authorities — Two-Layer Model

Based on the review session, the compliance architecture must model two distinct layers:

```text
┌──────────────────────────────────────────────────────────────┐
│  Layer 1: National Legislative Baseline                      │
│  nDSG / KVG / EPR — applies uniformly across all cantons    │
│  Controls must be mandatory and non-waivable                 │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│  Layer 2: Cantonal Implementation Governance                 │
│  Canton-specific enforcement authority                       │
│  Directive vs. advisory authority models vary by canton      │
│  Hospital-level risk acceptance responsibility               │
└──────────────────────────────────────────────────────────────┘
```

Importantly, two contrasting hospital governance postures were observed in the discussion:
- **Explicit approval model**: Hospital will not proceed without formal cantonal sign-off
- **Implied consent model**: Hospital over-documents and proceeds in the absence of objection

The platform's compliance documentation must accommodate **both postures** with appropriate evidence packaging.

---

## 9. Recommendations and Next Steps

### 9.1 Critical (Complete Before Next Review Gate)

| # | Action | Owner | Deadline |
|---|---|---|---|
| R-01 | **Integrate Sovereign Landing Zone** as the Azure infrastructure baseline; select SLZ Level 3 (Data Residency + Global Services + Encryption at Rest) as the target security level for hospital capacity data; document rationale | Solution Architect | Before pilot design |
| R-02 | **Design hybrid architecture** for 24/7 availability; identify which agents/services must operate locally (offline); evaluate Azure Local (Arc-enabled) as edge compute option | Solution Architect | Before pilot design |
| R-03 | **Implement RBAC controls for AHV/PID access** — formally separate capacity-processing roles from identity-resolution roles; implement Azure AD / Entra ID role assignments as code | Solution Architect | Before any data integration |
| R-04 | **Verify cantonal regulatory obligations** — engage the Hospital Digital Transformation Lead and cantonal health authority representative to confirm whether canton-specific health data laws impose requirements beyond the national nDSG/KVG baseline | Solution Architect | Next stakeholder session |

### 9.2 High Priority (Complete Within 2 Sprints)

| # | Action | Owner |
|---|---|---|
| R-05 | **Conduct SaMD classification assessment** — determine whether any agent's output constitutes clinical decision support under Swissmedic classification criteria; document the boundary explicitly | Solution Architect |
| R-06 | **Define formal data classification schema** aligned with SLZ tiers (Public / Confidential Corp / Confidential Online) and apply to all data flows | Solution Architect |
| R-07 | **Formalise secondary re-identification analysis** — enumerate quasi-identifiers present in capacity data; document de-identification policy and technical controls | Solution Architect |
| R-08 | **Define EPR integration boundary** — explicitly declare whether the platform integrates with, contributes to, or is isolated from the Swiss EPR framework | Solution Architect |
| R-09 | **Resolve Azure Foundry regional constraint** — document as a formal architectural constraint; confirm alternative hosting approach for Swiss region AI orchestration | Solution Architect |

### 9.3 Medium Priority (Before Stakeholder Presentations)

| # | Action | Owner |
|---|---|---|
| R-10 | Produce **Executive Summary** for Healthcare Team Thursday meeting to gather feedback from healthcare industry experts | Solution Architect |
| R-11 | Schedule **review with Hospital Digital Transformation Lead** to validate regulatory assumptions and explore Balgrist Klinik engagement | Solution Architect / CTO Mentor |
| R-12 | Finalise **agent design** — for each of the 5 agents, document: (a) AI vs. event-driven decision, (b) regional deployment target, (c) data inputs and outputs, (d) offline/hybrid behaviour | Solution Architect |
| R-13 | Complete review with **Technical Architecture Reviewer** (already scheduled) — focus on infrastructure and policy-as-code design | Solution Architect |
| R-14 | Track **SLZ GitHub repository archival** — migrate primary documentation references to Microsoft Learn / Sovereign Public Cloud; consider forking Terraform baseline | Solution Architect |

### 9.4 Stakeholder Engagement Plan

| Stakeholder (Role) | Purpose | Priority |
|---|---|---|
| Cantonal Health Regulator | Validate cantonal regulatory obligations; understand approval pathway | High |
| Hospital Digital Transformation Lead | Validate hospital-side requirements; regulatory implementation posture | High |
| Balgrist Klinik (technology-forward reference clinic) | Real-world requirement validation; ORX robotic surgical suite as reference context | High |
| Healthcare Industry Expert (Microsoft) | Internal domain review; Thursday meeting executive summary | Medium |
| Programme Mentor | Programme-level review; complementary perspective | Medium |
| Technical Architecture Reviewer | Infrastructure and IaC review | Medium |

---

## 10. Traceability Matrix

This matrix links key requirements and decisions to their sources in the review session transcript and artefacts.

| Req / Decision ID | Requirement / Decision | Control Dimension | Architecture Element | Primary Source | Status |
|---|---|---|---|---|---|
| TM-01 | Data minimisation: capacity-only processing, no PHI in primary tier | Compliance / Privacy | Fabric data layer; agent data contracts | Transcript ~3:39, ~8:50; nDSG Art. 6 | ✅ Decided |
| TM-02 | AHV number treated as sensitive PID; access restricted by RBAC | Compliance / Security | Entra ID RBAC; API access layer | Transcript ~22:59, ~24:03; nDSG | ⚠️ Decided, not implemented |
| TM-03 | Patient-data linkage occurs only at endpoint, delegated to core systems | Architecture | Integration boundary / API gateway | Transcript ~25:32, ~25:48 | ✅ Decided |
| TM-04 | Internal running numbers used for capacity-oriented processes (pseudonymisation) | Compliance / Privacy | Agent data contracts; Fabric schema | Transcript ~24:03 | ⚠️ Decided, not implemented |
| TM-05 | SLZ adopted as Azure infrastructure baseline; Swissmedic deployment as reference | Architecture | Azure Landing Zone; Terraform | Transcript ~31:46, ~35:30; SLZ Learn docs | ⚠️ Decided, not integrated |
| TM-06 | SLZ Level selection: Level 3 (Data Residency + Global Services + Encryption at Rest) recommended as minimum for health-adjacent data | Architecture / Compliance | Azure Policy; SLZ controls | Transcript ~37:04; SLZ Learn docs | ❓ Not yet decided |
| TM-07 | Hybrid architecture required for 24/7 hospital availability without hyperscaler connectivity | Architecture / Reliability | Azure Local / edge compute | Transcript ~39:19; NEW-01 | ❌ Not yet designed |
| TM-08 | Regulatory framework is two-layer: national legislation + cantonal implementation governance | Compliance | Compliance control taxonomy | Transcript ~4:52, ~11:27 | ⚠️ Understood, not yet formalised |
| TM-09 | Cantonal regulations need verification (may add obligations above nDSG/KVG) | Compliance | Compliance control taxonomy | Transcript ~11:04; follow-up TM-08 | ❌ Not yet verified |
| TM-10 | M365 integration is optional (not mandatory) — hospital M365 presence not guaranteed | Architecture | UI layer; connector design | Transcript ~14:38 | ✅ Decided |
| TM-11 | Agent design: Orchestrator + Demand Forecasting + Discharge Coordination + Bed Management + Integration Flow | Architecture | Agent orchestration layer | Transcript ~15:30; GitHub repo | ⚠️ In review |
| TM-12 | Demand Forecasting agent may be event-driven model rather than LLM agent | Architecture | Agent design | Transcript ~16:15 | ⚠️ In review |
| TM-13 | Azure Foundry not available in required regions — dependency constraint | Architecture | Agent hosting platform | Transcript ~15:08 | ⚠️ Acknowledged, not resolved |
| TM-14 | Full traceability via Control IDs / labels; GitHub as evidence repository | Governance | Compliance toolchain; IaC labels | Transcript ~12:41, ~13:37 | ✅ In progress |
| TM-15 | Policy-as-code target: controls deployed idempotently with rollback capability | Architecture / Governance | Azure Policy; IaC pipeline | Transcript ~13:29 | ⚠️ Planned |
| TM-16 | Secondary re-identification risk via quasi-identifiers (age, gender, diagnosis category) | Compliance / Privacy | Data minimisation policy; agent data contracts | Transcript ~27:16 | ❌ Not addressed |
| TM-17 | KYC / patient admission identification gap exists in current Swiss hospital process | Compliance | Out-of-scope (integration boundary) | Transcript ~21:33 | ❓ Scope TBD |
| TM-18 | Confidential computing applicability assessment needed | Architecture | Evaluation only | Transcript ~29:18 | ❓ Not evaluated |
| TM-19 | SLZ GitHub repo archival planned H1 2026 | Governance | Documentation / toolchain | SLZ GitHub README | ⚠️ Action required |
| TM-20 | Public GitHub under MIT licence — anonymisation discipline required | Governance | Documentation process | Transcript ~41:47 | ✅ Enforced |

---

## Appendix A — Glossary

| Term | Definition |
|---|---|
| AHV / AVS | Alters- und Hinterlassenenversicherung — Swiss old-age and survivors' insurance; the AHV number is Switzerland's national social security identifier |
| EPD / EPR | Elektronisches Patientendossier / Electronic Patient Record — Swiss federal framework for interoperable patient records, currently in early national rollout |
| KVG | Krankenversicherungsgesetz — Swiss Federal Health Insurance Act |
| nDSG | Datenschutzgesetz (new) — Swiss Federal Data Protection Act (revised, in force since September 2023) |
| PHI | Protected Health Information — personally identifiable health data |
| PID | Personal Identifier |
| SaMD | Software as a Medical Device — Swissmedic regulatory classification for clinical software |
| SLZ | Sovereign Landing Zone — Microsoft Azure reference architecture for sovereign/regulated workloads |
| Spitex | Spital-externe Krankenpflege — Swiss community home care service |
| Swissmedic | Swiss Agency for Therapeutic Products (equivalent to FDA / EMA) |
| Zero Trust | Security model that eliminates implicit trust; requires continuous verification regardless of network location |

---

## Appendix B — Review Session Metadata

| Field | Value |
|---|---|
| Recording date | 2026-06-09 |
| Recording duration | 43 minutes 43 seconds |
| Languages | German (primary), English (partial) |
| Transcript quality | Partially degraded (AI auto-transcription with phonetic errors) |
| Participants | Solution Architect, CTO Mentor |
| Document produced | 2026-06-09 |

*Transcript quality note: Several passages in the raw transcript contain phonetically transcribed errors (mixed-language STT artefacts). All findings in this document are based on contextually interpretable passages. Any finding relying on a single ambiguous passage has been flagged with ❓ in the traceability matrix and should be validated with the participants.*

---

End of document.
