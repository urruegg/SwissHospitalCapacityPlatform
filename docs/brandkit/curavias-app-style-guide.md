# Curavias App Style Guide (Fluent v9 + M365)

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-07-27 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (added the companion UX pattern catalogue cross-reference; issue #365) |
| **Sprint** | 27 — Curavias App UX Polish (tracker #365) |
| **Applies to** | `apps/hcc-app-fluent` (internal app, app.curavias.ch) |

> The single source of visual truth for the internal Curavias app. It maps the codified
> design system (`apps/hcc-app-fluent/src/theme/design-system/`) to the Fluent UI v9
> primitive each token wraps and the current Microsoft 365 app pattern (Outlook / Teams /
> M365 Copilot) it mirrors, and defines the per-screen heuristic review gate. Realises
> `FR-UX-002`; the checklist is the acceptance gate behind `NFR-UX-002`. For the
composed component + layout patterns (P1–P12) built from these tokens and recipes,
see the companion [`curavias-ux-patterns.md`](curavias-ux-patterns.md).

---

## 1. Token map

Import tokens from `src/theme/design-system` as `ds`. Never hard-code the underlying values.

| Token | Value / Fluent primitive | Mirrors (M365 pattern) |
|-------|--------------------------|------------------------|
| `ds.space.xs` (4px) | 4px | Chip and badge internal gaps |
| `ds.space.s` (8px) | 8px | Icon-to-label gaps; Outlook list-row inner padding |
| `ds.space.m` (12px) | 12px | Control grouping; Teams pane section gaps |
| `ds.space.l` (16px) | 16px | Card padding; board section spacing |
| `ds.space.xl` (24px) | 24px | Surface padding; M365 Copilot chat block spacing |
| `ds.space.xxl` (32px) | 32px | Empty-state and hero spacing |
| `ds.radii.control` | `borderRadiusMedium` | Buttons, inputs, tiles |
| `ds.radii.card` | `borderRadiusLarge` | Cards and surfaces |
| `ds.radii.pill` | `borderRadiusCircular` | Badges, status pills |
| `ds.elevation.flat` | `shadow2` | Resting rows / low-emphasis surfaces |
| `ds.elevation.card` | `shadow4` | Default cards (Fluent Card resting) |
| `ds.elevation.raised` | `shadow8` | Card hover / active (Teams pane hover) |
| `ds.elevation.overlay` | `shadow16` | Popovers, docked agent plane |
| `ds.elevation.dialog` | `shadow28` | Dialogs and modal surfaces |
| `ds.motion.durationFast` | `durationFaster` | Hover / focus micro-transitions |
| `ds.motion.durationNormal` | `durationNormal` | Card and panel transitions |
| `ds.motion.durationSlow` | `durationSlow` | Dock / drawer open-close |
| `ds.motion.easyEase` | `curveEasyEase` | Symmetric hover transitions |
| `ds.motion.decelerate` | `curveDecelerateMid` | Enter transitions (drawer / panel open) |
| `ds.focus.ringWidth` (2px) | 2px | Visible focus ring width |
| `ds.focus.ringOffset` (2px) | 2px | Visible focus ring offset |

Colour and RAG signalling stay on the existing Curavias theme (`curavias-theme.ts` +
`curavias-tokens.json`): green `#17B890` primary (dark text on green), blue `#365B7D`
secondary, and the `ragColors` map for red/amber/green status.

## 2. Recipe catalogue

Import recipes via `useSurfaceStyles()` and `useStateStyles()` from
`src/theme/design-system/recipes`.

| Recipe | Use when |
|--------|----------|
| `surfaceCard` | Any card / panel surface; raises on hover and shows a focus ring on `:focus-within`. |
| `boardGrid` | Responsive card grid on a MAIN role board (auto-fill, min 280px). |
| `sectionHeader` | The title + actions row above a card or board section. |
| `statTile` | A single KPI / metric tile (label + value). |
| `provenanceBadge` | The live-vs-simulated provenance pill (styled, never bypassed). |
| `emptyState` | No-data state — centred message + optional action. |
| `loadingState` | In-flight state — replace bare "Loading..." text. |
| `errorState` | Failed-load state — message with error colour. |

## 3. Per-screen heuristic checklist (the review gate)

A screen exits review only when every item holds. This is the reusable gate for every
screen this sprint and in the backlog (`NFR-UX-002`).

- **8 pt grid** — all spacing comes from `ds.space`; no raw pixel spacing literals.
- **Type ramp** — text uses Fluent `Text` / typography components; no ad-hoc `font-size`.
- **Elevation** — surfaces use `ds.elevation`; cards raise on hover.
- **Motion** — transitions use `ds.motion` durations and curves.
- **Interaction states** — visible hover, pressed, and focus states on all interactive elements.
- **Async states** — explicit `emptyState`, `loadingState`, and `errorState` (no bare text).
- **Dark-mode parity** — verified in both light and dark themes.
- **Accessibility (WCAG 2.1 AA)** — sufficient contrast, visible focus, correct roles and
  accessible names; `npm run test:a11y` green (`NFR-UX-001`).

## 4. Do / Don't

- **Do** import spacing, radii, elevation, motion, and focus from `ds`.
- **Don't** hard-code pixel spacing or shadow values in components.
- **Do** use Fluent `Text` / typography for all copy.
- **Don't** set raw `font-size` / `line-height` on text.
- **Do** render the `loadingState` / `emptyState` / `errorState` recipes for async surfaces.
- **Don't** ship a bare `Loading...` string or an unstyled error.
- **Do** keep the provenance badge styled through `provenanceBadge` — never remove or fake it.
- **Don't** import from or copy styles out of `apps/curavias-web` (the Astro public site,
  www.curavias.ch) — it is a different product surface and out of scope.
- **Don't** introduce PHI or real patient data (ADR-0016).
