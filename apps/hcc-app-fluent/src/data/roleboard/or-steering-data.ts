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

export interface OrCase {
  id: string;
  specialty: string;
  slot: string;           // e.g. "Tue 08:00"
  bedsImpact: number;     // post-op beds this case would consume
  deferable: boolean;
  bedsProtected: number;  // post-op beds freed by deferring this case
  reslotTo: string;       // target reslot timeframe (empty for non-deferable)
  recoId: string;         // key in recoById (equals id for deferable cases)
}

export interface ReslotLever {
  id: string;
  label: string;
  bedsProtected: number;  // beds freed by applying this lever
  detail: string;
  recoId: string;
}

export interface OrSteeringPayload {
  bedsShort: number;      // carried from bmca (3)
  casesDeferred: number;  // deferable elective cases (2)
  bedsFreed: number;      // post-op beds freed by deferral (2)
  residualBeds: number;   // bedsFreed - bedsShort (-1), forwarded to staffing
  cases: OrCase[];
  levers: ReslotLever[];  // ranked by bedsProtected desc, stable tie-break by id
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
  cases: [
    {
      id: 'ortho-knee-tue',
      specialty: 'Orthopedics',
      slot: 'Tue 08:00',
      bedsImpact: 1,
      deferable: true,
      bedsProtected: 1,
      reslotTo: 'Next Tue 08:00',
      recoId: 'ortho-knee-tue',
    },
    {
      id: 'gen-hernia-tue',
      specialty: 'General surgery',
      slot: 'Tue 10:30',
      bedsImpact: 1,
      deferable: true,
      bedsProtected: 1,
      reslotTo: 'Next Tue 10:30',
      recoId: 'gen-hernia-tue',
    },
    {
      id: 'cardiac-cabg-wed',
      specialty: 'Cardiac surgery',
      slot: 'Wed 07:30',
      bedsImpact: 2,
      deferable: false,
      bedsProtected: 0,
      reslotTo: '',
      recoId: 'or-gap',
    },
  ],
  // Pre-sorted by bedsProtected desc, stable tie-break by id.localeCompare
  // defer-gen-hernia < defer-ortho-knee (both bedsProtected=1)
  levers: [
    {
      id: 'defer-gen-hernia',
      label: 'Defer general surgery hernia repair',
      bedsProtected: 1,
      detail: 'Elective inguinal hernia repair — no acute indication; reschedule to next week',
      recoId: 'gen-hernia-tue',
    },
    {
      id: 'defer-ortho-knee',
      label: 'Defer ortho knee replacement',
      bedsProtected: 1,
      detail: 'Elective knee arthroplasty — stable patient; reschedule to next week',
      recoId: 'ortho-knee-tue',
    },
  ],
  recoById,
  defaultReco,
};
