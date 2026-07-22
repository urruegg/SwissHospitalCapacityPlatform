import { invokeInsight, type GroundedReply } from '../copilot-drawer/agent-manifest';
import type { AgentId, ContextInsight } from '../journey/RoleBoard';

export function buildInsightPrompt(insight: ContextInsight): string {
  return `Recommend a systemic action for "${insight.label}": ${JSON.stringify(insight.context)}`;
}

interface RouteDeps {
  agent: AgentId;
  openWithContext: (insight: ContextInsight) => void;
}

export async function routeInsight(
  insight: ContextInsight,
  deps: RouteDeps,
): Promise<GroundedReply> {
  deps.openWithContext(insight);
  return invokeInsight(deps.agent, insight.context);
}
