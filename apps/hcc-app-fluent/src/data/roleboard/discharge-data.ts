/**
 * Sprint 20 (parity) — enriched discharge dataset served THROUGH the data
 * layer (not hardcoded in a component). Flagged `simulated` until the Sprint 22
 * golden-source medallion is populated. Encodes the pinned golden-thread slice:
 * "9 expeditable discharges, residual site -7 beds" (OOA -16 → DCA -7).
 *
 * PHI: all patient ids are synthetic PT-xxxx tokens — no real patient data.
 */
import type { GroundedReco } from '../../copilot-rail/reco';

export type ReadinessStatus = 'READY' | 'BLOCKED' | 'PENDING';

export interface DischargeCandidate {
  id: string;
  patientId: string;        // PHI-safe synthetic: PT-xxxx
  ward: string;
  readiness: ReadinessStatus;
  blocker: string;
  estFreeHours: number;     // estimated hours until bed is free if actioned now
  bedsFreeable: number;
  recoId: string;
}

export interface CapacityBarrier {
  id: string;
  label: string;
  bedImpact: number;        // beds blocked by this barrier
  detail: string;
  recoId: string;
}

export interface DischargePayload {
  bedsNeeded: number;
  bedsFreeable: number;
  residualBeds: number;
  candidates: DischargeCandidate[];
  barriers: CapacityBarrier[];
  recoById: Record<string, GroundedReco>;
  defaultReco: GroundedReco;
}

const AGENT_LABEL = 'Discharge Copilot';
const CITES = ['gold.discharge_candidates', 'gold.fact_capacity_baseline'];

const recoById: Record<string, GroundedReco> = {
  'med-a-spitex': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Medicine A — Spitex block',
      qualifiers: ['4 beds', 'READY'],
      status: 'READY',
      tone: 'ok',
    },
    read:
      '4 Medicine A patients (PT-1001..PT-1004) are clinically discharge-ready but held by ' +
      'Spitex slot availability. Coordinating slots today frees 4 beds within 4h.',
    levers: [
      {
        text: 'Contact Spitex coordination desk — request 4 same-day slots',
        impact: { label: '+4 beds today', tone: 'beds' },
      },
      {
        text: 'Pre-confirm patients whose home setup is already complete (PT-1001, PT-1003)',
        impact: { label: '-4h wait', tone: 'time' },
      },
      {
        text: 'Route 1 low-complexity patient to Zollikerberg Spitex pool (capacity spare)',
        impact: { label: '+1 routing option', tone: 'routing' },
      },
    ],
    primaryCta: { label: 'Initiate Spitex coordination', kind: 'action' },
    projection: '4 beds freed within 4h',
    citations: CITES,
    provenance: 'simulated',
  },
  'med-a-rehab': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Medicine A — Rehab backlog',
      qualifiers: ['3 beds', 'READY'],
      status: 'READY',
      tone: 'ok',
    },
    read:
      '3 Medicine A patients are waiting on rehab transfer confirmation. ' +
      'Klinik Valens and RehaClinic have confirmed availability for today.',
    levers: [
      {
        text: 'Confirm 2 transfers to Klinik Valens (PT-1005, PT-1006)',
        impact: { label: '+2 beds / 6h', tone: 'beds' },
      },
      {
        text: 'Escalate PT-1007 to RehaClinic fast-track pathway',
        impact: { label: '+1 bed / 8h', tone: 'beds' },
      },
    ],
    primaryCta: { label: 'Confirm rehab transfers', kind: 'action' },
    projection: '3 beds freed within 8h',
    citations: CITES,
    provenance: 'simulated',
  },
  'surg-a-imaging': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Surgery A — Imaging queue',
      qualifiers: ['2 beds', 'READY'],
      status: 'READY',
      tone: 'ok',
    },
    read:
      '2 Surgery A patients (PT-2001, PT-2002) are awaiting final discharge imaging. ' +
      'Both scans are scheduled for 14:00 today. Early result turnaround clears the beds by 16:00.',
    levers: [
      {
        text: 'Request 12:00 slot pull-forward from radiology (capacity gap +2h)',
        impact: { label: '-2h wait', tone: 'time' },
      },
      {
        text: 'Pre-complete discharge paperwork while imaging runs',
        impact: { label: 'Zero queue on result', tone: 'time' },
      },
    ],
    primaryCta: { label: 'Coordinate with radiology', kind: 'action' },
    projection: '2 beds freed by 16:00',
    citations: CITES,
    provenance: 'simulated',
  },
  'med-b-family': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Medicine B — Family readiness',
      qualifiers: ['2 beds', 'PENDING'],
      status: 'PENDING',
      tone: 'pending',
    },
    read:
      '2 Medicine B patients are pending family care confirmation. ' +
      'Social work team has active contact. Expected resolution by end-of-shift.',
    levers: [
      {
        text: 'Social work follow-up call scheduled for 15:00',
        impact: { label: '+2 beds / 18h', tone: 'beds' },
      },
    ],
    primaryCta: { label: 'Check social work status', kind: 'action' },
    projection: '2 beds freed by end of shift',
    citations: CITES,
    provenance: 'simulated',
  },
  'discharge-gap': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Site discharge gap',
      qualifiers: ['9 beds freeable', '-7 residual'],
      status: '-7 beds',
      tone: 'watch',
    },
    read:
      '9 beds are freeable today: 4 blocked by Spitex shortage, 3 by rehab transfer backlog, ' +
      '2 by pending imaging clearance. Actioning all three top barriers closes 9/16 of the OOA gap.',
    levers: [
      {
        text: 'Coordinate Spitex slots (4 READY patients)',
        impact: { label: '+4 beds', tone: 'beds' },
      },
      {
        text: 'Confirm rehab transfers for 3 Medicine A patients',
        impact: { label: '+3 beds', tone: 'beds' },
      },
      {
        text: 'Pull-forward radiology queue for 2 Surgery A patients',
        impact: { label: '+2 beds', tone: 'time' },
      },
    ],
    primaryCta: {
      label: 'Hand off residual gap to Bed Manager (bmca)',
      kind: 'handoff',
      target: 'bmca-agent',
    },
    projection: '9 discharges cover 56% of the 16-bed demand; -7 residual passes to bmca',
    citations: CITES,
    provenance: 'simulated',
  },
};

const defaultReco: GroundedReco = {
  agentLabel: AGENT_LABEL,
  contextChip: {
    subject: 'Discharge gap: 9 beds freeable, -7 residual',
    tone: 'watch',
  },
  read:
    '9 beds are freeable today: 4 blocked by Spitex shortage, 3 by rehab transfer backlog, ' +
    '2 by pending discharge imaging. Actioning all three barriers leaves -7 beds residual for bmca.',
  levers: [
    {
      text: 'Resolve Spitex shortage — 4 READY patients (PT-1001..PT-1004)',
      impact: { label: '+4 beds', tone: 'beds' },
    },
    {
      text: 'Expedite rehab transfer for 3 Medicine A patients (PT-1005..PT-1007)',
      impact: { label: '+3 beds', tone: 'beds' },
    },
    {
      text: 'Clear imaging queue for 2 Surgery A patients (PT-2001, PT-2002)',
      impact: { label: '+2 beds', tone: 'time' },
    },
  ],
  primaryCta: {
    label: 'Hand off residual gap to Bed Manager (bmca)',
    kind: 'handoff',
    target: 'bmca-agent',
  },
  projection: '9 discharges cover 56% of the 16-bed demand; -7 residual passes to bmca',
  citations: CITES,
  provenance: 'simulated',
};

export const DISCHARGE_PINNED: DischargePayload = {
  bedsNeeded: 16,
  bedsFreeable: 9,
  residualBeds: -7, // MUST be -7 to preserve the golden-thread chain (OOA -16 → DCA -7)
  candidates: [
    {
      id: 'med-a-spitex',
      patientId: 'PT-1001',
      ward: 'Medicine A',
      readiness: 'READY',
      blocker: 'Awaiting Spitex slot',
      estFreeHours: 4,
      bedsFreeable: 4,
      recoId: 'med-a-spitex',
    },
    {
      id: 'med-a-rehab',
      patientId: 'PT-1005',
      ward: 'Medicine A',
      readiness: 'READY',
      blocker: 'Rehab transfer pending',
      estFreeHours: 6,
      bedsFreeable: 3,
      recoId: 'med-a-rehab',
    },
    {
      id: 'surg-a-imaging',
      patientId: 'PT-2001',
      ward: 'Surgery A',
      readiness: 'READY',
      blocker: 'Discharge imaging pending',
      estFreeHours: 2,
      bedsFreeable: 2,
      recoId: 'surg-a-imaging',
    },
    {
      id: 'med-b-family',
      patientId: 'PT-3001',
      ward: 'Medicine B',
      readiness: 'PENDING',
      blocker: 'Family readiness',
      estFreeHours: 12,
      bedsFreeable: 2,
      recoId: 'med-b-family',
    },
  ],
  // Pre-sorted by bedImpact desc; component also sorts to handle live data
  barriers: [
    {
      id: 'spitex-shortage',
      label: 'Spitex capacity shortage',
      bedImpact: 4,
      detail: '4 Medicine A patients awaiting Spitex home-care slot assignment',
      recoId: 'med-a-spitex',
    },
    {
      id: 'rehab-transfer',
      label: 'Rehab transfer backlog',
      bedImpact: 3,
      detail: '3 Medicine A patients awaiting rehab facility transfer confirmation',
      recoId: 'med-a-rehab',
    },
    {
      id: 'imaging-pending',
      label: 'Pending discharge imaging',
      bedImpact: 2,
      detail: '2 Surgery A patients awaiting final imaging clearance before discharge',
      recoId: 'surg-a-imaging',
    },
    {
      id: 'family-readiness',
      label: 'Family care readiness',
      bedImpact: 2,
      detail: '2 Medicine B patients pending family-care arrangement confirmation',
      recoId: 'med-b-family',
    },
  ],
  recoById,
  defaultReco,
};

