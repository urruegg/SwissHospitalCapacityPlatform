# Superpowers Checkpoint Matrix (Shared)

| Field | Value |
| ----- | ----- |
| **Version** | 1.2.0 |
| **Date** | 2026-07-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 1.1.0 (new shared matrix baseline) |

## Purpose

Provide one reusable checkpoint matrix for all sprint executions that use
Superpowers as mandatory operating mode.

## Stage and Gate Matrix

| Stage | Checkpoint | Pass Criteria | Evidence |
| ----- | ----- | ----- | ----- |
| brainstorming | Design brief approved | Alternatives and acceptance criteria documented | Link to issue comment or artifact |
| using-git-worktrees | Worktree isolation complete | One worktree per major slice and clean baseline check | Terminal output or note |
| writing-plans | Plan quality gate | Tasks include files, verification, requirement mapping | Plan artifact link |
| execution | Spec compliance review | No unresolved critical spec deviation | Review note link |
| execution | Quality review | No unresolved critical quality defect | Review note link |
| execution | Systematic debugging gate | Debug workflow evidence exists for any failure/regression path | Debug log link |
| test-driven-development | Validation proof | RED-GREEN evidence or test-first checklist attached | Test output link |
| requesting-code-review | Severity gate | Critical findings resolved or accepted by owner | Review summary link |
| finishing-a-development-branch | Verification-before-completion | Final verification evidence attached before completion claim | Verification output link |
| finishing-a-development-branch | Closeout gate | PR contract complete and branch decision recorded | PR link |

## Cross-Cutting Governance Checks

| Check | Pass Criteria | Evidence |
| ----- | ----- | ----- |
| Traceability | FR/NFR IDs explicit in issue and PR | Issue + PR links |
| Sprint traceability chain | Issue exists first and PR follows with backlink | Issue + PR links |
| Core skill evidence | PR includes applicability and evidence for core Superpowers skills | PR section |
| Compliance impact | Compliance impact statement included | PR section |
| Security impact | Security impact statement included | PR section |
| Deploy/delete guardrail | `approved-to-apply` used where applicable | PR/issue comment |
| Required checks | Lint/test/policy checks pass for scope | Command output links |

## Sprint Execution Log

Per-sprint closeout entries. Each row records the Superpowers-cycle outcome for a
sprint executed under this matrix.

| Sprint | Start | End | Status | Agents shipped | Evals green | Design spec | Plan |
| ------ | ----- | --- | ------ | -------------- | ----------- | ----------- | ---- |
| 11 | 2026-07-09 | 2026-07-09 | Merged | 8/8 (7 MVP + 1 stretch) | Yes | [`../superpowers/specs/2026-07-09-sprint-11-agents-design.md`](../superpowers/specs/2026-07-09-sprint-11-agents-design.md) | [`../superpowers/plans/2026-07-09-sprint-11-agents-plan.md`](../superpowers/plans/2026-07-09-sprint-11-agents-plan.md) |
| 13 | 2026-07-09 | 2026-07-09 | In review | n/a (app tier) | Yes | [`../superpowers/specs/2026-07-09-sprint-13-app-design.md`](../superpowers/specs/2026-07-09-sprint-13-app-design.md) | [`../superpowers/plans/2026-07-09-sprint-13-app-plan.md`](../superpowers/plans/2026-07-09-sprint-13-app-plan.md) |

### Sprint 11 retro notes

- All 8 agents (`bmca-agent`, `ooa-agent`, `dca-agent`, `orsa-agent`,
  `sba-agent`, `csa-agent` scaffold, `data-quality-agent`, `onboarding-agent`
  stretch) shipped with prompt file, ≥ 2 golden-task fixtures, runtime
  `manifest.yaml`, `agents/` compatibility stub, and an `AGENTS.md` §1 row.
- Model selection recorded in
  [`../adr/0020-sprint11-agent-model-selection.md`](../adr/0020-sprint11-agent-model-selection.md)
  and referenced by every agent.
- `fabric-mcp` and `entra-mcp` (read-only) added to
  [`../../.github/copilot/mcp.json`](../../.github/copilot/mcp.json) and
  `AGENTS.md` §2.
- Golden-task fixtures replayed structurally via
  [`../../.github/workflows/eval-goldens.yml`](../../.github/workflows/eval-goldens.yml).
- No Foundry Agent Service deployment (application-hosted per ADR-0008); the
  Sprint 13 Container Apps agent-host loads the manifests at runtime.
- `csa-agent` is a scaffold only — the Prepare phase is stubbed and the
  Run/Evaluate/Recommend body lands in Sprint 16. The Sprint 09 runtime pack at
  `agents/csa-agent/` was left intact.

### Sprint 13 retro notes

- **App tier delivered** across T1–T8: `apps/hcc-app-fluent/` (Fluent UI v9
  baseline), `apps/hcc-agent-host/` (Python + FastAPI Container Apps agent-host,
  [ADR-0022](../adr/0022-agent-host-language-python-fastapi.md)), and
  `apps/hcc-app-rayfin/` (PoC placeholder).
- **Fluent baseline** (T1–T4, T6): two-workspace shell, MSAL auth with
  `roles`/`hospital`/`env` claim parsing + SIT-gated role switcher, BedManager
  whiteboard with 6 card types over a custom canvas
  ([ADR-0021](../adr/0021-whiteboard-base-react-flow-vs-tldraw-vs-custom.md)),
  Backstage Roles tab (read-only Entra Graph), Copilot Drawer wired to BMCA.
  20 vitest unit tests + Playwright smoke/a11y/contract green; `app-build.yml`,
  `app-e2e.yml`, `app-a11y.yml` added.
- **Agent-host** (T5): manifest loader, orchestrator + Fabric grounding,
  deny-by-default HITL gate (ADR-0007 §6 schema), redaction, tool adapters,
  in-memory Cosmos/Redis stand-ins, FastAPI surface (`/agents`,
  `/agents/<name>/chat`, `/agents/<name>/tools/<tool>`, `/healthz`). 31 pytest
  tests green; `agent-host-build.yml` added; Bicep authored under
  `infra/modules/agent-host/` (`az bicep build` clean, **not deployed**).
- **Live deploys deferred**: T5's Container Apps + Redis + Cosmos provisioning is
  a `deploy`-ceiling action requiring the AGENTS.md §4 `approved-to-apply` gate,
  which was not exercised in this delivery. The Bicep is authored and validated
  but no Azure resources were created; the app + agent-host run on deterministic
  mocks + in-memory persistence in CI.
- **Rayfin PoC — not evaluable in scope** (T7): the proprietary Rayfin generator
  was not runnable in the environment. Recorded per the T7 time-box rule; the
  exit decision ADR
  [ADR-0023](../adr/0023-app-stack-fluent-vs-rayfin-decision.md) recommends the
  **Fluent** baseline for Sprint 14+.
