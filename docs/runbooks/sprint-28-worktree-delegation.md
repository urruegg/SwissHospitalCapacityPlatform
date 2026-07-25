# Sprint 28 - Worktree Delegation Runbook (parallel Copilot CLI)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-25 |
| **Author** | Urs Rueegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |

> **Purpose:** package the 8 Sprint 28 workstreams so each can be built **in
> parallel** by a fresh Copilot CLI agent in its own isolated git worktree.
> Grounded in the [Sprint 28 design](../superpowers/specs/2026-07-25-sprint-28-product-owner-agent-design.md)
> and [plan](../superpowers/plans/2026-07-25-sprint-28-product-owner-agent.md).
> Builds on the `superpowers:using-git-worktrees` and
> `superpowers:subagent-driven-development` skills.

---

## 1. Model

- **One worktree = one workstream = one branch = one PR.** Isolated workspaces so
  parallel agents never fight over the working tree.
- **Order:** merge `WS-G0` (contracts) and land `WS-INF` `what-if` **first**; then
  run `WS-A / WS-B / WS-C / WS-D / WS-X` **in parallel**; then `WS-RT` integrates.
- **Every agent** reads: its workstream section of the plan, the design spec, the
  frozen contracts (`G0.2`), and the repo patterns it mirrors (Sprint 21/22/23).
- **Human reviews + merges every PR.** No self-merge. Every `deploy` waits for an
  `approved-to-apply` comment.

## 2. One-time setup

```powershell
# From the repo root. Worktrees live under .worktrees/ (git-ignored).
git worktree list
New-Item -ItemType Directory -Force -Path .worktrees | Out-Null
```

## 3. Per-workstream worktree creation

Run once per workstream (branch off the latest `main`):

```powershell
git fetch origin
$ws = "ws-g0-governance"      # replace per workstream (see table in Section 5)
git worktree add ".worktrees/$ws" -b "sprint-28/$ws" origin/main
```

To remove a finished worktree after its PR merges:

```powershell
git worktree remove ".worktrees/ws-g0-governance"
```

## 4. Delegating a worktree to Copilot CLI

From inside the worktree directory, launch a fresh Copilot CLI agent scoped to
that workstream. Use the prompt template in [Section 6](#6-delegation-prompt-template).

```powershell
Set-Location ".worktrees/sprint-28-ws-a-corpus"
# Launch your Copilot CLI here, pasting the Section 6 prompt with WS = A.
```

## 5. Workstream -> worktree map

| WS | Branch (`sprint-28/...`) | Plan section | Wave | Depends on |
| -- | ------------------------ | ------------ | ---- | ---------- |
| G0 | `ws-g0-governance` | WS-G0 | 1 (first) | - |
| INF | `ws-inf-bicep` | WS-INF | 1 (first) | G0 contracts |
| A | `ws-a-corpus` | WS-A | 2 (parallel) | INF |
| B | `ws-b-liveproof` | WS-B | 2 (parallel) | G0 |
| C | `ws-c-cost` | WS-C | 2 (parallel) | G0 |
| D | `ws-d-ontology` | WS-D | 2 (parallel) | G0 |
| X | `ws-x-rail` | WS-X | 2 (parallel) | G0 |
| RT | `ws-rt-runtime` | WS-RT | 3 (last) | A/B/C/D |

**Wave 1** must merge before Wave 2 starts (contracts + provision plan). **Wave 2**
runs fully in parallel. **Wave 3** (`RT`) starts once A/B/C/D expose their tools.

## 6. Delegation prompt template

Paste into the Copilot CLI agent launched inside the workstream's worktree, with
`<WS>` filled in (`<issue>` = **377** for this sprint):

```text
You are implementing workstream <WS> of Sprint 28 (Curavias Product Owner Agent).

Read first (do not skip):
- Plan section WS-<WS> in docs/superpowers/plans/2026-07-25-sprint-28-product-owner-agent.md
- Design spec docs/superpowers/specs/2026-07-25-sprint-28-product-owner-agent-design.md
- Frozen contracts from task G0.2 (GroundedChunk + tool signatures)
- The repo patterns your plan section says to mirror (Sprint 21/22/23)

Rules:
- Use superpowers:subagent-driven-development; one task at a time, TDD, frequent commits.
- Stay strictly within workstream <WS>'s files; do not touch other workstreams.
- Runtime python (not python3). Synthetic / no-PHI only. Region Switzerland North.
- Ingestion/refresh jobs are Azure Container Apps, never GitHub workflows.
- Never apply any az deployment; produce what-if only and stop for approved-to-apply.
- Doc edits: run scripts/lint/check_mojibake.py + markdownlint-cli2; bump version headers.
- Open ONE PR for this workstream, linked to issue #<issue>. Never self-merge.
- Report status DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED at the end.
```

## 7. Integration + finish

- When Wave 2 PRs are merged, start `WS-RT` (Wave 3) in its worktree; it imports
  the A/B/C/D tools and wires the orchestrator + eval harness.
- Run the per-persona golden-question harness (`evals/product-owner-agent/run_evals.py`)
  as the sprint acceptance gate: citation coverage >= 95%, zero CFO/CISO/CLO
  hallucination, DE/EN + Partner personas covered.
- Use `superpowers:finishing-a-development-branch` per workstream PR.
- After all worktrees merge, remove them: `git worktree remove .worktrees/<ws>`.
