# Parallel-Session Runbook (Curavias Copilot Sessions)

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-24 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | - (initial runbook) |

> **Purpose**: The durable how-to for running the platform with multiple
> parallel Copilot CLI sessions (one per sprint) on a trunk-based, short-lived
> branch model. Covers how to **start** sessions, how to **close/wrap** a sprint
> session, and how to **establish a new work-stream** session. Complements the
> point-in-time `handoffs/*.md` snapshots, which capture live state at a break.

## 1. Model in one paragraph

Each active sprint runs in its own **git worktree** under `..\wt\<name>` with a
dedicated Copilot CLI session (tab). The **main repo checkout** is the
**coordinator** session (review triage, main-health, spinning streams up/down).
All streams branch off `main`, ship **one squash-merge PR** each, and **a human
reviews and merges every PR** (agents never self-merge). Wait for green required
checks before merging - never admin-merge a red PR (it poisons `main` for every
parallel branch).

## 2. Machine-local tooling (not committed)

| Artefact | Path | Role |
|----------|------|------|
| Launcher | `C:\Users\urruegg\source\urruegg\start-curavias-sessions.ps1` | Opens one Windows Terminal window with a tab per worktree, each running `copilot --allow-all-tools`. Auto-discovers worktrees via `git worktree list`, coordinator first. |
| Desktop shortcut | `Desktop\Curavias Copilot Sessions.lnk` | Double-click to run the launcher hidden. |
| Per-worktree kick-start | `<worktree>\KICKSTART.md` | Tailored first-prompt for that stream. **Git-excluded** via `.git/info/exclude` (shared across worktrees), so it never shows in `git status`. |

The launcher seeds each tab's session with its `KICKSTART.md` via
`copilot --allow-all-tools -i <prompt>` (auto-runs the prompt, which ends at a
plan-confirmation gate, so auto-run is safe). Run with `-NoKickstart` to open
plain shells instead. These files use absolute machine paths and are
intentionally **not** committed.

## 3. START sessions (resume all streams)

1. **Double-click** the desktop shortcut `Curavias Copilot Sessions.lnk`
   (or run `start-curavias-sessions.ps1`). One Windows Terminal window opens
   with a tab per worktree; each session auto-runs its `KICKSTART.md`.
2. In the **coordinator** tab, let it read the latest `handoffs/*.md` and refresh
   `git worktree list` / `gh pr list` / `gh issue list`, then review its status.
3. In each **sprint** tab, the session refreshes its branch state and drafts/
   refreshes `plan.md`, then stops at a plan-confirmation gate. Confirm or
   redirect before it codes.

If a stream has no `KICKSTART.md` yet, that tab opens a plain shell; paste a
kick-start prompt manually or create the file (see section 5).

## 4. CLOSE / wrap a sprint session

When pausing or finishing a stream:

1. **Commit WIP** on the sprint branch. For docs, bump SemVer headers, run
   `npx markdownlint-cli2` + `python scripts/lint/check_mojibake.py --staged`,
   then commit with the hook bypass: `git -c core.hooksPath=/dev/null commit`.
2. **Push** the branch and **open one squash-merge PR** (or update the existing
   one). Fill the PR Output Contract (FR/NFR IDs, lane impact, test evidence,
   security/infra impact). Do **not** self-merge - hand it to the human.
3. **Update the handoff**: refresh (or create) `docs/superpowers/handoffs/<date>-
   parallel-sprint-handoff.md` with each stream's branch + next step, open PRs,
   and the merged log. Save a copy to the session `files/` folder.
4. **After a PR squash-merges**: `git worktree remove <path>` and delete the
   branch (repo auto-deletes on merge). Re-running the launcher then simply omits
   the retired tab.

## 5. ESTABLISH a NEW work-stream session

1. **File a GitHub issue** describing the stream (sprint/lane labels, governing
   FR/NFR IDs). This issue governs the branch.
2. **Add a worktree off fresh main**:

   ```powershell
   git -C <repo> fetch origin main
   git -C <repo> worktree add ..\wt\<name> -b sprint-NN/<topic> origin/main
   ```

3. **Create `<worktree>\KICKSTART.md`** (git-excluded automatically). Include:
   worktree path + branch (tell the session to verify via `git`), the governing
   issue #, a read-order (sprint spec -> `.github/copilot-instructions.md` +
   `AGENTS.md` -> relevant `docs/*`), the mandatory Superpowers skills
   (`writing-plans` -> confirm plan -> `test-driven-development` ->
   `verification-before-completion`), the exact next slice/scope, the standing
   constraints (trunk-based, human-merge, doc SemVer, hook bypass), and
   "draft plan.md and ask me to confirm before coding."
4. **Relaunch** the shortcut - the new worktree is auto-discovered and gets its
   own seeded tab. No launcher edits needed.

## 6. Standing constraints (all streams)

- A human reviews and merges **every** PR; agents never self-merge or auto-merge.
- Trunk-based short-lived branches: one issue -> one branch -> one squash-merge
  PR -> delete branch/worktree on merge. Base every branch on `main` (no stacks).
- Any deploy/delete is hard-gated by `approved-to-apply` + human execution
  (AGENTS.md section 4) - critical for destructive PROD work (Sprint 19).
- Docs: bump the SemVer header per copilot-instructions section 9; pass
  markdownlint + mojibake before commit.
- Windows quirks: use `python` (not the `python3` Store stub); the pre-commit
  mojibake hook false-fails on Windows, so verify manually and commit with
  `git -c core.hooksPath=/dev/null commit`. CI mojibake-scan is the real backstop.
