import { Body1, Persona } from '@fluentui/react-components';
import { CardShell } from './_shared';
import type { CardModel } from './card-types';

export interface ResponsibleCardPayload {
  name: string;
  role: string;
  contact: string;
}

/** Sprint 13 T3 — the accountable person for a ward/board (mock). */
export function ResponsibleCard({ card }: { card: CardModel<ResponsibleCardPayload> }) {
  return (
    <CardShell title={card.title} testId="ResponsibleCard">
      <Persona name={card.payload.name} secondaryText={card.payload.role} />
      <Body1 as="p">{card.payload.contact}</Body1>
    </CardShell>
  );
}
