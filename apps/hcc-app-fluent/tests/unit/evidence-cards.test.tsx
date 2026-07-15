import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { cardRegistry } from '../../src/whiteboard/CardRegistry';
import {
  buildEvidenceCards,
  loadEvidenceDataset,
  evidenceLayouts,
} from '../../src/data/evidence/evidence-service';
import {
  provenanceIssue,
  EvidenceProvenanceFooter,
} from '../../src/cards/evidence/_provenance';
import type { CardType } from '../../src/cards/card-types';

const EVIDENCE_TYPES: CardType[] = [
  'BomCard',
  'AdrCard',
  'PrdRequirementCard',
  'GaEvidenceCard',
  'DependencyEdge',
];

function renderFooter(provenance: unknown) {
  return render(
    <FluentProvider theme={webLightTheme}>
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      <EvidenceProvenanceFooter provenance={provenance as any} />
    </FluentProvider>,
  );
}

describe('Evidence cards (Sprint 14.1 T5)', () => {
  it('registers the five evidence card types', () => {
    for (const type of EVIDENCE_TYPES) {
      expect(cardRegistry[type]).toBeDefined();
      expect(typeof cardRegistry[type]).toBe('function');
    }
  });

  it('dataset meets the presenter-whiteboard card contract (>=25 BOM, >=10 ADR, >=1 PRD)', () => {
    const d = loadEvidenceDataset();
    expect(d.boms.length).toBeGreaterThanOrEqual(25);
    expect(d.adrs.length).toBeGreaterThanOrEqual(10);
    expect(d.requirements.length).toBeGreaterThanOrEqual(1);
    expect(d.dependencies.length).toBeGreaterThanOrEqual(1);
  });

  it('preset layouts render the whole catalog and every card resolves via the registry', () => {
    // BVA preset is a boardroom-focused view (Sprint 15.4 mini-scope) and is
    // covered by its own assertion; skip it here.
    for (const layout of evidenceLayouts().filter((l) => l.key !== 'bva')) {
      const counts = layout.cards.reduce<Record<string, number>>((acc, c) => {
        acc[c.type] = (acc[c.type] ?? 0) + 1;
        return acc;
      }, {});
      expect(counts.BomCard).toBeGreaterThanOrEqual(25);
      expect(counts.AdrCard).toBeGreaterThanOrEqual(10);
      expect(counts.PrdRequirementCard).toBeGreaterThanOrEqual(1);
      expect(counts.DependencyEdge).toBeGreaterThanOrEqual(1);
      for (const card of layout.cards) {
        expect(cardRegistry[card.type]).toBeDefined();
      }
    }
  });

  it('the ga-parity preset adds GA-evidence cards', () => {
    const chNorth = buildEvidenceCards('ch-north-tshow');
    const gaParity = buildEvidenceCards('ga-parity');
    expect(chNorth.some((c) => c.type === 'GaEvidenceCard')).toBe(false);
    expect(gaParity.some((c) => c.type === 'GaEvidenceCard')).toBe(true);
  });

  it('the bva preset renders the BVA card cluster (Sprint 15.4 mini-scope)', () => {
    const bva = buildEvidenceCards('bva');
    const counts = bva.reduce<Record<string, number>>((acc, c) => {
      acc[c.type] = (acc[c.type] ?? 0) + 1;
      return acc;
    }, {});
    expect(counts.BvaHeadlineKpiCard).toBeGreaterThanOrEqual(2);
    expect(counts.BvaPlanVsActualCard).toBe(1);
    expect(counts.BvaTrendCard).toBe(1);
    // The BVA preset is a boardroom-focused view — no BOM/ADR/req cards.
    expect(counts.BomCard).toBeUndefined();
    expect(counts.AdrCard).toBeUndefined();
    expect(counts.PrdRequirementCard).toBeUndefined();
    // Every BVA card must still resolve via the registry.
    for (const card of bva) {
      expect(cardRegistry[card.type]).toBeDefined();
    }
    // The layout iterator surfaces the new preset key.
    const layoutKeys = evidenceLayouts().map((l) => l.key);
    expect(layoutKeys).toContain('bva');
  });

  it('every evidence card payload carries provenance (sourceUrl + asOf)', () => {
    for (const card of buildEvidenceCards('ga-parity')) {
      const p = (card.payload as { provenance: { sourceUrl: string; asOf: string } }).provenance;
      expect(provenanceIssue(p)).toBeNull();
    }
  });

  it('contains no PHI identifiers', () => {
    const serialized = JSON.stringify(loadEvidenceDataset()).toLowerCase();
    expect(serialized).not.toMatch(/geburtsdatum|\bssn\b|756\.\d{4}\.\d{4}\.\d{2}/);
  });
});

describe('Evidence provenance contract (Sprint 14.1 T5)', () => {
  it('provenanceIssue flags missing sourceUrl and asOf', () => {
    expect(provenanceIssue({ sourceUrl: 'x', asOf: '2026-07-10' })).toBeNull();
    expect(provenanceIssue({ sourceUrl: '', asOf: '2026-07-10' })).toBe('missing sourceUrl');
    expect(provenanceIssue({ sourceUrl: 'x', asOf: '' })).toBe('missing asOf');
    expect(provenanceIssue(null)).toBe('missing provenance');
  });

  it('renders a visible error state (not silent) when provenance is missing', () => {
    renderFooter({ sourceUrl: '', asOf: '' });
    const alert = screen.getByRole('alert');
    expect(alert).toBeInTheDocument();
    expect(alert.getAttribute('data-provenance-error')).toBe('true');
  });

  it('renders the source link + asOf when provenance is complete', () => {
    renderFooter({ sourceUrl: 'https://example.com/x', sourcePath: 'docs/x.md', asOf: '2026-07-10' });
    expect(screen.queryByRole('alert')).toBeNull();
    const link = screen.getByRole('link', { name: 'docs/x.md' });
    expect(link.getAttribute('href')).toBe('https://example.com/x');
    expect(screen.getByText(/as of 2026-07-10/)).toBeInTheDocument();
  });
});
