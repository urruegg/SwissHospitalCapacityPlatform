import type { GroundedReco } from '../../copilot-rail/reco';
import type { ChipTone } from '../../copilot-rail/reco';
import type { Provenance } from '../../journey/RoleBoard';

export type WardTrend = 'rising' | 'flat' | 'falling';

export interface WardRow {
  id: string;
  label: string;
  bedsUsed: number;
  bedsTotal: number;
  nowPct: number;
  forecastPct: number;
  trend: WardTrend;
  flag: ChipTone;
  recoId: string;
}

export interface SignalChannel {
  id: string;
  label: string;
}

export interface SpecStream {
  id: string;
  label: string;
  level: ChipTone;
  levelLabel: string;
  fedBy: string[];
  recoId: string;
}

export interface CapacitySummary {
  currentBeds: number;
  currentTotal: number;
  currentPct: number;
  forecastBeds: number;
  forecastTotal: number;
  forecastPct: number;
  gapBeds: number;
}

/**
 * Derived summary of the OccupancyPayload for the START surface teaser.
 * START and OOA share the same golden source so the figures agree.
 */
export interface SiteCapacitySummary {
  /** Ward label with the highest forecastPct in the OccupancyPayload.wards array. */
  peakWard: string;
  /** 72h forecastPct of the peak ward. */
  peakPct: number;
  /**
   * Equals capacity.gapBeds (negative = beds needed at 72h).
   */
  siteGapBeds: number;
  /**
   * Estimated hours until the peak ward breaches 100%.
   * Derivation: linear interpolation across the forecast window —
   *   round(windowHours × (100 − peakWard.nowPct) / (peakWard.forecastPct − peakWard.nowPct))
   * Returns 0 if already ≥ 100%; returns windowHours when no breach is predicted.
   */
  breachEtaHours: number;
  /** The agent that first surfaces this occupancy data. */
  firstSurfacedBy: 'ooa-agent';
  provenance: Provenance;
  /** ISO-8601 timestamp of when this summary was computed. */
  asOf: string;
}

/**
 * Pure aggregation helper — converts an OccupancyPayload into a SiteCapacitySummary.
 * Extracted so it can be unit-tested without I/O mocking.
 *
 * Empty `wards` guard: returns a safe fallback (peakWard='—', peakPct=0,
 * breachEtaHours=windowHours) so the START teaser degrades gracefully if a live
 * backend returns an empty ward list.
 */
export function aggregateSiteCapacity(
  wards: WardRow[],
  capacity: CapacitySummary,
  windowHours: number,
  provenance: Provenance,
  asOf: string,
): SiteCapacitySummary {
  if (wards.length === 0) {
    return {
      peakWard: '—',
      peakPct: 0,
      siteGapBeds: capacity.gapBeds,
      breachEtaHours: windowHours,
      firstSurfacedBy: 'ooa-agent',
      provenance,
      asOf,
    };
  }

  const peak = wards.reduce((a, b) => (b.forecastPct > a.forecastPct ? b : a));

  let breachEtaHours: number;
  if (peak.nowPct >= 100) {
    breachEtaHours = 0;
  } else if (peak.forecastPct > 100) {
    breachEtaHours = Math.round(
      (windowHours * (100 - peak.nowPct)) / (peak.forecastPct - peak.nowPct),
    );
  } else {
    breachEtaHours = windowHours;
  }

  return {
    peakWard: peak.label,
    peakPct: peak.forecastPct,
    siteGapBeds: capacity.gapBeds,
    breachEtaHours,
    firstSurfacedBy: 'ooa-agent',
    provenance,
    asOf,
  };
}

export interface OccupancyPayload {
  siteOccupancyPct: number;
  siteDeltaBeds: number;
  wards: WardRow[];
  channels: SignalChannel[];
  streams: SpecStream[];
  capacity: CapacitySummary;
  recoById: Record<string, GroundedReco>;
  defaultReco: GroundedReco;
}

const AGENT_LABEL = 'Occupancy Copilot';
const CITES = ['gold.fact_capacity_baseline', 'gold.fact_occupancy_forecast'];

const recoById: Record<string, GroundedReco> = {
  'med-a': {
    agentLabel: AGENT_LABEL,
    contextChip: { subject: 'Medicine A', qualifiers: ['forecast'], status: 'OVER', tone: 'over' },
    read: 'Medicine A tips to 102% within 72h - 6 flu admissions inbound against only 2 planned discharges.',
    levers: [
      { text: 'Expedite 6 discharge-ready patients before 17:00', impact: { label: '-6 beds', tone: 'beds' } },
      { text: 'Divert 3 low-acuity admits to Medicine B (8% spare)', impact: { label: '+3 buffer', tone: 'buffer' } },
      { text: 'Flag 2 length-of-stay outliers >9 days for review', impact: { label: '-2 / 48h', tone: 'time' } },
    ],
    primaryCta: { label: 'Open discharge worklist', kind: 'handoff', target: 'dca-agent' },
    projection: '102% -> 94%',
    citations: CITES,
    provenance: 'simulated',
  },
  icu: {
    agentLabel: AGENT_LABEL,
    contextChip: { subject: 'ICU', qualifiers: ['length-of-stay'], status: 'WATCH', tone: 'watch' },
    read: 'ICU runs 1.4 days above median length-of-stay and reaches 95% by Wednesday.',
    levers: [
      { text: 'Confirm 2 step-downs to HDU today', impact: { label: '+2 ICU beds', tone: 'beds' } },
      { text: 'Move 1 elective post-op from Wed to Thu', impact: { label: '>=2 free', tone: 'beds' } },
    ],
    primaryCta: { label: 'Notify ICU charge nurse', kind: 'action' },
    projection: 'Holds ICU at <=88%',
    citations: CITES,
    provenance: 'simulated',
  },
  'surg-b': {
    agentLabel: AGENT_LABEL,
    contextChip: { subject: 'Surgery B', qualifiers: ['electives'], status: 'WATCH', tone: 'watch' },
    read: 'Surgery B climbs to 88% as electives stack against slow post-op discharges.',
    levers: [
      { text: 'Shift 2 electives to the Friday list', impact: { label: '+2 beds Wed', tone: 'beds' } },
      { text: 'Early-discharge 3 day-2 post-ops meeting criteria', impact: { label: '-3 beds', tone: 'beds' } },
    ],
    primaryCta: { label: 'Draft OR reschedule proposal', kind: 'handoff', target: 'orsa-agent' },
    projection: 'Wednesday peak 88% -> 80%',
    citations: CITES,
    provenance: 'simulated',
  },
  cardio: {
    agentLabel: AGENT_LABEL,
    contextChip: { subject: 'Cardiology', qualifiers: ['donor'], status: 'OK', tone: 'ok' },
    read: 'Cardiology stays comfortable at 74% - it can absorb pressure.',
    levers: [
      { text: 'Offer 4 beds as overflow for Medicine A step-downs', impact: { label: '+4 shared', tone: 'routing' } },
    ],
    primaryCta: { label: 'Reserve 4 overflow beds', kind: 'action' },
    projection: 'Adds 4 beds to the relief pool',
    citations: CITES,
    provenance: 'simulated',
  },
  'site-gap': {
    agentLabel: AGENT_LABEL,
    contextChip: { subject: 'Site capacity', qualifiers: ['72h gap'], status: '-16 beds', tone: 'over' },
    read: 'Across all streams the site is 16 beds short in 72h.',
    levers: [
      { text: 'Launch discharge coordination - 8 candidates ready now', impact: { label: '+8 beds', tone: 'beds' } },
      { text: "Reserve Cardiology's 4 overflow beds", impact: { label: '+4 beds', tone: 'beds' } },
      { text: 'Hold 5 elective slots as buffer', impact: { label: '+5 flex', tone: 'buffer' } },
    ],
    primaryCta: { label: 'Hand off to Discharge Coordinator (dca)', kind: 'handoff', target: 'dca-agent' },
    projection: '8 discharge candidates cover 50% of the gap',
    citations: CITES,
    provenance: 'simulated',
  },
};

const defaultReco: GroundedReco = {
  agentLabel: AGENT_LABEL,
  contextChip: { subject: 'Why is pressure rising?', tone: 'signal' },
  read:
    'Medicine A has +6 forecast admissions (flu) vs 2 planned discharges; ICU length-of-stay is 1.4 days ' +
    'above median. Suggested next step: relieve Medicine A.',
  levers: [],
  primaryCta: { label: 'See 8 discharge candidates', kind: 'handoff', target: 'dca-agent' },
  citations: CITES,
  provenance: 'simulated',
};

export const OCCUPANCY_PINNED: OccupancyPayload = {
  siteOccupancyPct: 81,
  siteDeltaBeds: -16,
  wards: [
    { id: 'med-a', label: 'Medicine A', bedsUsed: 34, bedsTotal: 36, nowPct: 94, forecastPct: 102, trend: 'rising', flag: 'over', recoId: 'med-a' },
    { id: 'icu', label: 'ICU', bedsUsed: 11, bedsTotal: 12, nowPct: 92, forecastPct: 95, trend: 'rising', flag: 'watch', recoId: 'icu' },
    { id: 'surg-b', label: 'Surgery B', bedsUsed: 28, bedsTotal: 40, nowPct: 70, forecastPct: 88, trend: 'rising', flag: 'watch', recoId: 'surg-b' },
    { id: 'cardio', label: 'Cardiology', bedsUsed: 20, bedsTotal: 30, nowPct: 67, forecastPct: 74, trend: 'flat', flag: 'ok', recoId: 'cardio' },
  ],
  channels: [
    { id: 'ed-arrivals', label: 'ED arrivals' },
    { id: 'admissions', label: 'Admissions / transfers' },
    { id: 'elective-or', label: 'Elective OR schedule' },
    { id: 'planned-discharges', label: 'Planned discharges' },
    { id: 'los-signal', label: 'Length-of-stay signal' },
    { id: 'staffing-roster', label: 'Staffing roster' },
  ],
  streams: [
    { id: 'emergency', label: 'Emergency & Acute Medicine', level: 'over', levelLabel: 'HIGH', fedBy: ['ed-arrivals', 'admissions', 'los-signal'], recoId: 'med-a' },
    { id: 'surgery', label: 'Surgery & Perioperative', level: 'watch', levelLabel: 'WATCH', fedBy: ['elective-or', 'planned-discharges'], recoId: 'surg-b' },
    { id: 'intensive', label: 'Intensive Care', level: 'watch', levelLabel: 'WATCH', fedBy: ['admissions', 'los-signal', 'staffing-roster'], recoId: 'icu' },
    { id: 'cardiology', label: 'Cardiology', level: 'ok', levelLabel: 'OK', fedBy: ['admissions', 'planned-discharges'], recoId: 'cardio' },
  ],
  capacity: {
    currentBeds: 105,
    currentTotal: 130,
    currentPct: 81,
    forecastBeds: 121,
    forecastTotal: 130,
    forecastPct: 93,
    gapBeds: -16,
  },
  recoById,
  defaultReco,
};