import type { Hospital } from '../../auth/claim-parser';

/**
 * Sprint 27 — app-side mirror of the anonymized Curavias showcase tenants used
 * by the Fabric demo data
 * (`data/master-data/curavias-org-skills/dim_tenant.csv`). Every real hospital
 * name is anonymized to a Curavias tenant (Uniklinik CuraNova, Kantonsspital
 * Curalp, Spital Vialta) so the selector matches the gold / semantic-model data.
 * Single source for the hospital / tenant scopes the header selector offers;
 * keep in sync with the CSV.
 *
 * `scopeId` maps each tenant → the internal app `Hospital` scope key (not shown
 * in the UI). The platform-wide `all` scope is carried for completeness but is
 * not yet selectable (it becomes available once the role model adds
 * platform-admin roles that hold it).
 */
export type OrgScopeId = Hospital | 'all';

export interface OrgReference {
  /** tenant_id from the master data (CN / CP / VT), or the logical-scope key. */
  key: string;
  /** Maps to the internal app Hospital scope used by the boards / claims. */
  scopeId: OrgScopeId;
  /** Anonymized Curavias tenant name (from the master data). */
  displayName: string;
  /** Compact label for the selector button. */
  shortName: string;
  orgType: 'acute-hospital' | 'logical-scope';
  /** Anonymized canton code, or '-' for logical scopes. */
  canton: string;
  scope: 'hospital' | 'aggregate' | 'platform';
}

/** Every Curavias tenant / logical scope defined in the master data. */
export const ORGANIZATIONS: OrgReference[] = [
  { key: 'CN', scopeId: 'usz', displayName: 'Uniklinik CuraNova', shortName: 'CuraNova', orgType: 'acute-hospital', canton: 'HN', scope: 'hospital' },
  { key: 'CP', scopeId: 'luks', displayName: 'Kantonsspital Curalp', shortName: 'Curalp', orgType: 'acute-hospital', canton: 'CA', scope: 'hospital' },
  { key: 'VT', scopeId: 'zollikerberg', displayName: 'Spital Vialta', shortName: 'Vialta', orgType: 'acute-hospital', canton: 'HN', scope: 'hospital' },
  { key: 'Aggregated', scopeId: 'aggregated', displayName: 'Aggregated cross-hospital view', shortName: 'Aggregated', orgType: 'logical-scope', canton: '-', scope: 'aggregate' },
  { key: 'All', scopeId: 'all', displayName: 'Platform-wide (all tenants)', shortName: 'All', orgType: 'logical-scope', canton: '-', scope: 'platform' },
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
