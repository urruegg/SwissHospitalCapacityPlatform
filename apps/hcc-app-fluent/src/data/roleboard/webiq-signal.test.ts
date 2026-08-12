import { describe, it, expect } from 'vitest';
import { OCCUPANCY_SIGNALS } from './occupancy-data';
import { CRISIS_PINNED } from './crisis-data';

describe('Web IQ signal (Sprint 44, Trust-B, advisory-only)', () => {
  it('is present on the OOA panel as an external Trust-B channel with web citations', () => {
    const webiq = OCCUPANCY_SIGNALS.find((sig) => sig.id === 'webiq');
    expect(webiq).toBeDefined();
    expect(webiq!.scope).toBe('external');
    expect(webiq!.trustClass).toBe('Trust-B');
    expect(webiq!.webCitations?.length).toBeGreaterThan(0);
    expect(webiq!.webCitations![0].uri).toMatch(/^https:\/\//);
  });

  it('is present on the CSA board as a filtered (no-lever) Trust-B signal', () => {
    const webiq = CRISIS_PINNED.signals.find((sig) => sig.id === 'webiq-outbreak');
    expect(webiq).toBeDefined();
    expect(webiq!.source).toBe('Microsoft Web IQ');
    expect(webiq!.trustClass).toBe('Trust-B');
    expect(webiq!.filtered).toBe(true); // renders but does NOT arm a lever (ADR-0036)
    expect(webiq!.feedsLever).toBeUndefined(); // Trust-B never feeds a lever
  });
});
