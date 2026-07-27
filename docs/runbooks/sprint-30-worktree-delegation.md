# Sprint 30 — Worktree Delegation Runbook (single dedicated session)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-27 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |

> **Purpose:** package **Sprint 30** (Closed-Loop Learning Foundation) so it can
> be built by a **single fresh Copilot CLI agent in its own isolated git
> worktree**. Grounded in the
> [Sprint 30 design](../superpowers/specs/2026-07-27-sprint-30-closed-loop-learning-foundation-design.md)
> and [plan 1](../superpowers/plans/2026-07-27-sprint-30-closed-loop-learning-foundation.md).
> Builds on the `superpowers:using-git-worktrees` and
> `superpowers:subagent-driven-development` skills. Complements the durable
> [parallel-session runbook](../superpowers/handoffs/parallel-session-runbook.md).

---

## 1. Model

- **One worktree = one session = the whole sprint.** Sprint 30 stands up a **full
  single-agent closed loop** for the lead agent `ooa-agent` (capture → evaluate →
  curate → improve, advisory + human-gated) plus a Foundry Build+Operate capability
  assessment. It is concentrated in `apps/hcc-agent-host` (Python) with an app-side
  touch in `apps/hcc-app-fluent`, so it runs in **one** dedicated worktree. The
  in-session `subagent-driven-development` pattern keeps each task isolated and
  test-first.
- **Milestone chain (design §10):** `M0 → M1 → M2 → M3 → M4 → M5 → M6 → M7 → M8 →
  M9`, sliced into **work-package plans**. **Plan 1 (issue #445)** is the executable
  foundation — `M0 + M1-capture + M2` — and runs **first** because the rest of the
  loop and hybrid testing depend on it. Later milestones land as **follow-on plans**
  (M1-observe, M3–M4, M5, M7–M9), each its own issue → branch → squash PR.
- **Trunk-based per [ADR-0038](../adr/0038-trunk-based-parallel-sprint-workflow.md):**
  short-lived branches off `main`, **one issue → one branch → one squash PR**, CI is
  the merge gate, **a human merges every PR** (no self-merge). Deploys/live changes
  gated by `approved-to-apply` (AGENTS.md §4).
- **No infra apply / no autonomous promotion this sprint.** The loop is
  advisory-only; every prompt / knowledge / guardrail / model change stays
  human-gated. Synthetic / no-PHI only (ADR-0016); demo region (ADR-0013).

## 2. The worktree (already created)

The Sprint 30 worktree already exists off `main`:

```text
C:/Users/urruegg/source/urruegg/wt/sprint-30-closed-loop-capture  [sprint-30/closed-loop-capture]
```

If it ever needs recreating (off latest `main`):

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform fetch origin
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform worktree add `
  ..\wt\sprint-30-closed-loop-capture -b sprint-30/closed-loop-capture origin/main
```

The session rebranches per work package off the latest `main` as earlier PRs merge
(`git fetch origin; git switch -c sprint-30/m1-observe origin/main`).

To remove the worktree after the sprint's PRs merge:

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform worktree remove ..\wt\sprint-30-closed-loop-capture
```

## 3. Seed tool auto-approvals (per-worktree, not inherited)

A fresh worktree starts with an empty tool-approval set. Either launch with
`copilot --allow-all-tools`, or seed approvals per the
[parallel-session runbook §7](../superpowers/handoffs/parallel-session-runbook.md#7-auto-approval-permissions-are-per-worktree-not-inherited)
(run with all sessions closed; keep the `.bak-seed-*` backup).

## 4. Delegate to the Copilot CLI session

Launch a fresh Copilot CLI agent **inside the worktree** and paste the Section 5
prompt. The session reads the design + plan + issue #445, drafts/refreshes
`plan.md`, stops at a plan-confirmation gate, then implements task-by-task with TDD.

```powershell
Set-Location ..\wt\sprint-30-closed-loop-capture
copilot --allow-all-tools
```

Optionally create a git-excluded `KICKSTART.md` in the worktree (auto-excluded via
`.git/info/exclude`) holding the Section 5 prompt, so the launcher seeds the tab.

## 5. Delegation prompt template

Paste into the Copilot CLI agent launched inside the Sprint 30 worktree
(first work package `<issue>` = **445**; tracker = **443**):

```text
You are implementing Sprint 30 (Closed-Loop Learning Foundation) in this
dedicated worktree. Work ONLY in this worktree; branch off main per work package.

Read first (do not skip):
- docs/superpowers/plans/2026-07-27-sprint-30-closed-loop-learning-foundation.md
  (Plan 1 — capture foundation, tasks T1-T7)
- docs/superpowers/specs/2026-07-27-sprint-30-closed-loop-learning-foundation-design.md
  (esp. §6 DC-AGENT-INTERACTION-v1, §7 evaluators, §10 scope, §12 compliance)
- GitHub issue #445 (the executable work package: M0 + M1-capture + M2) and the
  tracker #443.
- .github/copilot-instructions.md + AGENTS.md, then the relevant docs/adr/*
  (ADR-0007 HITL, ADR-0013 demo region, ADR-0016 no-PHI, ADR-0032 Foundry,
  ADR-0038 trunk-based) and docs/DATA.md + docs/AI.md + docs/COMPLIANCE.md.
- The existing agent-host files the plan lists: apps/hcc-agent-host/src/
  {orchestrator,persistence,hitl,redaction} + its tests (read each before editing).

Rules:
- Superpowers skills are mandatory: writing-plans -> confirm plan.md with me ->
  test-driven-development -> subagent-driven-development (one task at a time,
  fresh subagent + quality review per task) -> verification-before-completion.
- Start with Plan 1 / issue #445 (T1-T7): DC-AGENT-INTERACTION-v1 schema +
  validator, interaction_record builder (prompt_hash + redaction reuse),
  agent_interactions Cosmos container + append_user_event, capture wiring in
  Orchestrator.dispatch() (+ interactionId on GroundedReply), interactionId in
  POST /chat, user-events append endpoint, docs/DATA.md registration.
- TDD every task: write the failing test first, run it, implement, re-run green.
- Stay strictly in apps/hcc-agent-host (Python) for Plan 1; the app-side userEvent
  emission (hcc-app-fluent) is M2-app, a SEPARATE follow-on plan. NO infra apply;
  the loop is advisory-only and human-gated. Synthetic / no-PHI only; never store
  a raw prompt (hash + redact). Region-agnostic config.
- Gates per slice: python -m pytest in apps/hcc-agent-host (new capture tests pass,
  existing dispatch/redaction/loader tests unregressed). Doc edits: check_mojibake.py
  + markdownlint-cli2, bump SemVer headers, commit with the hook bypass
  (git -c core.hooksPath=/dev/null). Runtime python (not python3).
- One SMALL squash PR per work package (branch sprint-30/<slice>), linked to its
  issue (Plan 1 -> #445). Never self-merge; wait for green required checks; a human
  merges. Follow-on milestones (M1-observe, M3-M4, M5, M7-M9) are separate plans +
  issues you propose after Plan 1 lands.
- Assign any NEW ADR number at execution (next free; verify collisions via
  git ls-tree). Replace 00NN and confirm every file path first.
- Report DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED at each work-package end.

First: read the plan + design + issue #445, draft/refresh plan.md for Plan 1, and
ask me to confirm before coding.
```

## 6. Integration + finish

- Merge **Plan 1 (#445)** first — it is the capture foundation everything else
  consumes. Then land the follow-on plans in dependency order: M1-observe → M3–M4
  (evaluate) → M5 (curate) → M6 (ADR + docs) → M7–M9 (Improve), each as its own
  human-reviewed squash PR. Rebranch off the latest `main` per work package.
- **Acceptance gate (sprint):** the design §10 milestone table + §14 requirements
  (`FR-LEARN-001..005`, `NFR-LEARN-001..004`) are green for `ooa-agent`: every turn
  persists a PHI-free `DC-AGENT-INTERACTION-v1` record; continuous + offline eval
  score interactions; curator emits versioned datasets + an advisory backlog;
  Improve (prompt/knowledge/fine-tune) runs human-gated with full lineage
  (interaction → dataset → eval → change); the capture ADR is recorded. Breadth to
  the other five agents is **Sprint 31** (design §11).
- Use `superpowers:finishing-a-development-branch` per PR.
- After all slices merge, remove the worktree (Section 2).

## 7. Coordinator note (plan-doc landing)

The Sprint 30 **Plan 1** doc
(`docs/superpowers/plans/2026-07-27-sprint-30-closed-loop-learning-foundation.md`)
was drafted on branch `sprint-27/curavias-ux-polish` and is in **open PR #441**
(single-file). It must **land on `main` before (or alongside) the first work
package** so the worktree — created off `main` — can read it. Merge #441 (a human
merges), then the session runs `git fetch origin` in the worktree to pick it up.
Until then, issue **#445** carries the full T1–T7 task list + acceptance criteria,
so the session can start from the design + #445 without waiting.
