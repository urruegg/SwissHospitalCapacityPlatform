import type { AgentId, BannerContext, Mode, ResidualPressure } from './RoleBoard';

/**
 * Sprint 1 (parity) — compute the handoff banner for a surface.
 * Demo: carry the prior role's residual pressure forward and keep the loop-back
 * to ooa active (except on ooa itself). User: show real context only, no chain.
 */
export function bannerFor(
  mode: Mode,
  agent: AgentId,
  prev: ResidualPressure | null,
): BannerContext {
  if (mode === 'user' || !prev) {
    return {
      situation: prev ? prev.headline.split(' -> ').pop() ?? prev.headline : 'Current capacity context',
      loopBackToOoa: false,
    };
  }

  return {
    situation: `Carried from ${prev.fromAgent}: ${prev.headline}`,
    loopBackToOoa: agent !== 'ooa-agent',
  };
}
