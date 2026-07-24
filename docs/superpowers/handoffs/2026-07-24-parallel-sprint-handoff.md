# Parallel-Sprint Session Handoff — 2026-07-24

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-24 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | — (initial handoff snapshot) |

> **Purpose**: A point-in-time snapshot to pause and later resume the coordinator
> session **and** the parallel sprint sessions from a documented state. Not a
> durable contract — regenerate/replace on the next break.

## 1. Baseline

- `main` HEAD at snapshot: **`f8ed875`** — CI green (5 required checks).
- Trunk-based, short-lived branches; **a human reviews and merges every PR**
  (the agent never self-merges). Wait for green required checks before merging.
- Windows quirks: use `python` (not `python3`); the pre-commit mojibake hook
  false-fails — verify with `python scripts/lint/check_mojibake.py` then commit
  with `git -c core.hooksPath=/dev/null commit`.

## 2. Open PR (needs human review)

| PR | Branch | State | Scope |
|----|--------|-------|-------|
| **#355** | `sprint-20/fix-e2e-testid` | CLEAN | Dedup board-bed-manager testid + refresh stale parity e2e (follow-up #352). |

## 3. Active worktrees / sessions

| Worktree | Branch | Clean? | Status & next step |
|----------|--------|--------|--------------------|
| `wt/sprint-19-prod-switzerland-north` | `sprint-19/harden-signal-runner-identity` | clean | Last work merged (#354, #347, #343). **Next:** PROD deploy to Switzerland North (#239) — `approved-to-apply`-gated `what-if` first. |
| `wt/sprint-20-app-parity` | `sprint-20/fix-e2e-testid` | 1 dirty | Full screen parity merged (#352). **PR #355 open.** **Next:** merge #355, then remaining parity items (#305) incl. SPA history-fallback #299. |
| `wt/sprint-23-org-skills-refactor` | `sprint-23/fix-hsl-orphan-349` | clean | Org spine + skills ontology + gold contract merged (#341/#344/#345/#348/#350). **Next:** remaining #255 items. |
| `wt/sprint-26-decision-ontology` | `sprint-26/status-break` (pushed `e549771`) | clean | **WS-A Foresight tier done+merged** (#346, #351, #353). Branch records WS-A-complete status. **Next:** WS-B lever catalog + deterministic expected-impact tool (local branch `sprint-26/ws-b-levers` exists). Issue #335. |
| `SwissHospitalCapacityPlatform` (main workdir) | `review/ama-hospital-ops-lead-2026-07-17` (merged via #337) | 8 dirty | **Parked / coordinator baseline.** Dirty = pre-existing untracked drafts owned by other sprints (see §5) — do NOT bulk-commit. |

## 4. What landed this cycle (merged since the last break)

`#340` unbreak main lint · `#341` org/skills gold contract (WS-C3) · `#342` evidence
fixture regen · `#343` codify ca-signal-runner Bicep · `#344` Curavias org spine +
skills ontology (WS-C4) · `#345` S23 DoD reconcile · `#346` WS-A synthetic
forecast/driver/signal gold · `#347` retire eastus2 CD → switzerlandnorth ·
`#348` skills-evidence Fabric glue · `#349/#350` prune H_HSL orphan facts ·
`#351` WS-A foresight · `#352` Sprint 20 full screen parity · `#353` WS-A Fabric
SIT evidence · `#354` harden signal-runner UAMI.

## 5. Uncommitted drafts in the main workdir (triage per owning sprint)

These are untracked/modified in the coordinator workdir — assign to the right
sprint branch before committing; do not sweep into an unrelated PR:

- `docs/sprints/sprint-20-curavias-ux-redesign.md` (modified)
- `docs/sprints/sprint-25-trusted-signals-proactive-csa-and-app-parity.md`
- `docs/superpowers/ideas/sprint-23-unified-curavias-organiisation-platform -refactor.md`
- `docs/superpowers/ideas/unified-curavias-organisation-and-skills-ontology/`
- `docs/superpowers/specs/2026-07-23-curavias-app-parity-findings.md`
- `docs/superpowers/specs/2026-07-23-curavias-app-parity-review-outcome.md`
- `docs/superpowers/specs/2026-07-23-sprint-25-trusted-signals-proactive-csa-parity-design.md`
- `.vscode/settings.json`

## 6. Open tracker issues

`#335` Sprint 26 · `#305` Sprint 20 · `#255` Sprint 23 · `#239` Sprint 19 ·
`#304` narrow ci-infra-validate trigger · `#299` SPA history-fallback ·
`#296` CsaView Demo path · `#290` external-signal triage handoff ·
`#275` PROD go-live gap · `#270` PROD Fabric IQ Ontology blocked ·
`#268` Sprint 24 legal/DNS · `#258` authorise ux-design-agent ·
`#252` IaC parity gaps.

## 7. How to resume a session

Open a dedicated CLI tab per worktree (note the **quoted** title — an unquoted
multi-word title caused the earlier `0x80070002` error):

```powershell
wt.exe new-tab --title "S26 WS-B" -d "C:\Users\urruegg\source\urruegg\wt\sprint-26-decision-ontology" powershell.exe -NoExit -Command copilot --allow-all-tools
```

Kick-start prompt skeleton for any sprint session:

```text
You work ONLY in this worktree: <path>. Branch: <branch>. Issue: #<n>.
1. Read: the sprint's design spec under docs/superpowers/specs/, then
   .github/copilot-instructions.md + AGENTS.md, then the relevant docs/*.md.
2. Superpowers skills are mandatory: writing-plans -> confirm plan with me ->
   test-driven-development -> verification-before-completion.
3. Scope = the next slice only (see the sprint row in this handoff).
4. Trunk-based: branch off main, ONE squash-merge PR, do NOT self-merge.
   Bump doc SemVer headers; run markdownlint + check_mojibake.py; commit with
   the hook bypass. PR lists FR/NFR IDs, lane impact, test evidence, issue link.
First: draft/refresh plan.md for the slice and ask me to confirm before coding.
```
