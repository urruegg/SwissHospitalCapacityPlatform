import { useCallback } from 'react';
import { useAuthSession } from './auth-session';
import { resetSessionContext } from '../context/session-reset';

/**
 * Sprint A — single source of truth for a full sign-out. Clears ALL per-user
 * session context (every (user x agent) thread, the Foundry thread map, and the
 * IQ ContextEnvelope) BEFORE ending the MSAL session, so a subsequent session
 * never inherits a prior user's context or data scope. Use everywhere a sign-out
 * is offered (UserMenu, AccountDialog) so the teardown can never drift.
 */
export function useSignOut(): () => void {
  const { signOut } = useAuthSession();
  return useCallback(() => {
    resetSessionContext();
    signOut();
  }, [signOut]);
}
