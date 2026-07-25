import { ROLE_MAP, deriveCapabilities, narrowRoles } from '../../src/auth/rbac-model';

describe('rbac model', () => {
  it('maps a bed manager to own-site scope and write ceiling', () => {
    const caps = deriveCapabilities('HCC.BedManager', 'usz');
    expect(caps.hospitalScope).toBe('usz');
    expect(caps.agentCeiling).toBe('write');
    expect(caps.nav.settings).toBe(false);
  });

  it('maps a viewer to aggregated scope and read-only', () => {
    const caps = deriveCapabilities('HCC.Viewer', 'usz');
    expect(caps.hospitalScope).toBe('aggregated');
    expect(caps.agentCeiling).toBe('read');
  });

  it('narrowing only keeps roles the user actually holds', () => {
    expect(narrowRoles(['HCC.Viewer'], 'HCC.PlatformAdmin')).toBe('HCC.Viewer');
    expect(narrowRoles(['HCC.PlatformAdmin', 'HCC.Viewer'], 'HCC.Viewer')).toBe('HCC.Viewer');
  });

  it('ROLE_MAP covers the real Entra app roles plus legacy aliases', () => {
    const keys = Object.keys(ROLE_MAP);
    // real app roles (data/entra/app-roles.csv)
    expect(keys).toContain('HCC.SuperAdmin');
    expect(keys).toContain('HCC.OperationsLead');
    expect(keys).toContain('HCC.CrisisManager');
    expect(keys).toContain('HCC.GuestReadOnly');
    expect(keys).toContain('HCC.OntologySteward');
    // legacy aliases retained for back-compat
    expect(keys).toContain('HCC.RegionalCrisisLead');
    expect(keys).toContain('HCC.Viewer');
    expect(keys).toHaveLength(19);
  });
});
