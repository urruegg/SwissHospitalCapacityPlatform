# Development Workflow

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-24 |
| **Author** | Urs Rueegg |
| **Status** | Accepted |
| **Previous Version** | 1.0.0 (initial version) |

> The simplest, best-practice way to run two to three parallel sprints on one
> desktop with GitHub issues and pull requests as the control plane. Formalised
> in [ADR-0038](adr/0038-trunk-based-parallel-sprint-workflow.md), which
> supersedes the retired contract-based branch-locking practice.

## The model in one sentence

**`main` is the trunk and baseline of truth; each parallel sprint is a worktree
with its own Copilot CLI session; CI is the merge gate; a human merges every
pull request.**

## 1. Directory layout

The root checkout stays on `main`. Each parallel sprint runs in its own worktree
next to the repository, so concurrent workers never share a working directory.

```text
SwissHospitalCapacityPlatform/        # root checkout, always on main (baseline of truth)
../wt/sprint-30-forecast/             # worktree, branch sprint-30/forecast, its own CLI session
../wt/sprint-31-bedboard/             # worktree, branch sprint-31/bedboard, its own CLI session
../wt/sprint-32-compliance/           # worktree, branch sprint-32/compliance, its own CLI session
```

Create a worktree with the helper (it always branches off the latest `main`):

```powershell
./scripts/dev/new-sprint-worktree.ps1 -Sprint 30 -Topic forecast
```

Then start an independent Copilot CLI session inside it. The CLI keys its session
and session-state to the working directory, so each worktree is a fully isolated
worker on the same desktop:

```powershell
cd ../wt/sprint-30-forecast
copilot --allow-all-tools
```

## 2. Branching rules

* **One issue, one branch, one squash pull request.** Name branches
  `sprint-NN/<topic>`.
* **Always branch off `main`. Never stack** a branch on another feature branch —
  stacking is what stranded PRs #291-#295.
* **Rebase onto `main` frequently** so integration conflicts surface early.
* **Delete the branch and its worktree immediately** after the pull request is
  squash-merged.

## 3. CI is the only merge lock

The repository squash-merges everything, so `git cherry` and "N commits ahead"
lie — a branch identical to `main` can still look many commits ahead. Trust the
**pull request merge state**, never diff or ancestry heuristics.

* Branch protection on `main` requires the check suite to pass. Green CI is the
  proof that a branch is mergeable — no manual file locking.
* **A human merges every pull request.** Agents open, update, and green pull
  requests but never self-merge.

## 4. GitHub is the control plane

* **Every sprint is tracked by a sprint-tracker issue** created from the
  [sprint-tracker template](../.github/ISSUE_TEMPLATE/sprint-tracker.yml). The
  tracker links the sprint's spec and plan documents, names the GitHub milestone,
  and lists the child task issues.
* **Each child task issue becomes one short-lived branch and one squash pull
  request**, assigned to the sprint milestone.
* **Deploys are pull-request-gated.** Merging an `infra/**` change to `main`
  triggers the environment deploy workflow; deploy and delete actions require an
  `approved-to-apply` comment per [AGENTS.md](../AGENTS.md) section 4.

### Label taxonomy

Prefixed labels keep issue and pull-request context legible at a glance, aligned
to how we **work**, **review**, and **approve**. The bare, sprint-specific labels
created in earlier sprints are legacy; new work uses these prefixes. The taxonomy
is codified in [`.github/labels.yml`](../.github/labels.yml) (single source of
truth) and applied idempotently by `python scripts/labels/sync_labels.py --apply`
or the manual **label-sync** workflow (`workflow_dispatch`).

| Prefix | Labels | Meaning |
| ------ | ------ | ------- |
| `sprint-NN` | `sprint-30`, `sprint-31`, ... | Which sprint the work belongs to |
| `type:` | `type:spec`, `type:plan`, `type:feat`, `type:fix`, `type:docs`, `type:infra`, `type:ci`, `type:test`, `type:refactor`, `type:perf`, `type:chore` | What kind of change (Conventional Commits) |
| `lane:` | `lane:governance`, `lane:control`, `lane:infra`, `lane:data`, `lane:ai`, `lane:experience` | Which architecture lane |
| `status:` | `status:wip`, `status:review`, `status:approved`, `status:blocked` | Lifecycle state |
| `deploy:` | `deploy:sit`, `deploy:prod` | Deployment intent |

The `status:` labels track the **work -> review -> approve** lifecycle of every
issue and pull request:

| Stage | Label | Set when |
| ----- | ----- | -------- |
| **Work** | `status:wip` | An issue is being implemented / a PR is a draft |
| **Review** | `status:review` | CI is green and the PR is handed off for human review |
| **Approve** | `status:approved` | A human has reviewed and approved it to proceed / merge (this is the tracking label for the `approved-to-apply` gate on `deploy:*` PRs) |
| _(off-track)_ | `status:blocked` | Work cannot proceed; document why |

Exactly one `status:` label should be present at a time; move it forward as the
item progresses. `status:approved` is set by the human reviewer, never by an
agent or bot.

## 5. Auto-approve: CLI is not the same as VS Code

`chat.tools.autoApprove` is a **VS Code** setting and does **not** apply to the
Copilot CLI. Use the mechanism that matches your worker.

**Recommended posture — scoped auto-approve, not blanket YOLO.** Auto-approve the
safe, high-frequency operations (read, build, test, lint, in-worktree `git`) and
keep push-to-`main`, deploy, and delete human-gated. This preserves "CI proves
the merge, a human merges" while removing prompt friction.

Copilot CLI (per worktree session):

```powershell
copilot --allow-all-tools
```

VS Code (workspace `.vscode/settings.json`), if you drive a sprint from the
editor instead of the CLI:

```json
{
  "chat.tools.global.autoApprove": true,
  "chat.tools.terminal.autoApprove": {
    "rm": false,
    "rmdir": false,
    "git push": false
  }
}
```

Do not commit a blanket auto-approve into the shared repository; keep it in your
local settings.

## 6. Sub-agent delegation from the plan

Each sprint's lead CLI session owns the plan and dispatches slices to sub-agents:

1. Write the plan with the `writing-plans` skill (spec then plan document, both
   merged to `main` before execution).
2. Execute with `subagent-driven-development` / `dispatching-parallel-agents`:
   the lead session delegates independent slices to sub-agents, each landing as a
   commit on the sprint branch.
3. Verify with `verification-before-completion` before opening the pull request:
   run the check command, read the output, then claim the result.

## 7. Branch-protection settings for `main`

Configure once in repository settings (Settings then Branches then add rule for
`main`):

* Require a pull request before merging.
* Require status checks to pass before merging; select the repository's required
  checks (markdown lint, mojibake scan, Bicep build, Superpowers contract, and
  any lane-specific checks).
* Require branches to be up to date before merging.
* Do not allow bypassing the above settings; do not grant merge to bot
  identities.

## 8. Lifecycle checklist per sprint

1. Open a sprint-tracker issue; link spec and plan; create the `sprint-NN` label
   and the GitHub milestone.
2. For each task: open a task issue, create a worktree and branch off `main`,
   start an isolated CLI session, implement a small vertical slice.
3. Open a squash pull request; label it; get CI green; hand off to a human to
   merge.
4. On merge: delete the branch and remove the worktree; check the next task off
   the tracker.
5. Close the tracker and the milestone when the sprint's definition of done is
   met.
