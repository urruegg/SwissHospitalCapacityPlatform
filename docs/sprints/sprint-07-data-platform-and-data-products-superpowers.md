# Sprint 07 - Data Platform and Data Products (Superpowers Execution)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-10 |
| **Author** | GitHub Copilot |
| **Status** | Planned |
| **Previous Version** | 0.0.0 (new sprint baseline) |

## Sprint Goal

Deliver the next domain sprint for data platform implementation and first data
products using the Superpowers Basic Workflow as the mandatory execution model.

The sprint prioritizes throughput and quality while preserving governance,
compliance, and evidence controls already defined in repository baselines.

## Source Baseline

1. [docs/PRD.md](../PRD.md)
2. [docs/ARCHITECTURE.md](../ARCHITECTURE.md)
3. [docs/DATA.md](../DATA.md)
4. [docs/COMPLIANCE.md](../COMPLIANCE.md)
5. [docs/SECURITY.md](../SECURITY.md)
6. [docs/ALM_PLAN.md](../ALM_PLAN.md)
7. [docs/TEST.md](../TEST.md)
8. [docs/runbooks/superpowers-cutover.md](../runbooks/superpowers-cutover.md)

## Sprint Scope

### In scope

1. Implement data-platform slices for ingestion-to-curation-to-serving paths.
2. Implement first data-product slices with explicit contract ownership.
3. Enforce Superpowers stage-gates for design, planning, execution, review, and closure.
4. Capture weekly KPI evidence for acceleration and quality.

### Out of scope

1. Removing approval gates or evidence contracts.
2. Reducing compliance controls for delivery speed.
3. Broad platform re-architecture beyond approved requirement scope.

## Superpowers Basic Workflow (Mandatory)

1. `brainstorming`
2. `using-git-worktrees`
3. `writing-plans`
4. `subagent-driven-development` or `executing-plans`
5. `test-driven-development`
6. `requesting-code-review`
7. `finishing-a-development-branch`

Each workflow stage has explicit artifacts and entry/exit criteria in
[sprint-07/stage-runbook.md](sprint-07/stage-runbook.md).

## Planned Artifacts

1. [docs/sprints/sprint-07/README.md](sprint-07/README.md)
2. [docs/sprints/sprint-07/stage-runbook.md](sprint-07/stage-runbook.md)
3. [docs/sprints/sprint-07/issue-body-templates.md](sprint-07/issue-body-templates.md)
4. [docs/sprints/sprint-07/checkpoint-matrix.md](sprint-07/checkpoint-matrix.md)
5. [docs/sprints/sprint-07/kpi-weekly-template.md](sprint-07/kpi-weekly-template.md)

## Definition of Done

1. Superpowers workflow is executed end-to-end for each in-scope delivery slice.
2. Every merged PR includes requirement traceability and evidence contract fields.
3. Data-product changes include contract/schema and validation evidence.
4. Weekly KPI summary is produced from sprint execution data.
5. No deploy/delete action bypasses `approved-to-apply`.
