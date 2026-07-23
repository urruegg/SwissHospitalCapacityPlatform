import { invokeInsight, type GroundedReply } from '../copilot-drawer/agent-manifest';
import type { AgentId, ContextInsight } from '../journey/RoleBoard';
import type { GroundedReco } from './reco';

export function buildInsightPrompt(insight: ContextInsight): string {
  return `Recommend a systemic action for "${insight.label}": ${JSON.stringify(insight.context)}`;
}

interface RouteDeps {
  agent: AgentId;
  openWithReco: (insight: ContextInsight, reco: GroundedReco) => void;
}

export async function routeInsight(
  insight: ContextInsight,
  reco: GroundedReco,
  deps: RouteDeps,
): Promise<GroundedReply> {
  deps.openWithReco(insight, reco);
  return invokeInsight(deps.agent, insight.context);
}
