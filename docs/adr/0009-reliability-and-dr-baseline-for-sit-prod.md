# ADR-0009: Reliability and Disaster Recovery Baseline for SIT and PROD

- Status: Accepted
- Date: 2026-06-09
- Deciders: Architecture Working Group
- Related Reviews:
  - `docs/reviews/2026-06-09-ama-caf-waf-review session.md`
  - `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md`
- Related Requirements: FR-GOV-001, FR-GOV-004, NFR-REL-001, NFR-REL-003, NFR-COMP-007

## Context

Sprint 5 review baseline confirmed that reliability intent exists, but production-grade DR and failover decisions are not yet fully operationalized. This is a blocker for governance-complete promotion to PROD.

## Decision

For Sprint 5 execution and MVP promotion controls:

1. Reliability and DR become explicit release-gated design artifacts, not implicit assumptions.
2. No PROD promotion for affected domains without:
   - defined RTO and RPO by data/workflow class,
   - documented dependency redundancy posture,
   - documented failover and restore procedure,
   - SIT rehearsal evidence (tabletop or technical drill).
3. PHI cross-region failover remains default-deny unless a compliance-approved exception workflow is completed.
4. Reliability controls must be represented in:
   - architecture baseline,
   - operations runbook,
   - test/release evidence requirements.
5. Best-practice design target baseline values are mandatory for Sprint 5 unless
    explicitly approved as exceptions:
    - Target 1 (Recovery class model):
       - Class R1 (patient-affecting critical workflows): RTO <= 60 minutes, RPO <= 15 minutes.
       - Class R2 (high-priority operational workflows): RTO <= 4 hours, RPO <= 1 hour.
       - Class R3 (supporting/reporting workflows): RTO <= 24 hours, RPO <= 24 hours.
    - Target 2 (DR rehearsal evidence package): each rehearsal must record
       `scenarioId`, `systemsInScope`, `targetRtoRpo`, `actualRtoRpo`,
       `passFailResult`, `gaps`, `owner`, and `retestDate`.
    - Target 3 (Stateful dependency restore proof): every in-scope stateful
       dependency must have at least one successful SIT restore proof artifact
       in the previous 90 days before PROD promotion.
    - Target 4 (PHI failover exception gate): exception requires legal/compliance
       approval, security approval, operations approval, compensating controls,
       and explicit expiry date not exceeding 90 days.
    - Target 5 (Revalidation cadence):
       - monthly evidence freshness review,
       - quarterly DR rehearsal minimum for R1 and R2 workflows,
       - semiannual DR rehearsal minimum for R3 workflows.

## Consequences

- Reliability posture is measurable and auditable per domain.
- Promotion risk is reduced through pre-production rehearsal evidence.
- Sprint throughput may slow due to mandatory rehearsal and evidence gates.
- Teams must maintain recurring reliability governance cadence for evidence and drills.

## Implementation Notes

- Sprint 5 must produce `docs/operations/reliability-dr-profile.md`.
- `docs/OPERATIONS.md` and `docs/TEST.md` must include DR evidence checkpoints.
- Any domain lacking reliability evidence is restricted to SIT until closure or approved risk acceptance.
- Any exception to design targets must include:
   - rationale,
   - risk acceptance owner,
   - mitigation plan,
   - time-bound expiry,
   - follow-up validation date.
