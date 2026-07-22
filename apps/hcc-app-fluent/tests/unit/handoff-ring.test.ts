import { describe, expect, it } from 'vitest';
import { GOLDEN_THREAD_SCOPE, SEED_SITUATION } from '../../src/journey/golden-thread';
import { residualFromPrev } from '../../src/journey/handoff-orchestrator';

describe('golden-thread residual ring', () => {
  it('starts ooa-agent from the seed situation in demo mode', async () => {
    await expect(residualFromPrev('ooa-agent', GOLDEN_THREAD_SCOPE, 'demo'))
      .resolves.toEqual(SEED_SITUATION);
  });

  it.each([
    ['dca-agent', 'ooa-agent'],
    ['bmca-agent', 'dca-agent'],
    ['orsa-agent', 'bmca-agent'],
    ['sba-agent', 'orsa-agent'],
    ['csa-agent', 'sba-agent'],
  ] as const)('carries residual pressure into %s from %s', async (agent, expectedFromAgent) => {
    const residual = await residualFromPrev(agent, GOLDEN_THREAD_SCOPE, 'demo');

    expect(residual?.fromAgent).toBe(expectedFromAgent);
  });

  it('does not carry the demo chain in user mode', async () => {
    await expect(residualFromPrev('bmca-agent', GOLDEN_THREAD_SCOPE, 'user'))
      .resolves.toBeNull();
  });
});
