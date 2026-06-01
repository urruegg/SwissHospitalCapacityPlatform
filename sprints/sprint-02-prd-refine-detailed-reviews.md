# Sprint 2 - PRD Refine Detailed Reviews

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-01 |
| **Author** | Urs Rueegg |
| **Status** | Completed |
| **Previous Version** | N/A |

## Sprint Goal

Refine the Sprint 1 PRD baseline by running detailed cross-domain reviews for
compliancy, security, architecture, AI, availability, and demand; then capture
the validated decisions, traceability, and residual gaps for implementation.

## Trigger Model

This sprint refinement is executed as a GitHub Issue-driven run. The sprint
issue is the tracking anchor, and `@copilot` is the execution trigger for
review and document updates.

## Traceability

- GitHub Issue: [#5](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/5)
- GitHub Project: Swiss Hospital Capacity Platform Delivery
- Baseline PRD: `docs/PRD.md`
- Review artefacts:
  - `docs/ARCHITECTURE.md`
  - `docs/AI.md`
  - `docs/COMPLIANCE.md`
  - `docs/SECURITY.md`

## Scope

### In scope

- Validate PRD non-functional requirements against the reviewed architecture.
- Validate Swiss compliance posture and legal-control traceability.
- Validate Zero Trust security pattern coverage against PRD and compliance controls.
- Validate AI deployment constraints for GA, residency, and PHI-safe inference paths.
- Validate availability and demand assumptions against architecture stress patterns.
- Record validated coverage and implementation gaps with explicit ownership direction.

### Out of scope

- Production deployment changes.
- New service onboarding beyond existing architecture decisions.
- Legal opinion issuance.
- Destructive infrastructure operations.

## Planned Work Items

1. Review current PRD and extract validation targets for each review domain.
2. Run architecture and AI challenge validation against NFR demand and availability assumptions.
3. Map compliance controls to architecture and security controls.
4. Validate security baseline coverage and identify remaining implementation gaps.
5. Update and align documents with explicit traceability and validation outcomes.
6. Publish sprint refinement summary and close issue after review acceptance.

## Acceptance Criteria

- PRD, architecture, AI, compliance, and security documents are mutually aligned.
- Security pattern demonstrates design-level coverage for relevant PRD FR and NFR controls.
- Compliance control set has explicit linkage to architecture and security controls.
- Availability and demand assumptions are documented with architecture implications.
- GitHub Issue is linked and serves as sprint execution and decision log anchor.

## Detailed Review Outcomes

### 1. Compliancy Review Outcome

- Swiss legal baseline anchored in FADP, DPO, EPDG, EPDV-EDI, with HRA and KVG
  as conditional regimes.
- Control model CH-C01 to CH-C10 established with implementation status and gaps.
- Purview contribution assessed with explicit GA and IaC boundaries.

### 2. Security Review Outcome

- Zero Trust security pattern established across identity, network, workload,
  application, data, and operations layers.
- Requirement and compliance traceability expanded to include governance and AI
  security-relevant controls.
- Residual work captured as implementation tasks (not design-definition gaps).

### 3. Architecture Review Outcome

- GA-only MVP architecture baseline confirmed.
- Swiss residency and PHI failover default-deny controls confirmed.
- React MVP channel and PHI-safe AI deployment constraints confirmed.

### 4. AI Review Outcome

- AI runtime pattern remains self-hosted and GA-focused.
- PHI inference constraints aligned to regional deployment rules.
- IaC coverage boundaries for Foundry and Fabric explicitly documented.

### 5. Availability Review Outcome

- Continuous-operation target validated against reliability NFR set.
- Degraded mode and restartability requirements retained as explicit design constraints.
- Recovery and failover remain policy-gated for PHI-sensitive workloads.

### 6. Demand Review Outcome

- Capacity envelope assumptions (event volume, concurrency, refresh cadence)
  documented and linked to architecture challenge matrix.
- Stress assumptions considered fit-for-planning and marked for load-test validation.
- No conflicting requirement discovered across PRD, architecture, and AI baselines.

## Residual Implementation Gaps

1. Formal DSR operating process with accountable ownership.
2. Cross-border transfer risk assessment and legal sign-off workflow.
3. Privacy incident decision matrix with notification timers.
4. EPR conformance and evidence pack when EPR integration is enabled.
5. AI override and safety acceptance thresholds with recurring reporting.

## Completion Summary

- Sprint 1 refinement completes design-level cross-domain validation.
- Required controls and guardrails are documented with full traceability.
- Remaining items are implementation and operations execution tracks.

## Notes

This refinement sprint hardens the Sprint 1 PRD foundation and de-risks the
next implementation phases by ensuring architecture, compliance, security, AI,
availability, and demand assumptions are aligned before build-out.
