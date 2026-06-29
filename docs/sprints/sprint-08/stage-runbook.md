# Sprint 08 Stage Runbook (Superpowers)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-29 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 0.0.0 (new Sprint 08 runbook) |

## Purpose

Operationalize the Superpowers Basic Workflow for Sprint 08 with explicit entry
criteria, outputs, and gates per stage.

## Stage 1 - brainstorming

### Stage 1 Entry criteria

1. Sprint-scoped GitHub issue exists for the delivery slice.
2. Issue has problem statement and target lane.
3. FR/NFR IDs are listed.

### Stage 1 Required outputs

1. Scoped design brief with assumptions and alternatives.
2. Explicit out-of-scope list.
3. Acceptance criteria draft.
4. Issue includes planned PR traceability note (`planned-pr: pending`).

### Stage 1 Gate

Design brief approved by human owner before branch execution begins.

## Stage 2 - using-git-worktrees

### Stage 2 Entry criteria

1. Design brief approved.

### Stage 2 Required outputs

1. One isolated worktree per major Sprint 08 slice:
   - source-sql
   - fabric-foundation
   - silver-gold
   - semantic-model
   - simulator
2. Clean baseline verification recorded.

### Stage 2 Gate

No implementation starts on shared branch without worktree isolation.

## Stage 3 - writing-plans

### Stage 3 Entry criteria

1. Worktree ready and scope fixed.

### Stage 3 Required outputs

1. Task list with 2-15 minute chunks.
2. Every task contains file targets, validation command, expected evidence.
3. Every task mapped to requirement IDs.

### Stage 3 Gate

Plan approved before implementation tasks run.

## Stage 4 - subagent-driven-development or executing-plans

### Stage 4 Entry criteria

1. Plan approved.

### Stage 4 Required outputs

1. Task execution logs and completion evidence.
2. Two-stage internal review per task:
   - spec compliance
   - code/document quality

### Stage 4 Gate

Critical issues block progression to next task cluster.

## Stage 4.1 - systematic-debugging (conditional mandatory)

### Stage 4.1 Entry criteria

1. Any failure, regression, flaky test, or unexpected behavior appears during execution.

### Stage 4.1 Required outputs

1. Reproducible failure statement and scope.
2. Hypothesis-driven debugging record.
3. Verified root-cause evidence.

### Stage 4.1 Gate

No workaround-only closure without identified root cause or explicit risk acceptance by owner.

## Stage 5 - test-driven-development

### Stage 5 Entry criteria

1. Implementation task active.

### Stage 5 Required outputs

1. RED-GREEN-REFACTOR sequence for executable artifacts.
2. For non-code artifacts, test-first checklist evidence.

### Stage 5 Gate

No task marked complete without passing validation proof.

## Stage 6 - requesting-code-review

### Stage 6 Entry criteria

1. Task cluster complete with evidence attached.

### Stage 6 Required outputs

1. Severity-ranked findings.
2. Resolution decisions and residual risks.

### Stage 6 Gate

No critical findings open before branch closeout.

## Stage 7 - finishing-a-development-branch

### Stage 7 Entry criteria

1. All planned tasks complete.
2. Required checks pass.
3. `verification-before-completion` evidence is attached.

### Stage 7 Required outputs

1. PR ready package with requirement/evidence contract.
2. Decision: merge, keep for follow-up, or discard.
3. Worktree cleanup record.
4. PR links back to sprint issue and closes or updates that issue.

### Stage 7 Gate

PR merge only when governance and approval rules are satisfied.

## Mandatory Cross-Stage Controls

1. `approved-to-apply` for deploy/delete actions.
2. Requirement traceability in each PR.
3. Security/compliance impact statement in each PR.
4. Every delivery slice starts with a sprint-linked issue.
5. Every mergeable change is delivered through a PR linked to that issue.
6. Core skills are explicitly assessed: `writing-plans`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`.
7. Checkpoint matrix completion: [checkpoint-matrix.md](checkpoint-matrix.md).
