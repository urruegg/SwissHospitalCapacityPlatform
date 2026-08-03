import type { ContextInsight } from '../../../journey/RoleBoard';
import type { GroundedReco } from '../../../copilot-rail/reco';

/**
 * Sprint 40 START polish — P17 rail helpers. Each polished START card becomes a
 * context-click that opens the Copilot rail with a short, honest grounded reco
 * (provenance 'simulated', real citations). Mirrors the backstage narrative
 * pattern (rail.openWithReco(insight, reco)).
 */
export function startInsight(id: string, label: string): ContextInsight {
  return { id, label, context: { source: 'start-narrative', topic: id } };
}

export function startReco(
  agentLabel: string,
  read: string,
  levers: string[],
  citations: string[],
): GroundedReco {
  return {
    agentLabel,
    contextChip: { subject: agentLabel, tone: 'signal' },
    read,
    levers: levers.map((text) => ({ text })),
    citations,
    provenance: 'simulated',
  };
}
