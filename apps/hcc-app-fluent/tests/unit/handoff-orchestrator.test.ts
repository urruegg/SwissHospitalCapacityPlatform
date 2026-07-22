import { describe, expect, it } from 'vitest';
import { ROLE_SEQUENCE, SEED_SITUATION, nextAgent } from '../../src/journey/golden-thread';
import { bannerFor } from '../../src/journey/handoff-orchestrator';

describe('handoff orchestrator', () => {
  it('advances the golden-thread sequence and loops csa back to ooa', () => {
    expect(ROLE_SEQUENCE).toEqual([
      'ooa-agent',
      'dca-agent',
      'bmca-agent',
      'orsa-agent',
      'sba-agent',
      'csa-agent',
    ]);
    expect(nextAgent('ooa-agent')).toBe('dca-agent');
    expect(nextAgent('csa-agent')).toBe('ooa-agent');
  });

  it('carries the residual pressure forward in demo mode', () => {
    const banner = bannerFor('demo', 'dca-agent', SEED_SITUATION);
    expect(banner.situation).toContain('102%');
    expect(banner.loopBackToOoa).toBe(true);
  });

  it('closes the loop-back flag off for the ooa surface itself', () => {
    const banner = bannerFor('demo', 'ooa-agent', null);
    expect(banner.loopBackToOoa).toBe(false);
  });

  it('shows real context only (no scripted chain) in user mode', () => {
    const banner = bannerFor('user', 'dca-agent', SEED_SITUATION);
    expect(banner.loopBackToOoa).toBe(false);
    expect(banner.situation).not.toContain('->');
  });
});
