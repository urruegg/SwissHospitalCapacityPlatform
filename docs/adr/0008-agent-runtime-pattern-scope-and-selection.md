# ADR-0008: Agent Runtime Pattern Scope and Selection

- Status: Accepted
- Date: 2026-06-09
- Deciders: Architecture Working Group
- Related Reviews:
  - `docs/reviews/2026-06-09-ama-caf-waf-review session.md`
  - `docs/reviews/2026-06-08-ama-review-session-csa-sd-challanger.md`
- Related Requirements: FR-GOV-001, FR-GOV-006, NFR-AI-001, NFR-AI-004, NFR-COMP-004

## Context

Sprint 5 review baseline identified architecture drift risk between:

1. current repository MVP baseline favoring application-hosted agents (`docs/AI.md`), and
2. external reference architectures based on Foundry Agent Service.

Without a formal runtime scope rule, implementation teams can produce inconsistent architecture and governance outcomes across domains.

## Decision

For Sprint 5 and MVP execution:

1. Application-hosted agent runtime remains the default pattern for regulated MVP paths.
2. Foundry Agent Service usage is permitted only when explicitly scoped and documented for the workload, with clear data-class boundaries and control mapping.
    - Mandatory go/no-go rule: the required Foundry service/capability must be GA
       in the selected target region.
    - If required service/capability is not GA in the selected region, Foundry path
       is no-go for that workload path.
3. Hybrid runtime is permitted only with an explicit boundary contract:
   - which flows run application-hosted,
   - which flows run Foundry-hosted,
   - which data classes are allowed per path.
4. Every runtime choice must be reflected consistently in:
   - `docs/ARCHITECTURE.md`
   - `docs/AI.md`
   - `docs/SD.md`
   - release traceability and test evidence.
5. Any Foundry or hybrid runtime path must pass explicit approval ownership gates
    before SIT promotion and before PROD promotion.
6. Runtime choices are subject to monthly revalidation.

## Consequences

- Architecture consistency improves across design and implementation.
- Runtime decisions become auditable and reviewable before phase implementation.
- Cross-team ambiguity is reduced for SIT/PROD promotion.
- Additional documentation and test burden is introduced for hybrid runtime scenarios.
- Monthly runtime review introduces recurring governance overhead but reduces
   long-lived architecture drift risk.

## Implementation Notes

- Phase 1 of Sprint 5 must include a runtime decision matrix.
- Any future change from this default requires a superseding ADR.
- Runtime-specific controls must map to CH controls and release evidence in `docs/TEST.md`.
- Best-practice hybrid boundary contract is mandatory for each hybrid flow and
   must include:
   1. flowId and business capability
   2. runtimeMode per segment (application-hosted or Foundry-hosted)
   3. dataClass and PHI handling rule
   4. region and GA capability evidence reference
   5. controlOwner and approver roles
   6. required evidence artifacts and test cases
   7. failure mode, fallback path, and rollback trigger
- Enforcement gates are mandatory:
   1. CI gate: runtime-matrix update required when runtime-related files change.
   2. SIT gate: boundary contract, GA-region evidence, and test evidence required.
   3. PROD gate: all SIT evidence plus explicit human approvals and residual-risk statement.
   4. Runtime gate: side-effecting paths must enforce selected runtime boundaries and deny
       execution on contract violations.
- Approval ownership model (best-practice baseline):
   1. Architecture Owner approves runtime pattern and boundary contract.
   2. Security and Compliance Owner approves data-class, residency, and control mapping.
   3. Operations Owner approves production readiness, fallback, and supportability.
- Monthly revalidation cadence checker:
   1. Run monthly review of runtime matrix and hybrid contracts.
   2. Validate GA availability status in selected regions for required capabilities.
   3. Validate control evidence freshness and open-risk status.
   4. Record outcomes in governance evidence artifacts and create follow-up issues for drift.
