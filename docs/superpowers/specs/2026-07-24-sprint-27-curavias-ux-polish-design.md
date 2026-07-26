# Sprint 27 — Curavias App UX Polish (OOA reference vertical) — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-24 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Approved |
| **Previous Version** | n/a (new document) |
| **Target app** | `apps/hcc-app-fluent` (internal app — app.curavias.ch) |
| **Owner agent** | [`ux-design-agent`](../../../agents/ux-design-agent/AGENT.md) |
| **Predecessors** | Sprint 20 (5-plane shell), Curavias app prototype-parity design + Sprint 25 / #276 (mockup ↔ app parity) |
| **Runtime posture** | GitHub Copilot coding agent + Superpowers-first execution; no per-agent runtime change (ADR-0002/ADR-0008 unchanged) |

> **For agentic workers:** This is a design spec. The implementation plan is produced
> separately via `superpowers:writing-plans` and executed via
> `superpowers:subagent-driven-development`. The brainstorming HARD-GATE is satisfied:
> this design was approved before any production code.

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Context and problem statement](#2-context-and-problem-statement)
3. [Scope](#3-scope)
4. [Approach decision](#4-approach-decision)
5. [M0 — SIT-connected shared-context local loop](#5-m0--sit-connected-shared-context-local-loop)
6. [The local brand — codified design system](#6-the-local-brand--codified-design-system)
7. [OOA reference vertical](#7-ooa-reference-vertical)
8. [Per-screen polish workflow and acceptance bar](#8-per-screen-polish-workflow-and-acceptance-bar)
9. [Ordered backlog for the remaining surfaces](#9-ordered-backlog-for-the-remaining-surfaces)
10. [Milestones](#10-milestones)
11. [Component boundaries and file map](#11-component-boundaries-and-file-map)
12. [Testing and accessibility](#12-testing-and-accessibility)
13. [Side-effect posture and approval gates](#13-side-effect-posture-and-approval-gates)
14. [Dependencies](#14-dependencies)
15. [Risk register](#15-risk-register)
16. [Traceability](#16-traceability)
17. [Definition of done](#17-definition-of-done)
18. [References](#18-references)

---

## 1. Goal and desired end state

Deliver a **fully polished, brand- and Fluent-aligned OOA operator experience** in the
internal Curavias app, plus a reusable **codified design system**, a **style-guide doc**,
an **in-app brand gallery**, and an **SIT-connected local visual-verify loop** — so that
polish is systematic (not ad-hoc) and later sprints apply the same recipe to the
remaining role boards.

**Desired end state:**

* A local development loop where the app runs locally (Vite dev server) against **SIT**,
  opened in a **VS Code browser tab** whose context is **shared with GitHub Copilot** via
  the read-only `playwright-mcp` server — enabling an *edit → hot-reload → re-snapshot →
  axe-scan* cycle for each screen.
* A **codified design system** in `apps/hcc-app-fluent/src/theme/design-system/` — semantic
  tokens (spacing on an 8 pt grid, elevation, motion, radii, density, focus) plus typed
  `makeStyles` component recipes — derived from the Curavias brandkit and Fluent UI v9,
  which every polished screen consumes.
* A **written style-guide** under `docs/brandkit/` mapping tokens to Fluent v9 and current
  M365 app patterns (Outlook / Teams / M365 Copilot), with do / don't examples.
* An **in-app `/brand` gallery route** that renders every token and component state in
  light and dark for visual and accessibility review.
* The **OOA reference vertical** — Start occupancy teaser → MAIN Occupancy board → OOA
  agent-plane context → the shared five-plane chrome — polished to the acceptance bar in
  [§8](#8-per-screen-polish-workflow-and-acceptance-bar).
* An **ordered backlog** capturing the same polish recipe for the remaining role boards
  and surfaces (executed in later sprints).

**Out of desired end state:** any backend, data-contract, semantic-model, agent-prompt, or
infrastructure change; the public site `apps/curavias-web` (www.curavias.ch) and any Astro
pattern; PHI or real patient data. This is an **experience-lane** sprint.

---

## 2. Context and problem statement

Sprint 20 rebuilt `apps/hcc-app-fluent` as a Teams-style five-plane shell on the Curavias
green-primary theme. The parity work (prototype-parity design + Sprint 25 / #276) brings
each surface to **functional 1:1 parity** with the locked prototype. What remains is
**quality polish**: the visual system is applied inconsistently across screens, interaction
states (hover / pressed / focus) and empty / loading / error states are uneven, spacing does
not always land on a grid, and the experience does not yet feel as refined as current M365
web apps.

Two structural gaps make polish slow and non-reproducible today:

1. **No single source of visual truth.** Screens hand-roll spacing, elevation, and
   component styling instead of consuming a shared token + recipe layer, so a fix on one
   screen does not propagate and drift returns.
2. **No tight visual-verify loop.** Reviewing a change means building and eyeballing;
   there is no documented loop that runs the app locally against SIT with a browser context
   that Copilot can inspect, screenshot, and axe-scan interactively inside VS Code.

This sprint closes both gaps and proves the recipe end-to-end on the highest-value role
view — **OOA (occupancy / 72 h forecast)** — before scaling to the rest.

**Non-negotiable principles (inherited from the parity design):**

* **No fabricated data or insights** at the UI layer. Polish is visual only; all board data
  still flows through the trusted-data contracts (`RoleBoard.load()` → `golden-source-client`)
  and all insights remain live agent-host round-trips. The provenance (live-vs-simulated)
  badge is *styled*, never bypassed.
* **RBAC and the role lens are unchanged.** Polish must not alter which acts / boards a role
  can see or a board's agent action ceiling.

---

## 3. Scope

### In scope

* The internal app `apps/hcc-app-fluent` only (app.curavias.ch).
* A documented **SIT-connected local visual-verify loop** with a VS Code / Copilot shared
  browser context (`playwright-mcp`).
* A **codified design system** (semantic tokens + component recipes) under
  `src/theme/design-system/`.
* An **app style-guide** doc under `docs/brandkit/`.
* An **in-app `/brand` gallery route**.
* Polishing the **OOA reference vertical**: Start occupancy teaser, MAIN Occupancy board,
  the OOA agent-plane context, and the shared five-plane chrome (Header / Navigation /
  Agent / Footer) that OOA renders inside.
* An **ordered backlog** for the remaining role boards and surfaces.

### Out of scope

* The public site `apps/curavias-web` (www.curavias.ch) and any Astro pattern, component,
  or asset — the internal app must not adopt Astro-site design.
* Backend, data-contract, semantic-model, agent-prompt, or infrastructure changes.
* Functional parity work already owned by Sprint 25 / #276 (this sprint assumes it merged).
* Executing polish on the non-OOA role boards (captured as backlog only).
* Any deploy or delete action; any PHI or real patient data ([ADR-0016](../../adr/0016-no-phi-in-mvp-demo-scope.md)).

---

## 4. Approach decision

**Chosen: Approach A — Fluent v9 token overlay + in-app gallery route.**

Extend the existing Sprint 20 `curavias-theme.ts` with a typed **semantic token layer** and
reusable `makeStyles` **component recipes**, add a lightweight **in-app `/brand` gallery
route**, and write the style-guide doc. This reuses the existing Vite / Fluent / Playwright
stack with near-zero new dependencies, and the gallery is itself a Playwright / axe target.

| Approach | Summary | Why not |
|----------|---------|---------|
| **A (chosen)** | Token overlay + recipes in-app + `/brand` gallery route + style-guide doc | — |
| B | Separate design-system package (`packages/curavias-ds`) | Monorepo package, build wiring, and versioning overhead for a single consuming app (YAGNI). |
| C | Storybook-based system | Second toolchain, extra dependencies, and a new CI surface alongside the existing Playwright / Vite setup; heavier than the value it adds here. |

A short ADR ([ADR-00NN](../../adr/)) records this decision: *codified design-system overlay
plus in-app gallery, no Storybook and no separate package.*

---

## 5. M0 — SIT-connected shared-context local loop

The enabler that every screen polish depends on. It is the first milestone and ships with a
runbook so it is reproducible.

**The loop:**

1. `npm run dev` serves the app at `http://localhost:5173` (Vite). MSAL and agent-host env
   vars point at **SIT** (`VITE_MSAL_*`, `VITE_AGENT_HOST_URL`). When the SIT vars are absent
   the app degrades to the anonymous `demo.guest` shell (aggregated-only data, deterministic
   grounded mock) so the loop still runs offline in CI and on a disconnected laptop.
2. A **VS Code browser tab** opens `localhost:5173`. The read-only `playwright-mcp` server
   (already in the allow-list and wired in [`.vscode/mcp.json`](../../../.vscode/mcp.json))
   shares that **live browser context with GitHub Copilot**, so the human in VS Code and
   Copilot inspect the same DOM. Copilot can `browser_navigate`, `browser_snapshot`,
   `browser_take_screenshot`, `browser_resize`, and read `browser_console_messages`.
3. **Standalone mode** stays available: the repo's local Playwright CLI
   ([`apps/hcc-app-fluent/playwright.config.ts`](../../../apps/hcc-app-fluent/playwright.config.ts),
   scripts `test:e2e` / `test:a11y`) captures screenshots, checks responsive breakpoints, and
   runs `axe` WCAG scans against a rendered screen.
4. The cycle for each screen: **edit locally → Vite hot-reload → re-snapshot in the shared
   browser → axe-scan → attach before/after evidence.**

**Deliverable:** a runbook `docs/runbooks/curavias-ux-local-verify-loop.md` covering the env
vars, both Playwright modes, the VS Code shared-context wiring, and the edit-verify cycle —
plus a verified green run of `npm run dev`, `test:e2e`, and `test:a11y` on the OOA screens as
the baseline capture.

**Security posture:** the loop is **read-oriented** — Playwright inspects and captures, it
never mutates repo or cloud state. SIT connection uses the existing MSAL app registration and
carries no secrets in source. No new MCP server and no allow-list change are required.

---

## 6. The local brand — codified design system

Three artifacts, one source of truth.

### 6.1 Design-system module (`src/theme/design-system/`)

A typed semantic layer on top of the Fluent v9 theme and the existing
`curavias-tokens.json` brand ramp (green `#17B890` primary, blue `#365B7D` secondary, plus
danger / warning / info / accent). It does **not** replace the Fluent theme — it names the
decisions Fluent leaves open so screens stop hand-rolling them.

| File | Responsibility |
|------|----------------|
| `src/theme/design-system/tokens.ts` | Semantic tokens: `space` (4 / 8 / 12 / 16 / 24 / 32 on an 8 pt grid), `radii`, `elevation` (shadow ramp mapped to Fluent `shadow2/4/8/16/28/64`), `motion` (duration + easing curves matching Fluent motion), `density`, `zIndex`, and `focus` (ring width + offset). |
| `src/theme/design-system/recipes.ts` | Typed `makeStyles` component recipes every screen reuses: `surfaceCard`, `boardGrid`, `sectionHeader`, `statTile` (KPI), `provenanceBadge`, and the three async states `emptyState`, `loadingState`, `errorState`. |
| `src/theme/design-system/index.ts` | Barrel re-exporting `tokens` and `recipes`. |

Tokens are derived from the brandkit and Fluent — no new brand values are invented. RAG
signalling continues to use the existing `ragColors` map from `curavias-theme.ts`.

### 6.2 App style-guide (`docs/brandkit/curavias-app-style-guide.md`)

A written guide that maps each semantic token and recipe to the Fluent v9 primitive and the
current M365 app pattern it mirrors (Outlook / Teams / M365 Copilot), with do / don't
examples. It is documentation the code links to; it is **not** imported by the app. It carries
a standard version header per copilot-instructions §9.

### 6.3 In-app brand gallery (`/brand` route)

A new route `src/workspaces/brand/BrandGalleryView.tsx` (mounted in
[`src/shell/router.tsx`](../../../apps/hcc-app-fluent/src/shell/router.tsx)) that renders every
token and every component-recipe state (default / hover / pressed / focus / disabled /
empty / loading / error) in both light and dark. The gallery is a first-class Playwright /
axe target so the design system itself is accessibility-verified. It is reachable only through
the route (not added to primary navigation) to keep the operator nav unchanged.

---

## 7. OOA reference vertical

The OOA (occupancy / 72 h forecast) journey is polished end-to-end as the reference
implementation that locks every pattern. The four surfaces, all consuming the design system:

| Surface | Primary files | Polish focus |
|---------|---------------|--------------|
| **Start — occupancy teaser** | `src/workspaces/start/StartView.tsx`, `src/workspaces/start/role-launcher.ts` | Teaser card rhythm, KPI tile, provenance badge, hover / focus, loading / empty states. |
| **MAIN — Occupancy board (OOA)** | `src/workspaces/main/boards/occupancy/OccupancyBoard.tsx`, `occupancy-board.ts`, `src/data/roleboard/occupancy-data.ts` | Board grid on the 8 pt grid, 72 h forecast presentation, ward rows, elevation, empty / loading / error, dark-mode parity. |
| **Agent plane — OOA context** | `src/copilot-drawer/`, `src/copilot-rail/` | Docked / floating states, context-insight chips, ceiling badge, message rhythm aligned to M365 Copilot chat surfaces. |
| **Shared five-plane chrome** | `src/shell/AppShell.tsx`, `src/shell/planes/`, `src/shell/TopBar/`, footer plane | Header controls, navigation rhythm, focus order, spacing, elevation — polished once, benefiting every role. |

Polishing the shared chrome inside the OOA vertical is deliberate: it is the highest-leverage
work and every subsequent role board inherits it.

---

## 8. Per-screen polish workflow and acceptance bar

**Workflow (per screen):**

1. Capture **before** via Playwright: light + dark, desktop (≥ 1280) + narrow (≈ 768).
2. Refactor the screen to consume the design-system tokens and recipes locally.
3. Verify in the **shared browser context** (hot-reload) — spacing, states, interaction.
4. Capture **after** (same matrix) and run the axe scan.
5. Attach before / after evidence to the screen's PR.

**Acceptance bar — a screen exits review only when all hold:**

* ✅ **Fluent + M365 heuristic checklist** passes: 8 pt spacing grid, Fluent type ramp,
  elevation / shadow correctness, motion on transitions, hover / pressed / focus states,
  and explicit empty / loading / error states.
* ✅ **WCAG 2.1 AA** green via `axe-core` (`npm run test:a11y`) — contrast, focus visibility,
  roles, and accessible names.
* ✅ **Before / after screenshots** (light + dark, desktop + narrow) attached to the PR.
* ✅ **Visual fidelity** to the brand / prototype intent — *as close as the Fluent UI stack
  reasonably allows* (explicitly **not** pixel-parity; extend Fluent to a sensible acceptance
  level rather than fighting the framework).

The heuristic checklist is written once (in the style-guide doc) and reused verbatim as the
review gate for every screen this sprint and in the backlog.

---

## 9. Ordered backlog for the remaining surfaces

Same recipe, later sprints. Ordered by demo value (highest first). No execution this sprint —
this section is the ready-to-run handoff.

| Order | Surface | Board / area | Notes |
|-------|---------|--------------|-------|
| 1 | MAIN — Discharge | `boards/discharge/` (DCA) | Closes the OOA → DCA residual-pressure handoff visually. |
| 2 | MAIN — Bed management | `boards/bed-manager/` (BMCA) | Whiteboard card system; highest card-density polish. |
| 3 | MAIN — Crisis | `boards/crisis/` (CSA) | Scenario board; pairs with the CSA wizard surface. |
| 4 | MAIN — OR steering | `boards/or-steering/` (ORSA) | Utilisation grid + first-case metrics. |
| 5 | MAIN — Staffing | `boards/staffing/` (SBA) | Roster balance view. |
| 6 | MAIN — BVA | `boards/bva/` | Bed-view analytics board. |
| 7 | BACKSTAGE | `src/workspaces/backstage/` | Roles & RBAC, evidence tabs. |
| 8 | SETTINGS | `src/workspaces/settings/` | Theme / language / refresh controls. |

Each backlog item is a same-shaped screen-polish task: consume the design system, run the
per-screen workflow, meet the acceptance bar.

---

## 10. Milestones

| Milestone | Deliverable | Depends on |
|-----------|-------------|-----------|
| **M0** | SIT-connected shared-context local loop + runbook + green baseline capture | — |
| **M1** | Design-system module (`tokens.ts`, `recipes.ts`, `index.ts`) + unit tests | M0 |
| **M2** | App style-guide doc (`docs/brandkit/curavias-app-style-guide.md`) incl. the heuristic checklist | M1 |
| **M3** | In-app `/brand` gallery route + Playwright / axe coverage | M1 |
| **M4** | Shared five-plane chrome polished to the acceptance bar | M1, M3 |
| **M5** | OOA Start occupancy teaser polished | M4 |
| **M6** | OOA MAIN Occupancy board polished | M4 |
| **M7** | OOA agent-plane context polished | M4 |
| **M8** | Integration: full a11y + e2e + build green; backlog handoff; docs + PRD + ADR closeout | M4–M7 |

M1–M3 are largely parallel after M0. M4 is the shared-chrome pass. M5–M7 are the OOA
surfaces. M8 is closeout.

---

## 11. Component boundaries and file map

Extends the existing `apps/hcc-app-fluent/src` structure and follows current patterns
(Fluent UI v9, `react-router-dom` v6, i18next, Vitest, Playwright / axe). New and modified
files:

```text
apps/hcc-app-fluent/src/
  theme/
    design-system/
      tokens.ts            # NEW  semantic tokens (space/radii/elevation/motion/density/focus)
      recipes.ts           # NEW  makeStyles component recipes
      index.ts             # NEW  barrel
  workspaces/
    brand/
      BrandGalleryView.tsx # NEW  /brand token + component-state gallery
    start/
      StartView.tsx        # MOD  OOA occupancy teaser polish (design-system consume)
    main/boards/occupancy/
      OccupancyBoard.tsx   # MOD  OOA board polish (design-system consume)
  shell/
    router.tsx             # MOD  mount /brand route
    AppShell.tsx           # MOD  chrome spacing/elevation/focus polish
    planes/                # MOD  plane rhythm polish
    TopBar/                # MOD  header control polish
  copilot-drawer/          # MOD  agent-plane docked/floating + chat rhythm polish
  copilot-rail/            # MOD  context-insight chip + ceiling badge polish

docs/
  brandkit/
    curavias-app-style-guide.md   # NEW  token→Fluent→M365 mapping + heuristic checklist
  runbooks/
    curavias-ux-local-verify-loop.md  # NEW  M0 loop runbook
  adr/
    00NN-curavias-app-design-system-overlay.md  # NEW  Approach A decision
```

**Boundary rule:** components import styling **only** from `theme/design-system` (or the
Fluent theme) — never hand-rolled inline spacing / shadow values. This is the invariant that
keeps polish from drifting back.

---

## 12. Testing and accessibility

* **Unit (Vitest):** `tokens.ts` exports the expected scale and `recipes.ts` produce the
  expected class shapes; a guard test asserts polished OOA components reference design-system
  classes (no raw pixel spacing literals in the changed files).
* **E2E (Playwright):** the existing shell smoke plus a `/brand` gallery render smoke and OOA
  vertical smoke (Start teaser, Occupancy board, agent plane).
* **Accessibility (axe-core):** `npm run test:a11y` green on the `/brand` gallery and every
  polished OOA screen — WCAG 2.1 AA. This is the `NFR-UX-001` gate.
* **Visual evidence:** before / after screenshots (light + dark, desktop + narrow) captured
  per screen via Playwright and attached to each PR — the `NFR-UX-003` gate.
* **Build:** `npm run lint` (tsc `--noEmit`) and `npm run build` green.

No backend, agent, or infra tests change — this is experience-lane only.

## 13. Side-effect posture and approval gates

* Owner agent [`ux-design-agent`](../../../agents/ux-design-agent/AGENT.md); side-effect
  ceiling `write`. Tools: `github-mcp` (`write` — branches / PRs / comments) and
  `playwright-mcp` (`read` — visual + a11y verification only).
* **No `deploy` / `delete`** in this sprint; no `approved-to-apply` gate is exercised.
* Control-plane files (`AGENTS.md`, `.github/copilot-instructions.md`,
  `.github/copilot/mcp.json`, `docs/adr/*`) are only touched via CODEOWNERS-reviewed PRs; the
  new ADR follows that path.

## 14. Dependencies

* **Sprint 25 / #276 parity merged to `main`** — this sprint starts from that baseline.
* Sprint 20 five-plane shell and Curavias theme (`curavias-theme.ts`, `curavias-tokens.json`).
* Existing `.vscode/mcp.json` + `playwright-mcp` allow-list entry (present; no change).
* Existing MSAL app registration and SIT agent-host for the live loop (fallback to
  `demo.guest` when absent).

## 15. Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|-----------|
| R1 | Parity work (#276) not yet merged when this sprint starts | Medium | High | Successor sequencing — M0 verifies the parity baseline on `main` before any polish; otherwise block and wait. |
| R2 | Polish accidentally changes data / insight behaviour | Low | High | Invariant: styling only; guard test asserts no data / agent-contract edits in changed files; provenance badge styled not bypassed. |
| R3 | Design-system overlay fights Fluent theming | Medium | Medium | Overlay *names* Fluent decisions, never replaces the theme; recipes build on `makeStyles` + Fluent tokens. |
| R4 | Astro / public-site patterns leak into the internal app | Low | Medium | Explicit out-of-scope; review gate rejects any `curavias-web` import or Astro asset. |
| R5 | SIT loop unavailable on a given machine | Medium | Low | `demo.guest` offline fallback keeps the loop and CI green without SIT. |
| R6 | Screen polish scope-creeps beyond OOA | Medium | Medium | Coverage boundary fixed to the OOA vertical; everything else is backlog only. |

## 16. Traceability

New requirement family added to [`docs/PRD.md`](../../PRD.md) §M and its Traceability Matrix
in the same change:

| Requirement | Summary |
|-------------|---------|
| `FR-UX-001` | Codified app design system (semantic tokens + component recipes) as the single source of visual truth. |
| `FR-UX-002` | App style-guide doc mapping tokens to Fluent v9 + current M365 app patterns, incl. the heuristic checklist. |
| `FR-UX-003` | In-app `/brand` gallery route rendering every token and component state (light / dark). |
| `FR-UX-004` | SIT-connected local visual-verify loop with a VS Code / Copilot shared browser context, documented as a runbook. |
| `FR-UX-005` | OOA reference vertical polished to the acceptance bar as the reference implementation. |
| `FR-UX-006` | Ordered polish backlog for the remaining role boards and surfaces (later sprints). |
| `NFR-UX-001` | Every polished screen passes WCAG 2.1 AA via axe-core. |
| `NFR-UX-002` | Every polished screen passes the Fluent v9 + M365 heuristic checklist. |
| `NFR-UX-003` | Every polished screen carries before / after visual evidence attached to its PR. |
| `NFR-UX-004` | Polish stays experience-lane only: no backend / data-contract / agent-prompt / infra change, no PHI, no public-site (Astro) patterns. |

Golden-task / PR references carry the `FR-UX-*` / `NFR-UX-*` IDs they advance.

## 17. Definition of done

* [ ] M0–M8 committed on a `sprint-27/curavias-ux-polish` worktree branched off `main`.
* [ ] SIT-connected shared-context local loop works and is documented in
      `docs/runbooks/curavias-ux-local-verify-loop.md`.
* [ ] Design-system module (`tokens.ts`, `recipes.ts`, `index.ts`) is the single styling
      source for the polished OOA surfaces; guard test green.
* [ ] `docs/brandkit/curavias-app-style-guide.md` published with the heuristic checklist.
* [ ] `/brand` gallery route renders all tokens + component states and is axe-clean.
* [ ] Shared five-plane chrome and the full OOA vertical (Start teaser, Occupancy board,
      agent plane) meet the acceptance bar in §8.
* [ ] `npm run lint`, `npm run test`, `npm run test:e2e`, `npm run test:a11y`, `npm run build`
      all green; before / after evidence attached per screen.
* [ ] No public-site / Astro pattern introduced; no data / agent-contract / infra change; no
      PHI.
* [ ] `FR-UX-001`..`FR-UX-006` + `NFR-UX-001`..`NFR-UX-004` added to `docs/PRD.md` §M and the
      Traceability Matrix; ADR-00NN merged (Approach A).
* [ ] Ordered backlog handed off; docs bumped per copilot-instructions §9; epic + tracker
      issues linked.

## 18. References

* [Sprint 20 — Curavias UX design spec](2026-07-17-sprint-20-curavias-ux-design.md)
* [Curavias app prototype-parity design](2026-07-21-curavias-app-prototype-parity-design.md)
* [Sprint 25 — trusted-signals, proactive CSA, app parity](2026-07-23-sprint-25-trusted-signals-proactive-csa-parity-design.md)
* [`ux-design-agent` prompt](../../../agents/ux-design-agent/AGENT.md)
* [Curavias Brand Guidelines](../../brandkit/Curavias-Brand-Guidelines.md)
* [DEV_WORKFLOW](../../DEV_WORKFLOW.md) (trunk-based parallel-sprint worktrees)
* [`.vscode/mcp.json`](../../../.vscode/mcp.json) (Playwright MCP shared-context wiring)
* [ADR-0002 — runtime is GitHub Copilot coding agent](../../adr/0002-runtime-is-github-copilot-coding-agent.md)
* [ADR-0016 — no PHI in MVP demo scope](../../adr/0016-no-phi-in-mvp-demo-scope.md)
