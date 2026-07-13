import { Badge, Caption1, tokens } from '@fluentui/react-components';
import { CardShell } from '../_shared';
import { ragColors } from '../../theme/helvion-theme';
import { EvidenceProvenanceFooter } from './_provenance';
import type { CardModel } from '../card-types';
import type { BomCardPayload, ReadinessResult } from '../../data/evidence/evidence-types';

/**
 * Sprint 14.1 · T5 — BOM item card. Resource name + type + region-availability
 * chip + dependency count, with readiness chips per track and a provenance
 * footer (design spec §5).
 */
function readinessColor(r?: ReadinessResult): string {
  if (!r) return ragColors.neutral;
  return r.status === 'Ready' ? ragColors.good : ragColors.bad;
}

export function BomCard({ card }: { card: CardModel<BomCardPayload> }) {
  const p = card.payload;
  const chip = p.regionChip;
  return (
    <CardShell title={p.name} subtitle={p.type} testId="BomCard">
      <div style={{ display: 'flex', gap: tokens.spacingHorizontalXS, flexWrap: 'wrap' }}>
        <Badge appearance="tint" color="informative">
          {p.category}
        </Badge>
        {chip ? (
          <Badge appearance="tint" color={chip.maturity === 'GA' ? 'success' : 'warning'}>
            {chip.region} · {chip.maturity}
          </Badge>
        ) : (
          <Badge appearance="tint" color="danger">
            no region fact
          </Badge>
        )}
        <Badge appearance="outline">{p.dependencyCount} deps</Badge>
      </div>
      <div style={{ display: 'flex', gap: tokens.spacingHorizontalXS, marginTop: tokens.spacingVerticalXS }}>
        <Caption1 style={{ color: readinessColor(p.readiness.tShow) }}>
          T-SHOW: {p.readiness.tShow?.status ?? 'n/a'}
        </Caption1>
        <Caption1 style={{ color: readinessColor(p.readiness.tProd) }}>
          T-PROD: {p.readiness.tProd?.status ?? 'n/a'}
        </Caption1>
      </div>
      <EvidenceProvenanceFooter provenance={p.provenance} />
    </CardShell>
  );
}
