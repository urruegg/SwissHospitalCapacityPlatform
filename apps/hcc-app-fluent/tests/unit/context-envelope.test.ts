import { buildEnvelope, DEFAULT_WINDOW_HOURS } from '../../src/context/context-envelope';
import type { RoleLensLike } from '../../src/context/context-envelope';
import type { ParsedClaims } from '../../src/auth/claim-parser';

const claims: ParsedClaims = {
  roles: ['HCC.BedManager', 'HCC.Viewer'],
  hospital: 'usz',
  env: 'sit',
  name: 'Bea Manager',
  oid: 'oid-123',
};

const bedManagerLens: RoleLensLike = {
  heldRoles: ['HCC.BedManager', 'HCC.Viewer'],
  activeRole: 'HCC.BedManager',
  capabilities: { hospitalScope: 'usz' },
};

describe('buildEnvelope', () => {
  it('builds a full envelope from claims + active role lens', () => {
    const env = buildEnvelope(claims, bedManagerLens, 'simulated', 'bmca-agent', 72);
    expect(env).toEqual({
      userOid: 'oid-123',
      heldRoles: ['HCC.BedManager', 'HCC.Viewer'],
      activeRole: 'HCC.BedManager',
      hospitalScope: 'usz',
      dataSource: 'simulated',
      agent: 'bmca-agent',
      windowHours: 72,
    });
  });

  it('carries the active role, not the highest held role', () => {
    const lens: RoleLensLike = {
      heldRoles: ['HCC.PlatformAdmin', 'HCC.Viewer'],
      activeRole: 'HCC.Viewer',
      capabilities: { hospitalScope: 'aggregated' },
    };
    const env = buildEnvelope(claims, lens, 'live', 'ooa-agent');
    expect(env.activeRole).toBe('HCC.Viewer');
    expect(env.heldRoles).toEqual(['HCC.PlatformAdmin', 'HCC.Viewer']);
    expect(env.dataSource).toBe('live');
  });

  it('defaults windowHours and simulated data source, null agent', () => {
    const env = buildEnvelope(claims, bedManagerLens);
    expect(env.windowHours).toBe(DEFAULT_WINDOW_HOURS);
    expect(env.dataSource).toBe('simulated');
    expect(env.agent).toBeNull();
  });

  it('falls back to least privilege when the lens is missing', () => {
    const env = buildEnvelope(claims, null, 'live', 'csa-agent');
    expect(env.activeRole).toBe('HCC.Viewer');
    expect(env.heldRoles).toEqual(['HCC.Viewer']);
    expect(env.hospitalScope).toBe('aggregated');
    // identity still preserved from claims
    expect(env.userOid).toBe('oid-123');
  });

  it('falls back to least privilege when claims are missing (no oid)', () => {
    const env = buildEnvelope(null, null);
    expect(env.userOid).toBeNull();
    expect(env.activeRole).toBe('HCC.Viewer');
    expect(env.heldRoles).toEqual(['HCC.Viewer']);
    expect(env.hospitalScope).toBe('aggregated');
    expect(env.dataSource).toBe('simulated');
    expect(env.agent).toBeNull();
    expect(env.windowHours).toBe(DEFAULT_WINDOW_HOURS);
  });
});
