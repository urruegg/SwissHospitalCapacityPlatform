# Curavias Start plane — narrative refactor design

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-07-31 |
| **Author** | Urs Rüegg |
| **Status** | Implemented — revised (see §6) |
| **Previous Version** | 1.0.0 (initial pre-Sprint-37 pattern-only plan; §6 records the delivered Option B) |

## 1. Problem

The Backstage plane was refactored onto a reusable narrative pattern system
(P13–P17 in [curavias-ux-patterns.md](../../brandkit/curavias-ux-patterns.md)):
`NarrativeShell` + eyebrow `SectionHeader` + full-width sticky section nav +
one-per-screen storytelling + context-click-to-Copilot-rail. The **Start plane**
still uses a bespoke inline layout (narrow 860px column, default-variant
`SectionHeader`, content-width nav). It should adopt the same anchored patterns
so Start and Backstage read as one product, and its C-level story should track
the [Curavias-Frontier-Showcase mockup](../ideas/Curavias-Frontier-Showcase.html).

## 2. Decision

**Pattern-only migration, mockup-aligned order + copy.** Keep every existing
Start section and its live data; restructure onto `NarrativeShell`; reorder to
the mockup's C-level narrative; adopt the mockup eyebrow/title copy.

### 2.1 Section order (mockup narrative)

| # | Section | Mockup anchor |
|---|---------|---------------|
| 0 | Welcome (intro) | Hero — "The hospital of the future is a Frontier Firm" |
| 1 | Operating model (`org-work`) | "The idea in one minute · org chart → work chart" |
| 2 | Hospitals (`hospitals`) | "Key visual 1 · Organisation · Three hospitals" |
| 3 | Care path (`care-path`) | "Key visual 2 · Patient journey · One patient, one flow" |
| 4 | Capacity (`capacity`) | "The first frontier · capacity, live" (live proof) |
| 5 | 90-day (`ninety-day`) | "The first frontier · Capacity Forecast, live in 90 days" |
| 6 | Why now (`why-now`) | Bridge — the change argument before the decision |
| 7 | Value (`value`) | "The decision · Business Value Assessment" |
| 8 | Get started (`get-started`) | "Main · the live operational product" (role boards) |

`leadingGroupCount = 2` groups Welcome + Operating model on the opening screen;
sections 2–8 fill one screen each.

### 2.2 Intro treatment

The current hero becomes intro section 0 via `NarrativeShell`:
`introTitle = "Curavias"` (kept short — see §3 guard), `introEyebrow =
"Start · for hospital & healthcare C-level · 5–10 min"`, `introDescription =
mission (Frontier-Firm framing)`, `introExtra = { simulated-data disclaimer
MessageBar, demo/user mode badge }`.

### 2.3 Component changes

- `NarrativeShell` gains a `navTestIdPrefix` prop (default `backstage-nav`);
  Start passes `start-nav`. Backstage is unchanged.
- The three frontier sections (`OrgWorkChartSection`, `ThreeHospitalsSection`,
  `NinetyDaySection`) drop their own outer `id` wrapper (the shell supplies the
  section `id`), switch to `variant="eyebrow"`, and keep their
  `start-org-work` / `start-hospitals` / `start-ninety-day` testids on the
  content wrapper.
- `StartView` renders `<div data-testid="start-view"><NarrativeShell …/></div>`;
  the bespoke hero, sticky nav, and `useScrollSpy` are removed (the shell owns
  them). The `siteCapacity` load stays in `StartView` and feeds the capacity +
  care-path renders via closures.

## 3. Constraints (test contract — must hold)

The 19 `start-view.test.tsx` assertions check **testids + data text**, not
header copy, so header restyling is free. Guards:

- Exactly **one** heading may contain "Curavias" (the intro). No section title
  (`h2`) may contain "Curavias" → `get-started` title is "Step into a role
  board", not the mockup's "…Curavias app".
- `getByText(/Today/i)` and `getByText(/With Curavias/i)` must stay **unique**
  (the why-now table column headers) → no eyebrow/title/description copy may
  contain those phrases.
- Preserve testids: `start-view`, `start-mode-badge`, `start-capacity-teaser`,
  `start-capacity-provenance-badge`, `start-value-tiles`, `start-copilot-count`,
  `start-why-now`, `start-patient-path`, and `launch-*`.
- Preserve data text: `kpi.measure` per tile, `ROM estimate`, BVA `asOf` date,
  copilot count = `LAUNCHER_TILES.length`, `illustrative` captions,
  `Medicine A` / `102` from the mocked capacity summary, `simulated` provenance.

## 4. Verification

`tsc --noEmit`, mojibake + markdownlint on touched docs/JSON, `vitest run
tests/unit/start-view.test.tsx` (must stay green), and a browser pass at
`http://localhost:5173/` for the narrative + one-per-screen behaviour.

## 5. Follow-ups (out of scope)

DE/FR/IT i18n keys for the new eyebrow/title copy (currently en-only); apply
the same P13–P17 conformance matrix row for Start in the patterns doc.

## 6. Delivered outcome (revises §2–§5)

After this spec was drafted, the **Sprint 37 "Start (Frontier Firm)"** work
(dedicated worktree `sprint-37/start-frontier`, design
[2026-07-29-sprint-37-curavias-start-frontier-design.md](2026-07-29-sprint-37-curavias-start-frontier-design.md))
was reviewed and found to be a **complete, tested, four-language** Start rebuild.
Rather than the pattern-only migration of the *old* Start (§2), we **incorporated
Sprint 37's content and re-layered it onto the shell** (the "Option B" reviewed
with the user). §2–§4 above describe the superseded plan; the delivered surface is:

- **Sections (7, Sprint 37 blueprint):** hero + squeeze · org → work chart ·
  CIO why-now (seven decisions) · three hospitals · patient-path launcher ·
  90-day · BVA decision — with Sprint 37's data bindings (`bva-evidence.ts`,
  live `siteCapacity`, `LAUNCHER_TILES` + RBAC) and `start.frontier.*` i18n in
  **en/de/fr/it**. The **Product Owner Agent** rail is docked on `/start`.
- **Presentation:** `StartView` composes the sections through `NarrativeShell`
  (P13-P17) — an `overview` intro (page title "Curavias Start" + eyebrow + lead +
  synthetic/advisory/no-PHI guardrails) + eyebrow `SectionHeader` per content
  section + sticky nav + scrollspy + one-per-screen (`leadingGroupCount={2}`).
  Each section wrapper is `<section data-start-section={id} data-testid="start-{id}">`.
- **Test contract (supersedes §3):** Sprint 37's `start-view.test.tsx` (heading
  "Curavias Start"; the three guardrails; the mode badge; the **seven
  `data-start-section` sections in `START_SECTIONS` order**; no legacy
  launcher/teaser testids) + the frontier component tests + `backstage-view`.
  **479 unit tests green; `tsc --noEmit` clean.**
- **Landed as** commit `1843f15` on `sprint-27/curavias-ux-polish` (pushed).

### 6.1 Remaining follow-ups

- Run the Playwright gate `tests/e2e/start.spec.ts` (contracts preserved; not run).
- DE/FR/IT copy for the P14 **eyebrow kickers** (section titles/bodies already
  localized in all four locales; only the eyebrows are English inline defaults).
- Review + polish pass with the user (parked).
