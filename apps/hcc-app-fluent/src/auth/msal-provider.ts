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

/** Default sign-in scopes; per-agent MCP scopes are acquired dynamically. */
export const loginRequest = {
  scopes: ['openid', 'profile', 'User.Read'],
};

export const msalInstance = new PublicClientApplication(msalConfig);
