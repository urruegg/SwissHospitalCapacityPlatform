# PRD

| Field | Value |
| ----- | ----- |
| **Version** | 1.7.0 |
| **Date** | 2026-07-18 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 1.6.0 (added `FR-ONT-008` Fabric-to-Foundry grounding seam + ADR-0033 traceability row) |

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

### G) Onboarding (Minimum-Data And Specialty-Driven Capacity)

Sprint 6 deltas. Onboarding is split into two lanes: a patient lane using only a
minimum required metadata set, and a hospital-capacity lane driven by
treatment-specialty metadata. See
[`docs/sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md`\](sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md).

| ID | Requirement |
| -- | ----------- |
| `FR-ONB-001` | The platform shall onboard new patients using a minimum required metadata set only. |
| `FR-ONB-002` | The platform shall onboard hospital capacity using specialty-tagged metadata. |
| `FR-ONB-003` | The platform shall support provider-specific specialty profiles for capacity planning. |
| `FR-ONB-004` | The platform shall classify onboarding workflows as deterministic service vs agentic flow using a documented criterion. |

### H) Semantic Ontology

Sprint 09 deltas per [ADR-0014](adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) (supersedes ADR-0002) and [AMA HCC/North Star review §5.1](reviews/2026-07-01-ama-hcc-northstar-review.md#51-ontology-requirements-new-family-fr-ont--nfr-ont). Adds a semantic backbone family that grounds copilot, dashboards and simulation on shared meaning. All items are gated per ADR-0014 §5 (G-A / G-B / G-C).

| ID | Requirement |
| -- | ----------- |
| `FR-ONT-001` | The platform shall maintain a **reference ontology** authored in OWL/RDF, importing established published ontologies (BFO ISO/IEC 21838-2:2021, OMRSE, OGMS, OOSTT, Goyer et al. healthcare-system classes) and adding the platform-specific `CapacityUnit` abstraction with subtypes for bed, OR slot, room, staff shift and device. |
| `FR-ONT-002` | The platform shall realise the **operational ontology** in Fabric IQ, auto-generated from the governed semantic model with static (lakehouse) and time-series (eventhouse) bindings. Use in `switzerlandnorth` PROD paths carrying PHI is gated on Fabric IQ Switzerland-region GA + DPA equivalence per ADR-0014 gate G-C; use in the `westus2` demo scope is permitted per ADR-0013. |
| `FR-ONT-003` | The platform shall model all in-scope hospital resource dimensions (beds, OR slots, rooms, staff shifts, devices) as **capacity-unit subtypes** with shared states (available / occupied / blocked / planned) and shared relations, so one set of KPIs, forecasts and simulation logic applies across all dimensions. |
| `FR-ONT-004` | The copilot and Fabric Data Agents shall **ground responses on ontology entities and relationships** to deliver concept-level traceability, extending `NFR-AI-002/003/004`. |
| `FR-ONT-005` | The platform shall provide a **process-ontology overlay** on the reference layer to support what-if simulation (`FR-SIM-*` when introduced). |
| `FR-ONT-006` | The ontology shall carry a **crosswalk to FHIR resource types and SNOMED CT concepts** for clinical interoperability (extends `FR-DATA-002`). |
| `FR-ONT-007` | The ontology shall support **provider-specific extensions** (specialisations) without re-architecture, realising `NFR-MAINT-004` at the semantic layer. |
| `FR-ONT-008` | Foundry-hosted copilots shall consume the read-only **Fabric Data Agent as their primary grounding source** ahead of table grounding (the Fabric-to-Foundry consumption seam), propagate its RLS and [ADR-0016](adr/0016-no-phi-in-mvp-demo-scope.md) PHI-gate `REFUSE:` codes **verbatim** (no route-around), and surface at least one `hcp:*` ontology citation per grounded answer. Realised per [ADR-0033](adr/0033-fabric-data-agent-as-foundry-grounding-tool.md); extends `FR-ONT-004`, `NFR-AI-002/004`. **Realised live (demo scope)** for the Foundry `ooa` surface — live E2E in [ADR-0034](adr/0034-fabric-iq-demo-scope-artefacts.md) + [evidence doc](architecture/fabric-iq-ready-evidence.md) (issue #251); the gpt-5 layer surfaces the refusal in natural language rather than the verbatim `REFUSE:` token (safety outcome preserved). App/agent-host surface pending. |
| `FR-GOV-ONT-001` | The data-governance RACI shall include a nominated **semantic / ontology owner**. Documented in [OPERATIONS.md](OPERATIONS.md) as of v1.4.0. |
| `FR-GOV-ONT-002` | Ontology changes shall follow an **OBO-inspired semantic change workflow** (proposal → domain-owner review → versioned release → downstream impact check), mirroring the data-contract breaking-change control in `NFR-MAINT-002`. |
| `FR-GOV-ONT-003` | The delivery pipeline shall include a **CI conformance check** verifying that every operational-layer entity maps to a reference-layer class (or is explicitly annotated as reference-layer-exempt). Failure fails the build. |

### I) Visualization And Dashboards (Sprint 09 T5)

Sprint 09 T5 deltas formalised per [ADR-0018](adr/0018-add-fr-viz-and-nfr-gov-ids.md). Referenced from [Sprint 09 v2 design spec §7.7](superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#77-traceability).

| ID | Requirement |
| -- | ----------- |
| `FR-VIZ-001` | The platform shall provide an operational **bed-capacity dashboard page** exposing current occupancy, forecast pressure windows, and data-quality signals, aligned with `FR-CX-005`. |
| `FR-VIZ-002` | The platform shall provide an operational **OR-steering dashboard page** exposing case-level utilisation, first-case on-time performance, cancellation, and idle-slot metrics, aligned with `FR-CX-005`. |

## Non-Functional Requirements

### A) Compliance And Privacy

| ID | Requirement |
| -- | ----------- |
| `NFR-COMP-001` | The solution shall support Swiss DSG compliance for healthcare data handling. |
| `NFR-COMP-002` | The solution shall support cantonal healthcare governance requirements in deployment and operations controls. |
| `NFR-COMP-003` | The solution shall support KVG/LAMal-aligned operational governance where applicable to patient flow data usage. |
| `NFR-COMP-004` | Data residency controls shall support Switzerland or permitted jurisdiction constraints for each dataset class. |
| `NFR-COMP-005` | The solution shall maintain a data processing inventory with legal basis and purpose tags for PHI and operational datasets. |
| `NFR-COMP-006` | The solution shall provide a documented data-subject-rights operating process with accountable ownership and response SLAs. |
| `NFR-COMP-007` | The solution shall implement policy-enforced default-deny behavior for PHI cross-border transfer and failover activation unless explicitly approved. |
| `NFR-COMP-008` | The solution shall maintain auditable privacy incident handling and notification decision workflows. |
| `NFR-COMP-009` | If EPR integration is enabled, the solution shall enforce consent, identity, access, and logging controls aligned to EPDG/EPDV-EDI obligations. |
| `NFR-COMP-010` | The solution shall maintain compliance evidence artifacts and review cadence mapped to legal obligations and internal controls. |
| `NFR-COMP-011` | Onboarding data contracts shall enforce minimum-sensitive-data controls and purpose tags (Sprint 6). |

### B) Security And Access Control

| ID | Requirement |
| -- | ----------- |
| `NFR-SEC-001` | Access shall be least-privilege and role-scoped by user and service identity. |
| `NFR-SEC-002` | Data access attempts and privilege changes shall be fully auditable. |
| `NFR-SEC-003` | Integration endpoints shall enforce authenticated and authorized communication patterns. |
| `NFR-SEC-004` | Secret material shall be managed outside source-controlled artifacts. |
| `NFR-SEC-005` | Onboarding identity and cross-tenant boundaries shall be explicit and auditable (Sprint 6). |

### C) Data Quality And Integrity

| ID | Requirement |
| -- | ----------- |
| `NFR-DQ-001` | Critical operational feeds shall include quality checks for completeness and schema validity. |
| `NFR-DQ-002` | Curated operational datasets shall support lineage from source to serving views. |
| `NFR-DQ-003` | Data model changes shall preserve backward compatibility or include controlled migration plans. |
| `NFR-DQ-004` | Integration message failures shall be observable and recoverable without silent data loss. |
| `NFR-DQ-005` | Specialty metadata shall include quality checks and controlled versioning (Sprint 6). |

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
| `NFR-REL-005` | Onboarding services shall remain available under defined degraded-mode behavior (Sprint 6). |

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
| `NFR-MAINT-005` | Sprint 6 onboarding and MVP agent services shall be deployable through IaC-first pipelines with reproducible environment bootstrap (Sprint 6). |

### H) Semantic Ontology (Sprint 9)

| ID | Requirement |
| -- | ----------- |
| `NFR-ONT-001` | The ontology (reference layer OWL/RDF + operational layer Fabric IQ + crosswalk) shall be **versioned, governed and promoted as a first-class asset** with DEV/SIT/PROD gates, an explicit reference↔operational crosswalk artefact (`docs/ontology/crosswalk.md`), and a **CI conformance check** enforcing `FR-GOV-ONT-003`. Extends `NFR-MAINT-002`. |

### I) Governance And Audit (Sprint 09 T5)

Sprint 09 T5 deltas formalised per [ADR-0018](adr/0018-add-fr-viz-and-nfr-gov-ids.md).

| ID | Requirement |
| -- | ----------- |
| `NFR-GOV-001` | The platform shall record change-management traceability for semantic-model, dashboard, and agent artefacts (aligns with `FR-GOV-001`). |
| `NFR-GOV-002` | The platform shall support audit-review workflows for governance evidence artefacts (aligns with `FR-GOV-004`). |
| `NFR-GOV-003` | The dashboard consumption path shall enforce role-scoped filtering that prevents PHI-tagged column exposure to any non-owner role (extends [ADR-0016](adr/0016-no-phi-in-mvp-demo-scope.md) gate 4). |
| `NFR-GOV-004` | Semantic-model and dashboard artefacts shall be round-trippable to source-controlled TMDL/PBIP such that any deployed state can be replayed from repository content alone. |
| `NFR-GOV-005` | Governance evidence artefacts shall be co-located with the sprint or ADR that produced them under `docs/sprints/*/evidence/` or `docs/adr/*.md`. |
| `NFR-GOV-006` | Every dashboard visual shall carry per-visual traceability back to its underlying semantic-model measure and its ontology-grounded source (`hcp:*` entities), aligned with `FR-CX-006` and `FR-ONT-004`. |

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
| `docs/COMPLIANCE.md` | `NFR-COMP-005` to `NFR-COMP-010` |
| `docs/sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md` | `FR-ONB-001` to `FR-ONB-004`, `NFR-COMP-011`, `NFR-SEC-005`, `NFR-DQ-005`, `NFR-REL-005`, `NFR-MAINT-005` |
| [`docs/adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md`](adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) *(supersedes [`0002`](adr/0002-defer-fabric-iq-ontology-from-mvp.md))* | `FR-ONT-001` to `FR-ONT-007`, `FR-GOV-ONT-001` to `FR-GOV-ONT-003`, `NFR-ONT-001` |
| [`docs/reviews/2026-07-01-ama-hcc-northstar-review.md`](reviews/2026-07-01-ama-hcc-northstar-review.md) *(source review, §5.1 and §5.8)* | `FR-ONT-001` to `FR-ONT-007`, `FR-GOV-ONT-001` to `FR-GOV-ONT-003`, `NFR-ONT-001` |
| [`docs/OPERATIONS.md`](OPERATIONS.md) *(v1.4.0 semantic-owner RACI + Live Risk Register)* | `FR-GOV-ONT-001`, `NFR-ONT-001` (partial — owner named; workflow + CI implementation pending) |
| [`docs/sprints/sprint-10-e2e-pipeline-and-dashboard-completion.md`](sprints/sprint-10-e2e-pipeline-and-dashboard-completion.md) *(Sprint 10 charter)* | `FR-VIZ-001` to `FR-VIZ-002`, `NFR-GOV-001` to `NFR-GOV-006`, `FR-CX-005`, `FR-DATA-005`, `FR-DATA-008`, `FR-GOV-001`, `FR-GOV-004`, `FR-ONT-004`, `FR-ONT-006` |
| [`docs/adr/0018-add-fr-viz-and-nfr-gov-ids.md`](adr/0018-add-fr-viz-and-nfr-gov-ids.md) *(formalises drift from Sprint 09 v2 design spec §7.7)* | `FR-VIZ-001` to `FR-VIZ-002`, `NFR-GOV-001` to `NFR-GOV-006` |
| [`docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md`](sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md) *(recovered draft — pre-refresh)* | `FR-ONT-001` to `FR-ONT-007` (MVO scope), `NFR-ONT-001` (target implementation slot) |

| [`docs/adr/0033-fabric-data-agent-as-foundry-grounding-tool.md`](adr/0033-fabric-data-agent-as-foundry-grounding-tool.md) *(Fabric-to-Foundry grounding seam, Slice 0)* | `FR-ONT-008` (extends `FR-ONT-004`, `NFR-AI-002/004`) |
| [`docs/adr/0034-fabric-iq-demo-scope-artefacts.md`](adr/0034-fabric-iq-demo-scope-artefacts.md) + [`docs/architecture/fabric-iq-ready-evidence.md`](architecture/fabric-iq-ready-evidence.md) *(live demo-scope realisation)* | `FR-ONT-008` (Foundry `ooa` surface proven live, issue #251) |

## Assumptions To Validate In Implementation Planning

- Provider-specific event-rate baselines and peak distributions.
- Exact FHIR profile and integration message sets by provider.
- Jurisdiction-specific residency controls by dataset class.
- Operational SLO values for data freshness, inference latency, and dashboard response time.

### Sprint 05 CAF/WAF Baseline Cross-References

The Sprint 05 documentation baseline operationalizes several of these assumptions into
explicit, release-gated artifacts mapped back to the requirements above:

- `NFR-COMP-001`/`NFR-COMP-002` (cantonal governance): [`docs/compliance/cantonal-annex.md`](compliance/cantonal-annex.md) (ADR-0011).
- `NFR-REL-001`/`NFR-REL-003` (reliability/DR): [`docs/operations/reliability-dr-profile.md`](operations/reliability-dr-profile.md) (ADR-0009).
- `NFR-AI-001`/`NFR-COMP-004` (runtime pattern + residency): [`docs/architecture/runtime-pattern-decision-matrix.md`](architecture/runtime-pattern-decision-matrix.md) (ADR-0008).
- CAF/WAF delta closure status: [`docs/architecture/caf-waf-alignment-matrix.md`](architecture/caf-waf-alignment-matrix.md).

