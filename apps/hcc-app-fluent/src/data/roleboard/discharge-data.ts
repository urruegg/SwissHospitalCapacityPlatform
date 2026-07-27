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
  blocker: string;          // barrier reason ('' when READY -> shown as '—')
  estFreeHours: number;     // numeric hours until the bed frees if actioned now
  estFreeLabel: string;     // display, e.g. '< 2h', 'today', '24h'
  bedsFreeable: number;
  recoId: string;
}

/** Leading glyph per capacity barrier. */
export type BarrierIcon = 'transport' | 'meds' | 'stepdown' | 'signoff' | 'homecare';

export interface CapacityBarrier {
  id: string;
  name: string;               // barrier title
  description: string;        // one-line context
  bedImpact: number;          // beds recovered when resolved
  impactLabel?: string;       // overrides the "N beds" label, e.g. '1 ICU'
  icon: BarrierIcon;          // leading glyph
  owner: string;              // responsible queue/team
  wait: string;               // e.g. 'stuck 4h'
  waitTone: 'ok' | 'watch' | 'over'; // dot colour: green | amber | red
  action: string;             // right-side next-step, e.g. 'clears today', 'by 14:00'
  agingRisk?: boolean;        // 'AGING RISK' badge
  recoId: string;
}

/** Header roll-up for the capacity barriers board (display). */
export interface BarrierSummary {
  readyNow: number;
  blocked: number;
  barriers: number;
  bedsRecoverable: number;
}

export interface DischargePayload {
  bedsNeeded: number;
  bedsFreeable: number;
  residualBeds: number;
  candidates: DischargeCandidate[];
  barriers: CapacityBarrier[];  // pre-sorted by bedImpact desc (stable)
  barrierSummary: BarrierSummary;
  recoById: Record<string, GroundedReco>;
  defaultReco: GroundedReco;
}

/** Stable sort by bedImpact desc; preserves the curated order for ties (matches the mockup rank). */
export function sortCapacityBarriers(barriers: CapacityBarrier[]): CapacityBarrier[] {
  return [...barriers].sort((a, b) => b.bedImpact - a.bedImpact);
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
  // 8 discharge candidates (Medicine A relief). The two canonical golden-thread
  // recos (med-a-spitex, med-a-rehab) back the two READY candidates so the insight
  // chain + dca→bmca handoff stay intact; the rest route to the discharge-gap playbook.
  candidates: [
    { id: 'med-a-spitex', patientId: 'PT-4471', ward: 'Medicine A', readiness: 'READY', blocker: '', estFreeHours: 2, estFreeLabel: '< 2h', bedsFreeable: 4, recoId: 'med-a-spitex' },
    { id: 'cand-4488', patientId: 'PT-4488', ward: 'Medicine A', readiness: 'BLOCKED', blocker: 'TTO meds pending', estFreeHours: 4, estFreeLabel: '4h', bedsFreeable: 1, recoId: 'discharge-gap' },
    { id: 'cand-4501', patientId: 'PT-4501', ward: 'Medicine A', readiness: 'BLOCKED', blocker: 'Transport not booked', estFreeHours: 3, estFreeLabel: '3h', bedsFreeable: 1, recoId: 'discharge-gap' },
    { id: 'cand-4459', patientId: 'PT-4459', ward: 'ICU', readiness: 'BLOCKED', blocker: 'HDU step-down bed', estFreeHours: 6, estFreeLabel: '6h', bedsFreeable: 1, recoId: 'discharge-gap' },
    { id: 'cand-4423', patientId: 'PT-4423', ward: 'Surgery B', readiness: 'PENDING', blocker: 'Consultant sign-off', estFreeHours: 8, estFreeLabel: 'today', bedsFreeable: 1, recoId: 'discharge-gap' },
    { id: 'cand-4510', patientId: 'PT-4510', ward: 'Medicine A', readiness: 'BLOCKED', blocker: 'Spitex placement', estFreeHours: 24, estFreeLabel: '24h', bedsFreeable: 1, recoId: 'med-a-spitex' },
    { id: 'med-a-rehab', patientId: 'PT-4467', ward: 'Cardiology', readiness: 'READY', blocker: '', estFreeHours: 2, estFreeLabel: '< 2h', bedsFreeable: 1, recoId: 'med-a-rehab' },
    { id: 'cand-4495', patientId: 'PT-4495', ward: 'Medicine A', readiness: 'BLOCKED', blocker: 'Family transport', estFreeHours: 5, estFreeLabel: '5h', bedsFreeable: 1, recoId: 'discharge-gap' },
  ],
  // Pre-sorted by bedImpact desc (stable). Mockup rank 1..5:
  //   patient-transport (2) > take-home-meds > icu-step-down > consultant-signoff > spitex-home-care (all 1)
  barriers: [
    { id: 'patient-transport', name: 'Patient transport', description: '2 patients · Medicine A · PT-4501, PT-4495', bedImpact: 2, icon: 'transport', owner: 'Transport desk', wait: 'stuck 4h', waitTone: 'watch', action: 'clears today', recoId: 'discharge-gap' },
    { id: 'take-home-meds', name: 'Take-home meds (TTO)', description: '1 patient · Medicine A · PT-4488', bedImpact: 1, icon: 'meds', owner: 'Pharmacy', wait: 'stuck 2h', waitTone: 'ok', action: 'by 14:00', recoId: 'discharge-gap' },
    { id: 'icu-step-down', name: 'ICU step-down', description: '1 patient · ICU → HDU · PT-4459', bedImpact: 1, impactLabel: '1 ICU', icon: 'stepdown', owner: 'HDU / bed mgmt', wait: 'stuck 6h', waitTone: 'watch', action: 'clears today', recoId: 'discharge-gap' },
    { id: 'consultant-signoff', name: 'Consultant sign-off', description: '1 patient · Surgery B · PT-4423', bedImpact: 1, icon: 'signoff', owner: 'On-call consultant', wait: 'stuck 3h', waitTone: 'watch', action: 'by 17:00', recoId: 'discharge-gap' },
    { id: 'spitex-home-care', name: 'Spitex home-care', description: '1 patient · Medicine A · PT-4510 · longest lead', bedImpact: 1, icon: 'homecare', owner: 'Spitex liaison', wait: 'stuck 20h', waitTone: 'over', action: 'within 24h', agingRisk: true, recoId: 'med-a-spitex' },
  ],
  // Display roll-up for the barriers header: 2 ready now, 6 blocked across 5 barriers, 8 beds recoverable.
  barrierSummary: { readyNow: 2, blocked: 6, barriers: 5, bedsRecoverable: 8 },
  recoById,
  defaultReco,
};

