import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { MsalProvider } from '@azure/msal-react';
import './i18n';
import { App } from './App';
import { msalInstance } from './auth/msal-provider';
import { ThemeModeProvider } from './theme/theme-context';

/**
 * Sprint 13 — app bootstrap.
 *
 * Wraps App in the MSAL provider. Claim extraction from the active account is
 * done by App via the claim parser; before sign-in the app renders as the
 * anonymous demo.guest shell (aggregated-only).
 */
const rootEl = document.getElementById('root');
if (rootEl) {
  createRoot(rootEl).render(
    <StrictMode>
      <ThemeModeProvider>
        <MsalProvider instance={msalInstance}>
          <App />
        </MsalProvider>
      </ThemeModeProvider>
    </StrictMode>,
  );
}
