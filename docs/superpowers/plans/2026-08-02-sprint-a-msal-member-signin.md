# Sprint A — MSAL member sign-in Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A tenant **member** signs into the SIT Curavias app, the app reads their `HCC.*` role claim and adapts the role lens, the operational loop and golden boards run under their oid, a **My Account** view shows identity + roles, and sign-out returns to the read-only Demo Guest.

**Architecture:** The MSAL sign-in path is ~90% built (`msal-provider` → `AuthSession` → `claim-parser` → `rbac-model` → role lens → `ContextEnvelope`). Sprint A makes MSAL config **runtime-injected** (one env-agnostic image, per [runtime-config.ts](../../../apps/hcc-app-fluent/src/config/runtime-config.ts) `window.__ENV__` precedence), threads the values through Bicep, adds the Entra SPA redirect, makes the Live boards **degrade instead of hang** when a golden read is refused, and adds a **My Account** dialog. The agent-host is **unchanged** (its `/golden` endpoint already serves any non-empty oid when `OBO_ENABLED=false`).

**Tech Stack:** React 18 + Vite + Fluent UI v9, `@azure/msal-browser` / `@azure/msal-react`, Vitest, Bicep (Container Apps), nginx-unprivileged entrypoint shell, Microsoft Graph (app-registration redirect URI).

**Discovered during planning (both fold into the tasks below, faithful to the approved spec's acceptance flow):**

1. The role switcher is gated on `env === 'sit'` ([role-context.tsx](../../../apps/hcc-app-fluent/src/context/role-context.tsx) `canSwitchRole`). The `ihzhhpf-app` token is not guaranteed to emit `env`/`hospital` custom claims, so Sprint A injects `APP_ENV` + `APP_HOME_HOSPITAL` at runtime (same `window.__ENV__` mechanism, no Entra claims-mapping policy) and reads them as a fallback. This is what makes the spec's "switch to DischargeCoordinator" step visible.
2. Section 4.4 "make the signed-in read succeed" needs **no agent-host change**: `GET /golden/{resource}` refuses (401) only when `X-User-Oid` is empty (the anonymous Demo Guest). A signed-in member sends a real oid → 200. The only fix is the client-side graceful-degrade guard so the anonymous case never hangs on "Wird geladen…".

---

## File Structure

**Modify (app):**

- `apps/hcc-app-fluent/src/config/runtime-config.ts` — add MSAL/env getters + `RuntimeEnv` fields.
- `apps/hcc-app-fluent/src/auth/msal-provider.ts` — resolve config from the runtime getters.
- `apps/hcc-app-fluent/src/context/role-context.tsx` — runtime `env`/`homeSite` fallback.
- `apps/hcc-app-fluent/src/data/roleboard/golden-source-client.ts` — degrade-not-hang on live-read failure.
- `apps/hcc-app-fluent/src/auth/auth-session.tsx` — expose `username` (UPN).
- `apps/hcc-app-fluent/src/shell/TopBar/UserMenu.tsx` — add "My account" item + dialog state.

**Create (app):**

- `apps/hcc-app-fluent/src/shell/account/AccountDialog.tsx` — the My Account view.
- Test files colocated: `runtime-config.msal.test.ts`, `role-context.env-fallback.test.tsx`, `golden-source-client.degrade.test.ts`, `AccountDialog.test.tsx`.

**Modify (runtime + infra):**

- `apps/hcc-app-fluent/docker-entrypoint.d/30-env-config.sh` — emit the new keys.
- `infra/modules/apps/hcc-app-fluent/main.bicep` — new params + container env entries.
- `infra/main.bicep` — new top-level params wired to the module.
- `infra/environments/sit.bicepparam` — set the SIT values.

**Modify (docs):**

- `docs/PRD.md` — add `FR-AUTH-001/002/003`, `NFR-AUTH-001/002` + §7 traceability. MINOR bump.

**Operational (main session, gated):**

- Microsoft Graph — add SPA redirect `https://appsit.curavias.ch` to `ihzhhpf-app`.
- `ci-build-app-fluent.yml` (image build) + gated `cd-infra-deploy-sit` (deploy) + sign-in E2E.

---

## Task 1: Runtime MSAL config resolution

**Files:**

- Modify: `apps/hcc-app-fluent/src/config/runtime-config.ts`
- Modify: `apps/hcc-app-fluent/src/auth/msal-provider.ts`
- Test: `apps/hcc-app-fluent/src/config/runtime-config.msal.test.ts`

- [ ] **Step 1: Write the failing test**

```ts
// apps/hcc-app-fluent/src/config/runtime-config.msal.test.ts
import { afterEach, describe, expect, it } from 'vitest';
import { getMsalClientId, getMsalTenantId, getMsalRedirectUri, getAppEnv } from './runtime-config';

describe('runtime MSAL config resolution', () => {
  afterEach(() => {
    delete (window as unknown as { __ENV__?: unknown }).__ENV__;
  });

  it('prefers window.__ENV__ over build-time fallback', () => {
    (window as unknown as { __ENV__: Record<string, string> }).__ENV__ = {
      MSAL_CLIENT_ID: '52681a08-c792-44b1-b6b5-01cb560d450f',
      MSAL_TENANT_ID: '1337187a-4c41-4da9-8fca-731bba7a4329',
      MSAL_REDIRECT_URI: 'https://appsit.curavias.ch',
      APP_ENV: 'sit',
    };
    expect(getMsalClientId()).toBe('52681a08-c792-44b1-b6b5-01cb560d450f');
    expect(getMsalTenantId()).toBe('1337187a-4c41-4da9-8fca-731bba7a4329');
    expect(getMsalRedirectUri()).toBe('https://appsit.curavias.ch');
    expect(getAppEnv()).toBe('sit');
  });

  it('falls back to empty client id when nothing is configured (demo)', () => {
    expect(getMsalClientId()).toBe('');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/hcc-app-fluent; npx vitest run src/config/runtime-config.msal.test.ts`
Expected: FAIL — `getMsalClientId is not a function`.

- [ ] **Step 3: Add the fields + getters to `runtime-config.ts`**

In `RuntimeEnv` (after `AGENT_HOST_SCOPE?: string;`) add:

```ts
  /** Sprint A — MSAL application (client) id for this environment; empty = demo (no sign-in). */
  MSAL_CLIENT_ID?: string;
  /** Sprint A — MSAL tenant id (MngEnvMCAP164444, ADR-0012). */
  MSAL_TENANT_ID?: string;
  /** Sprint A — SPA redirect URI for this slot (e.g. https://appsit.curavias.ch). */
  MSAL_REDIRECT_URI?: string;
  /** Sprint A — deployment env (dev|sit|prod) used when the token omits the `env` claim. */
  APP_ENV?: string;
  /** Sprint A — home hospital (usz|luks|zollikerberg|aggregated) used when the token omits `hospital`. */
  APP_HOME_HOSPITAL?: string;
```

At the end of the file add:

```ts
/** Resolve the MSAL client id: runtime value first, then build-time `VITE_MSAL_CLIENT_ID`, then empty (=> demo, no sign-in). Sprint A. */
export function getMsalClientId(): string {
  const runtime = runtimeEnv().MSAL_CLIENT_ID;
  if (runtime && runtime.length > 0) {
    return runtime;
  }
  return import.meta.env.VITE_MSAL_CLIENT_ID ?? '';
}

/** Resolve the MSAL tenant id: runtime first, then `VITE_MSAL_TENANT_ID`, then `common`. Sprint A. */
export function getMsalTenantId(): string {
  const runtime = runtimeEnv().MSAL_TENANT_ID;
  if (runtime && runtime.length > 0) {
    return runtime;
  }
  return import.meta.env.VITE_MSAL_TENANT_ID ?? 'common';
}

/** Resolve the SPA redirect URI: runtime first, then `VITE_MSAL_REDIRECT_URI`, then the current origin. Sprint A. */
export function getMsalRedirectUri(): string {
  const runtime = runtimeEnv().MSAL_REDIRECT_URI;
  if (runtime && runtime.length > 0) {
    return runtime;
  }
  const fallback = import.meta.env.VITE_MSAL_REDIRECT_URI ?? '';
  if (fallback.length > 0) {
    return fallback;
  }
  return typeof window !== 'undefined' ? window.location.origin : '';
}

/** Resolve the deployment env used when the ID token omits the `env` claim: runtime `APP_ENV` first, then `VITE_APP_ENV`, then empty. Sprint A. */
export function getAppEnv(): string {
  const runtime = runtimeEnv().APP_ENV;
  if (runtime && runtime.length > 0) {
    return runtime;
  }
  return import.meta.env.VITE_APP_ENV ?? '';
}

/** Resolve the home hospital used when the ID token omits the `hospital` claim: runtime `APP_HOME_HOSPITAL` first, then `VITE_APP_HOME_HOSPITAL`, then empty. Sprint A. */
export function getHomeHospital(): string {
  const runtime = runtimeEnv().APP_HOME_HOSPITAL;
  if (runtime && runtime.length > 0) {
    return runtime;
  }
  return import.meta.env.VITE_APP_HOME_HOSPITAL ?? '';
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/hcc-app-fluent; npx vitest run src/config/runtime-config.msal.test.ts`
Expected: PASS (2 passed).

- [ ] **Step 5: Point `msal-provider.ts` at the runtime getters**

Replace the top of `apps/hcc-app-fluent/src/auth/msal-provider.ts`:

```ts
import { Configuration, PublicClientApplication } from '@azure/msal-browser';
import { getMsalClientId, getMsalTenantId, getMsalRedirectUri } from '../config/runtime-config';

/**
 * Sprint 13 T2 / Sprint A — MSAL v2 configuration for the `ihzhhpf-app`
 * registration. Config is resolved at runtime from `window.__ENV__` (injected by
 * docker-entrypoint.d/30-env-config.sh) first, then build-time `VITE_MSAL_*`, so a
 * single env-agnostic image (#447) is configured per environment with no bake.
 */
const clientId = getMsalClientId();
const tenantId = getMsalTenantId() || 'common';

export const msalConfig: Configuration = {
  auth: {
    clientId,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri: getMsalRedirectUri(),
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
};
```

Leave `loginRequest` and `msalInstance` unchanged.

- [ ] **Step 6: Run the app test suite to confirm no regressions**

Run: `cd apps/hcc-app-fluent; npm run test 2>&1 | Select-Object -Last 20`
Expected: full suite green (existing `auth`/`config` tests still pass; `configured=false` in jsdom because no `window.__ENV__`).

- [ ] **Step 7: Commit**

```bash
git add apps/hcc-app-fluent/src/config/runtime-config.ts apps/hcc-app-fluent/src/config/runtime-config.msal.test.ts apps/hcc-app-fluent/src/auth/msal-provider.ts
git commit -m "feat(auth): resolve MSAL config from window.__ENV__ at runtime (Sprint A)"
```

---

## Task 2: Runtime env injection (entrypoint script)

**Files:**

- Modify: `apps/hcc-app-fluent/docker-entrypoint.d/30-env-config.sh`

- [ ] **Step 1: Add the MSAL + app-env keys to the generated `env-config.js`**

Replace the body of `apps/hcc-app-fluent/docker-entrypoint.d/30-env-config.sh` from `agent_host_url=...` through the closing `echo`:

```sh
html_dir="${NGINX_HTML_DIR:-/usr/share/nginx/html}"
target="${html_dir}/env-config.js"
agent_host_url="${AGENT_HOST_URL:-}"
golden_source_url="${GOLDEN_SOURCE_URL:-}"
foundry_threads_enabled="${FOUNDRY_THREADS_ENABLED:-}"
msal_client_id="${MSAL_CLIENT_ID:-}"
msal_tenant_id="${MSAL_TENANT_ID:-}"
msal_redirect_uri="${MSAL_REDIRECT_URI:-}"
app_env="${APP_ENV:-}"
app_home_hospital="${APP_HOME_HOSPITAL:-}"

cat > "${target}" <<EOF
// Generated at container start by docker-entrypoint.d/30-env-config.sh (#447, #424 M2, #424 M3, Sprint A).
window.__ENV__ = Object.assign(window.__ENV__ || {}, {
  AGENT_HOST_URL: "${agent_host_url}",
  GOLDEN_SOURCE_URL: "${golden_source_url}",
  FOUNDRY_THREADS_ENABLED: "${foundry_threads_enabled}",
  MSAL_CLIENT_ID: "${msal_client_id}",
  MSAL_TENANT_ID: "${msal_tenant_id}",
  MSAL_REDIRECT_URI: "${msal_redirect_uri}",
  APP_ENV: "${app_env}",
  APP_HOME_HOSPITAL: "${app_home_hospital}"
});
EOF

echo "[30-env-config] wrote ${target} (AGENT_HOST_URL='${agent_host_url}', GOLDEN_SOURCE_URL='${golden_source_url}', FOUNDRY_THREADS_ENABLED='${foundry_threads_enabled}', MSAL_CLIENT_ID='${msal_client_id}', APP_ENV='${app_env}')"
```

- [ ] **Step 2: Verify the script emits the keys (run it with env vars, POSIX sh)**

Run (from repo root, Git Bash / WSL if available; otherwise this is validated in CI on the Linux runner):

```bash
MSAL_CLIENT_ID=52681a08-c792-44b1-b6b5-01cb560d450f APP_ENV=sit NGINX_HTML_DIR=/tmp/envcfg \
  sh apps/hcc-app-fluent/docker-entrypoint.d/30-env-config.sh && cat /tmp/envcfg/env-config.js
```

Expected: `env-config.js` contains `MSAL_CLIENT_ID: "52681a08-..."` and `APP_ENV: "sit"`.

> On Windows without a POSIX shell, skip local execution — the CI Linux runner and the real container start exercise this. The change is a trivial additive `cat` heredoc.

- [ ] **Step 3: Commit**

```bash
git add apps/hcc-app-fluent/docker-entrypoint.d/30-env-config.sh
git commit -m "feat(auth): inject MSAL + app-env into window.__ENV__ at container start (Sprint A)"
```

---

## Task 3: Bicep parameter threading

**Files:**

- Modify: `infra/modules/apps/hcc-app-fluent/main.bicep`
- Modify: `infra/main.bicep`
- Modify: `infra/environments/sit.bicepparam`

- [ ] **Step 1: Add module params (`infra/modules/apps/hcc-app-fluent/main.bicep`)**

After the `foundryThreadsEnabled` param declaration, add:

```bicep
@description('Sprint A — MSAL application (client) id injected into the app at container start (window.__ENV__.MSAL_CLIENT_ID). Empty = demo (no sign-in). The ihzhhpf-app registration id.')
param msalClientId string = ''

@description('Sprint A — MSAL tenant id (MngEnvMCAP164444, ADR-0012) injected as window.__ENV__.MSAL_TENANT_ID.')
param msalTenantId string = ''

@description('Sprint A — SPA redirect URI for this slot injected as window.__ENV__.MSAL_REDIRECT_URI (e.g. appsit.curavias.ch). Must match a SPA redirect on the ihzhhpf-app registration.')
param msalRedirectUri string = ''

@description('Sprint A — deployment env (dev|sit|prod) injected as window.__ENV__.APP_ENV; used by the role lens when the ID token omits the env claim (gates the SIT role switcher).')
param appEnv string = ''

@description('Sprint A — home hospital (usz|luks|zollikerberg|aggregated) injected as window.__ENV__.APP_HOME_HOSPITAL; used for own-site role scope when the ID token omits the hospital claim.')
param appHomeHospital string = ''
```

- [ ] **Step 2: Add the container env entries (same file, in the `env:` array)**

Inside the `env: [ ... ]` array (after the `FOUNDRY_THREADS_ENABLED` entry) add:

```bicep
            {
              // Sprint A — MSAL runtime config (env-agnostic image; no build-time bake).
              name: 'MSAL_CLIENT_ID'
              value: msalClientId
            }
            {
              name: 'MSAL_TENANT_ID'
              value: msalTenantId
            }
            {
              name: 'MSAL_REDIRECT_URI'
              value: msalRedirectUri
            }
            {
              name: 'APP_ENV'
              value: appEnv
            }
            {
              name: 'APP_HOME_HOSPITAL'
              value: appHomeHospital
            }
```

- [ ] **Step 3: Add top-level params + wiring (`infra/main.bicep`)**

After the `appFluentFoundryThreadsEnabled` param, add:

```bicep
@description('Sprint A — MSAL application (client) id for the hcc-app-fluent (window.__ENV__.MSAL_CLIENT_ID). Empty keeps the app in demo (no sign-in). Set to the ihzhhpf-app registration id in SIT.')
param appFluentMsalClientId string = ''

@description('Sprint A — MSAL tenant id (MngEnvMCAP164444, ADR-0012) for the hcc-app-fluent.')
param appFluentMsalTenantId string = ''

@description('Sprint A — SPA redirect URI for the hcc-app-fluent (appsit.curavias.ch in SIT). Must match a SPA redirect on the ihzhhpf-app registration.')
param appFluentMsalRedirectUri string = ''

@description('Sprint A — deployment env (dev|sit|prod) injected into the hcc-app-fluent for the role lens env fallback.')
param appFluentAppEnv string = ''

@description('Sprint A — home hospital for own-site role scope when the token omits the hospital claim.')
param appFluentHomeHospital string = ''
```

In the `module appFluent ... { params: { ... } }` block, add these to `params`:

```bicep
    msalClientId: appFluentMsalClientId
    msalTenantId: appFluentMsalTenantId
    msalRedirectUri: appFluentMsalRedirectUri
    appEnv: appFluentAppEnv
    appHomeHospital: appFluentHomeHospital
```

- [ ] **Step 4: Set the SIT values (`infra/environments/sit.bicepparam`)**

After the `appFluentFoundryThreadsEnabled` line, add:

```bicep
// Sprint A — member sign-in runtime config (ihzhhpf-app, MngEnvMCAP164444 tenant,
// ADR-0012). Env-agnostic image (#447): values are injected into window.__ENV__ at
// container start, never baked. appEnv=sit gates the in-session role switcher when
// the ID token omits the custom env claim. Deploy approval-gated per AGENTS.md §4.
param appFluentMsalClientId = '52681a08-c792-44b1-b6b5-01cb560d450f'
param appFluentMsalTenantId = '1337187a-4c41-4da9-8fca-731bba7a4329'
param appFluentMsalRedirectUri = 'https://appsit.curavias.ch'
param appFluentAppEnv = 'sit'
param appFluentHomeHospital = 'usz'
```

- [ ] **Step 5: Build the Bicep to verify it compiles**

Run: `az bicep build --file infra/main.bicep`
Expected: exits 0, `infra/main.json` regenerated with the new params/env (no errors; warnings acceptable if pre-existing).

- [ ] **Step 6: Commit**

```bash
git add infra/modules/apps/hcc-app-fluent/main.bicep infra/main.bicep infra/main.json infra/environments/sit.bicepparam
git commit -m "feat(infra): thread MSAL + app-env runtime config into ca-app-fluent (Sprint A)"
```

> Do NOT push infra yet — pushing `infra/**` triggers `cd-infra-deploy-sit`. Infra push + gated deploy happen together with the new image in Task 9.

---

## Task 4: Role-lens env / home-site runtime fallback

**Files:**

- Modify: `apps/hcc-app-fluent/src/context/role-context.tsx`
- Test: `apps/hcc-app-fluent/src/context/role-context.env-fallback.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
// apps/hcc-app-fluent/src/context/role-context.env-fallback.test.tsx
import { afterEach, describe, expect, it } from 'vitest';
import { canSwitchRole } from './role-context';
import { parseClaims } from '../auth/claim-parser';

describe('role lens env fallback (Sprint A)', () => {
  afterEach(() => {
    delete (window as unknown as { __ENV__?: unknown }).__ENV__;
  });

  it('enables the role switcher when APP_ENV=sit even if the token omits the env claim', () => {
    (window as unknown as { __ENV__: Record<string, string> }).__ENV__ = { APP_ENV: 'sit' };
    // Token with roles but no `env` claim -> parseClaims defaults env to 'dev'.
    const claims = parseClaims({ roles: ['HCC.PlatformAdmin'] });
    expect(claims.env).toBe('dev');
    expect(canSwitchRole(claims)).toBe(true);
  });

  it('keeps the switcher hidden without a PlatformAdmin/DemoOperator role', () => {
    (window as unknown as { __ENV__: Record<string, string> }).__ENV__ = { APP_ENV: 'sit' };
    const claims = parseClaims({ roles: ['HCC.DischargeCoordinator'] });
    expect(canSwitchRole(claims)).toBe(false);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/hcc-app-fluent; npx vitest run src/context/role-context.env-fallback.test.tsx`
Expected: FAIL — first case returns `false` (env resolves to `dev`).

- [ ] **Step 3: Add the runtime fallback in `role-context.tsx`**

Add the import near the top:

```ts
import { getAppEnv, getHomeHospital } from '../config/runtime-config';
```

Add a helper above `canSwitchRole`:

```ts
const HOSPITAL_SCOPES: readonly HospitalScope[] = ['usz', 'luks', 'zollikerberg', 'aggregated'];

/** Effective env: runtime APP_ENV wins over the (often-absent) token `env` claim. Sprint A. */
function effectiveEnv(claims: ParsedClaims): AppEnv {
  const runtime = getAppEnv().toLowerCase();
  if (runtime === 'dev' || runtime === 'sit' || runtime === 'prod') {
    return runtime;
  }
  return claims.env;
}
```

Change `canSwitchRole` to use it:

```ts
export function canSwitchRole(claims: ParsedClaims): boolean {
  return effectiveEnv(claims) === 'sit' && hasAnyRole(claims, ROLE_SWITCHER_ROLES);
}
```

In `RoleProvider`, set `value.env` from the effective env and add a runtime home-site fallback. Replace the `value` memo's `env` line and the `homeSite` derivation:

```ts
  const value = useMemo<RoleContextValue>(
    () => ({
      roles: effectiveClaims.roles,
      env: effectiveEnv(effectiveClaims),
      canSwitchRole: canSwitchRole(effectiveClaims),
      has: (roles: string[]) => hasAnyRole(effectiveClaims, roles),
    }),
    [effectiveClaims],
  );
```

```ts
  const runtimeHome = getHomeHospital().toLowerCase();
  const runtimeHomeSite = HOSPITAL_SCOPES.includes(runtimeHome as HospitalScope)
    ? (runtimeHome as HospitalScope)
    : undefined;
  const homeSite: HospitalScope =
    testHomeSite ?? runtimeHomeSite ?? (effectiveClaims.hospital as Hospital as HospitalScope);
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/hcc-app-fluent; npx vitest run src/context/role-context.env-fallback.test.tsx`
Expected: PASS (2 passed).

- [ ] **Step 5: Run the full suite (role-context is shared — confirm no regressions)**

Run: `cd apps/hcc-app-fluent; npm run test 2>&1 | Select-Object -Last 20`
Expected: green. Existing role-context tests pass because `getAppEnv()` returns `''` in jsdom (no `window.__ENV__`), so effective env == claim env.

- [ ] **Step 6: Commit**

```bash
git add apps/hcc-app-fluent/src/context/role-context.tsx apps/hcc-app-fluent/src/context/role-context.env-fallback.test.tsx
git commit -m "feat(auth): runtime env/home-site fallback for the SIT role switcher (Sprint A)"
```

---

## Task 5: Live boards degrade instead of hang

**Files:**

- Modify: `apps/hcc-app-fluent/src/data/roleboard/golden-source-client.ts`
- Test: `apps/hcc-app-fluent/src/data/roleboard/golden-source-client.degrade.test.ts`

- [ ] **Step 1: Write the failing test**

```ts
// apps/hcc-app-fluent/src/data/roleboard/golden-source-client.degrade.test.ts
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { loadOccupancy, setContextEnvelope } from './golden-source-client';
import { setPreferredSource } from '../data-source';

describe('live golden read degrades instead of hanging (Sprint A, NFR-AUTH-002)', () => {
  beforeEach(() => {
    (window as unknown as { __ENV__: Record<string, string> }).__ENV__ = {
      GOLDEN_SOURCE_URL: 'https://agent-host.example/golden',
    };
    setPreferredSource('live');
    // Anonymous-style envelope with an empty oid -> the server would 401.
    setContextEnvelope({ userOid: '', hospitalScope: 'aggregated', activeRole: 'HCC.GuestReadOnly' } as never);
  });
  afterEach(() => {
    vi.restoreAllMocks();
    setPreferredSource('simulated');
    setContextEnvelope(null);
    delete (window as unknown as { __ENV__?: unknown }).__ENV__;
  });

  it('returns the fixture flagged degraded (does not throw) when the read is refused 401', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 401 }));
    const data = await loadOccupancy({ hospital: 'aggregated', windowHours: 72 } as never, 'live' as never);
    expect(data.degraded).toBe(true);
    expect(data.provenance).toBe('simulated');
    expect(data.payload).toBeTruthy();
  });
});
```

> Confirm the exact export names for the data-source setter (`setPreferredSource`) and the `ScenarioScope`/`Mode` shapes in [data-source.ts](../../../apps/hcc-app-fluent/src/data/data-source.ts) and [RoleBoard](../../../apps/hcc-app-fluent/src/journey/RoleBoard.tsx). If the test-only source setter differs, use the provider's actual API; the assertion (degraded fixture, no throw) is what matters.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/hcc-app-fluent; npx vitest run src/data/roleboard/golden-source-client.degrade.test.ts`
Expected: FAIL — the call throws `occupancy load failed: 401` instead of returning a degraded result.

- [ ] **Step 3: Wrap the live branch in try/catch in `loadBoard`**

In `apps/hcc-app-fluent/src/data/roleboard/golden-source-client.ts`, replace the live-read tail of `loadBoard`:

```ts
  // Live + configured -> OBO/RLS gateway (iqFetch refuses without a ContextEnvelope).
  try {
    const res = await iqFetch(
      `${goldenUrl()}/${resource}?hospital=${encodeURIComponent(scope.hospital)}&window=${scope.windowHours}`,
    );
    if (!res.ok) throw new Error(`${resource} load failed: ${res.status}`);
    const payload = (await res.json()) as P;
    return { provenance: 'live', scope: pinnedScope, payload, citations: cites, degraded: false };
  } catch {
    // Fail loud but never hang (NFR-AUTH-002): fall back to the fixture flagged
    // `degraded` so the GroundingNotice shows the live read was refused/unavailable
    // (e.g. anonymous Demo Guest = empty oid -> 401), instead of stalling the board.
    return { provenance: 'simulated', scope: pinnedScope, payload: fixture, citations: cites, degraded: true };
  }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/hcc-app-fluent; npx vitest run src/data/roleboard/golden-source-client.degrade.test.ts`
Expected: PASS (1 passed).

- [ ] **Step 5: Run the full suite (confirm the happy-path live test still returns `live`)**

Run: `cd apps/hcc-app-fluent; npm run test 2>&1 | Select-Object -Last 20`
Expected: green — a successful `res.ok` live read still returns `provenance: 'live'`, `degraded: false`.

- [ ] **Step 6: Commit**

```bash
git add apps/hcc-app-fluent/src/data/roleboard/golden-source-client.ts apps/hcc-app-fluent/src/data/roleboard/golden-source-client.degrade.test.ts
git commit -m "feat(data): live golden read degrades to fixture instead of hanging (Sprint A, NFR-AUTH-002)"
```

---

## Task 6: My Account view

**Files:**

- Modify: `apps/hcc-app-fluent/src/auth/auth-session.tsx`
- Create: `apps/hcc-app-fluent/src/shell/account/AccountDialog.tsx`
- Modify: `apps/hcc-app-fluent/src/shell/TopBar/UserMenu.tsx`
- Test: `apps/hcc-app-fluent/src/shell/account/AccountDialog.test.tsx`

- [ ] **Step 1: Expose `username` (UPN) on the auth session**

In `apps/hcc-app-fluent/src/auth/auth-session.tsx`:

Add to the `AuthSession` interface (after `name`):

```ts
  /** UPN / email of the signed-in account; undefined for the Demo Guest. */
  username?: string;
```

Add to `DEMO_GUEST`:

```ts
  username: undefined,
```

In `AuthSessionProvider`'s `session` memo, add to the returned object (after `name:`):

```ts
      username: isAuthenticated ? account?.username : undefined,
```

- [ ] **Step 2: Write the failing test for the account view**

```tsx
// apps/hcc-app-fluent/src/shell/account/AccountDialog.test.tsx
import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { RoleProvider } from '../../context/role-context';
import { AccountDialog } from './AccountDialog';
import { parseClaims } from '../../auth/claim-parser';

function renderAccount() {
  const claims = parseClaims({
    roles: ['HCC.PlatformAdmin', 'HCC.DischargeCoordinator'],
    oid: '7b9830a6-989b-4edd-b720-0d4bff7ffb2e',
    name: 'Admin User',
  });
  return render(
    <FluentProvider theme={webLightTheme}>
      <RoleProvider claims={claims}>
        <AccountDialog open onClose={() => {}} />
      </RoleProvider>
    </FluentProvider>,
  );
}

describe('AccountDialog (Sprint A, FR-AUTH-003)', () => {
  it('shows the held roles and the active-role scope', () => {
    renderAccount();
    expect(screen.getByText('HCC.PlatformAdmin')).toBeInTheDocument();
    expect(screen.getByText('HCC.DischargeCoordinator')).toBeInTheDocument();
    expect(screen.getByText(/7b9830a6-989b-4edd-b720-0d4bff7ffb2e/)).toBeInTheDocument();
  });
});
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd apps/hcc-app-fluent; npx vitest run src/shell/account/AccountDialog.test.tsx`
Expected: FAIL — cannot resolve `./AccountDialog`.

- [ ] **Step 4: Create `AccountDialog.tsx`**

```tsx
// apps/hcc-app-fluent/src/shell/account/AccountDialog.tsx
import {
  Dialog, DialogSurface, DialogTitle, DialogBody, DialogContent, DialogActions,
  Button, Badge, Divider, Text,
} from '@fluentui/react-components';
import { SignOutRegular } from '@fluentui/react-icons';
import { useAuthSession } from '../../auth/auth-session';
import { useRoleLens } from '../../context/role-context';
import { getMsalTenantId } from '../../config/runtime-config';
import { resetSessionContext } from '../../context/session-reset';

/**
 * Sprint A (FR-AUTH-003) — My Account view. Read-only reflection of the signed-in
 * identity + the `HCC.*` roles claim: display name, UPN, oid, held roles, and the
 * active-role lens (scope + agent ceiling). No new data source — reuses the auth
 * session facade and the role lens. Sign out clears all per-user session context.
 */
export function AccountDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { name, username, signOut } = useAuthSession();
  const { userOid, heldRoles, activeRole, capabilities } = useRoleLens();

  const handleSignOut = () => {
    resetSessionContext();
    signOut();
  };

  return (
    <Dialog open={open} onOpenChange={(_, d) => { if (!d.open) onClose(); }}>
      <DialogSurface aria-label="My account">
        <DialogBody>
          <DialogTitle>My account</DialogTitle>
          <DialogContent>
            <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 8, alignItems: 'center' }}>
              <Text weight="semibold">Name</Text><Text>{name}</Text>
              <Text weight="semibold">Sign-in</Text><Text>{username ?? '—'}</Text>
              <Text weight="semibold">Object id</Text><Text>{userOid ?? '—'}</Text>
              <Text weight="semibold">Tenant</Text><Text>{getMsalTenantId()}</Text>
            </div>
            <Divider style={{ margin: '12px 0' }}>Roles</Divider>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {heldRoles.map((r) => (
                <Badge key={r} appearance={r === activeRole ? 'filled' : 'tint'} color="brand">{r}</Badge>
              ))}
            </div>
            <Divider style={{ margin: '12px 0' }}>Active lens</Divider>
            <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 8 }}>
              <Text weight="semibold">Active role</Text><Text>{activeRole}</Text>
              <Text weight="semibold">Hospital scope</Text><Text>{capabilities.hospitalScope}</Text>
              <Text weight="semibold">Agent ceiling</Text><Text>{capabilities.agentCeiling}</Text>
            </div>
          </DialogContent>
          <DialogActions>
            <Button appearance="secondary" onClick={onClose}>Close</Button>
            <Button appearance="primary" icon={<SignOutRegular />} onClick={handleSignOut}>Sign out</Button>
          </DialogActions>
        </DialogBody>
      </DialogSurface>
    </Dialog>
  );
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd apps/hcc-app-fluent; npx vitest run src/shell/account/AccountDialog.test.tsx`
Expected: PASS (1 passed).

> If a Fluent `Badge` renders its label such that `getByText` needs an exact match, adjust the assertion to `screen.getByText('HCC.PlatformAdmin')` (already exact). Keep the test asserting held roles + oid.

- [ ] **Step 6: Wire the "My account" item into `UserMenu.tsx`**

Replace `apps/hcc-app-fluent/src/shell/TopBar/UserMenu.tsx` with:

```tsx
import { useState } from 'react';
import { Menu, MenuTrigger, MenuPopover, MenuList, MenuItem, Button, Badge } from '@fluentui/react-components';
import { PersonRegular, SignOutRegular, ArrowEnterRegular, ContactCardRegular } from '@fluentui/react-icons';
import { useAuthSession } from '../../auth/auth-session';
import { resetSessionContext } from '../../context/session-reset';
import { AccountDialog } from '../account/AccountDialog';

/**
 * Sprint 20 M3 / Sprint 27 / Sprint 29 / Sprint A — user menu bound to the auth
 * session. Shows the signed-in account (or the read-only Demo Guest), a "My
 * account" view of identity + roles when signed in (FR-AUTH-003), and Sign in /
 * Sign out against the MngEnvMCAP164444 tenant when MSAL is configured. Sign-out
 * clears all per-user session context (Sprint 29 #424 M1).
 */
export function UserMenu() {
  const { name, isAuthenticated, readOnly, configured, signIn, signOut } = useAuthSession();
  const [accountOpen, setAccountOpen] = useState(false);

  const handleSignOut = () => {
    resetSessionContext();
    signOut();
  };

  return (
    <>
      <Menu>
        <MenuTrigger disableButtonEnhancement>
          <Button aria-label="User menu" icon={<PersonRegular />} appearance="subtle">
            {name}
            {readOnly && (
              <Badge appearance="tint" color="informative" size="small" style={{ marginLeft: 8 }}>
                read-only
              </Badge>
            )}
          </Button>
        </MenuTrigger>
        <MenuPopover>
          <MenuList>
            {isAuthenticated ? (
              <>
                <MenuItem icon={<ContactCardRegular />} onClick={() => setAccountOpen(true)}>
                  My account
                </MenuItem>
                <MenuItem icon={<SignOutRegular />} onClick={handleSignOut}>
                  Sign out
                </MenuItem>
              </>
            ) : configured ? (
              <MenuItem icon={<ArrowEnterRegular />} onClick={signIn}>
                Sign in
              </MenuItem>
            ) : (
              <MenuItem disabled>Sign-in not configured (demo)</MenuItem>
            )}
          </MenuList>
        </MenuPopover>
      </Menu>
      <AccountDialog open={accountOpen} onClose={() => setAccountOpen(false)} />
    </>
  );
}
```

- [ ] **Step 7: Run the full suite (UserMenu + auth-session have existing tests)**

Run: `cd apps/hcc-app-fluent; npm run test 2>&1 | Select-Object -Last 25`
Expected: green. If an existing `UserMenu` test asserts the exact menu items, update it to include "My account" when authenticated.

- [ ] **Step 8: Typecheck + lint the app**

Run: `cd apps/hcc-app-fluent; npm run build 2>&1 | Select-Object -Last 15`
Expected: `tsc` + Vite build succeed (verifies the `ContactCardRegular` icon import and Dialog types).

- [ ] **Step 9: Commit**

```bash
git add apps/hcc-app-fluent/src/auth/auth-session.tsx apps/hcc-app-fluent/src/shell/account/AccountDialog.tsx apps/hcc-app-fluent/src/shell/account/AccountDialog.test.tsx apps/hcc-app-fluent/src/shell/TopBar/UserMenu.tsx
git commit -m "feat(auth): My Account view of identity + HCC roles (Sprint A, FR-AUTH-003)"
```

---

## Task 7: PRD requirements + traceability

**Files:**

- Modify: `docs/PRD.md`

- [ ] **Step 1: Add the requirements**

Add to the FR/NFR catalogue in `docs/PRD.md` (use the surrounding table format exactly):

- `FR-AUTH-001` — A tenant member can sign in and sign out of the Curavias app via Entra (`ihzhhpf-app`); signed-out state is the read-only Demo Guest.
- `FR-AUTH-002` — The app derives the role lens (nav, hospital scope, agent ceiling) from the `roles` claim; in SIT a PlatformAdmin/DemoOperator may narrow to any held role.
- `FR-AUTH-003` — A My Account view shows display name, UPN, oid, held roles, and the active-role scope + ceiling.
- `NFR-AUTH-001` — MSAL config is runtime-injected (`window.__ENV__`); one env-agnostic image, no secrets or per-env values baked at build.
- `NFR-AUTH-002` — Live boards fail loud (degrade to fixture + GroundingNotice) and never hang when a golden read is refused/unavailable.

- [ ] **Step 2: Update §7 traceability matrix**

Add matrix rows mapping each `FR-AUTH-*` / `NFR-AUTH-*` to this plan + the Task that implements it and its test file.

- [ ] **Step 3: Bump the PRD version (MINOR — additive requirements) and `Previous Version`**

Follow copilot-instructions §9. Update `Version`, `Date` (2026-08-02), and `Previous Version` with a parenthetical hint (`added FR/NFR-AUTH-*`).

- [ ] **Step 4: Gate the doc (mojibake + markdownlint)**

Run:

```powershell
python scripts/lint/check_mojibake.py docs/PRD.md
npx --yes markdownlint-cli2 docs/PRD.md
```

Expected: mojibake OK; markdownlint 0 issues.

- [ ] **Step 5: Commit**

```bash
git add docs/PRD.md
git commit -m "docs(prd): add FR/NFR-AUTH-* for Sprint A member sign-in"
```

---

## Task 8: Entra SPA redirect URI (operational, main session)

**Files:** none (Microsoft Graph change to the `ihzhhpf-app` registration — user pre-approved).

- [ ] **Step 1: Check the current SPA redirect URIs**

Use PowerShell + Graph (az.cmd mishandles `(` in filters — use `Invoke-RestMethod`). Acquire a token, then:

```powershell
$token = (az account get-access-token --resource https://graph.microsoft.com --query accessToken -o tsv)
$app = Invoke-RestMethod -Headers @{ Authorization = "Bearer $token" } `
  -Uri "https://graph.microsoft.com/v1.0/applications?`$filter=appId eq '52681a08-c792-44b1-b6b5-01cb560d450f'"
$obj = $app.value[0]
$obj.spa.redirectUris
```

Expected: prints the current SPA redirect URIs. Note the app object id (`$obj.id`).

- [ ] **Step 2: Add `https://appsit.curavias.ch` if missing (idempotent)**

```powershell
$uris = @($obj.spa.redirectUris)
if ($uris -notcontains 'https://appsit.curavias.ch') {
  $uris += 'https://appsit.curavias.ch'
  $body = @{ spa = @{ redirectUris = $uris } } | ConvertTo-Json -Depth 5
  Invoke-RestMethod -Method Patch -Headers @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' } `
    -Uri "https://graph.microsoft.com/v1.0/applications/$($obj.id)" -Body $body
}
```

- [ ] **Step 3: Verify**

Re-run Step 1; confirm `https://appsit.curavias.ch` is present in `spa.redirectUris`.

---

## Task 9: Build image, gated SIT deploy, sign-in E2E (operational, main session)

**Files:** none (CI + gated deploy).

- [ ] **Step 1: Push the app commits to build the image**

Push the branch/commits touching `apps/hcc-app-fluent/**`; `ci-build-app-fluent.yml` builds + pushes a new `hcc-app-fluent:<shortSHA>` to ACR (gated by the `sit` GitHub Environment — approve the pending deployment).

- [ ] **Step 2: Pin the new image tag in `sit.bicepparam`**

Update `appFluentImage = 'cri75lbu5sj4hza.azurecr.io/hcc-app-fluent:<newShortSHA>'` with a Sprint A comment. Commit.

- [ ] **Step 3: Push infra + approve the gated SIT deploy**

Push `infra/environments/sit.bicepparam` (+ the Task 3 infra commit). `cd-infra-deploy-sit` runs; approve the `sit` Environment gate. Deploy sets the MSAL env vars on `ca-app-fluent-ihzhhpf-sit` and rolls a new revision.

- [ ] **Step 4: Verify the runtime config landed**

```powershell
Invoke-WebRequest -UseBasicParsing https://appsit.curavias.ch/env-config.js | Select-Object -ExpandProperty Content
```

Expected: contains `MSAL_CLIENT_ID: "52681a08-..."`, `APP_ENV: "sit"`, `MSAL_REDIRECT_URI: "https://appsit.curavias.ch"`.

- [ ] **Step 5: Sign-in E2E (user drives credentials — the agent NEVER enters the password)**

Navigate to `https://appsit.curavias.ch`, open the User menu, click **Sign in**. The **user** completes the Entra prompt with `admin@mngenvmcap164444.onmicrosoft.com` (or `urruegg@…`). Then verify:

1. UserMenu shows the signed-in name (no "read-only" badge).
2. Role lens = PlatformAdmin (all nav visible); role switcher present (APP_ENV=sit).
3. Switch to DischargeCoordinator → main-only nav; discharge worklist loads live (3 barriers) via the loop endpoints.
4. Accept a barrier → outcome + shrink under the user oid; Closed-Loop Evidence board renders the trace.
5. Live board (e.g. Occupancy) renders live (200) or degrades gracefully — never hangs.
6. Open **My account** → shows both roles + oid + active-role scope.
7. Sign out → returns to Demo Guest (read-only badge); a Live board degrades (no hang).

- [ ] **Step 6: Record evidence**

Capture the E2E result (screenshots / notes) and confirm PROD is untouched (no `approved-to-apply` given for PROD).

---

## Self-Review

**Spec coverage:**

- Spec 4.1 (runtime MSAL config) → Task 1. ✓
- Spec 4.2 (env injection) → Task 2 + Task 3. ✓
- Spec 4.3 (Entra redirect) → Task 8. ✓
- Spec 4.4 (signed-in golden read + degrade companion) → resolved: no agent-host change (any non-empty oid → 200); the degrade guard is Task 5; verification is Task 9 Step 5. ✓
- Spec 4.5 (My Account view) → Task 6. ✓
- Spec §5 (role assignment) → already done 2026-08-02. ✓
- Spec §6 data flow ("switch to DischargeCoordinator") → Task 4 (env fallback enables the switcher). ✓
- Spec §7 testing/acceptance → Task 9 Step 5. ✓
- Spec §10 requirements → Task 7. ✓

**Placeholder scan:** No TBD/TODO; every code step shows complete code. Task 5 Step 1 and Task 6 Step 5 include a note to confirm exact export/label names against the actual files — verification instructions, not placeholders.

**Type consistency:** `RuntimeEnv` fields (`MSAL_CLIENT_ID`, `MSAL_TENANT_ID`, `MSAL_REDIRECT_URI`, `APP_ENV`, `APP_HOME_HOSPITAL`) are used identically by the getters (Task 1), the entrypoint script keys (Task 2), and the Bicep env names (Task 3). Getters `getMsalClientId/getMsalTenantId/getMsalRedirectUri/getAppEnv/getHomeHospital` are defined in Task 1 and consumed in Tasks 1/4/6. `AuthSession.username` defined in Task 6 Step 1, consumed in Task 6 Step 4. Role lens fields (`userOid`, `heldRoles`, `activeRole`, `capabilities.hospitalScope`, `capabilities.agentCeiling`) match `role-context.tsx` / `rbac-model.ts`.

---

## Execution Handoff

Two execution options:

1. **Subagent-Driven (recommended)** — fresh subagent per task, two-stage review between tasks (Tasks 1–7 are code/doc and subagent-friendly; Tasks 8–9 are operational and run in the main session with the approval gates).
2. **Inline Execution** — batch execution with checkpoints for review.
