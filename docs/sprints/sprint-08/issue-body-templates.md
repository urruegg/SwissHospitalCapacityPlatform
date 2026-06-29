# Sprint 08 Issue Body Templates

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-29 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 0.0.0 (new template pack) |

## Template A - Stage 1 brainstorming

```text
Title: [S08][brainstorming] <slice-name>

@copilot run Superpowers brainstorming for this Sprint 08 slice.

Requirements:
- FR-...
- NFR-...

Traceability:
- Sprint issue: #66
- Planned PR: pending

Problem:
- ...

Constraints:
- Swiss region and residency constraints
- No deploy/delete without approved-to-apply

Out of scope:
- ...

Expected output:
1) Design brief
2) Alternatives and recommendation
3) Acceptance criteria
```

## Template B - Stage 3 writing-plans

```text
Title: [S08][writing-plans] <slice-name>

@copilot produce a Superpowers writing-plans task list.

Approved design source:
- docs/sprints/sprint-08/... or linked PR comment

Requirements:
- FR-...
- NFR-...

Plan constraints:
- 2-15 minute task chunks
- each task must include target files and validation command
- each task must include expected evidence artifact
- issue must remain the parent traceability record for this slice

Expected output:
1) Ordered task plan
2) Task-to-requirement mapping
3) Verification checklist
```

## Template C - Stage 4 execution

```text
Title: [S08][execution] <slice-name>

@copilot execute approved plan using Superpowers execution workflow.

Plan reference:
- <link>

Execution mode:
- subagent-driven-development OR executing-plans

Stop conditions:
- Critical review issue
- Missing requirement traceability
- Missing policy/safety evidence

Expected output:
1) Completed task log
2) Evidence links
3) Residual risks
```

## Template D - Stage 6 review and Stage 7 finish

```text
Title: [S08][review-closeout] <slice-name>

@copilot run requesting-code-review and finishing-a-development-branch.

PR reference:
- <link>

Traceability closure:
- Parent sprint issue: #66
- PR must link issue and update issue with merged PR reference

Review rules:
- findings ordered by severity
- critical findings block closure

Closeout options:
- merge
- keep branch for follow-up
- discard branch

Expected output:
1) Findings report
2) Closure recommendation
3) Worktree cleanup note
```
