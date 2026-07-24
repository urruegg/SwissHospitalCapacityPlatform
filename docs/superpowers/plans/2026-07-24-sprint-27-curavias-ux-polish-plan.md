# Curavias App UX Polish (Sprint 27) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Polish the OOA operator experience in `apps/hcc-app-fluent` to Fluent v9 + Curavias brand + M365 app quality, backed by a codified design system, a style-guide, an in-app brand gallery, and an SIT-connected local visual-verify loop.

**Architecture:** A typed semantic-token + `makeStyles`-recipe overlay (`src/theme/design-system/`) on top of the existing Sprint 20 Fluent theme becomes the single styling source. An in-app `/brand` gallery renders every token/state as an axe target. Each OOA screen is refactored to consume the overlay and verified in a VS Code / Copilot shared browser context (Playwright MCP) against SIT, with a hot-reload → screenshot → axe cycle.

**Tech Stack:** React 18, TypeScript (strict), Fluent UI v9 (`@fluentui/react-components`), Vite 6, Vitest (unit), Playwright + `@axe-core/playwright` (e2e + a11y), i18next, `react-router-dom` v6.

**Status:** Approved by @urruegg 2026-07-24 — ready to execute (Sprint 27, tracker [#365](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/365)).

---

## Conventions for every task

- App root for `npm` commands: `apps/hcc-app-fluent`.
- Unit tests live in `apps/hcc-app-fluent/tests/unit/**/*.test.{ts,tsx}` (Vitest `include` in `vite.config.ts`).
- Commands: `npm run test` (Vitest), `npm run test:e2e` (Playwright), `npm run test:a11y` (axe), `npm run lint` (tsc `--noEmit`), `npm run build`, `npm run dev`.
- Commit style: Conventional Commits with a `Co-authored-by` trailer. Branch `sprint-27/curavias-ux-polish` off `main`.
- Never introduce raw pixel spacing/shadow literals in polished components — import from `src/theme/design-system`.

---

## File Structure

| File | Responsibility |
|------|----------------|
| `src/theme/design-system/tokens.ts` | Semantic tokens: `space`, `radii`, `elevation`, `motion`, `density`, `zIndex`, `focus`. |
| `src/theme/design-system/recipes.ts` | `makeStyles` recipes: `surfaceCard`, `boardGrid`, `sectionHeader`, `statTile`, `provenanceBadge`, `emptyState`, `loadingState`, `errorState`. |
| `src/theme/design-system/index.ts` | Barrel re-export of `tokens` + recipes. |
| `src/workspaces/brand/BrandGalleryView.tsx` | `/brand` route: renders every token + component-recipe state (light/dark). |
| `src/shell/router.tsx` | Add the `/brand` route. |
| `src/workspaces/start/StartView.tsx` | OOA teaser polish (consume design system). |
| `src/workspaces/main/boards/occupancy/OccupancyBoard.tsx` (+ `BoardHeader`, `WardForecastTable`, `CapacityFlowDiagram`) | OOA board polish. |
| `src/copilot-drawer/**`, `src/copilot-rail/**` | Agent-plane polish. |
| `src/shell/AppShell.tsx`, `src/shell/planes/**`, `src/shell/TopBar/**` | Shared five-plane chrome polish. |
| `docs/brandkit/curavias-app-style-guide.md` | Token→Fluent→M365 mapping + heuristic checklist. |
| `docs/runbooks/curavias-ux-local-verify-loop.md` | M0 loop runbook. |
| `docs/adr/00NN-curavias-app-design-system-overlay.md` | Approach A decision record. |
| `tests/unit/design-system-tokens.test.ts` | Token scale unit test. |
| `tests/unit/design-system-recipes.test.ts` | Recipe hook unit test. |
| `tests/unit/ooa-design-system-usage.test.ts` | Guard: polished OOA files import design-system. |

---

## M0 — SIT-connected shared-context local loop

### Task 0.1: Verify the parity baseline and branch

- [ ] **Step 1: Confirm Sprint 25 / #276 parity is on `main`**

Run: `git log --oneline -20 main | Select-String "parity|#276|sprint-25"`
Expected: parity merge commit(s) present. If absent, STOP — this sprint is a successor and must not start until parity merges.

- [ ] **Step 2: Create the worktree off `main`**

Run: `./scripts/dev/new-sprint-worktree.ps1 -Sprint 27 -Topic curavias-ux-polish`
Expected: `../wt/sprint-27-curavias-ux-polish` created on branch `sprint-27/curavias-ux-polish`.

- [ ] **Step 3: Install and record a green baseline**

Run (in `apps/hcc-app-fluent`): `npm install; npm run lint; npm run test; npm run build`
Expected: all green. Record the output as the pre-polish baseline.

### Task 0.2: Capture the OOA before-state

- [ ] **Step 1: Run the app locally**

Run (in `apps/hcc-app-fluent`): `npm run dev`
Expected: app served at `http://localhost:5173`; with SIT `VITE_*` env vars it uses SIT, otherwise the `demo.guest` fallback.

- [ ] **Step 2: Capture OOA before-screenshots + axe baseline**

Run: `npm run test:e2e; npm run test:a11y`
Expected: green. Save Playwright screenshots of `/start` and `/main/occupancy` (light+dark, desktop+narrow) into the PR evidence set as the "before" baseline.

### Task 0.3: Write the loop runbook

- [ ] **Step 1: Create the runbook**

Create `docs/runbooks/curavias-ux-local-verify-loop.md` documenting: required `VITE_MSAL_*` / `VITE_AGENT_HOST_URL` env vars and the `demo.guest` fallback; the two Playwright modes (standalone CLI via `playwright.config.ts`, and VS Code shared-context via `.vscode/mcp.json` + `playwright-mcp`); and the `edit → hot-reload → re-snapshot → axe-scan → attach evidence` cycle. Include the standard version header (`Version: 1.0.0`, `Previous Version: n/a`).

- [ ] **Step 2: Validate the doc**

Run: `python scripts/lint/check_mojibake.py docs/runbooks/curavias-ux-local-verify-loop.md; npx --yes markdownlint-cli2 "docs/runbooks/curavias-ux-local-verify-loop.md"`
Expected: no findings.

- [ ] **Step 3: Commit**

```bash
git add docs/runbooks/curavias-ux-local-verify-loop.md
git commit -m "docs(runbook): SIT-connected UX local visual-verify loop (Sprint 27 M0)"
```

---

## M1 — Design-system module

### Task 1.1: Semantic tokens

- [ ] **Step 1: Write the failing test**

Create `tests/unit/design-system-tokens.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { ds } from '../../src/theme/design-system';

describe('design-system tokens', () => {
  it('exposes an 8pt-derived space scale', () => {
    expect(ds.space.xs).toBe('4px');
    expect(ds.space.s).toBe('8px');
    expect(ds.space.m).toBe('12px');
    expect(ds.space.l).toBe('16px');
    expect(ds.space.xl).toBe('24px');
    expect(ds.space.xxl).toBe('32px');
  });

  it('exposes radii, elevation, motion, focus', () => {
    expect(ds.radii.card).toBeDefined();
    expect(ds.elevation.card).toBeDefined();
    expect(ds.motion.durationNormal).toBeDefined();
    expect(ds.focus.ringWidth).toBe('2px');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- design-system-tokens`
Expected: FAIL — cannot resolve `../../src/theme/design-system`.

- [ ] **Step 3: Write minimal implementation**

Create `src/theme/design-system/tokens.ts`:

```ts
import { tokens as fluent } from '@fluentui/react-components';

/** Semantic tokens: name the decisions Fluent leaves open so screens stop hand-rolling them. */
export const space = {
  xs: '4px',
  s: '8px',
  m: '12px',
  l: '16px',
  xl: '24px',
  xxl: '32px',
} as const;

export const radii = {
  control: fluent.borderRadiusMedium,
  card: fluent.borderRadiusLarge,
  pill: fluent.borderRadiusCircular,
} as const;

export const elevation = {
  flat: fluent.shadow2,
  card: fluent.shadow4,
  raised: fluent.shadow8,
  overlay: fluent.shadow16,
  dialog: fluent.shadow28,
} as const;

export const motion = {
  durationFast: fluent.durationFaster,
  durationNormal: fluent.durationNormal,
  durationSlow: fluent.durationSlow,
  easyEase: fluent.curveEasyEase,
  decelerate: fluent.curveDecelerateMid,
} as const;

export const density = { rowHeight: '44px', compactRowHeight: '36px' } as const;
export const zIndex = { base: 0, sticky: 100, drawer: 400, overlay: 800 } as const;
export const focus = { ringWidth: '2px', ringOffset: '2px' } as const;

export const dsTokens = { space, radii, elevation, motion, density, zIndex, focus } as const;
```

- [ ] **Step 4: Create the barrel**

Create `src/theme/design-system/index.ts`:

```ts
export * from './tokens';
export * from './recipes';
import { dsTokens } from './tokens';
export const ds = dsTokens;
```

- [ ] **Step 5: Run test to verify it passes**

Run: `npm run test -- design-system-tokens`
Expected: PASS (recipes barrel line will fail to resolve until Task 1.2 — create an empty `recipes.ts` stub first if needed: `export {};`).

- [ ] **Step 6: Commit**

```bash
git add src/theme/design-system/tokens.ts src/theme/design-system/index.ts tests/unit/design-system-tokens.test.ts
git commit -m "feat(app): add Curavias semantic design tokens (Sprint 27 M1)"
```

### Task 1.2: Component recipes

- [ ] **Step 1: Write the failing test**

Create `tests/unit/design-system-recipes.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useSurfaceStyles, useStateStyles } from '../../src/theme/design-system/recipes';

describe('design-system recipes', () => {
  it('surface recipe returns card + grid + header classes', () => {
    const { result } = renderHook(() => useSurfaceStyles());
    expect(result.current.surfaceCard).toBeTypeOf('string');
    expect(result.current.boardGrid).toBeTypeOf('string');
    expect(result.current.sectionHeader).toBeTypeOf('string');
    expect(result.current.statTile).toBeTypeOf('string');
    expect(result.current.provenanceBadge).toBeTypeOf('string');
  });

  it('state recipe returns empty/loading/error classes', () => {
    const { result } = renderHook(() => useStateStyles());
    expect(result.current.emptyState).toBeTypeOf('string');
    expect(result.current.loadingState).toBeTypeOf('string');
    expect(result.current.errorState).toBeTypeOf('string');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- design-system-recipes`
Expected: FAIL — no `useSurfaceStyles` / `useStateStyles` export.

- [ ] **Step 3: Write minimal implementation**

Create `src/theme/design-system/recipes.ts`:

```ts
import { makeStyles, tokens } from '@fluentui/react-components';
import { space, radii, elevation, motion, focus } from './tokens';

export const useSurfaceStyles = makeStyles({
  surfaceCard: {
    backgroundColor: tokens.colorNeutralBackground1,
    borderRadius: radii.card,
    boxShadow: elevation.card,
    padding: space.l,
    transitionDuration: motion.durationNormal,
    transitionTimingFunction: motion.easyEase,
    ':hover': { boxShadow: elevation.raised },
    ':focus-within': {
      outlineWidth: focus.ringWidth,
      outlineStyle: 'solid',
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: focus.ringOffset,
    },
  },
  boardGrid: { display: 'grid', gap: space.l, gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))' },
  sectionHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: space.m,
    marginBottom: space.m,
  },
  statTile: { display: 'flex', flexDirection: 'column', gap: space.xs, padding: space.m, borderRadius: radii.control },
  provenanceBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: space.xs,
    padding: `${space.xs} ${space.s}`,
    borderRadius: radii.pill,
  },
});

export const useStateStyles = makeStyles({
  emptyState: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: space.m, padding: space.xxl },
  loadingState: { display: 'flex', alignItems: 'center', gap: space.s, padding: space.xl },
  errorState: {
    display: 'flex',
    flexDirection: 'column',
    gap: space.s,
    padding: space.l,
    borderRadius: radii.control,
    color: tokens.colorPaletteRedForeground1,
  },
});
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test -- design-system-recipes`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/theme/design-system/recipes.ts tests/unit/design-system-recipes.test.ts
git commit -m "feat(app): add Curavias component-recipe styles (Sprint 27 M1)"
```

---

## M2 — App style-guide doc

### Task 2.1: Write the style-guide with the heuristic checklist

- [ ] **Step 1: Create the doc**

Create `docs/brandkit/curavias-app-style-guide.md`. Include the standard version header (`Version: 1.0.0`, `Previous Version: n/a`) and these sections:

1. **Token map** — a table: each `ds` token → the Fluent v9 primitive it wraps → the M365 app pattern it mirrors (Outlook list rhythm, Teams pane elevation, M365 Copilot chat spacing).
2. **Recipe catalogue** — `surfaceCard`, `boardGrid`, `sectionHeader`, `statTile`, `provenanceBadge`, `emptyState`, `loadingState`, `errorState` with a one-line "use when".
3. **The heuristic checklist** (the reusable per-screen review gate):
   8 pt spacing grid; Fluent type ramp; correct elevation; motion on transitions; hover / pressed / focus states; explicit empty / loading / error states; dark-mode parity; WCAG AA contrast + visible focus.
4. **Do / Don't** — e.g. *Do* import spacing from `ds.space`; *Don't* hard-code `px` or Astro-site styles from `apps/curavias-web`.

- [ ] **Step 2: Validate the doc**

Run: `python scripts/lint/check_mojibake.py docs/brandkit/curavias-app-style-guide.md; npx --yes markdownlint-cli2 "docs/brandkit/curavias-app-style-guide.md"`
Expected: no findings.

- [ ] **Step 3: Commit**

```bash
git add docs/brandkit/curavias-app-style-guide.md
git commit -m "docs(brandkit): Curavias app style-guide + heuristic checklist (Sprint 27 M2)"
```

---

## M3 — In-app `/brand` gallery

### Task 3.1: Gallery view

- [ ] **Step 1: Write the failing test**

Create `tests/unit/brand-gallery.test.tsx`:

```tsx
import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeModeProvider } from '../../src/theme/theme-context';
import { BrandGalleryView } from '../../src/workspaces/brand/BrandGalleryView';

describe('BrandGalleryView', () => {
  it('renders token and component-state sections', () => {
    render(<ThemeModeProvider><BrandGalleryView /></ThemeModeProvider>);
    expect(screen.getByTestId('brand-gallery')).toBeInTheDocument();
    expect(screen.getByText(/spacing/i)).toBeInTheDocument();
    expect(screen.getByText(/component states/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- brand-gallery`
Expected: FAIL — no `BrandGalleryView`.

- [ ] **Step 3: Write minimal implementation**

Create `src/workspaces/brand/BrandGalleryView.tsx` that renders, inside `data-testid="brand-gallery"`: a **Spacing** section (swatches for each `ds.space`), an **Elevation** section (cards using each `ds.elevation`), and a **Component states** section (each recipe in default / hover-hint / empty / loading / error). Use `useSurfaceStyles` + `useStateStyles`. Keep copy in English (dev-only surface); no i18n keys required.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test -- brand-gallery`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/workspaces/brand/BrandGalleryView.tsx tests/unit/brand-gallery.test.tsx
git commit -m "feat(app): add /brand design-system gallery view (Sprint 27 M3)"
```

### Task 3.2: Mount the route

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/router.test.tsx` (extend existing) a case asserting a `brand` path renders the gallery. Example:

```tsx
it('routes /brand to the gallery', async () => {
  const router = createMemoryRouter(routes, { initialEntries: ['/brand'] });
  render(<ThemeModeProvider><RouterProvider router={router} /></ThemeModeProvider>);
  expect(await screen.findByTestId('brand-gallery')).toBeInTheDocument();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- router`
Expected: FAIL — no `/brand` route.

- [ ] **Step 3: Add the route**

Modify `src/shell/router.tsx` — add `{ path: 'brand', element: <BrandGalleryView /> }` to the `AppShell` children (import `BrandGalleryView`). Keep it out of the primary navigation (route-only).

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test -- router`
Expected: PASS.

- [ ] **Step 5: Add axe coverage + commit**

Add a Playwright a11y case that navigates to `/brand` and asserts zero axe violations, then:

```bash
git add src/shell/router.tsx tests/unit/router.test.tsx tests/**/*brand*
git commit -m "feat(app): mount /brand route + axe coverage (Sprint 27 M3)"
```

- [ ] **Step 6: Verify the gallery in the shared-context loop**

Run: `npm run dev` then navigate the VS Code shared browser to `/brand`; screenshot light+dark; run `npm run test:a11y`.
Expected: gallery renders all tokens/states; axe green.

---

## M4 — Shared five-plane chrome polish

> Screen-polish milestones are iterative + visual. Each follows the same procedure; the exact
> style deltas are produced live in the shared-context loop, not pre-written here. The gate is
> the acceptance bar, verified by evidence + axe.

### Task 4.1: Add the guard test

- [ ] **Step 1: Write the guard test**

Create `tests/unit/ooa-design-system-usage.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const files = [
  'src/workspaces/start/StartView.tsx',
  'src/workspaces/main/boards/occupancy/OccupancyBoard.tsx',
];

describe('OOA surfaces consume the design system', () => {
  for (const f of files) {
    it(`${f} imports theme/design-system and has no raw px spacing literals`, () => {
      const src = readFileSync(resolve(__dirname, '../../', f), 'utf8');
      expect(src).toMatch(/theme\/design-system/);
      // no inline pixel spacing (padding/margin/gap: '12px')
      expect(src).not.toMatch(/(padding|margin|gap)\s*:\s*['"]\d+px['"]/);
    });
  }
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- ooa-design-system-usage`
Expected: FAIL — files do not yet import the design system.

- [ ] **Step 3: Note** — this test stays red until Tasks 5.x / 6.x import the design system. Commit it now so the guard exists:

```bash
git add tests/unit/ooa-design-system-usage.test.ts
git commit -m "test(app): guard OOA surfaces consume the design system (Sprint 27 M4)"
```

### Task 4.2: Polish the chrome

- [ ] **Step 1: Capture before** — screenshot Header/TopBar, Navigation, Agent, Footer planes (light+dark, desktop+narrow) via the shared browser.
- [ ] **Step 2: Refactor** `src/shell/AppShell.tsx`, `src/shell/planes/**`, `src/shell/TopBar/**` and the agent-plane containers to consume `ds.space` / `ds.elevation` / `ds.focus` and the recipes — remove hand-rolled spacing/shadows; ensure focus order and visible focus.
- [ ] **Step 3: Verify** in the loop — spacing on the 8 pt grid, elevation, hover/pressed/focus, dark-mode parity. Run `npm run test`, `npm run test:e2e`, `npm run test:a11y`.
- [ ] **Step 4: Acceptance gate** — heuristic checklist ✅, axe AA ✅, before/after screenshots attached.
- [ ] **Step 5: Commit**

```bash
git add src/shell tests
git commit -m "feat(app): polish five-plane chrome to design system (Sprint 27 M4)"
```

---

## M5 — OOA Start occupancy teaser

### Task 5.1: Polish `StartView`

- [ ] **Step 1: Capture before** — `/start` occupancy teaser (light+dark, desktop+narrow).
- [ ] **Step 2: Refactor** `src/workspaces/start/StartView.tsx` (and its teaser card) to use `useSurfaceStyles().surfaceCard` / `statTile` / `provenanceBadge` and `useStateStyles().loadingState` / `emptyState`; replace hand-rolled spacing with `ds.space`. Do **not** change data flow (`loadSiteCapacitySummary`) or the provenance badge semantics — style only.
- [ ] **Step 3: Verify** in the loop; run `npm run test -- start-view ooa-design-system-usage`, `npm run test:a11y`.
Expected: `start-view` + guard (StartView half) pass; axe green.
- [ ] **Step 4: Acceptance gate** — checklist ✅, axe AA ✅, before/after attached.
- [ ] **Step 5: Commit**

```bash
git add src/workspaces/start tests
git commit -m "feat(app): polish OOA Start occupancy teaser (Sprint 27 M5)"
```

---

## M6 — OOA Occupancy board

### Task 6.1: Polish `OccupancyBoard`

- [ ] **Step 1: Capture before** — `/main/occupancy` (light+dark, desktop+narrow).
- [ ] **Step 2: Refactor** `OccupancyBoard.tsx` + `BoardHeader.tsx` + `WardForecastTable.tsx` + `CapacityFlowDiagram.tsx`: replace the local `useStyles` `root` spacing with `ds.space` and wrap sections in `surfaceCard` / `boardGrid` / `sectionHeader`; add explicit `loadingState` (replacing the bare `Loading...` text) and `emptyState` / `errorState`; style the 72 h forecast + ward rows on the grid. Keep `occupancyBoard.load` / `routeInsight` / provenance unchanged.
- [ ] **Step 3: Verify** in the loop; run `npm run test -- occupancy ooa-design-system-usage`, `npm run test:e2e`, `npm run test:a11y`.
Expected: occupancy tests + guard pass; axe green.
- [ ] **Step 4: Acceptance gate** — checklist ✅, axe AA ✅, before/after attached.
- [ ] **Step 5: Commit**

```bash
git add src/workspaces/main/boards/occupancy tests
git commit -m "feat(app): polish OOA Occupancy board (Sprint 27 M6)"
```

---

## M7 — OOA agent-plane context

### Task 7.1: Polish the agent plane for the OOA context

- [ ] **Step 1: Capture before** — agent plane docked + floating, OOA context-insight chips, ceiling badge.
- [ ] **Step 2: Refactor** `src/copilot-drawer/**` and `src/copilot-rail/**` to consume `ds.space` / `ds.elevation` / recipes: chat/message rhythm aligned to M365 Copilot surfaces, context-insight chips, ceiling badge, docked↔floating transitions using `ds.motion`. Do not change agent round-trip logic (`routeInsight`, rail context) — style only.
- [ ] **Step 3: Verify** in the loop; run `npm run test -- rail reco-panel`, `npm run test:a11y`.
Expected: rail/reco tests pass; axe green.
- [ ] **Step 4: Acceptance gate** — checklist ✅, axe AA ✅, before/after attached.
- [ ] **Step 5: Commit**

```bash
git add src/copilot-drawer src/copilot-rail tests
git commit -m "feat(app): polish OOA agent-plane context (Sprint 27 M7)"
```

---

## M8 — Integration, ADR, PRD, backlog handoff

### Task 8.1: Full green + ADR

- [ ] **Step 1: Full suite**

Run (in `apps/hcc-app-fluent`): `npm run lint; npm run test; npm run test:e2e; npm run test:a11y; npm run build`
Expected: all green; the `ooa-design-system-usage` guard is now fully green.

- [ ] **Step 2: Write the ADR**

Create `docs/adr/00NN-curavias-app-design-system-overlay.md` (next free number): decision = Approach A (token overlay + in-app gallery, no Storybook, no separate package); status `Accepted`; link the design spec. Validate with `check_mojibake.py` + `markdownlint-cli2`.

- [ ] **Step 3: Commit**

```bash
git add docs/adr
git commit -m "docs(adr): record Curavias app design-system overlay decision (Sprint 27 M8)"
```

### Task 8.2: PRD requirements + traceability

- [ ] **Step 1: Add the `FR-UX-*` / `NFR-UX-*` family**

Modify `docs/PRD.md`: add section **M) App Experience Polish And Design System (Sprint 27)** with `FR-UX-001`..`FR-UX-006`, add `NFR-UX-001`..`NFR-UX-004` to the NFR section, add a Traceability Matrix row pointing at this plan, and bump the PRD version (MINOR) with `Previous Version` updated.

- [ ] **Step 2: Validate + commit**

Run: `python scripts/lint/check_mojibake.py docs/PRD.md; npx --yes markdownlint-cli2 "docs/PRD.md"`

```bash
git add docs/PRD.md
git commit -m "docs(prd): add FR-UX/NFR-UX app-polish requirements (Sprint 27 M8)"
```

### Task 8.3: Close out

- [ ] **Step 1: Attach the full before/after evidence set** to the epic PR (all OOA screens, light+dark, desktop+narrow).
- [ ] **Step 2: Move `Status` to `Delivered`** on the design spec and sprint doc only after every checklist item is green; bump their versions per copilot-instructions §9.
- [ ] **Step 3: Confirm the ordered backlog** (design spec §9) is current and hand it off in the epic issue for the next sprint.
- [ ] **Step 4: Final commit**

```bash
git add docs/superpowers/specs docs/sprints
git commit -m "docs: mark Sprint 27 UX polish delivered + backlog handoff"
```

---

## Self-Review

**Spec coverage:** M0 → design spec §5; M1 → §6.1; M2 → §6.2 + §8 checklist; M3 → §6.3; M4 → §7 chrome; M5 → §7 Start; M6 → §7 Occupancy board; M7 → §7 agent plane; M8 → §16 traceability + §4 ADR + §9 backlog. Acceptance bar (§8) enforced in every screen milestone's gate. All spec sections map to a task.

**Placeholder scan:** `00NN` ADR number and the tracker issue number are the only intentional placeholders (resolved at execution time — next free ADR number / filed issue number). No `TODO`/`TBD`/"handle edge cases" steps; code steps carry complete code; screen-polish steps carry exact files, commands, and the acceptance gate.

**Type consistency:** `ds` (barrel), `dsTokens`, `space/radii/elevation/motion/focus`, `useSurfaceStyles`/`useStateStyles`, `surfaceCard/boardGrid/sectionHeader/statTile/provenanceBadge/emptyState/loadingState/errorState`, and `BrandGalleryView` are used consistently across tasks and tests.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-07-24-sprint-27-curavias-ux-polish-plan.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
