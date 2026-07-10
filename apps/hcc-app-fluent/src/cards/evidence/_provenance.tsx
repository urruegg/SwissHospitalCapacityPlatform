import { Caption1, tokens } from '@fluentui/react-components';
import type { EvidenceProvenance } from '../../data/evidence/evidence-types';

/**
 * Sprint 14.1 · T5 — Evidence card provenance contract.
 *
 * Every Evidence card MUST render `sourceUrl` + `asOf`. Per design spec §5/§10
 * a card with missing provenance MUST fail visibly (an error state, never a
 * silent render). {@link provenanceIssue} is the pure predicate the unit tests
 * assert; {@link EvidenceProvenanceFooter} renders the footer or the error.
 */

/** Length of an ISO-8601 date prefix (`YYYY-MM-DD`) within an `asOf` timestamp. */
const ISO_DATE_LENGTH = 10;

/** Return a human-readable problem when provenance is incomplete, else null. */
export function provenanceIssue(provenance: EvidenceProvenance | undefined | null): string | null {
  if (!provenance) return 'missing provenance';
  if (!provenance.sourceUrl) return 'missing sourceUrl';
  if (!provenance.asOf) return 'missing asOf';
  return null;
}

export function EvidenceProvenanceFooter({ provenance }: { provenance: EvidenceProvenance }) {
  const issue = provenanceIssue(provenance);
  if (issue) {
    return (
      <Caption1
        role="alert"
        data-provenance-error="true"
        style={{ color: tokens.colorPaletteRedForeground1, display: 'block', marginTop: tokens.spacingVerticalXS }}
      >
        Provenance error — {issue}
      </Caption1>
    );
  }
  const asOf = provenance.asOf.slice(0, ISO_DATE_LENGTH);
  return (
    <Caption1
      data-provenance="true"
      style={{ color: tokens.colorNeutralForeground3, display: 'block', marginTop: tokens.spacingVerticalXS }}
    >
      <a href={provenance.sourceUrl} target="_blank" rel="noreferrer">
        {provenance.sourcePath ?? 'source'}
      </a>{' '}
      · as of {asOf}
    </Caption1>
  );
}
