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
 * Deterministic per-agent grounded artefacts for dev/CI — each mirrors the shape
 * a Foundry Agent returns so every role's Copilot pane demonstrates the artefact
 * catalogue (context chip, read, levers+impact, CTA+approval gate, projection,
 * citations) with role-appropriate content. Grounded, simulated values only; no
 * PHI. Read agents (ooa) hand off; write/deploy agents gate the CTA (HITL).
 */
const AGENT_RECOS: Record<string, GroundedReco> = {
  'ooa-agent': {
    agentLabel: 'Occupancy Copilot',
    contextChip: { subject: 'Medizin A', qualifiers: ['72-h-Prognose'], status: 'OVER', tone: 'over' },
    read: 'Medizin A erreicht in 72 h 102% - 6 Grippe-Zugänge stehen 2 geplanten Austritten gegenüber.',
    metrics: [
      { label: 'Jetzt', value: '96%' },
      { label: '72 h', value: '102%' },
      { label: 'Lücke', value: '-6 Betten', tone: 'beds' },
    ],
    levers: [
      { text: '6 austrittsbereite Patienten vor 17:00 entlassen', impact: { label: '-6 Betten', tone: 'beds' }, evidence: {
        summary: '6 Patienten sind als austrittsbereit markiert (Arztvisite abgeschlossen).',
        detail: ['4 warten auf Transport, 2 auf Rezept', 'Fenster bis 17:00 realistisch', 'Wirkung: Medizin A 102% -> 94%'],
        citations: ['hcp:Encounter', 'gold.fact_discharge_readiness'],
      } },
      { text: '3 Niedrig-Akut-Zugänge nach Medizin B umleiten', impact: { label: '+3 Puffer', tone: 'buffer' } },
    ],
    primaryCta: { label: 'Austrittsliste öffnen', kind: 'handoff', target: 'dca-agent' },
    projection: '102% -> 94%',
    citations: ['hcp:CapacityUnit', 'gold.fact_occupancy_forecast'],
    provenance: 'simulated',
    refused: false,
    followUps: ['Was passiert ohne Massnahme?', 'Station B vergleichen', 'Austrittsliste öffnen'],
  },
  'bmca-agent': {
    agentLabel: 'Bed-Management Copilot',
    contextChip: { subject: 'Station B', qualifiers: ['Belegung'], status: '92%', tone: 'watch' },
    read:
      'Station B liegt bei 92% und steigt weiter. Umschichtung Richtung Notaufnahme ' +
      'empfohlen; die Aktion erfordert HITL-02-Freigabe.',
    metrics: [
      { label: 'Jetzt', value: '92%' },
      { label: 'Trend', value: '96%' },
      { label: 'Ziel', value: '85%', tone: 'beds' },
    ],
    levers: [
      { text: '2 Betten Richtung Notaufnahme umschichten', impact: { label: '+2 Betten', tone: 'beds' } },
      { text: '1 verlegbaren Patienten auf Station A vormerken', impact: { label: '-1 Bett', tone: 'beds' } },
    ],
    primaryCta: { label: 'Umschichtung anstossen', kind: 'action', requiresApproval: true },
    projection: '92% -> 85%',
    citations: ['hcp:Bed', 'gold.bed_assignment'],
    provenance: 'simulated',
    refused: false,
    followUps: ['Warum steigt Station B?', 'Alternative Stationen zeigen', 'Freigabe anfordern'],
  },
  'dca-agent': {
    agentLabel: 'Discharge Copilot',
    contextChip: { subject: 'Austritte', qualifiers: ['heute'], status: '8 bereit', tone: 'ranked' },
    read: '8 Patienten sind austrittsbereit; 3 warten auf eine Nachsorge-Platzierung.',
    metrics: [
      { label: 'Bereit', value: '8' },
      { label: 'Blockiert', value: '3' },
      { label: 'Frei bis 12:00', value: '+2', tone: 'time' },
    ],
    levers: [
      { text: '3 Nachsorge-Platzierungen mit Spitex koordinieren', impact: { label: '+3 Betten', tone: 'beds' } },
      { text: '2 Austritte vor 12:00 priorisieren', impact: { label: '-2 / Vormittag', tone: 'time' } },
    ],
    primaryCta: { label: 'Austritte bestätigen', kind: 'action', requiresApproval: true },
    projection: '8 Kandidaten decken 50% der Lücke',
    citations: ['hcp:Encounter', 'gold.fact_discharge_readiness'],
    provenance: 'simulated',
    refused: false,
    followUps: ['Spitex-Slots prüfen', 'Austritte nach Uhrzeit', 'Nachsorge-Status'],
  },
  'orsa-agent': {
    agentLabel: 'OR-Steering Copilot',
    contextChip: { subject: 'OP-Plan', qualifiers: ['Mittwoch'], status: 'Überbucht', tone: 'watch' },
    read: 'Der Mittwoch-OP-Plan ist überbucht; zwei Elektiv-Eingriffe kollidieren mit langsamen Post-OP-Austritten.',
    metrics: [
      { label: 'Mi-Spitze', value: '88%' },
      { label: 'Nach Umplanung', value: '80%' },
      { label: 'Betten Mi', value: '+2', tone: 'beds' },
    ],
    levers: [
      { text: '2 Elektiv-Eingriffe auf Freitag verschieben', impact: { label: '+2 Betten Mi', tone: 'beds' } },
      { text: '1 Saal als Notfall-Puffer reservieren', impact: { label: 'Puffer', tone: 'buffer' } },
    ],
    primaryCta: { label: 'Umplanungs-Vorschlag erstellen', kind: 'action', requiresApproval: true },
    projection: 'Mittwoch-Spitze 88% -> 80%',
    citations: ['hcp:ORSlot', 'gold.fact_or_schedule'],
    provenance: 'simulated',
    refused: false,
    followUps: ['Freitag-Kapazität prüfen', 'Notfall-Puffer anzeigen', 'Post-OP-Austritte'],
  },
  'sba-agent': {
    agentLabel: 'Staffing Copilot',
    contextChip: { subject: 'Pflege IPS', qualifiers: ['Spätdienst'], status: 'Unterbesetzt', tone: 'over' },
    read: 'Die IPS ist im Spätdienst 1.5 FTE unter Bedarf gegenüber der prognostizierten Belegung.',
    metrics: [
      { label: 'Bedarf', value: '6.5 FTE' },
      { label: 'Besetzt', value: '5.0 FTE' },
      { label: 'Lücke', value: '-1.5 FTE', tone: 'status' },
    ],
    levers: [
      { text: '2 Pool-Pflegende für den Spätdienst anfragen', impact: { label: '+2 FTE', tone: 'status' }, evidence: {
        summary: 'IPS Spätdienst: 1.5 FTE unter Bedarf (Pflege).',
        detail: ['Rolle: Pflegefachperson (dipl. HF)', 'Schicht: 15:00-23:00'],
        people: ['A. Weber (dipl. HF)', 'T. Meier (dipl. HF)', 'L. Kunz (Pool)'],
        citations: ['hcp:CareTeam', 'gold.fact_staffing_roster'],
      } },
      { text: '1 elektive Aufnahme auf morgen verschieben', impact: { label: '-1 Bedarf', tone: 'buffer' } },
    ],
    primaryCta: { label: 'Dienstplan-Anpassung anstossen', kind: 'action', requiresApproval: true },
    projection: 'Deckung 88% -> 100%',
    citations: ['hcp:CareTeam', 'gold.fact_staffing_roster'],
    provenance: 'simulated',
    refused: false,
    followUps: ['Pool-Verfügbarkeit prüfen', 'Wer ist betroffen?', 'Deckung für morgen'],
  },
  'csa-agent': {
    agentLabel: 'Crisis Copilot',
    contextChip: { subject: 'Szenario Massenanfall', qualifiers: ['Bereitschaft'], status: 'Aktiv', tone: 'signal' },
    read: 'Szenario Massenanfall: geschätzt 20 Zusatz-Zugänge in 6 h. Zwei Hebel schaffen 14 Betten.',
    metrics: [
      { label: 'Zusatzbedarf', value: '20 Betten' },
      { label: 'Mobilisierbar', value: '14 Betten' },
      { label: 'Restrisiko', value: '-6 Betten', tone: 'routing' },
    ],
    levers: [
      { text: 'Elektiv-Programm für 24 h aussetzen', impact: { label: '+10 Betten', tone: 'beds' } },
      { text: 'Cross-Hospital-Verlegung nach Curalp aktivieren', impact: { label: '+4 Betten', tone: 'routing' } },
    ],
    primaryCta: { label: 'Krisen-Szenario ausführen', kind: 'action', requiresApproval: true },
    projection: 'Deckt 14 der 20 Zusatzbetten',
    citations: ['hcp:Facility', 'gold.fact_capacity_baseline'],
    provenance: 'simulated',
    refused: false,
    followUps: ['Curalp-Kapazität prüfen', 'Szenario anpassen', 'Freigabe-Status'],
  },
};

/**
 * Returns the role-specific grounded artefact, or a Station-B bed reco fallback
 * (relabelled) for non-board agents such as `orchestrator` at bare `/main`.
 */
function mockReco(agent: string): GroundedReco {
  const reco = AGENT_RECOS[agent];
  if (reco) return reco;
  return { ...AGENT_RECOS['bmca-agent'], agentLabel: AGENT_LABELS[agent] ?? agent };
}

/**
 * A11 — asks the agent must refuse. Destructive/side-effecting verbs without an
 * approval, or any request for patient-identifying data (PHI). Kept narrow so the
 * happy-path grounded recos are unaffected.
 */
const REFUSAL_TRIGGER = /(l\u00f6sch|entfern|delete|drop|force|\u00fcberschreib|ohne freigabe|ohne genehmigung)/i;
const PHI_TRIGGER = /(patientenname|namen der patient|ahv|geburtsdatum|krankengeschichte|diagnose von)/i;

/** Build a verbatim guardrail refusal artefact (A11) — no fabrication, cite the gate. */
function refusalReco(agent: string, prompt: string): GroundedReco {
  const phi = PHI_TRIGGER.test(prompt);
  const read = phi
    ? 'Anfrage abgelehnt: Es werden keine personenbezogenen Patientendaten (PHI) verarbeitet oder ausgegeben.'
    : 'Anfrage abgelehnt: Diese Aktion hat einen Seiteneffekt und erfordert eine HITL-Freigabe (approved-to-apply), bevor sie ausgef\u00fchrt werden kann.';
  return {
    agentLabel: AGENT_LABELS[agent] ?? agent,
    contextChip: { subject: 'Guardrail', status: 'Verweigert', tone: 'blocked' },
    read,
    levers: [],
    citations: phi ? ['policy:PHI-Gate', 'docs/SECURITY.md'] : ['policy:HITL-02', 'AGENTS.md#4-confirmation-rule'],
    provenance: 'simulated',
    refused: true,
  };
}

/**
 * Send a prompt to one agent via the agent-host. When no host URL is configured
 * (dev/CI), returns a deterministic grounded mock so the drawer demonstrates the
 * wiring end-to-end without a live backend. A destructive/PHI ask returns a
 * verbatim guardrail refusal (A11) instead of a recommendation.
 */
export async function invokeAgent(
  agent: string,
  prompt: string,
): Promise<GroundedReply> {
  if (!isAgentHostConfigured()) {
    const reco =
      REFUSAL_TRIGGER.test(prompt) || PHI_TRIGGER.test(prompt)
        ? refusalReco(agent, prompt)
        : mockReco(agent);
    return { answer: reco.read, citations: reco.citations, refused: reco.refused ?? false, reco };
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
