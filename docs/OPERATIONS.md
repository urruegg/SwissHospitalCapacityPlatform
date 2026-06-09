# OPERATIONS

| Field | Value |
| ----- | ----- |
| **Version** | 1.2.0 |
| **Date** | 2026-06-09 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 1.1.0 (Sprint 05 reliability/DR profile and DR evidence checkpoints) |

## Purpose

Define the target operating model for the Swiss Hospital Capacity Platform,
including service ownership, run operations, monitoring, health management,
and incident response.

This baseline supports the MVP scope and is aligned to the platform constraints
already defined in PRD, architecture, security, compliance, data, and ALM plans.

## Source Baseline

This document aligns to:
1. docs/PRD.md
2. docs/ARCHITECTURE.md
3. docs/SECURITY.md
4. docs/COMPLIANCE.md
5. docs/DATA.md
6. docs/ALM_PLAN.md
7. docs/TEST.md

## Target Operating Model (TOM)

### Operating Principles

1. Provider-local operational ownership with centralized governance controls.
2. 24x7 operational visibility for critical data and AI pathways.
3. Zero Trust and compliance-by-design are part of run operations, not post-checks.
4. Evidence-first operations: every critical incident and release is auditable.
5. PHI-sensitive controls are fail-safe and default deny for cross-border exposure.

### Operating Domains

| Domain | Responsibility | Primary Capability |
| ----- | ----- | ----- |
| Platform operations | Core service reliability and run-state control | Availability, deployment health, environment hygiene |
| Data operations | Feed quality, latency, and lineage continuity | Freshness, completeness, recoverability |
| AI operations | Forecast/discharge model and copilot inference health | Model run reliability, inference latency, response quality |
| Integration operations | Partner workflow and callback reliability | Retry, dead-letter handling, endpoint health |
| Security and compliance operations | Access, policy, incident, and evidence controls | Identity governance, policy conformance, audit readiness |

### Roles and Accountability (RACI Baseline)

| Capability | Accountable | Responsible | Consulted |
| ----- | ----- | ----- | ----- |
| Service reliability and release gating | Platform lead | SRE and platform ops | Security lead, product owner |
| Data quality and data incident triage | Data platform lead | Data operations | AI lead, integration lead |
| AI run reliability and guardrails | AI governance lead | AI engineering and MLOps | Platform ops, security lead |
| Integration incident handling | Integration lead | Integration operations | Platform ops, compliance lead |
| Security/privacy incident governance | Security lead | Security operations | Compliance lead, legal/privacy officer |

## Service Health Model

### Health States

1. Healthy: all critical SLO indicators within threshold.
2. Degraded: one or more non-critical indicators outside threshold, core service still operational.
3. Major Incident: critical pathway unavailable or unsafe for operations use.
4. Controlled Maintenance: planned service-impacting activity with approved change window.

### Critical Service Pathways

1. Event ingestion to curated data availability.
2. Forecast pipeline and hourly publish path.
3. Discharge scoring and recommendation path.
4. Copilot grounding, response, and citation path.
5. Partner orchestration and acknowledgement loop.

## SLI and SLO Baseline

### Reliability and Performance SLOs (Initial)

| SLO Area | Initial Target | Measurement Basis |
| ----- | ----- | ----- |
| Platform availability (critical operations surfaces) | 99.9 percent monthly | Availability checks and request telemetry |
| Data freshness for critical operational feeds | 95 percent within agreed freshness window | Ingestion lag metrics |
| Forecast pipeline success rate | 99 percent successful scheduled runs | Pipeline run telemetry |
| Copilot standard grounded response latency | P95 under 4 seconds | End-to-end request telemetry |
| Integration workflow completion reliability | 99 percent with retry and recovery policy | Workflow and queue telemetry |
| MTTD for high-severity incidents | under 10 minutes | Alert-to-acknowledge timing |
| MTTR for priority incidents | under 60 minutes for P1 | Incident lifecycle metrics |

Note: Final SLO values are validated in implementation planning and can be
re-baselined with measured production telemetry.

## Monitoring and Observability Baseline

### Monitoring Stack

1. Azure Monitor as central observability control plane.
2. Application Insights for application and API telemetry.
3. Log Analytics workspace for centralized logs and KQL analytics.
4. Azure Monitor Alerts and Action Groups for operational escalation.
5. Workbooks and dashboards for command-center and run-team visibility.

### Application Insights Monitoring Requirements

Application Insights is mandatory for MVP application and API components.

Required telemetry categories:
1. Request telemetry: throughput, duration, response codes, dependency latency.
2. Exception telemetry: handled and unhandled exceptions with correlation IDs.
3. Dependency telemetry: downstream call performance and failure profile.
4. Availability telemetry: synthetic availability tests on critical user journeys.
5. Custom events/metrics: forecast run ID, discharge scoring run ID,
   copilot session/response IDs, integration workflow correlation IDs.

Required implementation controls:
1. Distributed tracing with consistent operation and correlation IDs across services.
2. PII/PHI-safe telemetry strategy with explicit redaction and minimization rules.
3. Environment-level sampling strategy that preserves incident diagnostics.
4. Alert rules for latency, error-rate, availability, and pipeline-run failures.
5. Workbook views for platform health, data latency, AI pipeline health,
   and integration reliability.

### Core Alerting Baseline

| Alert Category | Trigger Baseline | Priority |
| ----- | ----- | ----- |
| Availability alert | Synthetic test failure beyond threshold | P1 |
| Latency alert | P95 response time breach for sustained interval | P2 |
| Error rate alert | 5xx/error percentage above threshold | P1/P2 |
| Data freshness alert | Critical feed lag beyond SLA | P1/P2 |
| Forecast/discharge run failure | Consecutive run failures or stale publish | P1 |
| Integration dead-letter growth | Dead-letter queue growth beyond threshold | P2 |
| Security anomaly alert | Privilege escalation or suspicious access pattern | P1 |

## Incident and Problem Management

### Incident Severity Model

1. P1: Critical operational pathway unavailable or high-risk safety/compliance state.
2. P2: Major degradation impacting decision cycle quality or timeliness.
3. P3: Localized defect with workaround.
4. P4: Minor issue with low operational impact.

### Incident Workflow Baseline

1. Detect via monitoring and/or user report.
2. Classify severity and assign incident commander.
3. Stabilize service with mitigation and communication updates.
4. Recover full function and verify health criteria.
5. Produce incident report with root cause and corrective actions.
6. Link evidence and remediation tasks to GitHub issue tracking.

### PHI-Sensitive Runbook Rule

1. Cross-region PHI failover remains default deny.
2. Activation requires approved compliance runbook and explicit authority sign-off.
3. Every activation decision is logged with timestamp, approver, and rationale.

## Operational Readiness and Change Control

### Release-to-Run Entry Criteria

1. All required TEST and ALM quality gates are passed.
2. Monitoring/alerting coverage is active for changed components.
3. On-call ownership and escalation paths are confirmed.
4. Runbook updates are completed and reviewed.
5. Compliance and security evidence impact is documented.

### Change Control Baseline

1. Standard changes: low-risk, pre-approved patterns.
2. Normal changes: reviewed and approved with rollback plan.
3. Emergency changes: time-critical, post-change review mandatory.

## Capacity and Cost Operations

1. Track daily event and copilot volume against assumed demand envelope.
2. Monitor capacity headroom for burst scenarios (3x target windows).
3. Track cost-to-serve KPIs: cost per copilot turn and cost per pipeline run.
4. Review monthly cost anomalies and optimization opportunities against BVA targets.

## Reliability and Disaster Recovery Operations

The reliability/DR target state — recovery classes R1/R2/R3, RTO/RPO targets, failover
boundaries by data class, and the DR rehearsal evidence model — is defined in
[`docs/operations/reliability-dr-profile.md`](operations/reliability-dr-profile.md)
(ADR-0009). Operations is the accountable owner (`OPS`) for the evidence cadence.

### DR Test Evidence Checkpoints

1. Each DR rehearsal records the schema fields in the reliability/DR profile
   (`scenarioId`, `systemsInScope`, `targetRtoRpo`, `actualRtoRpo`, `passFailResult`,
   `gaps`, `owner`, `retestDate`).
2. Every in-scope stateful dependency keeps a SIT restore-proof artifact fresh
   (<= 90 days) before PROD promotion.
3. Rehearsal cadence: quarterly for R1/R2 workflows, semiannual for R3; monthly
   evidence-freshness review.
4. PHI cross-region failover stays default-deny; activation requires the exception gate
   in the reliability/DR profile.

> The first SIT DR rehearsal and restore-proof capture were executed in Phase 3
> (`RV-02`, `RV-07`, `RV-11`); see the
> [DR Rehearsal and SIT Restore-Proof runbook](runbooks/dr-rehearsal-runbook.md)
> and the Phase 3 evidence record
> [`sprints/sprint-05/phase-3-reliability-dr.md`](../sprints/sprint-05/phase-3-reliability-dr.md).
> This section defines the recurring operational checkpoints they populate.

## Traceability to Requirements

| Requirement Family | Operations Coverage |
| ----- | ----- |
| FR-GOV-001 and FR-GOV-004 | Auditable telemetry, incident evidence, run reporting |
| FR-GOV-003 | DEV, SIT, PROD readiness and promotion controls via ALM and run gates |
| FR-GOV-005 and FR-GOV-006 | Policy-driven integration operations and provider-local control model |
| NFR-REL-001 to NFR-REL-004 | Continuous operations, restartability, degradation, and retry handling |
| NFR-PERF-001 to NFR-PERF-005 | Freshness, latency, throughput, and interactive performance monitoring |
| NFR-SEC-001 to NFR-SEC-004 | Operational access control, auditing, secure secret handling |
| NFR-COMP-004 to NFR-COMP-010 | Residency-safe operations, privacy incident governance, evidence cadence |
| NFR-AI-003 to NFR-AI-005 | Model and response traceability, AI run governance and control |

## Operational KPI Baseline

### Reliability and Health KPIs

1. Monthly availability for critical pathways.
2. Incident count by severity and service domain.
3. MTTD and MTTR by severity.
4. Forecast/discharge run success rate.

### Operational Effectiveness KPIs

1. Data freshness compliance rate.
2. Integration workflow success and dead-letter recovery rate.
3. Copilot P95 response latency and response error rate.
4. Percentage of incidents with complete post-incident evidence.

### Governance KPIs

1. Monitoring coverage completeness for in-scope services.
2. Alert quality ratio (actionable alerts versus total alerts).
3. Compliance evidence completeness per release cycle.
4. Number of unauthorized PHI transfer/failover events (target: zero).

## Initial Implementation Backlog

1. Define environment-specific SLO thresholds and alert values.
2. Implement Application Insights instrumentation standards in app/API components.
3. Create baseline Azure Monitor Workbooks for service, data, AI, and integration health.
4. Define incident communication templates and escalation matrix.
5. Add operations readiness checklist referenced by release PR template.
6. Add monthly operations review cadence with KPI trend reporting.
