import { Title2, Caption1 } from '@fluentui/react-components';
import { CardShell } from '../_shared';
import { ragColors } from '../../theme/helvion-theme';
import { ProvenanceFooter } from './_provenance';
import type { CardModel } from '../card-types';
import type { BvaHeadlineKpiPayload } from '../../data/bva/bva-evidence';

/**
 * Sprint 15 · T7 — BVA headline KPI card. Shows a single board-level KPI
 * (e.g. Net Value Realized) with RAG accent, its target context, and a
 * provenance stamp. Bound to the `bva_measures` catalogue (design spec §6/§7).
 */
export function BvaHeadlineKpiCard({ card }: { card: CardModel<BvaHeadlineKpiPayload> }) {
  const p = card.payload;
  const accent = ragColors[p.rag];
  return (
    <CardShell title={card.title} subtitle={p.measure} accent={accent} testId="BvaHeadlineKpiCard">
      <Title2 style={{ color: accent }}>
        {p.value}
        {p.unit ? ` ${p.unit}` : ''}
      </Title2>
      {p.targetLabel ? <Caption1>{p.targetLabel}</Caption1> : null}
      <ProvenanceFooter provenance={p} />
    </CardShell>
  );
}
