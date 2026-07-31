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
 * These are grounded in `docs/BVA.md` (the reviewed ROM BVA document) and are
 * intentionally distinct from `bvaHeadlineKpis` (headline KPI tiles) and
 * `bvaTrend` (a month-over-month trend) — never rebrand one group as another.
 */

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

const SEMANTIC_MODEL = 'capacity-dashboard.SemanticModel · bva_measures';
const AS_OF = '2026-06-30T02:00:00Z';

/** `docs/BVA.md` is the governance-reviewed ROM document (no live gold table
 * backs value levers, sensitivity scenarios, or governance targets yet), so
 * these are cited straight from the doc rather than through the Power BI
 * embed-fallback semantic model path `stamp()` uses. */
const BVA_DOC = 'docs/BVA.md';
const BVA_DOC_AS_OF = '2026-07-28T00:00:00Z';

function stamp(source: string): BvaProvenance {
  return { source, asOf: AS_OF, powerBiEmbedFallback: true };
}

function docStamp(section: string): BvaProvenance {
  return { source: `${BVA_DOC} · ${section}`, asOf: BVA_DOC_AS_OF, powerBiEmbedFallback: false };
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
    measure: 'Net Value Realized (3yr)',
    value: '4.2M',
    unit: 'CHF',
    rag: 'good',
    targetLabel: 'Benefit realization 78%',
    ...stamp(`${SEMANTIC_MODEL} · gold.bva_fact_value_realization`),
  },
  {
    measure: 'ROI %',
    value: '212',
    unit: '%',
    rag: 'good',
    targetLabel: 'Net annual benefit CHF 1.4M',
    ...stamp(`${SEMANTIC_MODEL} · gold.bva_fact_value_realization`),
  },
];

export const bvaPlanVsActual: BvaPlanVsActualPayload = {
  measure: 'Actual TCO (Annualized) vs Budget',
  plan: 760000,
  actual: 738000,
  variancePct: -2.9,
  currency: 'CHF',
  ...stamp(`${SEMANTIC_MODEL} · gold.bva_fact_budget`),
};

export const bvaTrend: BvaTrendPayload = {
  measure: 'Cost per Copilot Turn',
  unit: 'CHF',
  desiredDirection: 'down',
  points: [
    { label: 'Apr', value: 0.42 },
    { label: 'May', value: 0.38 },
    { label: 'Jun', value: 0.34 },
  ],
  ...stamp(`${SEMANTIC_MODEL} · gold.bva_fact_azure_consumption`),
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
    annualBenefit: 1650000,
    currency: 'CHF',
    valueLogic:
      'Faster coordination and discharge readiness decisions increase effective bed turnover',
    ...docStamp('Value Levers and Annual Benefit Assumptions'),
  },
  {
    id: 'command-center-productivity',
    lever: 'Improved command-center productivity',
    annualBenefit: 980000,
    currency: 'CHF',
    valueLogic: '120 peak users with reduced manual triage and faster decisions',
    ...docStamp('Value Levers and Annual Benefit Assumptions'),
  },
  {
    id: 'staffing-overtime-reduction',
    lever: 'Reduced overtime and agency premium through better demand visibility',
    annualBenefit: 620000,
    currency: 'CHF',
    valueLogic: 'Forecast-informed planning reduces expensive reactive staffing',
    ...docStamp('Value Levers and Annual Benefit Assumptions'),
  },
  {
    id: 'integration-reliability',
    lever: 'Lower integration and coordination failure cost',
    annualBenefit: 350000,
    currency: 'CHF',
    valueLogic: 'Better outbound/inbound workflow reliability and fewer manual recoveries',
    ...docStamp('Value Levers and Annual Benefit Assumptions'),
  },
  {
    id: 'compliance-audit-efficiency',
    lever: 'Compliance and audit preparation efficiency gain',
    annualBenefit: 220000,
    currency: 'CHF',
    valueLogic: 'Evidence-ready controls reduce recurring compliance and audit effort',
    ...docStamp('Value Levers and Annual Benefit Assumptions'),
  },
];

/**
 * Distinct sensitivity-scenario evidence — `docs/BVA.md` §"Sensitivity
 * Analysis". Three named what-if ranges (Conservative / Base ROM / Upside),
 * each carrying its own benefit, run cost, 3-year TCO, and 3-year ROI. Do not
 * reuse `bvaTrend.points` (a month-over-month trend) for a "sensitivity" UI —
 * they are a different evidence group with different semantics.
 */
export const bvaSensitivityScenarios: BvaSensitivityScenarioPayload[] = [
  {
    id: 'conservative',
    scenario: 'Conservative',
    annualBenefit: 2600000,
    annualRunCost: 1320000,
    threeYearTco: 5260000,
    threeYearRoiPct: 48,
    currency: 'CHF',
    comment: 'Lower operational uptake and slower process adoption',
    ...docStamp('Sensitivity Analysis'),
  },
  {
    id: 'base-rom',
    scenario: 'Base ROM',
    annualBenefit: 3820000,
    annualRunCost: 1250000,
    threeYearTco: 5050000,
    threeYearRoiPct: 127,
    currency: 'CHF',
    comment: 'Balanced adoption and expected improvement profile',
    ...docStamp('Sensitivity Analysis'),
  },
  {
    id: 'upside',
    scenario: 'Upside',
    annualBenefit: 5000000,
    annualRunCost: 1230000,
    threeYearTco: 4990000,
    threeYearRoiPct: 201,
    currency: 'CHF',
    comment: 'Strong adoption and larger throughput gains',
    ...docStamp('Sensitivity Analysis'),
  },
];

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
