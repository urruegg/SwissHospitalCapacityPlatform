import { Badge, Caption1 } from '@fluentui/react-components';
import { CardShell } from '../_shared';
import { EvidenceProvenanceFooter } from './_provenance';
import type { CardModel } from '../card-types';
import type { GaEvidenceCardPayload } from '../../data/evidence/evidence-types';

/**
 * Sprint 14.1 · T5 — GA-evidence card. Resource × region maturity chip
 * (GA / Preview / NotAvailable) + `asOf` + verifier, with a provenance footer
 * pointing at the curated availability fact (design spec §5).
 */
function maturityColor(maturity: string): 'success' | 'warning' | 'danger' {
  if (maturity === 'GA') return 'success';
  if (maturity === 'Preview') return 'warning';
  return 'danger';
}

export function GaEvidenceCard({ card }: { card: CardModel<GaEvidenceCardPayload> }) {
  const p = card.payload;
  return (
    <CardShell title={p.bomId} subtitle={p.region} testId="GaEvidenceCard">
      <Badge appearance="tint" color={maturityColor(p.maturity)}>
        {p.maturity}
      </Badge>
      <Caption1 as="p">verified by {p.verifiedBy}</Caption1>
      <EvidenceProvenanceFooter provenance={p.provenance} />
    </CardShell>
  );
}
