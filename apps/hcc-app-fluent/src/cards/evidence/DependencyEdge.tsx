import { Badge, Caption1, tokens } from '@fluentui/react-components';
import { CardShell } from '../_shared';
import { EvidenceProvenanceFooter } from './_provenance';
import type { CardModel } from '../card-types';
import type { DependencyEdgePayload } from '../../data/evidence/evidence-types';

/**
 * Sprint 14.1 · T5 — Dependency edge card. The Sprint 13 custom canvas has no
 * native edge primitive (docs/adr/0021-whiteboard-base-*), so a directed
 * dependency (`requires` / `hosts` / `grounds` / `binds` / `governs`) is
 * rendered as its own card that names both endpoints (design spec §5).
 */
export function DependencyEdge({ card }: { card: CardModel<DependencyEdgePayload> }) {
  const p = card.payload;
  return (
    <CardShell title={`${p.fromId} → ${p.toId}`} subtitle="dependency" testId="DependencyEdge">
      <Badge appearance="tint" color="brand">
        {p.type}
      </Badge>
      <Caption1 as="p" style={{ marginTop: tokens.spacingVerticalXS }}>
        {p.fromId} <b>{p.type}</b> {p.toId}
      </Caption1>
      <EvidenceProvenanceFooter provenance={p.provenance} />
    </CardShell>
  );
}
