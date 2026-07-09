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

const SEMANTIC_MODEL = 'capacity-dashboard.SemanticModel · bva_measures';
const AS_OF = '2026-06-30T02:00:00Z';

function stamp(source: string): BvaProvenance {
  return { source, asOf: AS_OF, powerBiEmbedFallback: true };
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
