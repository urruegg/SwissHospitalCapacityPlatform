# Runbook — Curavias UX Local Visual-Verify Loop

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-24 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (new document) |
| **Sprint** | 27 — Curavias App UX Polish (tracker #365) |
| **Applies to** | `apps/hcc-app-fluent` (internal app, app.curavias.ch) |

> Purpose: run the internal Curavias app locally against SIT, open it in a VS Code
> browser tab whose context is shared with GitHub Copilot, and iterate on each screen
> with an *edit → hot-reload → re-snapshot → accessibility-scan → attach evidence* cycle.
> This is the enabler (Sprint 27 M0) every screen-polish milestone depends on. Realises
> `FR-UX-004`.

---

## 1. Prerequisites

- Node.js (repo baseline) and npm.
- This worktree checked out on `sprint-27/curavias-ux-polish`.
- VS Code with GitHub Copilot; the Playwright MCP server wired in
  [`.vscode/mcp.json`](../../.vscode/mcp.json).
- Dependencies installed once: `npm --prefix apps/hcc-app-fluent install`.

## 2. Environment (SIT vs offline)

Provide these at run time (never hard-code — copilot-instructions §3). With them set, the
local app talks to **SIT**; without them it degrades to the anonymous `demo.guest` shell
(aggregated-only data, deterministic grounded mock) so the loop still runs offline and in CI.

| Var | Purpose |
|-----|---------|
| `VITE_MSAL_CLIENT_ID` | `ihzhhpf-app` application (client) id |
| `VITE_MSAL_TENANT_ID` | `MngEnvMCAP164444` tenant id (ADR-0012) |
| `VITE_MSAL_REDIRECT_URI` | SPA redirect URI for the local slot (e.g. `http://localhost:5173`) |
| `VITE_AGENT_HOST_URL` | Base URL of the SIT `hcc-agent-host` (Copilot drawer target) |

## 3. Start the app locally

```powershell
Set-Location "C:\Users\urruegg\source\urruegg\wt\sprint-27-curavias-ux-polish"
npm --prefix apps/hcc-app-fluent run dev
```

The app serves at `http://localhost:5173` (Vite, hot-reload enabled).

## 4. Two Playwright modes (both read-only)

Both modes only inspect and capture — they never mutate repo or cloud state.

### 4a. Standalone (local CLI)

The repo's Playwright config is at
[`apps/hcc-app-fluent/playwright.config.ts`](../../apps/hcc-app-fluent/playwright.config.ts).

```powershell
npm --prefix apps/hcc-app-fluent run test:e2e    # smoke (builds + previews first)
npm --prefix apps/hcc-app-fluent run test:a11y   # axe-core WCAG 2.1 AA scan
```

### 4b. Within VS Code, sharing context with GitHub Copilot

Open the running app (`http://localhost:5173`) in a VS Code browser tab. The
`playwright-mcp` server from [`.vscode/mcp.json`](../../.vscode/mcp.json) shares that live
browser context with Copilot, so you and Copilot inspect the same DOM. Copilot can then
`browser_navigate`, `browser_snapshot`, `browser_take_screenshot`, `browser_resize`, and read
`browser_console_messages`. This is the mode described in
[`agents/ux-design-agent/AGENT.md` §3](../../agents/ux-design-agent/AGENT.md).

## 5. The per-screen cycle

1. **Capture before** — screenshot the screen in light + dark and at desktop (≥ 1280) and
   narrow (≈ 768) widths.
2. **Refactor** — edit the screen to consume `src/theme/design-system` tokens + recipes.
3. **Verify** — Vite hot-reloads; re-snapshot in the shared browser; check spacing (8 pt
   grid), elevation, hover/pressed/focus, empty/loading/error states, dark-mode parity.
4. **Scan** — run `npm --prefix apps/hcc-app-fluent run test:a11y`; fix any axe violation.
5. **Attach evidence** — add the before/after screenshots to the screen's pull request.

## 6. Command reference

```powershell
npm --prefix apps/hcc-app-fluent run dev        # local dev server (localhost:5173)
npm --prefix apps/hcc-app-fluent run test       # Vitest unit tests
npm --prefix apps/hcc-app-fluent run test:e2e   # Playwright smoke
npm --prefix apps/hcc-app-fluent run test:a11y  # axe-core accessibility scan
npm --prefix apps/hcc-app-fluent run lint       # tsc --noEmit
npm --prefix apps/hcc-app-fluent run build      # production build
```

## 7. Guardrails

- Read-oriented only: browser automation inspects and captures; it never mutates repo or
  cloud state.
- No PHI or real patient data — the showcase is synthetic/generic only (ADR-0016).
- No secrets in source: SIT credentials come from environment/MSAL, never committed.
- Experience-lane only: polish changes styling; it does not change data, agent, or infra behaviour.
