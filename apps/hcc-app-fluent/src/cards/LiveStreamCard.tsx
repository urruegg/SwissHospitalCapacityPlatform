import { Body1, Caption1 } from '@fluentui/react-components';
import { CardShell } from './_shared';
import type { CardModel } from './card-types';

export interface LiveStreamEvent {
  ts: string;
  message: string;
}
export interface LiveStreamCardPayload {
  source: string;
  events: LiveStreamEvent[];
}

/** Sprint 13 T3 — recent live-stream events (mock; real Eventstream is Sprint 14+). */
export function LiveStreamCard({ card }: { card: CardModel<LiveStreamCardPayload> }) {
  return (
    <CardShell title={card.title} subtitle={card.payload.source} testId="LiveStreamCard">
      {card.payload.events.map((e, i) => (
        <Body1 as="p" key={i}>
          <Caption1>{e.ts}</Caption1> — {e.message}
        </Body1>
      ))}
    </CardShell>
  );
}
