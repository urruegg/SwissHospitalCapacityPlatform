# Parallel-Sprint Session Handoff — 2026-07-26

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-26 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | — (supersedes the 2026-07-24 snapshot) |

> **Purpose**: A point-in-time snapshot to resume the coordinator session **and**
> the parallel sprint sessions from a documented state. Not a durable contract —
> regenerate/replace on the next break. The durable how-to lives in
> [`parallel-session-runbook.md`](parallel-session-runbook.md).

## 1. Baseline

- `main` HEAD at snapshot: **`d835de2`** — CI green.
- **SIT and PROD infra deploys are both GREEN** as of this snapshot (see §2).
- Trunk-based, short-lived branches; **a human reviews and merges every PR**
  (agents never self-merge). Wait for green **required** checks before merging;
  never admin-merge a red PR (it poisons `main` for every parallel branch).
- Windows quirks: use `python` (not `python3`); the pre-commit mojibake hook
  false-fails — verify with `python scripts/lint/check_mojibake.py` then commit
  with `git -c core.hooksPath=/dev/null commit`.

## 2. Main-health resolution this cycle (coordinator-owned)

The SIT→PROD deploy chain was broken by the Sprint 28 PO-Agent infra (#384) and
is now fully restored:

- **#392** — pin PO-Agent OpenAI account to `eastus2` (SIT has no westus2 OpenAI
  quota) → cleared `SpecialFeatureOrQuotaIdRequired`.
- **#394** (WS-INF) — pin PO-Agent model to **gpt-5 / GlobalStandard** for
  switzerlandnorth (gpt-4o is deprecated/blocked for new deployments).
- **#397** — `enablePoAgentRuntimeModule = false` in **SIT** only (interim, while
  the model config settled) → SIT deploy green.
- **#398** — `enableCuraviasWebModule = false` in **prod-swn + prod** → cleared
  `PublicAccessNotPermitted` on the public-website media storage account; PROD
  deploy green.

Verified: SIT deploy run on `d835de2` ✓; PROD deploy run on `d835de2` ✓
(what-if + deploy).

### Coordinator-owned param pins — DO NOT touch in sprint PRs

These `*.bicepparam` toggles are main-health pins. Sprint streams must **not**
change them (rebasing onto `main` is fine; re-flipping them is not):

- `sit.bicepparam`: `poAgentOpenAiLocation = 'eastus2'`,
  `enablePoAgentRuntimeModule = false`.
- `prod-swn.bicepparam` / `prod.bicepparam`: `enableCuraviasWebModule = false`.
- PO-Agent module config on `main`: **gpt-5 / 2025-08-07 / GlobalStandard** —
  do not reintroduce gpt-4o or a westus2 OpenAI location.

## 3. Open PRs (needs human review)

Both are **draft** Sprint 28 (PO Agent) streams. **Merge order: #396 → #395**
(the WS-X app rail consumes the WS-RT runtime). Both last committed at 05:13,
**before** `d835de2`, so both must sync with `main` and re-run checks.

| PR | Branch | State | Directive |
|----|--------|-------|-----------|
| **#396** | `sprint-28/ws-rt-runtime` | draft, required checks **green** | Merge `origin/main`, re-run CI, then **Ready for review** → human merges. First in order. |
| **#395** | `sprint-28/ws-x-rail` | draft, **3 app checks RED** (`hcc-app-fluent` lint+unit+build, Playwright smoke, axe-core a11y) | Wait for #396 to land, rebase on it, **fix the red checks** (WS-X feature work; route UX/a11y via `ux-design-agent`), then Ready → human merges. |

Per-PR guidance was posted as coordinator comments on #395 and #396.

## 4. Active worktrees / sessions

Branches captured from `git worktree list`; each session owns its slice and its
own `plan.md`. **All streams: rebase/merge `main` (`d835de2`) to pick up the
main-health fixes before pushing.**

| Worktree | Branch | Next step |
|----------|--------|-----------|
| `SwissHospitalCapacityPlatform` (main workdir) | coordinator | Main-health, review triage, spinning streams up/down. |
| `wt/sprint-28-product-owner-agent` | `sprint-28/ws-x-rail` (+ `sprint-28/ws-rt-runtime`) | See §3. Runtime (#396) first, then app rail (#395). |
| `wt/curavias-web-retire` | `chore/retire-public-website` | Decommission the public website: remove the `curavias-web` module + its params entirely (supersedes the #398 toggle). Aligns with #268. |
| `wt/sprint-27-curavias-ux-polish` | `sprint-27/curavias-ux-polish` | Curavias app UX polish; route visual/a11y via `ux-design-agent`. |
| `wt/sprint-26-decision-ontology` | `sprint-26/ws-c-apply-runbook` | Sprint 26 decision-ontology WS-C apply runbook. Issue #335. |
| `wt/sprint-23-org-skills-refactor` | `sprint-23/eh-flip-execution` | Remaining #255 items (EventHub flip execution). |
| `wt/sprint-19-prod-switzerland-north` | `sprint-19/fix-po-agent-openai-swn-sku` | PO-Agent OpenAI SWN SKU follow-up. Coordinate with the gpt-5/GlobalStandard config now on `main`. Issue #239. |
| `wt/runbook-autoapprove` | `docs/runbook-per-worktree-autoapproval` | Per-worktree auto-approval runbook doc. |

## 5. Standing protocol for every stream (re: not-merging PRs)

1. **Sync first.** `main` moves under you. Before pushing or marking ready:
   `git fetch origin && git merge origin/main` (or rebase). Resolve conflicts
   toward the config on `main` (see §2 pins).
2. **Green before ready.** Only mark a PR *Ready for review* when **all required
   checks pass**. A red draft stays draft — fix it in your session.
3. **Human merges.** Never self-merge or admin-merge. The coordinator triages
   ready+green PRs and hands them to the human.
4. **One issue → one branch → one squash-merge PR → delete branch/worktree.**
   No stacks; base every branch on `main`.
5. **Deploy/delete is hard-gated** by `approved-to-apply` + human execution
   (AGENTS.md §4).
6. **Don't touch coordinator-owned main-health pins** (§2).

## 6. Open tracker issues (carried)

`#377` Sprint 28 PO Agent · `#335` Sprint 26 · `#305` Sprint 20 · `#255`
Sprint 23 · `#239` Sprint 19 · `#275` PROD go-live gap · `#270` PROD Fabric IQ
Ontology blocked · `#268` retire public website (Sprint 24) · `#252` IaC
parity gaps.

## 7. How to resume a session

See [`parallel-session-runbook.md`](parallel-session-runbook.md) §3 (START) and
§5 (establish a new stream). Kick-start skeleton for any sprint session:

```text
You work ONLY in this worktree: <path>. Branch: <branch>. Issue: #<n>.
1. Read: the sprint's design spec under docs/superpowers/specs/, then
   .github/copilot-instructions.md + AGENTS.md, then the relevant docs/*.md,
   then the latest docs/superpowers/handoffs/*.md.
2. Superpowers skills are mandatory: writing-plans -> confirm plan with me ->
   test-driven-development -> verification-before-completion.
3. FIRST sync with main (git fetch origin && git merge origin/main).
4. Scope = the next slice only (see the worktree row in this handoff).
5. Trunk-based: ONE squash-merge PR, do NOT self-merge, wait for green checks.
   Bump doc SemVer headers; run markdownlint + check_mojibake.py; commit with
   the hook bypass. PR lists FR/NFR IDs, lane impact, test evidence, issue link.
First: draft/refresh plan.md for the slice and ask me to confirm before coding.
```
