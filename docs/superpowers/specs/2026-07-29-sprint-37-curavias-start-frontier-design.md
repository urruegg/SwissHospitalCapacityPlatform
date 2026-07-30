# Sprint 37: Curavias Start (Frontier Firm) content intake - Design

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-29 |
| **Author** | Urs Rueegg (with GitHub Copilot) |
| **Status** | Approved for planning |
| **Previous Version** | n/a (initial design) |
| **Sprint** | Sprint 37 - Curavias Start content intake (slice 1 of 2) |
| **Issue** | [#546](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/546) |
| **Lane** | Experience (`apps/hcc-app-fluent/**`) |

---

## 1. Goal

Rebuild the Curavias App **Start** surface from the product-marketing draft plus the
clickable prototype's patient-path, delivered by **guided rapid prototyping** against
the local app. This is **slice 1 of 2**: Start now, Backstage content-intake as a
separate follow-on sprint. **Main is untouched.** Backstage keeps the **Digital
feedback loop** ([Sprint 35](2026-07-29-sprint-35-curavias-digital-feedback-loop-design.md),
merged) and **Solution design** ([Sprint 36](2026-07-29-sprint-36-curavias-solution-design-backstage-design.md),
PR #541) sections.

The existing Start content is replaced (per direction), but the **operational entry
into Main is preserved** - carried by the patient-path, which doubles as the role
launcher.

## 2. Sources and content BOM

| Source | Role |
| ------ | ---- |
| `docs/superpowers/ideas/Curavias-Frontier-Showcase.html` | PM Frontier-Firm C-level narrative (hero, org->work chart, three hospitals, 90-day, BVA) |
| `docs/superpowers/ideas/curavias-ux-ideas/prototype/surfaces/00-start.html` | Clickable prototype Start: hero + squeeze card, CIO 7-decisions table, and the **patient-path role launcher** |
| `apps/hcc-app-fluent/src/workspaces/start/StartView.tsx` (current) | Real-data bindings to reuse: `bvaHeadlineKpis`, live `siteCapacity`, `LAUNCHER_TILES`, RBAC via `useRoleLens` |

These are design evidence under `docs/superpowers/ideas/` and are not shipped; the app
re-expresses their content as Fluent v9 + Curavias design-system components.

## 3. Approved design decisions

- **D1 - Replace Start content** with the Frontier-Firm narrative; do not reuse the
  existing Start copy.
- **D2 - Patient-path is the role launcher** (Option A): the wave-band 6-stop journey
  is the operational entry into `/main/<role>`, RBAC-gated - no separate tile grid.
- **D3 - Blueprint order** (locked): Hero -> Org/work chart -> CIO why-now -> Three
  hospitals -> Patient path -> 90-day -> BVA decision.
- **D4 - Real-data bindings**: metrics and BVA read from `bva-evidence.ts`; the squeeze
  card reads live `siteCapacity`. **No inline literals** - every number carries a ROM
  label + provenance.
- **D5 - PO Agent rail on Start** (`FR-POA-002`): dock `product-owner-agent` on the
  Start surface, grounded/cited/advisory.
- **D6 - Guardrails visible**: synthetic/no-PHI and advisory-only remain on-screen;
  WCAG 2.1 AA + Fluent heuristics.
- **D7 - Method**: guided rapid prototyping section-by-section against the local app,
  refined via discussion (the reviewed BOM is the content contract).

## 4. Section blueprint

| # | Section | Content | Data / interaction |
| - | ------- | ------- | ------------------ |
| 1 | **Hero + squeeze card** | Frontier-Firm hook, value line, 3 metrics, "Site capacity - next 72h" sparkline, trust pills, disclaimer | metrics <- `bvaHeadlineKpis`; squeeze <- live `siteCapacity`; CTAs -> Backstage |
| 2 | **Org chart -> work chart** | Humans / Agents / On-demand + Frontier-Firm-principle -> Curavias map | static content |
| 3 | **CIO challenger - why now** | The 7 operational-decisions table (Today vs Curavias preview) | static content |
| 4 | **Three hospitals as Frontier Firms** | CuraNova / Curalp / Vialta cards + 7-agent team roster | static; hospital scope from the org spine |
| 5 | **The Curavias patient path** (launcher) | Wave-band 6 stops (OOA, BMCA, ORSA, SBA, DCA, Recovery) + CSA/DQ spanning + HITL footer | each stop RBAC-gated -> `/main/<role>` via `LAUNCHER_TILES`; carries the golden thread |
| 6 | **90-day frontier** | Frame&Ground / Build&Prove / Operate&Scale phases | static content |
| 7 | **BVA - the decision** | KPI tiles + TCO table + value levers + sensitivity + proof + decision card | <- `bva-evidence.ts` (ROM + provenance) |

The **Product Owner Agent** rail is docked on Start throughout (Section-agnostic).

## 5. Component architecture

`StartView.tsx` is rewritten to **compose section components** (the `/start` route is
unchanged). New folder `apps/hcc-app-fluent/src/workspaces/start/frontier/`:

- `start-content.ts` - typed content model + i18n keys for the static sections
  (hero copy, work-chart, cio-decisions, hospitals, ninety-day, bva labels). No React.
- `StartHero.tsx` - hero + squeeze card; binds `bvaHeadlineKpis` + live `siteCapacity`.
- `WorkChartSection.tsx` - org -> work chart.
- `CioChallengerSection.tsx` - the 7-decisions table.
- `HospitalsSection.tsx` - three hospitals + 7-agent roster.
- `PatientPathLauncher.tsx` - the wave-band patient path **and** role launcher; reuses
  `LAUNCHER_TILES` + RBAC `useRoleLens` and navigates to `/main/<role>`.
- `NinetyDaySection.tsx` - 90-day phases.
- `BvaDecisionSection.tsx` - BVA tiles/tables; binds `bva-evidence.ts`.

Each section is a focused Fluent component using the Curavias design-system tokens +
recipes. `StartView.tsx` renders them in blueprint order and owns page layout only.

**PO rail wiring**: update `apps/hcc-app-fluent/src/shell/planes/agent-context-map.ts`
so `/start` routes to `product-owner-agent` (today Start falls through to
`orchestrator`). This satisfies `FR-POA-002` (PO rail on START + BACKSTAGE) and reuses
the existing `AgentPlane` + `useCopilotRail`.

## 6. Guided rapid-prototyping execution

Delivery is section-by-section against the running local app:

- Local app: `http://localhost:5173/start` (Vite dev server).
- Loop (`FR-UX-004`): edit a section -> hot-reload -> snapshot in the shared browser ->
  axe scan -> refine via discussion -> next section.
- Each section lands as a small commit; the section set composes the full Start.
- Content is taken from the reviewed BOM (Section 2); wording refinements are captured
  in `start-content.ts` / i18n, not hard-coded in JSX.

## 7. Data and provenance

- **Metrics** (hero): `bvaHeadlineKpis` from `apps/hcc-app-fluent/src/data/bva/bva-evidence.ts`,
  each with a `ROM estimate` label + source note.
- **Squeeze card**: `loadSiteCapacitySummary` (`golden-source-client`) - live/simulated
  `siteCapacity` with the provenance badge the app already uses.
- **BVA section**: the same `bva-evidence.ts` data product (TCO, value levers,
  sensitivity, headline KPIs), never inline literals.
- **Patient path**: labels/evidence chips are illustrative synthetic content; the
  navigation targets come from `LAUNCHER_TILES` (single source of the role routes).

Any figure that cannot be sourced from a real binding is shown as an explicit
`ROM estimate` / illustrative label, consistent with the repo's provenance rule.

## 8. Accessibility and guardrails

- Every polished section passes WCAG 2.1 AA via axe (merge gate, `NFR-UX-001`).
- Fluent v9 + M365 heuristic checklist (`NFR-UX-002`): 8-pt spacing, type ramp,
  elevation, hover/pressed/focus, explicit empty/loading/error, dark-mode parity.
- The patient-path stops are accessible buttons/links (keyboard, focus, `aria`); the
  RBAC-hidden Crisis stop follows the existing `visibleTiles` gating.
- Synthetic/no-PHI + advisory-only remain visible (disclaimer + pills).
- The PO rail keeps its grounded, cited, advisory-only, human-decides contract.
- `NFR-UX-004`: experience-lane only - no backend / data-contract / agent-prompt /
  infra change, no public-site (Astro) patterns pulled into the app.

## 9. Verification strategy

### Unit and component checks

- `start-content.ts` exposes all seven sections' content; no PHI-shaped strings.
- `StartHero` renders `bvaHeadlineKpis` values and the live `siteCapacity` peak, each
  with a provenance label (no hard-coded numbers).
- `PatientPathLauncher` renders the RBAC-visible stops and navigates to the correct
  `/main/<role>` route; the Crisis stop is hidden without the capability.
- `BvaDecisionSection` reads `bva-evidence.ts` (asserts a value equals the source, not a
  literal).

### Playwright checks

- `/start` renders the seven sections in blueprint order; the old launcher grid is gone.
- Clicking a patient-path stop navigates to `/main/<role>`.
- The PO Agent rail is present and labelled on `/start`.
- Desktop and narrow screenshots show no overlap or horizontal scroll.
- Axe reports no serious/critical WCAG 2.1 AA violation on `/start`.

### App gates

From `apps/hcc-app-fluent`:

```powershell
npm test
npm run lint
npm run build
npx playwright test tests/e2e/start.spec.ts
npx playwright test tests/e2e/a11y.spec.ts
```

## 10. Delegation model

Delivery uses `subagent-driven-development` after the plan is approved. Shared content
model + PO-rail wiring land first, then sections in parallel-safe order:

- **WS-A** - `start-content.ts` typed content model + i18n + PO-rail wiring
  (`agent-context-map`), and the `StartView` shell that composes sections.
- **WS-B** - data-bound sections: `StartHero` (metrics + squeeze) and `BvaDecisionSection`.
- **WS-C** - `PatientPathLauncher` (patient path + RBAC role launcher + navigation).
- **WS-D** - static narrative sections: work-chart, CIO why-now, hospitals, 90-day.
- **WS-E** - Playwright + axe + responsive verification.

Each worker starts from current `main`, uses TDD, runs focused checks in the local app,
and opens a human-reviewed PR. No subagent self-merges. WS-B..E depend on the WS-A
content + shell contract.

## 11. Scope and traceability

Advances existing requirements only:

- `FR-UX-001`, `FR-UX-004`, `FR-UX-005`, `FR-UX-006`;
- `FR-POA-002`, `FR-CX-006`, `FR-BVA-005`;
- `NFR-UX-001` through `NFR-UX-004`.

No new FR/NFR ID, agent prompt, backend service, data contract, Fabric asset, Azure
resource, or infrastructure change is introduced. Main and Backstage surfaces are not
modified by this slice.

## 12. Relationship to Sprint 35 / 36 and the Backstage slice

- Sprint 35 (Digital feedback loop) is merged to `main`; Sprint 36 (Solution design) is
  in PR #541. Both live in **Backstage > Story** and are untouched here.
- **Slice 2 (Backstage content intake)** - adding the PM backstage sections (B1-B6:
  Success Framework, DevSecOps loop, six lanes, review sessions, PO knowledge classes)
  alongside the feedback loop + solution design - is a separate follow-on sprint,
  brainstormed after this Start slice lands.

## 13. Definition of Done

- Start renders the 7-section blueprint in order; the existing Start content is replaced.
- The patient path works as the RBAC-gated role launcher into `/main/<role>`.
- Metrics / squeeze / BVA bind to real app data with ROM + provenance; no inline literals.
- The Product Owner Agent rail is docked on Start, grounded + advisory.
- Synthetic/no-PHI + advisory-only remain visible; WCAG 2.1 AA (axe) + Fluent heuristics pass.
- Unit/component, Playwright interaction, screenshot, and axe gates pass; `npm test`,
  `npm run lint`, `npm run build` green.
- Delivery remains experience-lane only and uses synthetic, non-PHI content.
