# Sprint A - MSAL member sign-in + role-based E2E (design)

| Field | Value |
| ------- | ------- |
| **Version** | 1.0.0 |
| **Date** | 2026-08-02 |
| **Author** | Urs Rueegg |
| **Status** | Approved (design); pending implementation plan |
| **Previous Version** | - (new) |

> Brainstormed 2026-08-02 (Superpowers `brainstorming`). Reference pattern:
> `ATCSimulator` (`src/web/atcsim-shell/src/auth/*`). Deferred tracks captured in
> [../ideas/2026-08-02-signin-followups-b2b-guest-and-obo-rls.md](../ideas/2026-08-02-signin-followups-b2b-guest-and-obo-rls.md)
> and issues #559 (guest onboarding) + #560 (per-user OBO/RLS).

## 1. Goal

A tenant **member** (`admin@mngenvmcap164444.onmicrosoft.com` /
`urruegg@MngEnvMCAP164444.onmicrosoft.com`) signs into the SIT Curavias app; the
app reads their `HCC.*` role claim; the **role lens** adapts what they see and
can do; the operational loop (worklist -> accept/deny -> evidence) runs under
**their oid** against the agent-host's current golden data; a **My Account** view
shows who they are and which roles they hold; and sign-out returns to the
read-only Demo Guest.

## 2. Non-goals (deferred)

- **B2B guest onboarding** from another tenant - issue #559.
- **Full per-user OBO/RLS** on real Fabric golden rows (`#424 M5`) - issue #560.
  Sprint A runs on the agent-host's existing simulated-provenance golden data.

## 3. Current state (what already exists)

Sign-in is ~90% built and only needs runtime config + Entra + a role view:

- [msal-provider.ts](../../../apps/hcc-app-fluent/src/auth/msal-provider.ts) - MSAL config + `PublicClientApplication`.
- [auth-session.tsx](../../../apps/hcc-app-fluent/src/auth/auth-session.tsx) - `AuthSession` facade with `signIn`/`signOut` and the `configured = Boolean(clientId)` demo-gate.
- [claim-parser.ts](../../../apps/hcc-app-fluent/src/auth/claim-parser.ts) - parses `roles`/`hospital`/`env`/`name`/`oid`.
- [rbac-model.ts](../../../apps/hcc-app-fluent/src/auth/rbac-model.ts) - 19 `HCC.*` roles -> capability tiers (scope, ceiling, nav).
- [UserMenu.tsx](../../../apps/hcc-app-fluent/src/shell/TopBar/UserMenu.tsx) - shows "Sign-in not configured (demo)" today.

**Why SIT shows demo:** `msal-provider.ts` reads `import.meta.env.VITE_MSAL_CLIENT_ID` at **build time**, but the env-agnostic image (#447) was built without it and the SIT runtime `env-config.js` does not carry MSAL config, so `clientId=''` -> `configured=false`.

## 4. Design - five changes

### 4.1 Runtime MSAL config
Make [msal-provider.ts](../../../apps/hcc-app-fluent/src/auth/msal-provider.ts) resolve `clientId` / `tenantId` / `redirectUri` / `apiScope` from `window.__ENV__` first, then build-time `VITE_*`, then empty - mirroring the precedence in [runtime-config.ts](../../../apps/hcc-app-fluent/src/config/runtime-config.ts). Add `getMsalClientId()` etc. helpers there so one env-agnostic image is configured per environment. No build-time bake.

### 4.2 Runtime env injection
[docker-entrypoint.d/30-env-config.sh](../../../apps/hcc-app-fluent/docker-entrypoint.d/30-env-config.sh) writes `MSAL_CLIENT_ID`, `MSAL_TENANT_ID`, `MSAL_REDIRECT_URI`, `MSAL_API_SCOPE` into `env-config.js` from the Container App env; the SIT `ca-app-fluent` env vars are set in `infra/environments/sit.bicepparam` (+ the app-fluent module). Values: clientId `52681a08-c792-44b1-b6b5-01cb560d450f`, tenant `1337187a-4c41-4da9-8fca-731bba7a4329`, redirect `https://appsit.curavias.ch`.

### 4.3 Entra `ihzhhpf-app`
Confirm/add the **SPA redirect** `https://appsit.curavias.ch` on the `ihzhhpf-app` registration (appId `52681a08-...`). App roles already exist (17 `HCC.*`, verified). `appRoleAssignmentRequired=True`, so only assigned users sign in and the `roles` claim is emitted.

### 4.4 Signed-in golden read
Verify the agent-host's **simulated** golden provider serves data for a signed-in member (app sends `X-User-Oid` + `X-Hospital-Scope`) rather than the anonymous 401. If it still refuses, make the signed-in read succeed for a valid member scope. The new `/worklist`, `/decisions`, `/evidence` endpoints already work without an oid. **Companion fix:** the Live boards should degrade gracefully (fixture shell + the `GroundingNotice`) instead of hanging on "Wird geladen..." when a golden read fails - so a demo guest is never stuck.

### 4.5 My Account view
A panel/dialog opened from `UserMenu` showing: display name, UPN/email, oid, **assigned roles**, active role + derived hospital/env scope + agent ceiling, tenant, and Sign out. Reuses `claim-parser` + `rbac-model`; no new data source.

## 5. Role assignment (done 2026-08-02)

Both members hold **`HCC.PlatformAdmin`** (aggregated, all nav) and **`HCC.DischargeCoordinator`** (own-site, main-only, write) on `ihzhhpf-app (sit)` (SP `667b8c54-...`), so the demo can show breadth (PlatformAdmin) and the "narrow-only" role switch to a scoped operational role (DischargeCoordinator).

## 6. Data flow

sign in (`loginRedirect`) -> ID token with `roles` (`HCC.PlatformAdmin`, `HCC.DischargeCoordinator`) + `oid` -> `claim-parser` -> `rbac-model` capabilities -> role lens (nav + ceiling + scope) -> `ContextEnvelope` (`userOid` x `activeRole` x `hospitalScope`) -> agent-host calls carry `X-User-Oid` -> worklist/decisions/evidence + golden reads.

## 7. Testing & acceptance

Unit: runtime MSAL resolution (`window.__ENV__` precedence), `env-config.sh` emits the MSAL keys, account-view render from claims, Live-board graceful degrade. E2E/live: sign in as `admin@` -> lens = PlatformAdmin (all boards) -> switch to DischargeCoordinator (main only) -> discharge worklist loads live (3 barriers) -> Accept -> outcome + shrink under the user oid -> evidence board -> My Account shows both roles -> Sign out -> Demo Guest.

## 8. Rollout

SIT first: set the MSAL env vars + redirect, rebuild the app image, gated `cd-infra-deploy-sit`. PROD is a later, separately-approved step. No new Azure resources.

## 9. Risks

- **Signed-in golden 401** (section 4.4) - the one behavioural unknown; mitigated by the graceful-degrade companion fix so the loop (worklist/evidence, no oid) still works.
- Conditional Access could add MFA at sign-in (acceptable) - verified not a block.
- Redirect URI mismatch -> `AADSTS50011`; pinned to `https://appsit.curavias.ch`.

## 10. Proposed requirements (finalised in PRD during the plan)

`FR-AUTH-001` member sign-in/out; `FR-AUTH-002` role-lens from the `roles` claim; `FR-AUTH-003` My Account view of identity + roles; `NFR-AUTH-001` env-agnostic runtime config (no secrets baked); `NFR-AUTH-002` Live boards fail loud (degrade), never hang.
