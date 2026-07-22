import type { AgentId, ResidualPressure, ScenarioScope } from './RoleBoard';

/** Sprint 1 (parity) — the pinned Demo scenario + ordered 6-role sequence. */
export const GOLDEN_THREAD_SCOPE: ScenarioScope = {
  hospital: 'usz',
  windowHours: 72,
  pinned: true,
};

export const ROLE_SEQUENCE: AgentId[] = [
  'ooa-agent',
  'dca-agent',
  'bmca-agent',
  'orsa-agent',
  'sba-agent',
  'csa-agent',
];

export const SEED_SITUATION: ResidualPressure = {
  fromAgent: 'ooa-agent',
  headline: 'Medicine A -> 102% in 72h, site -16 beds',
  metrics: { occupancyPct: 102, deltaBeds: -16 },
};

/** Next agent in the ring, looping csa-agent back to ooa-agent. */
export function nextAgent(current: AgentId): AgentId {
  const i = ROLE_SEQUENCE.indexOf(current);
  return ROLE_SEQUENCE[(i + 1) % ROLE_SEQUENCE.length];
}
