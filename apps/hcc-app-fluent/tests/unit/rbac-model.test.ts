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

  it('keys of ROLE_MAP cover the five demo roles', () => {
    expect(Object.keys(ROLE_MAP).sort()).toEqual(
      ['HCC.BedManager', 'HCC.DemoOperator', 'HCC.PlatformAdmin', 'HCC.RegionalCrisisLead', 'HCC.Viewer'],
    );
  });
});
