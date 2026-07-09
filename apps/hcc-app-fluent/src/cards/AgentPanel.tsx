import { Body1, Badge } from '@fluentui/react-components';
import { CardShell } from './_shared';
import type { CardModel } from './card-types';

export interface AgentPanelPayload {
  agent: string;
  lastRecommendation: string;
}

/** Sprint 13 T3 — surfaces a Sprint 11 agent's latest recommendation (mock). */
export function AgentPanel({ card }: { card: CardModel<AgentPanelPayload> }) {
  return (
    <CardShell title={card.title} subtitle={card.payload.agent} testId="AgentPanel">
      <Badge appearance="tint" color="brand">{card.payload.agent}</Badge>
      <Body1 as="p">{card.payload.lastRecommendation}</Body1>
    </CardShell>
  );
}
