import { Configuration, PublicClientApplication } from '@azure/msal-browser';

/**
 * Sprint 13 T2 — MSAL v2 configuration for the `ihzhhpf-app` registration
 * (Sprint 12 T1 output). Values come from Vite env vars so the client-id and
 * tenant are never hard-coded (copilot-instructions §3 guardrail).
 *
 * Required env (see apps/hcc-app-fluent/README.md):
 *   VITE_MSAL_CLIENT_ID   — ihzhhpf-app application (client) id
 *   VITE_MSAL_TENANT_ID   — MngEnvMCAP164444 tenant id (ADR-0012)
 *   VITE_MSAL_REDIRECT_URI — SPA redirect URI for the current slot
 */
const clientId = import.meta.env.VITE_MSAL_CLIENT_ID ?? '';
const tenantId = import.meta.env.VITE_MSAL_TENANT_ID ?? 'common';

export const msalConfig: Configuration = {
  auth: {
    clientId,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri: import.meta.env.VITE_MSAL_REDIRECT_URI ?? window.location.origin,
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
