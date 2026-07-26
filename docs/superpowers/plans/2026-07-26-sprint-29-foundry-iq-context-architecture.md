# Foundry IQ Context Architecture (Sprint 29) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Sprint 29 runs in **one dedicated git worktree + Copilot CLI session** per [`docs/runbooks/sprint-29-worktree-delegation.md`](../../runbooks/sprint-29-worktree-delegation.md).

**Goal:** Make the app's three context tiers — **user**, **agent**, **grounding** — consistent by construction. Every IQ read and agent turn carries one `ContextEnvelope`; each board-agent keeps its own conversation thread; per-user data scope (RLS) + OBO are designed and *simulated*, config-gated to lift to live SIT without code edits.

**Governing issue:** [#399](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/399). **Design:** [`2026-07-26-sprint-29-foundry-iq-context-architecture-design.md`](../specs/2026-07-26-sprint-29-foundry-iq-context-architecture-design.md).

**Scope surface:** `apps/hcc-app-fluent` (TypeScript / React / Fluent v9), plus one ADR + PRD rows. **No infra provisioning** this sprint; demo stays synthetic, **no PHI**.

---

## Hard constraints (apply to every task)

- **Runtime `python`, not `python3`** for any script/lint command.
- **Commit with hooks disabled if needed:** `git -c core.hooksPath=/dev/null commit -m "..."`.
- **Synthetic / no-PHI only** (ADR-0016); westus2 demo scope (ADR-0013); region-agnostic config (ADR-0035).
- **No infra apply.** This sprint provisions nothing. All live wiring (Foundry threads, Fabric RLS, OBO endpoints) is **simulated + config-gated** and captured as a SIT follow-up (Approach B).
- **Human always reviews + merges every PR. Never self-merge.** One small PR per milestone slice, each linked to issue #399.
- **Trunk-based per ADR-0038:** short-lived branch off `main`; branch names `sprint-29/<milestone>-<slice>` within the one worktree.
- **Doc edits** follow copilot-instructions §9 + the `document-authoring` skill; mojibake/lint gates enforced by CI.
- **App gates are the acceptance bar:** `npm --prefix apps/hcc-app-fluent run lint && npm --prefix apps/hcc-app-fluent run build && npm --prefix apps/hcc-app-fluent test`, plus the Playwright smoke + `@axe-core/playwright` a11y suites where UI changes (route UX/a11y questions through the `ux-design-agent`).
- **Preserve provenance + citations** (ADR-0044): never emit an uncited/ungrounded claim; fail-loud `GroundingNotice` on degrade.

## Milestone dependency order (single worktree)

```text
M0 ContextEnvelope type + builder ── foundation ──┐
                                                  ▼
        M1 per-(user x agent) threads      M2 first-eligible default board   (parallel-safe)
                                                  │
                                                  ▼
        M3 envelope propagation through iq-client (simulated headers + guard)
                                                  │
                                                  ▼
        M4 Foundry thread-per-(user x agent) map (config-gated)
                                                  │
                                                  ▼
        M5 OBO / RLS contract + simulated per-user scope + golden tests (+ ADR)
                                                  │
                                                  ▼
                                   M6 docs + PRD/traceability + closeout
```

M0 first. M1 + M2 are independent and may be done in either order (or back-to-back). M3 depends on M0. M4 depends on M3. M5 depends on M3/M4. M6 last.

## Existing files to mirror / modify (verified paths)

- User context: `apps/hcc-app-fluent/src/context/role-context.tsx`, `apps/hcc-app-fluent/src/auth/rbac-model.ts`.
- Shared agent thread (Q2 bleed source): `apps/hcc-app-fluent/src/copilot-drawer/AgentInvoker.ts`, `apps/hcc-app-fluent/src/copilot-drawer/ConversationView.tsx`.
- Agent-per-board wiring: `apps/hcc-app-fluent/src/shell/planes/AgentPlane.tsx`, `apps/hcc-app-fluent/src/shell/planes/agent-context-map.ts`.
- Board registry / default board (Q1): `apps/hcc-app-fluent/src/shell/planes/board-registry.ts`, `apps/hcc-app-fluent/src/workspaces/main/MainView.tsx`, `apps/hcc-app-fluent/src/workspaces/start/role-launcher.ts`.
- Data-access gateway (ADR-0044 ingress): `apps/hcc-app-fluent/src/data/roleboard/golden-source-client.ts`.
- Provenance: `apps/hcc-app-fluent/src/cards/evidence/_provenance.tsx`.
- Hospital scope: `apps/hcc-app-fluent/src/shell/TopBar/HospitalScopeSelector.tsx`.

> Confirm each path at execution (`git grep`) before editing; the agent must read the target file before modifying it.

---

## M0 — `ContextEnvelope` type + builder (branch `sprint-29/m0-envelope`)

> Foundation. Publishes the single object every IQ read/agent turn carries.

### Task M0.1: Type + builder (TDD)

**Files:** Create `apps/hcc-app-fluent/src/context/context-envelope.ts` (+ `tests/unit/context-envelope.test.ts`)

- [ ] **Step 1 — Failing test:** `context-envelope.test.ts`: given mock claims (`oid`, `roles`), an active role lens, a hospital scope, and a data-source pref, assert `buildEnvelope(...)` returns `{ userOid, heldRoles, activeRole, hospitalScope, dataSource, agent, windowHours }` with correct values; assert missing claims → least-privilege fallback (`activeRole = Viewer`, aggregated `hospitalScope`).
- [ ] **Step 2 — Run test:** `npm --prefix apps/hcc-app-fluent test -- context-envelope` → **FAIL**.
- [ ] **Step 3 — Implement:** `ContextEnvelope` type + `buildEnvelope(claims, lens, hospital, dataSource, agent)`; derive from the existing `role-context` + `rbac-model` shapes (read those first). Pure function, no I/O.
- [ ] **Step 4 — Run tests:** `npm --prefix apps/hcc-app-fluent test -- context-envelope` → **PASS**.
- [ ] **Step 5 — Gates + commit:** `npm --prefix apps/hcc-app-fluent run lint && npm --prefix apps/hcc-app-fluent run build`; `git commit -am "feat(app): ContextEnvelope type + buildEnvelope (#399)"`.

**Acceptance gate:** envelope built correctly from claims + active role; least-privilege fallback proven; lint + build + unit green.

---

## M1 — Per-(user×agent) conversation scoping (branch `sprint-29/m1-conversation`)

> Fixes the cross-agent chat bleed (design Q2).

### Task M1.1: `useConversation(agent)` + `ConversationStore` (TDD)

**Files:** Create `apps/hcc-app-fluent/src/copilot-drawer/useConversation.ts` + `conversation-store.ts` (+ test); Modify `AgentInvoker.ts` / `ConversationView.tsx` consumers

- [ ] **Step 1 — Failing test:** assert switching `agent` shows *that* agent's own turn list and never leaks turns across agents; assert sign-out resets all threads.
- [ ] **Step 2 — Run test:** `npm --prefix apps/hcc-app-fluent test -- useConversation` → **FAIL**.
- [ ] **Step 3 — Implement:** `ConversationStore` keyed by `agent` (structured so the key can extend to `userOid×agent` in M4); `useConversation(agent)` replacing the single shared invoker turn list; clean reset on sign-out. Read `AgentInvoker.ts` + `agent-context-map.ts` first; keep the `AgentPlane` render contract intact.
- [ ] **Step 4 — Run tests:** unit green; run the Playwright shell smoke to confirm no regression in the drawer.
- [ ] **Step 5 — Gates + commit:** lint + build; `git commit -am "feat(app): per-(user x agent) conversation scoping (#399)"`.

**Acceptance gate:** per-agent thread isolation proven; sign-out reset proven; no drawer regression; gates green.

---

## M2 — First-eligible default board (branch `sprint-29/m2-default-board`)

> Fixes the hard-coded `bed-manager` default (design Q1).

### Task M2.1: `firstEligibleBoard(capabilities)` (TDD)

**Files:** Create `apps/hcc-app-fluent/src/shell/planes/first-eligible-board.ts` (+ test); Modify `MainView.tsx` / `role-launcher.ts`

- [ ] **Step 1 — Failing test:** given roles with different `nav` capabilities, assert `firstEligibleBoard()` returns the first board in patient-journey order (`occupancy → bed-manager → or-steering → staffing → discharge → crisis`) the role can see; assert a role that cannot see `bed-manager` never defaults to it.
- [ ] **Step 2 — Run test:** `npm --prefix apps/hcc-app-fluent test -- first-eligible-board` → **FAIL**.
- [ ] **Step 3 — Implement:** `firstEligibleBoard(capabilities)` reading the `board-registry` order + the role `nav` gates; wire into `MainView`/`/main` default (replace the hard-coded `bed-manager`).
- [ ] **Step 4 — Run tests:** unit green; update the e2e that asserts the default board (`tests/e2e/shell.spec.ts` or parity) to the role-first-eligible expectation.
- [ ] **Step 5 — Gates + commit:** lint + build + Playwright smoke; `git commit -am "feat(app): role-first-eligible default board (#399)"`.

**Acceptance gate:** `/main` opens the first patient-journey board the role can see; no role hard-defaults to a board it cannot access; e2e updated + green.

---

## M3 — Envelope propagation through `iq-client` (branch `sprint-29/m3-propagation`)

> Attaches the envelope to every IQ call; extends the single-ingress guard.

### Task M3.1: Scoped headers + guard (TDD)

**Files:** Modify `apps/hcc-app-fluent/src/data/roleboard/golden-source-client.ts` (the ADR-0044 ingress); Create a guard test

- [ ] **Step 1 — Failing test:** (a) assert every gateway call attaches the envelope as scoped headers (`X-User-Oid`, `X-Hospital-Scope`, `X-Active-Role`) — simulated in demo; (b) **guard test:** an IQ call issued *without* a `ContextEnvelope` **fails** (extends the existing single-ingress guard).
- [ ] **Step 2 — Run test:** `npm --prefix apps/hcc-app-fluent test -- iq-envelope` → **FAIL**.
- [ ] **Step 3 — Implement:** extend the gateway to accept a `ContextEnvelope` and attach the headers on every Fabric Data Agent + Foundry call; `simulated` provenance when endpoints are not configured (no silent "live"). Keep provenance/citation tagging intact.
- [ ] **Step 4 — Run tests:** unit + guard green.
- [ ] **Step 5 — Gates + commit:** lint + build; `git commit -am "feat(app): propagate ContextEnvelope through iq-client (#399)"`.

**Acceptance gate:** envelope attached to every call; envelope-less call refused by guard; `simulated` provenance surfaced on degrade; gates green.

---

## M4 — Foundry thread-per-(user×agent) model (branch `sprint-29/m4-threads`)

> Config-gated `(user, agent) → threadId` map, seeded with the envelope.

### Task M4.1: Thread map (TDD, config-gated)

**Files:** Create `apps/hcc-app-fluent/src/copilot-drawer/foundry-thread-map.ts` (+ test); Modify the M1 `ConversationStore` key to `userOid×agent`

- [ ] **Step 1 — Failing test:** assert the app maps each `(userOid, agent)` to a distinct `threadId`; assert the thread is seeded on first message with the envelope (hospital scope + active role + board); assert a thread-creation failure starts a fresh thread and never cross-contaminates another agent's context.
- [ ] **Step 2 — Run test:** `npm --prefix apps/hcc-app-fluent test -- foundry-thread` → **FAIL**.
- [ ] **Step 3 — Implement:** `(user, agent) → threadId` map behind a config flag (Foundry-managed id when configured; simulated id in demo). Extend the M1 store key to `userOid×agent`.
- [ ] **Step 4 — Run tests:** unit green; conversation-isolation tests still green with the extended key.
- [ ] **Step 5 — Gates + commit:** lint + build; `git commit -am "feat(app): Foundry thread-per-(user x agent) map (config-gated) (#399)"`.

**Acceptance gate:** distinct thread per (user×agent); envelope-seeded; failure isolation proven; config-gated (no live calls in demo); gates green.

---

## M5 — OBO / RLS contract + simulated per-user scope (branch `sprint-29/m5-rls`)

> Designed + simulated this sprint; validated live in SIT (follow-up).

### Task M5.1: Simulated RLS scope + golden tests (TDD)

**Files:** Create `apps/hcc-app-fluent/src/data/roleboard/rls-scope.ts` (+ golden test)

- [ ] **Step 1 — Failing golden test:** a signed-in **single-site** role sees only its hospital slice (simulated RLS by `hospitalScope`); an **aggregated** role sees the cross-hospital view; a missing/invalid envelope → least-privilege fallback (Viewer / aggregated).
- [ ] **Step 2 — Run test:** `npm --prefix apps/hcc-app-fluent test -- rls-scope` → **FAIL**.
- [ ] **Step 3 — Implement:** `rls-scope.ts` filtering results by the envelope's `hospitalScope`/`role` (simulated); document the OBO contract (user-triggered calls use OBO, app identity only for autonomous jobs) — enforced live in SIT via config, simulated here.
- [ ] **Step 4 — Run tests:** golden green.
- [ ] **Step 5 — Gates + commit:** lint + build; `git commit -am "feat(app): OBO/RLS contract + simulated per-user scope (#399)"`.

### Task M5.2: ADR — App context envelope + per-agent threads

**Files:** Create `docs/adr/00NN-app-context-envelope-per-agent-threads.md`

- [ ] **Step 1 — Write the ADR:** context (design v1.1, issue #399), decision (Approach A: app-side `ContextEnvelope` + per-(user×agent) threads + simulated OBO/RLS, config-gated to lift live), consequences, links to ADR-0032/0033/0044/0013/0016/0014. Status `Accepted`. **Assign the next free ADR number at execution** (currently ~0045; watch the known 0043/0044 collisions — verify with `git ls-tree`).
- [ ] **Step 2 — Doc gates:** `python scripts/lint/check_mojibake.py docs/adr/00NN-*.md; npx --yes markdownlint-cli2 "docs/adr/00NN-*.md"` → clean.
- [ ] **Step 3 — Commit:** `git commit -am "docs(adr): app context envelope + per-agent threads (#399)"`.

**Acceptance gate:** simulated RLS golden proven (single-site vs aggregated); least-privilege fallback proven; ADR Accepted + doc gates green; SIT live-wiring recorded as the follow-up.

---

## M6 — Docs + closeout (branch `sprint-29/m6-closeout`)

### Task M6.1: PRD requirements + traceability

**Files:** Modify `docs/PRD.md`

- [ ] **Step 1 — Add requirements** (bump PRD MINOR): `FR-CTX-001` envelope on every IQ read/agent turn; `FR-CTX-002` per-(user×agent) thread isolation; `FR-CTX-003` role-first-eligible default board; `FR-CTX-004` simulated per-user RLS scope lifts to live via config; `NFR-CTX-001` no PHI / demo-safe; `NFR-CTX-002` provenance + citations preserved on every result. Update the §7 traceability matrix.
- [ ] **Step 2 — Doc gates + commit:** gates green; `git commit -am "docs(prd): add FR/NFR-CTX context-architecture requirements (#399)"`.

### Task M6.2: Sprint closeout

- [ ] **Step 1** — Verify the design §7 Definition of done is fully satisfied; check every DoD box in issue #399.
- [ ] **Step 2** — Ensure each milestone's PR is linked to #399 and lists FR/NFR-CTX IDs, lane impact (Experience lane), test evidence, and a `Compliance impact: none (synthetic, no PHI)` statement.
- [ ] **Step 3** — Open the sprint closeout summary comment on #399; capture the **SIT live-wiring follow-up** (Approach B: Foundry threads + Fabric RLS + OBO endpoints) as a new tracked issue.

**Acceptance gate:** PRD rows + matrix consistent; all DoD boxes checked; SIT follow-up issue filed.

---

## Self-review checklist (run before handoff)

- **Spec coverage:** every design §4 component and every milestone M0–M6 maps to a task above.
- **Contract consistency:** the `ContextEnvelope` shape is identical across M0, M3, M4, M5.
- **Guard integrity:** the envelope-less IQ call is refused (M3) and provenance/citations are preserved everywhere.
- **No PHI / no infra apply:** every task is app-side + synthetic; nothing is provisioned; live wiring is simulated + config-gated.
- **No placeholders at execution:** replace `00NN` (the ADR number) with the real next-free value; confirm every file path with `git grep` before editing.

## Execution handoff

**Chosen execution:** one dedicated worktree + Copilot CLI session using `superpowers:subagent-driven-development` (fresh subagent per milestone task, spec + quality-review gate each time), per [`docs/runbooks/sprint-29-worktree-delegation.md`](../../runbooks/sprint-29-worktree-delegation.md). The milestone chain is mostly sequential in one codebase, so a single worktree avoids cross-worktree merge churn; each milestone still ships as its own small PR (`sprint-29/<milestone>-<slice>`), human-reviewed and merged.
