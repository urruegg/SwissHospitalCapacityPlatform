import { Badge, Body1, Caption1 } from '@fluentui/react-components';
import { CardShell } from '../_shared';
import { EvidenceProvenanceFooter } from './_provenance';
import type { CardModel } from '../card-types';
import type { AdrCardPayload } from '../../data/evidence/evidence-types';

/**
 * Sprint 14.1 · T5 — ADR card. ADR id + title + status + one-line decision, with
 * a provenance footer pointing at the ADR file (design spec §5).
 */
function statusColor(status: string): 'success' | 'warning' | 'subtle' {
  if (status === 'Accepted') return 'success';
  if (status === 'Superseded') return 'warning';
  return 'subtle';
}

export function AdrCard({ card }: { card: CardModel<AdrCardPayload> }) {
  const p = card.payload;
  return (
    <CardShell title={p.id} subtitle={p.title} testId="AdrCard">
      <Badge appearance="tint" color={statusColor(p.status)}>
        {p.status}
      </Badge>
      <Body1 as="p">
        <Caption1>{p.decisionSummary}</Caption1>
      </Body1>
      <EvidenceProvenanceFooter provenance={p.provenance} />
    </CardShell>
  );
}
