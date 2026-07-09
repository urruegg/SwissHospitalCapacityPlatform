/**
 * Sprint 13 T2 — parse the Sprint 12 app-registration claims into typed values.
 *
 * The `ihzhhpf-app` registration issues `roles`, `hospital`, and `env` claims.
 * `auth` is the single source of truth for these; everything else consumes them
 * (design spec §3 component boundaries).
 */

export type Hospital = 'usz' | 'luks' | 'zollikerberg' | 'aggregated';
export type AppEnv = 'dev' | 'sit' | 'prod';

/** App roles are namespaced `HCC.*` in the Sprint 12 registration. */
export interface ParsedClaims {
  roles: string[];
  hospital: Hospital;
  env: AppEnv;
  name?: string;
  oid?: string;
}

/** Raw ID-token claim shape (subset we consume). */
export interface RawClaims {
  roles?: string[] | string;
  hospital?: string;
  env?: string;
  name?: string;
  oid?: string;
  [key: string]: unknown;
}

const HOSPITALS: readonly Hospital[] = ['usz', 'luks', 'zollikerberg', 'aggregated'];
const ENVS: readonly AppEnv[] = ['dev', 'sit', 'prod'];

function normalizeRoles(roles: RawClaims['roles']): string[] {
  if (!roles) return [];
  if (Array.isArray(roles)) return roles.filter((r) => typeof r === 'string');
  // Some tokens emit a single space- or comma-delimited string.
  return roles
    .split(/[,\s]+/)
    .map((r) => r.trim())
    .filter(Boolean);
}

function coerceHospital(value: string | undefined): Hospital {
  const v = (value ?? '').toLowerCase();
  return HOSPITALS.includes(v as Hospital) ? (v as Hospital) : 'aggregated';
}

function coerceEnv(value: string | undefined): AppEnv {
  const v = (value ?? '').toLowerCase();
  return ENVS.includes(v as AppEnv) ? (v as AppEnv) : 'dev';
}

/**
 * Parse raw claims into a normalized shape. Unknown/missing hospital falls back
 * to `aggregated` (least data exposure), unknown env falls back to `dev`.
 */
export function parseClaims(raw: RawClaims | null | undefined): ParsedClaims {
  return {
    roles: normalizeRoles(raw?.roles),
    hospital: coerceHospital(raw?.hospital),
    env: coerceEnv(raw?.env),
    name: raw?.name,
    oid: raw?.oid,
  };
}

/** True when the caller holds at least one of the given roles. */
export function hasAnyRole(claims: ParsedClaims, roles: string[]): boolean {
  return roles.some((r) => claims.roles.includes(r));
}
