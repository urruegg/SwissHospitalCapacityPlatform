# infra/modules/apps/hcc-app-fluent

Sprint 13 T1 — Container App for the Fluent baseline UI (`apps/hcc-app-fluent/`).

## What it deploys

- A dedicated Container Apps managed environment (`cae-app-fluent-<suffix>`) wired to the platform Log Analytics workspace.
- A Container App (`ca-app-fluent-<suffix>`) that serves the React/Vite static bundle behind `nginx-unprivileged` on port 8080.
- A system-assigned managed identity on the Container App so the app-shell can request tokens for MSAL OBO flows (Graph API for the Backstage Roles tab, agent-host `/chat` endpoint, etc.).
- (Optional) AcrPull role assignment when `containerRegistryLoginServer` + `containerRegistryResourceId` are set — enables MI-based image pull with no admin creds.

## Runtime configuration (#447)

The app image is **env-agnostic**: the Foundry agent-host URL is injected at
container start, not baked at build time. The module sets a per-env
`AGENT_HOST_URL` container environment variable from the `agentHostUrl` param
(wired from top-level `appFluentAgentHostUrl`, set in each `.bicepparam`). At
startup `apps/hcc-app-fluent/docker-entrypoint.d/30-env-config.sh` writes
`env-config.js` (`window.__ENV__.AGENT_HOST_URL`), which the app reads before its
build-time `VITE_AGENT_HOST_URL` fallback. This lets one image (built once and
`az acr import`-ed to the PROD ACR) serve SIT and PROD, each calling its own
region's agent-host — replacing the former build-once+import quirk where PROD
inherited the SIT agent-host URL.

## What it does NOT deploy

- **Not the built app image.** Defaults to `nginxinc/nginx-unprivileged:1.27-alpine` until `app-build.yml` is extended to push the real image to ACR (follow-up gap-fill).
- **Not the front-door / custom domain / TLS cert** — that's a separate integration lane concern.

## Deploy gate

`deploy` ceiling per AGENTS.md §3. Enable via `enableAppFluentModule = true` in the target environment's `.bicepparam` file. The apply must post an `az deployment group what-if` output as a PR comment and wait for `approved-to-apply` before running `az deployment group create`.

## Related

- Sister module: `../agent-host/` — Container Apps agent-host (backend for the Fluent app's Copilot Drawer).
- Parent: `../../../main.bicep` — the top-level template that instantiates this module.
- App source: `apps/hcc-app-fluent/`.
- App Dockerfile: `apps/hcc-app-fluent/Dockerfile` (multi-stage: node:20 build → nginx-unprivileged runtime).
