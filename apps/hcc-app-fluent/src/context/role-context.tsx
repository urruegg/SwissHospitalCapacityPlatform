import { createContext, useContext, useMemo, type ReactNode } from 'react';
import { hasAnyRole, type AppEnv, type ParsedClaims } from '../auth/claim-parser';

/**
 * Sprint 13 T2/T4 — role context.
 *
 * Exposes the caller's roles + env and the derived permission flags the shell
 * needs. The role switcher is visible only when `env=sit` AND the caller holds
 * `HCC.PlatformAdmin` or `HCC.DemoOperator` (design spec §2.1).
 */
export const ROLE_SWITCHER_ROLES = ['HCC.PlatformAdmin', 'HCC.DemoOperator'];

interface RoleContextValue {
  roles: string[];
  env: AppEnv;
  canSwitchRole: boolean;
  has: (roles: string[]) => boolean;
}

const RoleContext = createContext<RoleContextValue | undefined>(undefined);

export function canSwitchRole(claims: ParsedClaims): boolean {
  return claims.env === 'sit' && hasAnyRole(claims, ROLE_SWITCHER_ROLES);
}

export function RoleProvider({
  claims,
  children,
}: {
  claims: ParsedClaims;
  children: ReactNode;
}) {
  const value = useMemo<RoleContextValue>(
    () => ({
      roles: claims.roles,
      env: claims.env,
      canSwitchRole: canSwitchRole(claims),
      has: (roles: string[]) => hasAnyRole(claims, roles),
    }),
    [claims],
  );
  return <RoleContext.Provider value={value}>{children}</RoleContext.Provider>;
}

export function useRole(): RoleContextValue {
  const ctx = useContext(RoleContext);
  if (!ctx) throw new Error('useRole must be used within a RoleProvider');
  return ctx;
}
