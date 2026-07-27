/**
 * Sprint 16.1 · S16.5 — role guard for the CSA wizard.
 *
 * Wraps the wizard render with a role check per S16 design spec §8. Users
 * without any of the allowed roles see nothing here — the informational
 * Scenario board (rendered by CsaView) is the shared surface, so a deny
 * message below it would only be noise. Matches the "least data exposure"
 * default from claim-parser.ts.
 *
 * Pure component; unit-tested against the role-context.
 */
import type { ReactNode } from 'react';
import { useRoleLens } from '../../../../context/role-context';

/**
 * Roles whose RBAC lens grants the `csa` nav capability.
 */
export const CSA_WIZARD_ROLES: readonly string[] = [
  'HCC.DemoOperator',
  'HCC.PlatformAdmin',
  'HCC.CrisisManager',
  'HCC.RegionalCrisisLead',
];

interface CsaRoleGuardProps {
  children: ReactNode;
}

/** Render children only for callers with any CSA-wizard role, deny otherwise. */
export function CsaRoleGuard({ children }: CsaRoleGuardProps) {
  const { capabilities } = useRoleLens();
  const allowed = capabilities.nav.csa;
  // Unauthorised callers see nothing here: the informational Scenario board
  // (rendered by CsaView) is the shared surface, so a deny message below it
  // would only be noise. The wizard stays gated to CSA-authorised roles.
  if (!allowed) return null;
  return <>{children}</>;
}
