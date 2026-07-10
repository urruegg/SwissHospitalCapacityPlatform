import { Body1, Caption1, tokens } from '@fluentui/react-components';
import { CardShell } from '../_shared';
import { ragColors } from '../../theme/helvion-theme';
import { ProvenanceFooter } from './_provenance';
import { budgetRag } from '../../data/bva/bva-evidence';
import type { CardModel } from '../card-types';
import type { BvaPlanVsActualPayload } from '../../data/bva/bva-evidence';

const fmt = (n: number, currency: string) =>
  `${currency} ${new Intl.NumberFormat('de-CH', { maximumFractionDigits: 0 }).format(n)}`;

/**
 * Sprint 15 · T7 — BVA plan-vs-actual card. Compares budget (plan) to actual
 * spend with a signed variance % (negative = under budget), RAG-coloured, plus
 * a proportional bar. Bound to `gold.bva_fact_budget` (design spec §6 CFO).
 */
export function BvaPlanVsActualCard({ card }: { card: CardModel<BvaPlanVsActualPayload> }) {
  const p = card.payload;
  const accent = ragColors[budgetRag(p.variancePct)];
  const actualPct = p.plan > 0 ? Math.min(100, (p.actual / p.plan) * 100) : 0;
  const sign = p.variancePct > 0 ? '+' : '';
  return (
    <CardShell title={card.title} subtitle={p.measure} accent={accent} testId="BvaPlanVsActualCard">
      <Body1>
        Plan {fmt(p.plan, p.currency)} · Actual {fmt(p.actual, p.currency)}
      </Body1>
      <div
        style={{
          height: '8px',
          borderRadius: '4px',
          background: tokens.colorNeutralBackground4,
          marginTop: tokens.spacingVerticalXS,
        }}
      >
        <div style={{ width: `${actualPct}%`, height: '100%', borderRadius: '4px', background: accent }} />
      </div>
      <Caption1 style={{ color: accent }}>
        Variance {sign}
        {p.variancePct.toFixed(1)}%
      </Caption1>
      <ProvenanceFooter provenance={p} />
    </CardShell>
  );
}
