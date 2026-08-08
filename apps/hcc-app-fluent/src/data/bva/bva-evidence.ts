/**
 * Sprint 15 · T7 — BVA evidence data source for the presenter whiteboard.
 *
 * The Sprint 14 Evidence tab + whiteboard framework were not delivered
 * (Sprint 14 stopped at T3), so per the BVA design spec §14 mitigation the BVA
 * cards render through the existing whiteboard/CardRegistry with a **Power BI
 * embed fallback**: each card carries a provenance stamp (`source`, `asOf`) and
 * points at the boardroom report/model instead of a bespoke Evidence surface.
 *
 * Mock only — real Fabric Gold (`gold.bva_fact_*`) lands when the model is
 * published (T5 gate). Values here mirror the synthetic KPI catalogue
 * (docs/adr/0025-bva-kpi-catalog.md) so the demo is self-consistent. No PHI.
 *
 * Sprint 37 · T3 — added distinct evidence groups for the Start/Frontier BVA
 * decision section (`workspaces/start/frontier/BvaDecisionSection.tsx`):
 * `bvaValueLevers` (value/ROI drivers), `bvaSensitivityScenarios` (named
 * what-if ranges), and `bvaProofPoints` (qualitative governance targets).
 * These are grounded in `docs/BVA.md` (the reviewed BVA document) and are
 * intentionally distinct from `bvaHeadlineKpis` (headline KPI tiles) and
 * `bvaTrend` (a month-over-month trend) — never rebrand one group as another.
 *
 * Sprint 40 — re-baselined to **docs/BVA.md v2.0.0 (Frontier-informed)**. Every
 * figure now flows from the canonical constants in `./bva-figures.ts`, so a
 * later sprint can bind them to Fabric gold tables (`gold.bva_fact_*`) in one
 * place. No PHI.
 */

import {
  BVA_COST_PER_COPILOT_TURN_CHF,
  BVA_CURRENCY,
  BVA_MODEL_VERSION,
  BVA_NET_ANNUAL_BENEFIT,
  BVA_NET_VALUE_3YR_FRONTIER,
  BVA_PAYBACK_MONTHS_FRONTIER,
  BVA_ROI_3YR_FRONTIER_PCT,
  BVA_SCENARIOS,
  BVA_TCO_3YR_FRONTIER,
  BVA_TCO_3YR_ROM,
  BVA_TCO_VARIANCE_PCT,
  BVA_VALUE_LEVERS,
  toMillionsLabel,
} from './bva-figures';

export interface BvaProvenance {
  /** Human-readable source of the figure (Gold table / semantic model). */
  source: string;
  /** ISO-8601 timestamp the figure was computed / last refreshed. */
  asOf: string;
  /** True while the Sprint 14 Evidence tab is unavailable (embed fallback). */
  powerBiEmbedFallback: boolean;
}

export type Rag = 'bad' | 'neutral' | 'good';

export interface BvaHeadlineKpiPayload extends BvaProvenance {
  measure: string;
  value: string;
  unit?: string;
  rag: Rag;
  targetLabel?: string;
}

export interface BvaPlanVsActualPayload extends BvaProvenance {
  measure: string;
  plan: number;
  actual: number;
  /** Signed variance % (actual vs plan); negative = under budget = good. */
  variancePct: number;
  currency: string;
}

export interface BvaTrendPoint {
  label: string;
  value: number;
}

export interface BvaTrendPayload extends BvaProvenance {
  measure: string;
  unit?: string;
  points: BvaTrendPoint[];
  /** 'down' means a downward trend is the desired direction (e.g. unit cost). */
  desiredDirection: 'up' | 'down';
}

/**
 * A distinct ROI/TCO value driver ("value lever"), e.g. from
 * `docs/BVA.md` §"Value Levers and Annual Benefit Assumptions". Never conflate
 * with `BvaHeadlineKpiPayload` (a headline KPI tile) — a lever explains *why*
 * the annual benefit accrues, one row per driver.
 */
export interface BvaValueLeverPayload extends BvaProvenance {
  id: string;
  lever: string;
  annualBenefit: number;
  currency: string;
  /** Qualitative rationale for the ROM benefit assumption — not a figure. */
  valueLogic: string;
}

/**
 * A distinct ROI/TCO sensitivity scenario (range), e.g. from `docs/BVA.md`
 * §"Sensitivity Analysis". Never conflate with `BvaTrendPayload` (a
 * time-series trend) — a scenario is a named what-if range across benefit,
 * run cost, TCO, and ROI, not a month-over-month data point.
 */
export interface BvaSensitivityScenarioPayload extends BvaProvenance {
  id: string;
  scenario: string;
  annualBenefit: number;
  annualRunCost: number;
  threeYearTco: number;
  threeYearRoiPct: number;
  currency: string;
  /** Qualitative narrative for the scenario — not a figure. */
  comment: string;
}

/**
 * A distinct proof/evidence claim that is qualitative by nature (a governance
 * target or threshold, not a computed figure), e.g. from `docs/BVA.md`
 * §"Governance and Risk KPIs". Kept separate from headline KPIs/TCO/levers so
 * the "Proof & evidence" panel never merely re-lists figures shown elsewhere.
 */
export interface BvaProofPointPayload extends BvaProvenance {
  id: string;
  claim: string;
  /** Qualitative target/threshold text — intentionally not a numeric figure. */
  target: string;
  cadence: string;
}

/** `docs/BVA.md` is the governance-reviewed ROM document (no live gold table
 * backs value levers, sensitivity scenarios, or governance targets yet), so
 * these are cited straight from the doc. */
const BVA_DOC = `docs/BVA.md ${BVA_MODEL_VERSION}`;
const BVA_DOC_AS_OF = '2026-08-07T00:00:00Z';

function docStamp(section: string): BvaProvenance {
  return { source: `${BVA_DOC} · ${section}`, asOf: BVA_DOC_AS_OF, powerBiEmbedFallback: false };
}

/** Canonical annual benefit for a value lever id (docs/BVA.md §6 / bva-figures). */
function leverBenefit(id: string): number {
  return BVA_VALUE_LEVERS.find((lever) => lever.id === id)?.annualBenefit ?? 0;
}

/** Variance % → RAG: under/near budget good, mild over neutral, big over bad. */
export function budgetRag(variancePct: number): Rag {
  if (variancePct <= 0) return 'good';
  if (variancePct <= 10) return 'neutral';
  return 'bad';
}

/** Deterministic mock BVA evidence for the presenter whiteboard demo. */
export const bvaHeadlineKpis: BvaHeadlineKpiPayload[] = [
  {
    measure: 'Net value (3-year)',
    value: toMillionsLabel(BVA_NET_VALUE_3YR_FRONTIER),
    unit: BVA_CURRENCY,
    rag: 'good',
    targetLabel: `Frontier-informed · payback ~${BVA_PAYBACK_MONTHS_FRONTIER} mo`,
    ...docStamp('§7.1 ROI and Payback'),
  },
  {
    measure: '3-year ROI',
    value: String(BVA_ROI_3YR_FRONTIER_PCT),
    unit: '%',
    rag: 'good',
    targetLabel: `Net annual benefit ${BVA_CURRENCY} ${toMillionsLabel(BVA_NET_ANNUAL_BENEFIT)}`,
    ...docStamp('§7.1 ROI and Payback'),
  },
];

export const bvaPlanVsActual: BvaPlanVsActualPayload = {
  measure: 'ROM plan (v1.0.1)',
  plan: BVA_TCO_3YR_ROM,
  actual: BVA_TCO_3YR_FRONTIER,
  variancePct: BVA_TCO_VARIANCE_PCT,
  currency: BVA_CURRENCY,
  ...docStamp('§7.1 ROI and Payback'),
};

export const bvaTrend: BvaTrendPayload = {
  measure: 'Cost per Copilot Turn',
  unit: 'CHF',
  desiredDirection: 'down',
  points: [{ label: 'Current', value: BVA_COST_PER_COPILOT_TURN_CHF }],
  ...docStamp('§2 Demand Baseline · §5 Recurring Annual Cost'),
};

/**
 * Distinct value-lever evidence — `docs/BVA.md` §"Value Levers and Annual
 * Benefit Assumptions". Five ROM annual-benefit drivers, each with the
 * qualitative logic behind the assumption. Do not reuse `bvaHeadlineKpis` for
 * a "value levers" UI — they are a different evidence group.
 */
export const bvaValueLevers: BvaValueLeverPayload[] = [
  {
    id: 'bed-day-discharge-throughput',
    lever: 'Reduced avoidable bed-day blocking and discharge delay',
    annualBenefit: leverBenefit('bed-day-discharge-throughput'),
    currency: BVA_CURRENCY,
    valueLogic:
      'Faster coordination and discharge readiness decisions increase effective bed turnover',
    ...docStamp('§6 Business Value Model'),
  },
  {
    id: 'command-center-productivity',
    lever: 'Improved command-center productivity',
    annualBenefit: leverBenefit('command-center-productivity'),
    currency: BVA_CURRENCY,
    valueLogic: '120 peak users with reduced manual triage and faster decisions',
    ...docStamp('§6 Business Value Model'),
  },
  {
    id: 'staffing-overtime-reduction',
    lever: 'Reduced overtime and agency premium through better demand visibility',
    annualBenefit: leverBenefit('staffing-overtime-reduction'),
    currency: BVA_CURRENCY,
    valueLogic: 'Forecast-informed planning reduces expensive reactive staffing',
    ...docStamp('§6 Business Value Model'),
  },
  {
    id: 'integration-reliability',
    lever: 'Lower integration and coordination failure cost',
    annualBenefit: leverBenefit('integration-reliability'),
    currency: BVA_CURRENCY,
    valueLogic: 'Better outbound/inbound workflow reliability and fewer manual recoveries',
    ...docStamp('§6 Business Value Model'),
  },
  {
    id: 'compliance-audit-efficiency',
    lever: 'Compliance and audit preparation efficiency gain',
    annualBenefit: leverBenefit('compliance-audit-efficiency'),
    currency: BVA_CURRENCY,
    valueLogic: 'Evidence-ready controls reduce recurring compliance and audit effort',
    ...docStamp('§6 Business Value Model'),
  },
];

/**
 * Distinct sensitivity-scenario evidence — `docs/BVA.md` §7.2 "Sensitivity —
 * Frontier-informed model". Three named what-if ranges (Conservative / Base
 * (Frontier-informed) / Upside), each carrying its own benefit, run cost,
 * 3-year TCO, and 3-year ROI, built from the canonical `BVA_SCENARIOS`
 * constants. Do not reuse `bvaTrend.points` (a month-over-month trend) for a
 * "sensitivity" UI — they are a different evidence group with different
 * semantics.
 */
const SCENARIO_COMMENTS: Record<string, string> = {
  conservative: 'Lower operational uptake and slower process adoption',
  'base-rom': 'Frontier-informed base case — measured build cost, balanced adoption',
  upside: 'Strong adoption and larger throughput gains',
};

export const bvaSensitivityScenarios: BvaSensitivityScenarioPayload[] = BVA_SCENARIOS.map(
  (scenario) => ({
    id: scenario.id,
    scenario: scenario.label,
    annualBenefit: scenario.annualBenefit,
    annualRunCost: scenario.annualRunCost,
    threeYearTco: scenario.threeYearTco,
    threeYearRoiPct: scenario.threeYearRoiPct,
    currency: BVA_CURRENCY,
    comment: SCENARIO_COMMENTS[scenario.id] ?? '',
    ...docStamp('§7.2 Sensitivity — Frontier-informed model'),
  }),
);

/**
 * Distinct proof/evidence claims — `docs/BVA.md` §"Governance and Risk KPIs".
 * These are qualitative governance targets/thresholds (not figures already
 * shown as KPI tiles, TCO, or levers), kept separate so the "Proof & evidence"
 * panel adds evidence rather than duplicating other panels.
 */
export const bvaProofPoints: BvaProofPointPayload[] = [
  {
    id: 'evidence-completeness',
    claim: 'Evidence completeness for compliance controls',
    target: '100 percent for release gates',
    cadence: 'Monthly',
    ...docStamp('Governance and Risk KPIs'),
  },
  {
    id: 'phi-transfer-violations',
    claim: 'PHI transfer policy violations',
    target: 'Zero tolerated',
    cadence: 'Continuous monitoring',
    ...docStamp('Governance and Risk KPIs'),
  },
  {
    id: 'security-findings-sla',
    claim: 'High-severity security or privacy findings open beyond SLA',
    target: 'Zero tolerated',
    cadence: 'Weekly',
    ...docStamp('Governance and Risk KPIs'),
  },
];
