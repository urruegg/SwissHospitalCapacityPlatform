/**
 * Sprint 20 (parity) — enriched Staffing dataset served THROUGH the data
 * layer (not hardcoded in a component). Flagged `simulated` until the Sprint 22
 * golden-source medallion is populated. Encodes the pinned golden-thread slice:
 * "1 surge bed enabled, residual site balanced (ring closed)".
 *
 * Golden-thread numbers (FROZEN):
 *   bedsShort=1, surgeBedsEnabled=1, residualBeds=0
 * The residual 0 closes the ring: bmca −3 → orsa −1 → sba 0 (balanced).
 */
import type { GroundedReco } from '../../copilot-rail/reco';

export interface StaffMove {
  id: string;
  fromUnit: string;
  toUnit: string;
  role: string;         // e.g. "RN"
  fte: number;
  bedsEnabled: number;  // surge beds this move enables
  shiftGap: string;     // e.g. "07:00-15:00"
  recoId: string;       // key in recoById
}

export interface StaffingLever {
  id: string;
  label: string;
  bedsEnabled: number;  // surge-bed coverage impact of applying this lever
  detail: string;
  recoId: string;
}

export interface StaffingPayload {
  bedsShort: number;        // carried from orsa (1)
  surgeBedsEnabled: number; // surge beds unlocked by staffing (1)
  residualBeds: number;     // surgeBedsEnabled - bedsShort (0 = balanced)
  moves: StaffMove[];
  levers: StaffingLever[];  // ranked by bedsEnabled desc, stable tie-break by id
  recoById: Record<string, GroundedReco>;
  defaultReco: GroundedReco;
}

const AGENT_LABEL = 'Staffing Copilot';
const CITES = ['gold.staff_schedule', 'gold.fact_capacity_baseline'];

const recoById: Record<string, GroundedReco> = {
  'rn-icu-to-meda': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'RN: ICU float → Medicine A — 1 surge bed',
      qualifiers: ['1 bed enabled', 'SURGE'],
      status: 'SURGE',
      tone: 'ok',
    },
    read:
      'Moving one RN from the ICU float pool to Medicine A enables the 1-bed surge slot for the ' +
      'morning shift (07:00-15:00). The ICU float pool retains sufficient cover at current census.',
    levers: [
      {
        text: 'Confirm RN reallocation: ICU float → Medicine A (07:00-15:00)',
        impact: { label: '+1 bed', tone: 'beds' },
      },
      {
        text: 'Notify ICU charge nurse and Medicine A ward coordinator',
        impact: { label: 'Zero risk', tone: 'status' },
      },
    ],
    primaryCta: { label: 'Confirm RN move to Medicine A', kind: 'action' },
    projection: '1 surge bed enabled by 07:00',
    citations: CITES,
    provenance: 'simulated',
  },
  'hca-surg-to-medb': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'HCA: Surgery B → Medicine B — coverage',
      qualifiers: ['0.5 FTE support', 'COVERAGE'],
      status: 'COVERAGE',
      tone: 'ok',
    },
    read:
      'Moving 0.5 FTE HCA from Surgery B to Medicine B provides afternoon coverage support (14:00-22:00). ' +
      'Surgery B can absorb the reduced cover at scheduled census.',
    levers: [
      {
        text: 'Confirm HCA reallocation: Surgery B → Medicine B (14:00-22:00)',
        impact: { label: '0.5 FTE', tone: 'status' },
      },
      {
        text: 'Notify Surgery B charge nurse and Medicine B coordinator',
        impact: { label: 'Zero risk', tone: 'status' },
      },
    ],
    primaryCta: { label: 'Confirm HCA move to Medicine B', kind: 'action' },
    projection: 'Coverage maintained for 14:00-22:00 shift',
    citations: CITES,
    provenance: 'simulated',
  },
  'orsa-coverage': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: '→ orsa ✓ ORSA deferrals covered',
      qualifiers: ['2 cases deferred confirmed', 'RING-CLOSED'],
      status: 'COVERED',
      tone: 'ok',
    },
    read:
      'The 2 OR cases deferred by orsa-agent (ortho knee + hernia) are confirmed covered by staffing ' +
      'reallocation. Post-op beds freed by ORSA are now matched by the RN surge-bed move. Ring closed.',
    levers: [
      {
        text: 'Send coverage confirmation to orsa-agent for ortho knee + hernia deferrals',
        impact: { label: 'Ring closed', tone: 'routing' },
      },
      {
        text: 'Update bed board — 2 post-op beds freed, 1 surge bed enabled',
        impact: { label: 'Net −0 beds', tone: 'status' },
      },
    ],
    primaryCta: { label: 'Confirm coverage to orsa-agent', kind: 'action' },
    projection: 'ORSA deferrals acknowledged; site balance ring closed at residual 0',
    citations: CITES,
    provenance: 'simulated',
  },
  'staffing-gap': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Site staffing: balanced (residual 0)',
      qualifiers: ['1 surge bed enabled', '0 residual beds'],
      status: '0 beds',
      tone: 'ok',
    },
    read:
      'The staffing balance agent has closed the ring: 1 surge bed enabled by RN reallocation to Medicine A, ' +
      'site is balanced (residual 0). ORSA deferrals are confirmed covered. ' +
      'For escalation of a concurrent crisis scenario, hand off to csa-agent.',
    levers: [
      {
        text: 'Confirm RN reallocation to Medicine A (+1 surge bed)',
        impact: { label: '+1 bed', tone: 'beds' },
      },
      {
        text: 'Confirm HCA coverage to Medicine B (afternoon shift)',
        impact: { label: '0.5 FTE', tone: 'status' },
      },
      {
        text: 'Escalate concurrent crisis scenario to csa-agent',
        impact: { label: '→ csa-agent', tone: 'routing' },
      },
    ],
    primaryCta: {
      label: 'Escalate to crisis planning (csa-agent)',
      kind: 'handoff',
      target: 'csa-agent',
    },
    projection: 'Site balanced at residual 0; csa-agent on standby for crisis scenarios',
    citations: CITES,
    provenance: 'simulated',
  },
};

const defaultReco: GroundedReco = {
  agentLabel: AGENT_LABEL,
  contextChip: {
    subject: 'Site balanced — residual 0',
    tone: 'ok',
  },
  read:
    'Staffing balance closed the ring: 1 surge bed enabled (RN reallocation to Medicine A, 07:00-15:00), ' +
    'site is balanced at residual 0. ORSA deferrals are covered. For crisis-scenario escalation, ' +
    'hand off to csa-agent.',
  levers: [
    {
      text: 'Confirm RN reallocation: ICU float → Medicine A (+1 surge bed)',
      impact: { label: '+1 bed', tone: 'beds' },
    },
    {
      text: 'Confirm HCA coverage: Surgery B → Medicine B (afternoon)',
      impact: { label: '0.5 FTE', tone: 'status' },
    },
    {
      text: 'Escalate concurrent crisis scenario to csa-agent',
      impact: { label: '→ csa-agent', tone: 'routing' },
    },
  ],
  primaryCta: {
    label: 'Escalate to crisis planning (csa-agent)',
    kind: 'handoff',
    target: 'csa-agent',
  },
  projection: '1 surge bed enabled; site balanced (residual 0)',
  citations: CITES,
  provenance: 'simulated',
};

/** Stable sort: bedsEnabled desc, tie-break by id (mirrors sortReslotLevers in or-steering-data). */
export function sortStaffingLevers(levers: StaffingLever[]): StaffingLever[] {
  return [...levers].sort((a, b) => b.bedsEnabled - a.bedsEnabled || a.id.localeCompare(b.id));
}

export const STAFFING_PINNED: StaffingPayload = {
  bedsShort: 1,
  surgeBedsEnabled: 1,
  residualBeds: 0, // MUST be 0: closes the ring (bmca −3 → orsa −1 → sba 0)
  moves: [
    {
      id: 'rn-icu-to-meda',
      fromUnit: 'ICU float',
      toUnit: 'Medicine A',
      role: 'RN',
      fte: 1,
      bedsEnabled: 1,
      shiftGap: '07:00-15:00',
      recoId: 'rn-icu-to-meda',
    },
    {
      id: 'hca-surg-to-medb',
      fromUnit: 'Surgery B',
      toUnit: 'Medicine B',
      role: 'HCA',
      fte: 0.5,
      bedsEnabled: 0,
      shiftGap: '14:00-22:00',
      recoId: 'hca-surg-to-medb',
    },
  ],
  // Pre-sorted by bedsEnabled desc, stable tie-break by id.localeCompare:
  //   move-rn-icu (1) > confirm-orsa (0, 'c') > escalate-csa (0, 'e') > move-hca-surg (0, 'm')
  levers: [
    {
      id: 'move-rn-icu',
      label: 'Move RN: ICU float → Medicine A (07:00-15:00)',
      bedsEnabled: 1,
      detail: 'RN from ICU float pool covers Medicine A morning surge slot — enables 1 surge bed',
      recoId: 'rn-icu-to-meda',
    },
    {
      id: 'confirm-orsa',
      label: '→ orsa ✓ Confirm ORSA deferrals covered',
      bedsEnabled: 0,
      detail: 'Acknowledge that 2 ORSA-deferred cases (ortho knee + hernia) are staffing-covered; ring closed',
      recoId: 'orsa-coverage',
    },
    {
      id: 'escalate-csa',
      label: '→ csa Escalate to crisis planning',
      bedsEnabled: 0,
      detail: 'Forward concurrent crisis scenario to csa-agent if residual crisis risk materialises',
      recoId: 'staffing-gap',
    },
    {
      id: 'move-hca-surg',
      label: 'Move HCA: Surgery B → Medicine B (14:00-22:00)',
      bedsEnabled: 0,
      detail: 'HCA coverage support for Medicine B afternoon shift — no direct surge-bed impact',
      recoId: 'hca-surg-to-medb',
    },
  ],
  recoById,
  defaultReco,
};
