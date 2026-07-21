# Sprint 24 — Curavias Product-Marketing Agent + Astro Webpage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a `product-marketing-agent` that keeps Curavias copy on-brand and compliant across channels, and a brandkit-aligned Astro website (DE/EN/FR/IT) published to PROD on `curavias.ch` + `www.curavias.ch`.

**Architecture:** A control-plane agent pack under `agents/product-marketing-agent/` (github-mcp `write`, no new MCP server) plus an Astro static site at `apps/curavias-web/` ported from the `curavias-site` mockup, hosted on Azure Static Web Apps with a Storage media library, deployed via OIDC into a gated PROD environment, with `curavias.ch` records added to the existing Azure DNS zone (ADR-0030).

**Tech Stack:** Markdown/YAML (agent pack), Astro + TypeScript (site), Bicep (SWA + Storage + DNS records), GitHub Actions + OIDC/WIF (deploy), Playwright + axe (a11y, via ux-design-agent).

**Design spec:** `docs/superpowers/specs/2026-07-21-sprint-24-curavias-product-marketing-and-webpage-design.md`

**Phasing:** Each phase maps to a Sprint 24 child issue and is independently shippable as its own PR for human review. PROD infra apply + custom-domain binding are gated on an `approved-to-apply` comment (AGENTS.md §4). PR merges are human-only.

---

## File structure

| Path | Responsibility |
| ---- | -------------- |
| `agents/product-marketing-agent/AGENT.md` | Agent prompt (Identity/Scope/Tools/Grounding/Refusal/Output/Confirmation/Golden) |
| `agents/product-marketing-agent/manifest.yaml` | Runtime manifest (runtime, tools, ceiling, grounding) |
| `agents/product-marketing-agent/golden-tasks.md` | Happy-path + failure-mode fixtures |
| `AGENTS.md` | Add registry row (governance; CODEOWNERS) |
| `apps/curavias-web/` | Astro project root |
| `apps/curavias-web/astro.config.mjs` | Astro config incl. i18n (de/en/fr/it) |
| `apps/curavias-web/src/layouts/BaseLayout.astro` | Head, SEO/OpenGraph, disclaimer banner, footer |
| `apps/curavias-web/src/components/sections/*.astro` | One component per landing section |
| `apps/curavias-web/src/pages/**` | index, agents, architecture, ontology-explorer, product-build (per locale) |
| `apps/curavias-web/src/i18n/*.ts` | Per-locale copy dictionaries |
| `apps/curavias-web/src/styles/brand.css` | Brandkit tokens (white bg) |
| `infra/modules/experience-hosting/curavias-web.bicep` | SWA + Storage media library |
| `infra/modules/dns/curavias.bicep` | Extend with SWA custom-domain records (existing) |
| `.github/workflows/curavias-web-deploy.yml` | Build Astro → deploy SWA (OIDC) + media sync |
| `docs/PRD.md` | New `FR-MKT-*` / `FR-WEB-*` + traceability |

---

## Phase 1 — product-marketing-agent (issue #262)

**Files:**
- Create: `agents/product-marketing-agent/AGENT.md`
- Create: `agents/product-marketing-agent/manifest.yaml`
- Create: `agents/product-marketing-agent/golden-tasks.md`
- Modify: `AGENTS.md` (add registry row + version bump)

### Task 1.1: Author the agent pack

- [ ] **Step 1: Create `AGENT.md`** following the fixed structure (Identity · Scope · Tools · Grounding · Refusal Rules · Output Contract · Confirmation Rules · Golden Tasks), per spec §4. Tools: `github-mcp` (write), optional `playwright-mcp` (read). Include the five refusal codes from spec §4.5 and the RACI table from spec §9. Version header 1.0.0, Status Draft, approvalIssue 262.

- [ ] **Step 2: Create `manifest.yaml`** mirroring `agents/ux-design-agent/manifest.yaml` shape:

```yaml
agent: product-marketing-agent
version: 1.0.0
runtime: copilot-coding-agent
invocation: issue-triggered            # @product-marketing-agent mention or any product-messaging issue
approvalIssue: 262
systemPromptRef: ./AGENT.md
refusalRulesRef: ./AGENT.md#5-refusal-rules
skillRef: brainstorming                # + writing-plans (handoff), elements-of-style writing skills
localTools:
  - markdownlint-cli2
mcpTools:
  - server: github-mcp
    tools: [get-issue, add-issue-comment, create-branch, create-or-update-file, create-pull-request]
    ceiling: write
  - server: playwright-mcp
    tools: [browser_navigate, browser_snapshot, browser_take_screenshot]
    ceiling: read
hitl:
  gates: []
grounding:
  - source: docs/brandkit
    scope: curavias-brand-voice-and-tokens
  - source: docs/superpowers/ideas/curavias-product-webpage/curavias-bom/curavias-context.md
    scope: north-star-tagline-guardrails
  - source: docs/PRD.md
    scope: fr-mkt-fr-web
goldenTasksRef: ./golden-tasks.md
```

- [ ] **Step 3: Create `golden-tasks.md`** with the four fixtures from spec §4.7 (1 happy-path, 3 failure-modes), each with front-matter `requirement:` key, `Input issue body`, `Expected output shape`, `Forbidden behaviors`. Mirror `agents/ux-design-agent/golden-tasks.md` structure.

- [ ] **Step 4: Add the `AGENTS.md` registry row** after the `ux-design-agent` row:

```markdown
| `product-marketing-agent` | Product-marketing / communications steward — stringent, brand-aligned Curavias messaging across customer-, user-, and devops-facing channels; RACI-paired with `ux-design-agent` (message vs. experience) (S24; approved via issue #262) | @urruegg | `@product-marketing-agent` mention or any product-messaging / copy / positioning issue | `github-mcp`, `playwright-mcp` (read; copy-in-context review) | `write` | [`agents/product-marketing-agent/AGENT.md`](agents/product-marketing-agent/AGENT.md) | [`agents/product-marketing-agent/golden-tasks.md`](agents/product-marketing-agent/golden-tasks.md) |
```

Bump `AGENTS.md` Version MINOR (2.6.0 → 2.7.0), update Previous Version line. No `mcp.json` change (both servers already allow-listed).

- [ ] **Step 5: Add the RACI cross-reference** to `agents/ux-design-agent/AGENT.md` (a short note + link to the product-marketing-agent as the message-owning counterpart). Bump ux-design-agent AGENT.md PATCH/MINOR.

- [ ] **Step 6: Lint** — `python scripts/lint/check_mojibake.py <files>` and `npx --yes markdownlint-cli2 <files>`; expect 0 errors.

- [ ] **Step 7: Commit** on a feature branch `feat/sprint-24-product-marketing-agent`:

```bash
git commit -m "feat(agents): add product-marketing-agent for cross-channel Curavias messaging"
```

- [ ] **Step 8: Open a draft PR** referencing issue #262 with the PR Output Contract (lanes: platform control / experience; FR-MKT-*; no infra/security impact; CODEOWNERS review required). Do not merge.

**Acceptance:** pack files present; `AGENTS.md` row + version bump; RACI documented in both agent files; lint green; draft PR open on #262.

---

## Phase 2 — Astro scaffold + page port (issue #263)

**Files:** `apps/curavias-web/**` (new Astro project).

### Task 2.1: Scaffold the Astro project

- [ ] **Step 1: Scaffold** (empty template, TypeScript, no sample content):

```bash
cd apps
npm create astro@latest curavias-web -- --template minimal --typescript strict --no-install --no-git --skip-houston
```

- [ ] **Step 2: Configure i18n + static output** in `apps/curavias-web/astro.config.mjs`:

```js
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://curavias.ch',
  output: 'static',
  i18n: {
    defaultLocale: 'de',
    locales: ['de', 'en', 'fr', 'it'],
    routing: { prefixDefaultLocale: false },
  },
});
```

- [ ] **Step 3: Add brand tokens** at `apps/curavias-web/src/styles/brand.css` — import/copy the CSS variables from `docs/brandkit` (green `#17B890`, blue `#365B7D`, ink `#2E4C68`, white background). Keep the accessibility rule (dark text on green).

- [ ] **Step 4: Build sanity check** — `cd apps/curavias-web; npm install; npm run build`; expect success (empty site).

- [ ] **Step 5: Commit** on branch `feat/sprint-24-curavias-web`.

### Task 2.2: BaseLayout + disclaimer

- [ ] **Step 1: Create `src/layouts/BaseLayout.astro`** with `<head>` (title/meta/OpenGraph/hreflang props), the mandatory showcase-disclaimer banner (from `curavias-context.md` §1), skip-link, header, `<slot/>`, and footer (from mockup S13). Props: `title`, `description`, `lang`, `ogImage`.

- [ ] **Step 2: Verify** the disclaimer renders on a temporary index page; `npm run build` passes.

- [ ] **Step 3: Commit.**

### Task 2.3: Port sections (index page)

- [ ] For each of the 13 index sections (Hero, Disclaimer, KPIs, HumanDecides, CioChallenger, PatientPath, SevenAgents, ThreeExperiences, Security, BusinessValue, Reviews, Cta, Footer), create `src/components/sections/<Name>.astro` by transforming the corresponding markup from `docs/superpowers/ideas/curavias-product-webpage/curavias-site/index.html` — replace inline `<style>` with brand.css classes, keep inline SVG, replace `<img src="data:...">` with media-library URLs (env base) or in-repo SVG. Text pulled from the i18n dictionary (Task 3).
- [ ] Compose them in `src/pages/index.astro` via `BaseLayout`.
- [ ] `npm run build`; visually verify with `npm run preview`.
- [ ] Commit per logical group (e.g. hero+kpis, patient-path, agents, security+bva, reviews+cta).

### Task 2.4: Port remaining pages

- [ ] Repeat Task 2.3 transformation for `agents.html`, `architecture.html`, `ontology-explorer.html`, `product-build.html` → `src/pages/{agents,architecture,ontology-explorer,product-build}.astro`, reusing shared section components where content overlaps.
- [ ] `npm run build` (all pages); commit.

- [ ] **Open draft PR** referencing #263. Do not merge.

**Acceptance:** all five pages build; disclaimer on every page; brand tokens applied (white bg); no `data:` image blobs left inline (moved to media refs/SVG); draft PR open.

---

## Phase 3 — i18n copy (DE/EN/FR/IT) (issue #264)

**Files:** `apps/curavias-web/src/i18n/{de,en,fr,it}.ts`, section components consume keys.

- [ ] **Task 3.1:** Extract all DE copy from the ported pages into `src/i18n/de.ts` as a typed dictionary (keys per section/field). Refactor components to read from the active locale dictionary.
- [ ] **Task 3.2:** Generate `en.ts`, `fr.ts`, `it.ts` via the `product-marketing-agent` process (brand voice, advisory verbs, disclaimer translated, KPI/BVA caveats preserved). Each key mirrors `de.ts`.
- [ ] **Task 3.3:** Add locale routing pages under `src/pages/{en,fr,it}/**` (or `[locale]` dynamic) so `/en`, `/fr`, `/it` render translated content; add `hreflang` alternates + per-locale meta.
- [ ] **Task 3.4:** `npm run build` (4 locales x 5 pages); broken-link check; commit; draft PR on #264.

**Acceptance:** four locales build; disclaimer present per locale; advisory voice preserved; hreflang set. Native review flagged before launch (risk R3).

---

## Phase 4 — Infra Bicep: SWA + Storage media (issue #265)

**Files:** `infra/modules/experience-hosting/curavias-web.bicep` (new), wired from `infra/main.bicep`; `infra/environments/prod.bicepparam` (params).

- [ ] **Task 4.1:** Create `curavias-web.bicep`:
  - `Microsoft.Web/staticSites@2023-12-01` named `stapp-ihzhhpf-prod` (SKU `Standard`), tags `{env:'prod',owner,costCenter,workload:'curavias-web'}`, output `defaultHostname` + `id`.
  - `Microsoft.Storage/storageAccounts@2023-05-01` named `stmediaihzhhpfprod` (StorageV2, Standard_LRS, `allowBlobPublicAccess` per policy), blob service + container `media` (public read or fronted by CDN), output blob endpoint.
- [ ] **Task 4.2:** Reference the module from `infra/main.bicep` guarded to the prod env; add params to `infra/environments/prod.bicepparam`.
- [ ] **Task 4.3:** `az bicep build --file infra/main.bicep`; expect clean. Run `what-if` against the PROD RG (read-only). Attach output to PR.
- [ ] **Task 4.4:** Commit; draft PR on #265 with Infra impact + `what-if` summary. **Apply is gated** on `approved-to-apply`.

**Acceptance:** bicep builds; `what-if` clean; naming/tags per §8; PR states impact; no apply without approval.

---

## Phase 5 — Deploy workflow + custom domains (issue #266)

**Files:** `.github/workflows/curavias-web-deploy.yml`; extend `infra/modules/dns/curavias.bicep` with SWA records.

- [ ] **Task 5.1:** Author `curavias-web-deploy.yml` modelled on `cd-infra-deploy-prod.yml` / `ci-build-app-fluent.yml`:
  - Triggers: `workflow_dispatch` + push to `apps/curavias-web/**` on main.
  - `permissions: { id-token: write, contents: read }`; `environment: prod` (gated).
  - Steps: checkout → setup-node 20 → `npm ci` + `npm run build` in `apps/curavias-web` → `azure/login@v2` (OIDC) → deploy to SWA (`Azure/static-web-apps-deploy` or `az staticwebapp` with deployment token from federated login) → `az storage blob upload-batch` media sync.
- [ ] **Task 5.2:** Extend `dns/curavias.bicep` to add: `www` CNAME → SWA `defaultHostname`; apex `curavias.ch` handling per SWA apex guidance (TXT validation record + ALIAS/A). Follow the module note: accept an `existing` zone reference when the zone stays owned by SIT RG.
- [ ] **Task 5.3:** Bind custom domains `curavias.ch` + `www.curavias.ch` to the SWA (via Bicep `staticSites/customDomains` or `az staticwebapp hostname`); managed TLS.
- [ ] **Task 5.4:** `az bicep build`; `what-if` for DNS records; commit; draft PR on #266. **Apply/deploy gated** on `approved-to-apply`.

**Acceptance:** workflow validates (actionlint/CI); DNS records + custom-domain binding defined; OIDC only, no secrets; gated PROD env; PR states security + infra impact.

---

## Phase 6 — Media library upload (issue #267)

- [ ] **Task 6.1:** Inventory required assets from `04-website-content-bom.md` §4.2/§4.3; place generated SVG/diagrams in-repo, raster/photo assets in the media library.
- [ ] **Task 6.2:** Upload current (placeholder + generated) assets to `stmediaihzhhpfprod/media` via the workflow media-sync step; record the public base URL as a build-time env for the site.
- [ ] **Task 6.3:** Track Brand Central marks/stock as a pending sign-in task (placeholders until approved). Commit any in-repo SVG; draft PR on #267.

**Acceptance:** site references media base URL; in-repo SVG committed; Brand Central items tracked; no unlicensed marks shipped.

---

## Phase 7 — Legal + DNS tracking (issue #268)

- [ ] **Task 7.1:** DNS control confirmed (Azure DNS zone, ADR-0030) — mark R2 resolved (done via issue comment).
- [ ] **Task 7.2:** Keep trademark (CH/EU) + Swiss-cross legal review as an open tracked task; must close before formal announcement (accepted residual risk for public go-live). Record status in the issue and risk register.

**Acceptance:** #268 reflects DNS resolved + legal open; no unresolved blocker for go-live per the accepted-risk decision.

---

## PRD traceability (cross-phase)

- [ ] Add `FR-MKT-001..00n` (message consistency, advisory voice, disclaimer enforcement) and `FR-WEB-001..00n` (public multilingual site, PROD hosting, WCAG AA, SEO) to `docs/PRD.md`; update the §7 traceability matrix; reference the IDs in each phase PR. Bump `docs/PRD.md` MINOR.

---

## Self-review notes

- **Spec coverage:** Phases 1–7 map 1:1 to spec §4–§10 and issues #262–#268; PRD traceability task covers spec §16.
- **No new MCP server:** both `github-mcp` and `playwright-mcp` are already allow-listed (AGENTS.md §2), so no `mcp.json` change/CODEOWNERS-for-allow-list needed — only the `AGENTS.md` row (still CODEOWNERS-reviewed).
- **Naming consistency:** `stapp-ihzhhpf-prod`, `stmediaihzhhpfprod` used identically in spec §6, Phase 4, Phase 5.
- **Gates:** every `deploy`/apply task (Phases 4–5) explicitly requires `approved-to-apply`; PR merges human-only.
