# Sprint 13 — App (Fluent UI primary + Rayfin PoC + Container Apps agent-host) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended — one subagent per task) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver Sprint 13's two-track React app + application-hosted agent-host backend per the design spec's T2 + M1 + H3 + Approach-C combination:

- `apps/hcc-app-fluent/` — Fluent UI v9 + Brandkit primary track
- `apps/hcc-app-rayfin/` — Rayfin parallel PoC (time-boxed to 3 engineering-days)
- `apps/hcc-agent-host/` — **Azure Container Apps backend** that loads Sprint 11 prompt manifests and dispatches to a Microsoft Foundry chat model per ADR-0008 + ADR-0007 (Redis + Cosmos wiring)
- Decision ADR at exit picking one of Fluent / Rayfin for Sprints 14+

**Architecture:** Sequential-ish tasks with parallelism where the dependency graph allows. Direct Lake semantic model preserved (owned by Sprint 09 v2). MSAL v2 for identity (frontend + server-side validation), OBO for Fabric token acquisition. Runtime posture per [ADR-0008](../../adr/0008-agent-runtime-pattern-scope-and-selection.md): application-hosted control plane, Foundry as model provider only. Design contract in [`docs/superpowers/specs/2026-07-09-sprint-13-app-design.md`](../specs/2026-07-09-sprint-13-app-design.md).

**Tech Stack:** React 18 + Fluent UI v9 (frontend), Vite build, TypeScript, MSAL for React v3, React Flow OR tldraw (whiteboard base — decided in T3 kickoff), @microsoft/microsoft-graph-client (Backstage Roles tab), Fluent theme derived from Brandkit tokens. Backend: Python (FastAPI) OR Node.js (Fastify) — decided in T5 kickoff based on Foundry chat-completion client SDK maturity and Semantic Kernel / OpenAI compatibility. Container Apps + Redis + Cosmos for backend. Rayfin PoC per its own tooling.

---

## Prerequisites (verify before starting)

- [ ] On `main` branch, clean of unrelated work: `git switch main; git pull`.
- [ ] Sprint 13 design spec merged and at v1.2.0 (from PR #148 + PR #155): `Get-Content docs/superpowers/specs/2026-07-09-sprint-13-app-design.md | Select-Object -First 15`.
- [ ] Sprint 11 agents merged (PR #149, #153, #155). Manifests at `agents/<name>/manifest.yaml` are the runtime contract T5 loads.
- [ ] Sprint 12 T1 (app registration) merged OR mockable — T2's MSAL wiring blocks on the real `ihzhhpf-app` client-id; T1/T3/T7 can start earlier.
- [ ] `az` CLI authenticated to the SIT tenant per ADR-0012.
- [ ] Node.js 20+ + npm 10+ available (Fluent app build).
- [ ] Python 3.11+ available (agent-host if we pick Python).
- [ ] `az bicep --version` ≥ 0.24.
- [ ] Fabric capacity `fabricihzhhpfsit` state = **Active** (needed for T5 Fabric integration + T8 semantic model embed test).
- [ ] Foundry `sprint11-chat` deployment reachable in `ai-ihzhhpf-sit` (blocked on T5 kickoff — see Task 5).
- [ ] `gh` CLI authenticated: `gh auth status`.
- [ ] Explicit go-ahead from @urruegg in the Sprint 13 kickoff issue thread.

---

## File Structure

Files created or modified across the ten tasks.

### T1 — Fluent app shell scaffold

- Create: `apps/hcc-app-fluent/package.json` — Vite + React 18 + TypeScript + Fluent UI v9.
- Create: `apps/hcc-app-fluent/tsconfig.json`, `vite.config.ts`, `index.html`.
- Create: `apps/hcc-app-fluent/src/main.tsx`, `src/App.tsx`.
- Create: `apps/hcc-app-fluent/src/shell/{TopBar,AppRail,WorkspaceRouter}.tsx`.
- Create: `apps/hcc-app-fluent/src/theme/helvion-theme.ts` — derived from [`data-platform/reports/capacity-dashboard.Report/themes/helvion-token-mapping.md`](../../../data-platform/reports/capacity-dashboard.Report/themes/helvion-token-mapping.md) landed in Power BI M1 (PR #152).
- Create: `apps/hcc-app-fluent/src/i18n/{de,en}.json` — DE default + EN fallback.
- Create: `apps/hcc-app-fluent/tests/unit/shell.test.tsx`, `tests/e2e/smoke.spec.ts` (Playwright).
- Create: `apps/hcc-app-fluent/Dockerfile` — multi-stage build, distroless base.
- Create: `.github/workflows/app-build.yml` — build + unit test both apps on PR.
- Create: `.github/workflows/app-e2e.yml` — Playwright smoke on push to main.
- Create: `.github/workflows/app-a11y.yml` — axe-core scan.
- Create: `apps/hcc-app-fluent/README.md`.
- Modify: `.github/CODEOWNERS` — add `/apps/hcc-app-fluent/` → @urruegg.

### T2 — MSAL auth + claim parsing

- Create: `apps/hcc-app-fluent/src/auth/{msal-provider,claim-parser,env-detection}.tsx`.
- Create: `apps/hcc-app-fluent/src/context/{hospital-context,role-context}.tsx`.
- Update: `apps/hcc-app-fluent/src/main.tsx` — wrap App in MSAL provider + context providers.
- Update: `apps/hcc-app-fluent/tests/unit/` — auth claim parsing tests.

### T3 — BedManager operational whiteboard (reference)

- Create: `apps/hcc-app-fluent/src/whiteboard/{Canvas,CardRegistry,LayoutManager}.tsx` — infinite-canvas component (React Flow or tldraw base; decided in T3 kickoff).
- Create: `apps/hcc-app-fluent/src/cards/{PowerBITile,AgentPanel,KpiCard,LiveStreamCard,ResponsibleCard,ScenarioCard}.tsx` — 6 card types per UX design §5.2.
- Create: `apps/hcc-app-fluent/src/workspaces/main/boards/bed-manager/BedManagerBoard.tsx` — the reference operational whiteboard.
- Create: `apps/hcc-app-fluent/src/workspaces/main/boards/bed-manager/mock-data.ts` — until real Fabric data lands via T6.
- Modify: `apps/hcc-app-fluent/src/theme/helvion-theme.ts` — extend with card-specific tokens.
- Create: mini-ADR `docs/adr/00XX-whiteboard-base-react-flow-vs-tldraw-vs-custom.md` — records the choice.

### T4 — Backstage Roles tab + navigation

- Create: `apps/hcc-app-fluent/src/workspaces/backstage/{BackstageRouter,Sidebar}.tsx`.
- Create: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/roles/RolesTab.tsx` — reads Entra Graph read-only via `@microsoft/microsoft-graph-client`.
- Create: `apps/hcc-app-fluent/src/shell/TopBar/HospitalSelector.tsx` — USZ / LUKS / Zollikerberg / Aggregated.
- Create: `apps/hcc-app-fluent/src/shell/TopBar/RoleSwitcher.tsx` — SIT-gated, requires `HCC.PlatformAdmin` or `HCC.DemoOperator`.

### T5 — Container Apps agent-host backend

**Biggest task. Substantial sub-scope.**

- Create: `apps/hcc-agent-host/pyproject.toml` OR `apps/hcc-agent-host/package.json` — Python (FastAPI + `azure-identity` + `openai` SDK against Foundry) OR Node (Fastify + `@azure/openai`) — decided in T5 kickoff.
- Create: `apps/hcc-agent-host/src/manifests/loader.py` — reads all `agents/<name>/manifest.yaml` at startup, validates against schema.
- Create: `apps/hcc-agent-host/src/orchestrator/dispatch.py` — composes system prompt + tools per manifest, calls Foundry chat completion, streams response.
- Create: `apps/hcc-agent-host/src/tools/{fabric,cosmos,github}_adapter.py` — MCP-server-flavoured tool adapters that wrap the actual SDKs.
- Create: `apps/hcc-agent-host/src/hitl/gate_enforcer.py` — HITL-01..HITL-05 middleware; deny-by-default before any side-effecting downstream action.
- Create: `apps/hcc-agent-host/src/cache/redis_client.py` — grounding + session cache.
- Create: `apps/hcc-agent-host/src/persistence/cosmos_client.py` — conversation, audit, approval-event containers per ADR-0007 §Implementation Notes.
- Create: `apps/hcc-agent-host/src/auth/token_validator.py` — MSAL server-side token validation + OBO for Fabric.
- Create: `apps/hcc-agent-host/src/http/app.py` — FastAPI/Fastify entry: `/agents/<name>/chat`, `/agents/<name>/tools/<tool>`, `/healthz`.
- Create: `apps/hcc-agent-host/tests/unit/` — one test file per module.
- Create: `apps/hcc-agent-host/tests/integration/test_bmca_end_to_end.py` — one integration test that loads the BMCA manifest, calls the mock Foundry model, asserts the response shape matches the golden-task fixture.
- Create: `apps/hcc-agent-host/Dockerfile`.
- Create: `infra/modules/agent-host/{main,container-app,redis,cosmos}.bicep` — Container App + Cache for Redis + Cosmos DB per ADR-0007.
- Modify: `.github/CODEOWNERS` — add `/apps/hcc-agent-host/` + `/infra/modules/agent-host/` → @urruegg.

### T6 — Copilot Drawer wiring (BMCA reference)

- Create: `apps/hcc-app-fluent/src/copilot-drawer/{Drawer,ConversationView,AgentInvoker}.tsx`.
- Create: `apps/hcc-app-fluent/src/copilot-drawer/agent-manifest.ts` — TypeScript type + fetch of the deployed agent list from the agent-host.
- Update: `apps/hcc-app-fluent/src/workspaces/main/boards/bed-manager/BedManagerBoard.tsx` — add "Ask BMCA" button that opens the drawer.
- Create: `apps/hcc-app-fluent/tests/integration/copilot-drawer-bmca.spec.ts` — Playwright test that opens the drawer, sends a canonical prompt, asserts a grounded reply and no PHI.

### T7 — Rayfin parallel PoC (time-boxed 3 eng-days)

- Create: `apps/hcc-app-rayfin/` — Rayfin CLI-generated skeleton.
- Reuse: `apps/hcc-app-fluent/src/theme/helvion-theme.ts` where possible.
- Reuse: `apps/hcc-app-fluent/tests/e2e/smoke.spec.ts` renamed for the Rayfin app.
- Create: `apps/hcc-app-rayfin/README.md` — Rayfin generation command, prompts used, deviations from Fluent baseline.
- Create: `docs/adr/00XX-app-stack-fluent-vs-rayfin-decision.md` — the exit ADR (drafted here, populated at T8).

### T8 — Decision ADR + retro

- Populate: `docs/adr/00XX-app-stack-fluent-vs-rayfin-decision.md` — evidence per rubric (design spec §4), recommendation, rollback path.
- Update: `docs/sprints/superpowers-checkpoint-matrix.md` — Sprint 13 row.
- Update: `docs/superpowers/specs/2026-07-09-sprint-13-app-design.md` — mark decision ADR link populated; bump MINOR.
- Close: Sprint 13 kickoff issue.

### Cross-cutting

- Modify: `.github/copilot/mcp.json` — if the agent-host adds new MCP servers, register them (unlikely; expected to reuse existing ones).

---

## Common per-task workflow (referenced by T1–T8)

Every task PR follows this skeleton.

- [ ] **Sub-step A: Branch off `main`**

```powershell
git switch main; git pull; git switch -c sprint-13/T<N>-<slug>
```

- [ ] **Sub-step B: Read the design spec section for this task**

Open [`docs/superpowers/specs/2026-07-09-sprint-13-app-design.md`](../specs/2026-07-09-sprint-13-app-design.md) §3 (repo layout) + §5 (agent + skill mix) + relevant task-specific sections.

- [ ] **Sub-step C: TDD — write the failing test first**

Every code change starts with a failing unit test or Playwright spec. For Bicep changes, `az deployment ... what-if` is the "failing test" (expected empty on first pass).

- [ ] **Sub-step D: Implement minimal code to pass the test**

Prefer smaller files with one clear responsibility per design spec §Design for isolation and clarity in the brainstorming skill.

- [ ] **Sub-step E: Run the full task-level test suite**

```powershell
# Fluent app
cd apps/hcc-app-fluent; npm test; npm run test:e2e; npm run test:a11y; cd ../..

# Agent-host (Python example)
cd apps/hcc-agent-host; pytest tests/; cd ../..
```

Expected: all pass. If any fail, iterate; do not push.

- [ ] **Sub-step F: For deploy-ceiling steps — post `what-if` + wait for `approved-to-apply`**

Applies to T5 (Container App + Redis + Cosmos provisioning) and any Container Apps redeploy. `what-if` output goes as a PR comment; @urruegg posts `approved-to-apply` per [AGENTS.md §4](../../../AGENTS.md#4-confirmation-rule-for-deploy--delete); only then does the apply run.

- [ ] **Sub-step G: Commit + push + open PR**

```powershell
git add apps/ infra/ .github/ docs/
git commit -m "feat(app): T<N> <slug> — <headline>"
git push -u origin sprint-13/T<N>-<slug>
gh pr create --base main --head sprint-13/T<N>-<slug> --title "feat(app): T<N> <slug>" --body-file <path> --label sprint-13 --label superpowers-execute
```

PR body follows [copilot-instructions.md §6](../../../.github/copilot-instructions.md) Output Contract.

- [ ] **Sub-step H: Wait for review + merge**

Merge unblocks the dependent tasks.

---

## Task 1 — T1: Fluent app shell scaffold

**Branch:** `sprint-13/T1-fluent-shell`  
**Depends on:** (none — can start immediately)

### Step 1.1 — Scaffold Vite + React 18 + TypeScript project

- [ ] **Step 1.1.1: Branch + init.**

```powershell
git switch main; git pull; git switch -c sprint-13/T1-fluent-shell
mkdir apps/hcc-app-fluent
cd apps/hcc-app-fluent
npm create vite@latest . -- --template react-ts
```

- [ ] **Step 1.1.2: Add Fluent UI v9 + MSAL react (T2 dependency-lite) + i18n.**

```powershell
npm install @fluentui/react-components @azure/msal-react @azure/msal-browser i18next react-i18next
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @axe-core/playwright @playwright/test
```

- [ ] **Step 1.1.3: Write failing test.**

Create `tests/unit/shell.test.tsx` asserting a `TopBar` component renders with the Helvion brand tokens and shows "Helvion" in the wordmark.

- [ ] **Step 1.1.4: Run it — expected FAIL.**

```powershell
npm test
```

Expected: FAIL because `TopBar` doesn't exist.

### Step 1.2 — Build shell scaffolding

- [ ] **Step 1.2.1: Create `src/shell/TopBar.tsx`** with the layout from UX design §3.2 — brand mark, hospital-context placeholder (T4 fills in real selector), search box, role-switcher placeholder, notifications, theme toggle, user Persona placeholder.
- [ ] **Step 1.2.2: Create `src/shell/AppRail.tsx`** — vertical rail with Main / Backstage / Home / Ask-Agent / Settings.
- [ ] **Step 1.2.3: Create `src/shell/WorkspaceRouter.tsx`** — routes for `/main/*` and `/backstage/*`; both placeholder for now (T3 fills Main, T4 fills Backstage).
- [ ] **Step 1.2.4: Create `src/App.tsx`** composing TopBar + AppRail + WorkspaceRouter.
- [ ] **Step 1.2.5: Create `src/theme/helvion-theme.ts`** — Fluent theme built from the Brandkit palette (Red `#E30613`, Blue `#365B7D`, Ink `#2E4C68`, Slate `#6B7A88`, Rainbow gradient).
- [ ] **Step 1.2.6: Run tests — expected PASS.**

### Step 1.3 — Playwright E2E scaffold + a11y

- [ ] **Step 1.3.1: Create `tests/e2e/smoke.spec.ts`** — opens the app, asserts TopBar visible, asserts app rail visible, asserts no console errors.
- [ ] **Step 1.3.2: Create `tests/e2e/a11y.spec.ts`** — axe-core scan on the home page. Zero violations at WCAG 2.1 AA.
- [ ] **Step 1.3.3: Run E2E — expected PASS.**

### Step 1.4 — Docker + CI workflows

- [ ] **Step 1.4.1: Create `Dockerfile`** — multi-stage build (node build → nginx serve). Distroless base.
- [ ] **Step 1.4.2: Create `.github/workflows/app-build.yml`.**
- [ ] **Step 1.4.3: Create `.github/workflows/app-e2e.yml`.**
- [ ] **Step 1.4.4: Create `.github/workflows/app-a11y.yml`.**
- [ ] **Step 1.4.5: Modify `.github/CODEOWNERS`** — add `/apps/hcc-app-fluent/` line.

### Step 1.5 — PR

- [ ] **Step 1.5.1: Commit + push + open PR** (Sub-step G).
- [ ] **Step 1.5.2: Confirm all 3 workflows green on the PR.**
- [ ] **Step 1.5.3: Wait for merge.**

**DoD:** Fluent app shell scaffolded, tests green, Docker image builds, 3 CI workflows operational.

---

## Task 2 — T2: MSAL auth + claim parsing

**Branch:** `sprint-13/T2-msal-auth`  
**Depends on:** T1 merged. **Sprint 12 T1 (app registration) merged.**

Follow the [Common per-task workflow](#common-per-task-workflow-referenced-by-t1t8). Task-specific specifics:

- MSAL client-id sourced from a per-slot config (SIT slot uses `ihzhhpf-app` client-id from Sprint 12 T1's output; PROD slot same).
- Parse `roles`, `hospital`, `env` claims into TypeScript types.
- Provide React context providers so any component can read `useCurrentRole()`, `useCurrentHospital()`, `useCurrentEnv()`.
- Env detection: read slot config OR host header pattern (`app-platform-ihzhhpf-sit-y26y.azurewebsites.net` → `sit`; PROD equivalent → `prod`).

**Tests:**
- Unit: claim parsing round-trips for all Sprint 12 personas (SuperAdmin, GuestReadOnly, BedManager USZ, etc.).
- E2E: sign in as `demo.guest` → land on Home → verify RLS-proof pill reads `Viewing: Aggregated • HCC.GuestReadOnly`.

**DoD:**
- [ ] `demo.guest` can sign in and land on Home with the correct claim signals.
- [ ] Role switcher is HIDDEN unless `env=sit` AND caller has `HCC.PlatformAdmin` or `HCC.DemoOperator`.

---

## Task 3 — T3: BedManager operational whiteboard (reference)

**Branch:** `sprint-13/T3-bedmanager-whiteboard`  
**Depends on:** T1 merged. Parallel-safe with T2.

### Step 3.1 — Choose whiteboard base

- [ ] **Step 3.1.1: Read the whiteboard-base decision guidance from the design spec §5.**
- [ ] **Step 3.1.2: Draft `docs/adr/00XX-whiteboard-base.md`** comparing React Flow vs tldraw vs custom. Recommend one; document rationale.
- [ ] **Step 3.1.3: Install the chosen library.**

### Step 3.2 — Whiteboard framework

- [ ] **Step 3.2.1: Write failing tests** for the `Canvas`, `CardRegistry`, `LayoutManager` components — assert cards can be added, moved (in-memory), and re-rendered.
- [ ] **Step 3.2.2: Implement `src/whiteboard/Canvas.tsx`.**
- [ ] **Step 3.2.3: Implement `src/whiteboard/CardRegistry.tsx`.**
- [ ] **Step 3.2.4: Implement `src/whiteboard/LayoutManager.tsx`** — in-memory only for Sprint 13; persistence lands in a follow-up sprint.

### Step 3.3 — 6 card types

For each of the 6 card types (`PowerBITile`, `AgentPanel`, `KpiCard`, `LiveStreamCard`, `ResponsibleCard`, `ScenarioCard`):

- [ ] Write failing test.
- [ ] Implement component.
- [ ] Pass test.

Each card uses mock data during Sprint 13; real Fabric wiring is Sprint 14+ scope.

### Step 3.4 — BedManager reference board

- [ ] **Step 3.4.1: Create `src/workspaces/main/boards/bed-manager/BedManagerBoard.tsx`** — composes 6 cards per UX design §5.1 example (occupancy KPI, 72-h pressure, discharge candidates, responsible/on-call, ED arrivals, scenario card).
- [ ] **Step 3.4.2: Playwright test** — navigate to `/main/bed-manager`, assert all 6 cards visible with mock content.

**DoD:**
- [ ] All 6 card types render.
- [ ] BedManager reference board visible at `/main/bed-manager`.
- [ ] Whiteboard-base ADR merged.

---

## Task 4 — T4: Backstage Roles tab + navigation

**Branch:** `sprint-13/T4-backstage-roles`  
**Depends on:** T2 merged. Uses Sprint 12 T2 identities (app roles must exist).

- Backstage router + sidebar with Roles / Ontology / Agents / Processes / Data-Contracts / KPI-catalog / Environment tabs (only Roles is populated in Sprint 13).
- Roles tab reads Entra Graph `/servicePrincipals/{ihzhhpf-app-id}?$select=appRoles` and `/servicePrincipals/{ihzhhpf-app-id}/appRoleAssignedTo` — displays the 15 app roles + 23 personas with their assignment.
- Hospital-context selector wired into TopBar with the 4 hospital options.
- Role switcher wired: SIT + PlatformAdmin/DemoOperator → visible; anyone else → hidden.

**Tests:**
- Playwright: sign in as `demo.guest` → Backstage tab visible but Roles content is aggregated-only view (no per-person data leaks).
- Playwright: sign in as `super.admin` → Roles tab shows all 23 personas with their app-role.

**DoD:**
- [ ] Roles tab renders 15 app roles + 23 personas from live Entra Graph read.
- [ ] Hospital selector operational (still mock filter until Fabric data wires in T6).

---

## Task 5 — T5: Container Apps agent-host backend

**Branch:** `sprint-13/T5-agent-host`  
**Depends on:** Sprint 11 agents (manifests exist under `agents/<name>/manifest.yaml`). T2 (MSAL claim shape). Sprint 12 T1 (app registration for OBO).

**BIGGEST TASK.** May be split into sub-PRs at execution time. The plan below is the shape.

### Step 5.1 — Choose language + framework

- [ ] Compare Python (FastAPI + `openai` SDK against Foundry chat completion) vs Node (Fastify + `@azure/openai`).
- [ ] Recommend one; document in a mini-ADR under `docs/adr/00XX-agent-host-runtime.md`.

Recommendation reasoning to weigh: Python has stronger Semantic Kernel + Foundry Agent Service SDKs and MCP-adjacent libraries (though we're not using MCP servers *directly* at runtime — the manifests declare MCP tool shapes and the host adapts them into real SDK calls). Node has better TypeScript type sharing with the frontend. **Suggested default: Python + FastAPI** — the Python Foundry chat-completion SDK is mature, and the backend is small enough that TS type sharing isn't a big win.

### Step 5.2 — Manifest loader + orchestrator

- [ ] TDD: write test that loads `agents/bmca-agent/manifest.yaml`, asserts fields (agent, modelDeploymentRef, systemPromptRef, mcpTools, hitl, grounding) parse correctly.
- [ ] Implement `src/manifests/loader.py`.
- [ ] TDD: write test that dispatches a canonical BMCA prompt to a **mock Foundry client** and asserts the response shape matches the golden-task fixture.
- [ ] Implement `src/orchestrator/dispatch.py`.

### Step 5.3 — MCP-flavoured tool adapters

- [ ] Implement `src/tools/fabric_adapter.py` — wraps the Fabric REST API for `fabric-mcp.query(table, filter)` calls. Uses OBO token for user-scoped queries.
- [ ] Implement `src/tools/cosmos_adapter.py` — wraps Cosmos SDK for `cosmos-mcp` shape (empty in Sprint 13; used in Sprint 16 by csa-agent).
- [ ] Implement `src/tools/github_adapter.py` — wraps the GitHub REST/GraphQL for `github-mcp` shape.

### Step 5.4 — HITL gate enforcer

- [ ] Implement `src/hitl/gate_enforcer.py` — middleware that inspects any outgoing tool call. If tool ceiling is `deploy` or `delete`, blocks and returns `HITL-<gate>` refusal. Gate mapping loaded from each manifest's `hitl.gates`.
- [ ] TDD: test that a mock `deploy`-ceiling call is denied with a HITL-01 or HITL-02 refusal.

### Step 5.5 — Redis cache + Cosmos persistence

- [ ] Implement `src/cache/redis_client.py` — grounding cache with TTL from ADR-0007 (defaults to 15 min).
- [ ] Implement `src/persistence/cosmos_client.py` — three containers per ADR-0007 §Implementation Notes: `conversations`, `audit`, `approval-events`.

### Step 5.6 — MSAL server-side auth + OBO

- [ ] Implement `src/auth/token_validator.py` — validates incoming MSAL access tokens against `ihzhhpf-app` audience, extracts claims, acquires OBO for Fabric on the user's behalf.

### Step 5.7 — HTTP surface

- [ ] Implement `src/http/app.py` — FastAPI app with:
  - `POST /agents/{name}/chat` — accepts a prompt, returns streaming response.
  - `POST /agents/{name}/tools/{tool}` — direct tool invocation (used by the drawer's "Suggest" button).
  - `GET /healthz` — health probe for Container Apps.

### Step 5.8 — Container Apps infrastructure

- [ ] Create `infra/modules/agent-host/main.bicep` — subscription-scope wrapper.
- [ ] Create `infra/modules/agent-host/container-app.bicep` — Container Apps environment + one app for `hcc-agent-host`. Uses managed identity + Workload Identity Federation.
- [ ] Create `infra/modules/agent-host/redis.bicep` — Azure Cache for Redis (Standard C0 tier is enough for demo).
- [ ] Create `infra/modules/agent-host/cosmos.bicep` — Cosmos DB account with three containers per ADR-0007. Note: this Cosmos is SEPARATE from the Sprint 16 CSA scenarios Cosmos.
- [ ] Create `infra/modules/agent-host/parameters/sit.bicepparam` (+ prod placeholder).
- [ ] `az deployment sub what-if`; post to PR; wait for `approved-to-apply`; apply.

### Step 5.9 — Integration test end-to-end

- [ ] Integration test `tests/integration/test_bmca_end_to_end.py`:
  - Load BMCA manifest.
  - Invoke `/agents/bmca-agent/chat` with the happy-path fixture prompt.
  - Assert response shape matches `agents/bmca-agent/golden-tasks.md` happy-path expectations.
  - Assert no PHI-shaped strings in the response.

**DoD:**
- [ ] `hcc-agent-host` deployed to Container Apps SIT.
- [ ] Loads all 7 Sprint 11 user-facing manifests at startup (BMCA + OOA + DCA + ORSA + SBA + CSA-scaffold + data-quality; skips onboarding as it's workflow-triggered per its manifest `runtime: workflow`).
- [ ] BMCA end-to-end integration test green.
- [ ] Redis instance provisioned; agent-host reads/writes grounding entries.
- [ ] Cosmos three containers provisioned; conversation persisted; audit event emitted.
- [ ] HITL-01..HITL-05 gate scaffolding in place with deny-by-default posture.

---

## Task 6 — T6: Copilot Drawer wiring (BMCA reference)

**Branch:** `sprint-13/T6-copilot-drawer`  
**Depends on:** T3 (BedManager board) + T5 (agent-host) merged.

- Create Copilot Drawer component with conversation view and input.
- On user submit, call `/agents/bmca-agent/chat` from the agent-host.
- Render streamed response with proper redaction of any PHI-shaped strings.
- Contract test: canonical prompt → grounded reply with citation footer.

**DoD:**
- [ ] Copilot Drawer opens from BedManager board's "Ask BMCA" button.
- [ ] End-to-end demo: user asks "Which patients on ward 3B are the strongest discharge candidates?" → BMCA response includes the ranked list, no PHI, citation footer.

---

## Task 7 — T7: Rayfin parallel PoC (time-boxed 3 eng-days)

**Branch:** `sprint-13/T7-rayfin-poc`  
**Depends on:** T1 merged (need Helvion theme tokens to reuse). Parallel-safe with T2-T6.

- Rayfin generates `apps/hcc-app-rayfin/` skeleton using the Helvion tokens and a Rayfin prompt that describes the same shell + BedManager whiteboard.
- Time-box: **3 engineering-days from PR open**. If the PoC has not produced a comparable output by then, stop and record "not evaluable in scope" in the exit ADR.
- Same Playwright smoke test used to prove parity (sign in with `demo.guest`, land on Home, see Bed Manager card cluster).

**DoD:**
- [ ] Rayfin app builds in CI.
- [ ] Playwright smoke passes OR the "not evaluable in scope" note is recorded.
- [ ] Comparison evidence per the design spec §4 rubric is collected.

---

## Task 8 — T8: Decision ADR + retro

**Branch:** `sprint-13/T8-retro`  
**Depends on:** T4, T6, T7 merged.

- Populate `docs/adr/00XX-app-stack-fluent-vs-rayfin-decision.md` with:
  - Recommendation (Fluent or Rayfin — expected: Fluent, but evidence-driven).
  - Evidence per criterion from the rubric.
  - Dissent notes.
  - Rollback path.
- Update `docs/sprints/superpowers-checkpoint-matrix.md` — Sprint 13 row.
- Update `docs/superpowers/specs/2026-07-09-sprint-13-app-design.md` — mark exit ADR link populated; bump MINOR.
- Close Sprint 13 kickoff issue with a retro comment.

**DoD:**
- [ ] Exit ADR merged.
- [ ] Checkpoint matrix entry landed.
- [ ] Sprint 13 kickoff issue closed.

---

## Definition of Sprint 13 done (mirrors design spec §11)

- [ ] `apps/hcc-app-fluent/`, `apps/hcc-app-rayfin/`, and `apps/hcc-agent-host/` all build in CI.
- [ ] Fluent app deployed to Container Apps SIT slot with MSAL sign-in verified.
- [ ] `hcc-agent-host` deployed to Container Apps SIT; loads BMCA manifest at startup.
- [ ] BedManager whiteboard renders 6 card types with mock data.
- [ ] Backstage Roles tab renders live app-role list from Entra Graph (read-only).
- [ ] Copilot Drawer invokes BMCA via the agent-host and shows a grounded reply for one canonical prompt.
- [ ] Redis cache instance provisioned; agent-host reads/writes grounding entries per ADR-0007.
- [ ] Cosmos DB `conversations`, `audit`, `approval-events` containers provisioned per ADR-0007 §Implementation Notes.
- [ ] HITL-01..HITL-05 gate scaffolding in place (gate-check middleware; enforcement bodies stubbed with a deny-by-default posture; positive gate wiring lands per agent in follow-up sprints).
- [ ] `app-build.yml`, `app-e2e.yml`, `app-a11y.yml` workflows green.
- [ ] Decision ADR merged and recommends one stack for Sprint 14+.
- [ ] Sprint 13 retro entry in [`docs/sprints/superpowers-checkpoint-matrix.md`](../../sprints/superpowers-checkpoint-matrix.md).

---

## Parallelism map (for the cloud coding agent's subagent scheduling)

```
T1 (shell) ──┬──▶ T3 (whiteboard) ──┬──▶ T6 (drawer wiring)
             │                       │
             └──▶ T2 (MSAL auth) ────┴──▶ T4 (Backstage Roles)
                                     │
             └──▶ T7 (Rayfin PoC) ───┴──▶ T8 (exit ADR + retro)

T5 (agent-host) starts in parallel from T1;
its DoD depends on Sprint 12 T1 (app registration) for OBO.
T5 → T6 blocks (drawer needs the /chat endpoint).
```

**Sprint 12 dependencies flagged (per task):**
- T2 blocks on Sprint 12 T1 (app registration client-id).
- T4 blocks on Sprint 12 T2 (13 app roles) + T4 Batch A (super/demo/guest personas).
- T5 blocks on Sprint 12 T1 (app registration for OBO).

If Sprint 12 T1 lands quickly, most of Sprint 13 unblocks.

---

## Self-Review

**1. Spec coverage.** Every Sprint 13 design-spec §11 Definition-of-done bullet maps to at least one task:
- Fluent app + shell → T1.
- MSAL auth → T2.
- BedManager whiteboard → T3.
- Backstage Roles tab → T4.
- Agent-host with all its wiring → T5.
- Copilot Drawer → T6.
- Rayfin PoC → T7.
- Exit ADR + retro → T8.

**2. Placeholder scan.** No `TBD` / `TODO`. Deliberate parametrics: `<N>`, `<slug>`, ADR number `00XX` (assigned at ADR creation). Whiteboard-base + agent-host-language decisions deferred to task kickoffs with explicit mini-ADRs.

**3. Type consistency.** Path conventions: `apps/hcc-app-fluent/`, `apps/hcc-app-rayfin/`, `apps/hcc-agent-host/`. Branch prefix `sprint-13/T<N>-<slug>`. Container Apps resource names follow the Azure resource pattern (`ca-agent-host-ihzhhpf-sit` etc.) per copilot-instructions §8.

**4. Approval gates.** Only T5 has `deploy`-ceiling steps (Container Apps + Redis + Cosmos provisioning). One `approved-to-apply` gate per Bicep deployment.

**5. Dependencies clean.** T1 → T2/T3/T5/T7 parallel. T4 needs T2. T6 needs T3 + T5. T8 needs T4 + T6 + T7. Sprint 12 T1 unblocks T2/T4/T5. No cycles.

**6. Rayfin time-box.** T7 explicitly time-boxed to 3 eng-days; if not evaluable, records that fact in the exit ADR. Doesn't block T8.

---

## Execution Handoff

Plan complete and will be saved to `docs/superpowers/plans/2026-07-09-sprint-13-app-plan.md`. Two execution options:

1. **GitHub Copilot cloud coding agent (recommended)** — matches Sprint 11 + Sprint 12 pattern. Assign the accompanying kickoff issue to Copilot in the GitHub UI. The cloud agent authors T1–T8 as separate PRs, respecting the parallelism map above.
2. **Inline execution here** — the chat session executes one task at a time.

**Which approach?** — my recommendation is the cloud agent again (proven three times: PR #149, #152, #156).
