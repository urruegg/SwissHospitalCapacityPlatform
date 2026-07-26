# Sprint 29 — Worktree Delegation Runbook (single dedicated session)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-26 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |

> **Purpose:** package **Sprint 29** (Foundry IQ context architecture) so it can
> be built by a **single fresh Copilot CLI agent in its own isolated git
> worktree**. Grounded in the
> [Sprint 29 design](../superpowers/specs/2026-07-26-sprint-29-foundry-iq-context-architecture-design.md)
> and [plan](../superpowers/plans/2026-07-26-sprint-29-foundry-iq-context-architecture.md).
> Builds on the `superpowers:using-git-worktrees` and
> `superpowers:subagent-driven-development` skills. Complements the durable
> [parallel-session runbook](../superpowers/handoffs/parallel-session-runbook.md).

---

## 1. Model

- **One worktree = one session = the whole sprint.** Unlike Sprint 28's 8-way
  split, Sprint 29 is concentrated in a single codebase (`apps/hcc-app-fluent`)
  with a mostly-sequential milestone chain, so it runs in **one** dedicated
  worktree. The in-session `subagent-driven-development` pattern keeps each
  milestone task isolated and test-first.
- **Milestone chain:** `M0 → (M1 ‖ M2) → M3 → M4 → M5 → M6`. One **small PR per
  milestone slice** (`sprint-29/<milestone>-<slice>`), each linked to issue #399.
- **Human reviews + merges every PR.** No self-merge; wait for green required
  checks. **No infra apply** this sprint — all live wiring is simulated +
  config-gated (Approach B is a SIT follow-up).

## 2. Create the worktree (off latest `main`)

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform fetch origin
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform worktree add `
  ..\wt\sprint-29-foundry-iq-context -b sprint-29/m0-envelope origin/main
```

The session rebranches per milestone off the latest `main` as earlier milestone
PRs merge (`git fetch origin && git switch -c sprint-29/m1-conversation origin/main`).

To remove the worktree after the sprint's PRs merge:

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform worktree remove ..\wt\sprint-29-foundry-iq-context
```

## 3. Seed tool auto-approvals (per-worktree, not inherited)

A fresh worktree starts with an empty tool-approval set. Either launch with
`copilot --allow-all-tools`, or seed approvals per the
[parallel-session runbook §7](../superpowers/handoffs/parallel-session-runbook.md#7-auto-approval-permissions-are-per-worktree-not-inherited)
(run with all sessions closed; keep the `.bak-seed-*` backup).

## 4. Delegate to the Copilot CLI session

Launch a fresh Copilot CLI agent **inside the worktree** and paste the Section 5
prompt. The session drafts/refreshes `plan.md`, stops at a plan-confirmation
gate, then implements milestone-by-milestone with TDD.

```powershell
Set-Location ..\wt\sprint-29-foundry-iq-context
copilot --allow-all-tools
```

Optionally create a git-excluded `KICKSTART.md` in the worktree (auto-excluded via
`.git/info/exclude`) holding the Section 5 prompt, so the launcher seeds the tab.

## 5. Delegation prompt template

Paste into the Copilot CLI agent launched inside the Sprint 29 worktree
(`<issue>` = **399**):

```text
You are implementing Sprint 29 (Foundry IQ context architecture) in this
dedicated worktree. Work ONLY in this worktree; branch off main per milestone.

Read first (do not skip):
- docs/superpowers/plans/2026-07-26-sprint-29-foundry-iq-context-architecture.md
- docs/superpowers/specs/2026-07-26-sprint-29-foundry-iq-context-architecture-design.md
- .github/copilot-instructions.md + AGENTS.md, then the relevant docs/adr/*
  (ADR-0032/0033/0044/0013/0016/0014) and docs/architecture/*iq* + *grounding*
- The existing app files the plan lists under "Existing files to mirror / modify"
  (read each target before editing it).

Rules:
- Superpowers skills are mandatory: writing-plans -> confirm plan.md with me ->
  test-driven-development -> subagent-driven-development (one task at a time,
  fresh subagent + quality review per task) -> verification-before-completion.
- Follow the milestone order M0 -> (M1 ‖ M2) -> M3 -> M4 -> M5 -> M6.
- TDD every task: write the failing test first, run it, implement, re-run green.
- Stay strictly app-side (apps/hcc-app-fluent) + one ADR + PRD rows. NO infra
  apply; all live wiring (Foundry threads, Fabric RLS, OBO) is SIMULATED and
  config-gated. Synthetic / no-PHI only. Region-agnostic config.
- App gates per slice: npm --prefix apps/hcc-app-fluent run lint && ... run build
  && ... test; plus Playwright smoke + axe-core a11y where UI changes. Route
  UX/a11y questions to the ux-design-agent.
- Runtime python (not python3). Doc edits: check_mojibake.py + markdownlint-cli2,
  bump SemVer headers, commit with the hook bypass (git -c core.hooksPath=/dev/null).
- One SMALL PR per milestone slice (branch sprint-29/<milestone>-<slice>), linked
  to issue #<issue>. Never self-merge; wait for green required checks.
- Assign the real ADR number at execution (next free, ~0045; verify 0043/0044
  collisions via git ls-tree). Replace 00NN and confirm every file path first.
- Report DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED at each milestone end.

First: draft/refresh plan.md for M0 and ask me to confirm before coding.
```

## 6. Integration + finish

- Merge M0 first (foundation), then M1/M2, then M3 → M4 → M5 → M6, each as its own
  human-reviewed PR. Rebranch off the latest `main` per milestone.
- **Acceptance gate (sprint):** the design §7 Definition of done is fully green —
  envelope on every IQ read/agent turn; per-agent thread isolation; role-first
  default board; simulated per-user RLS; guard/unit/golden tests green; provenance
  preserved; ADR recorded. File the **SIT live-wiring follow-up** (Approach B) as
  a new tracked issue.
- Use `superpowers:finishing-a-development-branch` per milestone PR.
- After all slices merge, remove the worktree (Section 2).

## 7. Coordinator note (design-spec relocation)

The Sprint 29 design was drafted on branch `sprint-27/curavias-ux-polish` as
`docs/superpowers/specs/2026-07-26-foundry-iq-context-architecture-design.md`. It
has been **relocated + renumbered** onto `main` as
`docs/superpowers/specs/2026-07-26-sprint-29-foundry-iq-context-architecture-design.md`.
The Sprint 27 stream should `git rm` its branch-local draft copy before opening
its PR to avoid a duplicate landing on `main`.
