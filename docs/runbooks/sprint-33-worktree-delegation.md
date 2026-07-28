# Sprint 33 — Worktree Delegation Runbook (single dedicated session)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |

> **Purpose:** package **Sprint 33** (Curavias BVA Agent — ROI/TCO reasoning +
> opportunity capture) so it can be built by a **single fresh Copilot CLI agent
> in its own isolated git worktree**. Grounded in the
> [Sprint 33 design](../superpowers/specs/2026-07-28-sprint-33-curavias-bva-agent-design.md),
> [Plan 1 (WS-G0 contracts)](../superpowers/plans/2026-07-28-sprint-33-curavias-bva-agent.md),
> and the [BVA Agent proposal](../superpowers/ideas/Curavias-BVA-Agent-Proposal.md).
> Builds on the `superpowers:using-git-worktrees` and
> `superpowers:subagent-driven-development` skills. Complements the durable
> [parallel-session runbook](../superpowers/handoffs/parallel-session-runbook.md).

---

## 1. Model

- **One worktree = one session = the whole sprint.** Sprint 33 delivers the
  Curavias BVA Agent across five workstreams — **WS-G0** (frozen contracts),
  **WS-A** (cost/BOM data product via the master-data pattern), **WS-B** (BVA
  reasoning + deterministic `bva.simulate` engine), **WS-C** (App-copilot
  orchestration + PO linkage), **WS-D** (opportunity capture). It touches
  `data/master-data/`, Fabric notebooks + semantic model, `agents/bva-agent/`,
  `apps/hcc-agent-host`, and `apps/hcc-app-fluent`, so it runs in **one**
  dedicated worktree. The in-session `subagent-driven-development` pattern keeps
  each task isolated and test-first.
- **Workstream chain (design §11):** **WS-G0 first** (everything builds against
  the frozen contracts), then **WS-A / WS-B / WS-D in parallel**, then **WS-C**
  integrates. **Plan 1 (WS-G0)** is the executable foundation and runs **first**;
  WS-A/B/D/C land as **follow-on plans** the session proposes after Plan 1 merges.
- **Trunk-based per [ADR-0038](../adr/0038-trunk-based-parallel-sprint-workflow.md):**
  short-lived branches off `main`, **one issue -> one branch -> one squash PR**, CI
  is the merge gate, **a human merges every PR** (no self-merge). Deploys / live
  Fabric data loads gated by `approved-to-apply` (AGENTS.md §4).
- **No infra apply / no autonomous action this sprint.** The agent is
  advisory-only and read-only against cloud (side-effect ceiling `write`, repo
  only; `fabric-mcp` at read). No LLM arithmetic — the ROI/TCO math is a
  deterministic tool. Synthetic / no-PHI only (ADR-0016); demo region (ADR-0013).

## 2. The worktree

Create the Sprint 33 worktree off the latest `main`:

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform fetch origin
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform worktree add `
  ..\wt\sprint-33-bva-agent -b sprint-33/ws-g0-contracts origin/main
```

The session rebranches per work package off the latest `main` as earlier PRs merge
(`git fetch origin; git switch -c sprint-33/ws-a-data-product origin/main`).

To remove the worktree after the sprint's PRs merge:

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform worktree remove ..\wt\sprint-33-bva-agent
```

## 3. Seed tool auto-approvals (per-worktree, not inherited)

A fresh worktree starts with an empty tool-approval set. Either launch with
`copilot --allow-all-tools`, or seed approvals per the
[parallel-session runbook §7](../superpowers/handoffs/parallel-session-runbook.md#7-auto-approval-permissions-are-per-worktree-not-inherited)
(run with all sessions closed; keep the `.bak-seed-*` backup).

## 4. Delegate to the Copilot CLI session

Launch a fresh Copilot CLI agent **inside the worktree** and paste the Section 5
prompt. The session reads the design + Plan 1 + the WS-G0 issue, drafts/refreshes
`plan.md`, stops at a plan-confirmation gate, then implements task-by-task with TDD.

```powershell
Set-Location ..\wt\sprint-33-bva-agent
copilot --allow-all-tools
```

Optionally create a git-excluded `KICKSTART.md` in the worktree (auto-excluded via
`.git/info/exclude`) holding the Section 5 prompt, so the launcher seeds the tab.

## 5. Delegation prompt template

Paste into the Copilot CLI agent launched inside the Sprint 33 worktree
(first work package = **WS-G0 contracts issue #490**; tracker = **#489**):

```text
You are implementing Sprint 33 (Curavias BVA Agent) in this dedicated worktree.
Work ONLY in this worktree; branch off main per work package.

Read first (do not skip):
- docs/superpowers/plans/2026-07-28-sprint-33-curavias-bva-agent.md
  (Plan 1 - WS-G0 frozen contracts, Tasks 1-4)
- docs/superpowers/specs/2026-07-28-sprint-33-curavias-bva-agent-design.md
  (esp. §3 decisions, §4 workstreams, §6 bva.simulate, §7 PO linkage, §8 opportunity)
- docs/superpowers/ideas/Curavias-BVA-Agent-Proposal.md (context + seed evidence)
- GitHub issue #490 (WS-G0 work package) and the tracker #489.
- .github/copilot-instructions.md + AGENTS.md, then the relevant docs/adr/*
  (ADR-0013 demo region, ADR-0016 no-PHI, ADR-0025 BVA KPIs, ADR-0032 Foundry,
  ADR-0038 trunk-based, ADR-0043 PO Agent) and docs/BVA.md + docs/agent_cost.md +
  docs/agent-cost-bom.md + docs/DATA.md + docs/AI.md + docs/COMPLIANCE.md.
- The PO contract precedent to mirror: docs/superpowers/specs/2026-07-25-sprint-28-
  po-agent-contracts.md + data/synthetic/schema/grounded-chunk-v1.schema.json +
  evals/product-owner-agent/ (schema/fixtures/tests layout to copy).
- The master-data pattern to reuse (WS-A, later plan): docs/superpowers/specs/
  2026-07-19-curavias-shared-master-data-and-ontology-design.md.

Rules:
- Superpowers skills are mandatory: writing-plans -> confirm plan.md with me ->
  test-driven-development -> subagent-driven-development (one task at a time,
  fresh subagent + quality review per task) -> verification-before-completion.
- Start with Plan 1 / WS-G0 (Tasks 1-4): bva-simulation-result-v1 + bva-opportunity-v1
  JSON Schemas, one fixture each, pytest conformance tests, and the frozen contracts
  doc docs/superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md. Freeze the
  CHF cost-basis normalization contract. All figures CHF; no LLM arithmetic; every
  figure a GroundedChunk (Class C) with a non-empty citation.sourceRef.
- TDD every task: write the failing test first, run it, implement, re-run green.
  Gate: python -m pytest evals/bva-agent -v. Runtime python (not python3).
- Doc edits: python scripts/lint/check_mojibake.py <files> + npx markdownlint-cli2,
  bump SemVer headers, commit with the hook bypass (git -c core.hooksPath=/dev/null).
- Stay strictly in the WS-G0 scope for Plan 1 (schemas + fixtures + tests + contracts
  doc). WS-A (data product), WS-B (engine + agent pack), WS-D (opportunity store),
  WS-C (orchestration) are SEPARATE follow-on plans you propose after Plan 1 lands.
  NO infra apply; the agent is advisory-only, read-only against cloud. Synthetic /
  no-PHI only.
- One SMALL squash PR per work package (branch sprint-33/<slice>), linked to its
  issue (Plan 1 -> WS-G0 issue). Never self-merge; wait for green required checks;
  a human merges. Rebranch off the latest main per work package.
- Assign the NEW BVA ADR number at execution (next free; verify collisions via
  git ls-tree; coordinate with the #378 ADR-collision cleanup). Replace 00NN and
  confirm every file path first.
- Report DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED at each work-package end.

First: read Plan 1 + the design + the WS-G0 issue, draft/refresh plan.md for Plan 1,
and ask me to confirm before coding.
```

## 6. Integration + finish

- Merge **Plan 1 (WS-G0 contracts)** first — it freezes the shapes every other
  workstream builds against. Then land the follow-on plans in dependency order:
  WS-A (data product) / WS-B (engine + agent) / WS-D (opportunity) in parallel,
  then WS-C (orchestration + PO linkage), each as its own human-reviewed squash PR.
  Rebranch off the latest `main` per work package.
- **Acceptance gate (sprint):** the design §9 requirements (`FR-BVA-001..005`,
  `NFR-BVA-001..005`) are green: grounded CHF ROI/TCO answers over `bva_*` gold;
  interactive new-hospital what-if via the deterministic `bva.simulate` tool;
  PO <-> BVA fan-out composing one cited answer; opportunity capture (Cosmos SoR +
  `bva_opportunity` gold projection + Backstage pipeline); Start/Backstage
  surfacing; the new BVA ADR recorded; `AGENTS.md` row + PRD §7 requirements added.
- Use `superpowers:finishing-a-development-branch` per PR.
- After all slices merge, remove the worktree (Section 2).

## 7. Coordinator note (doc landing)

The Sprint 33 **design spec**, **Plan 1**, and this **runbook** land together in the
delegation PR (tracker issue). They live on `main` so the worktree — created off
`main` — can read them. The three seed evidence docs
([`docs/agent_cost.md`](../agent_cost.md),
[`docs/agent-cost-bom.md`](../agent-cost-bom.md),
[`docs/superpowers/ideas/Curavias-BVA-Agent-Proposal.md`](../superpowers/ideas/Curavias-BVA-Agent-Proposal.md))
are WS-A's first curated inputs and should be on `main` before WS-A starts. Until
the WS-G0 PR merges, the WS-G0 issue carries the full Task 1-4 list + acceptance
criteria, so the session can start from the design + Plan 1 without waiting.
