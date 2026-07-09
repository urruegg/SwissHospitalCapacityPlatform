import { Body1, Caption1, tokens } from '@fluentui/react-components';
import { CardShell } from '../_shared';
import { ragColors } from '../../theme/helvion-theme';
import { ProvenanceFooter } from './_provenance';
import type { CardModel } from '../card-types';
import type { BvaTrendPayload } from '../../data/bva/bva-evidence';

/**
 * Sprint 15 · T7 — BVA trend card. Renders a compact bar sparkline of a monthly
 * measure and RAG-colours the latest move against the desired direction
 * (design spec §6/§7 — e.g. CTO cost-per-turn trending down is good).
 */
export function BvaTrendCard({ card }: { card: CardModel<BvaTrendPayload> }) {
  const p = card.payload;
  const values = p.points.map((pt) => pt.value);
  const max = Math.max(...values, 0) || 1;
  const first = values[0] ?? 0;
  const last = values[values.length - 1] ?? 0;
  const improving = p.desiredDirection === 'down' ? last <= first : last >= first;
  const accent = ragColors[improving ? 'good' : 'bad'];
  return (
    <CardShell title={card.title} subtitle={p.measure} accent={accent} testId="BvaTrendCard">
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: '6px', height: '48px' }}>
        {p.points.map((pt) => (
          <div key={pt.label} style={{ textAlign: 'center', flex: 1 }}>
            <div
              style={{
                height: `${Math.round((pt.value / max) * 40)}px`,
                background: accent,
                borderRadius: '2px',
              }}
            />
            <Caption1 style={{ color: tokens.colorNeutralForeground3 }}>{pt.label}</Caption1>
          </div>
        ))}
      </div>
      <Body1>
        {last}
        {p.unit ? ` ${p.unit}` : ''} · {improving ? 'on track' : 'off track'} (
        {p.desiredDirection})
      </Body1>
      <ProvenanceFooter provenance={p} />
    </CardShell>
  );
}
