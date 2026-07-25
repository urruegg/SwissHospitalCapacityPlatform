# Parallel-Session Runbook (Curavias Copilot Sessions)

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-07-24 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (added section 7 on per-worktree auto-approval) |

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
- Tool auto-approval is **per-worktree** and not inherited from parent folders -
  a fresh worktree re-prompts for everything until it is seeded (see section 7).

## 7. Auto-approval permissions are per-worktree (not inherited)

Copilot CLI persists **tool auto-approvals per directory** in
`~/.copilot/permissions-config.json` under `locations`, keyed by the session's
**git-worktree root**. Unlike `trustedFolders` in `config.json` (file-access
trust, which **is** prefix/ancestor-based), tool approvals are **not** inherited
from ancestor folders. So a worktree at `..\wt\<name>` starts with an **empty**
approval set and re-prompts for every tool, even though the main checkout
(`...\SwissHospitalCapacityPlatform`) is fully approved.

The launcher runs `copilot --allow-all-tools`, which covers a launcher-started
tab for its lifetime; this section is the fix for **persistent** approvals and
for sessions started **without** that flag (plain `copilot`, `-NoKickstart`,
manually attached tabs).

**Seed a worktree's approvals** (clone the main checkout's `tool_approvals` block
into each `..\wt\<name>` location key). Do this with **all CLI sessions closed** -
a live session may rewrite `permissions-config.json` from its in-memory map on
its next new approval and drop manual edits. Always keep the timestamped
`.bak-seed-*` backup the script writes.

```powershell
# node one-liner: clone main checkout approvals into every current worktree root
node -e "const fs=require('fs'),p='C:/Users/'+process.env.USERNAME+'/.copilot/permissions-config.json',c=JSON.parse(fs.readFileSync(p,'utf8')),cp=require('child_process');const root='C:\\Users\\'+process.env.USERNAME+'\\source\\urruegg\\SwissHospitalCapacityPlatform';const src=c.locations[root].tool_approvals;fs.writeFileSync(p+'.bak-seed-'+Date.now(),JSON.stringify(c,null,2));cp.execSync('git -C \"'+root+'\" worktree list --porcelain').toString().split(/\r?\n/).filter(l=>l.startsWith('worktree ')).map(l=>l.slice(9).replace(/\//g,'\\')).filter(w=>w!==root).forEach(w=>{c.locations[w]={tool_approvals:JSON.parse(JSON.stringify(src))}});fs.writeFileSync(p,JSON.stringify(c,null,2)+'\n');console.log('seeded '+Object.keys(c.locations).length+' locations');"
```

Then **restart the worktree sessions** so they load the seeded approvals. Repeat
after adding any new worktree (section 5). A durable alternative to seeding is to
rely on `--allow-all-tools` / autopilot for every worktree tab.
