# DATA

| Field | Value |
| ----- | ----- |
| **Version** | 0.7.1 |
| **Date** | 2026-07-23 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 0.7.0 (added DC-EXT-SIGNAL-v1 provenance plugin fields and ext_dim_source badge columns) |

## Purpose

Define the MVP data design baseline for the Swiss Hospital Capacity Platform,
including data domains, data contracts, retention, and governance controls.

This document is scoped to the approved MVP service pattern using:
1. Azure Health Data Services for healthcare interoperability.
2. Microsoft Fabric for curation, serving, and analytics.
3. Data lake storage layers (OneLake and controlled landing zones) for
	scalable governed data persistence.

## Source Baseline

This data design aligns to:
1. docs/PRD.md
2. docs/ARCHITECTURE.md
3. docs/AI.md
4. docs/COMPLIANCE.md
5. docs/SECURITY.md

## Data Scope for MVP

### In Scope

1. Provider-internal operational data for one cantonal provider deployment.
2. ED, ADT, bed-state, discharge coordination, and staffing/planning signals.
3. Forecast and discharge model input/output datasets.
4. Copilot grounding datasets and audit trace metadata.
5. Partner endpoint integration status and acknowledgement events.

### Out of Scope

1. Multi-provider pooled data domains.
2. Full clinical record replacement.
3. Preview-only data features on MVP critical path.
4. Unbounded research secondary-use stores without explicit legal basis.

## Data Domains

### Domain Model (MVP)

| Domain | Purpose | Primary Sources | Primary Consumers |
| ----- | ----- | ----- | ----- |
| Patient flow events | Track arrivals, admissions, transfers, discharge progress | KIS/EHR, ADT feeds, ED systems | Capacity dashboards, forecasting, copilot grounding |
| Bed and capacity state | Current and projected bed utilization by ward/specialty | Bed management systems, operations feeds | Operations views, copilot Q and A, demand balancing |
| Staffing and operations context | Operational readiness and staffing constraints | Planning and staffing systems | Forecast interpretation, discharge action planning |
| Discharge coordination | Candidate readiness, blockers, outbound partner workflows | Clinical workflow systems, integration events | Discharge AI, care coordination operations |
| Partner integration events | Outbound requests and inbound acknowledgements | Logic Apps and partner endpoint callbacks | Operations monitoring, audit and reliability controls |
| AI and decision trace | Forecast runs, model versions, confidence signals, citations | AML pipelines, inference services, runtime APIs | Copilot, governance reviews, model oversight |
| Governance and audit evidence | Access logs, policy results, lineage, evidence artifacts | Platform telemetry, policy engines, Purview metadata | Security, compliance, audit and release gates |

### Domain Ownership (Initial)

| Domain | Business Owner | Technical Owner |
| ----- | ----- | ----- |
| Patient flow and bed state | Operations command lead | Data platform lead |
| Discharge coordination | Care coordination lead | Integration lead |
| AI and decision trace | AI governance lead | AI engineering lead |
| Governance and audit evidence | Privacy and compliance lead | Security and platform lead |

## Data Contracts

### Contract Principles

1. Every producer-to-consumer boundary uses a versioned contract.
2. Every contract includes classification and residency tags.
3. Breaking changes require migration plan and approval.
4. Contract conformance is validated in CI and ingestion/runtime checks.

### Mandatory Contract Fields

Each contract must define:
1. Contract ID and semantic version.
2. Producer system and owning team.
3. Consumer systems and use cases.
4. Schema definition (fields, types, required flags, units/time zones).
5. Data quality rules (completeness, timeliness, valid ranges, uniqueness).
6. Classification and legal basis tags.
7. Residency and transfer constraints.
8. Retention class and deletion/archival behavior.

### Suggested Contract Groups (MVP)

| Contract Group | Example ID | Purpose |
| ----- | ----- | ----- |
| Ingestion contract | DC-ING-ADT-v1 | ADT/ED event ingestion schema and SLA rules |
| Curation contract | DC-CUR-CAPACITY-v1 | Curated capacity model for dashboards and AI features |
| AI feature contract | DC-AI-FEATURES-v1 | Stable model feature set with lineage fields |
| AI output contract | DC-AI-FORECAST-v1 | Forecast output schema and run metadata |
| Integration event contract | DC-INT-DISCHARGE-v1 | Outbound/inbound partner workflow event payloads |
| Copilot grounding contract | DC-GRD-CONTEXT-v1 | Grounding context and citation metadata format |
| Patient onboarding contract | DC-ONB-PATIENT-v1 | Minimum-data, pseudonymous patient onboarding metadata (Sprint 6) |
| Specialty-capacity onboarding contract | DC-ONB-CAPACITY-v1 | Specialty-tagged hospital capacity onboarding metadata (Sprint 6) |
| External signal contract | DC-EXT-SIGNAL-v1 | CAP-Suisse-aligned trusted external hazard signals for advisory CSA trigger evaluation |

### Sprint 6 Onboarding Contracts (Minimum-Data and Specialty Capacity)

Sprint 6 baselines two onboarding contract families with a minimum-sensitive-data
design. Machine-readable JSON Schema contracts and synthesized, non-production
SIT datasets live in [`data/synthetic/`](../data/synthetic/README.md) and are
validated by [`data/synthetic/validate_datasets.py`](../data/synthetic/validate_datasets.py)
in CI. These contracts realize `FR-ONB-001`, `FR-ONB-002`, `FR-ONB-003`,
`NFR-COMP-011`, `NFR-DQ-005`, and `CH-C01`.

#### DC-ONB-PATIENT-v1 (patient minimum-data lane)

Minimized, pseudonymous field set. Direct identifiers are forbidden and rejected
by the validator (re-identification minimization, `CH-C01` / `NFR-COMP-011`).

| Field | Type | Notes |
| ----- | ----- | ----- |
| `onboardingId` | string | Synthetic onboarding key (`ONB-...`) |
| `pseudonymId` | string | Pseudonym only; no direct identifier |
| `ageBand` | enum | Banded age (`0-17`..`80+`), not date of birth |
| `sex` | enum | `female`/`male`/`other`/`unspecified` |
| `admissionType` | enum | `emergency`/`elective`/`transfer`/`observation` |
| `careSpecialty` | string | Treatment specialty tag |
| `arrivalDate` | date | Day-granularity only |
| `purposeTag` | enum | Purpose limitation tag |
| `minimizationReviewed` | boolean | Minimization review marker |

Forbidden (validator-enforced): name, date of birth, AHV/SSN, address, contact
details, insurance/patient identifiers.

#### DC-ONB-CAPACITY-v1 and provider extensions (specialty-capacity lane)

Specialty-tagged capacity metadata with a versioned specialty taxonomy
(`specialtyTaxonomyVersion`) and the capacity invariant `bedsAvailable <=
bedsTotal` (`NFR-DQ-005`). Provider profiles (`FR-ONB-003`) extend the base
contract:

| Contract | Provider scope | Extension signals |
| ----- | ----- | ----- |
| `DC-ONB-CAPACITY-v1` | generic | specialty, specialty tags, ward, beds, LOS calibration |
| `DC-ONB-CAPACITY-HIRSLANDEN-v1` | Klinik Hirslanden | OR schedule pressure, specialty bed-demand windows, LOS calibration signal |
| `DC-ONB-CAPACITY-ZOLLIKERBERG-v1` | Spital Zollikerberg | care mode + optional Hospital-at-Home indicators (virtual ward, discharge pathway, telemetry readiness) |

Hospital-at-Home fields are optional and provider-scoped, consistent with the
Sprint 6 risk mitigation to keep the baseline model simple.

### Sprint 07 — Patient capacity planning data product contracts

| Contract ID | Role | CDM/FHIR source | Dataset |
| ----- | ----- | ----- | ----- |
| `DC-SUPPLY-ORGANIZATION-v1` | Tenancy and legal-entity catalog (Hospital) | `Organization` (Commoncore) | `datasets/dc-supply-organization-v1.sample.json` |
| `DC-SUPPLY-LOCATION-v1` | Recursive supply hierarchy (Site/Ward/Bed) | `Location` + embedded `HealthcareService` | `datasets/dc-supply-location-v1.sample.json` |
| `DC-DEMAND-ENCOUNTER-v1` | Inpatient demand (`Encounter.class=IMP`) | `Encounter` + `EncounterStatusHistory` | `datasets/dc-demand-encounter-v1.sample.json` |
| `DC-MATCH-RECOMMENDATION-v1` | Ranked top-N candidate Stations (advisory) | *(bespoke)* | `datasets/dc-match-recommendation-v1.sample.json` |

Design rationale, validator rules, partition-key strategy, and the deterministic stub matcher are documented in [docs/superpowers/specs/2026-06-12-patient-capacity-data-product-design.md](superpowers/specs/2026-06-12-patient-capacity-data-product-design.md).

### DC-EXT-SIGNAL-v1 (trusted external signal lane)

`DC-EXT-SIGNAL-v1` is the Sprint 21 contract for trusted external hazard
signals. It normalizes Trust-A Swiss public-authority feeds and synthetic
fixtures into a CAP-Suisse-aligned envelope for situational awareness,
capacity-planning, and advisory CSA trigger evaluation. The machine-readable
schema is [`data/synthetic/schema/dc-ext-signal-v1.schema.json`](../data/synthetic/schema/dc-ext-signal-v1.schema.json); external-trigger governance is recorded in
[ADR-0036](adr/0036-external-trigger-governance.md), and the reference-layer
ontology binding is [`docs/ontology/reference-layer.ttl`](ontology/reference-layer.ttl).
The lane is public-authority plus synthetic data only and carries no PHI.

Envelope fields:

| Field | Type / allowed values | Notes |
| ----- | --------------------- | ----- |
| `datasetId` | string, `DS-EXT-SIGNAL-*` | Dataset envelope identifier. |
| `contractId` | `DC-EXT-SIGNAL-v1` | Stable contract identifier. |
| `contractVersion` | SemVer string | Contract version of the payload. |
| `classification` | `public-authority` | Public authority data only. |
| `residency` | `CH`, `demo-westus2` | Swiss residency or ADR-0013 demo-scope residency. |
| `purposeTags` | `crisis-trigger`, `capacity-planning`, `situational-awareness` | Purpose limitation tags; at least one is required. |
| `records` | array | One or more normalized external-signal records. |

Required record fields and governed optional fields:

| Field | Type / allowed values | Notes |
| ----- | --------------------- | ----- |
| `signalId` | string | Stable signal identity. |
| `sourceId` | string | Source key for the trusted-source dimension. |
| `sourceAuthority` | string | Publishing authority such as MeteoSwiss, BABS/FOCP, SED-ETH, or FOPH/BAG. |
| `trustTier` | `A`, `B`, `C` | Trust tier; only `A` is auto-evaluated this sprint, while `B` and `C` remain human-curated. |
| `capIdentifier` | string or null | CAP identifier when present. |
| `hazardType` | string | Foreign key to the external hazard-type dimension. |
| `severity` | `Minor`, `Moderate`, `Severe`, `Extreme` | CAP-aligned severity. |
| `certainty` | `Observed`, `Likely`, `Possible`, `Unlikely` | CAP-aligned certainty. |
| `urgency` | `Immediate`, `Expected`, `Future`, `Past` | CAP-aligned urgency. |
| `dangerLevel` | integer 1..5 or null | Swiss warning scale where available. |
| `region` | object | `cantons`, `nuts`, and optional `geoPolygon`. |
| `effective` | date-time or null | Signal effective timestamp. |
| `onset` | date-time | Required event onset timestamp. |
| `expires` | date-time or null | Signal expiry timestamp. |
| `uri` | string or null | Source deep link. |
| `status` | `Actual`, `Test`, `Exercise`, `System` | Non-`Actual` records are quarantined. |
| `mappedScenarioTemplate` | string or null | CSA `ScenarioTemplate` pre-seed where mapped. |
| `defaultLageTier` | integer 1..3 or null | ADR-0024 Lage tier pre-seed. |
| `provenance.ingestedAt` | date-time | Ingestion timestamp. |
| `provenance.connectorVersion` | string | Connector version that produced the record. |
| `provenance.licence` | string | Source licence and attribution obligation; mandatory per signal. |
| `provenance.rawHash` | string | Hash of the raw source payload. |
| `provenance.activeBinding` | `live`, `simulated`, `internal` | Binding mode that produced this record; drives the trust badge. |
| `provenance.fellBackFrom` | `live` or null | Set when the runner fell back from a live binding; null otherwise. |
| `provenance.channelKind` | `external`, `internal` | `internal` for InternalBinding channels derived from gold tables; `external` for all others. |

The derived deduplication key is `sourceId + capIdentifier + hazardType +
region + onset`, bucketed to a time window so overlapping re-publishes collapse
before trigger evaluation. Noise governance is strict: `Test`, `Exercise`, and
`System` records are quarantined and never trigger CSA (`FR-EXT-005`). Only
Trust-A, `Actual` records that satisfy threshold rules can open an advisory CSA
handoff; external signals never mutate capacity, roster, or bed state directly.

#### ext_dim_source trust-badge columns (Sprint 21 provider-plugin refactor)

The `ext_dim_source` dimension table carries per-channel trust-badge columns
populated by the provider-runner service from `provenance.activeBinding`. These
columns flow through the semantic-model measures to CSA/OCA board cards as a
data-driven live/simulated/internal trust badge (FR-EXT-019).

| Column | Type / allowed values | Notes |
| ------ | --------------------- | ----- |
| `ext_data_mode` | `live`, `simulated`, `internal` | Current binding mode; set from `provenance.activeBinding` on the latest ingested record. |
| `ext_trust_tier` | `A`, `B`, `C` | Inherited from the source trust-tier catalogue entry. |
| `ext_last_live_at` | date-time or null | Timestamp of the most recent successfully ingested live record; null if live binding has never succeeded. |
| `ext_fell_back_from` | `live` or null | Mirrors `provenance.fellBackFrom`; set when the channel is in simulated mode due to a live-binding failure. |

The trust-badge propagation chain is:
`provenance.activeBinding` -> `ext_dim_source.ext_data_mode` -> semantic-model measures -> board cards.

### Deprecations

| Contract | Superseded by | Removal | Notes |
| ----- | ----- | ----- | ----- |
| `DC-ONB-CAPACITY-v1` (incl. provider variants `*-HIRSLANDEN-v1`, `*-ZOLLIKERBERG-v1`) | `DC-SUPPLY-LOCATION-v1` + `DC-SUPPLY-ORGANIZATION-v1` | Later sprint — migration PR will move provider variants to `extensions.<provider>` on the new `Location` contract | Sprint 07 keeps both in place; CI continues to validate the deprecated contract until removal. |

### Contract Validation Pattern

1. Producer-side schema validation before publish.
2. Consumer-side compatibility checks before promote.
3. Drift and quality alerts on schema or SLA breaches.
4. Change log and version trace retained for audit.

## Retention and Governance

### Data Classification Baseline

| Class | Description | Example Datasets | Handling Baseline |
| ----- | ----- | ----- | ----- |
| PHI-sensitive | Health and treatment-linked personal data | ADT, discharge details, patient-linked timelines | Swiss residency constraints, strict RBAC, highest audit rigor |
| Operational confidential | Internal operations without direct PHI payloads | Aggregated capacity KPIs, planning metrics | Controlled access, audit trails, policy-based sharing |
| Governance evidence | Logs, lineage, policy and release evidence | Access logs, policy reports, model run IDs | Tamper-resistant retention and audit access model |

### Retention Policy Proposal (MVP)

Retention classes are policy-driven and must be legally validated before go-live.

| Retention Class | Default Retention Target | Applies To |
| ----- | ----- | ----- |
| R1 Operational transient | 30 to 90 days | Raw transient event buffers and retry queues |
| R2 Operational analytics | 13 months | Curated operational trend analytics |
| R3 AI trace and model evidence | 24 months | Forecast/discharge run metadata and grounding trace |
| R4 Compliance and security evidence | 24 to 120 months (policy-dependent) | Access logs, incident and release evidence |
| R5 Legal hold override | Until release of hold | Datasets under litigation/regulatory hold |

Note: EPDG-specific retention obligations for EPR contexts and other legal
obligations may require stricter settings for specific datasets.

### Governance Control Model

1. Data inventory with purpose/legal basis tags (CH-C01).
2. Privacy-by-default and least privilege data access (CH-C02).
3. End-to-end traceability and auditable access trails (CH-C03).
4. DSR-supporting data location and lineage mapping (CH-C04).
5. Residency and cross-border control gates (CH-C05).
6. Incident-ready data and evidence handling controls (CH-C06).

### Purview and Metadata Governance Pattern

1. Use Purview as metadata and evidence accelerator, not as sole control engine.
2. Use IaC for Purview account baseline and security posture.
3. Use controlled operational automation for scans, classifications, and catalog lifecycle.
4. Persist lineage and classification outputs as governance evidence inputs.

## Azure Service Scope and Data Flow Responsibilities

### Azure Health Data Services Scope

Responsibilities:
1. Healthcare interoperability ingress and normalization boundaries.
2. FHIR-oriented canonical exchange model where required.
3. Controlled clinical data boundary into downstream curated data layers.

### Microsoft Fabric Scope

Responsibilities:
1. Curated data products and transformation pipelines.
2. Semantic serving for dashboards and copilot grounding.
3. Governed analytics and operational reporting outputs.

### Data Lake Scope (OneLake and Controlled Landing Zones)

Responsibilities:
1. Durable storage for raw-to-curated lifecycle stages.
2. Dataset partitioning by domain, environment, and classification tier.
3. Retention policy execution and archival transitions.

### End-to-End Data Flow (MVP)

1. Operational and clinical-adjacent events are ingested via interoperability boundaries.
2. Raw and staged datasets land in governed lake zones.
3. Fabric transforms data to curated domain products.
4. AI pipelines consume feature-ready curated datasets and emit versioned outputs.
5. Copilot and dashboards consume governed serving views with trace metadata.
6. Integration outcomes are fed back into curated operations and audit domains.

## Quality, Observability, and Drift Controls

1. Schema conformance checks at ingestion and curation boundaries.
2. Data quality scorecards for completeness, freshness, and validity.
3. Lineage visibility from source event to user-facing output.
4. Drift detection for schema, feature distributions, and downstream SLA breach.
5. Operational alerting for failed pipelines and message recovery paths.

## Requirement Coverage and Traceability Validation

This section validates data-lane coverage and traceability against PRD,
architecture, AI, and compliance baselines.

### PRD Requirement Mapping

| Requirement Set | Coverage in this document | Coverage Status |
| ----- | ----- | ----- |
| FR-DATA-001 to FR-DATA-008 | Data scope, domain model, contracts, service responsibilities, end-to-end flow | Covered |
| FR-GOV-001 | Lineage and source-to-consumption trace controls, governance evidence model | Covered |
| FR-GOV-004 | Governance evidence hooks, retention classes, audit-oriented data domains | Covered |
| FR-GOV-005 | Integration event contracts and partner event data domain | Covered |
| NFR-DQ-001 to NFR-DQ-004 | Contract validation pattern, quality scorecards, drift/observability controls | Covered |
| NFR-COMP-004 | Residency and transfer constraints in contract and governance control model | Covered |
| NFR-COMP-005 | Inventory and legal basis tagging in governance control model | Covered |
| NFR-COMP-006 | DSR-supporting lineage and data location mapping model | Partially Covered (operational workflow pending) |
| NFR-COMP-007 | Residency and cross-border control gates, legal-hold and transfer constraints | Covered |
| NFR-COMP-008 | Incident-ready evidence handling controls and retention classes | Partially Covered (timing matrix pending) |
| NFR-COMP-009 | EPR-specific retention and conformance dependency notes | Partially Covered (EPR pack pending) |
| NFR-COMP-010 | Governance evidence model, retention classes, release evidence hooks | Covered |
| NFR-AI-003 and NFR-AI-004 | AI trace domain, AI output contracts, grounding and versioned output flow | Covered |
| FR-ONB-001 to FR-ONB-003 | Sprint 6 onboarding contracts (`DC-ONB-PATIENT-v1`, `DC-ONB-CAPACITY-v1` + provider extensions) with synthesized SIT datasets | Covered |
| NFR-COMP-011 and NFR-DQ-005 | Minimum-data minimization (validator-enforced), specialty taxonomy versioning and capacity invariants | Covered |

### Compliance Control Mapping

| Compliance Control | Data-lane coverage anchor | Status |
| ----- | ----- | ----- |
| CH-C01 | Domain inventory, legal basis tags, contract mandatory fields | Covered |
| CH-C02 | Classification baseline, least-privilege handling guidance | Covered |
| CH-C03 | Traceability, lineage, audit evidence and quality/observability controls | Covered |
| CH-C04 | DSR-supporting lineage and location mapping | Partially Covered (process implementation pending) |
| CH-C05 | Residency and cross-border gates, retention/legal hold model | Covered |
| CH-C06 | Incident-ready evidence handling and retention classes | Partially Covered (decision timing/runbook linkage pending) |
| CH-C07 | EPR-related data boundary and integration dependency notes | Partially Covered (technical conformance pending) |
| CH-C08 | EPR conformance dependency explicitly tracked in residual gaps | Partially Covered |
| CH-C10 | AI traceability domain and governance evidence model | Covered |

### Validation Outcome

1. Data design coverage is complete at design level for MVP requirements in the
	data and governance lanes.
2. Traceability is now explicit from data constructs to PRD requirement IDs and
	compliance controls.
3. Remaining gaps are implementation tasks, not missing design definitions.

## MVP Deliverables for Data Lane

1. Domain catalogue with owner assignments.
2. First contract pack for ingestion, curation, AI outputs, and integration events.
3. Retention-class policy mapping per dataset group.
4. Data inventory with legal basis and classification tags.
5. Governance evidence hooks for release and compliance reviews.

## Residual Gaps and Next Steps

1. Final legal ratification of retention durations by dataset class.
2. DSR workflow integration with data contract and lineage inventory.
3. EPR-specific conformance controls when EPR integration is enabled.
4. Research secondary-use guardrails if HRA scope is activated.
5. Explicit implementation tracker under docs/compliance or docs/data-platform.
