# Sprint 6 - Minimal-Data Onboarding and Specialty-Driven Capacity Onboarding

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-06-09 |
| **Author** | Urs Rueegg |
| **Status** | Planned |
| **Previous Version** | 1.0.0 (initial Sprint 6 onboarding baseline) |

## Sprint Goal

Baseline and implement Sprint 6 onboarding capabilities using a minimum-sensitive-data design,
with hospital-capacity onboarding driven by treatment-specialty metadata.

This sprint operationalizes the review outcomes and extends provider onboarding coverage with
Klinik Hirslanden and Spital Zollikerberg analysis.

## Review Inputs and Baseline References

Primary review inputs:
1. `docs/reviews/2026-06-09-ama-cto-mentor-Review.md`
2. `docs/reviews/2026-06-09-ama-sd-review.md`

Additional architecture/data baseline:
1. `docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform analysis.md`
2. `docs/PRD.md`
3. `docs/SD.md`
4. `docs/ARCHITECTURE.md`
5. `docs/DATA.md`
6. `docs/COMPLIANCE.md`

## Guiding Principles (Locked for Sprint 6)

1. Hotel guest onboarding and capacity handling is the operating analogy for hospital flow onboarding.
2. Minimum-sensitive-data by default is mandatory for onboarding flows.
3. Onboarding is split into two lanes:
   - patient onboarding with least required metadata,
   - hospital capacity onboarding with treatment-specialty metadata.
4. Deterministic components are implemented as services/workflows, not AI agents by default.

## Scope

### In scope

1. Define and baseline patient onboarding minimal metadata contract.
2. Define and baseline specialty-driven capacity onboarding contract.
3. Incorporate provider specialty and capacity signals for:
   - Klinik Hirslanden,
   - Spital Zollikerberg.
4. Map onboarding requirements to FR/NFR/CH controls and evidence model.
5. Define provider onboarding sequence and acceptance gates for Sprint 6.
6. Kickstart data-platform build with IaC and synthesized test data.
7. Deliver MVP Phase 1 agent implementation scope:
   - Operations Orchestrator Agent (OOA),
   - Discharge Coordination Agent (DCA),
   - Bed Management Copilot Agent (BMCA).

### Out of scope

1. Full cross-provider multi-tenant runtime implementation.
2. Production rollout for new providers.
3. Clinical decision automation without human approval.

## New Sprint 6 Requirement Delta (to be baselined)

### Functional

1. `FR-ONB-001` The platform shall onboard new patients using a minimum required metadata set only.
2. `FR-ONB-002` The platform shall onboard hospital capacity using specialty-tagged metadata.
3. `FR-ONB-003` The platform shall support provider-specific specialty profiles for capacity planning.
4. `FR-ONB-004` The platform shall classify onboarding workflows as deterministic service vs agentic flow using a documented criterion.

### Non-functional

1. `NFR-COMP-011` Onboarding data contracts shall enforce minimum-sensitive-data controls and purpose tags.
2. `NFR-SEC-005` Onboarding identity and cross-tenant boundaries shall be explicit and auditable.
3. `NFR-DQ-005` Specialty metadata shall include quality checks and controlled versioning.
4. `NFR-REL-005` Onboarding services shall remain available under defined degraded-mode behavior.
5. `NFR-MAINT-005` Sprint 6 onboarding and MVP agent services shall be deployable through IaC-first pipelines with reproducible environment bootstrap.

## MVP Agent Scope for Sprint 6

### Phase 1 mandatory MVP agents

1. Operations Orchestrator Agent (OOA)
2. Discharge Coordination Agent (DCA)
3. Bed Management Copilot Agent (BMCA)

### Optional agents (deferred to Phase 3)

1. Demand Forecasting Agent (DFA)
2. Integration Workflow Agent (IWA)
3. Data Quality and Semantics Agent (DQSA)
4. Compliance and Safety Agent (CSA)
5. Explainability and Audit Agent (EAA)

## Data Platform Kickstart (IaC + Synthesized Data)

Sprint 6 starts the executable build lane for data-platform readiness using
infrastructure-as-code and non-production synthesized datasets.

### Mandatory Phase 1 deliverables

1. IaC modules and environment wiring for data-platform bootstrap paths used by
   OOA/DCA/BMCA MVP flows.
2. Synthesized onboarding datasets for SIT test execution:
   - patient-minimum onboarding metadata,
   - specialty-capacity onboarding metadata,
   - provider extension datasets for Hirslanden and Spital Zollikerberg.
3. Contract and schema validation checks for synthesized onboarding datasets in CI.
4. Traceability mapping from synthesized dataset artifacts to FR/NFR/CH controls.

## Provider Extension for Capacity Onboarding

### Klinik Hirslanden incorporation

1. Capacity onboarding must include specialty-weighted metadata for high-volume domains:
   - surgery and visceral surgery,
   - cardiology,
   - gynecology and obstetrics,
   - orthopedics/sports medicine,
   - urology,
   - neurosurgery.
2. Capacity metadata must include elective pipeline influences:
   - OR schedule pressure,
   - specialty-specific bed demand windows,
   - LOS calibration signal.

### Spital Zollikerberg incorporation

1. Capacity onboarding must include specialty and care-mode signals for:
   - internal medicine,
   - gynecology and obstetrics,
   - neonatology,
   - orthopedics/spine,
   - surgery,
   - emergency intake routing.
2. Capacity metadata must include Hospital-at-Home extension indicators:
   - virtual ward capacity contribution,
   - discharge pathway type (`conventional`, `hah-transfer`, `post-acute`),
   - telemetry-enabled readiness flags where contractually in scope.

## Phase Plan

### Phase 0 - Sprint 6 control bootstrap

1. Create Sprint 6 umbrella and linked phase issues.
2. Create Sprint 6 requires-validation register for onboarding and provider-extension deltas.
3. Publish PR evidence checklist with FR/NFR/CH mapping for new onboarding controls.

### Phase 1 - Baseline document updates

1. Update `docs/PRD.md` with onboarding FR/NFR deltas.
2. Update `docs/SD.md` and `docs/ARCHITECTURE.md` with onboarding lane design and deterministic classification rule.
3. Update `docs/DATA.md` with patient-minimum and specialty-capacity contract schemas.
4. Update `docs/COMPLIANCE.md` with minimum-data and re-identification controls for onboarding.
5. Add Sprint 6 MVP implementation baseline for OOA/DCA/BMCA with explicit IaC component mapping.
6. Add synthesized data generation and validation plan for SIT test cycles.

### Phase 2 - Policy and control enforcement

1. Add policy-as-code checks for onboarding minimum-data contracts.
2. Add specialty metadata validation and schema gate checks.
3. Add cross-tenant/onboarding identity boundary checks where applicable.
4. Enforce synthesized-data quality and minimization checks as required SIT gate criteria.

### Phase 3 - Reliability and provider onboarding evidence

1. Validate onboarding degraded-mode behavior and recovery controls.
2. Produce SIT evidence for Hirslanden and Zollikerberg specialty-capacity onboarding datasets.
3. Capture residual risk acceptance for provider-specific onboarding assumptions.
4. Optional agent wave (DFA/IWA/DQSA/CSA/EAA) can be onboarded in this phase when
   Phase 1 and Phase 2 gates are green.

### Phase 4 - Hardening and Sprint closure

1. Validate deterministic classification coverage (agent vs service).
2. Run golden-task checks for onboarding control paths.
3. Produce Sprint 6 closeout evidence and recommendation for next rollout increment.

## Definition of Done (Sprint 6)

1. All onboarding deltas are baselined across PRD/SD/Architecture/Data/Compliance docs.
2. Hirslanden and Spital Zollikerberg specialty-capacity onboarding is documented with explicit metadata contracts.
3. Minimum-sensitive-data controls are mapped to policy checks and evidence artifacts.
4. Sprint 6 issue/phase/PR traceability is complete and auditable.
5. OOA/DCA/BMCA MVP Phase 1 scope is implementation-ready with IaC mapping and SIT synthesized data validated.
6. Optional agent backlog for Phase 3 is explicitly documented and non-blocking for Phase 1 kickoff.

## Initial Risks and Mitigations

| Risk | Severity | Mitigation |
| ----- | ----- | ----- |
| Specialty metadata heterogeneity across providers | High | Versioned specialty taxonomy mapping and provider adapter contracts |
| Quasi-identifier re-identification through onboarding attributes | High | Mandatory minimization + re-identification risk rule in compliance and policy gate |
| Over-agentization of deterministic onboarding flows | Medium | Enforce deterministic classification criterion and review gate |
| Hospital-at-Home extensions over-complicate baseline model | Medium | Keep HaH fields optional and provider-scoped in contract v1 |

## Execution Note

Sprint 6 follows the same issue-driven, evidence-first model used in Sprint 05,
with explicit SIT gates before any PROD recommendation.
