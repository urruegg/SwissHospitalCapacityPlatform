import { buildEnvelope } from '../../src/context/context-envelope';
import type { ContextEnvelope } from '../../src/context/context-envelope';
import { applyRlsScope, rlsScopeOf } from '../../src/data/roleboard/rls-scope';
import type { HospitalScope } from '../../src/auth/rbac-model';

const rows = [
  { hospital: 'usz', ward: 'Med A', beds: 12 },
  { hospital: 'usz', ward: 'Med B', beds: 8 },
  { hospital: 'luks', ward: 'Surg', beds: 5 },
  { hospital: 'zollikerberg', ward: 'Geri', beds: 3 },
] as const;

function envelopeFor(hospitalScope: HospitalScope): ContextEnvelope {
  return {
    userOid: 'oid-rls-user',
    heldRoles: hospitalScope === 'aggregated' ? ['HCC.RegionalCrisisLead'] : ['HCC.BedManager'],
    activeRole: hospitalScope === 'aggregated' ? 'HCC.RegionalCrisisLead' : 'HCC.BedManager',
    hospitalScope,
    dataSource: 'simulated',
    agent: 'bmca-agent',
    windowHours: 72,
  };
}

describe('applyRlsScope', () => {
  it('returns only the signed-in single-site user hospital rows', () => {
    const scoped = applyRlsScope(rows, envelopeFor('usz'));

    expect(scoped).toEqual([
      { hospital: 'usz', ward: 'Med A', beds: 12 },
      { hospital: 'usz', ward: 'Med B', beds: 8 },
    ]);
    expect(rlsScopeOf(envelopeFor('usz'))).toBe('usz');
  });

  it('returns every row for an aggregated cross-hospital role', () => {
    const scoped = applyRlsScope(rows, envelopeFor('aggregated'));

    expect(scoped).toEqual([...rows]);
    expect(scoped).not.toBe(rows);
    expect(rlsScopeOf(envelopeFor('aggregated'))).toBe('aggregated');
  });

  it('denies a wholly missing envelope by default', () => {
    expect(applyRlsScope(rows, null)).toEqual([]);
    expect(rlsScopeOf(null)).toBe('denied');
  });

  it('keeps the least-privilege built envelope distinct from a missing envelope', () => {
    const leastPrivilegeEnvelope = buildEnvelope(null, null);

    expect(leastPrivilegeEnvelope.hospitalScope).toBe('aggregated');
    expect(applyRlsScope(rows, leastPrivilegeEnvelope)).toEqual([...rows]);
    expect(rlsScopeOf(leastPrivilegeEnvelope)).toBe('aggregated');
  });

  it('applies the same single-site isolation to another hospital', () => {
    const scoped = applyRlsScope(rows, envelopeFor('luks'));

    expect(scoped).toEqual([{ hospital: 'luks', ward: 'Surg', beds: 5 }]);
    expect(rlsScopeOf(envelopeFor('luks'))).toBe('luks');
  });
});
