import { Body1 } from '@fluentui/react-components';
import { CardShell } from './_shared';
import type { CardModel } from './card-types';

export interface PowerBITilePayload {
  reportName: string;
  embedPlaceholder: string;
}

/** Sprint 13 T3 — Power BI embed tile (mock: shows the report name + placeholder). */
export function PowerBITile({ card }: { card: CardModel<PowerBITilePayload> }) {
  return (
    <CardShell title={card.title} subtitle={card.payload.reportName} testId="PowerBITile">
      <Body1>{card.payload.embedPlaceholder}</Body1>
    </CardShell>
  );
}
