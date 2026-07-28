# Sprint 34 — Worktree Delegation Runbook (single dedicated session)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |

> **Purpose:** package **Sprint 34** (Curavias Documentation Alignment — Curavias
> anchor + IQ / Frontier-Firm terminology + canonical mermaid + customer-ready
> presentation) so it can be built by a **single fresh Copilot CLI agent in its
> own isolated git worktree**. Grounded in the
> [Sprint 34 design](../superpowers/specs/2026-07-28-sprint-34-doc-alignment-design.md)
> and [Plan 1 (WS-0 foundations)](../superpowers/plans/2026-07-28-sprint-34-doc-alignment.md).
> Builds on the `superpowers:using-git-worktrees`,
> `superpowers:subagent-driven-development`, and `document-authoring` skills.
> Complements the durable
> [parallel-session runbook](../superpowers/handoffs/parallel-session-runbook.md).

---

## 1. Model

- **One worktree = one session = the whole sprint.** Sprint 34 aligns the 16 main
  Curavias docs across five workstreams — **WS-0** (foundations: glossary + doc
  template + canonical mermaid library), **WS-1** (Governance: SECURITY,
  COMPLIANCE, AI), **WS-2** (Architecture/Data/Infra: ARCHITECTURE, INFRASTRUCTURE,
  DATA, ALM_PLAN), **WS-3** (Product/Experience: README hero, CURAVIAS-PRODUCT-STATUS,
  PRD, BVA, SD), **WS-4** (Ops/Dev: OPERATIONS, TEST, DEV_WORKFLOW, AGENTS). It
  touches only `docs/**`, `README.md`, and `AGENTS.md`, so it runs in **one**
  dedicated worktree. The in-session `subagent-driven-development` pattern keeps
  each doc/workstream isolated and reviewable.
- **Workstream chain (design §12):** **WS-0 first** (freezes the glossary +
  template + diagram library everything else copies), then **WS-3** (customer
  hero surface first), then **WS-2 / WS-1 / WS-4**. **Plan 1 (WS-0)** is the
  executable foundation and runs **first**; WS-1..4 land as **follow-on plans**
  the session proposes after Plan 1 merges.
- **Trunk-based per [ADR-0038](../adr/0038-trunk-based-parallel-sprint-workflow.md):**
  short-lived branches off `main`, **one issue -> one branch -> one squash PR**, CI
  is the merge gate, **a human merges every PR** (no self-merge).
- **Documentation-only.** No code, no infra, no ADR reversal. Advisory-only /
  synthetic / no-PHI product doctrine is unchanged and authoritative. Every doc
  edit passes mojibake + markdownlint + link-check and §9 SemVer bumps.

## 2. The worktree

Create the Sprint 34 worktree off the latest `main`:

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform fetch origin
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform worktree add `
  ..\wt\sprint-34-doc-alignment -b sprint-34/ws-0-foundations origin/main
```

The session rebranches per work package off the latest `main` as earlier PRs merge
(`git fetch origin; git switch -c sprint-34/ws-3-product-experience origin/main`).

To remove the worktree after the sprint's PRs merge:

```powershell
git -C C:\Users\urruegg\source\urruegg\SwissHospitalCapacityPlatform worktree remove ..\wt\sprint-34-doc-alignment
```

## 3. Seed tool auto-approvals (per-worktree, not inherited)

A fresh worktree starts with an empty tool-approval set. Either launch with
`copilot --allow-all-tools`, or seed approvals per the
[parallel-session runbook §7](../superpowers/handoffs/parallel-session-runbook.md#7-auto-approval-permissions-are-per-worktree-not-inherited)
(run with all sessions closed; keep the `.bak-seed-*` backup).

## 4. Delegate to the Copilot CLI session

Launch a fresh Copilot CLI agent **inside the worktree** and paste the Section 5
prompt. The session reads the design + Plan 1 + the WS-0 issue, drafts/refreshes
`plan.md`, stops at a plan-confirmation gate, then implements task-by-task.

```powershell
Set-Location ..\wt\sprint-34-doc-alignment
copilot --allow-all-tools
```

Optionally create a git-excluded `KICKSTART.md` in the worktree (auto-excluded via
`.git/info/exclude`) holding the Section 5 prompt, so the launcher seeds the tab.

## 5. Delegation prompt template

Paste into the Copilot CLI agent launched inside the Sprint 34 worktree
(first work package = **WS-0 foundations issue #506**; tracker = **#505**):

```text
You are implementing Sprint 34 (Curavias Documentation Alignment) in this
dedicated worktree. Work ONLY in this worktree; branch off main per work package.

Read first (do not skip):
- docs/superpowers/plans/2026-07-28-sprint-34-doc-alignment.md
  (Plan 1 - WS-0 foundations, Tasks 1-4)
- docs/superpowers/specs/2026-07-28-sprint-34-doc-alignment-design.md
  (esp. §3 decisions, §6 terminology, §7 template, §8 diagram library, §9 workstreams)
- GitHub issue #506 (WS-0 work package) and the tracker #505.
- .github/copilot-instructions.md (esp. §9 Document Versioning) + AGENTS.md.
- Precedent to mirror: docs/CURAVIAS-PRODUCT-STATUS.md (Curavias anchor + product
  doctrine) and docs/ARCHITECTURE.md (target-vs-as-deployed note).
- The document-authoring skill (.github/skills/document-authoring/SKILL.md) for the
  judgment layer (version bump level, traceability, status accuracy).

Rules:
- Superpowers skills are mandatory: writing-plans -> confirm plan.md with me ->
  subagent-driven-development (one doc/task at a time, fresh subagent + quality
  review per task) -> verification-before-completion. document-authoring governs
  every Markdown create/update.
- Start with Plan 1 / WS-0 (Tasks 1-4): docs/GLOSSARY.md, docs/architecture/
  diagram-library.md (5 canonical mermaid diagrams), and the customer-ready doc
  template block. Do NOT touch the 16 in-scope docs yet - that is WS-1..4.
- Terminology: Curavias is the anchor product name; use Microsoft IQ terms
  (Fabric IQ / Foundry IQ / Work IQ / Copilot IQ) and Frontier FIRM operating-model
  framing (human + AI-agent teams, agent boss, human-agent ratio) - NOT "frontier
  models". Do not change any technical decision, ADR, or the advisory-only /
  synthetic / no-PHI doctrine.
- Encoding: author with the create/edit tools or UTF-8 no-BOM writes. NEVER use
  PowerShell Set-Content/Get-Content on non-ASCII content (it double-encodes em
  dashes / §). Keep any piped Python ASCII-only.
- Gates on every doc: python scripts/lint/check_mojibake.py <files> + npx --yes
  markdownlint-cli2 "<files>" + npx --yes markdown-link-check <files>. Bump SemVer
  headers (§9) and Previous Version. Runtime python (not python3).
- One SMALL squash PR per work package (branch sprint-34/<slice>), linked to its
  issue (Plan 1 -> WS-0 issue). Never self-merge; wait for green required checks;
  a human merges. Rebranch off the latest main per work package.
- WS-1..4 (per-doc application by lane) are SEPARATE follow-on plans you propose
  after WS-0 lands. WS-3 (README hero + product/experience docs) goes first among
  them and also adds NFR-DOC-001..004 to PRD §7.
- Report DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED at each work-package end.

First: read Plan 1 + the design + the WS-0 issue, draft/refresh plan.md for Plan 1,
and ask me to confirm before authoring.
```

## 6. Integration + finish

- Merge **Plan 1 (WS-0 foundations)** first — it freezes the glossary + template +
  diagram library every other workstream copies. Then land the follow-on plans in
  order: **WS-3** (customer surface) first, then **WS-2**, **WS-1**, **WS-4**, each
  as its own human-reviewed squash PR off the latest `main`.
- **Acceptance gate (sprint):** the design §10 DoD is green for all 16 in-scope
  docs — Curavias-anchored title + product-anchor line + exec summary; glossary
  terminology used consistently; canonical diagram(s) embedded per §8; plain
  customer-ready wording; mojibake + markdownlint + link-check clean; §9 version
  bumps. `NFR-DOC-001..004` added to PRD §7 in WS-3. No technical decision or ADR
  changed.
- Use `superpowers:finishing-a-development-branch` per PR.
- After all slices merge, remove the worktree (Section 2).

## 7. Coordinator note (doc landing)

The Sprint 34 **design spec**, **Plan 1**, and this **runbook** land together in
the delegation PR (tracker issue). They live on `main` so the worktree — created
off `main` — can read them. WS-0 creates two new foundation docs
(`docs/GLOSSARY.md`, `docs/architecture/diagram-library.md`) that WS-1..4 depend
on, so WS-0 must merge before the per-doc workstreams start. Until the WS-0 PR
merges, the WS-0 issue carries the full Task 1-4 list + DoD, so the session can
start from the design + Plan 1 without waiting.
