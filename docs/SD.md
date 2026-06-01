# SD

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.1 |
| **Date** | 2026-06-01 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 1.0.0 (initial MVP solution design baseline) |

## Purpose

This document defines the MVP Solution Design baseline for the Swiss
Hospital Capacity Platform.

It translates requirements and architecture decisions into an implementable
solution shape across data, AI, app, integration, security, and operations.

## Source Baseline

This design is derived from and constrained by:
- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/AI.md`
- `docs/COMPLIANCE.md`
- `docs/SECURITY.md`
- `docs/adr/0001-runtime-is-github-copilot-coding-agent.md` and current ADR set

## MVP Scope

### In Scope

1. Provider-internal operational platform for one provider deployment at a time.
2. Near-real-time ingestion and curated operational datasets.
3. 72-hour demand forecast and discharge-readiness scoring.
4. React-based command-center experience and grounded copilot support.
5. Integration orchestration with external partner endpoints.
6. Zero Trust controls, Swiss residency constraints, and audit evidence baseline.

### Out of Scope

1. Multi-provider shared tenancy.
2. Preview-only features on the MVP critical path.
3. Fabric IQ Ontology dependency for MVP acceptance.
4. Foundry-hosted runtime agents.

## Design Principles

1. GA-only services in MVP critical path.
2. Swiss-first residency for PHI-sensitive data and AI inference.
3. Zero Trust by default across identity, network, workload, and data.
4. Evidence-first governance for compliance and auditability.
5. IaC-first infrastructure with operational automation for non-declarative areas.
6. Degraded-mode support over hard failure where clinically safe.

## Solution Overview

### Logical Domains

| Domain | MVP Responsibility | Primary Services |
| ----- | ----- | ----- |
| Experience | Operations UI and copilot interaction | React app on Azure App Service or Static Web Apps |
| API and agent runtime | Request handling, orchestration, policy checks | Azure Container Apps |
| Data ingestion and curation | Source normalization and serving datasets | Azure Health Data Services, Microsoft Fabric |
| AI decisioning | Forecasting, discharge scoring, grounded inference | Azure Machine Learning, Azure OpenAI |
| Integration | External partner workflow and acknowledgements | Azure Logic Apps, Service Bus |
| Security and governance | Identity, key management, policy, logs, evidence | Entra ID, Key Vault, Policy, Monitor, Purview |

### Region and Environment Topology

- Primary region: Switzerland North
- Secondary region: Switzerland West (failover gated by compliance runbook)
- Environments: DEV, SIT, PROD
- Promotion model: Git-first with environment approval gates

## Core Component Design

### 1) Experience Layer (React MVP Channel)

Responsibilities:
- Capacity command-center views.
- Copilot prompt and response interaction with citations.
- Role-aware UI actions.

Key controls:
- Entra-authenticated sessions.
- Role-based access and action guardrails.
- Full interaction telemetry and audit metadata.

### 2) API and Runtime Layer

Responsibilities:
- Route user requests to data and AI paths.
- Enforce policy checks before execution.
- Aggregate responses and evidence metadata.

Key controls:
- Managed identity for downstream access.
- Request-level authorization and safety checks.
- Correlation IDs across request, model call, and side effects.

### 3) Data Platform Layer

Responsibilities:
- Ingest and normalize operational signals (ED, ADT, bed-state, discharge).
- Maintain curated datasets and semantic serving views.
- Preserve source-to-consumption traceability.

Key controls:
- Data classification and minimization for PHI paths.
- Dataset lineage and quality checks.
- Residency enforcement by dataset class.

### 4) AI Layer

Responsibilities:
- Run forecast and discharge scoring pipelines.
- Support grounded copilot inference with context references.
- Persist model and response provenance.

Key controls:
- PHI inference only on approved regional deployment types.
- Block Global, Data Zone, and Developer deployment types for PHI scenarios.
- Advisory-only response framing with traceability metadata.

### 5) Integration Layer

Responsibilities:
- Trigger external coordination workflows.
- Capture partner acknowledgements.
- Handle retries and exceptions.

Key controls:
- Authenticated partner integration boundaries.
- Queue-based backpressure and retry control.
- Full event audit logging for outbound and inbound exchanges.

## End-to-End Flow (MVP)

1. Source systems emit operational events.
2. Ingestion normalizes and lands data into curated platform stores.
3. Forecast and discharge pipelines generate scored outputs.
4. React UI and copilot APIs query governed context and AI outputs.
5. API returns responses with citations, timestamps, and trace metadata.
6. Actionable events trigger Logic Apps partner workflows.
7. Acknowledgements are written back and surfaced in operational views.
8. Logs and evidence artifacts are emitted for governance review.

## Non-Functional Design Targets

### Performance and Demand Targets (Planning Baseline)

- Operational source events: 180000 per day baseline.
- Burst headroom target: 3x average in 10-minute windows.
- Copilot peak concurrency target: 120 users.
- Interactive response objective: P95 under 4 seconds for standard grounded paths.

### Reliability Targets

- Continuous operation (not batch-only).
- Restartable data and AI pipelines.
- Graceful degradation for non-critical dependency failures.

### Security Targets

- Least-privilege access and just-in-time admin elevation.
- No secrets in code or static app configuration.
- Centralized auditability for access and privileged actions.

## Security and Compliance Design Mapping

### Requirement Coverage

- FR-GOV-001/002/004/005/006 through policy, audit, and access controls.
- NFR-SEC-001 to NFR-SEC-004 through identity, logging, integration auth,
  and secretless workload design.
- NFR-COMP-004 to NFR-COMP-010 through residency, incident, evidence,
  EPR-aware control model, and compliance workflows.

### Control Coverage

This design is aligned to the compliance control model CH-C01 to CH-C10.
Current design coverage is complete; residual gaps are implementation tasks:
1. DSR process operationalization.
2. Cross-border transfer legal sign-off workflow.
3. Privacy incident timing matrix.
4. EPR conformance pack when EPR is enabled.
5. AI override and safety acceptance metrics.

## IaC and Delivery Design

### IaC-first Controls

Implement in Bicep or Terraform:
1. Resource topology, identity, and networking.
2. Key Vault, diagnostics, and policy assignments.
3. AI account and deployment resources.
4. Environment-scoped RBAC and baseline governance resources.

### Hybrid Operational Controls

Implement via scripted ops workflows:
1. Purview collections, scans, and policy lifecycle.
2. Access recertification and evidence collection.
3. Incident simulation and runbook validation.

## Implementation Plan (MVP)

### Phase 1: Foundation

1. Establish environment and network baseline.
2. Deploy core platform resources and identity model.
3. Enforce policy and diagnostic baseline.

### Phase 2: Data and AI Core

1. Integrate source ingestion and curated datasets.
2. Implement forecast and discharge scoring pipelines.
3. Establish AI inference path with Swiss PHI restrictions.

### Phase 3: Experience and Integration

1. Deliver React command-center and copilot UI.
2. Deliver API orchestration and citation-capable responses.
3. Deliver partner workflow integration and acknowledgement loop.

### Phase 4: Hardening and Readiness

1. Validate performance and concurrency assumptions.
2. Validate security, compliance, and evidence gates.
3. Execute readiness review for MVP go/no-go.

## Open Decisions

1. Final service SKUs and sizing by measured load test outcomes.
2. Exact FHIR profile and message-set boundaries per provider.
3. EPR integration timing and conformance sequencing.
4. Recovery objectives by data class and workflow criticality.

## Acceptance Criteria for MVP Solution Design

1. All MVP in-scope capabilities are mapped to implementable components.
2. Security and compliance controls are mapped to design and operations evidence.
3. Architecture constraints (GA-only, Swiss PHI controls, React MVP channel)
   are reflected without contradiction.
4. Residual risks and implementation dependencies are explicit and trackable.

## Notes

This document is the first draft solution design baseline.
It is intended to be refined through implementation planning and measured
validation results in subsequent sprints.
