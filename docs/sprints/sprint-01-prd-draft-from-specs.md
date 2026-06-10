# Sprint 1 - PRD Draft from Specs

| Field | Value |
| ----- | ----- |
| **Version** | 1.2.0 |
| **Date** | 2026-06-01 |
| **Author** | Urs Rüegg |
| **Status** | Completed |
| **Previous Version** | 1.1.0 (added GitHub Issue + @copilot trigger model) |

## Sprint Goal

Use `spec-parser-agent` to analyse the source specification documents in `docs/specs/` and produce the first solution-relevant PRD draft for the Swiss AI-Powered Patient Flow and Hospital Capacity Platform.

## Trigger Model

Sprint 1 is executed as a GitHub Issue-driven run. The sprint issue is the tracking anchor, and `@copilot` is the trigger for the agent run when the work is assigned.

## Traceability

- GitHub Issue: [#3](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/3)
- GitHub Project: Swiss Hospital Capacity Platform Delivery
- Source documents:
  - `docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform.md`
  - `docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform analysis.md`
- Target artefact: `docs/PRD.md`

## Scope

### In scope

- Read the two source documents in `docs/specs/`.
- Extract functional requirements, non-functional requirements, assumptions, exclusions, and open questions.
- Produce a first PRD draft that defines the MVP scope for the solution.
- Link the PRD draft back to the source documents and the sprint issue.
- Track the sprint work in GitHub Projects for traceability.

### Out of scope

- Landing zone implementation.
- Application implementation.
- Compliance sign-off.
- Drift remediation.
- Deploy or delete actions.

## Planned Work Items

1. Confirm the canonical source bundle under `docs/specs/`.
2. Run the spec analysis through `spec-parser-agent` from the Sprint 1 issue via `@copilot`.
3. Update `docs/PRD.md` with the first solution-draft requirement set.
4. Review the PRD for MVP scope coverage and open questions.
5. Keep the sprint issue and GitHub Project item in sync with the draft.

## Acceptance Criteria

- `docs/PRD.md` contains a first draft of the solution-specific FRs and NFRs.
- The PRD clearly separates solution scope, assumptions, exclusions, and MVP boundaries.
- The traceability section points to the source specs used to derive the requirements.
- GitHub Issue [#3](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/3) is linked to the GitHub Project delivery board.
- The sprint issue and `@copilot` trigger path are documented as the execution model for the sprint.

## Completion Summary

- Sprint 01 completed with a full PRD rewrite in `docs/PRD.md`.
- Functional and non-functional requirements were re-established from `docs/specs/` as the canonical source set.
- The Sprint 01 issue is closed after commit publication and documented completion.

## Notes

This sprint is the requirements-discovery entry point for the rest of the delivery lifecycle.
The output from this sprint is expected to inform architecture, data design, landing zone work, and downstream validation.
