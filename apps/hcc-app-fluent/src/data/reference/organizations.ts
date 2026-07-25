import type { Hospital } from '../../auth/claim-parser';

/**
 * Sprint 27 — app-side mirror of the Entra organizations master data
 * (`data/entra/organizations.csv`). Single source for the hospital / tenant
 * scopes the header selector offers, so the UI reflects the real data contract
 * instead of a hard-coded list. Keep in sync with the CSV.
 *
 * `scopeId` maps `org_key` → the app `Hospital` scope. The platform-wide `all`
 * scope is carried here for completeness but is not yet selectable (it becomes
 * available once the role model adds platform-admin roles that hold it).
 */
export type OrgScopeId = Hospital | 'all';

export interface OrgReference {
  /** org_key from the master data. */
  key: string;
  /** Maps to the app Hospital scope used by the boards / claims. */
  scopeId: OrgScopeId;
  /** Full display name (from the master data). */
  displayName: string;
  /** Compact label for the selector button. */
  shortName: string;
  orgType: 'acute-hospital' | 'logical-scope';
  /** Canton code, or '-' for logical scopes. */
  canton: string;
  scope: 'hospital' | 'aggregate' | 'platform';
}

/** Every organization / logical scope defined in the master data. */
export const ORGANIZATIONS: OrgReference[] = [
  { key: 'USZ', scopeId: 'usz', displayName: 'Universitätsspital Zürich', shortName: 'USZ', orgType: 'acute-hospital', canton: 'ZH', scope: 'hospital' },
  { key: 'LUKS', scopeId: 'luks', displayName: 'Luzerner Kantonsspital', shortName: 'LUKS', orgType: 'acute-hospital', canton: 'LU', scope: 'hospital' },
  { key: 'Zollikerberg', scopeId: 'zollikerberg', displayName: 'Spital Zollikerberg', shortName: 'Zollikerberg', orgType: 'acute-hospital', canton: 'ZH', scope: 'hospital' },
  { key: 'Aggregated', scopeId: 'aggregated', displayName: 'Aggregated cross-hospital view', shortName: 'Aggregated', orgType: 'logical-scope', canton: '-', scope: 'aggregate' },
  { key: 'All', scopeId: 'all', displayName: 'Platform-wide (all hospitals)', shortName: 'All', orgType: 'logical-scope', canton: '-', scope: 'platform' },
];

/**
 * Scopes offered by the hospital selector — the three sites plus the aggregated
 * cross-hospital view. Excludes the platform-wide `all` scope until roles hold it.
 */
export const HOSPITAL_OPTIONS: OrgReference[] = ORGANIZATIONS.filter((o) => o.scopeId !== 'all');

/** Display metadata for a given scope. */
export function orgForScope(scopeId: OrgScopeId): OrgReference | undefined {
  return ORGANIZATIONS.find((o) => o.scopeId === scopeId);
}
