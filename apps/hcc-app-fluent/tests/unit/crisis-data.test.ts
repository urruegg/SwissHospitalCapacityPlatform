import { describe, it, expect } from 'vitest';
import {
  CERTAINTY_TO_PROBABILITY,
  certaintyToProbability,
  sortScenarios,
  CRISIS_PINNED,
} from '../../src/data/roleboard/crisis-data';

describe('CERTAINTY_TO_PROBABILITY mapping', () => {
  it('maps Likely → 68', () => {
    expect(CERTAINTY_TO_PROBABILITY.Likely).toBe(68);
    expect(certaintyToProbability('Likely')).toBe(68);
  });

  it('maps Possible → 31', () => {
    expect(CERTAINTY_TO_PROBABILITY.Possible).toBe(31);
    expect(certaintyToProbability('Possible')).toBe(31);
  });

  it('maps Unlikely → 6', () => {
    expect(CERTAINTY_TO_PROBABILITY.Unlikely).toBe(6);
    expect(certaintyToProbability('Unlikely')).toBe(6);
  });
});

describe('CRISIS_PINNED payload', () => {
  it('has residualBeds = 0 (golden-thread sba→csa steady-state)', () => {
    expect(CRISIS_PINNED.residualBeds).toBe(0);
  });

  it('has at least one filtered/quarantined signal that renders but arms no lever', () => {
    const filtered = CRISIS_PINNED.signals.filter((s) => s.filtered);
    expect(filtered.length).toBeGreaterThanOrEqual(1);
  });

  it('filtered signal probability is derived from its certainty', () => {
    const filtered = CRISIS_PINNED.signals.find((s) => s.filtered);
    expect(filtered).toBeDefined();
    expect(filtered!.probability).toBe(certaintyToProbability(filtered!.certainty));
  });

  it('signals are Trust-A or Trust-B; Trust-B is filtered and never feeds a lever (ADR-0036/0060)', () => {
    for (const signal of CRISIS_PINNED.signals) {
      expect(['Trust-A', 'Trust-B']).toContain(signal.trustClass);
      if (signal.trustClass === 'Trust-B') {
        expect(signal.filtered).toBe(true);
        expect(signal.feedsLever).toBeUndefined();
      }
    }
  });

  it('scenarios are ranked by probability desc with stable id tie-break', () => {
    const sorted = sortScenarios(CRISIS_PINNED.scenarios);
    for (let i = 1; i < sorted.length; i++) {
      const prev = sorted[i - 1];
      const curr = sorted[i];
      if (prev.probability === curr.probability) {
        expect(prev.id.localeCompare(curr.id)).toBeLessThanOrEqual(0);
      } else {
        expect(prev.probability).toBeGreaterThan(curr.probability);
      }
    }
  });

  it('top scenario is heatwave-surge at probability 68', () => {
    const sorted = sortScenarios(CRISIS_PINNED.scenarios);
    expect(sorted[0].id).toBe('heatwave-surge');
    expect(sorted[0].probability).toBe(68);
  });

  it('recoById has an entry for each scenario', () => {
    for (const scenario of CRISIS_PINNED.scenarios) {
      expect(CRISIS_PINNED.recoById[scenario.id]).toBeDefined();
    }
  });

  it('scenario recos have requiresApproval: true (deploy-ceiling approval gate)', () => {
    for (const scenario of CRISIS_PINNED.scenarios) {
      const reco = CRISIS_PINNED.recoById[scenario.id];
      expect(reco.primaryCta?.requiresApproval).toBe(true);
    }
  });

  it('filtered signal reco is refused: true (DC-EXT-SIGNAL-v1 quarantine gate)', () => {
    const filtered = CRISIS_PINNED.signals.find((s) => s.filtered);
    expect(filtered).toBeDefined();
    const reco = CRISIS_PINNED.recoById[filtered!.id];
    expect(reco).toBeDefined();
    expect(reco.refused).toBe(true);
  });

  it('filtered signal does NOT arm a lever — no non-refused reco references the filtered signal id as its key', () => {
    const filteredIds = new Set(CRISIS_PINNED.signals.filter((s) => s.filtered).map((s) => s.id));
    for (const id of filteredIds) {
      const reco = CRISIS_PINNED.recoById[id];
      if (reco) {
        // Must be refused — cannot arm a lever
        expect(reco.refused).toBe(true);
      }
    }
  });

  it('defaultReco has provenance simulated', () => {
    expect(CRISIS_PINNED.defaultReco.provenance).toBe('simulated');
  });

  it('sortScenarios is stable for equal probabilities (tie-break by id)', () => {
    const tied = [
      { id: 'z-scenario', name: 'Z', bedImpact: 1, isSpof: false, probability: 50 },
      { id: 'a-scenario', name: 'A', bedImpact: 1, isSpof: false, probability: 50 },
    ];
    const sorted = sortScenarios(tied);
    expect(sorted[0].id).toBe('a-scenario');
    expect(sorted[1].id).toBe('z-scenario');
  });
});
