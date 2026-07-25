import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { MsalProvider, useMsal } from '@azure/msal-react';
import { App } from './App';
import { msalInstance } from './auth/msal-provider';
import { AuthSessionProvider } from './auth/auth-session';
import type { RawClaims } from './auth/claim-parser';
import './index.css';

/**
 * Sprint 13 / Sprint 27 — app bootstrap.
 *
 * `Root` reads the active MSAL account (once signed in) and bridges its
 * id-token claims into `App` as `rawClaims`; before sign-in the account is
 * absent, so `App` renders the anonymous read-only Demo Guest shell
 * (aggregated-only). `AuthSessionProvider` exposes the sign-in / sign-out
 * affordance to the shell. Theme + routing providers live inside `App`.
 */
function Root() {
  const { instance, accounts } = useMsal();
  const account = instance.getActiveAccount() ?? accounts[0] ?? null;
  const rawClaims = (account?.idTokenClaims ?? undefined) as RawClaims | undefined;
  return (
    <AuthSessionProvider>
      <App rawClaims={rawClaims} />
    </AuthSessionProvider>
  );
}

const rootEl = document.getElementById('root');
if (rootEl) {
  createRoot(rootEl).render(
    <StrictMode>
      <MsalProvider instance={msalInstance}>
        <Root />
      </MsalProvider>
    </StrictMode>,
  );
}
