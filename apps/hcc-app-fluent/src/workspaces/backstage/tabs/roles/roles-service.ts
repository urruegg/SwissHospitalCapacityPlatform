import type { Client } from '@microsoft/microsoft-graph-client';

/**
 * Sprint 13 T4 — read-only Entra app-role reader.
 *
 * Reads `/servicePrincipals/{ihzhhpf-app}?$select=appRoles` plus
 * `appRoleAssignedTo` via `@microsoft/microsoft-graph-client`. The side-effect
 * ceiling is strictly `read` (AGENTS.md §3) — this module never writes to Graph.
 *
 * When no Graph client / service-principal id is configured (dev, test, CI
 * without secrets) the reader returns a small synthetic sample so the tab still
 * renders. No PHI is involved (app-role metadata only).
 */
export interface AppRole {
  id: string;
  displayName: string;
  value: string;
  description: string;
  assignmentCount: number;
}

interface GraphAppRole {
  id: string;
  displayName?: string;
  value?: string;
  description?: string;
}

const SAMPLE_ROLES: AppRole[] = [
  {
    id: 'sample-1',
    displayName: 'Platform Admin',
    value: 'HCC.PlatformAdmin',
    description: 'Full platform administration (SIT demo).',
    assignmentCount: 2,
  },
  {
    id: 'sample-2',
    displayName: 'Demo Operator',
    value: 'HCC.DemoOperator',
    description: 'Runs demo scenarios; may switch roles in SIT.',
    assignmentCount: 3,
  },
  {
    id: 'sample-3',
    displayName: 'Bed Manager',
    value: 'HCC.BedManager',
    description: 'Operates the BedManager whiteboard for a hospital.',
    assignmentCount: 5,
  },
];

export async function readAppRoles(
  client: Client | null,
  servicePrincipalId: string | undefined,
): Promise<AppRole[]> {
  if (!client || !servicePrincipalId) {
    return SAMPLE_ROLES;
  }

  const sp = (await client
    .api(`/servicePrincipals/${servicePrincipalId}`)
    .select('appRoles')
    .get()) as { appRoles?: GraphAppRole[] };

  const assignments = (await client
    .api(`/servicePrincipals/${servicePrincipalId}/appRoleAssignedTo`)
    .select('appRoleId')
    .get()) as { value?: { appRoleId?: string }[] };

  const counts = new Map<string, number>();
  for (const a of assignments.value ?? []) {
    if (a.appRoleId) counts.set(a.appRoleId, (counts.get(a.appRoleId) ?? 0) + 1);
  }

  return (sp.appRoles ?? []).map((r) => ({
    id: r.id,
    displayName: r.displayName ?? r.value ?? r.id,
    value: r.value ?? '',
    description: r.description ?? '',
    assignmentCount: counts.get(r.id) ?? 0,
  }));
}
