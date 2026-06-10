# AGENTS.md — Agent Registry

| Field | Value |
| ------- | ------- |
| **Version** | 1.8.0 |
| **Date** | 2026-06-10 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | 1.7.0 (Superpowers-first execution alignment; legacy agents retained for compatibility) |

> **Purpose**: Top-level registry of every agent realised in this repository.
> The **GitHub Copilot coding agent** reads this file on every run to learn
> which agents exist, which MCP servers they may call, and how they refuse
> destructive actions.
>
> **Execution default (migration status)**: Superpowers-first execution is now
> the default operating model for new work. The per-agent registry below is
> retained as a compatibility layer during migration and remains authoritative
> for side-effect ceilings, refusal rules, and approval gates.
>
> **Runtime**: Per [ADR-0002](docs/adr/0002-runtime-is-github-copilot-coding-agent.md),
> legacy agent packs are archived as **Markdown** under `agents-archive/<name>/`
> with compatibility stubs retained under `agents/<name>/`, and configured
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
| `orchestrator` | Cross-cutting dispatcher | @urruegg | `@copilot` mention on any issue, or issue from [`smoke-echo.yml`](.github/ISSUE_TEMPLATE/smoke-echo.yml) | `github-mcp` | `write` | [`agents-archive/orchestrator/AGENT.md`](agents-archive/orchestrator/AGENT.md) | [`agents-archive/orchestrator/golden-tasks.md`](agents-archive/orchestrator/golden-tasks.md) |
| `spec-parser-agent` | Spec discovery and PRD drafting from `docs/specs/` | @urruegg | Issue requesting requirement extraction or PRD creation from source specs | `github-mcp` | `write` | [`agents-archive/spec-parser-agent/AGENT.md`](agents-archive/spec-parser-agent/AGENT.md) | [`agents-archive/spec-parser-agent/golden-tasks.md`](agents-archive/spec-parser-agent/golden-tasks.md) |
| `solution-design-agent` | PRD to solution architecture and MVP slicing | @urruegg | Issue requesting architecture, design, or scope decomposition from [docs/PRD.md](docs/PRD.md) | `github-mcp` | `write` | [`agents-archive/solution-design-agent/AGENT.md`](agents-archive/solution-design-agent/AGENT.md) | [`agents-archive/solution-design-agent/golden-tasks.md`](agents-archive/solution-design-agent/golden-tasks.md) |
| `landing-zone-agent` | PRD + architecture to Azure landing zone and IaC | @urruegg | Issue requesting Azure landing zone, Bicep, or deployment-plan generation | `github-mcp`, `azure-mcp` | `deploy` (plan-first, gated by `approved-to-apply`) | [`agents-archive/landing-zone-agent/AGENT.md`](agents-archive/landing-zone-agent/AGENT.md) | [`agents-archive/landing-zone-agent/golden-tasks.md`](agents-archive/landing-zone-agent/golden-tasks.md) |
| `compliance-agent` | Compliance coverage and control traceability | @urruegg | Issue requesting compliance mapping, evidence tracking, or policy gaps | `github-mcp` | `write` | [`agents-archive/compliance-agent/AGENT.md`](agents-archive/compliance-agent/AGENT.md) | [`agents-archive/compliance-agent/golden-tasks.md`](agents-archive/compliance-agent/golden-tasks.md) |
| `data-design-agent` | Data model, contracts, and platform design | @urruegg | Issue requesting data model, data platform, or interoperability design | `github-mcp` | `write` | [`agents-archive/data-design-agent/AGENT.md`](agents-archive/data-design-agent/AGENT.md) | [`agents-archive/data-design-agent/golden-tasks.md`](agents-archive/data-design-agent/golden-tasks.md) |
| `app-builder-agent` | App and integration implementation slices | @urruegg | Issue requesting app or integration implementation from approved architecture | `github-mcp` | `write` | [`agents-archive/app-builder-agent/AGENT.md`](agents-archive/app-builder-agent/AGENT.md) | [`agents-archive/app-builder-agent/golden-tasks.md`](agents-archive/app-builder-agent/golden-tasks.md) |
| `test-verifier-agent` | Artefact validation across docs, IaC, app, and integration outputs | @urruegg | Issue requesting test plan, validation, or release readiness review | `github-mcp` | `write` | [`agents-archive/test-verifier-agent/AGENT.md`](agents-archive/test-verifier-agent/AGENT.md) | [`agents-archive/test-verifier-agent/golden-tasks.md`](agents-archive/test-verifier-agent/golden-tasks.md) |
| `review-session-agent` | Review transcript evaluation and outcome reporting against repository artefacts | @urruegg | Issue requesting review-session transcript intake (for example Work IQ Teams Transcript) and evaluation report generation | `github-mcp`, `work-iq-mcp` (read-only) | `write` | [`agents-archive/review-session-agent/AGENT.md`](agents-archive/review-session-agent/AGENT.md) | [`agents-archive/review-session-agent/golden-tasks.md`](agents-archive/review-session-agent/golden-tasks.md) |
| `pr-review` | UC3 — PR Review | @urruegg | GitHub pull request or issue from [`uc3-pr-review.yml`](.github/ISSUE_TEMPLATE/uc3-pr-review.yml) | `github-mcp` | `write` (GitHub review comments only) | `agents/pr-review/AGENT.md` *(planned, S4)* | `agents/pr-review/golden-tasks.md` *(planned, S4)* |
| `drift-analyzer` | Solution and Azure drift detection | @urruegg | Issue from [`uc2-drift-scan.yml`](.github/ISSUE_TEMPLATE/uc2-drift-scan.yml) (on-demand; nightly scheduler `uc2-nightly.yml` deferred) | `github-mcp`, `azure-mcp` (read-only) | `write` (GitHub issue + branch artefacts only; `azure-mcp` ceiling downgraded to `read` per [`agents-archive/drift-analyzer/AGENT.md` §2](agents-archive/drift-analyzer/AGENT.md#2-scope); remediation routed through human-filed UC1 issues) | [`agents-archive/drift-analyzer/AGENT.md`](agents-archive/drift-analyzer/AGENT.md) | [`agents-archive/drift-analyzer/golden-tasks.md`](agents-archive/drift-analyzer/golden-tasks.md) |

> **Status legend**: agents marked *(planned, S`<n>`)* are scaffolded in this
> registry now and authored in the indicated sprint per
> [SPRINT_PLAN.md](docs/sprints/SPRINT_PLAN.md). No agent prompt file is required
> to exist on disk before its sprint.
>
> **Migration note**: For new issue intake, use Superpowers execution mode in
> issue templates. Agent-specific routing labels remain for legacy compatibility
> and controlled rollback only.

---

## 2. MCP Server Allow-List

The authoritative allow-list is [.github/copilot/mcp.json](.github/copilot/mcp.json).
Any new MCP server requires a CODEOWNERS-approved PR documenting purpose +
required permissions + at least one golden-task that exercises a representative
tool.

| MCP Server | Identifier | Purpose | Auth Mode |
| ------------ | ----------- | --------- | ----------- |
| Azure | `azure-mcp` | Read Azure resources, run `what-if`, push UC1-output Bicep deployments to customer subscriptions | Workload Identity Federation (OIDC) for autonomous runs; OBO for human-triggered |
| GitHub | `github-mcp` | Read/write this repo (issues, PRs, comments, branches) | GitHub Copilot coding-agent identity |
| Work IQ | `work-iq-mcp` | Read Microsoft 365 meeting context and transcript content for review-session intake | Least-privilege transcript and meeting read scopes |
| Repo-managed markdown specs | `github-mcp` | Read canonical source material from `docs/` and `docs/specs/` for planning and review flows | GitHub Copilot coding-agent identity |

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
