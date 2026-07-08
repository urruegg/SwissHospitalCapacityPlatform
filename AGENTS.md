# AGENTS.md — Agent Registry

| Field | Value |
| ------- | ------- |
| **Version** | 1.14.0 |
| **Date** | 2026-07-08 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | 1.13.0 (added §Skill discovery rule of engagement — trigger conditions, discovery order, evaluation checklist, PR shape, decision gate) |

> **Purpose**: Top-level registry of every agent realised in this repository.
> The **GitHub Copilot coding agent** reads this file on every run to learn
> which agents exist, which MCP servers they may call, and how they refuse
> destructive actions.
>
> **Tenant migration authoritative (Sprint 00 completed 2026-07-02):** the platform now runs in Entra tenant `1337187a-4c41-4da9-8fca-731bba7a4329` (`MngEnvMCAP164444.onmicrosoft.com`) with solution short name `ihzhhpf` and subscription `66a9953a-df37-4c51-856c-9971b9bf3e03`. **Demo/proof-of-technology scope only:** deployed in `westus2` per [ADR-0013](docs/adr/0013-temporary-us-region-demo-scope.md), synthetic sample data only, no PHI — sunset back to `switzerlandnorth` when target services reach Swiss GA. Old tenant `MngEnvMCAP228255` is frozen; teardown deferred. See [ADR-0012](docs/adr/0012-tenant-migration-to-mcap164444.md).
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

## Superpowers Skill Enforcement

This repository enforces mandatory skill execution semantics for Superpowers.

Before any task:

1. Determine if a Superpowers skill applies.
2. If a skill applies, read its `SKILL.md` before proceeding.

If a skill applies:

1. Use of that skill is mandatory.
2. Required steps in that skill must not be skipped.
3. If multiple skills apply, run them in a documented, justified sequence.

Core skills that must always be considered for applicable work:

1. `test-driven-development`
2. `systematic-debugging`
3. `writing-plans`
4. `verification-before-completion`

Compliance requirement:

1. Work that skips applicable mandatory skills is non-compliant and must be corrected before PR completion.

## Workspace-scoped skills (v1.13.0, 2026-07-08)

Seven domain skills installed under [`.github/skills/`](.github/skills/) to speed up M1..M4 execution per the [Sprint 10 completion strategy](docs/superpowers/specs/2026-07-08-sprint-10-completion-strategy.md). All are workspace-scoped (travel with the repo, git-tracked).

| Skill | Source | Trigger examples | When to use |
| ----- | ------ | ---------------- | ----------- |
| [`eventstream-authoring`](.github/skills/eventstream-authoring/SKILL.md) | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) fabric-authoring | "create eventstream", "add source to eventstream", "eventstream destination", "wire eventstream" | Any Eventstream topology work — sources, operators, destinations, `updateDefinition` REST |
| [`spark-authoring`](.github/skills/spark-authoring/SKILL.md) | microsoft/skills-for-fabric fabric-authoring | "run notebook", "spark session", "notebook job", "lakehouse Delta table" | Fabric notebook orchestration + Spark patterns — M1-B (bronze/silver/gold runs) |
| [`fabric-semantic-model-authoring`](.github/skills/fabric-semantic-model-authoring/SKILL.md) | microsoft/skills-for-fabric fabric-authoring | "semantic model", "measure", "relationship", "TMDL", "Direct Lake" | Semantic model authoring via Fabric REST — M1-C measures + relationship contract |
| [`powerbi-report-authoring`](.github/skills/powerbi-report-authoring/SKILL.md) | microsoft/skills-for-fabric powerbi-authoring | "PBIP", "visual container", "page layout", "KPI card", "Power BI report" | Report / visual authoring — M1-D KPI tiles + M2 remaining visuals |
| [`powerbi-optimization`](.github/skills/powerbi-optimization/SKILL.md) + [specialists/](.github/skills/powerbi-optimization/specialists/) | [PBI-Guy/Power-BI-Optimization-Skill](https://github.com/PBI-Guy/Power-BI-Optimization-Skill) | "optimize DAX", "slow measure", "RLS performance", "storage mode", "BPA" | DAX + model + RLS optimization — M2-M3 measure tuning + M3 RLS re-authoring |
| [`e2e-medallion-architecture`](.github/skills/e2e-medallion-architecture/SKILL.md) *(v1.13.0)* | microsoft/skills-for-fabric fabric-authoring | "medallion architecture", "bronze silver gold", "multi-layer lakehouse", "PHI gate", "data quality enforcement" | Bronze/silver/gold design + PHI/FK/schema gate patterns — M1.5 silver-hardening + M2 gold refinement |
| [`spark-operations`](.github/skills/spark-operations/SKILL.md) *(v1.13.0)* | microsoft/skills-for-fabric fabric-operations | "Spark session", "notebook logs", "Spark statement failure", "Spark diagnostics", `System_Cancelled_Session_Statements_Failed` | Diagnose Fabric Spark session errors + notebook runtime failures — M1.5 silver debugging + future notebook failure triage |

The `powerbi-optimization` skill ships with 5 specialists (`dax-mastery`, `model-design`, `report-performance`, `powerquery-m`, `security-rls`) plus BPA and MCP integration guides under `.github/skills/powerbi-optimization/`. The MCP integration is optional and requires a separate Power BI Modeling MCP server install; skip it unless we need automated DAX benchmarking.

Additional skills evaluated and **NOT installed** (available in the source repos if needed later):

- `microsoft/skills-for-fabric` `fabric-consumption` — read-only query workflows (we already have those covered)
- `microsoft/skills-for-fabric` `fabric-operations/mlv-operations-cli` — Materialized Lake View ops; candidate for M2 if gold uses MLVs
- `microsoft/skills-for-fabric` `fabric-operations/sqldw-operations-cli` — not our path (we use lakehouse per ADR-0015)
- `microsoft/skills-for-fabric` `fabric-authoring/{activator,dataflows,eventhouse,fabriciq-ontology,sqldw}-authoring-cli` — not part of the M1..M4 critical path
- `microsoft/skills-for-fabric` `powerbi-authoring/{powerbi-report-design,powerbi-report-management,powerbi-report-planning,check-updates}` — mostly workflow orchestration, not needed for direct M1..M4 deliverables

Skill refresh procedure — run once per sprint or on-demand:

```powershell
$tmp = "$env:TEMP\skills-install-refresh"
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
git clone --depth 1 https://github.com/microsoft/skills-for-fabric.git $tmp\skills-for-fabric
git clone --depth 1 https://github.com/PBI-Guy/Power-BI-Optimization-Skill.git $tmp\pbi-optimization
Copy-Item "$tmp\skills-for-fabric\plugins\fabric-authoring\skills\eventstream-authoring-cli\*" ".github\skills\eventstream-authoring\" -Recurse -Force
Copy-Item "$tmp\skills-for-fabric\plugins\fabric-authoring\skills\spark-authoring-cli\*" ".github\skills\spark-authoring\" -Recurse -Force
Copy-Item "$tmp\skills-for-fabric\plugins\fabric-authoring\skills\semantic-model-authoring\*" ".github\skills\fabric-semantic-model-authoring\" -Recurse -Force
Copy-Item "$tmp\skills-for-fabric\plugins\powerbi-authoring\skills\powerbi-report-authoring\*" ".github\skills\powerbi-report-authoring\" -Recurse -Force
Copy-Item "$tmp\pbi-optimization\skills\powerbi-optimization\*" ".github\skills\powerbi-optimization\" -Recurse -Force
git diff --stat .github/skills/
```

Diff any changes and PR them like normal repo edits.

## Skill discovery — rule of engagement (v1.14.0, 2026-07-08)

When the agent hits a task poorly covered by the workspace skills catalog above (or by user-scoped Superpowers skills), the agent **discovers and proposes new skills** rather than reinventing patterns. New skills are never auto-installed — every install goes through a user-reviewed PR.

### Trigger conditions (any one)

1. Task requires domain expertise beyond what installed `SKILL.md` files cover (e.g. Fabric Real-Time Intelligence, Direct Lake optimisation, agent evaluation patterns)
2. A failure pattern surfaces that a specialised skill would have prevented or diagnosed faster (e.g. today's `System_Cancelled_Session_Statements_Failed` on silver notebook → `spark-operations` skill installed via [PR #134](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/134))
3. A public best-practice source (Microsoft Learn, ADR, GitHub best-practice repo) references a skill / plugin the agent doesn't have loaded
4. User explicitly asks about additional skills

### Discovery order (stop at first useful match)

1. [`microsoft/skills-for-fabric`](https://github.com/microsoft/skills-for-fabric) — Fabric + Power BI + Real-Time Intelligence + Data Engineering
2. [`PBI-Guy/Power-BI-Optimization-Skill`](https://github.com/PBI-Guy/Power-BI-Optimization-Skill) — DAX + model + report + Power Query + RLS deep dive
3. User global skills at `~/.agents/skills/` and Superpowers marketplace at `~/.copilot/installed-plugins/superpowers-marketplace/superpowers/skills/`
4. Microsoft's [`skills-for-*`](https://github.com/microsoft?q=skills-for) naming pattern on GitHub for additional catalogs
5. Bundled agent-rule files in target repos (`.cursorrules`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) that may reference skills we haven't loaded

### Evaluation checklist (before proposing install)

- [ ] Skill directly targets the trigger problem OR upcoming milestone in the active sprint
- [ ] Skill has a `SKILL.md` file with clear description + triggers + steps
- [ ] Maturity is stable (not draft / experimental) OR the trigger is severe enough to accept preview risk
- [ ] License is compatible with our MIT posture
- [ ] No meaningful overlap with already-installed skills (or the PR body documents the reason for overlap)
- [ ] Fits the current sprint scope (e.g. Sprint 10 M1..M4) — don't install skills for future sprints speculatively

### PR shape for a proposed install

- **Branch:** `sprint-XX/skill-<name>-install` (single) or `sprint-XX/skills-<theme>` (bundle)
- **Files:** `.github/skills/<name>/*` + `AGENTS.md` row in the *Workspace-scoped skills* table + optional strategy spec entry
- **Title:** `feat(skills): install <name> for <problem or milestone>`
- **Body must include:**
  - Source repo URL(s) with commit SHA / release tag pinned
  - Trigger condition that surfaced the need
  - Evaluation checklist all ticked with brief rationale per box
  - Refresh command line snippet added to the *Skill refresh procedure* block in AGENTS.md
- **Label:** `sprint-XX` plus (optional) `skills`

### User decision gate

- Every skill install requires user review + merge — the agent **does not** auto-install even when the trigger condition is clear
- User may reject with reasons; agent then documents the non-install in AGENTS.md *NOT installed* list with rationale
- **Emergency skip** allowed only when the missing skill blocks a live outage AND user pre-approves in the same thread with the phrase `approved-to-apply`

### Removal / sunset

- Skills that fall out of relevance move to the AGENTS.md *NOT installed* list at sprint retrospective
- Physical deletion of `.github/skills/<name>/` is destructive and requires `approved-to-apply` in a dedicated hygiene PR

### Precedent from this repo

- [PR #133](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/133) — 5-skill install for Sprint 10 M1..M4 (proactive at user's request)
- [PR #134](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/134) — 2-skill follow-up after failure trigger (silver `System_Cancelled_Session_Statements_Failed`) surfaced the need for `spark-operations` + `e2e-medallion-architecture`

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
