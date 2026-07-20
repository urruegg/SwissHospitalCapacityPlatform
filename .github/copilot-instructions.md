# Copilot Instructions — Swiss Hospital Capacity Platform

| Field | Value |
|-------|-------|
| **Version** | 1.9.0 |
| **Date** | 2026-07-18 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | 1.8.0 (added the Experience-lane + `apps/**` Scope Guard anchor routing UX questions to the `ux-design-agent`, including its Playwright visual/accessibility verification; issue #258) |

This repository hosts a sample **Swiss Hospital Capacity Platform**: a system where AI agents
plan, execute, and observe hospital capacity management workflows (CI/CD, infrastructure provisioning,
incident response, cost/compliance) on Microsoft Azure.

**Runtime (per ADR-0002):**
This platform uses the **GitHub Copilot coding agent** with a
**Superpowers-first execution model** for new work, configured by assets in this
repository — `AGENTS.md`, all agent packs (prompt + runtime manifest +
golden-tasks) under `agents/<name>/` as the single source of truth,
this `copilot-instructions.md`, `.github/copilot/mcp.json`, ISSUE_TEMPLATE/,
PR template, validation workflows, and Bicep template libraries (UC1 outputs).
There is **no bespoke Python service, no Foundry-hosted agent, and no
platform-runtime Azure infrastructure** in this repo. Work targets Azure and
Microsoft 365 resources via MCP servers.

Use these instructions to guide all code, documentation, and review suggestions in
this repo.

### Superpowers Skills System (Mandatory)

Before starting any task:

1. Check whether a Superpowers skill applies to the requested work.
2. If a skill applies, read its `SKILL.md` before implementation.

When a skill applies:

1. Skill usage is mandatory.
2. Do not skip required steps in that skill.
3. If multiple skills apply, execute them in a defensible order and document the order in your reasoning or issue/PR trail.

Core skills that must always be considered for applicable work:

1. `test-driven-development`
2. `systematic-debugging`
3. `writing-plans`
4. `verification-before-completion`

Enforcement:

1. If a mandatory applicable skill is not used, treat the run as non-compliant.
2. Non-compliant runs must be corrected before completion or merge.

### Scenario Alignment (Case Study 26)
The target domain is a regulated Swiss healthcare platform for patient-flow and
capacity optimisation across multiple stakeholders (acute hospitals, rehab,
Spitex, and insurer-linked coordination). Repository guidance must therefore
support a multi-layer enterprise AI platform:

- Data platform and interoperability assets (Fabric, FHIR, ingestion, semantic models)
- AI/ML assets (forecasting, discharge optimisation, evaluation notebooks)
- Operational copilot assets (prompts, grounding, orchestration, evaluations)
- Application and integration assets (operations apps, APIs, Logic Apps, connectors)
- Security and compliance artefacts (DSG controls, policy mappings, governance evidence)

This alignment does not change the runtime decision in ADR-0002: the platform
agent runtime remains GitHub Copilot coding agent + MCP servers.

---

## Table of Contents

1. Project Architecture
2. Build & Test Commands
3. Coding Conventions
4. Security
5. Testing Strategy
6. Commit & PR Conventions
7. Code Review Checklist
8. Naming Conventions
9. Document Versioning

---

## 1. Project Architecture

### Repository Structure
> The repository is in an early stage. Folders marked *(planned)* are conventions
> agents should follow when creating new code; do not invent alternative layouts.
>
> **Important**: There is no Python service code, no FastAPI/Node API, and no
> hosted agent runtime in this repo. Per
> ADR-0002, agents
> are realised as **Markdown prompt files** and **MCP server configuration**.
> Any source code created by a use case (for example: data transformation,
> model training helper, or integration adapter) must live in an explicit
> domain folder and remain subordinate to governance-first documentation.

| Folder | Stack | Purpose |
|--------|-------|---------|
| `docs/` *(exists)* | Markdown | Canonical requirements, architecture, governance, ADRs, and workshop deliverables. |
| `docs/compliance/` *(planned)* | Markdown | Swiss DSG, cantonal constraints, interoperability and audit mappings. |
| `docs/architecture/` *(planned)* | Markdown / diagrams | Layered architecture views (data, AI, app, integration, security). |
| `AGENTS.md` *(planned, top-level)* | Markdown | Top-level agent registry: one row per agent (name, owner, trigger, MCP servers in use, side-effect ceiling, golden-task path). Read by the Copilot coding agent on every run. |
| `.github/copilot-instructions.md` | Markdown | This file. Repo-wide conventions and contracts for the Copilot coding agent. |
| `.github/copilot/` *(planned)* | JSON / Markdown | Copilot coding-agent configuration: `mcp.json` allow-list, optional per-agent overrides. |
| `.github/ISSUE_TEMPLATE/` *(planned)* | YAML | Issue templates that drive Superpowers-first execution (`uc1-build-subscription.yml`, `uc2-drift-scan.yml`, `uc3-pr-review.yml`, etc.). |
| `.github/PULL_REQUEST_TEMPLATE.md` *(exists)* | Markdown | PR template enforcing the PR Output Contract (§6). |
| `.github/workflows/` *(planned)* | GitHub Actions YAML | CI: markdown lint, Bicep build/validate, security/secret scans, optional eval-on-fixtures workflows. UC2 nightly scheduler workflow opens an issue for the drift agent. |
| `agents/` *(exists)* | Markdown / YAML | **Single source of truth** for every agent pack — prompt file (`AGENT.md`), runtime manifest (`manifest.yaml`), and golden-task fixtures. Includes platform-control-plane packs (orchestrator, spec-parser-agent, ...), Sprint 11 runtime packs (bmca-agent, ooa-agent, ...), and the Sprint 09 v2 `fabric-data-agent`. The retired `agents-archive/` folder (v2.0.0 restructure) is history-only in `git log`. |
| `evals/` *(planned)* | Markdown / YAML | Golden-task fixtures: input issue body + expected PR/comment shape. Optionally driven by a `gh` workflow. **Not pytest.** |
| `infra/` *(planned)* | Bicep | **UC1 output artefacts** — the Bicep modules the Spec Parser Agent assembles into a customer's landing-zone PR. Not infrastructure that hosts the agent. |
| `infra/environments/` *(planned)* | Bicep parameters | Customer environment definitions (`dev` / `sit` / `prod`) for UC outputs. |
| `data-platform/` *(planned)* | SQL / notebooks / config | Ingestion, transformations, semantic models, and healthcare interoperability mappings. |
| `ai-models/` *(planned)* | Python / notebooks / YAML | Forecasting and optimisation assets, training/evaluation configs, model cards. |
| `copilot/` *(planned)* | Markdown / config | Prompts, grounding references, orchestration definitions, and evaluation packs. |
| `apps/` *(planned)* | App code / low-code assets | Bed management app, dashboards, and operational UI integration outputs. |
| `integrations/` *(planned)* | Workflow / API definitions | Logic Apps, connectors, event flows, and FHIR integration adapters. |
| `security-governance/` *(planned)* | Policy-as-code / Markdown | Purview mappings, access model definitions, and control evidence. |
| `pipelines/` *(planned)* | YAML | Delivery workflows spanning docs, infra, data, AI, and app release lanes. |
| `samples/` *(planned)* | JSON / Markdown | Sample source bundles, sample GitHub PR payloads, and sample drift reports — used as fixtures in golden tasks. |
| `docs/sprints/` *(exists)* | Markdown | Sprint backlogs S0–S6. |

### Architecture Lanes (mandatory mental model)
When creating or reviewing changes, map them to one or more explicit lanes:

1. Governance lane: `docs/`, `security-governance/`, policy and compliance evidence
2. Platform control lane: `agents/`, `.github/`, `evals/`, `AGENTS.md`
3. Infrastructure lane: `infra/`, environment parameters, deployment contracts
4. Data lane: `data-platform/`, interoperability artefacts, semantic models
5. AI lane: `ai-models/`, `copilot/`, eval assets, safety controls
6. Experience lane: `apps/`, `integrations/`, operational workflows. All user-experience questions (mockups, flows, brand tokens, accessibility) are anchored to the [`ux-design-agent`](../agents/ux-design-agent/AGENT.md), which may use Playwright — the repo's local CLI (`@playwright/test` + `@axe-core/playwright`) or the read-only `playwright-mcp` server for the VS Code / Copilot shared-context mode — for visual + accessibility verification.

Every non-trivial PR should state which lanes are impacted.

### Key Documentation (read before making significant changes)

When `docs/ARTEFACTS.md` exists, treat it as the single entry point. Until then,
consult the relevant docs listed below before modifying architecture, data models,
security, or agent behavior.

#### Solution-Level Docs (`docs/` — create when first needed)
| Document | Purpose | Read before changing... |
|----------|---------|------------------------|
| `docs/PRD.md` | Product requirements: personas, user journeys, FR/NFR catalogue with stable IDs, traceability matrix | Any scope/feature/requirement change; ALWAYS read before writing user stories or PRs |
| `docs/ARCHITECTURE.md` | System architecture, agent topology, integrations, hosting | Service boundaries, agent contracts, infra topology |
| `docs/AI.md` | Responsible AI guidelines, agent governance, model selection, prompt patterns | Agent prompts, model upgrades, RAI compliance |
| `docs/SECURITY.md` | Zero Trust, identity, managed identity, auth, secrets, RBAC | Auth flows, Key Vault, RBAC, CORS |
| `docs/DATA.md` | Agent memory, trace storage, Cosmos DB partitioning, retention | Data models, partition keys, retention |
| `docs/INFRASTRUCTURE.md` | Azure resource inventory, Bicep modules, environments | Infra provisioning, environment config |
| `docs/INTEGRATION.md` | Cross-provider integration architecture (FHIR, Logic Apps, connectors) | API/orchestration boundaries and interoperability rules |
| `docs/COMPLIANCE.md` | Swiss DSG and cantonal control mappings | Data handling, retention, access, auditability decisions |
| `docs/OPERATIONS.md` | Day-2 runbooks, incident model, service ownership | On-call operations and support handoffs |
| `docs/ALM_PLAN.md` | CI/CD pipelines, OIDC federation, deployment strategy | Workflows, release process, rollback |
| `docs/TEST.md` | Test strategy, coverage thresholds, eval harness | Test patterns, eval gates |
| `docs/adr/NNNN-title.md` | Architecture Decision Records | Any cross-cutting change |

> **Rule**: When working on a sub-component (agent, tool, infra module), read its
> local README first, then fall back to the solution-level docs above for
> cross-cutting concerns (security, data, infrastructure, AI governance).

### Agent Decision Order
1. Identify target scope (`agents/<name>/`, `infra/`, `docs/`, `.github/`, etc.).
2. Read docs in this order: target's local `AGENT.md` or `README.md` (if present) → `AGENTS.md` → this file → cross-cutting solution docs (`docs/*`).
3. Use the **MCP server allow-list** in `.github/copilot/mcp.json` to discover which tools are available. Never assume an MCP server exists — if it isn't in the allow-list, propose adding it via a separate PR with mandatory reviewer.
4. Implement minimal changes in the correct layer (`agents/<name>/` for agent prompt / manifest / golden-task changes, `infra/` for UC1 Bicep outputs, `docs/` for governance).
5. Run the most specific golden-task fixture first, then broader ones, then propose updates to other fixtures if the change affects them.
6. Validate cross-cutting impact: prompts, MCP tool contracts in `AGENTS.md`, RBAC implied by new MCP usage, Bicep templates touched, security, docs.

### Scope Guards (mandatory)
- Changes in `agents/<name>/**`: read `agents/<name>/AGENT.md` and `AGENTS.md` first; if the change introduces a new MCP server or tool, also read `.github/copilot/mcp.json` and `docs/SECURITY.md`.
- Changes in `.github/copilot/mcp.json`: read `docs/SECURITY.md` and `docs/AI.md`; require CODEOWNERS approval; declare new server's required permissions in the PR.
- Changes in `infra/**`: read `docs/INFRASTRUCTURE.md` (which clarifies these are UC1 *outputs*) and `docs/ALM_PLAN.md` (Bicep validate workflow).
- Changes in `data-platform/**`: read `docs/DATA.md`, `docs/COMPLIANCE.md`, and `docs/INTEGRATION.md` first.
- Changes in `ai-models/**` or `copilot/**`: read `docs/AI.md`, `docs/TEST.md`, and `docs/COMPLIANCE.md` first.
- Changes in `apps/**` or `integrations/**`: read `docs/ARCHITECTURE.md`, `docs/INTEGRATION.md`, and `docs/SECURITY.md` first. Route user-experience questions (mockups, flows, brand tokens, accessibility) to the [`ux-design-agent`](../agents/ux-design-agent/AGENT.md); it may use Playwright (the repo's local CLI or the read-only `playwright-mcp` server) for visual + accessibility verification.
- Changes in `security-governance/**`: read `docs/SECURITY.md`, `docs/COMPLIANCE.md`, and `docs/AI.md` first.
- Changes in `.github/workflows/**`: read `docs/ALM_PLAN.md` and `docs/SECURITY.md` (OIDC, secrets) before editing.
- Changes in `evals/**` / `agents/<name>/golden-tasks.md`: read `docs/AI.md` and `docs/TEST.md` first.
- Changes in `docs/**` (and any Markdown create or update anywhere in the repo): every edited doc must follow §9 Document Versioning **and** use the [`document-authoring`](skills/document-authoring/SKILL.md) skill for the judgment checks (version-bump level, FR/NFR traceability, status accuracy). Mechanical encoding + lint gates are automated and enforced by `scripts/lint/check_mojibake.py`, the `.githooks/pre-commit` hook, and the CI `mojibake-scan` job — a doc that fails these gates must be repaired before it is saved or committed.

### Key Technical Decisions
- **Runtime**: **GitHub Copilot coding agent** (per ADR-0002) with Superpowers-first execution for new work. No bespoke service, no Foundry-hosted agent. Legacy per-agent Markdown assets are retained for compatibility and rollback.
- **Model**: Whatever GitHub Copilot uses at runtime. The platform does not select, deploy, or manage a model.
- **Cloud**: Microsoft Azure for **agent targets only** (UC1's customer landing zones and UC2's scanned subscriptions). Delivery, review, and planning workflows are GitHub-native. No multi-cloud abstractions unless explicitly required.
- **IaC**: **Bicep** for all UC1 *output artefacts* (the landing-zone templates the Spec Parser Agent assembles). Use Terraform only when multi-cloud or an existing verified module mandates it.
- **Solution shape**: Multi-layer enterprise AI platform repository (governance + control plane + infra + data + AI + app/integration lanes), aligned to Swiss healthcare operating constraints.
- **Identity**:
  - **GitHub Copilot coding-agent identity** for everything that happens inside this repo.
  - **Managed Identity / Workload Identity Federation** for any Azure MCP call made by the coding agent. OBO when human-triggered.
  - No connection strings, no long-lived client secrets in code, config, or PR descriptions.
- **Secrets**: GitHub Actions secrets for CI; Azure Key Vault references *only inside Bicep modules under `infra/` (UC1 outputs)*, never for the platform itself.
- **Agent memory & traces**: The **repository itself** (issues, PRs, comments, branches, audit log) plus GitHub Copilot coding-agent run history. **No Cosmos DB persistence at the platform-runtime layer.** A Cosmos DB resource may appear *inside* a UC1-generated Bicep template when a customer landing zone requires it — that is an output, not a dependency.
- **Observability**: GitHub-native (issue/PR threads, audit log, Actions logs). No OpenTelemetry/Application Insights wiring required for the platform. A UC1-generated landing zone may include App Insights as an output — again, that is the customer's infra, not ours.
- **CI/CD**: GitHub Actions — markdown lint, Bicep build/validate (for any committed `infra/` template), CodeQL/secret scan. **OIDC federation** to Azure is used *only* when a workflow needs to do a `what-if` against a customer subscription on behalf of UC1 — not for deploying this platform.
- **Environments**: This platform has no `dev` / `test` / `prod` environments of its own. UC1's *output* landing zones have those environments; they are owned by the customer.

### Scenario-to-Repository Mapping (Swiss Patient Flow)
Use the following mapping as a design constraint when structuring artefacts:

| Scenario Requirement | Primary Repo Areas |
|----------------------|--------------------|
| Multi-provider healthcare ecosystem | `integrations/`, `data-platform/`, `docs/INTEGRATION.md` |
| AI demand forecasting and optimisation | `ai-models/`, `copilot/`, `docs/AI.md` |
| Operational copilot for bed/capacity teams | `copilot/`, `apps/`, `agents/` |
| Real-time visibility and reporting | `data-platform/`, `apps/`, `docs/ARCHITECTURE.md` |
| Swiss DSG and cantonal governance | `security-governance/`, `docs/COMPLIANCE.md`, `docs/SECURITY.md` |
| Enterprise ALM from DEV to SIT to PROD | `infra/`, `pipelines/`, `docs/ALM_PLAN.md` |

---

## 2. Build & Test Commands

> Commands below are the conventions for this repo. The platform itself has
> **no application build** — it is Markdown + Bicep + YAML. Commands are
> limited to lint, schema/Bicep validate, and golden-task fixture replay.

```bash
# Markdown lint (every doc edit must pass)
npx --yes markdownlint-cli2 "**/*.md" "#node_modules"

# Link check (catches broken cross-doc anchors when bumping versions)
npx --yes markdown-link-check docs/**/*.md docs/sprints/*.md .github/*.md

# Bicep (UC1 output templates only)
az bicep build --file infra/main.bicep
# Dry-run against a customer subscription (UC1 staging deploy)
az deployment group what-if -g <rg> -f infra/main.bicep

# Golden-task replay (when evals/ exists; details in docs/TEST.md)
# Markdown-driven, not pytest. Example:
gh workflow run eval-goldens.yml -f agent=orchestrator -f fixture=smoke_echo

# Data/AI lane quality gates (run when those folders are introduced)
# Keep commands in lane-local README files and link them from docs/TEST.md
# Example placeholders:
# make data-test
# make ai-eval
```

**There is no `pip install`, `npm test`, or `pytest` step in this repo.** If a
future use case introduces source code, it brings its own build/test commands
and updates this section in the same PR.

For multi-lane repos, CI must remain explicit per lane: docs, infra, data, AI,
copilot/agent evals, and app/integration.

---

## 3. Coding Conventions

### Do / Don't (Agent Guardrails)
- **Do** keep changes minimal and scoped to the requested task.
- **Do** follow existing patterns in adjacent files before introducing new patterns.
- **Do** update tests and docs when behavior or contracts change.
- **Do** surface assumptions you made when context is incomplete.
- **Don't** hard-code subscription IDs, tenant IDs, resource names, URLs, or secrets.
- **Don't** introduce new frameworks, runtimes, or cloud providers without justification.
- **Don't** produce destructive commands (delete, drop, force-push, scale-to-zero,
  `rm -rf`, `terraform destroy`, `az ... delete`) without a dry-run and explicit
  user confirmation.
- **Don't** add tool/agent capabilities that bypass the dry-run / plan stage.
- **Don't** merge lane-coupled changes without updating cross-lane traceability
  in PR description (for example: AI model change without data-contract impact).

### General principles
- Prefer **clarity over cleverness**. Markdown and Bicep should be readable by an on-call engineer.
- Validate inputs at trust boundaries (issue body schema for agent triggers, MCP tool input schemas).
- Fail fast with actionable error messages in agent prompts; instruct agents to refuse rather than guess.
- Add comments / prompt-internal rationale only to explain *why*, not *what*.

### Markdown (prompts, docs, agent definitions)
- Use ATX headings (`#`, `##`, ...), reference-style links, and fenced code blocks with language hints.
- All cross-doc links use repo-relative paths and pass `markdown-link-check`.
- Agent prompt files (`agents/<name>/AGENT.md`) use a fixed structure: **Identity**, **Scope**, **Tools**, **Refusal Rules**, **Output Contract**, **Confirmation Rules for `deploy`/`delete`**.
- Golden-task files (`agents/<name>/golden-tasks.md` or `evals/<name>/*.md`) use a fixed structure: **Input issue body**, **Expected MCP tool calls (ordered or set)**, **Expected PR/comment shape**, **Forbidden behaviors**.

### Bicep (UC1 output templates only)
- One module per resource type under `infra/modules/`; compose from `infra/main.bicep`.
- Parameterise environment (`dev` / `test` / `prod`) for the **customer's** landing zone; never hard-code names.
- Tag every resource: `env`, `owner`, `costCenter`, `workload`.
- Enable diagnostic settings → Log Analytics for every production resource the customer deploys.
- Run `az deployment ... what-if` before any `create`. UC1 prompts must require this step.

### Shell & PowerShell (only if a use case introduces helper scripts)
- Bash: `set -euo pipefail` at top of every script.
- PowerShell 7+: `Set-StrictMode -Version Latest` and `$ErrorActionPreference = 'Stop'`.

### Python / TypeScript (not present today)
- The platform contains no Python or TypeScript source. If a future PR introduces some, it must (a) bring linting/formatting/test config in the same PR, (b) document the new build/test commands in §2, and (c) reference an ADR explaining why a non-Markdown component is necessary.

### Agentic patterns (Copilot coding agent)
- Every agent **prompt file** declares: **name, owner, trigger(s), MCP servers in use, side-effect ceiling (`read | write | deploy | delete`), required permissions, golden-task path**.
- Every **MCP tool call** is treated as a typed call with explicit inputs/outputs; the agent must not improvise tool parameter shapes.
- Tools with side-effect ceiling `deploy` or `delete` require an **explicit human confirmation comment on the agent's draft PR or issue** before the agent fires the corresponding MCP call. The agent must produce a **dry-run / plan** first; the human approves; only then does the agent execute. This rule is enforced by per-agent prompts and called out in the PR template.
- Persist agent intent and outputs as **GitHub-native artefacts** (issues, PRs, comments, commits) so they are auditable without external infrastructure.
- Treat any value received from an MCP tool or LLM output as **untrusted input**: validate before passing to another tool, shell, or KQL query.
- Any prompt or agent-behavior change must be backed by an updated **golden-task fixture** in `agents/<name>/golden-tasks.md` (or `evals/<name>/`) referenced in the PR.

### Data, AI, and Integration Conventions (when those lanes are present)
- Data contracts must be versioned and backwards-compatibility impact declared.
- AI artefacts require dataset provenance, evaluation metric definitions, and
  documented safety constraints before promotion.
- Integration artefacts must identify source system, target system, and PHI/PII
  classification for each flow.
- Copilot prompt/orchestration changes must include regression fixtures covering
  refusal behavior for unsafe or non-compliant actions.

### GitHub Copilot coding-agent usage
- The Copilot coding agent picks up issues created via `ISSUE_TEMPLATE/` or `@copilot`-mentioned issues. It then opens a branch + draft PR.
- All MCP servers used by the agent must be listed in `.github/copilot/mcp.json` (allow-list). Changes to this file go through CODEOWNERS-approved PRs.
- Long-running tool calls (deploy, drift scan) must be split into a *plan* PR and a separate *apply* PR or follow-up comment; do not chain mutations behind one prompt.
- The agent must reference the relevant FR/NFR ID(s) from `docs/PRD.md` in its PR description (see §6).

---

## 4. Security

- Follow the **OWASP Top 10**; flag and fix vulnerable patterns on sight.
- **Authentication**:
  - The agent acts under **GitHub Copilot coding-agent identity** in this repo.
  - Outbound MCP calls into Azure use **Workload Identity Federation** (no long-lived secrets), and **OBO** when a human triggers the agent.
  - Entra ID is the IdP for human callers of MCP-targeted resources.
- **Secrets**:
  - Repository-level secrets via **GitHub Actions secrets** + **GitHub OIDC** — never long-lived in code, config, prompts, or PR descriptions.
  - Bicep templates under `infra/` (UC1 outputs) reference **Azure Key Vault** for the *customer's* landing zone; that Key Vault is provisioned by the template, not by this platform.
  - Agents must never echo, log, or commit secrets; agents must redact token-like strings before posting any comment.
- **MCP allow-list**: Only MCP servers listed in `.github/copilot/mcp.json` are permitted. Adding a server requires a CODEOWNERS-approved PR documenting purpose, required permissions, and a golden-task that exercises a representative tool.
- **RBAC**: Least privilege on every MCP-side principal and Azure role assignment. Prefer built-in roles; scope at the resource or resource group level (never subscription unless required).
- **Tool inputs**: Validate and sanitise all MCP tool inputs at the prompt level. Treat any value derived from an LLM as untrusted.
- **Destructive actions**: deploy, delete, drop, force-push, scale-to-zero, and `terraform destroy` require an **explicit, separate human confirmation comment** on the agent's draft PR or issue. Do **not** auto-approve in any prompt or workflow.
- **Egress**: The platform itself has no egress (no service). UC1 *outputs* must use private endpoints for Key Vault, Cosmos DB, and Storage in production, and CORS allow-lists never `*`.

---

## 5. Testing Strategy

- **Test-first**: Write tests before implementing features or fixing bugs.
- **Fixture-first for agents**: Every agent change must include or update a **golden-task fixture** under `agents/<name>/golden-tasks.md` (or `evals/<name>/`) that describes input issue body + expected MCP tool calls + expected PR/comment shape + forbidden behaviors.
- **Coverage target**:
  - Agent prompts and orchestration must keep at least one happy-path fixture and one failure-mode fixture per agent before sprint exit.
  - When executable application code is introduced in this repo, target $\ge 80\%$ coverage for new code and do not decrease overall coverage in PRs.
- **Backend tests (when backend code exists)**: Prefer xUnit + Moq, follow Arrange-Act-Assert, and mock external dependencies (for example HTTP clients, service interfaces, and loggers) to keep tests deterministic.
- **Frontend tests (when frontend code exists)**: Prefer Jest for UI/unit tests, focus on hooks and service layers, and mock network/async dependencies (for example `fetch` and query clients).
- **Bicep validation**: Every `.bicep` file under `infra/` must build cleanly (`az bicep build`) and pass `what-if` in CI when changed.
- **Markdown lint**: Every Markdown file must pass `markdownlint-cli2` and `markdown-link-check` in CI.
- **Eval harness**: Optional workflow `eval-goldens.yml` (planned) replays selected fixtures via the Copilot coding agent and asserts the PR/comment shape. There is **no `pytest` harness** in this repo today.
- **CI gate**: All required checks must pass before merge. If a dedicated test workflow exists (for example `ci-test.yml`), it is a mandatory merge gate.
- **No flaky tests**: If a test is intermittent, fix or remove it; do not bypass quality gates by skipping unstable tests.
- **Lane-specific checks**: If `data-platform/`, `ai-models/`, `copilot/`, `apps/`, or `integrations/` are touched, run the lane checks documented in `docs/TEST.md` and include evidence in PR.
- **Regulated-change checks**: Any change that impacts PHI/PII handling requires explicit security/compliance review evidence in PR.

---

## 6. Commit & PR Conventions

### Commit Messages
Use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to use | Triggers release? |
|--------|-------------|-------------------|
| `fix:` | Bug fix | Patch (x.x.+1) |
| `feat:` | New feature | Minor (x.+1.0) |
| `feat!:` or `BREAKING CHANGE:` | Breaking change | Major (+1.0.0) |
| `docs:` | Documentation only | No |
| `ci:` | CI/CD workflow changes | No |
| `refactor:` | Code change that neither fixes nor adds | No |
| `test:` | Adding or updating tests | No |
| `perf:` | Performance improvement | No |
| `chore:` | Maintenance (deps, config) | No |

### Branch & PR Model
- **Single-branch model**: all work lands on `main`.
- Copilot coding agent creates feature branches automatically from issues.
- Use the PR template at `.github/PULL_REQUEST_TEMPLATE.md` (create if missing).

### PR Output Contract (for agents)
PR description must include:
- **What changed** (by file/area)
- **Why** (issue/requirement link)
- **Requirements implemented** — list every `FR-*` / `NFR-*` ID from `docs/PRD.md` advanced by this PR. Required by `NFR-GOV-006`. Use `partial:` if not fully verified.
- **Test evidence** (commands run + pass/fail summary)
- **Agent/eval impact** (eval scores before/after, golden-task delta)
- **API impact** (new/changed endpoints, tool contracts)
- **Infra impact** (Bicep modules added/changed, `what-if` summary)
- **Security impact** (new permissions, secrets, identities)
- **Lane impact** (which architecture lanes are affected and cross-lane dependencies)
- **Compliance impact** (DSG/cantonal considerations; `none` if not applicable)

### Agent PR Completion Contract (hard gate)
Agents must not create or mark a PR ready for review unless **all** points below
are satisfied:
- **Scope contract**: Change set is limited to the approved issue scope and
  allowed folders. Unrelated file edits are excluded or explicitly approved.
- **Validation contract**: Required CI checks for affected components run
  green: markdown lint + link check on doc changes; `az bicep build` + `what-if`
  on `infra/**` changes; golden-task fixture replay on `agents/**` changes.
  PR includes command-level validation evidence (CI log link or pasted output).
- **Eval contract**: If a prompt under `agents/**` or a fixture under
  `evals/**` or `agents/**/golden-tasks.md` changed, the relevant golden
  task(s) were replayed and results attached.
- **Documentation contract**: Relevant docs are updated when behavior, contracts,
  security, or operations changed. If no doc update is required, PR states
  explicit justification.
- **Commit contract**: Commit messages follow Conventional Commits. Branch and
  PR are linked to the governing issue(s).
- **Traceability contract**: PR description lists every `FR-*` / `NFR-*` ID from
  `docs/PRD.md` it implements. If a new requirement is introduced or scope shifts,
  `docs/PRD.md` §7 (traceability matrix) is updated in the same PR. Golden-task
  fixtures reference the requirement ID(s) they verify (front-matter `requirement:`
  key, e.g. `requirement: FR-UC1-005`).
- **Versioning contract**: Any doc edited in the PR has its **Version** header
  bumped per the rules in §9 Document Versioning, and
  the **Previous Version** field is updated. If the PR makes no semantic change
  to a doc (e.g. pure formatting in a CI commit), the contract is satisfied by a
  PATCH bump.
- **Impact contract**: PR includes Bicep (UC1 output) impact, MCP allow-list
  impact, security impact, and eval impact statements. If impact is none, PR
  states `none` explicitly.
- **Review handoff contract**: PR lists residual risks/open questions and the
  agent summarises what should be reviewed first.

---

## 7. Code Review Checklist

Before approving a PR, verify:
- [ ] All CI checks pass (markdown lint, link check, Bicep build/validate where applicable, security scan, golden-task replay where applicable)
- [ ] New / changed agent prompts have at least one happy-path and one failure-mode golden-task fixture
- [ ] PR lists the `FR-*` / `NFR-*` IDs it implements; `docs/PRD.md` §7 is consistent
- [ ] Every edited doc has its **Version** header bumped per §9 Document Versioning
- [ ] No hard-coded secrets, subscription IDs, tenant IDs, URLs, or resource names
- [ ] Any new MCP server is added to `.github/copilot/mcp.json` with documented purpose + required permissions, and a CODEOWNERS-approved review
- [ ] Agent prompts for `deploy`/`delete` side-effect tools enforce the human-confirmation comment rule
- [ ] Commit messages follow Conventional Commits format

### Change Impact Checklist (before merge)
- [ ] Documentation updated where behavior/contracts changed (`docs/*` or local `AGENT.md`)
- [ ] Security impact assessed (MCP allow-list, secrets, RBAC implied by new tool usage)
- [ ] Bicep (UC1 output) impact assessed (modules added/changed, `what-if` clean, tags applied)
- [ ] AI/eval impact assessed (golden-task replays, refusal-rule changes)
- [ ] Lane impact declared (governance/control/infra/data/AI/experience)
- [ ] Compliance impact declared for regulated data/process changes

---

## 8. Naming Conventions

- **Files & folders**: lowercase with hyphens (`uc1-build-subscription.yml`, `drift-analyzer/`). Markdown files use `UPPER-SNAKE.md` only for top-level conventional docs (`AGENTS.md`, `README.md`, `SECURITY.md`); per-agent files inside a folder use lowercase (`agent.md`, `golden-tasks.md`, `runbook.md`).
- **Domain lane folders**: `data-platform/`, `ai-models/`, `copilot/`, `apps/`,
  `integrations/`, `security-governance/`, `pipelines/`.
- **Bicep resources**: `kebab-case` with environment suffix
  (e.g., `kv-agentic-devops-dev`, `cosmos-agentic-devops-prod`). These names appear in UC1 *output* templates; they are not the platform's own infrastructure.
- **Azure resource short name**: Use `ihzhhpf` in Azure resource names to represent the solution.
- **Azure environment suffix policy**:
  - `SIT` resources must end with `-sit`.
  - `PROD` resources must end with `-prod`.
  - Shared resources across environments must not have an environment suffix.
  - `DEV` does not have a mandatory postfix rule in this baseline.
- **Azure resource pattern**: Prefer `<resource-type>-ihzhhpf-<env-suffix>` for environment-scoped resources and `<resource-type>-ihzhhpf` for shared resources.
- **Resource tags** (UC1 outputs): `env`, `owner`, `costCenter`, `workload` on every resource.
- **Git tags**: `vX.Y.Z` — managed by release tooling, never manual.
- **Agent names**: `kebab-case` matching the folder name (`spec-parser-agent`, `solution-design-agent`, `landing-zone-agent`, `compliance-agent`, `data-design-agent`, `app-builder-agent`, `test-verifier-agent`, `pr-review`, `drift-analyzer`, `orchestrator`).
- **MCP server identifiers**: `kebab-case` matching the server's published name (`azure-mcp`, `github-mcp`).
- **Issue templates**: `uc<N>-<short>.yml` (e.g., `uc1-build-subscription.yml`).

---

## 9. Document Versioning

Every Markdown document in `docs/`, `docs/sprints/`, `.github/`, and the root
`README.md` carries a version header (`Version`, `Date`, `Author`, `Status`,
`Previous Version`). Doc versions follow **[Semantic Versioning 2.0](https://semver.org/)**
adapted for prose:

| Bump | When | Examples |
|------|------|----------|
| **MAJOR** (`X.0.0`) | Breaking: rename/remove an identifier other docs depend on, reverse a previously-recorded decision, restructure headings so existing anchor links break, break a published contract. | Renaming `FR-UC1-005`; reversing SPRINT_PLAN §9 Q2; renaming a top-level section. |
| **MINOR** (`x.Y.0`) | Additive: new sections, new requirements, new stories, new decisions, refined wording that changes meaning but does not break IDs or anchors. | Adding the §9 decisions table; adding a new user story; adding a new FR/NFR row. |
| **PATCH** (`x.y.Z`) | Editorial: typos, formatting, link-target fixes, markdownlint fixes, tightening with no semantic change. | Fixing a typo; converting a 2-tuple version to a 3-tuple; reflowing a paragraph. |

### Rules
- Use the **three-component** form (`X.Y.Z`). Never `1.0` or `1`.
- Every PR that edits a doc must bump its `Version` and update `Previous Version`
  to the prior value (with a short parenthetical hint, e.g. `1.1.0 (added §7 matrix)`).
- Multiple bumps in a single PR collapse to **one** bump at the highest level
  applicable across the changes (e.g. an additive change plus typo fix = MINOR).
- A **MAJOR** bump must be backed by an ADR under `docs/adr/` explaining the
  break and migration path for any consumer that referenced the old IDs/anchors.
- The `Date` field is bumped only when the `Version` is bumped.
- Doc versions are **independent** from Git tag releases (`vX.Y.Z`). Git tags
  version the software; doc versions version the prose.
- ADRs (`docs/adr/NNNN-*.md`) use their `Status` field (Proposed → Accepted →
  Superseded) and do **not** require a SemVer header — supersession is recorded
  by linking the new ADR.
- When a previously-deferred decision becomes binding (e.g. SPRINT_PLAN §9 row
  reversed or refined), bump the document's MINOR (refinement) or MAJOR
  (reversal) and link to the superseding ADR.

### Examples in this repo
- Adding **§7 Traceability Matrix** to `docs/PRD.md` → MINOR (1.0.0 → 1.1.0).
- Adding `FR-PLT-007` after the matrix exists → another MINOR (1.1.0 → 1.2.0).
- Renaming `FR-UC1-005` → MAJOR (must add an ADR).
- Fixing a typo in a sprint header → PATCH (1.1.0 → 1.1.1).
