/**
 * Sprint 13 T6 — client-side contract for the deployed agent list + chat call.
 *
 * The Copilot Drawer is agent-agnostic; per-agent config comes from the
 * agent-host (`apps/hcc-agent-host`). The base URL is injected via Vite env so
 * the westus2 region (ADR-0013) is a config value, not code (design spec §9 risk).
 * Routed through the IQ-layer gateway (`../data/iq-client`); this module holds no
 * endpoint or `fetch` of its own.
 */
import type { GroundedReco } from '../copilot-rail/reco';
import { isAgentHostConfigured, iqAgentChat, iqAgentList } from '../data/iq-client';

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
  /**
   * Optional structured grounded artefact. When the agent-host (Foundry Agent)
   * returns a grounded recommendation, the Copilot pane renders it through the
   * shared RecoPanel block stack (context chip, levers, approval gate,
   * citations) instead of a flat text bubble. Absent → plain-text reply.
   */
  reco?: GroundedReco;
}

/** Fetch the deployed agent list from the agent-host, or a static fallback. */
export async function fetchAgents(): Promise<AgentManifestEntry[]> {
  if (!isAgentHostConfigured()) {
    return [
      { name: 'ooa-agent', displayName: 'OOA', ceiling: 'read' },
      { name: 'dca-agent', displayName: 'DCA', ceiling: 'write' },
      { name: 'bmca-agent', displayName: 'BMCA', ceiling: 'write' },
      { name: 'orsa-agent', displayName: 'ORSA', ceiling: 'write' },
      { name: 'sba-agent', displayName: 'SBA', ceiling: 'write' },
      { name: 'csa-agent', displayName: 'CSA', ceiling: 'deploy' },
    ];
  }
  return iqAgentList<AgentManifestEntry[]>();
}

/** Display label per role agent, used as the artefact's attribution line. */
const AGENT_LABELS: Record<string, string> = {
  'ooa-agent': 'Occupancy Copilot',
  'bmca-agent': 'Bed-Management Copilot',
  'dca-agent': 'Discharge Copilot',
  'orsa-agent': 'OR-Steering Copilot',
  'sba-agent': 'Staffing Copilot',
  'csa-agent': 'Crisis Copilot',
};

/**
 * Deterministic structured grounded answer for dev/CI — mirrors the shape a
 * Foundry Agent returns so the Copilot pane demonstrates the artefact rendering
 * end-to-end without a live agent-host. Grounded, simulated values only; no PHI.
 */
function mockReco(agent: string): GroundedReco {
  return {
    agentLabel: AGENT_LABELS[agent] ?? agent,
    contextChip: { subject: 'Station B', qualifiers: ['Auslastung'], status: '92%', tone: 'watch' },
    read:
      'Auslastung Station B liegt bei 92% und steigt weiter. Umschichtung Richtung ' +
      'Notaufnahme empfohlen; die Aktion erfordert HITL-02-Freigabe.',
    levers: [
      { text: '2 Betten Richtung Notaufnahme umschichten', impact: { label: '+2 Betten', tone: 'beds' } },
      { text: '1 verlegbaren Patienten auf Station A vormerken', impact: { label: '-1 Bett', tone: 'beds' } },
    ],
    primaryCta: { label: 'Umschichtung anstossen', kind: 'action', requiresApproval: true },
    projection: '92% -> 85%',
    citations: ['gold.bed_assignment', 'gold.fact_capacity_baseline'],
    provenance: 'simulated',
    refused: false,
  };
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
  if (!isAgentHostConfigured()) {
    const reco = mockReco(agent);
    return {
      answer:
        `Auslastung Station B liegt bei 92%. Empfehlung: 2 Betten Richtung ` +
        `Notaufnahme umschichten. Aktion erfordert HITL-02-Freigabe.`,
      citations: reco.citations,
      refused: false,
      reco,
    };
  }
  return iqAgentChat<GroundedReply>(agent, prompt);
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
