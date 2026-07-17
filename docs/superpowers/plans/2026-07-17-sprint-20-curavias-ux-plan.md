# Sprint 20 — Curavias App UX Redesign Implementation Plan

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-17 |
| **Author** | Urs Rueegg |
| **Status** | Draft for review |
| **Previous Version** | n/a |
| **Design spec** | [2026-07-17-sprint-20-curavias-ux-design.md](../specs/2026-07-17-sprint-20-curavias-ux-design.md) |
| **Sprint doc** | [sprint-20-curavias-ux-redesign.md](../../sprints/sprint-20-curavias-ux-redesign.md) |
| **Lane** | Experience (`apps/hcc-app-fluent`) |

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the `hcc-app-fluent` React app as a Teams-style five-plane shell (Header / Navigation / Main / Agent / Footer) themed with the Curavias brandkit, with a role dropdown that acts as an RBAC access lens, four-language i18n (EN/DE/FR/IT), a dockable context-aware agent plane, and Start/Main/CSA/Backstage/Settings surfaces.

**Architecture:** A single `react-router-dom` v6 layout route renders `<AppShell>`, which lays out four persistent planes (HeaderPlane top, NavigationPlane left, AgentPlane right, FooterPlane bottom) around a central `<Outlet/>` (AppMainPlane). Route segments (`/start`, `/main/:board?`, `/csa`, `/backstage/:widget?`, `/settings`) render into the outlet. The active app-role (from `HCC.*` Entra claims) is a global access lens that narrows hospital scope, gates navigation and boards, and sets the agent action ceiling.

**Tech Stack:** React 18, TypeScript, Fluent UI React v9 (`@fluentui/react-components` + `@fluentui/react-icons`), `react-router-dom` v6, i18next, Vitest + Testing Library (unit/integration), Playwright + axe (e2e/a11y), Vite.

---

## File structure

New and modified files, grouped by responsibility. Paths are relative to `apps/hcc-app-fluent/`.

* **Theme (M1)** — `src/theme/curavias-theme.ts` (new, replaces `helvion-theme.ts`), `src/theme/curavias-tokens.json` (new, copied from brandkit), `src/theme/tokens.ts` (new, typed semantic token helpers).
* **RBAC lens (M3)** — `src/auth/rbac-model.ts` (new, role-map + capability derivation), `src/context/role-context.tsx` (modified, expose active-role lens + narrow-only switch).
* **Shell (M2, M3, M4, M7, M8)** — `src/shell/AppShell.tsx` (new layout route), `src/shell/planes/HeaderPlane.tsx`, `src/shell/planes/NavigationPlane.tsx`, `src/shell/planes/AgentPlane.tsx`, `src/shell/planes/FooterPlane.tsx` (all new), `src/shell/router.tsx` (new route table). `src/shell/TopBar.tsx`, `src/shell/AppRail.tsx`, `src/shell/WorkspaceRouter.tsx` are superseded and removed in M4.
* **Header controls (M3, M6)** — `src/shell/TopBar/RoleSwitcher.tsx` (modified â†’ real dropdown), `src/shell/TopBar/HospitalSelector.tsx` (modified â†’ scope-aware), `src/shell/TopBar/LanguageSelector.tsx` (new), `src/shell/TopBar/ThemeToggle.tsx` (new), `src/shell/TopBar/UserMenu.tsx` (new).
* **Content surfaces (M5)** — `src/workspaces/start/StartView.tsx` (new), `src/workspaces/settings/SettingsView.tsx` (new), existing `src/workspaces/main/*`, `src/workspaces/backstage/*`, and `src/workspaces/main/wizards/csa/*` rewired to routes.
* **i18n (M6)** — `src/i18n/fr.json`, `src/i18n/it.json` (new), `src/i18n/index.ts` (modified â†’ 4 languages), `src/i18n/en.json` + `src/i18n/de.json` (extended keys).
* **Footer (M8)** — `src/shell/planes/FooterPlane.tsx`, `src/config/app-version.ts` (new, reads `__APP_VERSION__` from Vite define).
* **Tests** — `tests/unit/*.test.tsx`, `tests/integration/*.spec.ts`, `tests/e2e/*.spec.ts` as named per task.

---

## Conventions for every task

* **TDD:** write the failing test first, watch it fail, implement minimally, watch it pass, commit.
* **Bullets** in any Markdown you touch use `*` (repo MD004 rule). Code fences carry a language.
* **Commits:** Conventional Commits, and every commit body ends with the trailer `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.
* **Commands** run from `apps/hcc-app-fluent/` unless stated. Unit tests: `npm run test -- <path>`. Type-check: `npm run lint`. e2e/a11y: `npm run test:e2e` / `npm run test:a11y`.
* **Fluent UI only** for controls/icons; no raw HTML controls where a Fluent equivalent exists.

---

## Milestone M0 — Brandkit intake and baseline

### Task 0.1: Commit the brandkit into version control

**Files:**

* Modify (stage): `docs/brandkit/**` (currently untracked)

* [ ] **Step 1: Confirm the brandkit assets the app needs exist**

Run (from repo root): `Get-ChildItem -Recurse docs\brandkit\color, docs\brandkit\logo`
Expected: `curavias-theme.ts`, `curavias-tokens.json` under `color/`, and the `curavias-icon` SVG/PNG under `logo/`.

* [ ] **Step 2: Stage and commit the brandkit**

```bash
git add docs/brandkit
git commit -m "chore(brandkit): commit Curavias brandkit assets for Sprint 20 UX"
```

* [ ] **Step 3: Verify the working tree no longer lists brandkit as untracked**

Run (repo root): `git status --short docs/brandkit`
Expected: no output.

### Task 0.2: Green baseline before changes

**Files:** none (verification only).

* [ ] **Step 1: Install deps and run the current suite**

Run: `npm install; npm run lint; npm run test`
Expected: install succeeds; `tsc --noEmit` clean; existing Vitest suite passes. Record the passing count as the regression baseline.

---

## Milestone M1 — Curavias theme

### Task 1.1: Copy brandkit tokens into the app

**Files:**

* Create: `src/theme/curavias-tokens.json`
* Test: `tests/unit/theme-tokens.test.ts`

* [ ] **Step 1: Write the failing test**

```typescript
import tokens from '../../src/theme/curavias-tokens.json';

describe('curavias tokens', () => {
  it('exposes the brand and secondary ramps and semantic roles', () => {
    expect(tokens.brand['80']).toBe('#17B890');
    expect(tokens.brandSecondary['80']).toBe('#365B7D');
    expect(tokens.danger['80']).toBe('#E30613');
    expect(tokens.text.onLight).toBe('#0E0F11');
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/theme-tokens.test.ts`
Expected: FAIL — cannot find module `curavias-tokens.json`.

* [ ] **Step 3: Create the tokens file (copied from `docs/brandkit/color/curavias-tokens.json`, adding the semantic roles the app consumes)**

```json
{
  "brand": { "10": "#04120E", "20": "#082019", "40": "#0C4335", "60": "#12765F", "80": "#17B890", "100": "#8FE3CE" },
  "brandSecondary": { "40": "#1E3247", "60": "#28455F", "80": "#365B7D", "100": "#9CB6CE" },
  "danger": { "80": "#E30613" },
  "warning": { "80": "#E8A200" },
  "info": { "80": "#1FA9D6" },
  "text": { "onLight": "#0E0F11", "onDark": "#F5F7F8", "linkOnLight": "#12765F" }
}
```

* [ ] **Step 4: Run it and watch it pass**

Run: `npm run test -- tests/unit/theme-tokens.test.ts`
Expected: PASS.

* [ ] **Step 5: Commit**

```bash
git add src/theme/curavias-tokens.json tests/unit/theme-tokens.test.ts
git commit -m "feat(theme): add Curavias brandkit tokens to hcc-app-fluent"
```

### Task 1.2: Build the Curavias light + dark Fluent themes

**Files:**

* Create: `src/theme/curavias-theme.ts`
* Test: `tests/unit/curavias-theme.test.ts`

* [ ] **Step 1: Write the failing test**

```typescript
import { curaviasLightTheme, curaviasDarkTheme } from '../../src/theme/curavias-theme';

describe('curavias theme', () => {
  it('sets brand primary and keeps dark text on the green fill', () => {
    expect(curaviasLightTheme.colorBrandBackground).toBe('#17B890');
    expect(curaviasLightTheme.colorNeutralForegroundOnBrand).toBe('#0E0F11');
  });
  it('provides a dark theme variant', () => {
    expect(curaviasDarkTheme.colorBrandBackground).toBe('#17B890');
    expect(curaviasDarkTheme.colorNeutralBackground1).not.toBe(curaviasLightTheme.colorNeutralBackground1);
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/curavias-theme.test.ts`
Expected: FAIL — module not found.

* [ ] **Step 3: Implement the themes via Fluent `createLightTheme`/`createDarkTheme` and a brand ramp**

```typescript
import {
  createLightTheme, createDarkTheme, type BrandVariants, type Theme,
} from '@fluentui/react-components';
import tokens from './curavias-tokens.json';

const curaviasBrand: BrandVariants = {
  10: tokens.brand['10'], 20: tokens.brand['10'], 30: tokens.brand['20'],
  40: tokens.brand['20'], 50: tokens.brand['40'], 60: tokens.brand['40'],
  70: tokens.brand['60'], 80: tokens.brand['80'], 90: tokens.brand['80'],
  100: tokens.brand['80'], 110: tokens.brand['80'], 120: tokens.brand['100'],
  130: tokens.brand['100'], 140: tokens.brand['100'], 150: tokens.brand['100'], 160: tokens.brand['100'],
};

export const curaviasLightTheme: Theme = {
  ...createLightTheme(curaviasBrand),
  colorBrandBackground: tokens.brand['80'],
  colorNeutralForegroundOnBrand: tokens.text.onLight,
};

export const curaviasDarkTheme: Theme = {
  ...createDarkTheme(curaviasBrand),
  colorBrandBackground: tokens.brand['80'],
  colorNeutralForegroundOnBrand: tokens.text.onLight,
};
```

* [ ] **Step 4: Run it and watch it pass**

Run: `npm run test -- tests/unit/curavias-theme.test.ts`
Expected: PASS.

* [ ] **Step 5: Commit**

```bash
git add src/theme/curavias-theme.ts tests/unit/curavias-theme.test.ts
git commit -m "feat(theme): add Curavias light and dark Fluent themes"
```

### Task 1.3: Wire the theme provider with light/dark persistence

**Files:**

* Modify: `src/main.tsx`
* Create: `src/theme/theme-context.tsx`
* Test: `tests/unit/theme-context.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { render, screen, act } from '@testing-library/react';
import { ThemeModeProvider, useThemeMode } from '../../src/theme/theme-context';

function Probe() {
  const { mode, toggle } = useThemeMode();
  return <button onClick={toggle}>{mode}</button>;
}

describe('theme mode', () => {
  it('defaults to light and toggles + persists to localStorage', () => {
    render(<ThemeModeProvider><Probe /></ThemeModeProvider>);
    const btn = screen.getByRole('button');
    expect(btn.textContent).toBe('light');
    act(() => btn.click());
    expect(btn.textContent).toBe('dark');
    expect(localStorage.getItem('curavias.theme')).toBe('dark');
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/theme-context.test.tsx`
Expected: FAIL — module not found.

* [ ] **Step 3: Implement the theme-mode context**

```typescript
import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import { FluentProvider } from '@fluentui/react-components';
import { curaviasLightTheme, curaviasDarkTheme } from './curavias-theme';

type Mode = 'light' | 'dark';
const KEY = 'curavias.theme';
const Ctx = createContext<{ mode: Mode; toggle: () => void }>({ mode: 'light', toggle: () => {} });

export function ThemeModeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<Mode>(() => (localStorage.getItem(KEY) as Mode) ?? 'light');
  const value = useMemo(() => ({
    mode,
    toggle: () => setMode((m) => { const next = m === 'light' ? 'dark' : 'light'; localStorage.setItem(KEY, next); return next; }),
  }), [mode]);
  const theme = mode === 'dark' ? curaviasDarkTheme : curaviasLightTheme;
  return <Ctx.Provider value={value}><FluentProvider theme={theme}>{children}</FluentProvider></Ctx.Provider>;
}

export const useThemeMode = () => useContext(Ctx);
```

* [ ] **Step 4: Replace the `helvion` provider usage in `main.tsx` with `ThemeModeProvider`**

In `src/main.tsx`, remove the import of `helvion-theme` and the bare `FluentProvider theme={helvionTheme}` wrapper; wrap the app tree in `<ThemeModeProvider>` instead.

* [ ] **Step 5: Run tests + type-check**

Run: `npm run test -- tests/unit/theme-context.test.tsx; npm run lint`
Expected: PASS; `tsc --noEmit` clean.

* [ ] **Step 6: Delete the obsolete helvion theme and commit**

```bash
git rm src/theme/helvion-theme.ts
git add src/theme/theme-context.tsx src/main.tsx tests/unit/theme-context.test.tsx
git commit -m "feat(theme): provide Curavias theme with persisted light/dark mode"
```

---

## Milestone M2 — Router shell (five planes)

### Task 2.1: Add react-router-dom

**Files:**

* Modify: `package.json`

* [ ] **Step 1: Install the router**

Run: `npm install react-router-dom@^6.26.0`
Expected: `dependencies.react-router-dom` populated; lockfile updated.

* [ ] **Step 2: Commit the dependency**

```bash
git add package.json package-lock.json
git commit -m "chore(deps): add react-router-dom v6 for the app shell"
```

### Task 2.2: AppShell layout with four plane placeholders + outlet

**Files:**

* Create: `src/shell/AppShell.tsx`
* Test: `tests/unit/app-shell.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AppShell } from '../../src/shell/AppShell';

function renderShell(path = '/start') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/start" element={<div>start-content</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe('AppShell', () => {
  it('renders the four persistent planes and the routed main content', () => {
    renderShell();
    expect(screen.getByRole('banner')).toBeInTheDocument();          // header
    expect(screen.getByRole('navigation')).toBeInTheDocument();      // nav
    expect(screen.getByRole('complementary')).toBeInTheDocument();   // agent
    expect(screen.getByRole('contentinfo')).toBeInTheDocument();     // footer
    expect(screen.getByText('start-content')).toBeInTheDocument();   // main outlet
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/app-shell.test.tsx`
Expected: FAIL — module not found.

* [ ] **Step 3: Implement the shell grid with placeholder planes**

```typescript
import { Outlet } from 'react-router-dom';
import { makeStyles, tokens } from '@fluentui/react-components';
import { HeaderPlane } from './planes/HeaderPlane';
import { NavigationPlane } from './planes/NavigationPlane';
import { AgentPlane } from './planes/AgentPlane';
import { FooterPlane } from './planes/FooterPlane';

const useStyles = makeStyles({
  root: {
    display: 'grid', height: '100vh',
    gridTemplateColumns: 'auto 1fr auto',
    gridTemplateRows: 'auto 1fr auto',
    gridTemplateAreas: `'header header header' 'nav main agent' 'footer footer footer'`,
    backgroundColor: tokens.colorNeutralBackground2,
  },
  header: { gridArea: 'header' },
  nav: { gridArea: 'nav' },
  main: { gridArea: 'main', overflow: 'auto', minWidth: 0 },
  agent: { gridArea: 'agent' },
  footer: { gridArea: 'footer' },
});

export function AppShell() {
  const s = useStyles();
  return (
    <div className={s.root}>
      <div className={s.header}><HeaderPlane /></div>
      <div className={s.nav}><NavigationPlane /></div>
      <main className={s.main}><Outlet /></main>
      <div className={s.agent}><AgentPlane /></div>
      <div className={s.footer}><FooterPlane /></div>
    </div>
  );
}
```

* [ ] **Step 4: Create minimal plane stubs so the test can resolve them**

Create `src/shell/planes/HeaderPlane.tsx`, `NavigationPlane.tsx`, `AgentPlane.tsx`, `FooterPlane.tsx`, each exporting a function that returns a landmark element with the matching ARIA role:

```typescript
// HeaderPlane.tsx
export function HeaderPlane() { return <header role="banner">Curavias</header>; }
// NavigationPlane.tsx
export function NavigationPlane() { return <nav aria-label="Primary" />; }
// AgentPlane.tsx
export function AgentPlane() { return <aside role="complementary" aria-label="Agent" />; }
// FooterPlane.tsx
export function FooterPlane() { return <footer role="contentinfo" />; }
```

* [ ] **Step 5: Run it and watch it pass**

Run: `npm run test -- tests/unit/app-shell.test.tsx`
Expected: PASS.

* [ ] **Step 6: Commit**

```bash
git add src/shell/AppShell.tsx src/shell/planes/*.tsx tests/unit/app-shell.test.tsx
git commit -m "feat(shell): add five-plane AppShell layout with routed main outlet"
```

### Task 2.3: Route table with default + fallback redirect to Start

**Files:**

* Create: `src/shell/router.tsx`
* Test: `tests/unit/router.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { render, screen } from '@testing-library/react';
import { RouterProvider, createMemoryRouter } from 'react-router-dom';
import { routes } from '../../src/shell/router';

function renderAt(path: string) {
  const router = createMemoryRouter(routes, { initialEntries: [path] });
  return render(<RouterProvider router={router} />);
}

describe('routes', () => {
  it('defaults "/" to the Start surface', () => {
    renderAt('/');
    expect(screen.getByTestId('start-view')).toBeInTheDocument();
  });
  it('redirects unknown paths to Start', () => {
    renderAt('/nope');
    expect(screen.getByTestId('start-view')).toBeInTheDocument();
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/router.test.tsx`
Expected: FAIL — module not found.

* [ ] **Step 3: Implement the route table (surfaces are temporary stubs, replaced in M5)**

```typescript
import { Navigate, type RouteObject } from 'react-router-dom';
import { AppShell } from './AppShell';

const Stub = ({ id }: { id: string }) => <div data-testid={id} />;

export const routes: RouteObject[] = [
  {
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="/start" replace /> },
      { path: 'start', element: <Stub id="start-view" /> },
      { path: 'main/:board?', element: <Stub id="main-view" /> },
      { path: 'csa', element: <Stub id="csa-view" /> },
      { path: 'backstage/:widget?', element: <Stub id="backstage-view" /> },
      { path: 'settings', element: <Stub id="settings-view" /> },
      { path: '*', element: <Navigate to="/start" replace /> },
    ],
  },
];
```

* [ ] **Step 4: Run it and watch it pass**

Run: `npm run test -- tests/unit/router.test.tsx`
Expected: PASS (both cases).

* [ ] **Step 5: Mount the router in `App.tsx`**

Replace the `WorkspaceRouter` usage in `src/App.tsx` with `<RouterProvider router={createBrowserRouter(routes)} />`.

* [ ] **Step 6: Commit**

```bash
git add src/shell/router.tsx src/App.tsx tests/unit/router.test.tsx
git commit -m "feat(shell): add route table with Start default and fallback redirect"
```

---

## Milestone M3 — Header plane + RBAC role lens

### Task 3.1: RBAC role-map and capability derivation

**Files:**

* Create: `src/auth/rbac-model.ts`
* Test: `tests/unit/rbac-model.test.ts`

* [ ] **Step 1: Write the failing test**

```typescript
import { ROLE_MAP, deriveCapabilities, narrowRoles } from '../../src/auth/rbac-model';

describe('rbac model', () => {
  it('maps a bed manager to own-site scope and write ceiling', () => {
    const caps = deriveCapabilities('HCC.BedManager', 'usz');
    expect(caps.hospitalScope).toBe('usz');
    expect(caps.agentCeiling).toBe('write');
    expect(caps.nav.settings).toBe(false);
  });
  it('maps a viewer to aggregated scope and read-only', () => {
    const caps = deriveCapabilities('HCC.Viewer', 'usz');
    expect(caps.hospitalScope).toBe('aggregated');
    expect(caps.agentCeiling).toBe('read');
  });
  it('narrowing only keeps roles the user actually holds', () => {
    expect(narrowRoles(['HCC.Viewer'], 'HCC.PlatformAdmin')).toBe('HCC.Viewer');
    expect(narrowRoles(['HCC.PlatformAdmin', 'HCC.Viewer'], 'HCC.Viewer')).toBe('HCC.Viewer');
  });
  it('keys of ROLE_MAP cover the five demo roles', () => {
    expect(Object.keys(ROLE_MAP).sort()).toEqual(
      ['HCC.BedManager', 'HCC.DemoOperator', 'HCC.PlatformAdmin', 'HCC.RegionalCrisisLead', 'HCC.Viewer'],
    );
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/rbac-model.test.ts`
Expected: FAIL — module not found.

* [ ] **Step 3: Implement the model**

```typescript
export type AgentCeiling = 'read' | 'write' | 'deploy';
export type HospitalScope = 'usz' | 'luks' | 'zollikerberg' | 'aggregated';
export type HccRole =
  | 'HCC.PlatformAdmin' | 'HCC.DemoOperator' | 'HCC.RegionalCrisisLead'
  | 'HCC.BedManager' | 'HCC.Viewer';

export interface RoleCapabilities {
  hospitalScope: HospitalScope | 'own-site';
  agentCeiling: AgentCeiling;
  nav: { start: boolean; main: boolean; csa: boolean; backstage: boolean; settings: boolean };
}

export const ROLE_MAP: Record<HccRole, RoleCapabilities> = {
  'HCC.PlatformAdmin':      { hospitalScope: 'aggregated', agentCeiling: 'deploy', nav: { start: true, main: true, csa: true, backstage: true, settings: true } },
  'HCC.DemoOperator':       { hospitalScope: 'aggregated', agentCeiling: 'write',  nav: { start: true, main: true, csa: true, backstage: true, settings: true } },
  'HCC.RegionalCrisisLead': { hospitalScope: 'aggregated', agentCeiling: 'deploy', nav: { start: true, main: true, csa: true, backstage: true, settings: false } },
  'HCC.BedManager':         { hospitalScope: 'own-site',   agentCeiling: 'write',  nav: { start: true, main: true, csa: false, backstage: false, settings: false } },
  'HCC.Viewer':             { hospitalScope: 'aggregated', agentCeiling: 'read',   nav: { start: true, main: true, csa: false, backstage: true, settings: false } },
};

const RANK: HccRole[] = ['HCC.Viewer', 'HCC.BedManager', 'HCC.DemoOperator', 'HCC.RegionalCrisisLead', 'HCC.PlatformAdmin'];

export function deriveCapabilities(role: HccRole, homeSite: HospitalScope): RoleCapabilities & { hospitalScope: HospitalScope } {
  const base = ROLE_MAP[role];
  const scope = base.hospitalScope === 'own-site' ? homeSite : base.hospitalScope;
  return { ...base, hospitalScope: scope };
}

export function narrowRoles(held: HccRole[], requested: HccRole): HccRole {
  if (held.includes(requested)) return requested;
  return [...held].sort((a, b) => RANK.indexOf(a) - RANK.indexOf(b)).pop() ?? held[0];
}
```

* [ ] **Step 4: Run it and watch it pass**

Run: `npm run test -- tests/unit/rbac-model.test.ts`
Expected: PASS.

* [ ] **Step 5: Commit**

```bash
git add src/auth/rbac-model.ts tests/unit/rbac-model.test.ts
git commit -m "feat(auth): add RBAC role-map, capability derivation, narrow-only switch"
```

### Task 3.2: Extend role-context to expose the active lens

**Files:**

* Modify: `src/context/role-context.tsx`
* Test: `tests/unit/role-context.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { render, screen, act } from '@testing-library/react';
import { RoleProvider, useRoleLens } from '../../src/context/role-context';

function Probe() {
  const { activeRole, capabilities, setActiveRole } = useRoleLens();
  return (
    <div>
      <span data-testid="role">{activeRole}</span>
      <span data-testid="ceiling">{capabilities.agentCeiling}</span>
      <button onClick={() => setActiveRole('HCC.PlatformAdmin')}>elevate</button>
    </div>
  );
}

describe('role lens', () => {
  it('defaults to the highest held role and refuses to elevate beyond held roles', () => {
    render(<RoleProvider testRoles={['HCC.Viewer']} testHomeSite="usz"><Probe /></RoleProvider>);
    expect(screen.getByTestId('role').textContent).toBe('HCC.Viewer');
    act(() => screen.getByText('elevate').click());
    expect(screen.getByTestId('role').textContent).toBe('HCC.Viewer'); // narrow-only
    expect(screen.getByTestId('ceiling').textContent).toBe('read');
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/role-context.test.tsx`
Expected: FAIL — `useRoleLens` not exported.

* [ ] **Step 3: Extend the provider (keep existing exports; add lens on top of the parsed claims)**

```typescript
import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import { deriveCapabilities, narrowRoles, type HccRole, type HospitalScope } from '../auth/rbac-model';

const RANK: HccRole[] = ['HCC.Viewer', 'HCC.BedManager', 'HCC.DemoOperator', 'HCC.RegionalCrisisLead', 'HCC.PlatformAdmin'];
const highestHeld = (held: HccRole[]) => [...held].sort((a, b) => RANK.indexOf(a) - RANK.indexOf(b)).pop() ?? 'HCC.Viewer';

interface LensValue {
  heldRoles: HccRole[];
  activeRole: HccRole;
  capabilities: ReturnType<typeof deriveCapabilities>;
  setActiveRole: (r: HccRole) => void;
}
const LensCtx = createContext<LensValue | null>(null);

export function RoleProvider({ children, testRoles, testHomeSite }: { children: ReactNode; testRoles?: HccRole[]; testHomeSite?: HospitalScope }) {
  // In production, testRoles/testHomeSite are undefined and the values come from parseClaims().
  const held = testRoles ?? /* parseClaims().roles */ (['HCC.Viewer'] as HccRole[]);
  const homeSite: HospitalScope = testHomeSite ?? 'aggregated';
  const [activeRole, setActive] = useState<HccRole>(() => highestHeld(held));
  const value = useMemo<LensValue>(() => ({
    heldRoles: held,
    activeRole,
    capabilities: deriveCapabilities(activeRole, homeSite),
    setActiveRole: (r) => setActive(narrowRoles(held, r)),
  }), [held, homeSite, activeRole]);
  return <LensCtx.Provider value={value}>{children}</LensCtx.Provider>;
}

export function useRoleLens(): LensValue {
  const v = useContext(LensCtx);
  if (!v) throw new Error('useRoleLens must be used within RoleProvider');
  return v;
}
```

Note: leave the existing claim-parser wiring in place; replace the `testRoles ?? ...` fallback with the real `parseClaims()` result when integrating (do not remove the test props).

* [ ] **Step 4: Run it and watch it pass**

Run: `npm run test -- tests/unit/role-context.test.tsx`
Expected: PASS.

* [ ] **Step 5: Commit**

```bash
git add src/context/role-context.tsx tests/unit/role-context.test.tsx
git commit -m "feat(auth): expose active-role access lens with narrow-only switching"
```

### Task 3.3: Header controls — Theme, Language, Hospital, Role, User (rightâ†’left) + brand (left)

**Files:**

* Create: `src/shell/TopBar/ThemeToggle.tsx`, `src/shell/TopBar/LanguageSelector.tsx`, `src/shell/TopBar/UserMenu.tsx`
* Modify: `src/shell/TopBar/RoleSwitcher.tsx`, `src/shell/TopBar/HospitalSelector.tsx`, `src/shell/planes/HeaderPlane.tsx`
* Test: `tests/unit/header-plane.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { render, screen, within } from '@testing-library/react';
import { HeaderPlane } from '../../src/shell/planes/HeaderPlane';
import { RoleProvider } from '../../src/context/role-context';
import { ThemeModeProvider } from '../../src/theme/theme-context';

function renderHeader(roles: string[]) {
  return render(
    <ThemeModeProvider>
      <RoleProvider testRoles={roles as never[]} testHomeSite="usz">
        <HeaderPlane />
      </RoleProvider>
    </ThemeModeProvider>,
  );
}

describe('HeaderPlane', () => {
  it('shows the brand on the left and all five right-aligned controls', () => {
    renderHeader(['HCC.PlatformAdmin', 'HCC.Viewer']);
    const header = screen.getByRole('banner');
    expect(within(header).getByText('Curavias')).toBeInTheDocument();
    expect(within(header).getByLabelText(/theme/i)).toBeInTheDocument();
    expect(within(header).getByLabelText(/language/i)).toBeInTheDocument();
    expect(within(header).getByLabelText(/hospital/i)).toBeInTheDocument();
    expect(within(header).getByLabelText(/role/i)).toBeInTheDocument();
    expect(within(header).getByLabelText(/user/i)).toBeInTheDocument();
  });
  it('the role dropdown lists only held roles', () => {
    renderHeader(['HCC.PlatformAdmin', 'HCC.Viewer']);
    const role = screen.getByLabelText(/role/i);
    expect(within(role).queryByText('HCC.BedManager')).not.toBeInTheDocument();
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/header-plane.test.tsx`
Expected: FAIL — controls missing.

* [ ] **Step 3: Implement `RoleSwitcher` as a real Fluent `Dropdown` bound to the lens**

```typescript
import { Dropdown, Option, Field } from '@fluentui/react-components';
import { useRoleLens } from '../../context/role-context';

export function RoleSwitcher() {
  const { heldRoles, activeRole, setActiveRole } = useRoleLens();
  return (
    <Field label="Role" aria-label="Role">
      <Dropdown
        aria-label="Role"
        value={activeRole}
        selectedOptions={[activeRole]}
        onOptionSelect={(_, d) => d.optionValue && setActiveRole(d.optionValue as never)}
      >
        {heldRoles.map((r) => <Option key={r} value={r}>{r}</Option>)}
      </Dropdown>
    </Field>
  );
}
```

* [ ] **Step 4: Implement `ThemeToggle`, `LanguageSelector`, `UserMenu`, and a scope-aware `HospitalSelector`**

```typescript
// ThemeToggle.tsx
import { Switch } from '@fluentui/react-components';
import { useThemeMode } from '../../theme/theme-context';
export function ThemeToggle() {
  const { mode, toggle } = useThemeMode();
  return <Switch aria-label="Theme" checked={mode === 'dark'} onChange={toggle} label={mode === 'dark' ? 'Dark' : 'Light'} />;
}
```

```typescript
// LanguageSelector.tsx
import { Dropdown, Option } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
const LANGS = [['de', 'Deutsch'], ['en', 'English'], ['fr', 'Français'], ['it', 'Italiano']] as const;
export function LanguageSelector() {
  const { i18n } = useTranslation();
  return (
    <Dropdown aria-label="Language" value={i18n.language} selectedOptions={[i18n.language]}
      onOptionSelect={(_, d) => d.optionValue && i18n.changeLanguage(d.optionValue)}>
      {LANGS.map(([c, n]) => <Option key={c} value={c}>{n}</Option>)}
    </Dropdown>
  );
}
```

```typescript
// UserMenu.tsx
import { Menu, MenuTrigger, MenuPopover, MenuList, MenuItem, Button } from '@fluentui/react-components';
import { PersonRegular } from '@fluentui/react-icons';
export function UserMenu({ name = 'Demo User' }: { name?: string }) {
  return (
    <Menu>
      <MenuTrigger disableButtonEnhancement>
        <Button aria-label="User menu" icon={<PersonRegular />} appearance="subtle">{name}</Button>
      </MenuTrigger>
      <MenuPopover><MenuList><MenuItem>Sign out</MenuItem></MenuList></MenuPopover>
    </Menu>
  );
}
```

`HospitalSelector` reads `capabilities.hospitalScope` from `useRoleLens()`; when the scope is a single site it renders a disabled single-value dropdown; when `aggregated` it lists the sites the role may view.

* [ ] **Step 5: Compose the HeaderPlane (brand left; Theme, Language, Hospital, Role, User rightâ†’left)**

```typescript
import { makeStyles, tokens, Image, Text } from '@fluentui/react-components';
import { ThemeToggle } from '../TopBar/ThemeToggle';
import { LanguageSelector } from '../TopBar/LanguageSelector';
import { HospitalSelector } from '../TopBar/HospitalSelector';
import { RoleSwitcher } from '../TopBar/RoleSwitcher';
import { UserMenu } from '../TopBar/UserMenu';
import curaviasIcon from '../../../docs-brandkit/curavias-icon.svg';

const useStyles = makeStyles({
  bar: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalM, padding: `0 ${tokens.spacingHorizontalL}`, height: '48px', backgroundColor: tokens.colorBrandBackground2 },
  brand: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalS },
  spacer: { flexGrow: 1 },
  controls: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalM },
});

export function HeaderPlane() {
  const s = useStyles();
  return (
    <header role="banner" className={s.bar}>
      <div className={s.brand}><Image src={curaviasIcon} alt="Curavias" height={24} /><Text weight="semibold">Curavias</Text></div>
      <div className={s.spacer} />
      <div className={s.controls}><ThemeToggle /><LanguageSelector /><HospitalSelector /><RoleSwitcher /><UserMenu /></div>
    </header>
  );
}
```

Note: import the icon from the app-consumable brandkit path established in M0; adjust the relative import to the committed location (a Vite `resolve.alias` such as `@brandkit` is acceptable and preferred over a deep relative path).

* [ ] **Step 6: Run tests + type-check**

Run: `npm run test -- tests/unit/header-plane.test.tsx; npm run lint`
Expected: PASS; type-check clean.

* [ ] **Step 7: Commit**

```bash
git add src/shell/TopBar/*.tsx src/shell/planes/HeaderPlane.tsx tests/unit/header-plane.test.tsx
git commit -m "feat(shell): header plane with theme/lang/hospital/role/user controls and RBAC role dropdown"
```

---

## Milestone M4 — Navigation plane with role gating

### Task 4.1: NavigationPlane with five destinations, disabled-not-hidden gating

**Files:**

* Modify: `src/shell/planes/NavigationPlane.tsx`
* Test: `tests/unit/navigation-plane.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { NavigationPlane } from '../../src/shell/planes/NavigationPlane';
import { RoleProvider } from '../../src/context/role-context';

function renderNav(roles: string[]) {
  return render(
    <MemoryRouter>
      <RoleProvider testRoles={roles as never[]} testHomeSite="usz"><NavigationPlane /></RoleProvider>
    </MemoryRouter>,
  );
}

describe('NavigationPlane', () => {
  it('renders all five destinations for an admin', () => {
    renderNav(['HCC.PlatformAdmin']);
    ['Start', 'Main', 'CSA', 'Backstage', 'Settings'].forEach((n) => expect(screen.getByText(n)).toBeInTheDocument());
  });
  it('disables (but keeps visible) CSA/Settings for a bed manager', () => {
    renderNav(['HCC.BedManager']);
    expect(screen.getByRole('tab', { name: 'CSA' })).toHaveAttribute('aria-disabled', 'true');
    expect(screen.getByRole('tab', { name: 'Settings' })).toHaveAttribute('aria-disabled', 'true');
    expect(screen.getByRole('tab', { name: 'Main' })).not.toHaveAttribute('aria-disabled', 'true');
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/navigation-plane.test.tsx`
Expected: FAIL — nav has no destinations yet.

* [ ] **Step 3: Implement the rail using Fluent `TabList` + `react-icons`, driven by `capabilities.nav`**

```typescript
import { TabList, Tab } from '@fluentui/react-components';
import { HomeRegular, GridRegular, WarningRegular, DataTrendingRegular, SettingsRegular } from '@fluentui/react-icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useRoleLens } from '../../context/role-context';

const ITEMS = [
  { key: 'start', to: '/start', icon: <HomeRegular />, label: 'Start' },
  { key: 'main', to: '/main', icon: <GridRegular />, label: 'Main' },
  { key: 'csa', to: '/csa', icon: <WarningRegular />, label: 'CSA' },
  { key: 'backstage', to: '/backstage', icon: <DataTrendingRegular />, label: 'Backstage' },
  { key: 'settings', to: '/settings', icon: <SettingsRegular />, label: 'Settings' },
] as const;

export function NavigationPlane() {
  const { capabilities } = useRoleLens();
  const nav = useNavigate();
  const loc = useLocation();
  const { t } = useTranslation();
  const selected = ITEMS.find((i) => loc.pathname.startsWith(i.to))?.key ?? 'start';
  return (
    <nav aria-label="Primary">
      <TabList vertical selectedValue={selected} onTabSelect={(_, d) => { const it = ITEMS.find((i) => i.key === d.value); if (it && (capabilities.nav as Record<string, boolean>)[it.key]) nav(it.to); }}>
        {ITEMS.map((i) => (
          <Tab key={i.key} value={i.key} icon={i.icon} disabled={!(capabilities.nav as Record<string, boolean>)[i.key]}>
            {t(`nav.${i.key}`, i.label)}
          </Tab>
        ))}
      </TabList>
    </nav>
  );
}
```

* [ ] **Step 4: Run it and watch it pass**

Run: `npm run test -- tests/unit/navigation-plane.test.tsx`
Expected: PASS.

* [ ] **Step 5: Remove the superseded `AppRail`/`TopBar`/`WorkspaceRouter` and commit**

```bash
git rm src/shell/AppRail.tsx src/shell/TopBar.tsx src/shell/WorkspaceRouter.tsx
git add src/shell/planes/NavigationPlane.tsx tests/unit/navigation-plane.test.tsx
git commit -m "feat(shell): navigation plane with role-gated destinations; remove legacy rail/router"
```

---

## Milestone M5 — Content surfaces

### Task 5.1: Start surface (vision/mission + demo disclaimer)

**Files:**

* Create: `src/workspaces/start/StartView.tsx`
* Modify: `src/shell/router.tsx` (swap the `start` stub for `StartView`)
* Test: `tests/unit/start-view.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { render, screen } from '@testing-library/react';
import { StartView } from '../../src/workspaces/start/StartView';

describe('StartView', () => {
  it('shows the mission and the simulated-data disclaimer', () => {
    render(<StartView />);
    expect(screen.getByRole('heading', { name: /curavias/i })).toBeInTheDocument();
    expect(screen.getByText(/Microsoft Innovation Hub/i)).toBeInTheDocument();
    expect(screen.getByText(/simulated .* generic data .* demo/i)).toBeInTheDocument();
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/start-view.test.tsx`
Expected: FAIL — module not found.

* [ ] **Step 3: Implement StartView with a Fluent `MessageBar` disclaimer**

```typescript
import { makeStyles, tokens, Title1, Body1, MessageBar, MessageBarBody } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';

const useStyles = makeStyles({ root: { padding: tokens.spacingHorizontalXXL, display: 'grid', gap: tokens.spacingVerticalL, maxWidth: '860px' } });

export function StartView() {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <section className={s.root} data-testid="start-view">
      <Title1>{t('start.title', 'Curavias')}</Title1>
      <Body1>{t('start.mission', 'Coordinating hospital capacity across the Swiss care network.')}</Body1>
      <MessageBar intent="info">
        <MessageBarBody>{t('start.disclaimer', 'Microsoft Innovation Hub Showcase — simulated, generic data for demo purposes only.')}</MessageBarBody>
      </MessageBar>
    </section>
  );
}
```

* [ ] **Step 4: Swap the router stub, run tests, commit**

Run: `npm run test -- tests/unit/start-view.test.tsx`
Expected: PASS.

```bash
git add src/workspaces/start/StartView.tsx src/shell/router.tsx tests/unit/start-view.test.tsx
git commit -m "feat(start): add Start surface with mission and demo-data disclaimer"
```

### Task 5.2: Main surface — mount existing whiteboard boards behind `/main/:board?`

**Files:**

* Create: `src/workspaces/main/MainView.tsx`
* Modify: `src/shell/router.tsx`
* Test: `tests/unit/main-view.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { MainView } from '../../src/workspaces/main/MainView';
import { RoleProvider } from '../../src/context/role-context';

describe('MainView', () => {
  it('defaults to the bed-manager board when no board segment is present', () => {
    render(
      <MemoryRouter initialEntries={['/main']}>
        <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
          <Routes><Route path="/main/:board?" element={<MainView />} /></Routes>
        </RoleProvider>
      </MemoryRouter>,
    );
    expect(screen.getByTestId('board-bed-manager')).toBeInTheDocument();
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/main-view.test.tsx`
Expected: FAIL — module not found.

* [ ] **Step 3: Implement MainView that reads `:board`, defaults to `bed-manager`, and renders the existing board component within the whiteboard `Canvas`**

```typescript
import { useParams } from 'react-router-dom';
import { Canvas } from '../../whiteboard/Canvas';
import { BedManagerBoard } from './boards/bed-manager/BedManagerBoard';

const BOARDS: Record<string, () => JSX.Element> = {
  'bed-manager': () => <div data-testid="board-bed-manager"><BedManagerBoard /></div>,
};

export function MainView() {
  const { board = 'bed-manager' } = useParams();
  const Board = BOARDS[board] ?? BOARDS['bed-manager'];
  return <Canvas><Board /></Canvas>;
}
```

* [ ] **Step 4: Run it and watch it pass, then commit**

Run: `npm run test -- tests/unit/main-view.test.tsx`
Expected: PASS.

```bash
git add src/workspaces/main/MainView.tsx src/shell/router.tsx tests/unit/main-view.test.tsx
git commit -m "feat(main): route existing whiteboard boards behind /main/:board"
```

### Task 5.3: CSA surface — mount the existing CSA wizard behind `/csa`

**Files:**

* Create: `src/workspaces/main/wizards/csa/CsaView.tsx`
* Modify: `src/shell/router.tsx`
* Test: `tests/unit/csa-view.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { CsaView } from '../../src/workspaces/main/wizards/csa/CsaView';
import { RoleProvider } from '../../src/context/role-context';

describe('CsaView', () => {
  it('renders the wizard for a crisis lead and blocks a viewer via the existing guard', () => {
    render(
      <MemoryRouter>
        <RoleProvider testRoles={['HCC.RegionalCrisisLead'] as never[]} testHomeSite="usz"><CsaView /></RoleProvider>
      </MemoryRouter>,
    );
    expect(screen.getByTestId('csa-view')).toBeInTheDocument();
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/csa-view.test.tsx`
Expected: FAIL — module not found.

* [ ] **Step 3: Implement CsaView wrapping the existing `CsaRoleGuard` + `CsaWizard`**

```typescript
import { CsaRoleGuard } from './CsaRoleGuard';
import { CsaWizard } from './CsaWizard';

export function CsaView() {
  return <section data-testid="csa-view"><CsaRoleGuard><CsaWizard /></CsaRoleGuard></section>;
}
```

* [ ] **Step 4: Run it, commit**

Run: `npm run test -- tests/unit/csa-view.test.tsx`
Expected: PASS.

```bash
git add src/workspaces/main/wizards/csa/CsaView.tsx src/shell/router.tsx tests/unit/csa-view.test.tsx
git commit -m "feat(csa): route the existing CSA wizard behind /csa"
```

### Task 5.4: Backstage surface — mount existing evidence/roles tabs as widgets behind `/backstage/:widget?`

**Files:**

* Create: `src/workspaces/backstage/BackstageView.tsx`
* Modify: `src/shell/router.tsx`
* Test: `tests/unit/backstage-view.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { BackstageView } from '../../src/workspaces/backstage/BackstageView';
import { RoleProvider } from '../../src/context/role-context';

describe('BackstageView', () => {
  it('defaults to the evidence widget', () => {
    render(
      <MemoryRouter initialEntries={['/backstage']}>
        <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
          <Routes><Route path="/backstage/:widget?" element={<BackstageView />} /></Routes>
        </RoleProvider>
      </MemoryRouter>,
    );
    expect(screen.getByTestId('widget-evidence')).toBeInTheDocument();
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/backstage-view.test.tsx`
Expected: FAIL — module not found.

* [ ] **Step 3: Implement BackstageView reusing the existing `EvidenceTab` / `RolesTab` as widgets in a whiteboard `Canvas`**

```typescript
import { useParams } from 'react-router-dom';
import { Canvas } from '../../whiteboard/Canvas';
import { EvidenceTab } from './tabs/evidence/EvidenceTab';
import { RolesTab } from './tabs/roles/RolesTab';

const WIDGETS: Record<string, () => JSX.Element> = {
  evidence: () => <div data-testid="widget-evidence"><EvidenceTab /></div>,
  roles: () => <div data-testid="widget-roles"><RolesTab /></div>,
};

export function BackstageView() {
  const { widget = 'evidence' } = useParams();
  const W = WIDGETS[widget] ?? WIDGETS.evidence;
  return <Canvas><W /></Canvas>;
}
```

* [ ] **Step 4: Run it, commit**

Run: `npm run test -- tests/unit/backstage-view.test.tsx`
Expected: PASS.

```bash
git add src/workspaces/backstage/BackstageView.tsx src/shell/router.tsx tests/unit/backstage-view.test.tsx
git commit -m "feat(backstage): route evidence/roles widgets behind /backstage/:widget"
```

### Task 5.5: Settings surface (app + user preferences)

**Files:**

* Create: `src/workspaces/settings/SettingsView.tsx`
* Modify: `src/shell/router.tsx`
* Test: `tests/unit/settings-view.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { render, screen } from '@testing-library/react';
import { SettingsView } from '../../src/workspaces/settings/SettingsView';
import { ThemeModeProvider } from '../../src/theme/theme-context';

describe('SettingsView', () => {
  it('surfaces theme and language preference controls', () => {
    render(<ThemeModeProvider><SettingsView /></ThemeModeProvider>);
    expect(screen.getByTestId('settings-view')).toBeInTheDocument();
    expect(screen.getByText(/preferences/i)).toBeInTheDocument();
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/settings-view.test.tsx`
Expected: FAIL — module not found.

* [ ] **Step 3: Implement SettingsView reusing `ThemeToggle` + `LanguageSelector` and showing the active role (read-only mirror of the header lens)**

```typescript
import { makeStyles, tokens, Title2, Card } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { ThemeToggle } from '../../shell/TopBar/ThemeToggle';
import { LanguageSelector } from '../../shell/TopBar/LanguageSelector';

const useStyles = makeStyles({ root: { padding: tokens.spacingHorizontalXXL, display: 'grid', gap: tokens.spacingVerticalL, maxWidth: '640px' } });

export function SettingsView() {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <section className={s.root} data-testid="settings-view">
      <Title2>{t('settings.preferences', 'Preferences')}</Title2>
      <Card><ThemeToggle /></Card>
      <Card><LanguageSelector /></Card>
    </section>
  );
}
```

* [ ] **Step 4: Run it, commit**

Run: `npm run test -- tests/unit/settings-view.test.tsx`
Expected: PASS.

```bash
git add src/workspaces/settings/SettingsView.tsx src/shell/router.tsx tests/unit/settings-view.test.tsx
git commit -m "feat(settings): add Settings surface with theme/language preferences"
```

### Task 5.6: Refresh-on-change — re-fetch content when hospital/role/route changes

**Files:**

* Create: `src/shell/useContentRefresh.ts`
* Test: `tests/unit/content-refresh.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { renderHook } from '@testing-library/react';
import { useContentRefresh } from '../../src/shell/useContentRefresh';

describe('useContentRefresh', () => {
  it('invokes the callback when any of role/hospital/route changes', () => {
    const cb = vi.fn();
    const { rerender } = renderHook(({ deps }) => useContentRefresh(deps, cb), { initialProps: { deps: ['HCC.Viewer', 'usz', '/main'] } });
    expect(cb).toHaveBeenCalledTimes(1);
    rerender({ deps: ['HCC.Viewer', 'luks', '/main'] });
    expect(cb).toHaveBeenCalledTimes(2);
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/content-refresh.test.tsx`
Expected: FAIL — module not found.

* [ ] **Step 3: Implement the hook as a thin `useEffect` over a dependency tuple**

```typescript
import { useEffect } from 'react';

export function useContentRefresh(deps: ReadonlyArray<string>, onRefresh: () => void) {
  useEffect(() => { onRefresh(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, deps);
}
```

* [ ] **Step 4: Run it, commit**

Run: `npm run test -- tests/unit/content-refresh.test.tsx`
Expected: PASS.

```bash
git add src/shell/useContentRefresh.ts tests/unit/content-refresh.test.tsx
git commit -m "feat(shell): refresh content when role/hospital/route changes"
```

---

## Milestone M6 — Four-language i18n

### Task 6.1: Add FR + IT resources and expand the supported set to four

**Files:**

* Create: `src/i18n/fr.json`, `src/i18n/it.json`
* Modify: `src/i18n/index.ts`, `src/i18n/en.json`, `src/i18n/de.json`
* Test: `tests/unit/i18n.test.ts`

* [ ] **Step 1: Write the failing test**

```typescript
import i18n from '../../src/i18n';

describe('i18n', () => {
  it('supports EN/DE/FR/IT with DE default and EN fallback', () => {
    expect(i18n.options.supportedLngs).toEqual(expect.arrayContaining(['de', 'en', 'fr', 'it']));
    expect(i18n.options.fallbackLng).toContain('en');
  });
  it('has the nav keys in every language', async () => {
    for (const lng of ['de', 'en', 'fr', 'it']) {
      await i18n.changeLanguage(lng);
      expect(i18n.t('nav.start')).not.toBe('nav.start');
      expect(i18n.t('nav.settings')).not.toBe('nav.settings');
    }
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/i18n.test.ts`
Expected: FAIL — fr/it missing, supportedLngs incomplete.

* [ ] **Step 3: Create `fr.json` and `it.json`, mirroring the key set of `de.json`/`en.json`**

Add at minimum the keys used by this sprint: `nav.{start,main,csa,backstage,settings}`, `start.{title,mission,disclaimer}`, `settings.preferences`, plus the existing keys. Example `fr.json` header block:

```json
{
  "nav": { "start": "Accueil", "main": "Principal", "csa": "CSA", "backstage": "Coulisses", "settings": "Paramètres" },
  "start": { "title": "Curavias", "mission": "Coordonner la capacité hospitalière du réseau de soins suisse.", "disclaimer": "Vitrine Microsoft Innovation Hub — données simulées et génériques à des fins de démonstration uniquement." },
  "settings": { "preferences": "Préférences" }
}
```

`it.json` block:

```json
{
  "nav": { "start": "Inizio", "main": "Principale", "csa": "CSA", "backstage": "Backstage", "settings": "Impostazioni" },
  "start": { "title": "Curavias", "mission": "Coordinare la capacità ospedaliera nella rete sanitaria svizzera.", "disclaimer": "Vetrina Microsoft Innovation Hub — dati simulati e generici solo a scopo dimostrativo." },
  "settings": { "preferences": "Preferenze" }
}
```

* [ ] **Step 4: Expand `index.ts` to register all four with DE default + EN fallback + `localStorage` persistence (`curavias.lang`)**

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import de from './de.json'; import en from './en.json'; import fr from './fr.json'; import it from './it.json';

const saved = typeof localStorage !== 'undefined' ? localStorage.getItem('curavias.lang') : null;
void i18n.use(initReactI18next).init({
  resources: { de: { translation: de }, en: { translation: en }, fr: { translation: fr }, it: { translation: it } },
  lng: saved ?? 'de', fallbackLng: 'en', supportedLngs: ['de', 'en', 'fr', 'it'], interpolation: { escapeValue: false },
});
i18n.on('languageChanged', (lng) => { if (typeof localStorage !== 'undefined') localStorage.setItem('curavias.lang', lng); });
export default i18n;
```

* [ ] **Step 5: Run it and watch it pass, commit**

Run: `npm run test -- tests/unit/i18n.test.ts`
Expected: PASS.

```bash
git add src/i18n/fr.json src/i18n/it.json src/i18n/index.ts src/i18n/en.json src/i18n/de.json tests/unit/i18n.test.ts
git commit -m "feat(i18n): add French and Italian; support EN/DE/FR/IT with DE default"
```

---

## Milestone M7 — Agent plane (dockable, context-aware)

### Task 7.1: Context map + ceiling badge

**Files:**

* Create: `src/shell/planes/agent-context-map.ts`
* Test: `tests/unit/agent-context-map.test.ts`

* [ ] **Step 1: Write the failing test**

```typescript
import { agentForRoute } from '../../src/shell/planes/agent-context-map';

describe('agent context map', () => {
  it('maps each surface to its default agent', () => {
    expect(agentForRoute('/start')).toBe('orchestrator');
    expect(agentForRoute('/main/bed-manager')).toBe('bmca-agent');
    expect(agentForRoute('/csa')).toBe('csa-agent');
    expect(agentForRoute('/backstage/evidence')).toBe('knowledge-agent');
    expect(agentForRoute('/settings')).toBe('orchestrator');
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/agent-context-map.test.ts`
Expected: FAIL — module not found.

* [ ] **Step 3: Implement the map**

```typescript
export function agentForRoute(pathname: string): string {
  if (pathname.startsWith('/main')) return 'bmca-agent';
  if (pathname.startsWith('/csa')) return 'csa-agent';
  if (pathname.startsWith('/backstage')) return 'knowledge-agent';
  return 'orchestrator';
}
```

* [ ] **Step 4: Run it, commit**

Run: `npm run test -- tests/unit/agent-context-map.test.ts`
Expected: PASS.

```bash
git add src/shell/planes/agent-context-map.ts tests/unit/agent-context-map.test.ts
git commit -m "feat(agent): map each surface to its context agent"
```

### Task 7.2: Dockable AgentPlane (icon-only â†” open) wrapping the existing drawer

**Files:**

* Modify: `src/shell/planes/AgentPlane.tsx`
* Test: `tests/unit/agent-plane.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { render, screen, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AgentPlane } from '../../src/shell/planes/AgentPlane';
import { RoleProvider } from '../../src/context/role-context';

function renderAgent(roles: string[], path = '/csa') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <RoleProvider testRoles={roles as never[]} testHomeSite="usz"><AgentPlane /></RoleProvider>
    </MemoryRouter>,
  );
}

describe('AgentPlane', () => {
  it('starts collapsed (icon only) and opens on toggle', () => {
    renderAgent(['HCC.RegionalCrisisLead']);
    const toggle = screen.getByRole('button', { name: /open agent/i });
    expect(screen.queryByRole('complementary')).not.toBeInTheDocument();
    act(() => toggle.click());
    expect(screen.getByRole('complementary')).toBeInTheDocument();
  });
  it('shows the action ceiling badge derived from the active role', () => {
    renderAgent(['HCC.Viewer']);
    act(() => screen.getByRole('button', { name: /open agent/i }).click());
    expect(screen.getByText(/read/i)).toBeInTheDocument();
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/agent-plane.test.tsx`
Expected: FAIL — plane is a stub.

* [ ] **Step 3: Implement the dockable plane, reusing the existing `Drawer` conversation UI and the context map + lens**

```typescript
import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Button, Badge, makeStyles, tokens } from '@fluentui/react-components';
import { BotRegular } from '@fluentui/react-icons';
import { Drawer } from '../../copilot-drawer/Drawer';
import { agentForRoute } from './agent-context-map';
import { useRoleLens } from '../../context/role-context';

const useStyles = makeStyles({
  rail: { width: '48px', display: 'flex', justifyContent: 'center', paddingTop: tokens.spacingVerticalM },
  panel: { width: '360px', height: '100%', borderLeft: `1px solid ${tokens.colorNeutralStroke2}` },
});

export function AgentPlane() {
  const s = useStyles();
  const [open, setOpen] = useState(false);
  const loc = useLocation();
  const { capabilities } = useRoleLens();
  const agent = agentForRoute(loc.pathname);
  if (!open) {
    return <div className={s.rail}><Button aria-label="Open agent" icon={<BotRegular />} appearance="subtle" onClick={() => setOpen(true)} /></div>;
  }
  return (
    <aside role="complementary" aria-label="Agent" className={s.panel}>
      <Button aria-label="Close agent" appearance="subtle" onClick={() => setOpen(false)}>Close</Button>
      <Badge appearance="tint">{capabilities.agentCeiling}</Badge>
      <Drawer agent={agent} />
    </aside>
  );
}
```

Note: match the actual `Drawer` prop contract — if the existing `Drawer` selects its agent from `agent-manifest.ts` rather than a prop, pass the equivalent selector instead of `agent={agent}`.

* [ ] **Step 4: Run it and watch it pass, commit**

Run: `npm run test -- tests/unit/agent-plane.test.tsx`
Expected: PASS.

```bash
git add src/shell/planes/AgentPlane.tsx tests/unit/agent-plane.test.tsx
git commit -m "feat(agent): dockable context-aware agent plane with role ceiling badge"
```

---

## Milestone M8 — Footer plane

### Task 8.1: App version define + footer with refresh-rate dropdown

**Files:**

* Create: `src/config/app-version.ts`
* Modify: `vite.config.ts` (add `define: { __APP_VERSION__: JSON.stringify(pkg.version) }`), `src/shell/planes/FooterPlane.tsx`
* Test: `tests/unit/footer-plane.test.tsx`

* [ ] **Step 1: Write the failing test**

```typescript
import { render, screen } from '@testing-library/react';
import { FooterPlane } from '../../src/shell/planes/FooterPlane';

describe('FooterPlane', () => {
  it('shows the app version and a refresh-rate selector', () => {
    render(<FooterPlane />);
    expect(screen.getByText(/v\d+\.\d+\.\d+/)).toBeInTheDocument();
    expect(screen.getByLabelText(/refresh rate/i)).toBeInTheDocument();
  });
});
```

* [ ] **Step 2: Run it and watch it fail**

Run: `npm run test -- tests/unit/footer-plane.test.tsx`
Expected: FAIL — footer is a stub.

* [ ] **Step 3: Add the version define + config module**

```typescript
// src/config/app-version.ts
declare const __APP_VERSION__: string;
export const APP_VERSION = typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : '0.0.0';
```

Add a matching declaration to `src/vite-env.d.ts`: `declare const __APP_VERSION__: string;`

* [ ] **Step 4: Implement the FooterPlane**

```typescript
import { makeStyles, tokens, Text, Dropdown, Option } from '@fluentui/react-components';
import { APP_VERSION } from '../../config/app-version';

const useStyles = makeStyles({ bar: { display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: tokens.spacingHorizontalM, height: '28px', padding: `0 ${tokens.spacingHorizontalL}`, backgroundColor: tokens.colorNeutralBackground3 } });
const RATES = [['off', 'Off'], ['30', '30s'], ['60', '60s'], ['300', '5m']] as const;

export function FooterPlane() {
  const s = useStyles();
  return (
    <footer role="contentinfo" className={s.bar}>
      <Dropdown aria-label="Refresh rate" size="small" defaultValue="Off" defaultSelectedOptions={['off']}>
        {RATES.map(([v, l]) => <Option key={v} value={v}>{l}</Option>)}
      </Dropdown>
      <Text size={200}>{`v${APP_VERSION}`}</Text>
    </footer>
  );
}
```

* [ ] **Step 5: Run it and watch it pass, commit**

Run: `npm run test -- tests/unit/footer-plane.test.tsx; npm run lint`
Expected: PASS; type-check clean.

```bash
git add src/config/app-version.ts src/vite-env.d.ts vite.config.ts src/shell/planes/FooterPlane.tsx tests/unit/footer-plane.test.tsx
git commit -m "feat(shell): footer plane with app version and refresh-rate selector"
```

---

## Milestone M9 — Integration, e2e, a11y, and close

### Task 9.1: End-to-end shell smoke (Playwright)

**Files:**

* Create: `tests/e2e/shell.spec.ts`

* [ ] **Step 1: Write the e2e test**

```typescript
import { test, expect } from '@playwright/test';

test('five-plane shell renders and Start is the default surface', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('banner')).toBeVisible();
  await expect(page.getByRole('navigation')).toBeVisible();
  await expect(page.getByRole('contentinfo')).toBeVisible();
  await expect(page.getByTestId('start-view')).toBeVisible();
});

test('navigating to Main renders a board', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('tab', { name: 'Main' }).click();
  await expect(page.getByTestId('board-bed-manager')).toBeVisible();
});
```

* [ ] **Step 2: Run it**

Run: `npm run test:e2e -- tests/e2e/shell.spec.ts`
Expected: PASS (dev server auto-started per the existing Playwright config).

* [ ] **Step 3: Commit**

```bash
git add tests/e2e/shell.spec.ts
git commit -m "test(e2e): five-plane shell smoke and Main navigation"
```

### Task 9.2: Accessibility gate for the new shell surfaces

**Files:**

* Modify: `tests/e2e/a11y.spec.ts`

* [ ] **Step 1: Extend the axe scan to cover Start, Main, CSA, Backstage, Settings**

Add, for each route, a block that navigates and asserts zero serious/critical axe violations, mirroring the existing pattern in `a11y.spec.ts`:

```typescript
for (const path of ['/start', '/main', '/csa', '/backstage', '/settings']) {
  test(`no critical a11y violations on ${path}`, async ({ page }) => {
    await page.goto(path);
    const results = await new AxeBuilder({ page }).analyze();
    const serious = results.violations.filter((v) => ['serious', 'critical'].includes(v.impact ?? ''));
    expect(serious).toEqual([]);
  });
}
```

* [ ] **Step 2: Run the a11y gate**

Run: `npm run test:a11y`
Expected: PASS — no serious/critical violations. Fix contrast/label issues if any surface fails (contrast is pre-solved by the Curavias tokens; failures are most likely missing `aria-label`s).

* [ ] **Step 3: Commit**

```bash
git add tests/e2e/a11y.spec.ts
git commit -m "test(a11y): extend axe scan to the five shell surfaces"
```

### Task 9.3: Full regression + build

**Files:** none (verification only).

* [ ] **Step 1: Run the complete gate**

Run: `npm run lint; npm run test; npm run build`
Expected: type-check clean; all Vitest suites pass (>= the M0 baseline count, plus the new tests); `tsc -b && vite build` succeeds.

* [ ] **Step 2: If any legacy test referenced the removed `TopBar`/`AppRail`/`WorkspaceRouter`, update it to the new shell selectors**

The existing `tests/unit/shell.test.tsx` targets the old shell — rewrite its assertions against `AppShell`/`NavigationPlane`, or delete it if fully superseded by `app-shell.test.tsx` + `navigation-plane.test.tsx`. Commit any such change with `test:` prefix.

---

## Validation checklist (run before PR)

* [ ] `npm run lint` — `tsc --noEmit` clean.
* [ ] `npm run test` — all Vitest unit/integration suites pass; new-code coverage does not drop below the M0 baseline.
* [ ] `npm run test:e2e` — shell smoke + Main navigation pass.
* [ ] `npm run test:a11y` — zero serious/critical axe violations on all five surfaces.
* [ ] `npm run build` — production build succeeds.
* [ ] Manual: switch language across EN/DE/FR/IT and confirm nav + Start text change and persist across reload.
* [ ] Manual: switch role in the header and confirm nav gating, hospital scope, and the agent ceiling badge all update.
* [ ] Manual: toggle light/dark and confirm the Curavias green/secondary palette and persisted preference.
* [ ] Docs: sprint doc, design spec, and this plan pass `python scripts/lint/check_mojibake.py` and `npx markdownlint-cli2` (already gated on the doc branch).

## Sprint close criteria

* [ ] All M0–M9 tasks committed on a `sprint20/*` implementation branch.
* [ ] The five-plane shell is the app's only entry path; `AppRail`/`TopBar`/`WorkspaceRouter` are removed.
* [ ] Role dropdown acts as an access lens (narrow-only) that gates nav, hospital scope, boards/widgets, and the agent ceiling.
* [ ] Four languages selectable and persisted; DE default, EN fallback.
* [ ] Curavias theme (light + dark) replaces the Helvion theme; WCAG AA verified by the a11y gate.
* [ ] Agent plane is dockable and context-aware across all surfaces.
* [ ] PR description lists the FR/NFR IDs from the design spec §16 and states lane = Experience with `none` for infra/security/compliance impact.
* [ ] Design spec and sprint doc `Status` updated from `Draft for review` to `Delivered` only after the validation checklist is fully green.

---

## Execution notes

* This plan targets an existing codebase — always read the current file before editing and follow the established Fluent-UI-v9 patterns already in `src/cards`, `src/whiteboard`, and `src/copilot-drawer`.
* Where a task says "reuse the existing X", verify X's real export/prop shape before wiring; the tests above assert behaviour, not internal signatures, so adapt the wiring to the real component contract.
* Keep each commit green: a task is not done until its test passes and `tsc --noEmit` is clean.
