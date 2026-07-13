import { Badge, Caption1, tokens } from '@fluentui/react-components';
import { CardShell } from '../_shared';
import { EvidenceProvenanceFooter } from './_provenance';
import type { CardModel } from '../card-types';
import type { PrdRequirementCardPayload } from '../../data/evidence/evidence-types';

/**
 * Sprint 14.1 · T5 — PRD requirement card. Requirement id + family + title +
 * MVP flag, with a provenance footer pointing at docs/PRD.md (design spec §5).
 */
export function PrdRequirementCard({ card }: { card: CardModel<PrdRequirementCardPayload> }) {
  const p = card.payload;
  return (
    <CardShell title={p.id} subtitle={p.family} testId="PrdRequirementCard">
      <div style={{ display: 'flex', gap: tokens.spacingHorizontalXS, flexWrap: 'wrap' }}>
        <Badge appearance="tint" color="informative">
          {p.kind}
        </Badge>
        {p.mvp ? (
          <Badge appearance="tint" color="success">
            MVP
          </Badge>
        ) : (
          <Badge appearance="outline">post-MVP</Badge>
        )}
      </div>
      <Caption1 as="p">{p.title}</Caption1>
      <EvidenceProvenanceFooter provenance={p.provenance} />
    </CardShell>
  );
}
