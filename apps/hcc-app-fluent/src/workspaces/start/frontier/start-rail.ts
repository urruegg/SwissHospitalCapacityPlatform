import type { ContextInsight } from '../../../journey/RoleBoard';
import type { GroundedReco } from '../../../copilot-rail/reco';
import type { CopilotRailValue } from '../../../copilot-rail/rail-context';
import { invokeAgent } from '../../../copilot-drawer/agent-manifest';

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

/**
 * Sprint 41 WS-FE — progressive-enhancement live enrichment. Fire-and-forget:
 * asks the Product Owner Agent the same question behind the static reco, and
 * swaps in the live-grounded answer via `rail.updateActiveReco` once it
 * resolves. Never throws into the caller's click handler; a failed live call
 * simply leaves the static reco visible.
 */
export async function enrichWithLiveAnswer(
  question: string,
  rail: Pick<CopilotRailValue, 'updateActiveReco'>,
): Promise<void> {
  const reply = await invokeAgent('product-owner-agent', question);
  if (reply.reco) {
    rail.updateActiveReco(reply.reco);
  }
}
