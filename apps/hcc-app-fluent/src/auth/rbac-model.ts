/**
 * Sprint 20 M3 — RBAC role model.
 *
 * The active role is an access lens: it derives the hospital data scope, the
 * agent side-effect ceiling, and per-destination navigation capability from the
 * five demo roles issued by the `ihzhhpf-app` registration. In-session role
 * switching may only NARROW to a role the user actually holds (never elevate).
 */

export type AgentCeiling = 'read' | 'write' | 'deploy';
export type HospitalScope = 'usz' | 'luks' | 'zollikerberg' | 'aggregated';
export type HccRole =
  | 'HCC.PlatformAdmin'
  | 'HCC.DemoOperator'
  | 'HCC.RegionalCrisisLead'
  | 'HCC.BedManager'
  | 'HCC.Viewer';

export interface RoleCapabilities {
  hospitalScope: HospitalScope | 'own-site';
  agentCeiling: AgentCeiling;
  nav: { start: boolean; main: boolean; csa: boolean; backstage: boolean; settings: boolean };
}

export const ROLE_MAP: Record<HccRole, RoleCapabilities> = {
  'HCC.PlatformAdmin':      { hospitalScope: 'aggregated', agentCeiling: 'deploy', nav: { start: true, main: true, csa: true,  backstage: true,  settings: true } },
  'HCC.DemoOperator':       { hospitalScope: 'aggregated', agentCeiling: 'write',  nav: { start: true, main: true, csa: true,  backstage: true,  settings: true } },
  'HCC.RegionalCrisisLead': { hospitalScope: 'aggregated', agentCeiling: 'deploy', nav: { start: true, main: true, csa: true,  backstage: true,  settings: false } },
  'HCC.BedManager':         { hospitalScope: 'own-site',   agentCeiling: 'write',  nav: { start: true, main: true, csa: false, backstage: false, settings: false } },
  'HCC.Viewer':             { hospitalScope: 'aggregated', agentCeiling: 'read',   nav: { start: true, main: true, csa: false, backstage: true,  settings: false } },
};

const RANK: HccRole[] = ['HCC.Viewer', 'HCC.BedManager', 'HCC.DemoOperator', 'HCC.RegionalCrisisLead', 'HCC.PlatformAdmin'];

/** True when the given string is one of the five mapped demo roles. */
export function isHccRole(role: string): role is HccRole {
  return role in ROLE_MAP;
}

export function deriveCapabilities(
  role: HccRole,
  homeSite: HospitalScope,
): RoleCapabilities & { hospitalScope: HospitalScope } {
  const base = ROLE_MAP[role];
  const scope = base.hospitalScope === 'own-site' ? homeSite : base.hospitalScope;
  return { ...base, hospitalScope: scope };
}

/**
 * Narrow-only switch: returns `requested` if the user holds it, otherwise the
 * highest-ranked role they actually hold (never elevates beyond held roles).
 */
export function narrowRoles(held: HccRole[], requested: HccRole): HccRole {
  if (held.includes(requested)) return requested;
  return [...held].sort((a, b) => RANK.indexOf(a) - RANK.indexOf(b)).pop() ?? held[0];
}
