# Sprint 07 Delegation Kickoff (Superpowers)

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-06-12 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 1.0.0 (new kickoff guide) |

## Objective

Kick off Sprint 07 by delegating slices through Superpowers workflow with
mandatory issue-to-PR traceability.

## Non-Negotiable Traceability Rule

1. Every slice starts with a GitHub issue linked to Sprint 07.
2. Every delivery change is implemented through a PR linked to that issue.
3. Issue must be updated with merged PR link before closure.

## Recommended Delegation Sequence

1. Stage 1 `brainstorming`
2. Stage 3 `writing-plans`
3. Stage 4 `subagent-driven-development` or `executing-plans`
4. `systematic-debugging` when failures, regressions, or unexpected behavior appears
5. Stage 5 `test-driven-development`
6. Stage 6 `requesting-code-review`
7. `verification-before-completion` before claiming completion
8. Stage 7 `finishing-a-development-branch`

Use detailed templates in [issue-body-templates.md](issue-body-templates.md).

## Kickoff Slices (Initial)

1. Data contract baseline for first product domain.
2. Ingestion pipeline slice for synthetic source onboarding.
3. Validation and policy-gate evidence slice.
4. Data serving/read model slice for capacity reporting.

## Issue Naming Convention

`[S07][<stage>] <slice-name>`

Examples:
1. `[S07][brainstorming] data-contract-baseline`
2. `[S07][writing-plans] ingestion-pipeline-slice`
3. `[S07][execution] policy-evidence-slice`

## PR Naming Convention

`[S07][<slice-name>] <change-summary>`

## Minimum Issue Fields

1. Requirements (`FR-*`, `NFR-*`)
2. Problem statement
3. Constraints (including `approved-to-apply` guardrail)
4. Acceptance criteria
5. Traceability fields:
   - Sprint issue: `#...`
   - Planned PR: `pending`

## Minimum PR Fields

1. Parent sprint issue: `#...`
2. Delivery issue: `#...`
3. Requirements implemented list
4. Validation evidence
5. Security/compliance impact
6. Skill applicability and evidence for core Superpowers skills

Use [../../../../.github/PULL_REQUEST_TEMPLATE.md](../../../../.github/PULL_REQUEST_TEMPLATE.md).

## First 30-Minute Startup Checklist

1. Create 4 Sprint 07 kickoff issues (one per initial slice).
2. Run `brainstorming` on first slice and approve brief.
3. Run `writing-plans` and confirm 2-15 minute task chunking.
4. Start execution on one slice only until review gate is green.
5. Open PR with mandatory linked issue fields.

## Evidence and Cadence

1. Update [checkpoint-matrix.md](checkpoint-matrix.md) per slice.
2. Fill [kpi-weekly-template.md](kpi-weekly-template.md) every week.
3. Keep issue as system of record; PR as implementation evidence.
