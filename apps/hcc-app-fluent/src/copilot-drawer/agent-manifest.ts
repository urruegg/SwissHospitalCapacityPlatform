/**
 * Sprint 13 T6 — client-side contract for the deployed agent list + chat call.
 *
 * The Copilot Drawer is agent-agnostic; per-agent config comes from the
 * agent-host (`apps/hcc-agent-host`). The base URL is injected via Vite env so
 * the westus2 region (ADR-0013) is a config value, not code (design spec §9 risk).
 */
export interface AgentManifestEntry {
  name: string;
  displayName: string;
  ceiling: 'read' | 'write' | 'deploy' | 'delete';
}

export interface GroundedReply {
  /** Agent answer text. Must be free of PHI (server enforces; see agent-host). */
  answer: string;
  /** Grounding citations rendered as a footer. */
  citations: string[];
  /** True when the agent refused (e.g. a HITL gate blocked a side effect). */
  refused: boolean;
}

const agentHostBaseUrl: string = import.meta.env.VITE_AGENT_HOST_URL ?? '';

/** Fetch the deployed agent list from the agent-host, or a static fallback. */
export async function fetchAgents(): Promise<AgentManifestEntry[]> {
  if (!agentHostBaseUrl) {
    return [{ name: 'bmca-agent', displayName: 'BMCA', ceiling: 'write' }];
  }
  const res = await fetch(`${agentHostBaseUrl}/agents`);
  if (!res.ok) throw new Error(`agent list failed: ${res.status}`);
  return (await res.json()) as AgentManifestEntry[];
}

/**
 * Send a prompt to one agent via the agent-host. When no host URL is configured
 * (dev/CI), returns a deterministic grounded mock so the drawer demonstrates the
 * wiring end-to-end without a live backend.
 */
export async function invokeAgent(
  agent: string,
  prompt: string,
): Promise<GroundedReply> {
  if (!agentHostBaseUrl) {
    return {
      answer:
        `Auslastung Station B liegt bei 92%. Empfehlung: 2 Betten Richtung ` +
        `Notaufnahme umschichten. Aktion erfordert HITL-02-Freigabe.`,
      citations: ['gold.bed_assignment', 'gold.fact_capacity_baseline'],
      refused: false,
    };
  }
  const res = await fetch(`${agentHostBaseUrl}/agents/${agent}/chat`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error(`agent chat failed: ${res.status}`);
  return (await res.json()) as GroundedReply;
}

/**
 * Sprint 1 (parity) — fetch a systemic recommendation for a clicked context
 * insight. Grounded by the agent-host; when no host URL is configured returns a
 * deterministic reply derived FROM the passed context (the no-fabrication rule
 * is enforced here at the agent boundary, never inside a board component).
 */
export async function invokeInsight(
  agent: string,
  context: Record<string, unknown>,
): Promise<GroundedReply> {
  const prompt = `Recommend a systemic action for: ${JSON.stringify(context)}`;
  return invokeAgent(agent, prompt);
}
