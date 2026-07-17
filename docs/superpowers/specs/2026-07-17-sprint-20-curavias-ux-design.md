# Sprint 20 — Curavias App UX Redesign (5-Plane Teams-Style Shell) — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-07-17 |
| **Author** | Urs Rueegg |
| **Status** | Delivered |
| **Previous Version** | 1.0.0 (design draft for review) |
| **Anchor triggers** | User-experience improvement request for the `hcc-app-fluent` React app; validated interactive mockup (`sprint-20-curavias-ux-mockup.html`); brandkit re-base to Curavias green-primary theme |
| **Runtime posture** | GitHub Copilot coding agent + Superpowers-first execution; no change to per-agent runtime posture (ADR-0008 unchanged); app remains a Container Apps-hosted SPA calling the Sprint 13 agent-host |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Context and problem statement](#2-context-and-problem-statement)
3. [Scope](#3-scope)
4. [Architecture — the 5-plane shell](#4-architecture--the-5-plane-shell)
5. [Design system — Curavias theme](#5-design-system--curavias-theme)
6. [Content surfaces](#6-content-surfaces)
7. [Role dropdown and RBAC access lens](#7-role-dropdown-and-rbac-access-lens)
8. [Internationalisation (EN/DE/FR/IT)](#8-internationalisation-endefrit)
9. [Agent plane](#9-agent-plane)
10. [Data flow and refresh](#10-data-flow-and-refresh)
11. [Component boundaries](#11-component-boundaries)
12. [Testing and accessibility](#12-testing-and-accessibility)
13. [Side-effect posture and approval gates](#13-side-effect-posture-and-approval-gates)
14. [Dependencies](#14-dependencies)
15. [Risk register](#15-risk-register)
16. [Traceability](#16-traceability)
17. [Definition of done](#17-definition-of-done)
18. [References](#18-references)

---

## 1. Goal and desired end state

Redesign the existing `hcc-app-fluent` React application into a **Teams-style
five-plane shell** that adopts the Curavias green-primary brand, supports four
languages, exposes a docked context-aware agent plane, and enforces a
**role-based access lens** driven by Entra security-group assignments.

**Desired end state:**

* A five-plane layout (Header / Navigation / Main / Agent / Footer) where Main
  always fills the space bounded by the other planes.
* A single Curavias theme (green `#17B890` primary, blue `#365B7D` secondary)
  wired for light and dark, persisted to `localStorage` and user Settings.
* Header controls (right-to-left): user identity, **role**, hospital, language,
  theme; brand mark and product name on the left.
* Flat navigation (no cascaded sub-items): Start / Main / CSA / Backstage /
  Settings, with Settings pinned to the bottom.
* A role dropdown whose selection sets the effective access scope — the visible
  hospitals, navigation entries, boards, actions, and the agent action ceiling.
* Four-language support (EN/DE/FR/IT) with in-session switching that refreshes
  the active content.
* A docked agent plane that collapses to a floating icon and defaults to the
  workspace's context agent, with an always-available switch to the orchestrator.

**Out of desired end state:** any change to backend data contracts, agent
prompts, or infrastructure topology. This sprint is an experience-lane redesign.

---

## 2. Context and problem statement

The current app (`apps/hcc-app-fluent`, React 18 + Fluent UI v9 + Vite 6) uses a
`useState`-driven workspace switch, a top bar plus a vertical rail, and an
overlay copilot drawer. Three gaps block the intended demo experience:

* **Shell shape.** The layout is not the surrounded-Main, five-plane Teams-style
  frame the stakeholders expect, and the agent surface is a transient overlay
  rather than a first-class docked plane.
* **Brand drift.** `theme/helvion-theme.ts` still carries the retired
  blue-primary Helvion palette. The brandkit has re-based to Curavias
  green-primary with documented WCAG rules, and no dark mode is wired.
* **Access and reach.** Only two languages exist (`de`, `en`), and there is no
  first-class role picker; the stub `RoleSwitcher` is gated to SIT admins and
  renders as a single button, not a scoped access lens.

This sprint closes those gaps without touching the data, AI, or infrastructure
lanes. It is a **demo/proof-of-technology** surface: all figures are pure
simulated, generic data — no PHI.

---

## 3. Scope

### In scope

* New five-plane shell built on `react-router-dom` v6 (layout route + `Outlet`).
* Curavias theme module (light + dark) sourced from the brandkit, replacing the
  Helvion theme; theme toggle and persistence.
* Header plane with brand mark, role, hospital, language, theme, and user.
* Flat navigation plane with collapse behaviour and bottom-pinned Settings.
* Content surfaces: Start, Main (role-persona boards), CSA cockpit, Backstage
  governance widgets, Settings.
* Role dropdown and the RBAC access-lens model (role -> hospital scope -> nav /
  board / action gating -> agent ceiling).
* Four-language i18n (`en`, `de`, `fr`, `it`) with refresh-on-switch.
* Docked, context-aware agent plane with orchestrator switch and ceiling badge.
* Footer plane with a live-data refresh picker and app version.
* Unit, e2e, and accessibility tests for the above.

### Out of scope

* Backend/data-platform changes, agent prompt changes, new MCP servers.
* New Azure infrastructure or region moves (Sprint 18/19 own that).
* New product requirements — this sprint advances existing FR/NFR IDs (see §16).

---

## 4. Architecture — the 5-plane shell

**Chosen approach: full `react-router-dom` v6 shell (Approach B).** A layout
route renders the four surrounding planes and an `Outlet` for Main. The Header,
Navigation, Agent, and Footer planes stay mounted across navigations; a route
change is the trigger to refresh Main content.

### Plane grid

```text
+-----------------------------------------------------------+
|  AppHeaderPlane  (48px)                                   |
+---------+---------------------------------------+---------+
|  Nav    |  AppMainPlane (Outlet)                | Agent   |
| Plane   |  fills all remaining width/height     | Plane   |
| (left,  |                                       | (right, |
| collap- |                                       | docked/ |
| sible)  |                                       | fab)    |
+---------+---------------------------------------+---------+
|  AppFooterPlane  (32px)  refresh picker | app version     |
+-----------------------------------------------------------+
```

### Route map

| Route | Workspace | Notes |
|-------|-----------|-------|
| `/start` | Start | Default redirect target; vision/mission + showcase disclaimer |
| `/main/:board?` | Main | `:board` selects the persona board; defaults to first allowed |
| `/csa` | CSA | Crisis-simulation cockpit |
| `/backstage/:widget?` | Backstage | Governance/evidence widgets |
| `/settings` | Settings | App and user preferences |

`*` redirects to `/start`. Navigation entries the active role cannot access are
disabled (not hidden) so the information architecture stays legible.

### Component tree

```text
<RouterProvider>
  <AppShell>                (layout route)
    <ThemeProvider>
      <RbacProvider>        (role -> scope)
        <AppHeaderPlane/>   (brand | RoleMenu HospitalMenu LanguageMenu ThemeToggle UserMenu)
        <AppNavigationPlane/> (Start Main CSA Backstage | Settings pinned)
        <AppMainPlane> <Outlet/> </AppMainPlane>
        <AppAgentPlane/>    (docked plane <-> floating fab)
        <AppFooterPlane/>   (RefreshPicker | version)
```

---

## 5. Design system — Curavias theme

Source of truth: the brandkit under `docs/brandkit/` (`color/curavias-theme.ts`,
`curavias-tokens.json`, `Curavias-Fluent-Color-System.md`). Committing the
brandkit into the app-consumable path is the first implementation task (M0).

### Palette roles

| Role | Token | Value | Usage |
|------|-------|-------|-------|
| Primary | `brand[80]` | `#17B890` (green) | Selection bars, accents, primary fills with dark text |
| Secondary | `brand-secondary[80]` | `#365B7D` (blue) | Solid buttons with white text, header background |
| Danger | `danger[80]` | `#E30613` (Swiss red) | Error/critical only |
| Warning | `warning[80]` | `#E8A200` | Above-target/attention states |
| Info | `info[80]` | `#1FA9D6` | Neutral informational chips |

### Accessibility rules (baked into the brandkit)

* Green `#17B890` **fails** WCAG AA with white text (2.53:1). Use **dark** text
  on green (`#0E0F11`, 7.57:1 AAA).
* For white-text solid buttons use **secondary blue** `#365B7D` (7.12:1 AAA).
* Green text/links on white use `brand[50]` `#12765F` (5.55:1 AA).
* Swiss red is reserved for error/critical only — never decorative.

### Theme wiring

* One `curaviasLightTheme` and one `curaviasDarkTheme` (Fluent v9 `Theme`),
  generated from the brand ramp.
* `ThemeProvider` holds the active mode in React state, applies the Fluent
  `FluentProvider` theme, and persists the choice to `localStorage`
  (`curavias.theme`) plus the user Settings surface.
* Theme toggle lives in the header; default mode = light.

---

## 6. Content surfaces

### Start

Vision and mission statement, plus a prominent disclaimer: *Microsoft
Innovation Hub Showcase — pure simulated, generic data for demonstration only,
no PHI.* No live data; footer refresh picker hidden.

### Main — role-persona boards (infinity whiteboard)

A board bar selects a persona board on the whiteboard surface, each anchored to
a Sprint 11 agent:

| Board | Agent | Primary content |
|-------|-------|-----------------|
| Bed Manager | `bmca-agent` | Occupancy now, free beds, pending discharges |
| Occupancy / Forecast | `ooa-agent` | 72h forecast peak, breach windows, ward trend |
| Discharge | `dca-agent` | Discharge-ready list, blockers |
| OR-Steering | `orsa-agent` | Case utilisation, first-case on-time, idle slots |
| Staffing | `sba-agent` | Shift balance, coverage gaps |

Boards visible to the user are gated by the active role (see §7). Every visual
carries a source citation to preserve per-visual traceability.

### CSA — crisis-simulation cockpit

A four-step flow **Prepare -> Run -> Evaluate -> Recommend** wired to
`csa-agent`. Run is a `deploy`-ceiling action gated by the `approved-to-apply`
human-in-the-loop comment (mirrors the agent's confirmation rule). Panels:
scenario inputs, response levers, run status, results/recommendations.

### Backstage — governance and evidence widgets (infinity whiteboard)

One widget per artefact class, each with provenance: ADRs, PRD / FR-NFR
traceability, bill of materials, GA/Preview evidence, Roles/RBAC, Sprint status,
Agent registry.

### Settings

App and user preferences persisted to `localStorage`: active role (read-only
reflection), theme, language, default hospital, default refresh rate, and
agent-plane default open state.

---

## 7. Role dropdown and RBAC access lens

This extends the existing claims model rather than replacing it. Today
`auth/claim-parser.ts` parses `HCC.*` app-role claims (issued from Entra
**security-group -> app-role** mappings via the `ihzhhpf-app` registration),
plus `hospital` and `env` claims. `role-context.tsx` and `hospital-context.tsx`
already hold role and hospital state.

### Model

* The role dropdown lists **only** the `HCC.*` roles the signed-in user actually
  holds. It never offers a role the user has not been granted.
* The selected role is the **access lens**. A role definition maps to:
  * **hospital scope** — which hospitals the Hospital dropdown may offer;
  * **navigation** — which workspaces are enabled;
  * **boards/widgets** — which Main boards and Backstage widgets are available;
  * **action ceiling** — the maximum agent side-effect the user may trigger
    (`read` < `write` < `deploy`).
* In-session switching only ever **narrows** to a role the user already holds;
  it cannot grant new access. This preserves least-privilege while enabling
  demo persona walkthroughs.
* Changing role re-derives the hospital list, re-gates nav/boards, and updates
  the agent ceiling badge. If the current workspace becomes inaccessible, the
  shell falls back to the first allowed workspace.

### Role map (demo baseline)

| Role | Hospital scope | Navigation | Boards | Ceiling |
|------|----------------|------------|--------|---------|
| `HCC.PlatformAdmin` | all | all | all | `deploy` |
| `HCC.DemoOperator` | all | all | all | `write` |
| `HCC.RegionalCrisisLead` | all | all | all | `deploy` |
| `HCC.BedManager` | own site | Start/Main/Settings | Bed Manager, Occupancy, Discharge | `write` |
| `HCC.Viewer` | aggregated | Start/Main | Occupancy | `read` |

The map is a typed table in a single `rbac-model.ts` module so it is testable in
isolation and easy to extend. Role is the primary lens; hospital is secondary
within the lens.

---

## 8. Internationalisation (EN/DE/FR/IT)

* Add `fr.json` and `it.json` resource bundles; expand `supportedLanguages` to
  `['en', 'de', 'fr', 'it']`. Keep DE as the seeded default with EN fallback per
  current behaviour, but allow header selection of any of the four.
* Language selection lives in the header and is persisted (`curavias.lang`).
* Changing language refreshes the active content (labels, nav, board titles,
  agent-plane chrome). Data values are locale-formatted where applicable.
* All user-visible strings route through i18n keys; no hard-coded copy in
  components. New keys are added for the shell chrome (planes, role menu,
  refresh picker, showcase disclaimer).

---

## 9. Agent plane

* **Docked + context-aware by default.** Collapsed state = a floating
  bottom-right icon button; expanded state = a docked right-hand plane that
  resizes Main. The user opens/closes it explicitly.
* **Context agent per workspace:** Start -> orchestrator, Main -> bmca/ooa,
  CSA -> csa-agent, Backstage -> knowledge-agent, Settings -> orchestrator. An
  always-available **Ask Orchestrator** switch lets the user route to the
  dispatcher instead.
* The plane header shows the active agent and its **action ceiling badge**,
  which reflects the active role's ceiling (§7). A read-only role cannot trigger
  write/deploy actions from the plane.
* Reuses the existing `agent-manifest.ts` for agent metadata; the transient
  overlay `CopilotDrawer` becomes this persistent plane.

---

## 10. Data flow and refresh

* Route change is the single trigger to (re)fetch Main content; surrounding
  planes stay mounted.
* The footer **refresh picker** is shown only on live-data workspaces (Main,
  CSA) and hidden elsewhere. Selected interval drives polling for that surface;
  default from Settings.
* When a non-critical dependency fails, the surface degrades gracefully (stale
  badge + retry) rather than blanking the plane (`NFR-REL-003`).
* Agent responses preserve source references and timestamps as today
  (`FR-CX-006`).

---

## 11. Component boundaries

Each unit has one purpose, a typed interface, and is independently testable:

| Unit | Responsibility | Depends on |
|------|----------------|------------|
| `AppShell` | Layout route; composes the five planes + `Outlet` | router, ThemeProvider, RbacProvider |
| `AppHeaderPlane` | Brand + control cluster | RoleMenu, HospitalMenu, LanguageMenu, ThemeToggle, UserMenu |
| `AppNavigationPlane` | Flat nav + collapse + bottom Settings | RbacProvider (nav gating), router |
| `AppMainPlane` | Hosts `Outlet`; enforces max width/height | router |
| `AppAgentPlane` | Docked/fab agent surface, ceiling badge | agent-manifest, RbacProvider |
| `AppFooterPlane` | Refresh picker + version | Settings, workspace liveness |
| `ThemeProvider` | Light/dark state + persistence | brandkit theme |
| `RbacProvider` + `rbac-model.ts` | Role -> scope derivation | claim-parser |
| Board components | One per persona board | agent-manifest, data hooks |
| Backstage widgets | One per artefact class | repo/evidence data |
| CSA cockpit steps | Prepare/Run/Evaluate/Recommend | csa-agent, HITL gate |

Files that grow beyond a single responsibility (for example the current
`App.tsx` switch) are decomposed as part of this work.

---

## 12. Testing and accessibility

* **Unit (vitest):** rbac-model mapping (role -> hospital/nav/board/ceiling and
  narrow-only guarantee), theme persistence, i18n key coverage for all four
  languages, refresh-picker visibility logic.
* **E2E (Playwright):** default redirect to `/start`; nav routing across all
  workspaces; role switch narrows hospital options + gates nav/boards + updates
  ceiling; agent dock/undock; theme toggle persistence; language switch refresh.
* **Accessibility (`test:a11y`):** WCAG AA on the green/blue token combos
  (dark-on-green, white-on-blue, green-link-on-white); disabled nav items stay
  in the accessibility tree with correct state; keyboard reachability of all
  header controls and the agent plane.
* **Lint/type:** `tsc --noEmit` clean; markdownlint clean for docs.

---

## 13. Side-effect posture and approval gates

* The app is a read/interact surface; the only `deploy`-ceiling path is the CSA
  **Run** step, which routes through `csa-agent` and requires the
  `approved-to-apply` human-in-the-loop comment before any simulation apply.
* The role access lens caps what a user can trigger; it cannot elevate.
* No new MCP servers; no changes to `.github/copilot/mcp.json`.

---

## 14. Dependencies

* Brandkit committed to an app-consumable path (M0 task).
* Existing agent-host + `agent-manifest.ts` (Sprint 13) for agent metadata.
* `ihzhhpf-app` registration claims (`roles`, `hospital`, `env`) unchanged.
* Sprint 11 agent set for board/context mapping.
* No dependency on the parked knowledge-agent PR (#243); Sprint 20 docs branch
  off `main` and merge independently.

---

## 15. Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| R1 | Router migration regresses existing workspace deep links | Medium | Medium | Keep hash-compatible redirects; e2e covers every route |
| R2 | Theme swap breaks contrast in dark mode | Medium | High | Enforce brandkit WCAG rules in `test:a11y`; dark-on-green only |
| R3 | Role narrowing hides content a demo presenter expects | Medium | Medium | PlatformAdmin/DemoOperator retain full scope; role is explicit in header + Settings |
| R4 | i18n gaps (missing FR/IT keys) surface raw keys | Medium | Low | Key-coverage unit test fails CI on any missing key |
| R5 | Agent plane resize competes with Main whiteboard | Low | Medium | Docked plane uses fixed width; Main reflows; fab state frees full width |

---

## 16. Traceability

This sprint advances existing requirements; no new FR/NFR is introduced.

| Requirement | How Sprint 20 advances it |
|-------------|---------------------------|
| `FR-CX-001` | Copilot interface realised as the docked agent plane |
| `FR-CX-002` | Grounded answers surfaced with source context in the plane |
| `FR-CX-003` | Bottleneck explanations rendered on Main boards + plane |
| `FR-CX-004` | Bed state / pressure windows / discharges shown on boards |
| `FR-CX-006` | Source references + timestamps preserved in agent responses |
| `FR-VIZ-001` | Bed-capacity board (occupancy, forecast, DQ signals) |
| `FR-VIZ-002` | OR-steering board (utilisation, on-time, idle slots) |
| `FR-GOV-002` | Access-control enforcement via the role access lens |
| `NFR-SEC-001` | Least-privilege, role-scoped visibility and actions |
| `NFR-SEC-002` | Role/hospital changes are explicit and auditable in-session |
| `NFR-GOV-003` | Role-scoped filtering prevents non-owner data exposure |
| `NFR-GOV-006` | Per-visual source citations on boards |
| `NFR-REL-003` | Graceful degradation of live surfaces on dependency failure |
| `NFR-AI-001` | Agent plane outputs remain advisory |
| `NFR-MAINT-001` | Work stays within the experience (app) lane |

If implementation introduces a new requirement, `docs/PRD.md` §7 is updated in
the same PR.

---

## 17. Definition of done

* [ ] Five-plane shell on `react-router-dom` v6 with Main filling the frame.
* [ ] Curavias light + dark theme wired, persisted, brandkit-sourced.
* [ ] Header controls present (role, hospital, language, theme, user) + brand.
* [ ] Flat nav with collapse and bottom-pinned Settings.
* [ ] Start / Main boards / CSA cockpit / Backstage widgets / Settings built.
* [ ] Role dropdown + RBAC access lens (narrow-only) gating scope/nav/boards/ceiling.
* [ ] EN/DE/FR/IT with refresh-on-switch and full key coverage.
* [ ] Docked context-aware agent plane with orchestrator switch + ceiling badge.
* [ ] Footer refresh picker (live surfaces only) + app version.
* [ ] Unit + e2e + a11y tests green; `tsc --noEmit` clean.
* [ ] All CI checks pass; docs version-bumped and lint-clean.

---

## 18. References

* Mockup (validated): `sprint-20-curavias-ux-mockup.html` (session artifact)
* Sprint doc: [`sprint-20-curavias-ux-redesign.md`](../../sprints/sprint-20-curavias-ux-redesign.md)
* Plan: [`2026-07-17-sprint-20-curavias-ux-plan.md`](../plans/2026-07-17-sprint-20-curavias-ux-plan.md)
* Brandkit: `docs/brandkit/` (color system + tokens)
* App: `apps/hcc-app-fluent/`
* Agent registry: [`AGENTS.md`](../../../AGENTS.md)
* PRD: [`docs/PRD.md`](../../PRD.md)
