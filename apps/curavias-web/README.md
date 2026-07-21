# Curavias Web (`apps/curavias-web`)

Astro static site for the **Curavias — Swiss Hospital Capacity Copilot** product landing
page, published to **PROD only** on `curavias.ch` / `www.curavias.ch` via Azure Static Web
Apps.

> **Showcase.** Not a real product. Curavias is a Microsoft Innovation Hub Zürich showcase —
> synthetic data, advisory-only AI, not a medical device, not for clinical use. The showcase
> disclaimer MUST remain visible on every page.

## Stack

- **Astro 4** static output, TypeScript strict, zero client JS (fully static HTML/CSS).
- Brand tokens mirror `docs/brandkit/color/curavias-tokens.css` (white background).
- Multilingual via Astro i18n: **DE-CH** default (unprefixed), **EN/FR/IT** prefixed
  (`/en`, `/fr`, `/it`). Content lives in `src/i18n/<locale>.ts` against the typed
  `SiteContent` model in `src/i18n/types.ts`.

## Content model

All copy is data-driven. The source of truth is `src/i18n/de.ts`, sourced from
`docs/superpowers/ideas/curavias-product-webpage/curavias-bom/curavias-context.md`.
Add a locale by creating `src/i18n/<locale>.ts` and registering it in `src/i18n/index.ts`.

## Structure

```
src/
  i18n/         types.ts, de.ts, index.ts (locale registry + helpers)
  layouts/      BaseLayout.astro, LandingPage.astro
  components/   Header, Footer, Hero, DisclaimerBanner, KpiStrip, Summary,
                Challenger, PatientPath, Agents, Experiences, Trust,
                ValueTable, NextSteps, BrandMark
  pages/        index.astro (de), 404.astro
public/         brand/curavias-icon.svg, robots.txt, staticwebapp.config.json
```

## Commands

```bash
npm install
npm run dev       # local dev server
npm run build     # astro check + astro build -> dist/
npm run preview   # preview the production build
```

## Deployment

Static output in `dist/` is deployed by the `curavias-web-deploy` workflow (OIDC, gated
`prod` environment) to Azure Static Web Apps. Custom domains `curavias.ch` + `www.curavias.ch`
are bound via the Azure DNS zone (`infra/modules/dns/curavias.bicep`, ADR-0030).
