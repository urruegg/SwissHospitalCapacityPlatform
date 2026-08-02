import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import { hasAnyRole, parseClaims, type AppEnv, type Hospital, type ParsedClaims } from '../auth/claim-parser';
import {
  deriveCapabilities,
  highestRole,
  isHccRole,
  narrowRoles,
  type HccRole,
  type HospitalScope,
  type RoleCapabilities,
} from '../auth/rbac-model';
import { getAppEnv, getHomeHospital } from '../config/runtime-config';

/**
 * Sprint 13 T2/T4 — role context.
 *
 * Exposes the caller's roles + env and the derived permission flags the shell
 * needs. The role switcher is visible only when `env=sit` AND the caller holds
 * `HCC.PlatformAdmin` or `HCC.DemoOperator` (design spec §2.1).
 *
 * Sprint 20 M3 — the additive role LENS. `useRoleLens()` exposes the active
 * role as an access lens (data scope + agent ceiling + nav capabilities) with
 * narrow-only in-session switching. The legacy `claims` API and `useRole()`
 * are preserved unchanged so the existing shell keeps working.
 */
export const ROLE_SWITCHER_ROLES = ['HCC.PlatformAdmin', 'HCC.DemoOperator'];

interface RoleContextValue {
  roles: string[];
  env: AppEnv;
  canSwitchRole: boolean;
  has: (roles: string[]) => boolean;
}

interface RoleLensValue {
  userOid: string | null;
  heldRoles: HccRole[];
  activeRole: HccRole;
  capabilities: RoleCapabilities & { hospitalScope: HospitalScope };
  setActiveRole: (role: HccRole) => void;
}

const RoleContext = createContext<RoleContextValue | undefined>(undefined);
const RoleLensContext = createContext<RoleLensValue | undefined>(undefined);

const HOSPITAL_SCOPES: readonly HospitalScope[] = ['usz', 'luks', 'zollikerberg', 'aggregated'];

/** Effective env: runtime APP_ENV wins over the (often-absent) token `env` claim. Sprint A. */
function effectiveEnv(claims: ParsedClaims): AppEnv {
  const runtime = getAppEnv().toLowerCase();
  if (runtime === 'dev' || runtime === 'sit' || runtime === 'prod') {
    return runtime;
  }
  return claims.env;
}

export function canSwitchRole(claims: ParsedClaims): boolean {
  return effectiveEnv(claims) === 'sit' && hasAnyRole(claims, ROLE_SWITCHER_ROLES);
}

export function RoleProvider({
  claims,
  testRoles,
  testHomeSite,
  children,
}: {
  claims?: ParsedClaims;
  testRoles?: string[];
  testHomeSite?: HospitalScope;
  children: ReactNode;
}) {
  const effectiveClaims = claims ?? parseClaims(undefined);

  const value = useMemo<RoleContextValue>(() => {
    const env = effectiveEnv(effectiveClaims);
    return {
      roles: effectiveClaims.roles,
      env,
      canSwitchRole: canSwitchRole(effectiveClaims),
      has: (roles: string[]) => hasAnyRole(effectiveClaims, roles),
    };
  }, [effectiveClaims]);

  // Held roles for the lens: prefer explicit test roles, else the parsed claim
  // roles, filtered to the five mapped demo roles. Defaults to Viewer (least
  // privilege) so unmapped roles (e.g. HCC.SuperAdmin) never break derivation.
  const rawHeld: string[] = testRoles ?? effectiveClaims.roles;
  const held: HccRole[] = rawHeld.filter(isHccRole);
  const heldSafe: HccRole[] = held.length > 0 ? held : ['HCC.Viewer'];
  const runtimeHome = getHomeHospital().toLowerCase();
  const runtimeHomeSite = HOSPITAL_SCOPES.includes(runtimeHome as HospitalScope)
    ? (runtimeHome as HospitalScope)
    : undefined;
  const homeSite: HospitalScope =
    testHomeSite ?? runtimeHomeSite ?? (effectiveClaims.hospital as Hospital as HospitalScope);
  const userOid = effectiveClaims.oid ?? null;

  const [activeRole, setActive] = useState<HccRole>(() => highestRole(heldSafe));

  const heldKey = heldSafe.join(',');
  const lensValue = useMemo<RoleLensValue>(
    () => ({
      userOid,
      heldRoles: heldSafe,
      activeRole,
      capabilities: deriveCapabilities(activeRole, homeSite),
      setActiveRole: (role: HccRole) => setActive(narrowRoles(heldSafe, role)),
    }),
    // heldSafe/homeSite derive from stable claim/test inputs; activeRole drives updates.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [activeRole, homeSite, heldKey, userOid],
  );

  return (
    <RoleContext.Provider value={value}>
      <RoleLensContext.Provider value={lensValue}>{children}</RoleLensContext.Provider>
    </RoleContext.Provider>
  );
}

export function useRole(): RoleContextValue {
  const ctx = useContext(RoleContext);
  if (!ctx) throw new Error('useRole must be used within a RoleProvider');
  return ctx;
}

export function useRoleLens(): RoleLensValue {
  const ctx = useContext(RoleLensContext);
  if (!ctx) throw new Error('useRoleLens must be used within a RoleProvider');
  return ctx;
}
