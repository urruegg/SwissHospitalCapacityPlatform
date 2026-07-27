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

/** Coverage status per shift (drives the STATUS badge). */
export type ShiftStatus = 'GAP' | 'FILLED' | 'PENDING' | 'WATCH';

export interface StaffMove {
  id: string;           // internal key; the two golden-thread moves keep their canonical ids
  shiftNo: string;      // display shift number, e.g. 'SH-4402'
  time: string;         // shift time, e.g. '14–22'
  window: string;       // shift window/period, e.g. 'Late', 'Night', 'Twilight'
  fromUnit: string;
  toUnit: string;
  role: string;         // short role token used by the insight, e.g. 'RN' | 'HCA'
  skill: string;        // display skill, e.g. 'RN oncology'
  fte: number;
  covers: string;       // what this shift covers, e.g. '+2 beds · orsa'
  status: ShiftStatus;  // coverage status badge
  bedsEnabled: number;  // surge beds this move enables
  recoId: string;       // key in recoById
}

/** Leading glyph per staffing lever. */
export type StaffLeverIcon = 'skillmatch' | 'float' | 'overtime' | 'buddy' | 'agency';

export interface StaffingLever {
  id: string;
  label: string;
  description: string;   // one-line context
  bedsEnabled: number;   // surge-bed coverage impact (drives bar + sort)
  impactLabel?: string;  // overrides the "N beds" label, e.g. 'hold 3', 'resilience', 'reserve'
  icon: StaffLeverIcon;  // leading glyph
  owner: string;         // responsible queue/team
  timing: string;        // e.g. 'tightest', 'shift now', 'opt-in', 'buddy', '££ cost'
  timingTone: 'ok' | 'watch' | 'over'; // dot colour: green | amber | red
  window: string;        // right-side action/route, e.g. 'hold RN', 'reassign', 'via csa'
  critical?: boolean;    // 'CRITICAL' badge
  lastResort?: boolean;  // 'LAST RESORT' badge
  handoffTo?: string;    // cross-agent handoff, e.g. 'csa'
  recoId: string;
}

/** Header roll-up for the staffing levers board (display, derived from the levers). */
export interface StaffLeverSummary {
  oncologyToSecure: number; // time-critical oncology shifts still to secure
  generalCovered: number;   // general shifts already covered
  bedsStaffed: number;      // beds staffed across the staffing levers
}

export interface StaffingPayload {
  bedsShort: number;        // carried from orsa (1)
  surgeBedsEnabled: number; // surge beds unlocked by staffing (1)
  residualBeds: number;     // surgeBedsEnabled - bedsShort (0 = balanced)
  moves: StaffMove[];
  levers: StaffingLever[];  // pre-sorted by bedsEnabled desc (stable)
  leverSummary: StaffLeverSummary;
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
        evidence: {
          summary: '0.5 FTE HCA cover moved Surgery B → Medicine B (14:00-22:00).',
          detail: ['Role: Health-care assistant (HCA)', 'Surgery B absorbs reduced cover at scheduled census'],
          people: ['M. Frei (HCA)', 'S. Huber (HCA, 0.5)'],
          citations: ['hcp:CareTeam', 'gold.staff_schedule'],
        },
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

/** Stable sort by bedsEnabled desc; preserves the curated order for ties (matches the mockup rank). */
export function sortStaffingLevers(levers: StaffingLever[]): StaffingLever[] {
  return [...levers].sort((a, b) => b.bedsEnabled - a.bedsEnabled);
}

export const STAFFING_PINNED: StaffingPayload = {
  bedsShort: 1,
  surgeBedsEnabled: 1,
  residualBeds: 0, // MUST be 0: closes the ring (bmca −3 → orsa −1 → sba 0)
  // 6 coverage-worklist shifts (Medicine A relief). The two golden-thread
  // canonical moves (rn-icu-to-meda, hca-surg-to-medb) keep their ids/fields so
  // the insight chain + sba→csa ring stay intact; the rest are display shifts
  // that route to the staffing playbook when clicked.
  moves: [
    { id: 'sh-4402', shiftNo: 'SH-4402', time: '14–22', window: 'Late', fromUnit: 'Bank', toUnit: 'Medicine A', role: 'RN', skill: 'RN oncology', fte: 1, covers: '+2 beds · orsa', status: 'GAP', bedsEnabled: 0, recoId: 'staffing-gap' },
    { id: 'rn-icu-to-meda', shiftNo: 'SH-4401', time: '14–22', window: 'Late', fromUnit: 'ICU float', toUnit: 'Medicine A', role: 'RN', skill: 'RN general', fte: 1, covers: '+1 bed · bmca', status: 'FILLED', bedsEnabled: 1, recoId: 'rn-icu-to-meda' },
    { id: 'sh-4403', shiftNo: 'SH-4403', time: '22–07', window: 'Night', fromUnit: 'Ward pool', toUnit: 'Medicine A', role: 'RN', skill: 'RN general', fte: 1, covers: '+3 rollover', status: 'PENDING', bedsEnabled: 0, recoId: 'staffing-gap' },
    { id: 'hca-surg-to-medb', shiftNo: 'SH-4404', time: '14–22', window: 'Late', fromUnit: 'Surgery B', toUnit: 'Medicine B', role: 'HCA', skill: 'HCA support', fte: 0.5, covers: 'surge +3', status: 'FILLED', bedsEnabled: 0, recoId: 'hca-surg-to-medb' },
    { id: 'sh-4405', shiftNo: 'SH-4405', time: '14–22', window: 'Late', fromUnit: 'Surgery B', toUnit: 'Surgery B', role: 'RN', skill: 'RN · Surgery B', fte: 1, covers: 'orsa redirect', status: 'WATCH', bedsEnabled: 0, recoId: 'orsa-coverage' },
    { id: 'sh-4406', shiftNo: 'SH-4406', time: '17–01', window: 'Twilight', fromUnit: 'Float pool', toUnit: 'Medicine A', role: 'RN', skill: 'RN flex', fte: 0.5, covers: 'peak overlap', status: 'FILLED', bedsEnabled: 0, recoId: 'staffing-gap' },
  ],
  // Pre-sorted by bedsEnabled desc (stable). Mockup rank 1..5:
  //   oncology-skillmatch (2) > float-pool (1) > voluntary-ot (1) > cross-cover-buddy (0) > agency-bank (0)
  levers: [
    {
      id: 'oncology-skillmatch',
      label: 'Oncology skill-match',
      description: 'secure the 1 free oncology-competent RN for OR-3307 / OR-3308 post-op · Medicine A late',
      bedsEnabled: 2,
      icon: 'skillmatch',
      owner: 'Staffing office',
      timing: 'tightest',
      timingTone: 'over',
      window: 'hold RN',
      critical: true,
      recoId: 'staffing-gap',
    },
    {
      id: 'float-pool',
      label: 'Float-pool reallocation',
      description: 'pull 1 general RN from Surgery A (low-pressure) to Medicine A late · covers bmca RQ-2208',
      bedsEnabled: 1,
      icon: 'float',
      owner: 'Float pool',
      timing: 'shift now',
      timingTone: 'ok',
      window: 'reassign',
      recoId: 'rn-icu-to-meda',
    },
    {
      id: 'voluntary-ot',
      label: 'Voluntary overtime',
      description: 'incentive OT fills the night rollover + HCA surge · 2 staff opted in · SH-4403, SH-4404',
      bedsEnabled: 1,
      impactLabel: 'hold 3',
      icon: 'overtime',
      owner: 'Charge nurse',
      timing: 'opt-in',
      timingTone: 'watch',
      window: 'confirm',
      recoId: 'staffing-gap',
    },
    {
      id: 'cross-cover-buddy',
      label: 'Cross-cover buddy',
      description: 'pair a general RN on Surgery B with oncology charge oversight · backfills the orsa redirect · SH-4405',
      bedsEnabled: 0,
      impactLabel: 'resilience',
      icon: 'buddy',
      owner: 'Ward lead',
      timing: 'buddy',
      timingTone: 'ok',
      window: 'pair',
      recoId: 'orsa-coverage',
    },
    {
      id: 'agency-bank',
      label: 'Agency / bank',
      description: 'only if internal levers slip · cost + lead-time · pressure-test via csa before booking',
      bedsEnabled: 0,
      impactLabel: 'reserve',
      icon: 'agency',
      owner: 'Staffing office',
      timing: '££ cost',
      timingTone: 'over',
      window: 'via csa',
      lastResort: true,
      handoffTo: 'csa',
      recoId: 'staffing-gap',
    },
  ],
  // Display roll-up for the levers header: 2 oncology to secure, 1 general covered, 3 beds staffed.
  leverSummary: { oncologyToSecure: 2, generalCovered: 1, bedsStaffed: 3 },
  recoById,
  defaultReco,
};
