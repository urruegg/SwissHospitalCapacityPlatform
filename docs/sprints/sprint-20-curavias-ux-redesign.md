# Sprint 20 — Curavias App UX Redesign (five-plane Teams-style shell)

| Field | Value |
| ----- | ----- |
| **Version** | 1.2.0 |
| **Date** | 2026-07-23 |
| **Author** | @urruegg |
| **Status** | Delivered |
| **Previous Version** | 1.1.0 (added §6 references, delivered status) |

> **Sprint theme.** Rebuild the `hcc-app-fluent` React app as a Teams-style five-plane shell (Header / Navigation / Main / Agent / Footer) themed with the Curavias brandkit, add a role dropdown that acts as an RBAC access lens, four-language i18n (EN/DE/FR/IT), a dockable context-aware agent plane, and Start/Main/CSA/Backstage/Settings surfaces.

---

## 1. Sprint goal

Deliver a coherent, brand-aligned, accessible operator experience for Curavias by replacing the ad-hoc shell with a Teams-style five-plane layout, wiring role-based access as a first-class UX lens, and preparing the app for multi-language demo use.

**Success shape:**

* Five persistent planes (Header, Navigation, Agent, Footer) surround a max-space Main outlet driven by `react-router-dom` v6.
* The header exposes Theme, Language, Hospital, Role, and User controls; the Role dropdown narrows hospital scope, gates navigation and boards, and sets the agent action ceiling.
* Curavias light + dark themes replace the Helvion theme and pass the WCAG AA accessibility gate.
* EN/DE/FR/IT are selectable and persisted (DE default, EN fallback).
* The agent plane is dockable (icon-only ↔ open) and context-aware across all surfaces.
* All unit/integration/e2e/a11y suites and the production build pass.

---

## 2. Source baseline

1. [Sprint 20 Design Spec](../superpowers/specs/2026-07-17-sprint-20-curavias-ux-design.md) — five-plane architecture, theme, RBAC lens, i18n, agent plane
2. [Sprint 20 Implementation Plan](../superpowers/plans/2026-07-17-sprint-20-curavias-ux-plan.md) — milestone-by-milestone TDD tasks (M0–M9)
3. [PRD](../PRD.md) — FR/NFR source of truth (see spec §16 traceability)
4. `apps/hcc-app-fluent` — the existing React/Fluent-UI-v9 app being redesigned
5. `docs/brandkit/` — Curavias theme tokens, colour ramps, and icon assets
6. [AGENTS.md §1 Registry](../../AGENTS.md) — agent context map for the agent plane

---

## 3. Sprint scope

| # | Task | Deliverable | DoD |
|---|------|-------------|-----|
| M0 | Brandkit intake + green baseline | `docs/brandkit/**` committed; baseline suite recorded | Committed + baseline green |
| M1 | Curavias theme | `src/theme/curavias-theme.ts` + tokens + persisted light/dark | Helvion removed; tests pass |
| M2 | Router shell | `AppShell` + route table (`/start` default, `*`→`/start`) | Planes render; tests pass |
| M3 | Header + RBAC lens | `rbac-model.ts` + role dropdown + 5 header controls | Narrow-only lens; tests pass |
| M4 | Navigation plane | Five role-gated destinations (disabled-not-hidden) | Legacy rail removed; tests pass |
| M5 | Content surfaces | Start, Main, CSA, Backstage, Settings behind routes | All surfaces render; tests pass |
| M6 | Four-language i18n | `fr.json` + `it.json`; EN/DE/FR/IT switch | Persisted; tests pass |
| M7 | Agent plane | Dockable, context-aware, ceiling badge | Icon↔open; tests pass |
| M8 | Footer plane | App version + refresh-rate selector | Version define; tests pass |
| M9 | Integration + e2e + a11y + close | Playwright shell + axe on 5 surfaces + full build | All gates green |

---

## 4. Key decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Approach B — full `react-router-dom` v6 layout route | A single layout route renders the four planes around `<Outlet/>`; routes are addressable, testable, and match Teams-style navigation. Chosen over an ad-hoc state-driven switch. |
| D2 | Role dropdown is an RBAC access lens, not a preference | The active role narrows hospital scope, gates nav + boards + widgets, and sets the agent ceiling. This keeps demo access model honest and observable. |
| D3 | In-session role switching only narrows to held roles | Switching never elevates beyond the user's Entra `HCC.*` claims; it only restricts to a lower-privilege view. Prevents demo privilege escalation. |
| D4 | Curavias green (`#17B890`) primary with dark text | Green fails AA with white text (2.53:1); dark text `#0E0F11` on green is AAA (7.57:1). White-text buttons use secondary blue `#365B7D` (AAA). Baked into the theme so a11y passes by construction. |
| D5 | DE default, EN fallback across EN/DE/FR/IT | Matches the Swiss-German operator baseline while covering all four national languages for demo. |

---

## 5. Definition of Done

* [ ] M0–M9 tasks committed on a `sprint20/*` implementation branch
* [ ] Five-plane shell is the only entry path; `AppRail`/`TopBar`/`WorkspaceRouter` removed
* [ ] Role dropdown acts as a narrow-only access lens (nav + hospital scope + boards/widgets + agent ceiling)
* [ ] Curavias light + dark themes replace Helvion; WCAG AA verified by the a11y gate
* [ ] EN/DE/FR/IT selectable and persisted (DE default, EN fallback)
* [ ] Agent plane dockable and context-aware across all five surfaces
* [ ] `npm run lint`, `npm run test`, `npm run test:e2e`, `npm run test:a11y`, `npm run build` all pass
* [ ] PR lists the FR/NFR IDs from the design spec §16; lane = Experience; infra/security/compliance impact = none
* [ ] Design spec + this sprint doc `Status` moved to `Delivered` only after the validation checklist is fully green
* [ ] All CI checks pass (markdown lint + mojibake on docs; app build/test on code)

---

## 6. References

* Design: [`2026-07-17-sprint-20-curavias-ux-design.md`](../superpowers/specs/2026-07-17-sprint-20-curavias-ux-design.md)
* Plan: [`2026-07-17-sprint-20-curavias-ux-plan.md`](../superpowers/plans/2026-07-17-sprint-20-curavias-ux-plan.md)
* Interactive mockup (session artifact, not committed): validated five-plane wireframe with role dropdown
* Issue: [#245 — Sprint 20: Curavias App UX Redesign](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/245)

### Follow-on: app prototype parity (issue #305)

* Design: [`2026-07-21-curavias-app-prototype-parity-design.md`](../superpowers/specs/2026-07-21-curavias-app-prototype-parity-design.md)
* Review outcome (evidence-driven parity + live-data requirements): [`2026-07-23-curavias-app-parity-review-outcome.md`](../superpowers/specs/2026-07-23-curavias-app-parity-review-outcome.md)
* Full findings dossier (screen-by-screen evidence): [`2026-07-23-curavias-app-parity-findings.md`](../superpowers/specs/2026-07-23-curavias-app-parity-findings.md)
* Issue: [#305 — Sprint 20: App parity build](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/305)
