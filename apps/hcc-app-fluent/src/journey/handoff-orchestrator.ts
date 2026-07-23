import type { AgentId, BannerContext, Mode, ResidualPressure, RoleBoard, ScenarioScope } from './RoleBoard';
import { ROLE_SEQUENCE, SEED_SITUATION } from './golden-thread';
import { occupancyBoard } from '../workspaces/main/boards/occupancy/occupancy-board';
import { dischargeBoard } from '../workspaces/main/boards/discharge/discharge-board';
import { bedManagerBoard } from '../workspaces/main/boards/bed-manager/bed-manager-board';
import { orSteeringBoard } from '../workspaces/main/boards/or-steering/or-steering-board';
import { staffingBoard } from '../workspaces/main/boards/staffing/staffing-board';
import { crisisBoard } from '../workspaces/main/boards/crisis/crisis-board';

const BOARD_BY_AGENT: Record<AgentId, RoleBoard> = {
  'ooa-agent': occupancyBoard,
  'dca-agent': dischargeBoard,
  'bmca-agent': bedManagerBoard,
  'orsa-agent': orSteeringBoard,
  'sba-agent': staffingBoard,
  'csa-agent': crisisBoard,
};

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

/**
 * Demo only — the residual pressure carried INTO `agent` from its predecessor
 * in the golden-thread ring. ooa starts the ring from the seed situation. In
 * User mode there is no chain, so returns null.
 */
export async function residualFromPrev(
  agent: AgentId,
  scope: ScenarioScope,
  mode: Mode,
): Promise<ResidualPressure | null> {
  if (mode !== 'demo') return null;
  if (agent === 'ooa-agent') return SEED_SITUATION;
  const i = ROLE_SEQUENCE.indexOf(agent);
  const prevAgent = ROLE_SEQUENCE[(i - 1 + ROLE_SEQUENCE.length) % ROLE_SEQUENCE.length];
  const prevBoard = BOARD_BY_AGENT[prevAgent];
  const data = await prevBoard.load(scope, mode);
  return prevBoard.toHandoff(data);
}
