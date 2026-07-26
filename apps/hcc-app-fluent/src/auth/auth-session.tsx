import { createContext, useContext, useMemo, type ReactNode } from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest, msalConfig } from './msal-provider';

/**
 * Sprint 27 — auth session facade.
 *
 * Wraps MSAL so the shell can show a real sign-in / sign-out affordance against
 * the MngEnvMCAP164444 tenant (per ADR-0012) when configured, and degrade to a
 * read-only Demo Guest when not. Kept as a thin context so `UserMenu` (and any
 * other consumer) never calls MSAL hooks directly — that also lets components
 * render in tests without an `MsalProvider`.
 */
export interface AuthSession {
  isAuthenticated: boolean;
  /** Display name; the read-only Demo Guest when signed out. */
  name: string;
  /** True while running as the anonymous read-only demo guest. */
  readOnly: boolean;
  /** True when MSAL is configured (a client id is present) so sign-in can work. */
  configured: boolean;
  signIn: () => void;
  signOut: () => void;
}

/** Fallback used when no provider is present (tests / anonymous bootstrap). */
const DEMO_GUEST: AuthSession = {
  isAuthenticated: false,
  name: 'Demo Guest',
  readOnly: true,
  configured: false,
  signIn: () => {},
  signOut: () => {},
};

const AuthSessionContext = createContext<AuthSession | undefined>(undefined);

export function AuthSessionProvider({ children }: { children: ReactNode }) {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const configured = Boolean(msalConfig.auth.clientId);
  const account = accounts[0];

  const session = useMemo<AuthSession>(
    () => ({
      isAuthenticated,
      name: isAuthenticated && account?.name ? account.name : 'Demo Guest',
      readOnly: !isAuthenticated,
      configured,
      signIn: () => {
        // Guard: without a configured client id a redirect would only error.
        if (configured) void instance.loginRedirect(loginRequest);
      },
      signOut: () => {
        void instance.logoutRedirect();
      },
    }),
    [isAuthenticated, account, configured, instance],
  );

  return <AuthSessionContext.Provider value={session}>{children}</AuthSessionContext.Provider>;
}

/** Auth session; degrades to the read-only Demo Guest when no provider is present. */
export function useAuthSession(): AuthSession {
  return useContext(AuthSessionContext) ?? DEMO_GUEST;
}
