# AGENTS.md — Agent Registry

| Field | Value |
| ------- | ------- |
| **Version** | 1.3.0 |
| **Date** | 2026-05-18 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (initial release; aligned with [ADR-0002 Runtime is GitHub Copilot coding agent](docs/adr/0002-runtime-is-github-copilot-coding-agent.md)); 1.1.0 marks `orchestrator` ready (Sprint 1 MVP shipped); 1.2.0 marks `spec-parser` ready (Sprint 2 UC1 happy-path shipped, ADR-0003 Accepted, ADR-0006 added); 1.3.0 marks `drift-analyzer` ready in **minimum-viable** scope (Sprint 5 — `AGENT.md` + 4 golden tasks; nightly scheduler, tracked-subscription registry, runbook, and WorkIQ MCP wiring deferred). Spec source for the MVP is repo-checked-in JSON, not WorkIQ. |

> **Purpose**: Top-level registry of every agent realised in this repository.
> The **GitHub Copilot coding agent** reads this file on every run to learn
> which agents exist, which MCP servers they may call, and how they refuse
> destructive actions.
>
> **Runtime**: Per [ADR-0002](docs/adr/0002-runtime-is-github-copilot-coding-agent.md),
> every agent is realised as **Markdown** under `agents/<name>/` and configured
> via [.github/copilot/mcp.json](.github/copilot/mcp.json) — no Python service,
> no Foundry-hosted agent, no platform-runtime Azure infrastructure.

---

## Table of Contents

1. [Registry](#1-registry)
2. [MCP Server Allow-List](#2-mcp-server-allow-list)
3. [Side-Effect Ceilings](#3-side-effect-ceilings)
4. [Confirmation Rule for Deploy / Delete](#4-confirmation-rule-for-deploy--delete)
5. [Refusal Rules (Shared)](#5-refusal-rules-shared)
6. [Adding a New Agent](#6-adding-a-new-agent)

---

## 1. Registry

| Agent | Use Case | Owner | Trigger | MCP Servers | Side-Effect Ceiling | Prompt | Golden Tasks |
| ------- | ---------- | ------- | --------- | ------------- | -------------------- | -------- | -------------- |
| `orchestrator` | Cross-cutting | @urruegg | `@copilot` mention on any issue, or issue from [`smoke-echo.yml`](.github/ISSUE_TEMPLATE/smoke-echo.yml) | `github-mcp` | `write` | [`agents/orchestrator/AGENT.md`](agents/orchestrator/AGENT.md) | [`agents/orchestrator/golden-tasks.md`](agents/orchestrator/golden-tasks.md) |
| `spec-parser` | UC1 — Build Subscription | @urruegg | Issue from [`uc1-build-subscription.yml`](.github/ISSUE_TEMPLATE/uc1-build-subscription.yml) | `github-mcp`, `workiq-mcp`, `azure-mcp`, `azure-devops-mcp` | `deploy` (UC1 outputs only, behind `approved-to-apply`) | [`agents/spec-parser/AGENT.md`](agents/spec-parser/AGENT.md) | [`agents/spec-parser/golden-tasks.md`](agents/spec-parser/golden-tasks.md) |
| `pr-review` | UC3 — PR Review | @urruegg | ADO Service Hook → `repository_dispatch` → issue from [`uc3-pr-review.yml`](.github/ISSUE_TEMPLATE/uc3-pr-review.yml) | `github-mcp`, `azure-devops-mcp` | `write` (ADO comments only) | `agents/pr-review/AGENT.md` *(planned, S4)* | `agents/pr-review/golden-tasks.md` *(planned, S4)* |
| `drift-analyzer` | UC2 — Drift Detection | @urruegg | Issue from [`uc2-drift-scan.yml`](.github/ISSUE_TEMPLATE/uc2-drift-scan.yml) (on-demand; nightly scheduler `uc2-nightly.yml` deferred) | `github-mcp`, `azure-mcp` (read-only), `azure-devops-mcp` (Wiki only) | `write` (ADO Wiki + GH issue only; `azure-mcp` ceiling downgraded to `read` per [`agents/drift-analyzer/AGENT.md` §2](agents/drift-analyzer/AGENT.md#2-scope); remediation routed through human-filed UC1 issues) | [`agents/drift-analyzer/AGENT.md`](agents/drift-analyzer/AGENT.md) | [`agents/drift-analyzer/golden-tasks.md`](agents/drift-analyzer/golden-tasks.md) |

> **Status legend**: agents marked *(planned, S`<n>`)* are scaffolded in this
> registry now and authored in the indicated sprint per
> [SPRINT_PLAN.md](sprints/SPRINT_PLAN.md). No agent prompt file is required
> to exist on disk before its sprint.

---

## 2. MCP Server Allow-List

The authoritative allow-list is [.github/copilot/mcp.json](.github/copilot/mcp.json).
Any new MCP server requires a CODEOWNERS-approved PR documenting purpose +
required permissions + at least one golden-task that exercises a representative
tool.

| MCP Server | Identifier | Purpose | Auth Mode |
| ------------ | ----------- | --------- | ----------- |
| Azure | `azure-mcp` | Read Azure resources, run `what-if`, push UC1-output Bicep deployments to customer subscriptions | Workload Identity Federation (OIDC) for autonomous runs; OBO for human-triggered |
| Azure DevOps | `azure-devops-mcp` | Read PRs, create branches/commits/PRs, post review comments, upsert Wiki pages | OAuth (OBO) for human-triggered; service-principal OIDC for autonomous |
| GitHub | `github-mcp` | Read/write this repo (issues, PRs, comments, branches) | GitHub Copilot coding-agent identity |
| WorkIQ | `workiq-mcp` | Read landing-zone specs (UC1 input) | Workload Identity Federation (OIDC) |

---

## 3. Side-Effect Ceilings

Every agent declares a ceiling in column 6 of [§1](#1-registry). The
Copilot coding agent must refuse to call any MCP tool whose effective side
effect exceeds the agent's ceiling.

| Ceiling | Permits | Forbids |
| --------- | --------- | --------- |
| `read` | Pure reads (list, get, query) | Any state mutation |
| `write` | Creating/updating issues, PRs, comments, Wiki pages, branches | Provisioning or deleting cloud resources |
| `deploy` | Creating/updating Azure resources via UC1-output Bicep + `what-if` + apply | Deletes |
| `delete` | All of the above + delete operations | — (requires `approved-to-apply` per [§4](#4-confirmation-rule-for-deploy--delete)) |

---

## 4. Confirmation Rule for Deploy / Delete

Tools whose side-effect ceiling is `deploy` or `delete` must:

1. **Plan first** — the agent produces a dry-run / `what-if` result in a PR
   description or issue comment.
2. **Wait for a human** to reply on the same PR or issue thread with a
   comment containing the exact magic phrase: `approved-to-apply`.
3. **Only then** fire the corresponding MCP tool call. The agent must echo
   the approver's GitHub handle and the timestamp in the resulting commit
   message or follow-up comment.

The agent must **refuse** to apply if:

- the approver is the agent itself or a bot identity,
- the approver does not have write access to the repo (verified via
  `github-mcp`),
- or the `what-if` output materially differs from the plan that was approved
  (re-plan and re-request approval).

---

## 5. Refusal Rules (Shared)

All agents refuse to:

- Operate outside the repositories / subscriptions / tenants listed in their
  per-agent `AGENT.md` scope section.
- Echo, log, or commit anything that pattern-matches a secret (PAT, client
  secret, connection string, JWT).
- Execute deploy / delete tools without the `approved-to-apply` comment per
  [§4](#4-confirmation-rule-for-deploy--delete).
- Modify `.github/copilot/mcp.json`, `.github/CODEOWNERS`,
  `.github/copilot-instructions.md`, `AGENTS.md`, or any `docs/adr/*.md`
  without a human-authored issue requesting the change and a CODEOWNERS
  reviewer assigned.
- Trust values returned by an MCP tool or LLM output without re-validating
  them at the next tool boundary.

---

## 6. Adding a New Agent

1. Open an issue describing the agent's use case, trigger, required MCP
   servers, and side-effect ceiling. Link the relevant `FR-*` / `NFR-*`
   IDs from [docs/PRD.md](docs/PRD.md).
2. The Copilot coding agent opens a branch and a draft PR containing:
   - `agents/<name>/AGENT.md` (Identity, Scope, Tools, Refusal Rules,
     Output Contract, Confirmation Rules).
   - `agents/<name>/golden-tasks.md` with ≥ 1 happy-path and ≥ 1
     failure-mode fixture.
   - A new row in [§1](#1-registry).
   - Updates to [.github/copilot/mcp.json](.github/copilot/mcp.json) if a
     new MCP server is required (CODEOWNERS review mandatory).
3. A human reviewer verifies the side-effect ceiling, refusal rules, and
   golden-task coverage before merging.
