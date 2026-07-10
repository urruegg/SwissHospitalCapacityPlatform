# OPERATIONS

| Field | Value |
| ----- | ----- |
| **Version** | 1.6.0 |
| **Date** | 2026-07-10 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 1.5.0 (added §Infra deploy governance runbook after the 2026-07-10 SIT auto-deploy incident) |

## Purpose

Define the target operating model for the Swiss Hospital Capacity Platform,
including service ownership, run operations, monitoring, health management,
and incident response.

> **Sprint 00 tenant migration (authoritative as of 2026-07-02):**
> The platform is now operated from Entra tenant `1337187a-4c41-4da9-8fca-731bba7a4329`
> (`MngEnvMCAP164444.onmicrosoft.com`) using subscription `66a9953a-df37-4c51-856c-9971b9bf3e03`
> in region `westus2` (demo/proof-of-technology scope per [ADR-0013](adr/0013-temporary-us-region-demo-scope.md)).
> Old tenant `MngEnvMCAP228255.onmicrosoft.com` is frozen — teardown deferred.
> See [ADR-0012](adr/0012-tenant-migration-to-mcap164444.md) and
> [sprint-00 report](sprints/sprint-00-new-tenantprovisioning.md).

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
| Semantic / ontology stewardship (reference layer + operational layer + crosswalk) | Data platform lead | **Semantic / ontology owner** *(new role — nominated per [ADR-0014](adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) §4; incumbent TBD, target nomination in Sprint 09)* | AI governance lead, product owner, security lead |

### Semantic / Ontology Owner (new role per ADR-0014)

Realises `FR-GOV-ONT-001..003` and anchors `NFR-ONT-001`. See [ADR-0014 §4](adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#4-governance-model-obo-inspired).

1. **Remit.** Authority over the reference ontology (OWL/RDF under `docs/ontology/`), the operational ontology (Fabric IQ), and the crosswalk artefact (`docs/ontology/crosswalk.md`). Approves the semantic change workflow: proposal → domain-owner review → versioned release → downstream impact check.
2. **Change discipline.** Every ontology change follows the same breaking-change control as data contracts (`NFR-MAINT-002`): SemVer, deprecation window, downstream-consumer notification, CI conformance check must be green.
3. **Principles enforced.** Realism (align to OBO Foundry), univocity (one term / one meaning), orthogonality / reuse (import; do not duplicate published ontologies).
4. **Deliverables owned.** The reference-layer skeleton in `docs/ontology/`, the crosswalk in `docs/ontology/crosswalk.md`, the CI conformance workflow, and the ontology entries in [DATA.md](DATA.md) and [PRD.md](PRD.md).
5. **Escalation.** Semantic change disputes escalate to Architecture Working Group. Preview-service exceptions escalate through the `policy/exceptions.json` mechanism ([ADR-0010](adr/0010-policy-as-code-and-release-evidence-gates.md)).
6. **Nomination status (2026-07-02).** Role created; incumbent not yet nominated. Sprint 09 acceptance evidence includes the named individual per [AMA §11.3](reviews/2026-07-01-ama-hcc-northstar-review.md#113-sprint-09-acceptance-evidence-proposed).

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

### Infra deploy governance (2026-07-10)

**Context.** The Sprint 13.1 SIT deploy (2026-07-10 11:51 CET) auto-fired on PR #189 merge because `cd-infra-deploy-sit.yml` triggers on `push` to `main`. This bypassed the AGENTS.md §4 `approved-to-apply` gate. The workflow already declares `environment: sit`, so the fix is a **repo-settings-only change** — no YAML edit.

**Enforcement — one-time repo setup.** Repository admin (`@urruegg`) configures the `sit` and `prod` GitHub Environments with a **required-reviewer protection rule**:

1. Repository → **Settings** → **Environments** → **`sit`** → **Edit**.
2. Under *Deployment protection rules*, enable **Required reviewers** and add `@urruegg` (or a `deploy-approvers` team).
3. Optionally add a **Wait timer** of 0-5 minutes to allow last-minute veto.
4. Save.
5. Repeat for the `prod` environment.

Once configured, every deploy job that carries `environment: sit` (or `prod`) pauses at the `environment:` step and shows a "Waiting for review" state in the Actions UI. A designated reviewer clicks **Approve** to proceed, or **Reject** to abort. GitHub records the approval identity in the environment history.

**PR conformance checklist** (for every PR that touches `infra/**`):

- [ ] `az bicep build --file infra/main.bicep` clean locally.
- [ ] `az deployment group what-if -g rg-ihzhhpf-sit --template-file infra/main.bicep --parameters infra/environments/sit.bicepparam` clean, no unexpected `~ Modify` or `- Delete`.
- [ ] What-if output pasted into the PR description.
- [ ] PR description ends with an explicit "Approval flow" section stating: `Merging this PR triggers cd-infra-deploy-sit.yml. The workflow will pause at the sit environment gate — approve via the Actions UI to complete the apply.`
- [ ] If the change is destructive (`- Delete` in what-if), the PR carries a `destructive-infra` label and an explicit `approved-to-apply` reply from the approver *before* merge (not just at the gate).

**Post-deploy validation** (mandatory after every gated apply):

1. `az deployment group show -g rg-ihzhhpf-sit --name deploy-sit-<run-id>` confirms `provisioningState=Succeeded`.
2. Spot-check the affected resource types via `az resource list -g rg-ihzhhpf-sit --resource-type <type>` to confirm expected count.
3. If the deploy left the outer deployment `Failed` with partial resource landing, the recovery PR must include a `what-if` that captures the corrected state — see PR #190 (Redis migration recovery) as reference precedent.

**Rollback**: `az deployment group create --mode Incremental --template-file infra/main.bicep --parameters infra/environments/sit.bicepparam` is idempotent — pushing a "revert" PR that reverts the offending Bicep changes will bring SIT back to the prior state on next apply. There is no separate rollback command.

## Capacity and Cost Operations

1. Track daily event and copilot volume against assumed demand envelope.
2. Monitor capacity headroom for burst scenarios (3x target windows).
3. Track cost-to-serve KPIs: cost per copilot turn and cost per pipeline run.
4. Review monthly cost anomalies and optimization opportunities against BVA targets.

## Reliability and Disaster Recovery Operations

The reliability/DR target state â€” recovery classes R1/R2/R3, RTO/RPO targets, failover
boundaries by data class, and the DR rehearsal evidence model â€” is defined in
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
> [`docs/sprints/sprint-05/phase-3-reliability-dr.md`\](sprints/sprint-05/phase-3-reliability-dr.md).
> This section defines the recurring operational checkpoints they populate.

## Live Risk Register (new)

Added 2026-07-02 (v1.4.0) per [ADR-0014](adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) §5 to give operations a single place to track live vendor/product-readiness go/no-go items that gate architectural commitments. Distinct from **incident** tracking (§ Incident and Problem Management) and from **DR rehearsal evidence** (§ Reliability and Disaster Recovery Operations).

**Owner:** each row names an accountable role who owns the go/no-go call. **Review cadence:** monthly; escalate to Architecture Working Group when severity is `H` or trigger date passes without decision.

| Risk ID | Description | Category | Severity | Trigger / Go-No-Go | Owner | Fallback | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OPS-RISK-01 | **Fabric IQ Ontology Switzerland-region GA + DPA equivalence** — gates the regulated-path operational ontology layer per [ADR-0014](adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) §5 gate G-C | Technical / Vendor | **H** | Microsoft publishes firm GA date for `switzerlandnorth` + DPA equivalence with GA Fabric components. Review monthly; escalate if no update by 2026-Q4. | Semantic / ontology owner (RACI table above) | Regulated operational layer runs on GA property-graph fallback per [ADR-0014 §3](adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#3-sprint-09-delivers-the-minimum-viable-ontology-mvo); demo scope continues on Fabric IQ preview in `westus2` per [ADR-0013](adr/0013-temporary-us-region-demo-scope.md) | [AMA review R-01](reviews/2026-07-01-ama-hcc-northstar-review.md#11-key-risks-h--high-m--medium-l--low), [ADR-0014 gate G-C](adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#5-explicit-go-no-go-gates) |
| OPS-RISK-02 | **ADR-0013 westus2 demo exception expiry** (`EX-2026-07-02-westus2-demo`) — 90-day window per [`policy/exceptions.json`](../policy/exceptions.json) | Compliance / Governance | **M** | Expiry 2026-09-30. Renewal review required by 2026-09-15. | Compliance lead | Migrate demo workloads back to `switzerlandnorth` (subject to service GA); alternatively renew exception with fresh 90-day window via [ADR-0010](adr/0010-policy-as-code-and-release-evidence-gates.md) mechanism | [ADR-0013](adr/0013-temporary-us-region-demo-scope.md), [`policy/exceptions.json`](../policy/exceptions.json) |
| OPS-RISK-03 | **Direct Lake preview stability** — semantic model refresh or Direct Lake query returns stale/inconsistent results during Fabric preview volatility in `westus2` demo scope | Technical / Vendor | **M** | Sustained Direct Lake query anomaly (>1 recurrence in a review cycle) or Microsoft preview-flag toggle. Review monthly with T4 owner; escalate if regressions block Sprint 09 dashboard smoke test. | Semantic / ontology owner | Fall back to Import mode with 15-min scheduled refresh (RB-03 fallback pattern validated in Sprint 00); monitor Fabric release notes; long-term path per [ADR-0014 §3](adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#3-sprint-09-delivers-the-minimum-viable-ontology-mvo) | [Design spec §7.5](superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#75-risk-register), [ADR-0013](adr/0013-temporary-us-region-demo-scope.md) |
| OPS-RISK-04 | **Fabric F2 forgot-to-pause** — SIT capacity `fabricihzhhpfsit` left Active over weekend/off-hours, accruing unnecessary Fabric CU cost | Cost / Operational hygiene | **L-M** | Any weekend SIT-capacity-active >8 h without an open sprint-execution window, or Azure Budget alert firing at 50% MTD. | Platform ops | [DX.2 `Suspend-FabricCapacity.ps1`](../infra/scripts/Suspend-FabricCapacity.ps1) + [`fabric-capacity-lifecycle.yml`](../.github/workflows/fabric-capacity-lifecycle.yml) `workflow_dispatch` + Azure Budget alert at 50% MTD; runbook [`fabric-capacity-lifecycle.md`](runbooks/fabric-capacity-lifecycle.md) | [Design spec §7.5](superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#75-risk-register), [DX.2 runbook](runbooks/fabric-capacity-lifecycle.md) |
| OPS-RISK-05 | **3-hospital calibration realism drift** — synthetic simulator patterns (USZ / LUKS / SZB presets) diverge from HCC LUKS reference over time (MAPE > 15%) | Data / Quality | **M** | MAPE > 15% on any weekly HCC pattern conformance replay, or reference-fixture rebase against updated HCC PNG. | Semantic / ontology owner | Sprint 08 HCC pattern conformance test [`test_seasonal_profile.py`](../apps/sim-capacity/tests/test_seasonal_profile.py) enforces MAPE < 15% in CI (blocking); nightly re-validation harness deferred to Sprint 10 | [Design spec §7.5](superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#75-risk-register), [ADR-0016](adr/0016-no-phi-in-mvp-demo-scope.md) |

### Risk Register Discipline

1. **Add rule.** New rows added on ADR approval whenever a decision is gated on an external event (vendor GA, regulatory change, partner commitment).
2. **Close rule.** Rows are closed when either the trigger fires (positive close: recorded in row's history + monthly review) or the fallback is activated (negative close: incident-reported + ADR-supersession or amendment PR).
3. **Traceability.** Every row cites its source ADR / AMA review section. Rows without a source citation are invalid and must be corrected before the next monthly review.
4. **Escalation.** Severity `H` rows appear in the monthly Architecture Working Group agenda automatically.

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
| FR-GOV-ONT-001 to FR-GOV-ONT-003 *(proposed)* | Semantic / ontology owner role (RACI baseline), semantic change workflow, two-layer conformance CI — per [ADR-0014](adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) |
| NFR-ONT-001 *(proposed)* | Ontology versioning + governed reference↔operational crosswalk + CI check — per [ADR-0014 §4](adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#4-governance-model-obo-inspired) |

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

