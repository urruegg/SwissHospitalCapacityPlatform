# Sprint 07 Checkpoint Matrix

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.1 |
| **Date** | 2026-06-10 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 1.0.0 (new checkpoint matrix) |

## Usage

Mark each checkpoint `pass`, `fail`, or `n/a` with evidence links.

## Stage and Gate Matrix

| Stage | Checkpoint | Pass Criteria | Evidence |
| ----- | ----- | ----- | ----- |
| brainstorming | Design brief approved | Alternatives and acceptance criteria documented | Link to issue comment or artifact |
| using-git-worktrees | Worktree isolation complete | One worktree per major slice and clean baseline check | Terminal output or note |
| writing-plans | Sprint issue present | Sprint-linked issue exists before implementation starts | Issue link |
| writing-plans | Plan quality gate | Tasks include files, verification, requirement mapping | Plan artifact link |
| execution | Spec compliance review | No unresolved critical spec deviation | Review note link |
| execution | Quality review | No unresolved critical quality defect | Review note link |
| test-driven-development | Validation proof | RED-GREEN evidence or test-first checklist attached | Test output link |
| requesting-code-review | Severity gate | Critical findings resolved or accepted by owner | Review summary link |
| finishing-a-development-branch | Closeout gate | PR contract complete and branch decision recorded | PR link |
| finishing-a-development-branch | Issue to PR closure | PR references sprint issue and issue reflects merged PR | Issue + PR links |

## Cross-Cutting Governance Checks

| Check | Pass Criteria | Evidence |
| ----- | ----- | ----- |
| Traceability | FR/NFR IDs explicit in issue and PR | Issue + PR links |
| Sprint traceability chain | Issue exists first and PR follows with backlink | Issue + PR links |
| Compliance impact | Compliance impact statement included | PR section |
| Security impact | Security impact statement included | PR section |
| Deploy/delete guardrail | `approved-to-apply` used where applicable | PR/issue comment |
| Required checks | Lint/test/policy checks pass for scope | Command output links |
