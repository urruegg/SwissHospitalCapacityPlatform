import type { CardModel } from '../../../../cards/card-types';
import {
  bvaHeadlineKpis,
  bvaPlanVsActual,
  bvaTrend,
} from '../../../../data/bva/bva-evidence';

/**
 * Sprint 15 · T7 — BVA card cluster for the presenter whiteboard.
 *
 * Renders the three BVA card types via the existing CardRegistry (Power BI
 * embed fallback — the Sprint 14 Evidence tab was not delivered; design spec
 * §14). Mock only, no PHI: synthetic board-value aggregates that mirror the KPI
 * catalogue (docs/adr/0025-bva-kpi-catalog.md).
 */
export const bvaBoardCards: CardModel[] = [
  {
    id: 'bva-headline-net-value',
    type: 'BvaHeadlineKpiCard',
    title: 'Net value realized (3yr)',
    position: { x: 24, y: 24 },
    payload: bvaHeadlineKpis[0],
  },
  {
    id: 'bva-headline-roi',
    type: 'BvaHeadlineKpiCard',
    title: 'Return on investment',
    position: { x: 312, y: 24 },
    payload: bvaHeadlineKpis[1],
  },
  {
    id: 'bva-plan-vs-actual-tco',
    type: 'BvaPlanVsActualCard',
    title: 'TCO vs budget',
    position: { x: 600, y: 24 },
    payload: bvaPlanVsActual,
  },
  {
    id: 'bva-trend-cost-per-turn',
    type: 'BvaTrendCard',
    title: 'Cost per copilot turn',
    position: { x: 888, y: 24 },
    payload: bvaTrend,
  },
];
