import { useEffect, useState } from 'react';
import {
  Title2,
  Body1,
  Spinner,
  Table,
  TableHeader,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
} from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { readAppRoles, type AppRole } from './roles-service';

/**
 * Sprint 13 T4 — Backstage "Roles & RBAC" tab.
 *
 * Renders the live app-role list from Entra Graph (read-only). Falls back to a
 * synthetic sample when no Graph client is wired (dev/CI). Graph client wiring is
 * injected from the MSAL provider in a follow-up; the tab is data-source-agnostic.
 */
export function RolesTab() {
  const { t } = useTranslation();
  const [roles, setRoles] = useState<AppRole[] | null>(null);

  useEffect(() => {
    let active = true;
    // No Graph client injected yet → sample data (read-only reader handles it).
    void readAppRoles(null, undefined).then((r) => {
      if (active) setRoles(r);
    });
    return () => {
      active = false;
    };
  }, []);

  return (
    <section aria-label={t('backstage.roles')}>
      <Title2>{t('backstage.roles')}</Title2>
      <Body1 as="p">{t('backstage.rolesDescription')}</Body1>
      {roles === null ? (
        <Spinner label={t('app.loading')} />
      ) : (
        <Table aria-label={t('backstage.roles')}>
          <TableHeader>
            <TableRow>
              <TableHeaderCell>Role</TableHeaderCell>
              <TableHeaderCell>Value</TableHeaderCell>
              <TableHeaderCell>Assignments</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {roles.map((r) => (
              <TableRow key={r.id}>
                <TableCell>{r.displayName}</TableCell>
                <TableCell>{r.value}</TableCell>
                <TableCell>{r.assignmentCount}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </section>
  );
}
