import { Title2, Caption1 } from '@fluentui/react-components';
import { CardShell } from './_shared';
import { ragColors } from '../theme/curavias-theme';
import type { CardModel } from './card-types';

export type Rag = 'bad' | 'neutral' | 'good';
export interface KpiCardPayload {
  value: string;
  unit?: string;
  rag: Rag;
  delta?: string;
}

/** Sprint 13 T3 — KPI headline with RAG accent (mock). */
export function KpiCard({ card }: { card: CardModel<KpiCardPayload> }) {
  const accent = ragColors[card.payload.rag];
  return (
    <CardShell title={card.title} accent={accent} testId="KpiCard">
      <Title2 style={{ color: accent }}>
        {card.payload.value}
        {card.payload.unit ? ` ${card.payload.unit}` : ''}
      </Title2>
      {card.payload.delta ? <Caption1>{card.payload.delta}</Caption1> : null}
    </CardShell>
  );
}
