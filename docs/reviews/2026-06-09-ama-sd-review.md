# AMA Solution Design Review
## SwissHospitalCapacityPlatform
### Review Date: 2026-06-09 | Status: Draft v1.0

---

## 1. Executive Summary

This document provides a structured post-review analysis of the AMA (Azure Mastery Architect) Solution Design Review session conducted on 9 June 2026, evaluating the **SwissHospitalCapacityPlatform** — an AI-powered patient flow and hospital capacity management platform for Swiss cantonal hospital providers.

The solution demonstrates strong foundational thinking: GA-only service constraints, a deliberate human-in-the-loop design, and an emerging data minimization principle are architecturally sound and appropriate for the Swiss public sector healthcare context. However, several critical gaps were surfaced during the review.

### Overall Assessment: Conditionally Sound — Critical Actions Required

| Dimension | Status | Notes |
|-----------|--------|-------|
| Product Requirements (PRD) | Partially complete | Core functional scope defined; emerging requirements not yet captured |
| Solution Design | Partially complete | Agent decomposition largely sound; integration workflow misclassified |
| Architecture | In progress | Hosting, data, and event patterns reasonable; Zero Trust not detailed |
| Compliance | Gaps identified | Data residency confirmed; legal mapping, PHI controls, tenant hardening incomplete |

**Top 5 Critical Items:**
1. AI model availability for Switzerland North/West regions is unconfirmed — a potential architecture blocker
2. PHI minimization design principle adopted but formal risk assessment is outstanding
3. Canton-specific legal applicability mapping is not yet formalized
4. Abstract governance framework (top-down) not yet bridged to technical IaC policy implementation (bottom-up)
5. Forecasting pipeline design is deferred but is the core value driver of the solution

---

## 2. Context Overview

### 2.1 Project Context

| Attribute | Detail |
|-----------|--------|
| Project | SwissHospitalCapacityPlatform |
| Purpose | AMA Certification case study — AI-powered patient flow for Swiss cantonal hospitals |
| Domain | Public sector healthcare, Switzerland |
| Repository | [urruegg/SwissHospitalCapacityPlatform](https://github.com/urruegg/SwissHospitalCapacityPlatform) |
| Technology constraint | GA Azure services only; no preview features |
| Data residency | Switzerland North or Switzerland West regions (hard requirement) |

### 2.2 Review Session Details

| Attribute | Detail |
|-----------|--------|
| Date | 2026-06-09, 07:06 AM |
| Duration | ~41 minutes |
| Participants | Solution Owner (SO), Senior Architect Reviewer (SAR) |
| External reference | Canton/CSA Reference (CCR) — CSA from Compton Argentiero, running a master thesis on Azure Cloud Adoption Framework and landing zone design for cantonal services |

> **Note on anonymization:** Participant names have been replaced with role titles throughout this document. "Solution Owner (SO)" refers to the certification candidate; "Senior Architect Reviewer (SAR)" refers to the review mentor; "Canton/CSA Reference (CCR)" refers to the external CSA whose prior review inputs were cited by the SO.

### 2.3 Solution Scope as Confirmed in Session

**MVP Features (In-scope):**
- Demand forecasting agent
- Discharge coordination agent
- Bed management co-pilot agent

**Explicitly Excluded from MVP:**
- External integration flows (no external demand integration requirement at this stage)
- Ontology model layer (not GA; deferred to future horizon)

**Non-functional constraints (confirmed):**
- All Azure services must be Generally Available
- All data and AI inference restricted to Switzerland North or West
- Human-in-the-loop mandatory; advisory-only AI responses
- Minimum invasiveness within hospital tenant environments

### 2.4 Baseline Architecture (per transcript and repository)

The solution is structured in three tiers:

```text
┌───────────────────────────────────────────────────────────────┐
│               React Frontend (Web Application)                │
│     Site deployment within existing solutions OR standalone   │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                    Orchestration Tier                          │
│   Orchestrator Agent — intent classification, execution plan, │
│   agent dispatch                                              │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                     Domain Agent Tier                          │
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │   Demand     │  │   Discharge      │  │  Bed Mgmt      │  │
│  │  Forecasting │  │  Coordination    │  │  Co-pilot      │  │
│  └──────────────┘  └──────────────────┘  └────────────────┘  │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                     Governance Tier                            │
│  Data Quality & Semantic Agents | Compliance/Safety Agent     │
│  Audit Agent                                                  │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                     Service Layer                              │
│  Cosmos DB (runtime) | Service Bus + Logic Apps (events)      │
│  Azure Foundry (model control plane)                          │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│          Data Platform — Microsoft Fabric / OneLake           │
│  Ingestion → Data Quality → Semantic Model → Agent Input      │
│  [ PHI fields: isolated, classified, partitioned ]            │
│  Event patterns: Logic Apps + Service Bus + Event Router      │
└───────────────────────────────────────────────────────────────┘
```

---

## 3. Key Findings from Review Session

### 3.1 Decisions Confirmed or Reached

| ID | Decision | Rationale | Source |
|----|----------|-----------|--------|
| D-01 | Integration workflow (Agent 5) reclassified as domain microservice | No AI intelligence required; deterministic routing via Service Bus; "not doing agents for the sake of agents" | Transcript: SAR challenge (09:34), SO agreement (10:12–10:31) |
| D-02 | Agent reasoning style: deterministic / controllable; no extended reasoning loop | Latency constraint (~4s target), predictability in clinical context, human reviewability | Transcript: SO (13:20–13:34), SAR confirmation (14:39–14:59) |
| D-03 | PHI minimization: platform receives only anonymized / minimal capacity data | Simplifies compliance, reduces security review burden for hospitals, lowers sales barrier | Transcript: SAR (23:01–24:08), SO adoption (24:44–25:16) |
| D-04 | Runtime PHI integration by hospital's own systems at display time only | Hospital retains control of sensitive data; platform never persists identifiable information | Transcript: SAR (25:49–26:09), SO (26:19–26:41) |
| D-05 | Hosting: App Service or Azure Container Apps (ACA); AKS not appropriate | Single-tenant, low-complexity scenario; AKS only justified for self-hosted multi-tenant distribution | Transcript: SAR/SO (30:59–31:43) |
| D-06 | Frontend: React web application (site or standalone deployment) | Minimally invasive; M365 Copilot availability in hospitals uncertain | Transcript: SO (04:46–05:13) |
| D-07 | Model selection: cost- and efficiency-driven; OpenAI or Foundry models both candidates | No hard requirement; evaluation needed once CH-region availability confirmed | Transcript: SAR/SO (33:24–33:48) |
| D-08 | Data platform: Microsoft Fabric / OneLake; runtime state: Cosmos DB | Managed services; no custom vector database | Transcript: SO (22:58), confirmed |
| D-09 | Ontology model deferred to future horizon | Not GA | Transcript: SO (18:35–18:45) |
| D-10 | All deterministic components to be reviewed for agent vs. traditional code | Deterministic code is faster, cheaper, more predictable; not every component needs an agent | Transcript: SAR (39:46–39:54), SO (39:48–39:54) |

### 3.2 Key Assumptions

| ID | Assumption | Risk if Incorrect |
|----|------------|-------------------|
| A-01 | Suitable AI models are available in Switzerland North/West at acceptable latency/capacity | Architecture redesign required; data residency compliance risk if models route outside CH |
| A-02 | Hospital source systems can filter/anonymize data before sending to platform | PHI may arrive despite design intent; requires defensive validation layer |
| A-03 | Hospitals will accept React-based deployment without M365 Copilot dependency | Integration strategy may need revision for M365-enabled hospitals |
| A-04 | Data already exists in Fabric/OneLake for MVP start | MVP scope blocked if no pre-existing data in Fabric |
| A-05 | Usage baseline: 100 concurrent users, 24 forecast runs/day, ~185 data events | Real usage may be significantly higher, especially with agentic consumption patterns |
| A-06 | Single-tenant deployment for MVP; multi-tenant is a future-state concern | Multi-tenant architectural requirements should influence MVP design early to avoid rework |

### 3.3 Open Items

| ID | Item | Owner | Status |
|----|------|-------|--------|
| O-01 | AI model availability list for Switzerland North/West regions | SAR | Follow-up committed in session |
| O-02 | PHI minimization risk assessment | SO | Action committed in session |
| O-03 | Forecasting pipeline design (Azure ML vs. Fabric ML) | SO | Deferred; acknowledged as critical |
| O-04 | Canton-specific legal applicability mapping | SO + CCR | Raised; not yet actioned |
| O-05 | Agent vs. tool formal classification criterion | SO | Philosophical boundary raised; needs documentation |
| O-06 | PTU (Provisioned Throughput Unit) deployment feasibility in Switzerland | Open | Regional availability unclear |

---

## 4. Deviation Analysis

### 4.1 Deviations from Microsoft Cloud Adoption Framework (CAF)

| ID | Area | CAF Best Practice | Observed State | Severity |
|----|------|-------------------|----------------|----------|
| CAF-01 | Landing Zone Design | Separate platform, management, identity, and connectivity landing zones; workload landing zones per environment | Engineering/test/production tenant separation discussed but landing zone topology not detailed | **Medium** |
| CAF-02 | Management Group Hierarchy | Tenant Root → Management Groups → Subscriptions → Resource Groups with policy inheritance | Not explicitly validated in session; cross-tenant access mentioned without hierarchy design | **High** |
| CAF-03 | Policy-as-Code | Azure Policy deployed from management group scope; aligned to CAF guardrails | GitHub IaC approach confirmed but canton-specific policy inheritance from management group not clarified | **Medium** |
| CAF-04 | Governance Registration | Governance baseline documented and controls registered before workload onboarding | Raised as requirement by CCR; not yet implemented | **Medium** |
| CAF-05 | RBAC Design | Documented role assignments per workload, persona, and environment | Persona roles identified (clinical lead, care coordinator, capacity manager) but RBAC design not formalized | **Medium** |
| CAF-06 | Cost Management | Cost allocation, tagging strategy, and budget alerts per workload | Initial usage estimates exist; no cost governance structure discussed | **Low** |

### 4.2 Deviations from Azure Well-Architected Framework (WAF)

| ID | Pillar | WAF Best Practice | Observed State | Severity |
|----|--------|-------------------|----------------|----------|
| WAF-01 | Reliability | SLA/SLO targets, failure mode analysis, recovery targets (RTO/RPO) per component | Latency target (~4s) defined; SLA/SLO and failover strategy not discussed | **Medium** |
| WAF-02 | Security | Zero Trust segmentation, private endpoints, secrets management, threat modelling | Referenced implicitly; no detailed security architecture discussed | **High** |
| WAF-03 | Cost Optimisation | Rightsizing, reserved capacity, PTU evaluation for AI workloads | Usage estimates exist; PTU evaluation deferred; model not selected | **Medium** |
| WAF-04 | Operational Excellence | Monitoring, alerting, observability, incident response, CI/CD validation | CI/CD confirmed in place; monitoring and alerting not discussed | **Medium** |
| WAF-05 | Performance Efficiency | Latency budgets per service boundary; load testing baseline | 4s aggregate target stated; per-service breakdown absent | **Low** |
| WAF-06 | Sustainability | Carbon-aware scheduling, efficient resource utilization | Not discussed | **Low** |

### 4.3 Deviations from Zero Trust Principles

| ID | Principle | Expected Control | Observed State | Severity |
|----|-----------|-----------------|----------------|----------|
| ZT-01 | Verify Explicitly | Authentication and authorisation at every service boundary, including agent-to-agent calls | Agent-to-agent authentication not addressed | **High** |
| ZT-02 | Use Least Privilege | Minimal permissions per service identity; managed identities throughout | Cross-tenant access restrictions mentioned; per-agent managed identity strategy not defined | **Medium** |
| ZT-03 | Assume Breach | Network segmentation; private endpoints; lateral movement controls | PHI isolation in Fabric discussed; network architecture not detailed | **Medium** |
| ZT-04 | Data Classification | Classify and label data at ingestion; enforce controls based on classification | PHI isolation/partitioning mentioned for Fabric; formal classification schema not defined | **Medium** |
| ZT-05 | Device Health | Conditional Access for user-facing endpoints | Not discussed | **Low** |

### 4.4 Governance Framework vs. Technical Implementation Conflict

A structural tension was identified during the session and requires explicit resolution.

The **CCR (Canton/CSA Reference)** has produced an abstract, intentionally top-down governance framework for cantonal cloud adoption — this defines what controls must exist but not how they are implemented technically.

The **SO** is building from the bottom up: GitHub-first, infrastructure-as-code, policy-as-code, with a CI/CD-gated deployment pipeline.

**Gap:** No explicit bridge exists between these two layers. Abstract governance controls (cantonal legal requirements, data sovereignty mandates, audit obligations) are not yet translated into specific Azure Policy definitions, IaC templates, or automated compliance checks.

> *"Javi from him was more on a framework that is intentionally based as abstract, not close. My part was more about I want to do more policy GitHub infrastructure-based first approach means I come from bottom up and he comes from top down." — SO, Transcript 37:07*

This bottom-up / top-down gap is a governance risk: the solution may be technically compliant in implementation but unable to demonstrate traceability to the required cantonal framework.

---

## 5. New & Emerging Requirements

The following requirements were not explicitly part of the original PRD but emerged from the session discussion. They must be formally captured, prioritised, and incorporated.

| ID | Emerging Requirement | Category | Priority | Source |
|----|---------------------|----------|----------|--------|
| ER-01 | **Data minimization as architectural constraint**: the system must receive only the minimum data required for capacity planning; PHI must not be ingested by default | Compliance / Architecture | **Critical** | SAR/SO discussion (23:01–25:16) |
| ER-02 | **Runtime PHI integration pattern**: hospital systems must be able to inject patient-identifiable context at display time without persisting it in the platform | Architecture / Privacy | **High** | SAR (25:49–26:09) |
| ER-03 | **Canton-specific legal applicability mapping**: each canton's legal obligations must map to specific technical controls with evidence traceability | Compliance | **High** | SO referencing CCR (37:22–37:38) |
| ER-04 | **Cross-tenant access restriction controls**: engineering, test, and production tenants must have explicit, auditable cross-tenant access restrictions | Security / Governance | **High** | SO (37:38–37:50) |
| ER-05 | **AI model availability validation**: confirm which models are available in Switzerland North/West before finalising architecture; design model-agnostic inference layer | Architecture | **Critical** | SAR follow-up (15:32–16:00) |
| ER-06 | **Determinism constraint for agent design**: all agents must follow controllable, deterministic patterns; autonomous reasoning loops are prohibited | Architecture / Safety | **High** | SAR/SO agreement (13:20–14:59) |
| ER-07 | **Agent vs. microservice classification criterion**: a formal decision criterion must document when a component qualifies as an agent vs. a traditional microservice | Architecture / Documentation | **Medium** | Discussion on Agent 5 (09:07–10:31) |
| ER-08 | **Future-state multi-tenant scalability consideration**: MVP architecture must not foreclose multi-tenant scaling; minimal invasiveness principle must be applied from the start | Architecture | **Medium** | SAR (27:52–28:13), SO summary (38:41–39:11) |
| ER-09 | **Governance registration before production**: all controls must be formally registered and traceable to the governance framework before any production deployment | Governance | **High** | SO referencing CCR (36:52–37:16) |
| ER-10 | **Forecasting pipeline design required**: a concrete demand forecasting pipeline (Azure ML vs. Fabric ML) must be designed; this is the core value driver | Architecture / Product | **Critical** | SAR challenge (21:22–21:28), SO acknowledgement |

---

## 6. Risk Assessment

### 6.1 Risk Register

| ID | Category | Description | Likelihood | Impact | Severity | Recommended Mitigation |
|----|----------|-------------|-----------|--------|----------|------------------------|
| R-01 | Technical | AI models for the required use case are not available in Switzerland North/West, forcing data routing outside Switzerland | **High** | Critical | **Critical** | Confirm availability list (O-01); design model-agnostic inference layer with regional fallback strategy |
| R-02 | Compliance | PHI arrives in the platform despite anonymization design, creating undisclosed personal data handling | **Medium** | Critical | **Critical** | Formal PHI risk assessment (O-02); defensive PHI detection at Fabric ingestion boundary; contract obligations on source systems |
| R-03 | Architecture | Forecasting pipeline absent from MVP; core value proposition unvalidated and may require significant rework | **High** | High | **High** | Prioritise forecasting pipeline design; do not defer beyond Sprint 1 |
| R-04 | Compliance | Canton-specific legal applicability mapping not formalized; regulatory evidence gap at audit time | **Medium** | High | **High** | Develop control-to-regulation matrix with CCR; validate before production |
| R-05 | Governance | Abstract governance framework (CCR) not translated to technical policy-as-code; traceability chain broken | **Medium** | High | **High** | Map each abstract control to an Azure Policy definition or IaC control; document linkage |
| R-06 | Security | Agent-to-agent authentication undefined; identity chain between services not established | **Medium** | High | **High** | Define managed identity strategy per agent and service; document auth flow diagrams |
| R-07 | Operational | Concurrent usage estimate (100) may be significantly underestimated if agentic consumption patterns emerge | **Medium** | Medium | **Medium** | Load test with buffer; evaluate PTU capacity for AI workloads once models confirmed |
| R-08 | Architecture | Ontology model deferred but may be required for semantic interoperability across canton-specific data schemas | **Low** | Medium | **Medium** | Document as technical debt; plan Horizon 2 scope; design Fabric semantic model to accommodate future ontology |
| R-09 | Security | Cross-tenant access restriction gaps could allow data leakage between engineering, test, and production environments | **Low** | High | **Medium** | Implement and independently audit tenant isolation controls; include in CI/CD pipeline gate |
| R-10 | Architecture | App Service vs. ACA decision not finalized; potential containerization rework later | **Low** | Low | **Low** | Document decision; SAR preference for ACA noted; formalise before infrastructure deployment |

---

## 7. Architecture & Governance Alignment Review

### 7.1 Agent Classification Assessment

The SAR raised a key design principle: *"Not doing agents for the sake of doing agents."* The following table applies this principle to the defined agent set.

| Component | Original Classification | Recommended Classification | Rationale |
|-----------|------------------------|---------------------------|-----------|
| Demand Forecasting Agent | Agent | **Agent** | Requires model inference over time-series data; contextual reasoning appropriate |
| Discharge Coordination Agent | Agent | **Agent** | Coordination logic benefits from contextual reasoning over multi-factor inputs |
| Bed Management Co-pilot | Agent | **Agent** | Advisory recommendation pattern is the correct use case for an agent |
| Integration Workflow (Agent 5) | Agent | **Domain Microservice** | Deterministic routing via Service Bus; no AI reasoning required; confirmed in session |
| Data Quality & Semantic Agent | Agent | **Agent or deterministic service TBD** | Depends on schema variability across hospital sources; evaluate case-by-case |
| Compliance / Safety Agent | Agent | **Agent** | Policy reasoning and audit log generation benefit from AI pattern matching |
| Audit Agent | Agent | **Agent** | Appropriate for immutable audit trail generation and anomaly detection |

### 7.2 Data Flow Assessment

The event-driven architecture is well-suited to the requirements. Key observations:

- **Logic Apps + Service Bus** as the integration backbone is appropriate for asynchronous event routing
- **Fabric / OneLake** as the data platform is correct for the scale and managed service requirement
- **Cosmos DB** for runtime state is appropriate (low-latency, document model fits agent state)
- **Gap**: The transition from batch data (daily master data updates) to real-time event streams is acknowledged but the dual-mode design (batch + event) introduces complexity not yet fully accounted for in the service design

### 7.3 Governance Alignment Matrix

| Governance Dimension | Abstract Level (CCR Framework) | Technical Implementation | Alignment Status |
|---------------------|-------------------------------|--------------------------|-----------------|
| Legal applicability mapping | Canton-specific mapping required | Not yet implemented | **Gap** |
| Data residency | Switzerland only | CH North/West hard constraint in design | **Aligned** |
| Tenant isolation | Engineering / Test / Production | Referenced; topology not designed | **Partial** |
| Cross-tenant access restriction | Mandatory | Mentioned; not implemented | **Gap** |
| Policy enforcement | Governance controls mandatory | GitHub IaC planned; cantonal policies not codified | **Partial** |
| Traceability (Req → Control → Evidence) | Required by framework | Mentioned in agent design (PRD ↔ compliance control mapping); not complete | **Partial** |
| Governance registration | Required before deployment | Identified as requirement; not actioned | **Gap** |
| RBAC per persona | Required | Personas identified; RBAC not designed | **Gap** |

### 7.4 CI/CD and Infrastructure-as-Code Assessment

The SO confirmed that infrastructure-as-code is deployed, CI/CD is implemented, and the pipeline is gated. This is a significant positive. Outstanding items:

- Confirm that Azure Policy definitions for cantonal compliance controls are part of the IaC repository
- Confirm that compliance gate checks are included in the CI/CD pipeline (not just deployment gates)
- Confirm that the deployment pipeline distinguishes between engineering, test, and production tenants

---

## 8. Compliance Evaluation — Swiss Public Sector Context

### 8.1 Applicable Regulatory Framework

| Regulation | Level | Applicability | Status |
|------------|-------|---------------|--------|
| **nDSG** (Revised Federal Data Protection Act, in force Sept 2023) | Federal | Mandatory — governs all personal data processing including health data | Not mapped to controls |
| **KVG / LAMal** (Federal Health Insurance Act) | Federal | Governs hospital operations, data standards, patient rights | Not mapped |
| **Canton-specific health data regulations** | Cantonal | Varies per canton; legal applicability mapping mandatory | Gap identified (CCR) |
| **ISB / Federal IT governance standards** | Federal | Applicable to cantonal IT systems using federal infrastructure | Not discussed |
| **DSRV** (Data Security Regulation / Verordnung über die Informationssicherheit) | Federal | Technical and organisational security measures | Not discussed |
| **GDPR** (informative) | EU | Not directly applicable in Switzerland; nDSG is the Swiss equivalent; GDPR informs best practice | Informative only |

### 8.2 Data Residency Assessment

| Item | Status | Action Required |
|------|--------|----------------|
| Compute and storage restricted to CH North/West | Confirmed in design | Validate per service in Azure compliance documentation |
| Azure Foundry model inference stays within CH | **Unconfirmed** | Validate — global model routing may occur depending on model availability |
| Microsoft Fabric data residency in CH regions | **Unconfirmed** | Validate — Fabric workspaces must be explicitly provisioned in CH regions |
| Cosmos DB data residency | Implied by regional constraint | Confirm geo-replication is disabled or CH-only |
| Service Bus / Logic Apps data residency | Implied | Confirm no cross-region message routing |

### 8.3 PHI Handling Assessment

The session produced a pivotal design decision: **the platform should receive only anonymized or minimal capacity metadata, not PHI.** This is architecturally sound from a compliance perspective and significantly reduces the solution's regulatory surface area. However, formalisation is required:

| Requirement | Status | Notes |
|------------|--------|-------|
| Formal definition of "minimum required data" | Missing | Must be documented as a data schema contract |
| Source system contractual obligations | Missing | Hospitals must contractually commit to data filtering before transmission |
| Defensive PHI detection at ingestion boundary | Missing | Platform must validate incoming data; cannot rely solely on source-side filtering |
| Runtime PHI injection security design | Missing | Token-based, in-browser-only, encrypted; no server-side persistence of PHI |
| Risk assessment of anonymization trade-offs | Outstanding (O-02) | Committed action; must evaluate functional limitations introduced by anonymization |

### 8.4 Zero Trust Implementation Gaps

| Control | Requirement | Status |
|---------|-------------|--------|
| Managed identities for all services | Mandatory | Not confirmed |
| Private endpoints for all data services (Cosmos DB, Fabric, Service Bus) | Mandatory | Not discussed |
| Encryption at rest and in transit (TLS 1.2+, AES-256) | Mandatory | Not discussed |
| Conditional Access for user-facing React application | Required | Not discussed |
| Immutable audit logging for all AI recommendations | Required | Audit agent mentioned; design not detailed |
| SIEM integration (Microsoft Sentinel recommended) | Recommended | Not discussed |
| Secret management (Azure Key Vault, no hardcoded credentials) | Mandatory | Not discussed |
| Network segmentation between tiers | Required | Not discussed |

---

## 9. Recommendations & Next Steps

### 9.1 Critical / Immediate (Before Architecture Finalisation)

| ID | Recommendation | Owner | Priority |
|----|---------------|-------|----------|
| REC-01 | **Confirm AI model availability in Switzerland North/West**: obtain the confirmed model list from the SAR follow-up (O-01) and update the model selection decision. If required models are unavailable, redesign the inference layer to be model-agnostic and evaluate a regional fallback strategy. | SO (input from SAR) | **Critical** |
| REC-02 | **Conduct PHI minimization risk assessment** (O-02): document the functional trade-offs of receiving only anonymized data; define what "minimum required data" means as a formal schema contract; identify failure modes where PHI may arrive despite source-side filtering. | SO | **Critical** |
| REC-03 | **Design the forecasting pipeline** (O-03): evaluate Azure Machine Learning vs. Microsoft Fabric ML for demand forecasting; produce a data flow design and prototype; this is the core value driver of the solution and cannot remain undesigned. | SO | **Critical** |
| REC-04 | **Reclassify Integration Workflow (Agent 5) as Domain Microservice** in all documents and diagrams. Document the classification criterion used (deterministic routing, no AI reasoning required). | SO | **High** |
| REC-05 | **Formalize canton-specific legal applicability mapping** (O-04): create a matrix mapping each applicable regulation (nDSG, KVG, canton-specific health law) to specific architectural controls. Validate with CCR. | SO + CCR | **High** |

### 9.2 Near-Term (Sprint 1–2)

| ID | Recommendation | Owner | Priority |
|----|---------------|-------|----------|
| REC-06 | **Define Zero Trust implementation plan**: specify managed identities, private endpoints, network segmentation, conditional access, and secret management per service. Produce a security architecture diagram. | SO | **High** |
| REC-07 | **Design tenant separation topology**: document engineering / test / production tenant structure, subscription hierarchy, management group policy inheritance, and cross-tenant access restrictions. | SO | **High** |
| REC-08 | **Bridge abstract governance framework to IaC policy-as-code**: for each abstract control in the CCR framework, create a corresponding Azure Policy definition or IaC compliance check. Document the traceability linkage explicitly. | SO + CCR | **High** |
| REC-09 | **Define agent-to-agent authentication model**: establish a managed identity strategy per agent and service; document authentication flows between orchestrator and domain agents. | SO | **High** |
| REC-10 | **Validate Microsoft Fabric and Azure Foundry data residency** in CH regions: obtain Microsoft compliance documentation confirming that workload data stays within Switzerland for each service used. | SO | **High** |
| REC-11 | **Formalize RBAC design** per persona (clinical lead, care coordinator, capacity manager, operations lead, security auditor): document role assignments per environment and per agent/service. | SO | **Medium** |
| REC-12 | **Finalise hosting platform decision (App Service vs. ACA)**: document the decision with rationale. Note: SAR preference is ACA for back-end agent hosting given containerisation flexibility. Document future-state path to multi-tenant if AKS becomes relevant. | SO | **Medium** |

### 9.3 Governance

| ID | Recommendation | Owner | Priority |
|----|---------------|-------|----------|
| REC-13 | **Register solution in governance framework before production deployment**: ensure all controls are traceable, evidenced, and registered in the cantonal governance framework (CCR alignment). | SO | **High** |
| REC-14 | **Define data classification schema in Fabric**: formalise PHI field identification, classification labels, and partition strategy at the data platform level. Align with nDSG data categories. | SO | **High** |
| REC-15 | **Add compliance gate to CI/CD pipeline**: ensure that Azure Policy compliance checks are part of the deployment pipeline gate for all environments, not just post-deployment. | SO | **Medium** |

---

## 10. Traceability Matrix

| Requirement / Decision | Control / Design Element | Architecture Decision | Source |
|------------------------|--------------------------|----------------------|--------|
| GA-only Azure services | All services must be Generally Available; preview features prohibited | Architecture constraint in PRD and IaC | Transcript: SO (01:38, 02:58–03:00) |
| Data residency: CH North/West | All compute, storage, and AI inference within Switzerland North or West | Regional deployment constraint; IaC region parameters | Transcript: SO (04:46–05:00); PRD |
| Human-in-the-loop | AI provides recommendations only; no autonomous clinical actions; human acceptance mandatory | Agent design: propose/accept pattern; no closed-loop execution | Transcript: SO (05:29–05:42); PRD |
| Minimum invasiveness | Solution deployable without M365 Copilot dependency; site or standalone deployment | React web application with flexible deployment model | Transcript: SO (04:53–05:13); PRD |
| PHI minimization principle | Platform receives only anonymized capacity metadata; PHI not ingested by default | Data ingestion design: source-side filtering + defensive validation at Fabric intake | Transcript: SAR (23:01–24:08), SO agreement (24:44–25:16) |
| Runtime PHI injection pattern | Hospital systems inject patient-identifiable context at display time; PHI never persists in platform | Frontend design: runtime data mesh; hospital system retains PHI ownership | Transcript: SAR (25:49–26:09), SO (26:19–26:41) |
| Integration workflow as microservice | Agent 5 (integration workflow) reclassified as domain microservice | Architecture: deterministic Service Bus routing, no AI reasoning | Transcript: SAR (09:34–10:04), SO (10:12–10:31) |
| Deterministic agent pattern | Agents use input-output pattern; no extended reasoning loop; ~4s latency target | Agent design: controllable, deterministic, human-reviewable output | Transcript: SO (13:20–13:34), SAR (14:39–14:59) |
| Event-driven architecture | Asynchronous event path for data ingestion from hospital source systems | Logic Apps + Service Bus + Fabric ingestion + event router | Transcript: SO (16:23–16:51) |
| Hosting: ACA/App Service, not AKS | AKS only justified for self-hosted multi-tenant distribution model | Hosting decision: ACA preferred for back-end; App Service or ACA for front-end | Transcript: SAR (30:59–31:22), SO (31:43) |
| Canton-specific legal mapping | Each canton's regulations must map to specific controls with evidence | Compliance architecture: control matrix per regulation; IaC policy layer | Transcript: SO (37:22–37:38), CCR feedback |
| Tenant hardening | Engineering, test, production tenants with cross-tenant access restrictions | Tenant topology; Azure Policy; management group hierarchy | Transcript: SO (37:38–37:50) |
| Governance registration | All controls registered before production deployment | Governance control register; traceability documentation | Transcript: SO referencing CCR (36:52–37:16) |
| Cost-driven model selection | Model selection based on cost and efficiency; OpenAI and Foundry both candidates | Model evaluation exercise; cost benchmarking required | Transcript: SAR/SO (33:24–33:48) |
| Managed services only | No custom vector database; Cosmos DB, Fabric, Foundry used as managed services | Service architecture: no self-hosted AI infrastructure | Transcript: SAR (32:45–32:57), SO confirmation |
| Data semantic layer | Fabric semantic model on top of OneLake for agent data consumption | Data platform: curated layer → semantic model → agent input | Transcript: SO (19:53–20:01) |
| Forecast pipeline (open) | Azure ML or Fabric ML for demand forecasting; not yet designed | TBD — critical for core value proposition | Transcript: SO (20:39–20:53); O-03 open item |
| AI model availability (open) | Model selection depends on Switzerland North/West availability confirmation | Architecture constraint: model-agnostic design recommended until confirmed | Transcript: SAR (15:32–16:00); O-01 follow-up |
| PHI risk assessment (open) | Risk assessment of anonymization approach required before finalising data design | Design validation gate before Sprint 1 data architecture decisions | Transcript: SO (29:02–29:11); O-02 action |

---

*This document was produced based on the transcript of the AMA Solution Design Review Call (2026-06-09) and the baseline documentation available in the [SwissHospitalCapacityPlatform repository](https://github.com/urruegg/SwissHospitalCapacityPlatform). Participant names have been anonymised: **Solution Owner (SO)**, **Senior Architect Reviewer (SAR)**, **Canton/CSA Reference (CCR)**. Items marked **[Gap]** indicate controls or requirements not yet addressed. Items marked **[Open]** indicate unresolved questions requiring follow-up action.*
