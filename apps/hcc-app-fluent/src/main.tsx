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
  const root = createRoot(rootEl);
  const render = () =>
    root.render(
      <StrictMode>
        <MsalProvider instance={msalInstance}>
          <Root />
        </MsalProvider>
      </StrictMode>,
    );
  // Redeem the redirect auth-code response and pin the active account BEFORE the
  // router mounts. The code arrives in the URL fragment (response_mode=fragment);
  // React Router's initial navigation would otherwise drop it before MSAL reads
  // it, leaving the app anonymous after a successful sign-in.
  msalInstance
    .initialize()
    .then(() => msalInstance.handleRedirectPromise())
    .then((result) => {
      const account =
        result?.account ?? msalInstance.getActiveAccount() ?? msalInstance.getAllAccounts()[0];
      if (account) {
        msalInstance.setActiveAccount(account);
      }
    })
    .catch((error) => {
      console.error('MSAL redirect handling failed', error);
    })
    .finally(render);
}
