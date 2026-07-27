/**
 * Sprint 20 (parity) — enriched OR-steering dataset served THROUGH the data
 * layer (not hardcoded in a component). Flagged `simulated` until the Sprint 22
 * golden-source medallion is populated. Encodes the pinned golden-thread slice:
 * "2 elective cases deferred, bedsFreed=2, residual site −1 beds" (bmca −3 → orsa −1).
 *
 * Golden-thread numbers (FROZEN):
 *   bedsShort=3, casesDeferred=2, bedsFreed=2, residualBeds=−1
 * The −1 residual forwards to sba-agent (Staffing) via the handoff CTA.
 */
import type { GroundedReco } from '../../copilot-rail/reco';

/** Recommended steering action per elective case (drives the ACTION badge). */
export type OrAction = 'DEFER' | 'RESLOT' | 'REDIRECT' | 'PROCEED';

export interface OrCase {
  id: string;             // internal key; the two golden-thread cases keep their canonical ids
  caseNo: string;         // display case number, e.g. 'OR-3301'
  specialty: string;
  slot: string;           // e.g. "Tue 08:00"
  postOp: string;         // post-op ward flagged, e.g. 'Medicine A'
  bedsImpact: number;     // post-op beds this case would consume
  bedsProtected: number;  // post-op beds freed by the recommended action
  action: OrAction;       // recommended steering action (display)
  window: string;         // timing/routing note, e.g. 'low-acuity', '→ Thu off-peak'
  deferable: boolean;     // true = surfaced as a golden-thread insight (the 2 canonical deferrals)
  recoId: string;         // key in recoById
}

/** Leading glyph per reslot lever. */
export type LeverIcon = 'defer' | 'reslot' | 'redirect' | 'proceed';

export interface ReslotLever {
  id: string;
  label: string;
  description: string;    // one-line context
  bedsProtected: number;  // beds freed by applying this lever (0 for must-proceed)
  icon: LeverIcon;        // leading glyph
  owner: string;          // responsible queue/team
  timing: string;         // e.g. 'list Wed', 'Thu slot', 'today', 'OR 07:30'
  timingTone: 'ok' | 'watch' | 'over'; // dot colour: green | amber | red
  window: string;         // right-side routing/timeframe, e.g. 'next week', 'Surgery B', 'via sba'
  mustProceed?: boolean;  // 'MUST PROCEED' badge
  handoffTo?: string;     // cross-agent handoff, e.g. 'sba'
  recoId: string;
}

/** Live incoming-OR-case eventstream item (left pane of the upper lane). */
export interface OrCaseEvent {
  id: string;
  ts: string;
  message: string;
  kind: 'added' | 'urgent' | 'update';
  caseNo: string;    // e.g. 'OR-3307'
  detail: string;    // grounded hover-popover detail
}

/** Header roll-up for the reslot levers board (display, derived from the levers). */
export interface OrLeverSummary {
  bedsProtected: number;  // total elective beds protected across the reslot levers
  proceedCount: number;   // time-critical cases that must proceed
}

export interface OrSteeringPayload {
  bedsShort: number;      // carried from bmca (3)
  casesDeferred: number;  // golden-thread deferable elective cases (2)
  bedsFreed: number;      // post-op beds freed by deferral (2)
  residualBeds: number;   // bedsFreed - bedsShort (-1), forwarded to staffing
  cases: OrCase[];
  levers: ReslotLever[];  // ranked by bedsProtected desc, stable tie-break by id
  liveCases: OrCaseEvent[];
  leverSummary: OrLeverSummary;
  recoById: Record<string, GroundedReco>;
  defaultReco: GroundedReco;
}

const AGENT_LABEL = 'OR Steering Copilot';
const CITES = ['gold.or_schedule', 'gold.fact_capacity_baseline'];

const recoById: Record<string, GroundedReco> = {
  'ortho-knee-tue': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'Ortho knee — reslot to next week',
      qualifiers: ['1 bed protected', 'DEFERABLE'],
      status: 'DEFERABLE',
      tone: 'ok',
    },
    read:
      'The Tuesday 08:00 orthopedic knee replacement is clinically deferrable by one week. ' +
      'Rescheduling to next Tuesday frees 1 post-op bed and moves no urgent procedure.',
    levers: [
      {
        text: 'Contact ortho coordinator — reschedule to Tue 08:00 next week',
        impact: { label: '+1 bed', tone: 'beds' },
      },
      {
        text: 'Notify patient and anaesthesiology team of reslot',
        impact: { label: 'Zero risk', tone: 'status' },
      },
    ],
    primaryCta: { label: 'Confirm ortho reslot', kind: 'action' },
    projection: '1 post-op bed freed by Tuesday 08:00',
    citations: CITES,
    provenance: 'simulated',
  },
  'gen-hernia-tue': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'General surgery hernia — reslot to next week',
      qualifiers: ['1 bed protected', 'DEFERABLE'],
      status: 'DEFERABLE',
      tone: 'ok',
    },
    read:
      'The Tuesday 10:30 inguinal hernia repair is an elective procedure with no acute indication. ' +
      'Rescheduling by one week frees 1 post-op bed with no clinical risk.',
    levers: [
      {
        text: 'Reschedule hernia repair to Tue 10:30 next week via OR booking system',
        impact: { label: '+1 bed', tone: 'beds' },
      },
      {
        text: 'Notify surgical team and patient pre-admission',
        impact: { label: 'Zero risk', tone: 'status' },
      },
    ],
    primaryCta: { label: 'Confirm hernia reslot', kind: 'action' },
    projection: '1 post-op bed freed by Tuesday 10:30',
    citations: CITES,
    provenance: 'simulated',
  },
  'or-gap': {
    agentLabel: AGENT_LABEL,
    contextChip: {
      subject: 'OR site gap',
      qualifiers: ['3 beds short', '−1 residual → staffing'],
      status: '−1 beds',
      tone: 'watch',
    },
    read:
      '3 post-op beds are short across the site. Deferring 2 elective cases (ortho knee + hernia) ' +
      'frees 2 beds, leaving −1 residual gap forwarded to Staffing (sba-agent).',
    levers: [
      {
        text: 'Defer ortho knee replacement (Tue 08:00) — +1 bed',
        impact: { label: '+1 bed', tone: 'beds' },
      },
      {
        text: 'Defer general surgery hernia repair (Tue 10:30) — +1 bed',
        impact: { label: '+1 bed', tone: 'beds' },
      },
      {
        text: 'Escalate −1 residual bed gap to Staffing for surge coverage planning',
        impact: { label: '→ sba-agent', tone: 'routing' },
      },
    ],
    primaryCta: {
      label: 'Hand off residual gap to Staffing (sba)',
      kind: 'handoff',
      target: 'sba-agent',
    },
    projection: '2 deferrals cover 67% of the 3-bed gap; −1 residual passes to sba',
    citations: CITES,
    provenance: 'simulated',
  },
};

const defaultReco: GroundedReco = {
  agentLabel: AGENT_LABEL,
  contextChip: {
    subject: 'OR gap: 2 beds deferrable, −1 residual',
    tone: 'watch',
  },
  read:
    '3 post-op beds are short. Deferring 2 elective cases (ortho knee + hernia) ' +
    'frees 2 beds, leaving −1 residual gap for sba-agent.',
  levers: [
    {
      text: 'Defer ortho knee replacement (Tue 08:00)',
      impact: { label: '+1 bed', tone: 'beds' },
    },
    {
      text: 'Defer general surgery hernia repair (Tue 10:30)',
      impact: { label: '+1 bed', tone: 'beds' },
    },
    {
      text: 'Forward −1 residual to Staffing for surge planning',
      impact: { label: '→ sba-agent', tone: 'routing' },
    },
  ],
  primaryCta: {
    label: 'Hand off residual gap to Staffing (sba)',
    kind: 'handoff',
    target: 'sba-agent',
  },
  projection: '2 deferrals cover 67% of the 3-bed gap; −1 residual passes to sba',
  citations: CITES,
  provenance: 'simulated',
};

/** Stable sort: bedsProtected desc, tie-break by id (mirrors sortBarriers in bed-manager-data). */
export function sortReslotLevers(levers: ReslotLever[]): ReslotLever[] {
  return [...levers].sort((a, b) => b.bedsProtected - a.bedsProtected || a.id.localeCompare(b.id));
}

export const OR_STEERING_PINNED: OrSteeringPayload = {
  bedsShort: 3,
  casesDeferred: 2,
  bedsFreed: 2,
  residualBeds: -1, // MUST be -1 to preserve the golden-thread chain (bmca -3 → orsa -1)
  // 8 elective cases (next 72h) with post-op ward flagged. The two golden-thread
  // canonical deferrals (ortho-knee-tue, gen-hernia-tue) are the only `deferable`
  // cases surfaced as insights; the rest carry a display `action` and route to
  // the or-gap reslot playbook when clicked.
  cases: [
    { id: 'ortho-knee-tue', caseNo: 'OR-3301', specialty: 'Orthopedics', slot: 'Tue 08:00', postOp: 'Medicine A', bedsImpact: 1, bedsProtected: 1, action: 'DEFER', window: 'low-acuity', deferable: true, recoId: 'ortho-knee-tue' },
    { id: 'ortho-hip-tue', caseNo: 'OR-3303', specialty: 'Orthopedics', slot: 'Tue 11:00', postOp: 'Medicine A', bedsImpact: 1, bedsProtected: 1, action: 'DEFER', window: 'low-acuity', deferable: false, recoId: 'or-gap' },
    { id: 'gen-hernia-tue', caseNo: 'OR-3302', specialty: 'General surgery', slot: 'Tue 10:30', postOp: 'Medicine A', bedsImpact: 1, bedsProtected: 1, action: 'DEFER', window: 'follow-up', deferable: true, recoId: 'gen-hernia-tue' },
    { id: 'vascular-wed', caseNo: 'OR-3304', specialty: 'Vascular', slot: 'Wed 09:00', postOp: 'Medicine A', bedsImpact: 1, bedsProtected: 1, action: 'RESLOT', window: '→ Thu off-peak', deferable: false, recoId: 'or-gap' },
    { id: 'gen-colon-wed', caseNo: 'OR-3305', specialty: 'General surgery', slot: 'Wed 13:00', postOp: 'Medicine A', bedsImpact: 1, bedsProtected: 1, action: 'RESLOT', window: '→ Thu off-peak', deferable: false, recoId: 'or-gap' },
    { id: 'urology-today', caseNo: 'OR-3306', specialty: 'Urology', slot: 'Today 14:00', postOp: 'Medicine A', bedsImpact: 1, bedsProtected: 1, action: 'REDIRECT', window: '→ Surgery B', deferable: false, recoId: 'or-gap' },
    { id: 'onco-am', caseNo: 'OR-3307', specialty: 'Oncology', slot: 'Today 07:30', postOp: 'Medicine A', bedsImpact: 1, bedsProtected: 0, action: 'PROCEED', window: 'time-critical', deferable: false, recoId: 'or-gap' },
    { id: 'onco-thu', caseNo: 'OR-3308', specialty: 'Oncology', slot: 'Thu 07:30', postOp: 'Medicine A', bedsImpact: 1, bedsProtected: 0, action: 'PROCEED', window: 'time-critical', deferable: false, recoId: 'or-gap' },
  ],
  // Pre-sorted by bedsProtected desc, stable tie-break by id.localeCompare.
  // Sorted order: defer-ortho, reslot-thu (both 2) → defer-general, redirect-urology
  // (both 1) → proceed-oncology (0), matching the mockup rank 1..5.
  levers: [
    {
      id: 'defer-ortho',
      label: 'Defer low-acuity ortho',
      description: '2 electives post-op → Medicine A · OR-3301, OR-3303 · deferrable, no clinical harm',
      bedsProtected: 2,
      icon: 'defer',
      owner: 'OR scheduling',
      timing: 'list Wed',
      timingTone: 'ok',
      window: 'next week',
      recoId: 'ortho-knee-tue',
    },
    {
      id: 'reslot-thu',
      label: 'Reslot to off-peak (Thu)',
      description: "2 electives can move to Thu's low-pressure block · OR-3304, OR-3305 · no cancellation",
      bedsProtected: 2,
      icon: 'reslot',
      owner: 'Anaesthesia / OR',
      timing: 'Thu slot',
      timingTone: 'ok',
      window: 'Thu',
      recoId: 'or-gap',
    },
    {
      id: 'defer-general',
      label: 'Defer general follow-up',
      description: '1 general-surgery follow-up · OR-3302 · elective, safe to rebook',
      bedsProtected: 1,
      icon: 'defer',
      owner: 'OR scheduling',
      timing: 'list Wed',
      timingTone: 'ok',
      window: 'next week',
      recoId: 'gen-hernia-tue',
    },
    {
      id: 'redirect-urology',
      label: 'Redirect post-op ward',
      description: '1 urology case proceeds today · post-op recovers in Surgery B · OR-3306 · no Med A bed',
      bedsProtected: 1,
      icon: 'redirect',
      owner: 'Surgery B flow',
      timing: 'today',
      timingTone: 'watch',
      window: 'Surgery B',
      recoId: 'or-gap',
    },
    {
      id: 'proceed-oncology',
      label: 'Time-critical oncology',
      description: '2 oncology cases cannot move · OR-3307, OR-3308 · consume 2 Med A beds · guarantee staffing',
      bedsProtected: 0,
      icon: 'proceed',
      owner: 'Oncology / sba',
      timing: 'OR 07:30',
      timingTone: 'over',
      window: 'via sba',
      mustProceed: true,
      handoffTo: 'sba',
      recoId: 'or-gap',
    },
  ],
  liveCases: [
    { id: 'orc-01', ts: '07:12', message: 'OR-3307 hinzugefügt — Onkologie, zeitkritisch', kind: 'urgent', caseNo: 'OR-3307', detail: 'Neuer zeitkritischer Fall · Onkologie · OR 07:30 · Post-op Medicine A' },
    { id: 'orc-02', ts: '07:20', message: 'OR-3304 verschoben — Vaskulär → Donnerstag', kind: 'update', caseNo: 'OR-3304', detail: 'Reslot in die Do-Nebenzeit vorgeschlagen · kein Ausfall · Anästhesie / OR' },
    { id: 'orc-03', ts: '07:34', message: 'OR-3301 gelistet — Orthopädie elektiv', kind: 'added', caseNo: 'OR-3301', detail: 'Elektiver Eingriff · geringe Akuität · deferrable ohne klinischen Schaden' },
    { id: 'orc-04', ts: '07:41', message: 'OR-3306 umgeleitet — Urologie → Chirurgie B', kind: 'update', caseNo: 'OR-3306', detail: 'Post-op Erholung in Chirurgie B · kein Medicine-A-Bett benötigt' },
  ],
  // Display roll-up for the levers header: 2+2+1+1 beds protected, 2 must-proceed.
  leverSummary: { bedsProtected: 6, proceedCount: 2 },
  recoById,
  defaultReco,
};
