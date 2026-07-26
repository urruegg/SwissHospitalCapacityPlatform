/**
 * Sprint 16.1 · S16.5 — role guard for the CSA wizard.
 *
 * Wraps the wizard render with a role check per S16 design spec §8. Users
 * without any of the allowed roles see a friendly deny message instead of the
 * wizard, matching the "least data exposure" default from claim-parser.ts.
 *
 * Pure component; unit-tested against the role-context.
 */
import type { ReactNode } from 'react';
import { Body1, MessageBar, Title2 } from '@fluentui/react-components';
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
  if (allowed) return <>{children}</>;
  return (
    <section aria-label="CSA wizard access denied" data-testid="CsaRoleGuardDenied">
      <Title2>Crisis Scenario Analysis</Title2>
      <MessageBar intent="warning">
        <Body1 as="p">
          You need one of the following app roles to run the CSA wizard:{' '}
          {CSA_WIZARD_ROLES.join(', ')}. Ask a Platform Admin to grant access.
        </Body1>
      </MessageBar>
    </section>
  );
}
