import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { MsalProvider } from '@azure/msal-react';
import { App } from './App';
import { msalInstance } from './auth/msal-provider';

/**
 * Sprint 13 — app bootstrap.
 *
 * Wraps App in the MSAL provider. Claim extraction from the active account is
 * done by App via the claim parser; before sign-in the app renders as the
 * anonymous demo.guest shell (aggregated-only). Theme + routing providers live
 * inside App so it stays self-contained for tests and bootstrap alike.
 */
const rootEl = document.getElementById('root');
if (rootEl) {
  createRoot(rootEl).render(
    <StrictMode>
      <MsalProvider instance={msalInstance}>
        <App />
      </MsalProvider>
    </StrictMode>,
  );
}
