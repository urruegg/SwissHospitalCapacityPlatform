import { describe, expect, it } from 'vitest';
import { FEEDBACK_LOOP_DOMAINS, IQ_LAYERS } from './feedback-loop-model';

describe('feedback-loop catalog', () => {
  it('defines four unique domains and all five Microsoft IQ layers', () => {
    expect(FEEDBACK_LOOP_DOMAINS).toHaveLength(4);
    expect(new Set(FEEDBACK_LOOP_DOMAINS.map(({ id }) => id)).size).toBe(4);
    expect(IQ_LAYERS).toEqual([
      'work',
      'foundry',
      'fabric',
      'process',
      'governance',
    ]);
  });

  it('provides a complete, non-PHI context for every domain', () => {
    for (const domain of FEEDBACK_LOOP_DOMAINS) {
      expect(domain.signalIds.length).toBeGreaterThan(0);
      expect(domain.proposedActionId).toBeTruthy();
      expect(domain.outcomeId).toBeTruthy();
      expect(domain.iqLayers.length).toBeGreaterThan(0);
      expect(JSON.stringify(domain)).not.toMatch(/patient|person|birth|mrn/i);
    }
  });
});
