import { describe, it, expect } from 'vitest';
import { BEDMANAGER_PINNED, BED_MANAGER_PINNED } from '../../src/data/roleboard/bed-manager-data';

describe('BEDMANAGER_PINNED model', () => {
  it('keeps the golden-thread residual chain: bedsShort=7, bedsReallocated=4, residualBeds=-3', () => {
    expect(BEDMANAGER_PINNED.bedsShort).toBe(7);
    expect(BEDMANAGER_PINNED.bedsReallocated).toBe(4);
    expect(BEDMANAGER_PINNED.residualBeds).toBe(-3);
  });

  it('BED_MANAGER_PINNED is the backward-compat alias for BEDMANAGER_PINNED', () => {
    expect(BED_MANAGER_PINNED).toBe(BEDMANAGER_PINNED);
  });

  it('has placement requests with PHI-safe patientId (PT-xxxx), priority, and recoId', () => {
    expect(BEDMANAGER_PINNED.placements.length).toBeGreaterThanOrEqual(3);
    for (const p of BEDMANAGER_PINNED.placements) {
      expect(p.patientId).toMatch(/^PT-\d+$/);
      expect(['HIGH', 'MED', 'LOW']).toContain(p.priority);
      expect(p.waitMin).toBeGreaterThan(0);
      expect(p.recoId).toBeTruthy();
      expect(p.fromWard).toBeTruthy();
      expect(p.toWard).toBeTruthy();
    }
  });

  it('has at least one HIGH and one LOW priority placement', () => {
    const priorities = BEDMANAGER_PINNED.placements.map((p) => p.priority);
    expect(priorities).toContain('HIGH');
    expect(priorities).toContain('LOW');
  });

  it('has barriers sorted by bedImpact descending (stable tie-break)', () => {
    const impacts = BEDMANAGER_PINNED.barriers.map((b) => b.bedImpact);
    expect(impacts.length).toBeGreaterThanOrEqual(2);
    for (let i = 1; i < impacts.length; i++) {
      expect(impacts[i - 1]).toBeGreaterThanOrEqual(impacts[i]);
    }
  });

  it('has bed-state KPIs: utilPct, freeBeds, targetFree, slaRisk', () => {
    expect(BEDMANAGER_PINNED.utilPct).toBeGreaterThan(0);
    expect(BEDMANAGER_PINNED.freeBeds).toBeGreaterThan(0);
    expect(BEDMANAGER_PINNED.targetFree).toBeGreaterThan(0);
    expect(['HIGH', 'MED', 'LOW', 'OK']).toContain(BEDMANAGER_PINNED.slaRisk);
  });

  it('has admissions eventstream with both admit and discharge events', () => {
    const kinds = BEDMANAGER_PINNED.admissions.map((e) => e.kind);
    expect(kinds).toContain('admit');
    expect(kinds).toContain('discharge');
    for (const ev of BEDMANAGER_PINNED.admissions) {
      expect(ev.id).toBeTruthy();
      expect(ev.ts).toBeTruthy();
      expect(ev.message).toBeTruthy();
    }
  });

  it('has a Power BI embed with reportName and embedPlaceholder', () => {
    expect(BEDMANAGER_PINNED.powerBiEmbed.reportName).toBe('capacity-dashboard');
    expect(BEDMANAGER_PINNED.powerBiEmbed.embedPlaceholder).toBeTruthy();
  });

  it('HITL move reco has requiresApproval: true on its primaryCta', () => {
    const hitlReco = BEDMANAGER_PINNED.recoById['move-pt-4003-hitl'];
    expect(hitlReco).toBeDefined();
    expect(hitlReco.primaryCta?.requiresApproval).toBe(true);
  });

  it('refused reco exists with refused: true (blocked move awaiting approval)', () => {
    const refusedReco = BEDMANAGER_PINNED.recoById['move-pt-4004-refused'];
    expect(refusedReco).toBeDefined();
    expect(refusedReco.refused).toBe(true);
  });

  it('has a defaultReco with non-empty levers, a handoff CTA, gold citations, and simulated provenance', () => {
    const { defaultReco } = BEDMANAGER_PINNED;
    expect(defaultReco.levers.length).toBeGreaterThan(0);
    expect(defaultReco.primaryCta).toBeDefined();
    expect(defaultReco.primaryCta?.kind).toBe('handoff');
    expect(defaultReco.citations).toContain('gold.bed_assignment');
    expect(defaultReco.citations).toContain('gold.fact_capacity_baseline');
    expect(defaultReco.provenance).toBe('simulated');
  });

  it('recoById has entries for all placements with non-empty levers or refused flag', () => {
    for (const p of BEDMANAGER_PINNED.placements) {
      const reco = BEDMANAGER_PINNED.recoById[p.recoId];
      expect(reco).toBeDefined();
      const hasLeversOrRefused = reco.levers.length > 0 || reco.refused === true;
      expect(hasLeversOrRefused).toBe(true);
      expect(reco.provenance).toBe('simulated');
      expect(reco.citations.some((c) => c.startsWith('gold.'))).toBe(true);
    }
  });

  it('contains no PHI identifiers in serialized form', () => {
    const serialized = JSON.stringify(BEDMANAGER_PINNED).toLowerCase();
    expect(serialized).not.toMatch(/\bahv\b|\bgeburtsdatum\b|\bdob\b|\bssn\b/);
    // Patient IDs are synthetic PT-xxxx tokens only
    const patientMatches = serialized.match(/"pt-\d+"/g) ?? [];
    for (const m of patientMatches) {
      expect(m).toMatch(/^"pt-\d+"$/);
    }
  });
});
