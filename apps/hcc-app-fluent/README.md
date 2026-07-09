# hcc-app-fluent — Fluent UI baseline app

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-09 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | — (initial, Sprint 13) |

Sprint 13 primary track: the **deployable baseline** app for the Swiss Hospital
Capacity Platform — React 18 + Fluent UI v9 + Helvion brand tokens + MSAL against
the Sprint 12 `ihzhhpf-app` registration. It renders a two-workspace shell (Main +
Backstage), the BedManager operational whiteboard (6 card types), the Backstage
Roles & RBAC tab, and a Copilot Drawer that invokes the Sprint 11 `bmca-agent`
through the `hcc-agent-host` backend.

See the design spec:
[`docs/superpowers/specs/2026-07-09-sprint-13-app-design.md`](../../docs/superpowers/specs/2026-07-09-sprint-13-app-design.md).

## Stack

- Vite 6 + React 18 + TypeScript (strict)
- Fluent UI v9 (`@fluentui/react-components`), theme derived from
  [`helvion-token-mapping.md`](../../data-platform/reports/capacity-dashboard.Report/themes/helvion-token-mapping.md)
- MSAL for React (`@azure/msal-react`) — claims `roles` / `hospital` / `env`
- `@microsoft/microsoft-graph-client` — read-only Entra app-role list
- i18next — DE default, EN fallback
- Vitest (unit) + Playwright (E2E smoke + axe-core a11y)

## Scripts

```bash
npm install
npm run dev          # local dev server (http://localhost:5173)
npm run build        # tsc -b && vite build → dist/
npm run test         # vitest unit tests
npm run test:e2e     # Playwright smoke (builds + previews first)
npm run test:a11y    # axe-core accessibility scan
npm run lint         # tsc --noEmit
```

## Environment variables

Provide these at build/deploy time (never hard-code — copilot-instructions §3):

| Var | Purpose |
|-----|---------|
| `VITE_MSAL_CLIENT_ID` | `ihzhhpf-app` application (client) id (Sprint 12 T1) |
| `VITE_MSAL_TENANT_ID` | `MngEnvMCAP164444` tenant id (ADR-0012) |
| `VITE_MSAL_REDIRECT_URI` | SPA redirect URI for the current slot |
| `VITE_AGENT_HOST_URL` | Base URL of `hcc-agent-host` (Copilot Drawer target) |

When `VITE_AGENT_HOST_URL` / MSAL vars are absent (CI, local demo), the app runs
as an anonymous **demo.guest** shell (aggregated-only data, deterministic grounded
mock in the Copilot Drawer) so it builds and demonstrates the wiring end-to-end
without a live backend.

## Component boundaries (design spec §3)

- `shell/` — top bar, app rail, workspace router (knows nothing about agents).
- `auth/` — single source of `roles` / `hospital` / `env` claims.
- `context/` — hospital + role context providers.
- `whiteboard/` — pure canvas; cards plug in via `CardRegistry`.
- `cards/` — the 6 card types.
- `copilot-drawer/` — agent-agnostic drawer; per-agent config via manifest.
- `theme/` — Fluent v9 theme from Helvion tokens.
- `i18n/` — DE/EN resources.

## Deployment

Container image via [`Dockerfile`](./Dockerfile) → Azure Container Apps SIT slot.
Provisioning Bicep lives in `infra/modules/agent-host/` (shared env) and is a
`deploy`-ceiling action gated by `approved-to-apply` (AGENTS.md §4).
