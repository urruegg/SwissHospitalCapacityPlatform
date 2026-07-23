/**
 * Sprint 20 (parity) — enriched bed-manager dataset served THROUGH the data
 * layer (not hardcoded in a component). Flagged `simulated` until the Sprint 22
 * golden-source medallion is populated. Encodes the pinned golden-thread slice:
 * "7 beds short, 4 beds reallocated, residual site -3 beds" (DCA -7 → BMCA -3).
 *
 * PHI: all patient ids are synthetic PT-xxxx tokens — no real patient data.
 */
import type { GroundedReco } from '../../copilot-rail/reco';

export type PlacementPriority = 'HIGH' | 'MED' | 'LOW';
export type SlaRisk = 'HIGH' | 'MED' | 'LOW' | 'OK';

export interface PlacementRequest {
  id: string;
  patientId: string;       // PHI-safe synthetic: PT-xxxx
  fromWard: string;
  toWard: string;
  priority: PlacementPriority;
  waitMin: number;          // minutes in queue
  recoId: string;
}

export interface PlacementBarrier {
  id: string;
  label: string;
  bedImpact: number;
  detail: string;
  recoId: string;
}

export interface BedReallocation {
  id: string;
  fromWard: string;
  toWard: string;
  beds: number;
}

export interface BedManagerPayload {
  bedsShort: number;         // carried from dca (7)
  bedsReallocated: number;   // absorbed via reallocations (4)
  residualBeds: number;      // bedsReallocated - bedsShort (-3), forwarded to orsa
  reallocations: BedReallocation[];
  placements: PlacementRequest[];
  barriers: PlacementBarrier[];   // pre-sorted by bedImpact desc; component re-sorts for live data
  utilPct: number;                // site-level bed utilisation (%)
  freeBeds: number;               // absolute free bed count
  targetFree: number;             // minimum free-bed target
  slaRisk: SlaRisk;               // SLA risk level
  admissions: { id: string; ts: string; message: string; kind: 'admit' | 'discharge' }[];
  powerBiEmbed: { reportName: string; embedPlaceholder: string };
  recoById: Record<string, GroundedReco>;
  defaultReco: GroundedReco;
}

const AGENT_LABEL = 'Bed Management Copilot';
const CITES = ['gold.bed_assignment', 'gold.fact_capacity_baseline'];

const recoById: Record<string, GroundedReco> = {
  'move-pt-4001': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Surgery A → ICU',
      qualifiers: ['PT-4001', 'HIGH'],
      status: 'HIGH',
      tone: 'over',
    },
    read:
      'PT-4001 requires ICU step-up from Surgery A. ICU has 1 flex bed available ' +
      'following the PT-3002 step-down completed at 10:45.',
    levers: [
      {
        text: 'Confirm ICU bed assignment and notify ward coordinator',
        impact: { label: '-1 wait', tone: 'time' },
      },
      {
        text: 'Pre-position anaesthesia team for handover',
        impact: { label: 'Safe transition', tone: 'trust' },
      },
    ],
    primaryCta: { label: 'Execute transfer PT-4001', kind: 'action' },
    projection: 'Transfer complete within 20 min',
    citations: CITES,
    provenance: 'simulated',
  },
  'move-pt-4002': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Medicine A → Cardiology',
      qualifiers: ['PT-4002', 'MED'],
      status: 'MED',
      tone: 'watch',
    },
    read:
      'PT-4002 is stable for step-down to Cardiology (74% utilisation, 4 free beds). ' +
      'Move frees 1 Medicine A bed needed for an incoming Surgery A transfer.',
    levers: [
      {
        text: 'Request Cardiology bed from charge nurse',
        impact: { label: '+1 Med A bed', tone: 'beds' },
      },
    ],
    primaryCta: { label: 'Initiate step-down transfer', kind: 'action' },
    projection: '+1 Medicine A bed within 1h',
    citations: CITES,
    provenance: 'simulated',
  },
  'move-pt-4003-hitl': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Medicine B → Medicine A',
      qualifiers: ['PT-4003', 'HIGH', 'HITL-02'],
      status: 'HITL',
      tone: 'over',
    },
    read:
      'PT-4003 requires a cross-ward transfer with HITL-02 approval (two attending physicians). ' +
      'Both Dr. Schneider and Dr. Meier must sign off before execution.',
    levers: [
      {
        text: 'Route HITL-02 approval request to Dr. Schneider and Dr. Meier',
        impact: { label: 'HITL gate', tone: 'trust' },
      },
      {
        text: 'Pre-arrange transfer equipment and nursing handover notes',
        impact: { label: 'Reduce post-approval lag', tone: 'time' },
      },
    ],
    primaryCta: {
      label: 'Submit HITL-02 approval request',
      kind: 'action',
      requiresApproval: true,
    },
    projection: 'Transfer executable 30 min after HITL-02 approval',
    citations: CITES,
    provenance: 'simulated',
  },
  'move-pt-4004-refused': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Orthopedics → Medicine B',
      qualifiers: ['PT-4004', 'LOW', 'BLOCKED'],
      status: 'BLOCKED',
      tone: 'blocked',
    },
    read:
      'Transfer blocked — Medicine B bed request submitted at 15:40 but awaiting charge nurse ' +
      'approval. No action possible until sign-off received.',
    levers: [],
    primaryCta: { label: 'Awaiting approval — no action available', kind: 'action' },
    citations: CITES,
    provenance: 'simulated',
    refused: true,
  },
  'ward-overflow': {
    agentLabel: AGENT_LABEL,
    contextChip: { subject: 'Ward capacity overflow', qualifiers: ['3 beds'], tone: 'over' },
    read:
      '3 beds blocked by a Surgery A / ICU co-management gap. ' +
      'Confirming step-up criteria for 3 outlier patients frees 3 positions within 2h.',
    levers: [
      {
        text: 'Confirm ICU step-up criteria for 3 Surgery A outliers',
        impact: { label: '+3 beds', tone: 'beds' },
      },
      {
        text: 'Open HDU overflow protocol (2 flex beds available)',
        impact: { label: '+2 buffer', tone: 'buffer' },
      },
    ],
    primaryCta: { label: 'Activate overflow protocol', kind: 'action' },
    projection: '+3 beds freed within 2h',
    citations: CITES,
    provenance: 'simulated',
  },
  'cleaning-backlog': {
    agentLabel: AGENT_LABEL,
    contextChip: { subject: 'Bed cleaning backlog', qualifiers: ['2 beds'], tone: 'watch' },
    read:
      '2 Medicine A beds (12A, 14B) awaiting terminal cleaning. ' +
      'Housekeeping team has a 45-min backlog — escalating priority frees both beds within 1h.',
    levers: [
      {
        text: 'Escalate cleaning priority for Medicine A beds 12A and 14B',
        impact: { label: '-45 min wait', tone: 'time' },
      },
    ],
    primaryCta: { label: 'Escalate to housekeeping supervisor', kind: 'action' },
    projection: '2 beds available within 1h',
    citations: CITES,
    provenance: 'simulated',
  },
  'approval-pending': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Transfer approval pending',
      qualifiers: ['1 bed', 'HITL'],
      tone: 'pending',
    },
    read:
      '1 bed transfer (PT-4004 to Medicine B) awaiting charge nurse sign-off since 15:40. ' +
      'A reminder escalation unblocks the transfer.',
    levers: [
      {
        text: 'Send reminder to charge nurse (pager 4412)',
        impact: { label: 'Unblock transfer', tone: 'trust' },
      },
    ],
    primaryCta: { label: 'Escalate approval reminder', kind: 'action' },
    projection: '1 bed freed after approval',
    citations: CITES,
    provenance: 'simulated',
  },
  'placement-gap': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Site placement gap',
      qualifiers: ['3 beds short', '-3 residual'],
      status: '-3 beds',
      tone: 'watch',
    },
    read:
      '3 beds remain short after 4 reallocations: 3 blocked by ward overflow, 2 by cleaning ' +
      'backlog, 1 by approval delay. Actioning the top 2 barriers closes the site gap.',
    levers: [
      {
        text: 'Resolve ward overflow — ICU step-up criteria for 3 patients',
        impact: { label: '+3 beds', tone: 'beds' },
      },
      {
        text: 'Clear cleaning backlog — escalate Medicine A priority',
        impact: { label: '+2 beds / 1h', tone: 'beds' },
      },
    ],
    primaryCta: {
      label: 'Hand off residual pressure to OR Steering (orsa)',
      kind: 'handoff',
      target: 'orsa-agent',
    },
    projection: 'Closing top 2 barriers fully covers the -3 residual',
    citations: CITES,
    provenance: 'simulated',
  },
};

const defaultReco: GroundedReco = {
  agentLabel: AGENT_LABEL,
  contextChip: {
    subject: 'Placement gap: 3 beds short, 4 reallocations done',
    tone: 'watch',
  },
  read:
    '4 beds reallocated; site still -3 beds. Top pressures: ward overflow (3 beds), ' +
    'cleaning backlog (2 beds). Actioning both barriers eliminates the residual gap.',
  levers: [
    {
      text: 'Activate ICU overflow protocol — 3 Surgery A patients',
      impact: { label: '+3 beds', tone: 'beds' },
    },
    {
      text: 'Escalate bed cleaning in Medicine A (beds 12A, 14B)',
      impact: { label: '+2 beds / 1h', tone: 'beds' },
    },
    {
      text: 'Expedite HITL-02 approval for PT-4003 transfer',
      impact: { label: '+1 bed / 30 min', tone: 'time' },
    },
  ],
  primaryCta: {
    label: 'Hand off residual pressure to OR Steering (orsa)',
    kind: 'handoff',
    target: 'orsa-agent',
  },
  projection: 'Actioning top 2 barriers covers the full -3 bed residual',
  citations: CITES,
  provenance: 'simulated',
};

/** Stable sort: bedImpact descending; id ascending as tie-breaker. */
export function sortBarriers(barriers: PlacementBarrier[]): PlacementBarrier[] {
  return [...barriers].sort((a, b) => b.bedImpact - a.bedImpact || a.id.localeCompare(b.id));
}

export const BEDMANAGER_PINNED: BedManagerPayload = {
  bedsShort: 7,
  bedsReallocated: 4,
  residualBeds: -3, // MUST be -3 to preserve the golden-thread chain (DCA -7 → BMCA -3)
  reallocations: [
    { id: 'surg-a-to-med-a', fromWard: 'Surgery A', toWard: 'Medicine A', beds: 2 },
    { id: 'surg-b-to-med-a', fromWard: 'Surgery B', toWard: 'Medicine A', beds: 1 },
    { id: 'ortho-to-med-b', fromWard: 'Orthopedics', toWard: 'Medicine B', beds: 1 },
  ],
  placements: [
    {
      id: 'place-pt-4001',
      patientId: 'PT-4001',
      fromWard: 'Surgery A',
      toWard: 'ICU',
      priority: 'HIGH',
      waitMin: 45,
      recoId: 'move-pt-4001',
    },
    {
      id: 'place-pt-4002',
      patientId: 'PT-4002',
      fromWard: 'Medicine A',
      toWard: 'Cardiology',
      priority: 'MED',
      waitMin: 30,
      recoId: 'move-pt-4002',
    },
    {
      id: 'place-pt-4003',
      patientId: 'PT-4003',
      fromWard: 'Medicine B',
      toWard: 'Medicine A',
      priority: 'HIGH',
      waitMin: 60,
      recoId: 'move-pt-4003-hitl',
    },
    {
      id: 'place-pt-4004',
      patientId: 'PT-4004',
      fromWard: 'Orthopedics',
      toWard: 'Medicine B',
      priority: 'LOW',
      waitMin: 15,
      recoId: 'move-pt-4004-refused',
    },
  ],
  barriers: [
    {
      id: 'ward-overflow',
      label: 'Ward capacity overflow',
      bedImpact: 3,
      detail: '3 beds blocked by Surgery A / ICU co-management gap',
      recoId: 'ward-overflow',
    },
    {
      id: 'cleaning-backlog',
      label: 'Bed cleaning backlog',
      bedImpact: 2,
      detail: '2 Medicine A beds awaiting terminal cleaning (12A, 14B)',
      recoId: 'cleaning-backlog',
    },
    {
      id: 'approval-pending',
      label: 'Transfer approval pending',
      bedImpact: 1,
      detail: '1 transfer awaiting charge nurse sign-off (HITL gate)',
      recoId: 'approval-pending',
    },
  ],
  utilPct: 87,
  freeBeds: 18,
  targetFree: 12,
  slaRisk: 'HIGH',
  admissions: [
    { id: 'adm-01', ts: '11:02', message: 'Zugang Station A — PT-4005', kind: 'admit' },
    { id: 'adm-02', ts: '11:06', message: 'Austritt Station C — PT-3008', kind: 'discharge' },
    { id: 'adm-03', ts: '11:14', message: 'Zugang Station B — PT-4006', kind: 'admit' },
    { id: 'adm-04', ts: '11:21', message: 'Austritt Station A — PT-1009', kind: 'discharge' },
  ],
  powerBiEmbed: {
    reportName: 'capacity-dashboard',
    embedPlaceholder: 'Power BI Embed (Direct Lake, RLS by hospital) — mock',
  },
  recoById,
  defaultReco,
};

// Backward-compatibility alias — golden-source-client.ts imports this name.
export const BED_MANAGER_PINNED = BEDMANAGER_PINNED;
