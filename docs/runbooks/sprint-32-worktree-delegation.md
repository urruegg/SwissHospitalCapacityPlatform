# Sprint 32 — Worktree Delegation Runbook (Signal Agent)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-27 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |

> **Purpose:** package **Sprint 32** (Signal Agent — SGA) so it can be built by a
> **single fresh Copilot CLI agent in its own isolated git worktree**. Grounded in the
> [SGA+DQA design](../superpowers/specs/2026-07-27-sprint-31-32-signal-and-data-quality-agents-design.md)
> and the [Sprint 32 plan](../superpowers/plans/2026-07-27-sprint-32-signal-agent.md).
> Builds on the `superpowers:using-git-worktrees` and
> `superpowers:subagent-driven-development` skills. Sibling runbook:
> [Sprint 31 (DQA)](sprint-31-worktree-delegation.md).
>
> **⚠ Hard dependency — start AFTER Sprint 31.** SGA consumes the frozen
> `DC-DQ-GAP-v1` "new-source-needed" seam that Sprint 31 (DQA) merges to `main`. Do
> not begin the onboarding work until that seam is on `main`.

---

## 1. Model

- **One worktree = one session = the whole sprint.** Sprint 32 stands up a **new**
  `signal-agent` (sibling to the runtime `signal-triage-agent`) that owns the
  **channel-intake lifecycle** — discover → classify → adapter → contract →
  ontology-bind → sandbox-test → HITL-activate → monitor — with the flagship
  **certification register → skills baseline** worked example. It is concentrated in
  `data-platform/signals/` (Python) + a new `agents/signal-agent/` pack +
  `data/synthetic/schema/` contract + ontology + governance docs, so it runs in
  **one** dedicated worktree.
- **Milestone chain (design §11):** `S0 → S1 → … → S6`, realised as the plan's tasks
  **T1–T7** (issue **#454**). Demand-driven — SGA onboards the channel a Sprint 31
  `DC-DQ-GAP-v1` `newSourceNeeded` record asked for.
- **Trunk-based per [ADR-0038](../adr/0038-trunk-based-parallel-sprint-workflow.md):**
  short-lived branch off `main`, **one issue → one branch → one squash PR**, CI is the
  merge gate, **a human merges every PR** (no self-merge). Deploys/live changes gated
  by `approved-to-apply` (AGENTS.md §4).
- **Advisory-only, HITL, no autonomous activation.** SGA proposes; a human
  (data-owner + compliance/DPO) approves each channel and ontology change. Staff
  certification data is **staff-PII (nDSG)** — pseudonymised `WID-*` work-IDs,
  Swiss-region, endpoint-only linkage; **never** treated as non-PHI, never real names
  (ADR-0016). Web-search discovery is **deferred** — run on a **curated sample feed**.

## 2. The worktree (already created)

The Sprint 32 worktree already exists off `main`:

```text
C:/Users/urruegg/source/urruegg/wt/sprint-32-signal-agent  [sprint-32/signal-agent]
```

If it ever needs recreating (off latest `main`, **after** the Sprint 31 seam merged):

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform fetch origin
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform worktree add `
  ..\wt\sprint-32-signal-agent -b sprint-32/signal-agent origin/main
```

To remove the worktree after the sprint's PR merges:

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform worktree remove ..\wt\sprint-32-signal-agent
```

## 3. Seed tool auto-approvals (per-worktree, not inherited)

A fresh worktree starts with an empty tool-approval set. Either launch with
`copilot --allow-all-tools`, or seed approvals per the
[parallel-session runbook §7](../superpowers/handoffs/parallel-session-runbook.md#7-auto-approval-permissions-are-per-worktree-not-inherited)
(run with all sessions closed; keep the `.bak-seed-*` backup).

## 4. Delegate to the Copilot CLI session

**Only after the Sprint 31 `DC-DQ-GAP-v1` seam is on `main`.** Launch a fresh Copilot
CLI agent **inside the worktree**, sync `main` (pulls the design + plan from PR #456
**and** the merged Sprint 31 seam), then paste the Section 5 prompt:

```powershell
Set-Location ..\wt\sprint-32-signal-agent
git fetch origin; git merge origin/main --no-edit    # pull design + plan + the DC-DQ-GAP-v1 seam
Test-Path data\synthetic\schema\dc-dq-gap-v1.schema.json   # expect True (Sprint 31 seam present)
copilot --allow-all-tools
```

Optionally drop a git-excluded `KICKSTART.md` in the worktree holding the Section 5
prompt so the launcher seeds the tab.

## 5. Delegation prompt template

Paste into the Copilot CLI agent launched inside the Sprint 32 worktree
(work package `<issue>` = **454**; tracker = **452**):

```text
You are implementing Sprint 32 (Signal Agent — SGA) in this dedicated worktree.
Work ONLY in this worktree; branch off main. HARD PREREQUISITE: the Sprint 31
DC-DQ-GAP-v1 seam (data/synthetic/schema/dc-dq-gap-v1.schema.json) must already be
on main — confirm it exists before starting; if missing, STOP and report BLOCKED.

Read first (do not skip):
- docs/superpowers/plans/2026-07-27-sprint-32-signal-agent.md (tasks T1-T7)
- docs/superpowers/specs/2026-07-27-sprint-31-32-signal-and-data-quality-agents-design.md
  (esp. §7 SGA, §8 the seam you consume, §9 contracts+ontology, §10 compliance,
  §11 Sprint-32 milestones)
- GitHub issue #454 (the work package) and tracker #452.
- .github/copilot-instructions.md + AGENTS.md (incl. §5 refusal + §6 adding-an-agent
  process), then docs/adr/* (ADR-0007 HITL, ADR-0016 no-PHI, ADR-0038 trunk-based,
  ADR-0006/0042 GA-gate) + docs/DATA.md + docs/COMPLIANCE.md + docs/ontology/*.
- The sibling agent to mirror in pack shape: agents/signal-triage-agent/
  {AGENT.md,manifest.yaml,golden-tasks.md}. The deterministic-module pattern:
  data-platform/decision/impact/compute_expected_impact.py. The existing skill
  contracts: data/synthetic/schema/dc-skill-event-v1 + dc-skill-evidence-v1.

Rules:
- Superpowers skills are mandatory: writing-plans -> confirm plan.md with me ->
  test-driven-development -> subagent-driven-development (one task at a time, fresh
  subagent + quality review per task) -> verification-before-completion.
- Tasks T1-T7: DC-REF-CERTIFICATION-v1 schema (staff-PII, WID-* only) + a curated
  synthetic sample feed; new agents/signal-agent/ pack (AGENT.md + manifest +
  golden-tasks, sibling to signal-triage-agent); deterministic modules in
  data-platform/signals/ (credential_resolver + skills enrichment; gap_register;
  channel_scorecard) each with tests; ontology additions (Credential/Competency/
  Qualification/IssuingAuthority) + reference<->operational crosswalk + CI
  conformance; signal-channel-lifecycle ADR + FR-SIG-* PRD rows + DATA registration
  + an AGENTS.md registry row for signal-agent.
- TDD every code task: failing test first, run it, implement, re-run green.
- Advisory-only, HITL: no channel activation or ontology change without a recorded
  data-owner + compliance/DPO approval. Staff-PII per nDSG: pseudonymised WID-*
  work-IDs ONLY, never names/AHV, never treated as non-PHI. Web-search discovery is
  OUT of scope — use the curated sample feed. NO infra apply. Consume a Sprint 31
  DC-DQ-GAP-v1 newSourceNeeded record as the intake trigger.
- Editing AGENTS.md is governance-gated: it is authorised by issue #454 + the
  CODEOWNERS review on this PR (AGENTS.md §5/§6) — add the registry row in T7.
- Gates per slice: python -m pytest data-platform/signals/tests (green) + the
  ontology crosswalk CI check. Doc edits: check_mojibake.py + markdownlint-cli2, bump
  SemVer headers, commit with the hook bypass if needed. Runtime python (not python3).
- ONE small squash PR (branch sprint-32/signal-agent) linked to #454. Never
  self-merge; wait for green required checks; a human merges.
- Assign the NEW ADR number at execution (next free; verify collisions). Replace 00NN
  and confirm every file path first.
- Report DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED at the end.

First: confirm the DC-DQ-GAP-v1 seam is on main, then read the plan + design +
issue #454, draft/refresh plan.md, and ask me to confirm before coding.
```

## 6. Integration + finish

- **Acceptance gate (sprint):** design §11 Sprint-32 DoD is green — a Signal Gap
  Register is produced from a real scan; one certification channel is onboarded
  end-to-end on the **curated sample feed** (`DC-REF-CERTIFICATION-v1` merged,
  ontology crosswalk + CI conformance green, Channel Readiness Scorecard passed, HITL
  approval recorded, skills baseline populated by pseudonymised `WID-*` on a sample);
  the intake was triggered by a Sprint 31 `DC-DQ-GAP-v1` record; the
  signal-channel-lifecycle ADR is recorded; `FR-SIG-*` PRD rows + the `signal-agent`
  `AGENTS.md` row land; provenance + audit complete; connectors GA; no PHI /
  mishandled staff-PII.
- Use `superpowers:finishing-a-development-branch` for the PR.
- After the PR merges, remove the worktree (Section 2).

## 7. Coordinator note (dependency + landing)

The Sprint 32 design + plan are in **open PR #456** (`sprint-27/curavias-ux-polish`)
and must land on `main` first (§4 `git merge origin/main`). **Additionally, this
sprint's onboarding work must not start until Sprint 31's `DC-DQ-GAP-v1` seam is
merged to `main`** — it is SGA's intake trigger and hard prerequisite. Until both
land, issue **#454** carries the full T1–T7 task list + acceptance criteria for
reading, but coding waits on the seam.
