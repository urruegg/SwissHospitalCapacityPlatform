import { describe, it, expect } from 'vitest';
import { parseClaims, hasAnyRole } from '../../src/auth/claim-parser';
import { canSwitchRole } from '../../src/context/role-context';
import { envFromHost } from '../../src/auth/env-detection';

describe('parseClaims', () => {
  it('normalizes array roles and known hospital/env', () => {
    const c = parseClaims({
      roles: ['HCC.PlatformAdmin', 'HCC.BedManager'],
      hospital: 'USZ',
      env: 'sit',
      name: 'Demo',
    });
    expect(c.roles).toContain('HCC.PlatformAdmin');
    expect(c.hospital).toBe('usz');
    expect(c.env).toBe('sit');
  });

  it('splits a delimited role string', () => {
    const c = parseClaims({ roles: 'HCC.A HCC.B,HCC.C' });
    expect(c.roles).toEqual(['HCC.A', 'HCC.B', 'HCC.C']);
  });

  it('falls back to aggregated hospital and dev env on unknown/missing values', () => {
    const c = parseClaims({ roles: [], hospital: 'unknown', env: 'weird' });
    expect(c.hospital).toBe('aggregated');
    expect(c.env).toBe('dev');
  });

  it('treats null claims as an anonymous aggregated/dev session', () => {
    const c = parseClaims(null);
    expect(c.roles).toEqual([]);
    expect(c.hospital).toBe('aggregated');
    expect(c.env).toBe('dev');
  });
});

describe('hasAnyRole', () => {
  it('returns true when at least one role matches', () => {
    const c = parseClaims({ roles: ['HCC.DemoOperator'] });
    expect(hasAnyRole(c, ['HCC.PlatformAdmin', 'HCC.DemoOperator'])).toBe(true);
    expect(hasAnyRole(c, ['HCC.PlatformAdmin'])).toBe(false);
  });
});

describe('canSwitchRole (role switcher gate)', () => {
  it('is visible only in SIT with an admin/operator role', () => {
    expect(canSwitchRole(parseClaims({ roles: ['HCC.PlatformAdmin'], env: 'sit' }))).toBe(true);
    expect(canSwitchRole(parseClaims({ roles: ['HCC.DemoOperator'], env: 'sit' }))).toBe(true);
  });

  it('is hidden in PROD even with the role', () => {
    expect(canSwitchRole(parseClaims({ roles: ['HCC.PlatformAdmin'], env: 'prod' }))).toBe(false);
  });

  it('is hidden in SIT without the role', () => {
    expect(canSwitchRole(parseClaims({ roles: ['HCC.BedManager'], env: 'sit' }))).toBe(false);
  });
});

describe('envFromHost', () => {
  it('detects sit and prod slots from the host name', () => {
    expect(envFromHost('hcc-app-fluent-sit.azurecontainerapps.io')).toBe('sit');
    expect(envFromHost('hcc-app-fluent-prod.azurecontainerapps.io')).toBe('prod');
    expect(envFromHost('localhost')).toBe('dev');
  });
});
