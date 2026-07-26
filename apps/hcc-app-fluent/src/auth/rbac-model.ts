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
  | 'HCC.SuperAdmin'
  | 'HCC.PlatformAdmin'
  | 'HCC.DemoOperator'
  | 'HCC.CrisisManager'
  | 'HCC.RegionalCrisisLead'
  | 'HCC.OperationsLead'
  | 'HCC.BedManager'
  | 'HCC.FlowManager'
  | 'HCC.EDLead'
  | 'HCC.ORCoordinator'
  | 'HCC.StaffingCoordinator'
  | 'HCC.DischargeCoordinator'
  | 'HCC.OntologySteward'
  | 'HCC.Executive'
  | 'HCC.CantonalViewer'
  | 'HCC.AIGovernance'
  | 'HCC.Auditor'
  | 'HCC.GuestReadOnly'
  | 'HCC.Viewer';

export interface RoleCapabilities {
  hospitalScope: HospitalScope | 'own-site';
  agentCeiling: AgentCeiling;
  nav: { start: boolean; main: boolean; csa: boolean; backstage: boolean; settings: boolean };
}

/**
 * Capability tiers for the real Entra app roles (`data/entra/app-roles.csv`),
 * grouped by the master-data `category`. `HCC.RegionalCrisisLead` and
 * `HCC.Viewer` are retained as back-compat aliases (the real equivalents are
 * `HCC.CrisisManager` / `HCC.GuestReadOnly`). Ceilings + nav are demo defaults
 * (simulated data, no PHI, ADR-0013): operational roles are single-site + write,
 * governance is aggregated + read, super / admin / crisis are elevated.
 */
export const ROLE_MAP: Record<HccRole, RoleCapabilities> = {
  // super
  'HCC.SuperAdmin':           { hospitalScope: 'aggregated', agentCeiling: 'deploy', nav: { start: true, main: true, csa: true,  backstage: true,  settings: true } },
  'HCC.GuestReadOnly':        { hospitalScope: 'aggregated', agentCeiling: 'read',   nav: { start: true, main: true, csa: false, backstage: true,  settings: false } },
  // governance / admin
  'HCC.PlatformAdmin':        { hospitalScope: 'aggregated', agentCeiling: 'deploy', nav: { start: true, main: true, csa: true,  backstage: true,  settings: true } },
  'HCC.DemoOperator':         { hospitalScope: 'aggregated', agentCeiling: 'write',  nav: { start: true, main: true, csa: true,  backstage: true,  settings: true } },
  'HCC.Executive':            { hospitalScope: 'aggregated', agentCeiling: 'read',   nav: { start: true, main: true, csa: false, backstage: true,  settings: false } },
  'HCC.CantonalViewer':       { hospitalScope: 'aggregated', agentCeiling: 'read',   nav: { start: true, main: true, csa: false, backstage: false, settings: false } },
  'HCC.OntologySteward':      { hospitalScope: 'aggregated', agentCeiling: 'write',  nav: { start: true, main: true, csa: false, backstage: true,  settings: false } },
  'HCC.AIGovernance':         { hospitalScope: 'aggregated', agentCeiling: 'read',   nav: { start: true, main: true, csa: false, backstage: true,  settings: false } },
  'HCC.Auditor':              { hospitalScope: 'aggregated', agentCeiling: 'read',   nav: { start: true, main: true, csa: false, backstage: true,  settings: false } },
  // crisis
  'HCC.CrisisManager':        { hospitalScope: 'aggregated', agentCeiling: 'deploy', nav: { start: true, main: true, csa: true,  backstage: false, settings: false } },
  'HCC.RegionalCrisisLead':   { hospitalScope: 'aggregated', agentCeiling: 'deploy', nav: { start: true, main: true, csa: true,  backstage: true,  settings: false } },
  // operational (single-site, write)
  'HCC.OperationsLead':       { hospitalScope: 'own-site',   agentCeiling: 'write',  nav: { start: true, main: true, csa: false, backstage: false, settings: false } },
  'HCC.BedManager':           { hospitalScope: 'own-site',   agentCeiling: 'write',  nav: { start: true, main: true, csa: false, backstage: false, settings: false } },
  'HCC.FlowManager':          { hospitalScope: 'own-site',   agentCeiling: 'write',  nav: { start: true, main: true, csa: false, backstage: false, settings: false } },
  'HCC.EDLead':               { hospitalScope: 'own-site',   agentCeiling: 'write',  nav: { start: true, main: true, csa: false, backstage: false, settings: false } },
  'HCC.ORCoordinator':        { hospitalScope: 'own-site',   agentCeiling: 'write',  nav: { start: true, main: true, csa: false, backstage: false, settings: false } },
  'HCC.StaffingCoordinator':  { hospitalScope: 'own-site',   agentCeiling: 'write',  nav: { start: true, main: true, csa: false, backstage: false, settings: false } },
  'HCC.DischargeCoordinator': { hospitalScope: 'own-site',   agentCeiling: 'write',  nav: { start: true, main: true, csa: false, backstage: false, settings: false } },
  // read-only (legacy alias)
  'HCC.Viewer':               { hospitalScope: 'aggregated', agentCeiling: 'read',   nav: { start: true, main: true, csa: false, backstage: true,  settings: false } },
};

const RANK: HccRole[] = [
  'HCC.Viewer', 'HCC.GuestReadOnly', 'HCC.CantonalViewer', 'HCC.Auditor', 'HCC.AIGovernance', 'HCC.Executive',
  'HCC.BedManager', 'HCC.FlowManager', 'HCC.EDLead', 'HCC.ORCoordinator', 'HCC.StaffingCoordinator',
  'HCC.DischargeCoordinator', 'HCC.OperationsLead', 'HCC.OntologySteward',
  'HCC.DemoOperator', 'HCC.CrisisManager', 'HCC.RegionalCrisisLead', 'HCC.PlatformAdmin', 'HCC.SuperAdmin',
];

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

/** Highest-ranked role among those held — the default active lens. */
export function highestRole(held: HccRole[]): HccRole {
  return [...held].sort((a, b) => RANK.indexOf(a) - RANK.indexOf(b)).pop() ?? held[0] ?? 'HCC.Viewer';
}
