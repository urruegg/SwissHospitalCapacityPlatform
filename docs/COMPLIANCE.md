# COMPLIANCE

| Field | Value |
| ----- | ----- |
| **Version** | 0.3.0 |
| **Date** | 2026-06-01 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | 0.2.0 (initial Swiss legal baseline with control and evidence model) |

## Purpose

Define the compliance baseline for the Swiss Hospital Capacity Platform and make
Swiss legal obligations traceable to architecture controls, delivery artifacts,
and operational evidence.

Scope of this version:
- Swiss federal privacy and health-data obligations relevant to the platform.
- Zero Trust and Responsible AI controls derived from those obligations.
- Practical evidence model for audits and release gates.

Out of scope for this version:
- Canton-specific legal analysis by canton.
- Formal legal advice.

## Regulatory Scope

Primary legal and regulatory anchors (Swiss official sources):

| Topic | Source | Why it matters for this platform |
| ----- | ----- | ----- |
| Federal Data Protection Act (FADP) | https://www.fedlex.admin.ch/eli/cc/2022/491/en | Core obligations for lawful processing of health-related personal data, data subject rights, cross-border disclosure, security, and breach handling. |
| Data Protection Ordinance (DPO) | https://www.fedlex.admin.ch/eli/cc/2022/568/en | Operational detail for technical and organisational measures, logging/traceability, and implementation expectations under FADP. |
| Federal Act on the Electronic Patient Record (EPDG) | https://www.fedlex.admin.ch/eli/cc/2017/203/de | Consent model, access rights, emergency access, identity requirements, certification duties, and mandatory logging for EPR contexts. |
| Ordinance of the FDI on EPR (EPDV-EDI) | https://www.fedlex.admin.ch/eli/cc/2017/205/de | Technical and organisational certification baselines, metadata and interoperability requirements for EPR ecosystems. |
| Federal Act on Research involving Human Beings (HRA), conditional | https://www.fedlex.admin.ch/eli/cc/2013/617/en | Applies if platform data is used for regulated research workflows; includes consent, ethics approval, safeguards, and export conditions. |
| Federal Health Insurance Act (KVG), conditional | https://www.fedlex.admin.ch/eli/cc/1995/1328_1328_1328/de | Relevant where insurer-facing data exchange, quality reporting, or statutory data-sharing duties are in scope. |

Important implementation note:
Article-level legal interpretation must be validated with legal counsel before
production deployment. This document is an engineering control baseline.

## Applicability Model

- Always in scope:
	- FADP and DPO for personal data and sensitive health data.
- In scope when EPR integration is used:
	- EPDG and EPDV-EDI controls.
- In scope for research/secondary use programs:
	- HRA controls and ethics workflow.
- In scope for insurer/statutory reimbursement or quality exchange:
	- KVG-linked data governance requirements.

## Zero Trust and Responsible AI Baseline

Zero Trust principles used in this repository:
- Verify explicitly: strong identity, least privilege, and policy-bound access.
- Use least privilege: role-scoped and time-bounded access to PHI-bearing systems.
- Assume breach: full logging, anomaly detection, and rehearsed containment.

Responsible AI principles used in this repository:
- Human oversight on clinically impactful recommendations.
- Transparency to users on AI-assisted decisions.
- Safety and performance monitoring with rollback/fallback.
- Data minimization and purpose limitation for model inputs and traces.

These principles are treated as implementation controls that support Swiss legal
obligations, especially for sensitive data handling and explainability needs.

## Control Mapping

### Compliance-to-Architecture Traceability

| Control ID | Obligation theme | Swiss legal anchor | Required platform control | Current repo alignment | Gap status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| CH-C01 | Lawfulness, purpose limitation, data minimization | FADP (principles; sensitive data) + DPO | Data processing inventory per use case, explicit purpose tags, minimised PHI fields | Directionally present in architecture narrative | Open: add machine-readable data inventory and purpose registry |
| CH-C02 | Privacy by design and default | FADP + DPO | Secure defaults, least-privilege access, deny-by-default for PHI egress | Strongly aligned via ADR decisions on PHI processing and failover deny | Partial: implement policy-as-code checks in CI |
| CH-C03 | Security and traceability | DPO + EPDG Art. 10 | End-to-end audit logs, tamper resistance, retention controls, access trail for PHI | Logging intent exists in docs | Open: define concrete log schema, retention, and evidence extraction runbook |
| CH-C04 | Data subject rights | FADP rights regime | DSR workflow: access, correction, deletion/restriction where applicable, response SLAs | Not yet operationalised | Open: create DSR process, ownership, and ticket templates |
| CH-C05 | Cross-border disclosure restrictions | FADP cross-border regime | PHI residency enforcement, transfer assessment, exception approvals, compensating controls | Strongly aligned by Swiss-only PHI processing decisions | Partial: add formal transfer-risk assessment template and legal sign-off gate |
| CH-C06 | Personal data breach notification | FADP + DPO | Incident triage for privacy events, notification decision tree, regulatory and contractual notification paths | Security/ops direction exists | Open: add privacy incident runbook with decision matrix and timers |
| CH-C07 | EPR consent and access governance | EPDG Art. 3, 7, 9 | Explicit consent capture/revocation, identity assurance, role and break-glass controls | Architecture supports gated access patterns | Open: define technical integration requirements and test cases |
| CH-C08 | EPR certification and interoperability | EPDG Art. 11-13 + EPDV-EDI | Certification boundary mapping, conformance evidence for standards/profiles | Not yet defined in detail | Open: add EPR conformance control pack and responsibility matrix |
| CH-C09 | Research use governance (conditional) | HRA (consent, ethics, export, storage) | Separate legal basis for research, ethics approvals, segregated environments and data pipelines | Not implemented | Open: create optional research lane with explicit opt-in controls |
| CH-C10 | AI oversight for high-impact workflows | FADP transparency/automated decision context + HRA principles (if research) | Human-in-the-loop, explainability notes, model risk thresholds, post-deployment monitoring | AI guidance exists in docs | Partial: add measurable AI acceptance criteria and override audit trail |

### Architecture Challenge Outcome (Compliance Lens)

Decisions already aligned:
- React-only MVP is compliance-neutral and simplifies data flow boundaries.
- PHI failover default-deny reduces unlawful disclosure risk.
- Swiss-only PHI processing policy supports cross-border risk control.

Material gaps to close:
- Formal controller/processor and subprocessor register.
- Article-linked DSR operating model.
- Policy-as-code enforcement for residency and deployment-type rules.
- Evidence automation for audits and release readiness.

## Microsoft Purview Coverage Evaluation (GA and IaC)

This section defines how Microsoft Purview contributes to the control set
CH-C01 to CH-C10, based on currently documented GA and automation capability.

### Purview Control Fit

| Control ID | Purview contribution | Delivery model |
| ----- | ----- | ----- |
| CH-C01 | Data catalog, classification, lineage, and metadata stewardship support purpose and minimization governance | Hybrid: IaC for account baseline + operational catalog workflows |
| CH-C03 | Auditability and lineage capabilities support traceability evidence | Hybrid: service provisioning via IaC, evidence workflows operational |
| CH-C05 | Sensitivity labels and policy frameworks can support transfer and disclosure governance signals | Mostly operational policy configuration |
| CH-C10 | Compliance and governance solutions support AI-related data governance evidence and oversight context | Mostly operational policy and reporting workflows |

### Purview GA and IaC Boundary

| Capability | Current status for this architecture | Implementation rule |
| ----- | ----- | ----- |
| Purview account resource deployment | IaC-ready | Deploy via Bicep/ARM in landing-zone baseline |
| Account-level identity/network controls | IaC-ready | Enforce in infrastructure lane before workload onboarding |
| Collections and scan onboarding | Not fully declarative end-to-end in Bicep guidance | Execute through controlled automation runbooks after infra deployment |
| Ongoing compliance policy configuration and tuning | Operational | Manage through controlled change process and evidence artifacts |

### Compliance Implementation Rule

For this repository, Purview shall be treated as:
1. A mandatory governance accelerator for metadata, lineage, and evidence
	controls where workload scope requires it.
2. A two-lane implementation model:
	- lane A: IaC for account and baseline security posture,
	- lane B: operational automation for catalog, scans, and policy lifecycle.
3. A region-gated control plane where production use for PHI controls requires
	explicit GA confirmation for the selected region and feature.

## Evidence Model

### Evidence Categories

| Evidence ID | Evidence artifact | Owner | Frequency | Gate |
| ----- | ----- | ----- | ----- | ----- |
| E-01 | Data processing inventory with purpose and legal basis tags | Data governance | Quarterly and on major release | Architecture review |
| E-02 | Access control evidence (role matrix, privileged access reviews, JIT records) | Security | Monthly | Release and audit |
| E-03 | Residency and egress policy verification report | Platform engineering | Each release | Deployment gate |
| E-04 | Logging and traceability evidence (sampled audit trails, retention proof) | Platform engineering | Monthly | Operations review |
| E-05 | DSR workflow evidence (request logs, SLA compliance, outcomes) | Privacy office | Monthly | Compliance review |
| E-06 | Privacy incident drill and real-incident postmortems | SecOps + Privacy | Quarterly and post-incident | Risk committee |
| E-07 | AI safety and oversight report (quality, drift, override and escalation stats) | AI governance | Monthly | AI change approval |
| E-08 | EPR conformance evidence package (if EPR enabled) | Integration lead | Before go-live and annually | External conformance |
| E-09 | Research governance packet (if HRA in scope) | Research governance | Per study and annual | Ethics and legal approval |

### Minimum Release Checklist

- Residency controls for PHI validated in CI and pre-deploy.
- Access and logging controls validated against CH-C03 and CH-C07.
- DSR and incident response operational checks completed.
- AI oversight controls validated for affected workflows.
- Evidence artifacts E-01 to E-07 attached to release record.

## Sources and Traceability Notes

- All legal references in this document are from Swiss federal official sources
	(Fedlex and federal administration websites where available).
- For implementation decisions, cite both:
	- legal source URL, and
	- internal control ID (CH-Cxx) in PR descriptions and ADR updates.
- When this file is updated with article-level legal interpretation,
	include reviewer sign-off from legal/compliance.

## Next Steps

1. Create a control implementation tracker in docs/compliance mapped to CH-C01 to CH-C10.
2. Add CI policy checks for residency and PHI transfer guardrails.
3. Add operational runbooks for DSR and privacy incident response.
4. Add evidence collection templates for E-01 to E-09.
5. Add canton-specific annex once target canton rollout plan is fixed.
