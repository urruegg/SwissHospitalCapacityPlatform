# ADR-0011: Cantonal Legal Applicability Gate for Production Promotion

- Status: Accepted
- Date: 2026-06-09
- Deciders: Architecture Working Group
- Related Reviews:
  - `docs/reviews/2026-06-09-ama-caf-waf-review session.md`
  - `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md`
- Related Requirements: NFR-COMP-001, NFR-COMP-002, NFR-COMP-005, NFR-COMP-010

## Context

Review findings explicitly state that federal baseline controls are insufficient for cantonal public-sector production claims without canton-specific applicability mapping.

## Decision

For Sprint 5 and public-sector promotion governance:

1. A canton-specific legal applicability annex is mandatory before PROD promotion for cantonal workloads.
2. The annex must map:
   - legal obligation scope,
   - CH control mapping,
   - control owner,
   - required evidence artifacts,
   - unresolved validation points.
3. If canton-specific applicability is not completed, deployment scope is limited to SIT/non-production validation.
4. Compliance status statements must distinguish:
   - design aligned,
   - implemented,
   - requires validation.
5. Best-practice design target baseline values are mandatory unless explicitly
    approved as exceptions:
    - Target 1 (Annex schema minimum): each canton entry must include
       `cantonId`, `legalSource`, `obligationSummary`, `controlMappings`,
       `controlOwner`, `evidenceArtifacts`, `status`, and `openValidationPoints`.
    - Target 2 (Promotion threshold): zero unresolved high-severity legal
       applicability gaps for PROD promotion in the target canton scope.
    - Target 3 (Approval ownership): cantonal applicability sign-off requires
       Legal and Compliance Owner, Security and Compliance Owner, and
       Operations and Release Owner approvals.
    - Target 4 (Exception validity): max exception validity is 90 days with
       documented compensating controls and explicit risk acceptance owner.
    - Target 5 (Cadence checker): monthly applicability revalidation for active
       cantonal deployments and immediate reassessment on legal/regulatory changes.
6. Expired legal applicability exceptions are hard blockers for PROD promotion
    until renewed or remediated.

## Consequences

- Regulatory alignment improves and legal ambiguity is reduced.
- Production-readiness decisions become explicit and defensible.
- Additional coordination with legal/compliance stakeholders is required.
- Monthly legal applicability review overhead increases but reduces
   regulatory-drift risk.

## Implementation Notes

- Sprint 5 Phase 1 must introduce `docs/compliance/cantonal-annex.md`.
- Sprint 5 Phase 2 must integrate annex checks into release evidence requirements.
- Any exception to this gate requires documented risk acceptance by accountable governance owners.
- Annex checks in release evidence must confirm:
   - schema completeness,
   - owner assignments,
   - evidence-link validity,
   - exception status and expiry.
