# ADR-0038: Trunk-based parallel-sprint development workflow

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-23 |
| **Author** | Urs Rueegg |
| **Decision-makers** | @urruegg |
| **Related issue** | Sprint-close retrospective (Epic #276) |

## Context

The Epic #276 sprint exposed recurring friction in how work was branched,
integrated, and tracked while two or three efforts progressed in parallel on a
single developer desktop:

* A **contract-based branch-locking** convention was used to reserve files and
  serialize changes. Continuous integration already verifies whether a branch is
  mergeable, so the manual lock duplicated that guarantee and mostly added
  coordination overhead.
* **Stacked pull requests** (branches based on other feature branches rather than
  `main`) stranded work: PRs #291-#295 could not land independently and had to be
  consolidated into PR #297.
* The repository **squash-merges** every pull request. As a result, ancestry
  heuristics such as `git cherry` and "N commits ahead" report false positives —
  a branch whose content is byte-identical to `main` still appears to be many
  commits ahead. The only reliable "is it merged?" signal is the pull request
  merge state.
* Parallel work in a **single working directory** caused index contention and
  context bleed between concurrent efforts.

The team wants a simple, best-practice model that supports two to three parallel
sprints, keeps GitHub issues and pull requests as the development control plane,
keeps `main` as the local baseline of truth with work-in-progress layered on top,
and lets each Copilot CLI worker run an independent session on the same desktop.

## Decision

Adopt a trunk-based, worktree-per-sprint workflow. It is documented in full in
[docs/DEV_WORKFLOW.md](../DEV_WORKFLOW.md); the binding decisions are:

* **`main` is the trunk and the baseline of truth.** The root checkout stays on
  `main`. All work-in-progress lives in short-lived branches layered on top.
* **One worktree per parallel sprint, one Copilot CLI session per worktree.**
  Each sprint gets a dedicated `git worktree` on its own branch. Launching the
  Copilot CLI inside a worktree yields an independent session and session-state,
  so concurrent workers on the same desktop do not collide.
* **Short-lived branches, always based on `main`. No stacking.** One issue maps
  to one branch to one squash pull request. Branches are rebased onto `main`
  frequently and never based on another feature branch.
* **CI is the only merge lock.** Branch protection on `main` requires the check
  suite to pass. The manual contract-based file-locking convention is retired.
* **A human merges every pull request.** Agents open, update, and green pull
  requests but never self-merge. Deploy and delete steps remain gated by the
  `approved-to-apply` control in [AGENTS.md](../../AGENTS.md) section 4.
* **GitHub is the control plane.** Every sprint is tracked by a persistent
  sprint-tracker issue that links its spec and plan documents and lists its child
  task issues, using the
  [sprint-tracker template](../../.github/ISSUE_TEMPLATE/sprint-tracker.yml).
  Issues and pull requests are labelled with prefixed `type:`, `lane:`,
  `status:`, and `deploy:` labels plus the sprint's `sprint-NN` label.
* **Merged branches and their worktrees are deleted immediately.** State is read
  from the pull request merge status, not from diff or ancestry heuristics.

This ADR supersedes the contract-based branch-locking practice for all new work.

## Consequences

### Positive

* Removes the manual locking overhead while preserving the mergeability
  guarantee CI already provides.
* Eliminates the stacked-PR trap by mandating branches off `main`.
* Gives each parallel worker true filesystem and session isolation on one
  desktop.
* Makes sprint context legible in GitHub through trackers and a consistent label
  taxonomy.

### Negative

* Requires discipline to rebase short-lived branches onto `main` frequently so
  integration conflicts surface early rather than at a late merge.
* Parallel sprints that touch the same files can still conflict at merge time;
  scoping sprints to different architecture lanes reduces but does not remove
  this.

### Neutral

* Does not change the human-in-the-loop deploy and delete controls or the
  `approved-to-apply` gate.
* Does not alter the governance-protected files
  ([AGENTS.md](../../AGENTS.md), [.github/copilot-instructions.md](../../.github/copilot-instructions.md),
  `.github/copilot/mcp.json`, `.github/CODEOWNERS`), which continue to require a
  human-authored issue and CODEOWNERS review.

## Alternatives considered

| Alternative | Why rejected |
| ----------- | ------------ |
| Keep contract-based file locking | Duplicates the CI mergeability check and adds coordination friction for parallel work. |
| Single shared working directory with branch switching | Causes index contention and context bleed between concurrent efforts; defeats independent CLI sessions. |
| Separate full clones per sprint instead of worktrees | Heavier on disk and slower to set up; worktrees share one object store and are lightweight. |
| Long-lived per-sprint integration branches | Reintroduces drift and the stacked-PR consolidation problem this ADR removes. |

## Links

* [Development workflow guide](../DEV_WORKFLOW.md)
* [Sprint-tracker issue template](../../.github/ISSUE_TEMPLATE/sprint-tracker.yml)
* [New-sprint worktree helper](../../scripts/dev/new-sprint-worktree.ps1)
* [AGENTS.md section 4: deploy/delete confirmation](../../AGENTS.md)
* Epic #276 (sprint-close retrospective source)
