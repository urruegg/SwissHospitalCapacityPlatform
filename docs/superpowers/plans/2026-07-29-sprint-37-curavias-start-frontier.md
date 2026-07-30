# Sprint 37 Curavias Start (Frontier Firm) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Curavias App **Start** surface from the Frontier-Firm content
BOM, with the patient-path as the RBAC-gated role launcher and the Product Owner Agent
rail docked - delivered by guided rapid prototyping against the local app.

**Architecture:** `StartView` is rewritten to compose focused Fluent v9 section
components under `workspaces/start/frontier/`. A typed `start-content.ts` holds the
static copy; hero + BVA sections bind to real app data (`bvaHeadlineKpis`, live
`siteCapacity`, `bva-evidence.ts`); the patient path reuses `LAUNCHER_TILES` + RBAC to
navigate into `/main/<role>`. The PO rail is wired on `/start` via `agent-context-map`.

**Tech Stack:** React 18, TypeScript 5.7, Fluent UI v9, React Router 6, i18next,
Vitest, Testing Library, Playwright, axe-core.

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-29 |
| **Author** | Urs Rueegg (with GitHub Copilot) |
| **Status** | Approved for delegation |
| **Previous Version** | n/a (initial implementation plan) |
| **Sprint** | Sprint 37 - Curavias Start content intake (slice 1 of 2) |
| **Issue** | [#546](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/546) |

**Design:**
[Sprint 37 design](../specs/2026-07-29-sprint-37-curavias-start-frontier-design.md)

**Tracker:**
[#546](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/546)

**Local app for rapid prototyping:** `http://localhost:5173/start`

---

## Delivery order and ownership

| Slice | Owner | Files owned | Dependency |
| ----- | ----- | ----------- | ---------- |
| WS-A | Shell subagent | `start-content.ts`, `StartView.tsx`, `agent-context-map.ts`, i18n | none |
| WS-B | Data subagent | `StartHero.tsx`, `BvaDecisionSection.tsx`, tests | WS-A |
| WS-C | Launcher subagent | `PatientPathLauncher.tsx`, tests | WS-A |
| WS-D | Narrative subagent | `WorkChartSection.tsx`, `CioChallengerSection.tsx`, `HospitalsSection.tsx`, `NinetyDaySection.tsx` | WS-A |
| WS-E | Verification subagent | `tests/e2e/start.spec.ts`, `tests/e2e/a11y.spec.ts` | WS-A..D |

WS-A lands first (content model + shell + PO-rail wiring). WS-B, WS-C, WS-D rebase on it
and run in parallel. WS-E closes out.

## File structure

Create under `apps/hcc-app-fluent/src/workspaces/start/frontier/`:

- `start-content.ts` - typed content model + i18n keys for the static sections.
- `start-content.test.ts` - content invariants + non-PHI check.
- `StartHero.tsx` - hero + squeeze card (binds metrics + live siteCapacity).
- `StartHero.test.tsx` - data-binding + provenance test.
- `WorkChartSection.tsx`, `CioChallengerSection.tsx`, `HospitalsSection.tsx`,
  `NinetyDaySection.tsx` - static narrative sections.
- `PatientPathLauncher.tsx` - patient path + RBAC role launcher.
- `PatientPathLauncher.test.tsx` - navigation + RBAC test.
- `BvaDecisionSection.tsx` - BVA tiles/tables (binds `bva-evidence.ts`).
- `BvaDecisionSection.test.tsx` - source-binding test.

Modify:

- `apps/hcc-app-fluent/src/workspaces/start/StartView.tsx` - compose the sections.
- `apps/hcc-app-fluent/src/shell/planes/agent-context-map.ts` - `/start` ->
  `product-owner-agent`.
- `apps/hcc-app-fluent/src/i18n/en.json` and `de.json` - Start copy.
- `apps/hcc-app-fluent/tests/e2e/start.spec.ts` - Start section order, launcher nav,
  PO rail, responsive.
- `apps/hcc-app-fluent/tests/e2e/a11y.spec.ts` - `/start` already scanned; keep the new
  content in scope.

## Task 1: Content model, shell, and PO-rail wiring (WS-A)

**Files:**

- Create: `apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.test.ts`
- Create: `apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.ts`
- Modify: `apps/hcc-app-fluent/src/shell/planes/agent-context-map.ts`

- [ ] **Step 1: Write the failing content + wiring tests**

```ts
import { describe, expect, it } from 'vitest';
import { START_SECTIONS } from './start-content';
import { agentForRoute } from '../../../shell/planes/agent-context-map';

describe('start content + PO rail wiring', () => {
  it('defines the seven Start sections in blueprint order', () => {
    expect(START_SECTIONS.map((s) => s.id)).toEqual([
      'hero', 'work-chart', 'cio-why-now', 'hospitals', 'patient-path', 'ninety-day', 'bva',
    ]);
    expect(JSON.stringify(START_SECTIONS)).not.toMatch(/patient name|birth|mrn|ssn/i);
  });

  it('docks the Product Owner Agent on /start', () => {
    expect(agentForRoute('/start')).toBe('product-owner-agent');
  });
});
```

- [ ] **Step 2: Run and verify failure**

```powershell
npx vitest run src/workspaces/start/frontier/start-content.test.ts
```

Expected: FAIL - module missing and `/start` currently maps to `orchestrator`.

- [ ] **Step 3: Implement the content model + wiring**

Create `START_SECTIONS` as a typed, ordered array of section descriptors
(`{ id, titleKey, kind: 'static' | 'data' | 'launcher' }`) matching the blueprint order.
Add the i18n keys under `start.frontier.*` in `en.json` + `de.json` (English fallback).

In `agent-context-map.ts`, add: if `pathname.startsWith('/start')` return
`'product-owner-agent'` (before the orchestrator fallthrough).

- [ ] **Step 4: Run tests + typecheck**

```powershell
npx vitest run src/workspaces/start/frontier/start-content.test.ts
npm run lint
```

Expected: PASS; TypeScript exits 0.

- [ ] **Step 5: Compose the StartView shell**

Rewrite `StartView.tsx` to render the section components in `START_SECTIONS` order
inside the page layout (placeholders acceptable until WS-B..D land, but the section
containers + `data-testid="start-<id>"` must exist and the old launcher grid + teaser
copy must be removed).

- [ ] **Step 6: Commit WS-A**

```powershell
git add apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.ts apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.test.ts apps/hcc-app-fluent/src/workspaces/start/StartView.tsx apps/hcc-app-fluent/src/shell/planes/agent-context-map.ts apps/hcc-app-fluent/src/i18n/en.json apps/hcc-app-fluent/src/i18n/de.json
git commit -m "feat(start): frontier content model, section shell, PO rail on /start"
```

## Task 2: Hero + squeeze card, data-bound (WS-B)

**Files:**

- Create: `apps/hcc-app-fluent/src/workspaces/start/frontier/StartHero.test.tsx`
- Create: `apps/hcc-app-fluent/src/workspaces/start/frontier/StartHero.tsx`

- [ ] **Step 1: Write the failing data-binding test**

```tsx
import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { describe, expect, it } from 'vitest';
import { StartHero } from './StartHero';
import { bvaHeadlineKpis } from '../../../data/bva/bva-evidence';

describe('StartHero', () => {
  it('renders BVA headline metrics from evidence with a provenance label', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <StartHero />
      </FluentProvider>,
    );
    const roi = String(bvaHeadlineKpis.roiPct ?? bvaHeadlineKpis.roi ?? '');
    if (roi) expect(screen.getByText(new RegExp(roi))).toBeInTheDocument();
    expect(screen.getByText(/ROM|estimate|provenance/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run and verify failure**

```powershell
npx vitest run src/workspaces/start/frontier/StartHero.test.tsx
```

Expected: FAIL - component missing. (Adjust the metric accessor in Step 1 to the real
`bvaHeadlineKpis` shape before implementing.)

- [ ] **Step 3: Implement StartHero**

Render the Frontier-Firm hook, value line, three metric tiles from `bvaHeadlineKpis`
(each with a `ROM estimate` provenance caption), the "Site capacity - next 72h" squeeze
card from `loadSiteCapacitySummary` (live/simulated with the app's provenance badge),
trust pills, and the synthetic/no-PHI disclaimer. CTAs link to `/backstage`. No
hard-coded numbers - all figures come from the bindings.

- [ ] **Step 4: Run + typecheck**

```powershell
npx vitest run src/workspaces/start/frontier/StartHero.test.tsx
npm run lint
```

Expected: PASS; TypeScript exits 0.

- [ ] **Step 5: Commit**

```powershell
git add apps/hcc-app-fluent/src/workspaces/start/frontier/StartHero.tsx apps/hcc-app-fluent/src/workspaces/start/frontier/StartHero.test.tsx
git commit -m "feat(start): data-bound hero + site-capacity squeeze card"
```

## Task 3: BVA decision section, data-bound (WS-B)

**Files:**

- Create: `apps/hcc-app-fluent/src/workspaces/start/frontier/BvaDecisionSection.test.tsx`
- Create: `apps/hcc-app-fluent/src/workspaces/start/frontier/BvaDecisionSection.tsx`

- [ ] **Step 1: Write the failing source-binding test**

```tsx
import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { describe, expect, it } from 'vitest';
import { BvaDecisionSection } from './BvaDecisionSection';
import { bvaHeadlineKpis } from '../../../data/bva/bva-evidence';

describe('BvaDecisionSection', () => {
  it('renders KPI tiles sourced from bva-evidence (not literals)', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <BvaDecisionSection />
      </FluentProvider>,
    );
    const roi = String(bvaHeadlineKpis.roiPct ?? bvaHeadlineKpis.roi ?? '');
    if (roi) expect(screen.getAllByText(new RegExp(roi)).length).toBeGreaterThan(0);
    expect(screen.getByText(/ROM/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run and verify failure**

```powershell
npx vitest run src/workspaces/start/frontier/BvaDecisionSection.test.tsx
```

Expected: FAIL - component missing.

- [ ] **Step 3: Implement BvaDecisionSection**

Render the KPI tiles, TCO table, value-levers table, sensitivity pills, proof list, and
the decision card - all values from `bva-evidence.ts`, each with a `ROM estimate` label.
A CTA opens the PO rail. No inline literals.

- [ ] **Step 4: Run + typecheck**

```powershell
npx vitest run src/workspaces/start/frontier/BvaDecisionSection.test.tsx
npm run lint
```

Expected: PASS; TypeScript exits 0.

- [ ] **Step 5: Commit**

```powershell
git add apps/hcc-app-fluent/src/workspaces/start/frontier/BvaDecisionSection.tsx apps/hcc-app-fluent/src/workspaces/start/frontier/BvaDecisionSection.test.tsx
git commit -m "feat(start): BVA decision section bound to bva-evidence"
```

## Task 4: Patient-path role launcher (WS-C)

**Files:**

- Create: `apps/hcc-app-fluent/src/workspaces/start/frontier/PatientPathLauncher.test.tsx`
- Create: `apps/hcc-app-fluent/src/workspaces/start/frontier/PatientPathLauncher.tsx`

- [ ] **Step 1: Write the failing navigation + RBAC test**

```tsx
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { describe, expect, it } from 'vitest';
import { PatientPathLauncher } from './PatientPathLauncher';

describe('PatientPathLauncher', () => {
  it('renders journey stops as links into /main/<role>', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <MemoryRouter>
          <PatientPathLauncher />
        </MemoryRouter>
      </FluentProvider>,
    );
    expect(screen.getByRole('link', { name: /occupancy|emergency|admission/i }))
      .toHaveAttribute('href', '/main/occupancy');
    expect(screen.getByRole('link', { name: /discharge/i }))
      .toHaveAttribute('href', '/main/discharge');
  });
});
```

- [ ] **Step 2: Run and verify failure**

```powershell
npx vitest run src/workspaces/start/frontier/PatientPathLauncher.test.tsx
```

Expected: FAIL - component missing.

- [ ] **Step 3: Implement PatientPathLauncher**

Render the wave-band 6-stop patient path (OOA, BMCA, ORSA, SBA, DCA, Recovery) plus the
CSA + Data-Quality spanning cards and the HITL footer. Each operational stop is a
`react-router` `Link` to its `LAUNCHER_TILES` route, filtered by the existing RBAC
`useRoleLens` `visibleTiles` (Crisis hidden without capability). Use Fluent-styled
buttons/links with keyboard + focus + `aria`. Carry the golden-thread evidence chips.

- [ ] **Step 4: Run + typecheck**

```powershell
npx vitest run src/workspaces/start/frontier/PatientPathLauncher.test.tsx
npm run lint
```

Expected: PASS; TypeScript exits 0.

- [ ] **Step 5: Commit**

```powershell
git add apps/hcc-app-fluent/src/workspaces/start/frontier/PatientPathLauncher.tsx apps/hcc-app-fluent/src/workspaces/start/frontier/PatientPathLauncher.test.tsx
git commit -m "feat(start): patient-path role launcher with RBAC navigation"
```

## Task 5: Static narrative sections (WS-D)

**Files:**

- Create: `WorkChartSection.tsx`, `CioChallengerSection.tsx`, `HospitalsSection.tsx`,
  `NinetyDaySection.tsx` under `apps/hcc-app-fluent/src/workspaces/start/frontier/`

- [ ] **Step 1: Implement the four static sections**

Each reads its copy from `start-content.ts` / i18n and renders with the Curavias
design-system recipes:

- `WorkChartSection` - Humans / Agents / On-demand cards + principle -> Curavias map.
- `CioChallengerSection` - the 7 operational-decisions table (Today vs preview).
- `HospitalsSection` - CuraNova / Curalp / Vialta cards + 7-agent roster.
- `NinetyDaySection` - Frame&Ground / Build&Prove / Operate&Scale phases.

Each section root carries `data-testid="start-<id>"`.

- [ ] **Step 2: Wire sections into StartView + typecheck**

Import and render them in blueprint order in `StartView.tsx`.

```powershell
npm run lint
npx vitest run src/workspaces/start/frontier
```

Expected: TypeScript exits 0; component tests PASS.

- [ ] **Step 3: Commit**

```powershell
git add apps/hcc-app-fluent/src/workspaces/start/frontier apps/hcc-app-fluent/src/workspaces/start/StartView.tsx
git commit -m "feat(start): frontier narrative sections (work-chart, cio, hospitals, 90-day)"
```

## Task 6: Playwright, responsive, and accessibility (WS-E)

**Files:**

- Create: `apps/hcc-app-fluent/tests/e2e/start.spec.ts`
- Modify: `apps/hcc-app-fluent/tests/e2e/a11y.spec.ts`

- [ ] **Step 1: Write the Start E2E test**

```ts
import { expect, test } from '@playwright/test';

test('Start renders the frontier blueprint and launches role boards', async ({ page }) => {
  await page.goto('/start');
  for (const id of ['hero', 'work-chart', 'cio-why-now', 'hospitals', 'patient-path', 'ninety-day', 'bva']) {
    await expect(page.getByTestId(`start-${id}`)).toBeVisible();
  }
  await expect(page.getByTestId('start-launcher')).toHaveCount(0); // old grid removed

  await page.getByRole('link', { name: /discharge/i }).click();
  await expect(page).toHaveURL(/\/main\/discharge/);

  await page.goto('/start');
  await expect(page.getByRole('complementary', { name: /agent/i })).toBeVisible();
});

test('Start has no horizontal scroll at narrow width', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/start');
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth === document.documentElement.clientWidth,
  );
  expect(overflow).toBe(true);
  await page.screenshot({ path: 'test-results/start-narrow.png', fullPage: true });
});
```

- [ ] **Step 2: Run and verify (iterate against the local app)**

```powershell
npx playwright test tests/e2e/start.spec.ts
```

Expected: PASS. Use `http://localhost:5173/start` for interactive refinement during
implementation.

- [ ] **Step 3: Confirm the axe scan covers /start**

`/start` is already in the `a11y.spec.ts` `SURFACES` list; ensure no exclusion hides the
new sections. Run:

```powershell
npx playwright test tests/e2e/a11y.spec.ts
```

Expected: no serious/critical WCAG 2.1 AA violations.

- [ ] **Step 4: Run full app gates**

```powershell
npm test
npm run lint
npm run build
npm run test:e2e
```

Expected: all exit 0. Record results + screenshot paths in the PR.

- [ ] **Step 5: Commit**

```powershell
git add apps/hcc-app-fluent/tests/e2e/start.spec.ts apps/hcc-app-fluent/tests/e2e/a11y.spec.ts
git commit -m "test(start): verify frontier Start UX, launcher nav, and accessibility"
```

## Task 7: Documentation and PR close-out

- [ ] **Step 1: Run document gates**

```powershell
python scripts/lint/check_mojibake.py docs/superpowers/specs/2026-07-29-sprint-37-curavias-start-frontier-design.md docs/superpowers/plans/2026-07-29-sprint-37-curavias-start-frontier.md
npx --yes markdownlint-cli2 "docs/superpowers/specs/2026-07-29-sprint-37-curavias-start-frontier-design.md" "docs/superpowers/plans/2026-07-29-sprint-37-curavias-start-frontier.md"
```

Expected: no mojibake and 0 Markdown issues.

- [ ] **Step 2: Confirm scope**

```powershell
git diff --name-only origin/main...HEAD
```

Expected: changed files limited to `apps/hcc-app-fluent/**` and Sprint 37 docs; Main and
Backstage surfaces untouched.

- [ ] **Step 3: Open the human-reviewed PR(s)**

Each workstream lands as its own squash PR linked to #546 with: requirements advanced
(`FR-UX-001`, `FR-UX-004`, `FR-UX-005`, `FR-UX-006`, `FR-POA-002`, `FR-CX-006`,
`FR-BVA-005`, `NFR-UX-001`..`NFR-UX-004`); experience-lane impact; no API/infra/MCP/PHI/
deploy/delete impact; unit/lint/build/Playwright/screenshot/axe evidence; residual risks.
Never self-merge; a human reviews the visual evidence + PO advisory/citation behavior.

## Final acceptance checklist

- [ ] `START_SECTIONS` defines the seven sections in blueprint order; no PHI.
- [ ] `/start` renders the seven sections; the old launcher grid + teaser copy are gone.
- [ ] Patient-path stops navigate to `/main/<role>`; Crisis is RBAC-gated.
- [ ] Hero metrics, squeeze, and BVA bind to real data with ROM + provenance (no literals).
- [ ] PO Agent rail is docked and labelled on `/start`.
- [ ] Desktop + narrow layouts have no overlap or horizontal scroll.
- [ ] Unit, lint, build, Playwright, screenshot, and axe gates pass.
- [ ] Synthetic/no-PHI + advisory-only remain visible; Main + Backstage untouched.
