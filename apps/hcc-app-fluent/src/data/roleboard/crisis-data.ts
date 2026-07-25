/**
 * Sprint 20 M5 (parity) — CSA crisis dataset, DC-EXT-SIGNAL-v1 compliant.
 * Rewritten from the Sprint 4 stub to the locked data model from the
 * parity-review outcome spec §3.  Supersedes the old Certainty enum
 * ('high'/'medium'/'low') with the canonical Trust-A mapping:
 *   Likely → 68%, Possible → 31%, Unlikely → 6%
 */
import type { GroundedReco } from '../../copilot-rail/reco';

export type Certainty = 'Likely' | 'Possible' | 'Unlikely';

/** Trust-A certainty → integer probability (DC-EXT-SIGNAL-v1). */
export const CERTAINTY_TO_PROBABILITY: Record<Certainty, number> = {
  Likely: 68,
  Possible: 31,
  Unlikely: 6,
};

export function certaintyToProbability(c: Certainty): number {
  return CERTAINTY_TO_PROBABILITY[c];
}

export interface ExternalSignal {
  id: string;
  source: 'MeteoSwiss' | 'BAG/FOPH' | 'Alertswiss/BABS' | 'SED-ETH';
  feed: string;
  status: string;
  trustClass: 'Trust-A';
  lageLevel?: string;
  certainty: Certainty;
  probability: number;    // derived via CERTAINTY_TO_PROBABILITY
  feedsLever?: string;
  licence: string;
  provenance: string;
  filtered?: boolean;     // Test/quarantined signals RENDER but do NOT arm a lever
}

export interface Scenario {
  id: string;
  name: string;
  bedImpact: number;
  isSpof: boolean;
  probability: number;
  triggerSignal?: string;
}

export interface ScenarioRun {
  id: string;
  scenarioId: string;
  params: Record<string, unknown>;
  status: 'draft' | 'running' | 'complete';
  result?: Record<string, unknown>;
}

export interface CrisisPayload {
  residualBeds: number;   // carried in from sba (0 = balanced steady state)
  signals: ExternalSignal[];
  scenarios: Scenario[];
  recoById: Record<string, GroundedReco>;
  defaultReco: GroundedReco;
}

const AGENT_LABEL = 'Crisis Copilot';
const CITES = ['gold.crisis_signals', 'gold.fact_capacity_baseline'];

const recoById: Record<string, GroundedReco> = {
  'heatwave-surge': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Heatwave demand surge — simulate',
      qualifiers: ['68% probability', 'SPOF', '+14 beds'],
      status: 'Likely',
      tone: 'watch',
    },
    read:
      'MeteoSwiss Trust-A level-3 heatwave warning is active at 68% probability. ' +
      'Simulating this scenario projects a 14-bed surge across medical and ICU wards. ' +
      'Running the simulation requires approved-to-apply before csa-agent fires the csa-simulate notebook.',
    levers: [
      {
        text: 'Trigger csa-simulate notebook for heatwave-surge scenario',
        impact: { label: '14 beds at risk', tone: 'beds' },
      },
      {
        text: 'Pre-position surge beds and staffing via sba-agent handoff',
        impact: { label: 'Risk mitigation', tone: 'trust' },
      },
      {
        text: 'Notify incident commander and site medical director',
        impact: { label: '68% probability', tone: 'probability' },
      },
    ],
    primaryCta: {
      label: 'Run heatwave simulation',
      kind: 'action',
      requiresApproval: true,
    },
    projection: '+14 beds in 72h if heatwave materialises',
    citations: CITES,
    provenance: 'simulated',
  },
  'resp-virus-surge': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Respiratory virus surge — simulate',
      qualifiers: ['31% probability', '+9 beds'],
      status: 'Possible',
      tone: 'watch',
    },
    read:
      'BAG/FOPH Trust-A Sentinella signal is Possible (31%). ' +
      'Simulating projects a 9-bed surge primarily across respiratory and ICU wards.',
    levers: [
      {
        text: 'Trigger csa-simulate notebook for resp-virus-surge scenario',
        impact: { label: '9 beds at risk', tone: 'beds' },
      },
      {
        text: 'Review respiratory isolation ward capacity',
        impact: { label: '31% probability', tone: 'probability' },
      },
    ],
    primaryCta: {
      label: 'Run respiratory virus simulation',
      kind: 'action',
      requiresApproval: true,
    },
    projection: '+9 beds in 72h if respiratory surge materialises',
    citations: CITES,
    provenance: 'simulated',
  },
  'seismic-event': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Seismic event response — simulate',
      qualifiers: ['6% probability', 'SPOF', '+5 beds'],
      status: 'Unlikely',
      tone: 'pending',
    },
    read:
      'SED-ETH Trust-A seismic signal is Unlikely (6%). ' +
      'Low probability but a SPOF event would require activating full emergency protocols.',
    levers: [
      {
        text: 'Trigger csa-simulate notebook for seismic-event scenario',
        impact: { label: '5 beds at risk', tone: 'beds' },
      },
      {
        text: 'Verify structural safety protocols and SPOF mitigations',
        impact: { label: 'SPOF mitigation', tone: 'trust' },
      },
    ],
    primaryCta: {
      label: 'Run seismic event simulation',
      kind: 'action',
      requiresApproval: true,
    },
    projection: '+5 beds if seismic event materialises',
    citations: CITES,
    provenance: 'simulated',
  },
  'crisis-readiness': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Site crisis readiness',
      qualifiers: ['3 active signals', '0 residual beds'],
      status: 'OK',
      tone: 'ok',
    },
    read:
      'Site is at balanced steady-state (0 residual beds from sba). ' +
      '3 Trust-A signals are active; 1 Alertswiss test signal is quarantined by the DC-EXT-SIGNAL-v1 gate. ' +
      'Top risk: heatwave-surge at 68%. No immediate crisis posture change required.',
    levers: [
      {
        text: 'Monitor heatwave-surge signal — highest probability scenario',
        impact: { label: '68% probability', tone: 'probability' },
      },
      {
        text: 'Verify surge plan covers both heatwave and resp-virus scenarios',
        impact: { label: 'Dual scenario', tone: 'trust' },
      },
    ],
    primaryCta: {
      label: 'Review full crisis readiness',
      kind: 'action',
    },
    projection: '0 residual beds; site balanced — proactive readiness only',
    citations: CITES,
    provenance: 'simulated',
  },
  // Refused reco for the quarantined Alertswiss test signal (DC-EXT-SIGNAL-v1 gate)
  'alertswiss-heat-test': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Alertswiss test signal — quarantined',
      qualifiers: ['filtered', 'DC-EXT-SIGNAL-v1'],
      status: 'Filtered',
      tone: 'signal',
    },
    read:
      'This Alertswiss/BABS signal was flagged as a test/quarantined payload by the ' +
      'DC-EXT-SIGNAL-v1 gate (filtered=true). It renders for visibility but does NOT arm any ' +
      'crisis lever. No simulation action can be triggered for quarantined signals.',
    levers: [],
    primaryCta: {
      label: 'Quarantined — no action available',
      kind: 'action',
    },
    projection: 'Signal quarantined; lever not armed per DC-EXT-SIGNAL-v1',
    citations: ['dc-ext-signal-v1.gate'],
    provenance: 'simulated',
    refused: true,
  },
};

const defaultReco: GroundedReco = {
  agentLabel: AGENT_LABEL,
  contextChip: {
    subject: 'Crisis readiness summary',
    qualifiers: ['0 residual beds', '3 active signals'],
    tone: 'ok',
  },
  read:
    'Site is at balanced steady-state. Three Trust-A signals are active; ' +
    'the heatwave-surge scenario at 68% is the primary risk. ' +
    'Simulate the top scenario to validate surge capacity.',
  levers: [
    {
      text: 'Run heatwave-surge simulation (highest probability, 68%)',
      impact: { label: '68% probability', tone: 'probability' },
    },
    {
      text: 'Monitor BAG/FOPH respiratory signal (Possible, 31%)',
      impact: { label: '31% probability', tone: 'probability' },
    },
  ],
  primaryCta: {
    label: 'Review crisis readiness',
    kind: 'action',
  },
  projection: '0 residual beds; proactive readiness',
  citations: CITES,
  provenance: 'simulated',
};

/** Stable sort: probability desc, tie-break by id (mirrors sortReslotLevers in or-steering-data). */
export function sortScenarios(scenarios: Scenario[]): Scenario[] {
  return [...scenarios].sort((a, b) => b.probability - a.probability || a.id.localeCompare(b.id));
}

export const CRISIS_PINNED: CrisisPayload = {
  residualBeds: 0,   // MUST be 0: golden-thread sba→csa steady-state (sba closes the gap)
  signals: [
    {
      id: 'meteoswiss-heat',
      source: 'MeteoSwiss',
      feed: 'CAP-CH Hitzewelle Warnung Level 3',
      status: 'ACTIVE',
      trustClass: 'Trust-A',
      lageLevel: 'Orange',
      certainty: 'Likely',
      probability: certaintyToProbability('Likely'),
      feedsLever: 'heatwave-surge',
      licence: 'MeteoSwiss Open Data (OGD) — CC BY 4.0',
      provenance: 'simulated',
    },
    {
      id: 'bag-resp',
      source: 'BAG/FOPH',
      feed: 'Sentinella Respiratory Virus Surveillance',
      status: 'ELEVATED',
      trustClass: 'Trust-A',
      certainty: 'Possible',
      probability: certaintyToProbability('Possible'),
      feedsLever: 'resp-virus-surge',
      licence: 'BAG/FOPH Open Government Data — dl-ch/2.0',
      provenance: 'simulated',
    },
    {
      id: 'sed-seismic',
      source: 'SED-ETH',
      feed: 'SED SeismoStats Minor Seismic Activity',
      status: 'MONITORING',
      trustClass: 'Trust-A',
      lageLevel: 'Yellow',
      certainty: 'Unlikely',
      probability: certaintyToProbability('Unlikely'),
      feedsLever: 'seismic-event',
      licence: 'SED Open Data — CC BY 4.0',
      provenance: 'simulated',
    },
    {
      id: 'alertswiss-heat-test',
      source: 'Alertswiss/BABS',
      feed: 'TEST Alertswiss CAP Hitzewelle',
      status: 'TEST',
      trustClass: 'Trust-A',
      certainty: 'Likely',
      probability: certaintyToProbability('Likely'),
      licence: 'Alertswiss/BABS Public Alerts — CC BY 4.0',
      provenance: 'simulated',
      filtered: true,   // DC-EXT-SIGNAL-v1: quarantined — renders but does NOT arm a lever
    },
  ],
  scenarios: [
    {
      id: 'heatwave-surge',
      name: 'Summer heatwave demand surge',
      bedImpact: 14,
      isSpof: true,
      probability: certaintyToProbability('Likely'),   // 68
      triggerSignal: 'meteoswiss-heat',
    },
    {
      id: 'resp-virus-surge',
      name: 'Respiratory virus surge',
      bedImpact: 9,
      isSpof: false,
      probability: certaintyToProbability('Possible'), // 31
      triggerSignal: 'bag-resp',
    },
    {
      id: 'seismic-event',
      name: 'Seismic event response',
      bedImpact: 5,
      isSpof: true,
      probability: certaintyToProbability('Unlikely'), // 6
      triggerSignal: 'sed-seismic',
    },
  ],
  recoById,
  defaultReco,
};
