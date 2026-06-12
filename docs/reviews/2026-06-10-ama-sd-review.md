# AMA Solution Design Review - 2026-06-10

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-12 |
| **Author** | AI-assisted review synthesis |
| **Status** | Reviewed |
| **Previous Version** | 0.0.0 (new review baseline) |

---

## 1. Executive Summary

The AMA Review Session confirms a strong and coherent domain-driven solution foundation, centred on:
- The "Hospitalisation-as-Unit" (Episode-based control model)
- A Minimal-Invasive Data Architecture approach

These principles align well with Zero Trust, Data Minimisation (DSG), and scalable optimisation patterns.

However, the review highlights several critical gaps and risks:

- Lack of formalised governance and control mapping (policy-as-code, enforceability unclear)
- Missing data governance and taxonomy ownership model (critical for metadata-driven matching)
- Unclear tenant, landing zone and environment separation strategy
- No explicit compliance traceability (DSG / cantonal requirements)
- Dependency risks on metadata quality without defined control mechanisms
- Ambiguity between abstract governance principles and enforceable architecture

Overall:
> The concept is strategically strong, but operationalisation and governance maturity are insufficient for a production-ready Swiss public sector deployment.

---

## 2. Context Overview

### Inputs
- AMA Review Session transcript (primary findings source)
- SwissHospitalCapacityPlatform (baseline architecture - assumed)
- Supporting documentation (implicit assumptions)

### Core Solution Pattern

Hospital Operations abstraction model:
- Control unit = Hospitalisation Episode (not patient)
- Matching:
  - Demand (episode metadata)
  - Supply (bed/station metadata)

Minimal-Invasive Data Architecture:
- No PII processing on planning platform
- Pseudonymised identifiers only
- Separation:
  - KIS -> identity layer
  - Planning platform -> metadata layer

### Intended Benefits
- Reduced regulatory burden (DSG)
- Algorithmic optimisation (forecasting, matching)
- Standardised capacity management

---

## 3. Key Findings from Review Session

### 3.1 Domain and Data Model
- Strong consensus on:
  - Decoupling identity from planning
  - Episode as control abstraction
- Implicit assumption:
  - Metadata sufficiently describes clinical needs

### 3.2 Architecture Thinking
- Implicit support for:
  - Platform-based architecture (central planning layer)
  - Integration with hospital systems (KIS)

### 3.3 Compliance Strategy
- Clear direction:
  - Avoid processing of PII
  - Use pseudonymisation
- Assumption:
  - This significantly reduces compliance complexity

### 3.4 Critical Hypothesis Identified

> "System quality depends heavily on metadata completeness and structure"

-> This is a single-point-of-failure risk not yet mitigated.

---

## 4. Deviation Analysis

| Area | Observation | Deviation |
| ---- | ----------- | --------- |
| Governance | No defined policy framework or enforcement mechanism | Misaligned with CAF (governance implementation missing) |
| Architecture | No explicit landing zone / environment segregation model | Deviates from Azure Landing Zone best practices |
| Security | Zero Trust concept implied but not defined | Missing identity, device, network, data-layer enforcement |
| Data Governance | No ownership or stewardship model for metadata | Critical gap vs Well-Architected Data pillar |
| Compliance | Relies on "no PII = low risk" assumption | Oversimplification of DSG (context still sensitive) |
| Operations | No observability or monitoring model defined | Not aligned with reliability/operational excellence |

---

## 5. New and Emerging Requirements

### 5.1 Data Governance

- Metadata taxonomy standardisation (mandatory)
- Data quality controls:
  - Validation rules
  - Completeness thresholds
- Ownership model:
  - Data Stewards per hospital / canton

### 5.2 Architecture

- Clear separation:
  - Dev / Test / Prod environments
- Multi-tenancy model definition:
  - National vs cantonal vs hospital segmentation

### 5.3 Security and Identity

- Pseudonymisation service design
- Identity boundary between:
  - KIS and planning platform
- Access control:
  - Role-based and context-aware

### 5.4 Compliance

- Formal classification:
  - Even pseudonymised health data = sensitive
- Audit and traceability requirements

### 5.5 Matching Engine

- Explainability requirement:
  - Why was a bed assigned?
- Override workflows (human-in-loop)

---

## 6. Risk Assessment

### 6.1 Critical Risks

| Risk | Impact | Likelihood | Comment |
| ---- | ------ | ---------- | ------- |
| Poor metadata quality | High | High | Leads to wrong bed allocation |
| Undefined governance | High | Medium | Inconsistent implementation across cantons |
| Oversimplified compliance assumption | High | Medium | Regulatory exposure |
| Missing tenant isolation | High | Medium | Data leakage risk |
| No auditability | High | Medium | Non-compliant in public sector |

### 6.2 Technical Risks

- Integration dependencies on KIS systems
- Latency in real-time matching scenarios
- Inconsistent data schemas across providers

### 6.3 Operational Risks

- Lack of ownership (no accountable entity)
- No defined SLA / service reliability model

---

## 7. Architecture and Governance Alignment Review

### Observed Gap

| Governance Layer | Technical Implementation | Alignment |
| ---------------- | ------------------------ | --------- |
| Data minimisation | Assumed, not enforced | Weak |
| Pseudonymisation | Conceptual only | Weak |
| Zero Trust | Not defined in architecture | Missing |
| Policy enforcement | Not implemented (no Azure Policy / DLP) | Missing |
| Tenant governance | Not defined | Critical gap |

### Key Issue

> Governance exists as principles, not as executable controls.

### Required Evolution

Move from:
- Conceptual governance

To:
- Policy-as-Code
- Automated enforcement (Azure Policy, Purview, Defender)

---

## 8. Compliance Evaluation (Swiss Context)

### Valid Strengths

- Data minimisation aligned with DSG
- Separation of identity from operational layer
- Reduction of PII exposure

### Critical Gaps

- Pseudonymised data still considered sensitive in healthcare context
- No defined:
  - Data residency enforcement (CH regions)
  - Cross-cantonal data sharing rules
  - Consent / legal basis handling

### Required Controls

- Data classification (health data tier)
- Encryption:
  - At rest (CMK)
  - In transit
- Logging:
  - Access logs
  - Data access justification
- Auditability:
  - End-to-end trace of allocation decisions

---

## 9. Recommendations and Next Steps

### 9.1 Immediate (High Priority)

- Define data governance model
  - Roles (Data Owner, Steward, Custodian)
- Establish metadata standard
- Define tenant and landing zone architecture
- Introduce policy-as-code framework
  - Azure Policy
  - DLP policies

### 9.2 Short Term

- Design pseudonymisation service
- Define Zero Trust architecture:
  - Identity
  - Network
  - Data
- Implement audit logging strategy

### 9.3 Mid Term

- Introduce matching explainability layer
- Define operational model
  - SLA, ownership, support
- Align with Swiss regulatory bodies (BAG / cantonal authorities)

---

## 10. Traceability Matrix

| Requirement | Control | Architecture Decision | Source |
| ----------- | ------- | --------------------- | ------ |
| Data minimisation | Pseudonymisation | No PII in planning system | Transcript |
| Episode-based planning | Metadata abstraction | Hospitalisation entity model | Transcript |
| Matching optimisation | Metadata model | Demand vs supply comparison engine | Transcript |
| Compliance simplification | Separation of concerns | KIS vs platform separation | Transcript |
| Data quality dependency | Validation controls (missing) | Not implemented yet | Transcript (critical hypothesis) |
| Governance enforcement | Policy-as-code (missing) | Not defined | Gap analysis |
| Tenant separation | Multi-tenant architecture | Not defined | Gap analysis |
| Auditability | Logging and tracing | Not defined | Gap analysis |

---

## Final Assessment

The solution represents a high-potential, modern platform pattern for healthcare capacity optimisation.

However:

> It is currently conceptually strong but operationally incomplete, with significant risks in governance, compliance, and data quality control.

A transition towards enforceable governance, structured data control, and Swiss-compliant architecture is mandatory before progressing further.
