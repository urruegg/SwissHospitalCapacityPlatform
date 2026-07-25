# Sprint 27 — Curavias App UX Polish (OOA reference vertical)

| Field | Value |
|-------|-------|
| **Version** | 1.3.0 |
| **Date** | 2026-07-25 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | In progress (paused 2026-07-25; review + action plan 2026-07-26) |
| **Previous Version** | 1.2.0 (session 2026-07-25 log + backlog) |
| **Design spec** | [`docs/superpowers/specs/2026-07-24-sprint-27-curavias-ux-polish-design.md`](../superpowers/specs/2026-07-24-sprint-27-curavias-ux-polish-design.md) |
| **Implementation plan** | [`docs/superpowers/plans/2026-07-24-sprint-27-curavias-ux-polish-plan.md`](../superpowers/plans/2026-07-24-sprint-27-curavias-ux-polish-plan.md) |
| **Predecessors** | Sprint 20 (5-plane shell) · Curavias app prototype-parity · Sprint 25 / #276 (mockup ↔ app parity) |
| **Owner agent** | [`ux-design-agent`](../../agents/ux-design-agent/AGENT.md) |
| **Workflow** | Trunk-based parallel sprints — [`docs/DEV_WORKFLOW.md`](../DEV_WORKFLOW.md) v1.0.0 + ADR-0038 |
| **Tracker issue** | [#365](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/365) (epic) |

> **Multi-sprint parallel-work note.** Per `docs/DEV_WORKFLOW.md`: `main` is the
> trunk; this sprint runs on its own worktree `sprint-27/curavias-ux-polish`
> created off `main` (never stacked on another sprint's branch). Spec + this doc +
> plan land on `main` before execution. One issue → one branch → one squash PR; CI
> is the merge gate; a human merges. Other workers see this sprint through the
> tracker issue (Appendix A) and the `sprint-27` label.

---

## 1. Sprint goal

Deliver a **fully polished, brand- and Fluent-aligned OOA operator experience** in the
internal Curavias app (`apps/hcc-app-fluent`, app.curavias.ch), plus a reusable **codified
design system + style-guide doc + in-app brand gallery** and an **SIT-connected local
visual-verify loop** — establishing the recipe that later sprints apply to the remaining
role boards.

**Success shape:**

* A local dev loop runs the app against **SIT**, opened in a **VS Code browser tab** whose
  context is **shared with GitHub Copilot** via the read-only `playwright-mcp` server, with
  an *edit → hot-reload → re-snapshot → axe-scan* cycle.
* A **design-system module** (semantic tokens + component recipes) is the single styling
  source; a **style-guide doc** and an **in-app `/brand` gallery** codify it.
* The **OOA reference vertical** (Start teaser → Occupancy board → agent plane → shared
  five-plane chrome) meets the per-screen acceptance bar.
* All unit / e2e / a11y suites and the production build pass; before / after evidence is
  attached per screen.

---

## 2. Source baseline

1. [Sprint 27 design spec](../superpowers/specs/2026-07-24-sprint-27-curavias-ux-polish-design.md) — approach, M0 loop, design system, OOA vertical, acceptance bar, backlog.
2. [Sprint 27 implementation plan](../superpowers/plans/2026-07-24-sprint-27-curavias-ux-polish-plan.md) — milestone-by-milestone TDD tasks (M0–M8).
3. [PRD](../PRD.md) — FR/NFR source of truth (see design spec §16 traceability; new `FR-UX-*` / `NFR-UX-*` family).
4. `apps/hcc-app-fluent` — the internal app being polished.
5. `docs/brandkit/` — Curavias theme tokens, colour ramps, icon assets.
6. Sprint 25 / #276 parity baseline (assumed merged to `main`).

---

## 3. Sprint scope

| # | Task | Deliverable | DoD |
|---|------|-------------|-----|
| M0 | SIT-connected shared-context loop + runbook | `docs/runbooks/curavias-ux-local-verify-loop.md`; green baseline capture | Loop documented; `dev`/`test:e2e`/`test:a11y` green on OOA baseline |
| M1 | Design-system module | `src/theme/design-system/{tokens,recipes,index}.ts` + unit tests | Tokens + recipes exported; tests pass |
| M2 | App style-guide doc | `docs/brandkit/curavias-app-style-guide.md` incl. heuristic checklist | Published + versioned; lint-clean |
| M3 | In-app `/brand` gallery | `src/workspaces/brand/BrandGalleryView.tsx` + route | Renders all tokens/states; axe-clean |
| M4 | Shared five-plane chrome polish | `shell/**`, `copilot-drawer/**`, `copilot-rail/**` consume design system | Acceptance bar met; a11y green |
| M5 | OOA Start teaser polish | `workspaces/start/StartView.tsx` | Acceptance bar met; evidence attached |
| M6 | OOA Occupancy board polish | `workspaces/main/boards/occupancy/OccupancyBoard.tsx` | Acceptance bar met; evidence attached |
| M7 | OOA agent-plane context polish | `copilot-drawer/**`, `copilot-rail/**` | Acceptance bar met; evidence attached |
| M8 | Integration + backlog handoff + closeout | Full a11y/e2e/build green; PRD + ADR + backlog | All gates green; docs bumped |

---

## 4. Key decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | **Successor to parity** — start from the merged Sprint 25 / #276 baseline on `main` | Avoids editing the RoleBoard / badge / shell seams #276 is actively changing; polish builds on functional parity. |
| D2 | **Approach A** — Fluent v9 token overlay + in-app `/brand` gallery route (no Storybook, no separate package) | Reuses the existing Vite / Fluent / Playwright stack with near-zero new deps; the gallery is itself an axe target. Recorded in ADR-00NN. |
| D3 | **M0 first** — the SIT-connected shared-context loop is a formal deliverable, not an assumption | Every screen polish depends on the tight visual-verify loop; document it once, reuse it everywhere. |
| D4 | **OOA reference vertical this sprint + ordered backlog for the rest** | Realistic DoD; the OOA vertical locks every pattern the backlog reuses; compounding quality over a shallow full sweep. |
| D5 | **Not pixel-parity** — "as close as the Fluent UI stack reasonably allows" | Extend Fluent to a sensible acceptance level rather than fighting the framework; the heuristic checklist + AA gate define "done". |
| D6 | **Internal app only** — public site `apps/curavias-web` and any Astro pattern are out of scope | The internal app must not adopt Astro-site design; strict experience-lane boundary. |
| D7 | **Real-data linkage (in-sprint extension, 2026-07-25)** — wire the header controls to live data at the user's direction: hospital selector from the anonymized Curavias tenant master data, role model to the real 17 Entra app roles, MSAL sign-in/out + read-only Demo Guest | Verifies the mockup hypotheses against the underlying data. Consumes existing master data + MSAL only (no data-contract or infra change); extends the pure-visual scope into the identity/data lanes. |

---

## 5. Definition of done

* [ ] M0–M8 committed on the `sprint-27/curavias-ux-polish` implementation branch.
* [ ] SIT-connected shared-context local loop works and is documented in a runbook.
* [ ] Design-system module is the single styling source for the polished OOA surfaces; guard
      test green.
* [ ] Style-guide doc published with the reusable heuristic checklist; `/brand` gallery
      renders all tokens + component states and is axe-clean.
* [ ] Shared five-plane chrome + full OOA vertical (Start teaser, Occupancy board, agent
      plane) meet the acceptance bar (heuristic checklist + WCAG AA + before/after evidence).
* [ ] `npm run lint`, `npm run test`, `npm run test:e2e`, `npm run test:a11y`, `npm run build`
      all pass.
* [ ] No public-site / Astro pattern; no data / agent-contract / infra change; no PHI.
* [ ] `FR-UX-001`..`FR-UX-006` + `NFR-UX-001`..`NFR-UX-004` in `docs/PRD.md` §M + Traceability
      Matrix; ADR-00NN merged; PR lists the FR/NFR IDs; lane = Experience; infra / security /
      compliance impact = none.
* [ ] Ordered backlog handed off; design spec + this sprint doc `Status` moved to `Delivered`
      only after the validation checklist is fully green.

---

## 6. Session log

### Sprint achievements to date (2026-07-25)

Delivered across Sessions 1–3 on `sprint-27/curavias-ux-polish`:

* **Foundation (M0–M3):** SIT-connected shared-context verify loop + runbook; codified
  design-system module (tokens + recipes); app style-guide doc; in-app `/brand` gallery.
* **OOA reference vertical:** ward-forecast table (full-width, ontology drill-down, icon-only
  colour-coded Flag/Trend, narrowed drill-down column); external + internal Signals panel
  (Trust-A + live/simulated provenance); capacity-flow (Signals → Streams → Recommendation);
  brand RAG badges; patient-journey MAIN tab order.
* **Frame / M365 alignment:** full-viewport five-plane shell; header selectors as icon
  menu-buttons; M365-Copilot left nav (Demo/User switch, light selected background); Copilot
  pane as a lower-right FAB + M365-style input pill.
* **Copilot experience:** official Microsoft Copilot mark (replacing the custom sparkle) +
  brandkit icons; agent chat replies rendered as **grounded artefacts** through the shared
  `RecoPanel` block stack (one artefact vocabulary for proactive reco + conversational reply).
* **Real-data linkage (D7):** hospital selector from the anonymized Curavias tenant master
  data with working selection; role model adopting the real 17 Entra app roles; MSAL
  sign-in/out with a read-only Demo Guest fallback.
* **Verification:** `tsc` clean throughout; unit suite **400 passed**; **4 pre-existing
  `start-view` redirect-race failures** remain (documented; not regressions).

Open (M8 closeout, next): full `test:e2e` / `test:a11y` (axe); resolve the 4 `start-view`
failures; ADR-00NN (Approach A); PRD `FR-UX` / `NFR-UX` status → Delivered; rebase onto
`main`; PR to #365. Plus the new **data-access / IQ-layer** work (§8).

### 2026-07-24 — Session 1 (OOA board + frame polish)

Executed subagent-driven from the `sprint-27/curavias-ux-polish` worktree using the
SIT-connected shared-context loop (local app + Playwright MCP in a VS Code tab). Commits on
`sprint-27/curavias-ux-polish`, newest first:

| Commit | Summary |
|--------|---------|
| `4440b76` | Status/level badges use brand RAG colours (`RagBadge`) to match the Flag/Trend amber |
| `2818014` | Filled (full-colour) status/level badges |
| `7bd2c73` | OOA actionable-insight 3-column flow (Signals → Streams → Recommendation) + signal & icon-only provenance icons |
| `d9100ea` | Ward table full-width + ontology drill-down + icon-only colour-coded Flag/Trend |
| `464da5f` | Frame polish — header elevation + navigation surface with pinned Settings |
| `98bb1c3` | OOA external+internal Signals panel (Trust-A + live/simulated) + 2 unit tests |
| `fc10719` | Patient-journey MAIN tab order (CSA last) + OOA card surfaces + ward-row interactions |
| `cbbb9bd` / `275de02` / `cb3fb7a` / `5fa059b` | M1 design-system module · M0 loop runbook · M2 style-guide · M3 `/brand` gallery |
| `8be073e` | Approved planning docs (spec + plan + this doc) + PRD `FR-UX`/`NFR-UX` |

Verified: `tsc` clean on every increment; `ward-forecast-table`, `capacity-flow-diagram`,
`signals-panel` unit tests pass; light + dark mode confirmed live in the shared tab. Branch
is ahead of `origin/main` (rebase at closeout).

Milestone status: M0–M3 done; M4 frame done (header + nav; footer/agent reviewed); OOA
vertical board + Signals/actionable-insight redesign done; Start-teaser polish still open.
Not yet run: full unit suite, `test:e2e` / `test:a11y` (axe), ADR-00NN, PRD status flip,
rebase, PR.

### 2026-07-25 — Session 2 (frame + M365 Copilot alignment)

Delivered backlog items 1–4. Commits on `sprint-27/curavias-ux-polish`, newest first:

| Commit | Summary |
|--------|---------|
| `85bf7bf` | FluentProvider fills viewport height (removes the bottom white band) |
| `730bead` | Copilot pane — floating lower-right FAB when collapsed + M365-style input pill |
| `7217628` | M365-Copilot nav — Demo/User switch on top, wider rail, light selected background |
| `77325af` | Header selectors as icon menu-buttons (leading icon + fit-to-text) |
| `c5e89a7` | Full-viewport shell via global reset (no body-margin gap) |

Verified: `tsc` clean each step; `header-plane`, `navigation-plane`, `agent-plane` unit
tests pass; light + dark confirmed live. Item 5 remains (dark re-verify done; axe scan,
ADR-00NN, PRD status flip, rebase, PR).

**Known pre-existing failures (not regressions; fix at M8):** `shell.test` + `router.test`
StartView `start-view` testid races the `/`→`/start` redirect under jsdom — fix with
`findByTestId`; the app boots to Start correctly in the browser.

### 2026-07-25 — Session 3 (chat artefacts, official Copilot mark, header real-data linkage)

Extended the polish into **real-data linkage** at the user's direction (see D7). Commits on
`sprint-27/curavias-ux-polish`, newest first:

| Commit | Summary |
|--------|---------|
| `be13469` | Role model adopts the real 17 Entra app roles + legacy aliases (selector reflects the group-based app-role assignment) |
| `d6f06d0` | Real MSAL sign-in/out with a read-only Demo Guest fallback (claims bridged from the active account) |
| `e6d874a` | Hospital selector shows the anonymized Curavias tenant names (Uniklinik CuraNova / Kantonsspital Curalp / Spital Vialta) — bug fix |
| `c8b43b1` | Hospital selector sourced from real Entra org data + working selection (re-scopes the boards) |
| `b7cc513` | Narrow ward-forecast drill-down column to widen the data columns |
| `c86132f` | Official Microsoft Copilot mark for the Copilot affordance (FAB + header) + brandkit icons |
| `302f679` | Agent chat replies render as grounded artefacts (Foundry structured reply) via the shared `RecoPanel` block stack |

Verified: `tsc` clean each step; full unit suite = **400 passed**; hospital / role / sign-in /
Copilot-mark / chat-artefact changes confirmed live in the shared tab.

**Correction to the Session 2 note:** `findByTestId` alone does **not** clear the 4
`start-view` failures (`shell.test` ×1, `router.test` ×3) — they persist after the async
query, so M8 needs a deeper look at the `/`→`/start` redirect / loader under jsdom, not just
an async matcher. Not a regression (the app boots to Start in the browser); this session added
zero new failures.

## 7. Next-session backlog (general wireframe + M365 Copilot alignment)

Captured 2026-07-24. **Items 1–4 delivered in Session 2 (2026-07-25); item 5 remains.**

1. **Wireframe / window fit** — the shell does not fill the window on the top/left/right and
   the footer band is too tall. Make the five-plane grid use the full viewport and right-size
   the footer. Cross-check Microsoft Teams, M365 Copilot, and Outlook (all Fluent UI React).
2. **Header dropdown selectors** — add a leading icon in front of each dropdown (Language,
   Hospital, Role) as done for the User account; size each dropdown to fit the max
   option-text length (no clipping, no over-wide control).
3. **Copilot pane** — collapsed state shows a **Copilot icon-only overlay in the lower-right**;
   expanded state shows the chat panel. Refine the input ("Ask the agent…" + send) to match the
   M365 Copilot "Message Copilot" input (see reference screenshot).
4. **Navigation → M365 Copilot style** — align the left nav to the M365 Copilot layout
   (New chat / Search / Library / Tasks / Notebooks / Agents / Pinned pattern). The top
   Chat/Cowork switch maps to our **Demo / User** mode toggle. A selected menu item should
   show a **light selected-background**.
5. **Acceptance-bar closeout** — dark-mode re-verify on the final layout + `axe` a11y scan;
   then M8 (full suite, ADR-00NN, PRD status → Delivered, rebase onto `main`, PR to #365).

---

## 8. Data-access / IQ-layer backlog (next work in this sprint)

Captured 2026-07-25 for the **2026-07-26 review + action plan**. Design doc:
[`docs/architecture/app-iq-data-access-pattern.md`](../architecture/app-iq-data-access-pattern.md)
(Draft for review).

**Finding.** The app has two data paths: the **conversational** path is IQ-governed (Foundry
Agent → Fabric Data Agent → semantic model over Gold), but the **structured board** path reads
Gold directly via `golden-source-client` (or simulated in demo) and bypasses the IQ
semantic / ontology layer. So "we always go through the IQ layer" is only partially true today.

**Goal.** Establish a single **IQ data-access pattern** so every app read is
golden-evidence-grounded via Fabric IQ / Foundry IQ, with provenance + citations always visible.

**Proposed first slices (confirm order at the review):**

1. ADR "App data access via the IQ layer" (precedence + evidence envelope).
2. `src/data/iq-client.ts` — single ingress + evidence envelope; refactor
   `golden-source-client` + `agent-manifest` to call it (keep the simulated fallback).
3. Route board reads through the Fabric Data Agent / semantic-model surface (board KPIs carry
   `hcp:*` citations, matching the chat path).
4. ESLint guard: only `iq-client` may hold a `fetch` / endpoint import.
5. `grounding degraded` UI affordance + golden tests for the envelope.

**Lane / impact.** Data lane; behind the existing `provenance` contract + golden tests; no
data-contract or infra change implied by the app-side gateway. PHI stays out (ADR-0013/0016);
Fabric IQ PROD / PHI paths stay GA-gated (ADR-0014).

---

## Appendix A — Tracker issue seed

**Title:** `Sprint 27 — Curavias App UX Polish (OOA reference vertical) [epic]`

**Body:**

* **Goal:** polished OOA operator experience + codified design system + SIT-connected
  visual-verify loop; recipe for the remaining role boards.
* **Scope:** internal app `apps/hcc-app-fluent` only; OOA vertical + shared chrome; backlog
  for the rest. Out: public site / Astro; backend / data / agent / infra; PHI.
* **Design spec:** `docs/superpowers/specs/2026-07-24-sprint-27-curavias-ux-polish-design.md`
* **Plan:** `docs/superpowers/plans/2026-07-24-sprint-27-curavias-ux-polish-plan.md`
* **Requirements:** `FR-UX-001`..`FR-UX-006`, `NFR-UX-001`..`NFR-UX-004`.
* **Milestones:** M0 loop · M1 design system · M2 style-guide · M3 gallery · M4 chrome ·
  M5 Start teaser · M6 Occupancy board · M7 agent plane · M8 closeout.
* **Labels:** `sprint-27`, `experience-lane`, `epic`.
