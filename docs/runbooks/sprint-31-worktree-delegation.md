# Sprint 31 — Worktree Delegation Runbook (Data Quality Agent)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-27 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |

> **Purpose:** package **Sprint 31** (Data Quality Agent — DQA) so it can be built by
> a **single fresh Copilot CLI agent in its own isolated git worktree**. Grounded in
> the [SGA+DQA design](../superpowers/specs/2026-07-27-sprint-31-32-signal-and-data-quality-agents-design.md)
> and the [Sprint 31 plan](../superpowers/plans/2026-07-27-sprint-31-data-quality-agent.md).
> Builds on the `superpowers:using-git-worktrees` and
> `superpowers:subagent-driven-development` skills. Sibling runbook:
> [Sprint 32 (SGA)](sprint-32-worktree-delegation.md).

---

## 1. Model

- **One worktree = one session = the whole sprint.** Sprint 31 **elevates the existing
  `data-quality-agent`** from ingestion gates to **proactive** assessment: a
  deterministic per-domain **Trust Score**, **gap detection with impact**, an
  owner-routed remediation loop, grounding-readiness certification, and the frozen
  **`DC-DQ-GAP-v1` "new-source-needed" seam** that Sprint 32 (SGA) consumes. It is
  concentrated in `data-platform/quality/` (Python) + the `agents/data-quality-agent/`
  pack + `data/synthetic/schema/` contracts + governance docs, so it runs in **one**
  dedicated worktree.
- **Milestone chain (design §11):** `D0 → D1 → D2 → D3 → D4 → D5`, realised as the
  plan's tasks **T1–T6** (issue **#453**). All executable this sprint (no follow-on
  plan split needed — the slice is self-contained).
- **Trunk-based per [ADR-0038](../adr/0038-trunk-based-parallel-sprint-workflow.md):**
  short-lived branch off `main`, **one issue → one branch → one squash PR**, CI is the
  merge gate, **a human merges every PR** (no self-merge). Deploys/live changes gated
  by `approved-to-apply` (AGENTS.md §4).
- **Read-only, advisory-only, no infra apply.** DQA never edits source data; it
  proposes, owners remediate. Synthetic / no-PHI only (ADR-0016); demo region
  (ADR-0013). The trust-score model + thresholds are ratified in a **new ADR**.

## 2. The worktree (already created)

The Sprint 31 worktree already exists off `main`:

```text
C:/Users/urruegg/source/urruegg/wt/sprint-31-data-quality-agent  [sprint-31/data-quality-agent]
```

If it ever needs recreating (off latest `main`):

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform fetch origin
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform worktree add `
  ..\wt\sprint-31-data-quality-agent -b sprint-31/data-quality-agent origin/main
```

To remove the worktree after the sprint's PR merges:

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform worktree remove ..\wt\sprint-31-data-quality-agent
```

## 3. Seed tool auto-approvals (per-worktree, not inherited)

A fresh worktree starts with an empty tool-approval set. Either launch with
`copilot --allow-all-tools`, or seed approvals per the
[parallel-session runbook §7](../superpowers/handoffs/parallel-session-runbook.md#7-auto-approval-permissions-are-per-worktree-not-inherited)
(run with all sessions closed; keep the `.bak-seed-*` backup).

## 4. Delegate to the Copilot CLI session

Launch a fresh Copilot CLI agent **inside the worktree** and paste the Section 5
prompt. First sync `main` so the design + plan (PR #456) are present:

```powershell
Set-Location ..\wt\sprint-31-data-quality-agent
git fetch origin; git merge origin/main --no-edit    # pull the merged design + plan
copilot --allow-all-tools
```

Optionally drop a git-excluded `KICKSTART.md` in the worktree holding the Section 5
prompt so the launcher seeds the tab.

## 5. Delegation prompt template

Paste into the Copilot CLI agent launched inside the Sprint 31 worktree
(work package `<issue>` = **453**; tracker = **451**):

```text
You are implementing Sprint 31 (Data Quality Agent — DQA) in this dedicated
worktree. Work ONLY in this worktree; branch off main.

Read first (do not skip):
- docs/superpowers/plans/2026-07-27-sprint-31-data-quality-agent.md (tasks T1-T6)
- docs/superpowers/specs/2026-07-27-sprint-31-32-signal-and-data-quality-agents-design.md
  (esp. §6 DQA, §8 the DC-DQ-GAP-v1 seam, §10 compliance, §11 Sprint-31 milestones)
- GitHub issue #453 (the work package) and tracker #451.
- .github/copilot-instructions.md + AGENTS.md, then docs/adr/* (ADR-0007 HITL,
  ADR-0016 no-PHI, ADR-0038 trunk-based, ADR-0006/0042 GA-gate) + docs/DATA.md +
  docs/AI.md + docs/COMPLIANCE.md.
- The pattern to mirror: data-platform/decision/impact/compute_expected_impact.py
  (deterministic, no randomness, no LLM estimate) + its tests.
- The agent you are expanding: agents/data-quality-agent/{AGENT.md,manifest.yaml,
  golden-tasks.md} (read before editing) and the dc-*-v1.schema.json convention in
  data/synthetic/schema/.

Rules:
- Superpowers skills are mandatory: writing-plans -> confirm plan.md with me ->
  test-driven-development -> subagent-driven-development (one task at a time, fresh
  subagent + quality review per task) -> verification-before-completion.
- Tasks T1-T6: DC-DQ-TRUSTSCORE-v1 + DC-DQ-GAP-v1 JSON schemas; deterministic
  trust_score() module + tests; assess_gaps() module + tests (data-platform/quality/,
  new package + conftest for imports); expand the data-quality-agent pack (proactive
  assessment + trust score + gap->owner + grounding-readiness, read-only/advisory);
  golden-task fixtures (trust-score, gap->owner, below-threshold degraded gate, PHI
  refusal); trust-score ADR + FR-DQA-* PRD rows + docs/DATA.md contract registration.
- TDD every code task: failing test first, run it, implement, re-run green.
- DQA is READ-ONLY (never edits source data) and advisory (owner remediates). The
  trust score is deterministic + versioned + explainable (NEVER an LLM estimate).
  Freeze the DC-DQ-GAP-v1 seam shape exactly as the design §8 specifies — Sprint 32
  SGA builds against it. Synthetic / no-PHI only. No infra apply.
- Gates per slice: python -m pytest data-platform/quality/tests (green). Doc edits:
  check_mojibake.py + markdownlint-cli2, bump SemVer headers, commit with the hook
  bypass if needed (git -c core.hooksPath=/dev/null). Runtime python (not python3).
- ONE small squash PR (branch sprint-31/data-quality-agent) linked to #453. Never
  self-merge; wait for green required checks; a human merges.
- Assign the NEW ADR number at execution (next free; verify collisions via
  git ls-tree). Replace 00NN and confirm every file path first.
- Report DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED at the end.

First: read the plan + design + issue #453, draft/refresh plan.md, and ask me to
confirm before coding.
```

## 6. Integration + finish

- **Acceptance gate (sprint):** design §11 Sprint-31 DoD is green — a deterministic,
  unit-tested Trust Score is published for ≥1 gold domain with dimension breakdown;
  one gap is opened + routed to a named owner + closed on a sample (re-assessment
  shows the delta); a below-threshold domain is withheld/degraded (not silently
  served); the trust-score ADR is recorded; `FR-DQA-*` PRD rows land; **the
  `DC-DQ-GAP-v1` seam is frozen**; no PHI in any artefact.
- Use `superpowers:finishing-a-development-branch` for the PR.
- After the PR merges, remove the worktree (Section 2). **Notify the Sprint 32
  session** that the `DC-DQ-GAP-v1` seam is now on `main` (SGA's hard prerequisite).

## 7. Coordinator note (design + plan landing)

The Sprint 31 design + plan are in **open PR #456** (`sprint-27/curavias-ux-polish`).
They must **land on `main` before the work package starts** so the worktree — created
off `main` — can read them (§4 `git merge origin/main`). A human merges #456; until
then, issue **#453** carries the full T1–T6 task list + acceptance criteria, so the
session can start from the design + #453 without waiting.
