# PRD

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-01 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | 0.3.0 (preliminary baseline, superseded by full rewrite from specs) |

## Purpose

This product requirements document defines the complete functional and non-functional
requirements for the Swiss AI-Powered Patient Flow and Hospital Capacity Platform,
derived from the source specifications in `docs/specs`.

The target product is a provider-internal operational intelligence platform for one
Swiss cantonal hospital provider deployment at a time.

## Source Scope

### Canonical Inputs

- `docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform.md`
- `docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform analysis.md`

### In Scope

- Provider-internal deployment model for one provider instance.
- AI-powered operations support for forecasting, discharge coordination, and bed management.
- Integration with external ecosystem partners as controlled endpoints.
- Data, AI, application, integration, governance, and delivery lanes.

### Out Of Scope

- Multi-provider shared tenancy or cross-provider shared governance runtime.
- External partner direct platform operations access.
- Dynamics 365 case-management workflows.
- Full clinician workstation replacement.

## Functional Requirements

### A) Operating Model And Product Scope

| ID | Requirement |
| -- | ----------- |
| `FR-OM-001` | The solution shall be deployed for one hospital provider instance at a time. |
| `FR-OM-002` | The solution shall support provider-internal governance and data ownership boundaries. |
| `FR-OM-003` | The solution shall support an implementation sequence for USZ-first or LUKS-first rollout patterns. |
| `FR-OM-004` | External care entities shall be integrated as endpoints and not as first-class platform operators. |
| `FR-OM-005` | The product shall support a phased implementation model where capabilities can be enabled incrementally. |

### B) Data And Interoperability

| ID | Requirement |
| -- | ----------- |
| `FR-DATA-001` | The platform shall ingest provider-internal operational signals, including ED, ADT, bed-state, and discharge-related events. |
| `FR-DATA-002` | The platform shall support HL7 FHIR-oriented normalization where healthcare interoperability requires it. |
| `FR-DATA-003` | The platform shall maintain curated datasets that unify operational, planning, and model input data. |
| `FR-DATA-004` | The platform shall capture partner acknowledgements and status updates from integration flows. |
| `FR-DATA-005` | The platform shall expose governed semantic models for dashboard and copilot consumption. |
| `FR-DATA-006` | The platform shall support data ingestion from KIS/EHR, ED systems, bed management systems, and staffing/planning systems. |
| `FR-DATA-007` | The platform shall support outbound and inbound orchestration with downstream partners via integration workflows. |
| `FR-DATA-008` | The platform shall keep source-to-consumption traceability for operational and AI-serving datasets. |

### C) Forecasting And Capacity Intelligence

| ID | Requirement |
| -- | ----------- |
| `FR-FC-001` | The solution shall produce a 72-hour demand forecast for emergency demand and admission pressure. |
| `FR-FC-002` | Forecast outputs shall be segmented by specialty and time window. |
| `FR-FC-003` | Forecasting shall use provider-internal arrivals plus downstream capacity signals as model inputs. |
| `FR-FC-004` | Forecast outputs shall be published to operations-facing dashboards. |
| `FR-FC-005` | Forecast outputs shall be available as grounding context for the bed management copilot. |
| `FR-FC-006` | Forecast generation runs shall persist execution timestamps and model run identifiers for auditability. |

### D) Discharge Coordination Intelligence

| ID | Requirement |
| -- | ----------- |
| `FR-DC-001` | The solution shall identify inpatients approaching discharge readiness. |
| `FR-DC-002` | The solution shall produce ranked discharge candidates with explanatory factors. |
| `FR-DC-003` | The solution shall trigger integration-based downstream actions for discharge coordination. |
| `FR-DC-004` | The solution shall record outbound coordination events and returned partner statuses. |
| `FR-DC-005` | The solution shall surface discharge blockers to operations users. |
| `FR-DC-006` | The solution shall make discharge-readiness outputs available to dashboards and copilot interactions. |

### E) Bed Management Copilot And User Experience

| ID | Requirement |
| -- | ----------- |
| `FR-CX-001` | The solution shall provide a copilot interface for operations teams to query bed and flow status. |
| `FR-CX-002` | The copilot shall provide grounded answers based on live operational data, forecast outputs, and discharge signals. |
| `FR-CX-003` | The copilot shall provide bottleneck explanations and recommended operational options. |
| `FR-CX-004` | The copilot shall present current bed state, predicted pressure windows, and likely same-day discharges. |
| `FR-CX-005` | Power BI-based operational visibility shall be available for non-conversational usage scenarios. |
| `FR-CX-006` | Copilot responses shall preserve references to source context and response timestamp metadata. |

### F) Governance, Delivery, And Operations

| ID | Requirement |
| -- | ----------- |
| `FR-GOV-001` | The solution shall provide auditable traceability between source data, model outputs, user-facing answers, and integration events. |
| `FR-GOV-002` | The solution shall support access-control enforcement for clinical and operational data surfaces. |
| `FR-GOV-003` | The delivery model shall support structured promotion across DEV, SIT, and PROD stages. |
| `FR-GOV-004` | The solution shall produce governance evidence artifacts for compliance reviews. |
| `FR-GOV-005` | The solution shall support policy-driven integration controls for outbound partner interactions. |
| `FR-GOV-006` | The solution shall maintain provider-local control over prompts, model configuration, and operational workflows. |

## Non-Functional Requirements

### A) Compliance And Privacy

| ID | Requirement |
| -- | ----------- |
| `NFR-COMP-001` | The solution shall support Swiss DSG compliance for healthcare data handling. |
| `NFR-COMP-002` | The solution shall support cantonal healthcare governance requirements in deployment and operations controls. |
| `NFR-COMP-003` | The solution shall support KVG/LAMal-aligned operational governance where applicable to patient flow data usage. |
| `NFR-COMP-004` | Data residency controls shall support Switzerland or permitted jurisdiction constraints for each dataset class. |

### B) Security And Access Control

| ID | Requirement |
| -- | ----------- |
| `NFR-SEC-001` | Access shall be least-privilege and role-scoped by user and service identity. |
| `NFR-SEC-002` | Data access attempts and privilege changes shall be fully auditable. |
| `NFR-SEC-003` | Integration endpoints shall enforce authenticated and authorized communication patterns. |
| `NFR-SEC-004` | Secret material shall be managed outside source-controlled artifacts. |

### C) Data Quality And Integrity

| ID | Requirement |
| -- | ----------- |
| `NFR-DQ-001` | Critical operational feeds shall include quality checks for completeness and schema validity. |
| `NFR-DQ-002` | Curated operational datasets shall support lineage from source to serving views. |
| `NFR-DQ-003` | Data model changes shall preserve backward compatibility or include controlled migration plans. |
| `NFR-DQ-004` | Integration message failures shall be observable and recoverable without silent data loss. |

### D) Performance And Throughput

| ID | Requirement |
| -- | ----------- |
| `NFR-PERF-001` | Ingestion shall support near-real-time updates for ED, ADT, bed-state, and discharge status signals. |
| `NFR-PERF-002` | Forecast inference shall support at least hourly refresh cadence for the 72-hour horizon. |
| `NFR-PERF-003` | Discharge-readiness scoring shall support multiple recalculations per day. |
| `NFR-PERF-004` | The platform shall support burst headroom above average event volume. |
| `NFR-PERF-005` | End-user operational surfaces shall support interactive decision cycles without batch-only dependence. |

### E) Reliability And Operational Continuity

| ID | Requirement |
| -- | ----------- |
| `NFR-REL-001` | The platform shall support continuous operations and shall not be designed as overnight batch-only service. |
| `NFR-REL-002` | Critical data and inference pipelines shall provide failure visibility and restartability. |
| `NFR-REL-003` | Operational dashboards and copilot services shall degrade gracefully when non-critical dependencies fail. |
| `NFR-REL-004` | Integration workflows shall provide retry and exception-handling behavior for transient endpoint errors. |

### F) Responsible AI And Auditability

| ID | Requirement |
| -- | ----------- |
| `NFR-AI-001` | Copilot outputs shall remain advisory and shall not replace human operational authority. |
| `NFR-AI-002` | Copilot outputs shall be retrieval-grounded in provider operational context and model outputs. |
| `NFR-AI-003` | Forecast and discharge model outputs shall be traceable to model version and execution time. |
| `NFR-AI-004` | User-facing AI responses and coordination triggers shall be auditable to source context. |
| `NFR-AI-005` | AI-serving behavior shall support provider-local governance and change control. |

### G) Maintainability And Delivery

| ID | Requirement |
| -- | ----------- |
| `NFR-MAINT-001` | The solution shall support modular architecture lanes for data, AI, app, integration, and governance assets. |
| `NFR-MAINT-002` | Delivery workflows shall be Git-first and support auditable promotion across environments. |
| `NFR-MAINT-003` | Requirement artifacts shall remain traceable to specification sources and implementation increments. |
| `NFR-MAINT-004` | Platform configuration shall support provider-specific rollout without full re-architecture. |

## MVP Definition

The MVP is a provider-internal release that demonstrates end-to-end operational value with controlled risk:

- Baseline ingestion and semantic visibility for core capacity and discharge signals.
- Initial 72-hour demand forecasting output in operational views.
- Initial discharge-readiness scoring and partner coordination triggers.
- Grounded copilot support for bed management operations.
- Compliance, security, and audit controls active for pilot scope.

## Traceability Matrix

| Source | Requirement Coverage |
| ------ | -------------------- |
| `docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform.md` | `FR-OM-001` to `FR-OM-005`, `FR-DATA-001` to `FR-DATA-007`, `FR-FC-001` to `FR-FC-005`, `FR-DC-001` to `FR-DC-005`, `FR-CX-001` to `FR-CX-005`, `NFR-COMP-001` to `NFR-COMP-004`, `NFR-SEC-001` to `NFR-SEC-004` |
| `docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform analysis.md` | `FR-DATA-008`, `FR-FC-006`, `FR-DC-006`, `FR-CX-006`, `FR-GOV-001` to `FR-GOV-006`, `NFR-DQ-001` to `NFR-DQ-004`, `NFR-PERF-001` to `NFR-PERF-005`, `NFR-REL-001` to `NFR-REL-004`, `NFR-AI-001` to `NFR-AI-005`, `NFR-MAINT-001` to `NFR-MAINT-004` |

## Assumptions To Validate In Implementation Planning

- Provider-specific event-rate baselines and peak distributions.
- Exact FHIR profile and integration message sets by provider.
- Jurisdiction-specific residency controls by dataset class.
- Operational SLO values for data freshness, inference latency, and dashboard response time.
