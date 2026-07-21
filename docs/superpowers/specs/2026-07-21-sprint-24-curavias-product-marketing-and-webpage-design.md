# Sprint 24 — Curavias Product-Marketing Copilot + Product Landing Page (Astro, PROD) — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-21 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | (none; initial design draft for review) |
| **Anchor triggers** | User request to (1) establish a product-marketing copilot agent grounded in the Curavias brandkit + vision/mission for stringent, cross-channel communication aligned with `ux-design-agent`, and (2) build + publish a Curavias product landing page (Astro) to PROD (`curavias.ch` + `www.curavias.ch`) from `docs/superpowers/ideas/curavias-product-webpage/curavias-site` |
| **Runtime posture** | GitHub Copilot coding agent + Superpowers-first execution (ADR-0002). New `product-marketing-agent` is a control-plane prompt pack; the Astro site is an Experience-lane app deliverable deployed to Azure. No change to per-agent runtime posture. |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Context and problem statement](#2-context-and-problem-statement)
3. [Scope](#3-scope)
4. [Part 1 — product-marketing-agent](#4-part-1--product-marketing-agent)
5. [Part 2 — Curavias Astro site](#5-part-2--curavias-astro-site)
6. [Infrastructure (PROD only)](#6-infrastructure-prod-only)
7. [Delivery and deployment](#7-delivery-and-deployment)
8. [Internationalisation (DE/EN/FR/IT)](#8-internationalisation-deenfrit)
9. [Agent alignment and RACI](#9-agent-alignment-and-raci)
10. [Governance, security and compliance](#10-governance-security-and-compliance)
11. [Component boundaries](#11-component-boundaries)
12. [Testing and accessibility](#12-testing-and-accessibility)
13. [Sprint anchoring and work breakdown](#13-sprint-anchoring-and-work-breakdown)
14. [Dependencies](#14-dependencies)
15. [Risk register](#15-risk-register)
16. [Traceability](#16-traceability)
17. [Definition of done](#17-definition-of-done)
18. [References](#18-references)

---

## 1. Goal and desired end state

Two coupled deliverables that together give Curavias a **single source of message
truth** and a **public product presence**:

1. A **`product-marketing-agent`** — a control-plane agent that owns product
   messaging, voice, positioning, and cross-channel consistency (customer-facing,
   user-facing, devops-team-facing), grounded in the Curavias brandkit and the
   vision/mission/north-star, and cleanly aligned with the `ux-design-agent`
   (message vs. experience boundary).
2. A **Curavias product website** built with **Astro** (static), ported from the
   existing `curavias-site` HTML mockup, brandkit-aligned (white background),
   available in **DE / EN / FR / IT**, and **published to PROD** on `curavias.ch`
   and `www.curavias.ch`.

**Desired end state:**

* `agents/product-marketing-agent/` exists (AGENT.md + manifest.yaml +
  golden-tasks.md), registered in `AGENTS.md`, ceiling `write`, no new MCP server.
* A documented RACI cleanly separates message ownership (marketing) from
  experience ownership (UX), with a defined handoff.
* `apps/curavias-web/` is an Astro project rendering all five pages (index,
  agents, architecture, ontology-explorer, product-build) across four locales, with
  the showcase disclaimer on every page/locale.
* Azure Static Web App (`stapp-ihzhhpf-prod`) serves the site; an Azure Storage
  media library (`stmediaihzhhpfprod`) holds photos/icons/artefacts.
* `curavias.ch` and `www.curavias.ch` resolve to the SWA over managed TLS.
* CI builds and deploys via OIDC into a gated PROD environment.

## 2. Context and problem statement

Curavias messaging currently lives across a flyer, `curavias-context.md`, the
brandkit, the app shell, and the `curavias-site` HTML mockup. There is **no single
agent that guarantees message consistency** across customer, user, and internal
channels, and **no published public webpage**. The `ux-design-agent` (Sprint 20)
owns experience judgment but explicitly does **not** own copy/voice/positioning.

The `curavias-site` mockup (five self-contained HTML pages, 13 landing sections,
inline SVG, embedded imagery) is a validated visual starting point but is not a
maintainable, multilingual, deployable site. This sprint converts it to Astro and
publishes it, while standing up the messaging agent that keeps its copy — and all
other Curavias copy — on-brand and compliant.

## 3. Scope

### In scope

* Author `product-marketing-agent` pack + `AGENTS.md` registry row + RACI.
* Scaffold `apps/curavias-web/` Astro project; port all five `curavias-site` pages
  into layouts + section components; brandkit tokens; white background.
* Astro i18n for DE (default) / EN / FR / IT; DE copy from the mockup, EN/FR/IT
  drafted by `product-marketing-agent` and placed by `ux-design-agent`.
* Azure Static Web App + Storage media library Bicep under `infra/`, PROD only.
* GitHub Actions deploy workflow (OIDC, gated PROD environment) + custom-domain
  binding + media upload.
* Showcase disclaimer, per-locale SEO/OpenGraph/alt-text, WCAG AA.

### Out of scope

* SIT/DEV environments for the website (PROD only, per user decision).
* Real (non-synthetic) content, real patient/clinician names, PHI (ADR-0016).
* Video production (BOM VID-01..04 remain P1/P2 backlog).
* Brand Central asset download automation (sign-in gated; tracked task).
* Changing the `hcc-app-fluent` application (separate Experience-lane track).

## 4. Part 1 — product-marketing-agent

### 4.1 Pack layout

`agents/product-marketing-agent/` with `AGENT.md`, `manifest.yaml`,
`golden-tasks.md`, matching the fixed AGENT.md structure (Identity · Scope · Tools ·
Grounding · Refusal Rules · Output Contract · Confirmation Rules · Golden Tasks).

### 4.2 Identity and channels

Product-marketing / communications steward for Curavias. Guarantees that every
externally- or internally-visible message is **stringent, on-brand, and aligned**
across three channels:

* **Customer-facing** — website copy, executive/CIO framing, flyer, CTAs.
* **User-facing** — in-app copy, onboarding, tooltips, empty states, notifications.
* **Devops-team-facing** — README/enablement, release notes, PR/issue communication,
  internal narrative.

### 4.3 Tools and ceiling

| MCP server | Ceiling | Use |
| ---------- | ------- | --- |
| `github-mcp` | `write` | Draft/update copy in issues, PRs, comments, branches |
| `playwright-mcp` | `read` (optional) | Review copy *in rendered context* (shared with `ux-design-agent`) |

No new MCP server → `.github/copilot/mcp.json` allow-list unchanged.

### 4.4 Grounding sources

`docs/brandkit/` (guidelines, colour, voice), `curavias-context.md` (north star,
tagline, patient path, 7 agents, 3 experiences, BVA, guardrails), `docs/PRD.md`
(FR/NFR IDs), ADR-0016 (no-PHI demo gate).

### 4.5 Voice guardrails and refusal rules

Inherit shared refusals (AGENTS.md §5). In addition:

| Code | Trigger |
| ---- | ------- |
| `REFUSE: non-advisory-voice` | Copy states the AI "entscheidet/diagnostiziert" or otherwise breaks the advisory-only voice ("beraet/Vorschlag/Vorschau"). |
| `REFUSE: missing-disclaimer` | A customer- or user-facing artefact omits the mandatory showcase disclaimer. |
| `REFUSE: clinical-claim` | Copy implies a medical device, clinical use, or regulatory approval. |
| `REFUSE: real-identity` | Copy uses real patient/clinician names or non-synthetic testimonials. |
| `REFUSE: out-of-lane` | Request asks for layout/visual/a11y decisions (redirect to `ux-design-agent`) or backend/data/infra changes (redirect to owning agent). |

### 4.6 Output contract

Channel-tagged copy blocks (customer / user / devops) plus a **voice & compliance
checklist** (disclaimer present · advisory verbs · no clinical claim ·
synthetic-only · Microsoft/Swiss-cross brand notes respected) and the `FR-*`/`NFR-*`
IDs advanced.

### 4.7 Golden tasks

* Happy-path: draft the DE hero + subhead with disclaimer and advisory voice.
* Failure-mode A: refuse copy containing "entscheidet/diagnostiziert".
* Failure-mode B: refuse a customer-facing artefact with the disclaimer removed.
* Failure-mode C: refuse real-name testimonial / PHI.

## 5. Part 2 — Curavias Astro site

### 5.1 Stack and structure

* Astro with `output: 'static'`, TypeScript, brandkit tokens imported from
  `docs/brandkit/color/` (or a copied token module). White background baseline.
* `src/layouts/BaseLayout.astro` — head, per-locale SEO/OpenGraph, disclaimer
  banner, footer.
* `src/components/sections/*` — Hero, KpiStrip, HumanDecides, CioChallenger,
  PatientPath, SevenAgents, ThreeExperiences, Security, BusinessValue, Reviews,
  Cta. Inline SVG retained from the mockup.
* `src/pages/**` — index, agents, architecture, ontology-explorer, product-build
  (per locale via i18n routing).
* Interactivity (e.g. patient-path hover) implemented as a small Astro island only
  where needed; otherwise static HTML/CSS.

### 5.2 Content and media

* Copy stored in per-locale content collections / dictionaries. DE from the mockup;
  EN/FR/IT authored by `product-marketing-agent`.
* Images/icons referenced from the Storage media library via an
  environment-configurable base URL. Inline SVG stays in-repo.
* Brand Central stock + Microsoft marks are sign-in gated → tracked task; the site
  ships with placeholders until approved assets are uploaded.

## 6. Infrastructure (PROD only)

Bicep under `infra/`, PROD only, naming per copilot-instructions §8
(`ihzhhpf`, `-prod` suffix):

| Module | Resource | Name | Notes |
| ------ | -------- | ---- | ----- |
| `infra/modules/static-web-app.bicep` | Static Web App | `stapp-ihzhhpf-prod` | Standard tier; custom domains; managed TLS |
| `infra/modules/storage-media.bicep` | Storage account | `stmediaihzhhpfprod` | Blob `media` container; static-website or CDN read for public assets |

* `infra/environments/prod.*` parameters. Tags on every resource: `env=prod`,
  `owner`, `costCenter`, `workload=curavias-web`.
* `az bicep build` + `what-if` are mandatory CI gates before any apply.
* **Residency note**: Azure Static Web Apps is a global/CDN-fronted service; content
  is edge-served. The site carries **no PHI** (public marketing showcase), so Swiss
  data-residency risk is low and is documented explicitly rather than engineered
  around.

## 7. Delivery and deployment

* `.github/workflows/curavias-web-deploy.yml`: install → build Astro → deploy to SWA
  via **OIDC / Workload Identity Federation**; a separate step/job syncs the media
  library to Storage.
* Deployment targets a **gated PROD GitHub environment** (manual approval); any
  `deploy` MCP action follows the plan-first / `approved-to-apply` rule
  (AGENTS.md §4).
* **Custom domains**: bind `curavias.ch` (apex) and `www.curavias.ch` to the SWA;
  managed TLS. DNS records at the registrar are a tracked prerequisite task.

## 8. Internationalisation (DE/EN/FR/IT)

* Astro i18n: `defaultLocale: 'de'`, `locales: ['de','en','fr','it']`, routed `/`,
  `/en`, `/fr`, `/it`.
* DE-CH is the source of truth (existing mockup copy). EN/FR/IT are drafted by
  `product-marketing-agent` (brand-aligned, advisory voice, disclaimer present) and
  placed/reviewed by `ux-design-agent`.
* Per-locale metadata: title, meta description, OpenGraph image, `hreflang`
  alternates, and alt text for every image/diagram.

## 9. Agent alignment and RACI

The two agents own **different judgment layers** and hand off cleanly:

| Activity | `product-marketing-agent` | `ux-design-agent` |
| -------- | ------------------------- | ----------------- |
| Message, voice, positioning, claims, disclaimer | **A / R** | C |
| Copy per channel + locale | **A / R** | C |
| Layout, visual system, component/section design | C | **A / R** |
| Accessibility (WCAG) + i18n placement | C | **A / R** |
| Brand-token/colour usage | C | **A / R** |
| Rendered copy-in-context review (Playwright) | C | **A / R** |

Handoff: marketing drafts channel/locale copy → UX places it in mockups/components
and verifies visual + a11y → marketing signs off on final voice. Both `AGENT.md`
files reference this table.

## 10. Governance, security and compliance

* Adding `product-marketing-agent` + the `AGENTS.md` registry row requires a
  human-authored issue + CODEOWNERS review (AGENTS.md §6) — provided by this
  sprint's child issue.
* No secrets in code/config/PRs; OIDC/WIF for Azure deploy; no long-lived secrets.
* Showcase disclaimer mandatory on every page/locale; advisory-only framing
  everywhere; synthetic content only (ADR-0016).
* **Legal (accepted residual risk)**: trademark clearance (CH/EU healthcare-IT /
  software) and Swiss-cross legal review are flagged in the brandkit as required
  *before public production use*. Per the sprint decision, the site is published
  publicly now relying on the disclaimer + advisory framing; legal clearance remains
  a tracked residual-risk task to close before any formal announcement.

## 11. Component boundaries

* `agents/product-marketing-agent/` — prompt + manifest + fixtures (control plane).
* `apps/curavias-web/src/layouts` — shell (head/SEO/disclaimer/footer).
* `apps/curavias-web/src/components/sections` — one component per landing section,
  independently reviewable and testable.
* `apps/curavias-web/src/content` (or `i18n/`) — copy dictionaries per locale.
* `infra/modules/{static-web-app,storage-media}.bicep` — one resource per module.
* `.github/workflows/curavias-web-deploy.yml` — build + deploy + media sync.

## 12. Testing and accessibility

* Astro build must succeed for all locales; broken-link check across pages/locales.
* WCAG AA verified with `axe-core` via the `ux-design-agent` Playwright harness
  (both modes: local CLI and `playwright-mcp`).
* `az bicep build` + `what-if` green on infra changes.
* Markdown lint + link check + mojibake gate on all docs.
* Agent change ships happy-path + failure-mode golden tasks (§4.7).

## 13. Sprint anchoring and work breakdown

One **epic sprint issue** anchors the sprint; **seven child issues** decompose it:

1. `product-marketing-agent` pack + `AGENTS.md` row + RACI (control plane; CODEOWNERS).
2. Astro scaffold + port five `curavias-site` pages to layouts/components (Experience).
3. DE/EN/FR/IT i18n + copy (marketing drafts, UX places).
4. Infra Bicep — SWA + Storage media library, PROD params (Infra).
5. Deploy workflow (OIDC, gated PROD) + custom-domain binding (Delivery).
6. Media library upload (Brand Central + generated assets) (Experience/Assets).
7. Legal + DNS tracking (trademark/Swiss-cross clearance; registrar DNS) (Governance).

Each child issue follows the PR Output Contract and references the FR/NFR IDs it
advances.

## 14. Dependencies

* Azure subscription `66a9953a-...` (tenant MCAP164444), OIDC federation for PROD.
* Registrar/DNS control for `curavias.ch` (custom-domain binding).
* Brand Central sign-in for approved Microsoft marks + stock imagery.
* Brandkit tokens under `docs/brandkit/color/`.
* `ux-design-agent` (Sprint 20) for placement + a11y verification.

## 15. Risk register

| ID | Risk | Likelihood | Impact | Mitigation |
| -- | ---- | ---------- | ------ | ---------- |
| R1 | Trademark / Swiss-cross clearance pending at public go-live | Med | High | Disclaimer + advisory framing; tracked legal task before announcement (accepted) |
| R2 | DNS control for `curavias.ch` unavailable | Low | High | Child issue #7 verifies registrar access before domain binding |
| R3 | EN/FR/IT translation quality/voice drift | Med | Med | Marketing agent drafts + voice checklist; UX places; native review before launch |
| R4 | Brand Central asset licensing / access | Med | Med | Placeholders until approved assets uploaded to media library |
| R5 | SWA residency perception for a Swiss brand | Low | Low | Documented: no PHI, public marketing content, global CDN acceptable |
| R6 | Scope (full 5 pages x 4 locales) exceeds one increment | Med | Med | Child issues sequence DE-complete first, then EN/FR/IT per page |

## 16. Traceability

New requirement IDs will be proposed in `docs/PRD.md` in the implementation PRs and
recorded in the §7 traceability matrix:

* `FR-MKT-*` — product-marketing-agent message-consistency requirements.
* `FR-WEB-*` — public Curavias website requirements.
* Reuses/extends existing `FR-CX-*`, `FR-VIZ-*`, `NFR-GOV-*`, `NFR-REL-*` where the
  website advances experience/governance requirements already catalogued.

## 17. Definition of done

* `product-marketing-agent` pack + `AGENTS.md` row merged with golden tasks green;
  RACI documented in both agent files.
* `apps/curavias-web` builds all five pages in DE/EN/FR/IT with the disclaimer on
  every page/locale; WCAG AA clean.
* SWA + Storage provisioned (PROD); `curavias.ch` + `www.curavias.ch` serve the site
  over managed TLS.
* Deploy workflow green via OIDC into the gated PROD environment.
* Docs updated + versioned (§9 versioning); PRD FR/NFR + traceability updated.
* Residual-risk tasks (legal, DNS, Brand Central) tracked and owned.

## 18. References

* `docs/brandkit/Curavias-Brand-Guidelines.md` — brand, colour, voice, legal notes.
* `docs/superpowers/ideas/curavias-product-webpage/curavias-bom/curavias-context.md`
  — north star, patient path, 7 agents, 3 experiences, BVA, guardrails.
* `docs/superpowers/ideas/curavias-product-webpage/curavias-bom/04-website-content-bom.md`
  — section-by-section content inventory.
* `docs/superpowers/ideas/curavias-product-webpage/curavias-site/` — reference HTML
  mockup (five pages).
* `agents/ux-design-agent/AGENT.md` — experience-lane anchor (RACI counterpart).
* `docs/superpowers/specs/2026-07-17-sprint-20-curavias-ux-design.md` — shell/theme
  baseline.
* `.github/copilot-instructions.md`, `AGENTS.md` — conventions, governance,
  MCP allow-list, naming.
