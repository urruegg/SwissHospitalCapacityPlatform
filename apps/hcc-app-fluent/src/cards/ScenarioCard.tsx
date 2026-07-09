import { Body1, Badge } from '@fluentui/react-components';
import { CardShell } from './_shared';
import type { CardModel } from './card-types';

export interface ScenarioCardPayload {
  scenario: string;
  status: 'draft' | 'running' | 'evaluated';
  summary: string;
}

/** Sprint 13 T3 — crisis/scenario summary card (mock; CSA wizard lands Sprint 16). */
export function ScenarioCard({ card }: { card: CardModel<ScenarioCardPayload> }) {
  return (
    <CardShell title={card.title} subtitle={card.payload.scenario} testId="ScenarioCard">
      <Badge appearance="outline">{card.payload.status}</Badge>
      <Body1 as="p">{card.payload.summary}</Body1>
    </CardShell>
  );
}
