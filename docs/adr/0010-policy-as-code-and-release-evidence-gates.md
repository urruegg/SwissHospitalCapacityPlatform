# ADR-0010: Policy-as-Code and Release Evidence Gates

- Status: Accepted
- Date: 2026-06-09
- Deciders: Architecture Working Group
- Related Reviews:
  - `docs/reviews/2026-06-09-ama-caf-waf-review session.md`
  - `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md`
- Related Requirements: FR-GOV-003, FR-GOV-004, FR-GOV-005, NFR-COMP-007, NFR-SEC-001, NFR-SEC-002

## Context

The review baseline identified a consistent gap: controls are documented but not fully automated or evidenced in CI/CD. This weakens governance assurance and public-sector audit readiness.

## Decision

For Sprint 5 and subsequent release cycles:

1. Critical controls must be enforced through policy-as-code checks in CI/CD where technically feasible.
2. At minimum, automated checks must cover:
   - PHI residency and transfer guardrails,
   - prohibited deployment-type restrictions,
   - mandatory diagnostics and identity controls for affected resources.
3. Promotion gates require evidence artifacts for control effectiveness.
4. Failed critical policy checks block promotion to the next gate.
5. Manual exceptions require explicit approval record, owner, expiry, and mitigation plan.
6. Best-practice design target baseline values are mandatory unless explicitly
   approved as exceptions:
   - Target 1 (Promotion quality threshold): zero critical policy failures for
     SIT to PROD promotion.
   - Target 2 (Mandatory control coverage): 100 percent check coverage for
     listed mandatory controls in changed deployment scope.
   - Target 3 (Evidence artifact schema): each gate run must produce an artifact
     with at least:
     `policyPackVersion`, `gateName`, `evaluatedResources`, `passFailSummary`,
     `failureDetails`, `exceptionRefs`, `executionTimestampUtc`, `pipelineRunId`.
   - Target 4 (Exception validity): max exception validity is 90 days, monthly
     review required, expired exceptions block promotion.
   - Target 5 (Cadence checker): monthly policy/evidence conformance review with
     tracked remediation issues for drift.
7. Feasibility exception rule for automation gaps:
   - "technically feasible" gaps must be documented with rationale,
     compensating control, owner, and expiry date.
   - unresolved feasibility gaps are treated as open risk items and reviewed at
     each promotion gate.
8. Approval ownership model (best-practice baseline):
   - Platform and Architecture Owner approves policy-pack scope and changes.
   - Security and Compliance Owner approves control mapping and exception risk.
   - Operations and Release Owner approves promotion readiness and evidence completeness.

## Consequences

- Governance posture shifts from design intent to enforceable controls.
- Auditability and release confidence improve.
- Additional engineering effort is required for policy implementation and evidence pipelines.
- Monthly governance review overhead increases but reduces control drift risk.

## Implementation Notes

- Sprint 5 Phase 2 is the first mandatory implementation phase for this ADR.
- `docs/ALM_PLAN.md` and `docs/TEST.md` must reflect gate logic and evidence contract.
- Evidence outputs must be linked in PRs and release records.
- Expired exceptions are hard blockers and must be remediated or renewed through
  explicit approval before promotion proceeds.
