import { describe, it, expect } from 'vitest';
import { DISCHARGE_PINNED } from '../../src/data/roleboard/discharge-data';

describe('DISCHARGE_PINNED model', () => {
  it('keeps the golden-thread residual chain: bedsNeeded=16, bedsFreeable=9, residualBeds=-7', () => {
    expect(DISCHARGE_PINNED.bedsNeeded).toBe(16);
    expect(DISCHARGE_PINNED.bedsFreeable).toBe(9);
    expect(DISCHARGE_PINNED.residualBeds).toBe(-7);
  });

  it('has candidates with PHI-safe patientId (PT-xxxx), readiness, estFreeHours, recoId', () => {
    expect(DISCHARGE_PINNED.candidates.length).toBeGreaterThanOrEqual(3);
    for (const c of DISCHARGE_PINNED.candidates) {
      expect(c.patientId).toMatch(/^PT-\d+$/);
      expect(['READY', 'BLOCKED', 'PENDING']).toContain(c.readiness);
      expect(c.estFreeHours).toBeGreaterThan(0);
      expect(typeof c.bedsFreeable).toBe('number');
      expect(c.recoId).toBeTruthy();
    }
  });

  it('includes at least one READY and one PENDING candidate', () => {
    const statuses = DISCHARGE_PINNED.candidates.map((c) => c.readiness);
    expect(statuses).toContain('READY');
    expect(statuses).toContain('PENDING');
  });

  it('has barriers sorted by bedImpact descending', () => {
    const impacts = DISCHARGE_PINNED.barriers.map((b) => b.bedImpact);
    expect(impacts.length).toBeGreaterThanOrEqual(2);
    for (let i = 1; i < impacts.length; i++) {
      expect(impacts[i - 1]).toBeGreaterThanOrEqual(impacts[i]);
    }
  });

  it('has a defaultReco with non-empty levers, a CTA, gold citations, and simulated provenance', () => {
    const { defaultReco } = DISCHARGE_PINNED;
    expect(defaultReco.levers.length).toBeGreaterThan(0);
    expect(defaultReco.primaryCta).toBeDefined();
    expect(defaultReco.citations).toContain('gold.discharge_candidates');
    expect(defaultReco.provenance).toBe('simulated');
  });

  it('has recoById entries for all READY candidates with non-empty levers', () => {
    const ready = DISCHARGE_PINNED.candidates.filter((c) => c.readiness === 'READY');
    expect(ready.length).toBeGreaterThan(0);
    for (const c of ready) {
      const reco = DISCHARGE_PINNED.recoById[c.recoId];
      expect(reco).toBeDefined();
      expect(reco.levers.length).toBeGreaterThan(0);
      expect(reco.provenance).toBe('simulated');
      expect(reco.citations.some((ci) => ci.startsWith('gold.'))).toBe(true);
    }
  });
});
