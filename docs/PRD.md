# PRD

| Field | Value |
| ----- | ----- |
| **Version** | 0.2.0 |
| **Date** | 2026-06-01 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | 0.1.0 (placeholder baseline document) |

## Purpose

This product requirements document defines the initial functional and non-functional
requirements for the Swiss Hospital Capacity Platform scenario represented in this
repository.

The target solution is a provider-internal AI-powered patient flow and hospital
capacity platform deployed for one Swiss cantonal hospital provider at a time,
for example USZ or LUKS. The repository scope also includes the GitHub-native
Copilot agent contracts used to plan, validate, and govern the solution assets.

## Scope

### In scope

- Single-provider deployment model within one cantonal hospital provider boundary.
- AI-powered operational support for:
  - 72-hour emergency demand forecasting.
  - Discharge readiness and downstream coordination.
  - Bed and capacity decision support for hospital operations teams.
- Controlled integration with external partners such as Spitex, rehabilitation,
  and insurer-linked coordination units.
- Repo-managed specification sources under `docs/` and `docs/specs/`.
- GitHub-native issue, PR, and project workflows for Copilot agent execution.
- Azure-targeted planning and validation for UC1 and UC2 flows.

### Out of scope

- Multi-provider shared tenancy or cantonal shared operations platform.
- External partner direct platform access.
- Dynamics 365 Customer Service workflows.
- Full clinician workstation replacement.
- WorkIQ or Azure DevOps as authoritative specification or workflow systems.

## Functional Requirements

### Platform Foundation

| ID | Requirement |
| -- | ----------- |
| `FR-PLT-001` | The platform shall provide a GitHub-native orchestrator flow that can accept an issue, classify it, and respond or route it to the correct specialized agent. |
| `FR-PLT-002` | The platform shall define explicit MCP tool contracts and allow-listed tool usage for every active agent. |
| `FR-PLT-003` | The platform shall require an explicit `approved-to-apply` confirmation before any deploy-capable agent executes an apply action. |
| `FR-PLT-004` | The platform shall treat repository-managed markdown under `docs/` and `docs/specs/` as the canonical source set for business and solution scope. |
| `FR-PLT-005` | The platform shall use GitHub Issues, Pull Requests, and GitHub Project as the operational workflow and planning surface. |

### UC1 Build Subscription

| ID | Requirement |
| -- | ----------- |
| `FR-UC1-001` | The spec-parser agent shall create a deployable landing-zone plan for a target Azure subscription from the canonical repo-managed source set. |
| `FR-UC1-002` | The spec-parser agent shall ingest the requested source bundle from `docs/`, `docs/specs/`, and supporting repo artefacts referenced in the issue. |
| `FR-UC1-003` | The spec-parser agent shall reject spreadsheet-only or other non-repo source inputs in the current scope. |
| `FR-UC1-004` | The spec-parser agent shall validate that the referenced source bundle contains sufficient deployable information before generating outputs. |
| `FR-UC1-005` | The spec-parser agent shall generate deterministic `.bicepparam` outputs for the same source inputs. |
| `FR-UC1-006` | The spec-parser agent shall run a Bicep build and `what-if` plan before any deployment action. |
| `FR-UC1-007` | The spec-parser agent shall publish its plan in a GitHub draft PR and link the run back to the triggering issue. |
| `FR-UC1-008` | The spec-parser agent shall apply the planned deployment only after valid human approval. |

### UC2 Drift Detection

| ID | Requirement |
| -- | ----------- |
| `FR-UC2-001` | The drift-analyzer agent shall compare a single Azure subscription against a canonical repo-managed source reference. |
| `FR-UC2-002` | The drift-analyzer agent shall execute Azure discovery in read-only mode. |
| `FR-UC2-003` | The drift-analyzer agent shall persist a deterministic drift report to the issue thread and a reproducible repo sidecar artifact. |
| `FR-UC2-004` | The drift-analyzer agent shall support full-subscription, single-resource-group, and tag-filtered scan scopes. |
| `FR-UC2-005` | The drift-analyzer agent shall classify findings by severity and apply the matching issue label. |
| `FR-UC2-006` | The drift-analyzer agent shall not require a separate platform runtime persistence layer for storing drift results. |
| `FR-UC2-007` | The drift-analyzer agent shall produce a remediation handoff block that a human can use to initiate UC1 planning. |

### UC3 Pull Request Review

| ID | Requirement |
| -- | ----------- |
| `FR-UC3-001` | The PR review flow shall support GitHub pull request review scenarios. |
| `FR-UC3-002` | The PR review flow shall use GitHub-native PR references and comments rather than Azure DevOps objects. |
| `FR-UC3-003` | The PR review flow shall be comment-only and shall not mutate code, branch state, or PR status. |

### Solution Use Cases

| ID | Requirement |
| -- | ----------- |
| `FR-SOL-001` | The solution shall forecast emergency demand over a 72-hour horizon for a single hospital provider, segmented by specialty and time window. |
| `FR-SOL-002` | The solution shall identify inpatients approaching discharge readiness and support downstream coordination through integration endpoints. |
| `FR-SOL-003` | The solution shall provide a GenAI-powered bed management copilot for hospital operations teams. |
| `FR-SOL-004` | The solution shall provide end-to-end operational visibility from admission through discharge, including outbound transitions to post-acute care. |
| `FR-SOL-005` | The solution shall integrate internal provider systems, external ecosystem endpoints, and reporting/analytics surfaces through a governed data platform. |

## Non-Functional Requirements

### Governance And Traceability

| ID | Requirement |
| -- | ----------- |
| `NFR-GOV-001` | All Copilot-driven changes shall remain traceable to repository-managed specifications and requirement IDs. |
| `NFR-GOV-006` | Every agent-authored issue response, PR, fixture, and change request shall reference the relevant `FR-*` and `NFR-*` identifiers from this document or explicitly refuse when they are absent. |

### Security And Access

| ID | Requirement |
| -- | ----------- |
| `NFR-SEC-001` | Active agents shall operate only through the MCP servers explicitly allow-listed in `.github/copilot/mcp.json`. |
| `NFR-SEC-002` | Azure interactions shall use least-privilege access and forbid destructive operations without explicit gated approval. |
| `NFR-SEC-003` | Secrets, tokens, and secret-like values shall never be echoed into issues, PRs, or committed artefacts. |

### Maintainability And Delivery

| ID | Requirement |
| -- | ----------- |
| `NFR-MAINT-001` | Agent contracts shall remain readable and maintainable as markdown-first assets in the repository. |
| `NFR-MAINT-002` | The active agent runtime shall remain GitHub Copilot coding agent plus repository prompts and MCP configuration, with no bespoke hosted agent service required. |

### Compliance And Data Governance

| ID | Requirement |
| -- | ----------- |
| `NFR-COMP-001` | The solution shall support compliance with Swiss DSG, cantonal governance constraints, and healthcare interoperability requirements. |
| `NFR-DATA-001` | The operational deployment model shall remain provider-internal and provider-governed, not a shared multi-provider tenancy. |
| `NFR-DATA-002` | External care partners shall be treated as integration endpoints rather than first-class platform operators. |

### Operational Performance And Reliability

| ID | Requirement |
| -- | ----------- |
| `NFR-PERF-001` | The solution architecture shall support near-real-time ingestion of ED, ADT, bed-state, and discharge-status signals. |
| `NFR-PERF-002` | Forecast inference shall support an operationally useful refresh cadence, with hourly refresh as the baseline target for the 72-hour forecast. |
| `NFR-PERF-003` | Discharge-readiness scoring shall support multiple recalculations during the day to reflect changing inpatient conditions. |
| `NFR-AVAIL-001` | The operational support capabilities shall be designed for continuous service rather than overnight batch-only operation. |
| `NFR-OPS-001` | The platform shall preserve explicit headroom for burst demand above average throughput. |

### Auditability And Responsible AI

| ID | Requirement |
| -- | ----------- |
| `NFR-AUD-001` | Forecasts, discharge scores, copilot answers, and outbound coordination triggers shall remain auditable to source context and execution time. |
| `NFR-AI-001` | The copilot layer shall remain advisory, with human operators retaining operational decision authority. |
| `NFR-AI-002` | The copilot layer shall be grounded in provider operational data and model outputs rather than unsupported free-form generation. |

## Traceability

| Source | Requirements derived |
| ------ | -------------------- |
| `docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform.md` | `FR-SOL-001` to `FR-SOL-005`, `NFR-COMP-001`, `NFR-DATA-001`, `NFR-DATA-002` |
| `docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform analysis.md` | `NFR-PERF-001` to `NFR-PERF-003`, `NFR-AVAIL-001`, `NFR-OPS-001`, `NFR-AUD-001`, `NFR-AI-001`, `NFR-AI-002` |
| Active GitHub agent contracts and templates | `FR-PLT-001` to `FR-PLT-005`, `FR-UC1-001` to `FR-UC1-008`, `FR-UC2-001` to `FR-UC2-007`, `FR-UC3-001` to `FR-UC3-003`, `NFR-GOV-001`, `NFR-GOV-006`, `NFR-SEC-001` to `NFR-SEC-003`, `NFR-MAINT-001`, `NFR-MAINT-002` |
