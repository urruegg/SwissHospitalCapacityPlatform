import { Caption1, tokens } from '@fluentui/react-components';
import type { BvaProvenance } from '../../data/bva/bva-evidence';

/**
 * Sprint 15 · T7 — shared BVA provenance footer.
 *
 * Every BVA card renders its `source` + `asOf` so a board figure is never shown
 * without its lineage. When the Sprint 14 Evidence tab is unavailable the
 * `powerBiEmbedFallback` flag is surfaced so the presenter knows the figure is
 * served via the Power BI embed fallback (design spec §14).
 */
export function ProvenanceFooter({ provenance }: { provenance: BvaProvenance }) {
  const asOf = provenance.asOf.slice(0, 10);
  return (
    <Caption1 style={{ color: tokens.colorNeutralForeground3, display: 'block', marginTop: tokens.spacingVerticalXS }}>
      {provenance.source} · as of {asOf}
      {provenance.powerBiEmbedFallback ? ' · Power BI embed fallback' : ''}
    </Caption1>
  );
}
