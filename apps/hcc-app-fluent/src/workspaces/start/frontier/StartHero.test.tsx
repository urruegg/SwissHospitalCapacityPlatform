import '../../../i18n';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../../i18n';
import { bvaHeadlineKpis } from '../../../data/bva/bva-evidence';
import { setPreferredSource } from '../../../data/data-source';
import * as goldenSourceClient from '../../../data/roleboard/golden-source-client';
import { GOLDEN_THREAD_SCOPE } from '../../../journey/golden-thread';
import { StartHero } from './StartHero';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

beforeEach(async () => {
  await i18n.changeLanguage('en');
  setPreferredSource('simulated');
});

afterEach(() => {
  vi.restoreAllMocks();
  setPreferredSource('simulated');
});

function renderHero(mode: 'demo' | 'user' = 'demo') {
  return render(
    <MemoryRouter>
      <FluentProvider theme={webLightTheme}>
        <StartHero mode={mode} />
      </FluentProvider>
    </MemoryRouter>,
  );
}

function metricPattern(value: string, unit?: string) {
  return new RegExp(unit ? `${value}\\s+${unit}` : value);
}

function selectExpectedHeroEvidence() {
  const netValueRealized = bvaHeadlineKpis.find((payload) => payload.measure === 'Net Value Realized (3yr)');
  const roi = bvaHeadlineKpis.find((payload) => payload.measure === 'ROI %');
  if (!netValueRealized) {
    throw new Error('Test fixture missing Net Value Realized (3yr) KPI');
  }
  if (!roi?.targetLabel) {
    throw new Error('Test fixture missing ROI % KPI targetLabel');
  }
  return {
    netValueRealized,
    roi: { ...roi, targetLabel: roi.targetLabel },
    figures: [
      `${netValueRealized.value} ${netValueRealized.unit}`.trim(),
      `${roi.value} ${roi.unit}`.trim(),
      roi.targetLabel,
    ],
  };
}

function expectedHeroCaptions(
  label: string,
  asOfPrefix: (payload: (typeof bvaHeadlineKpis)[number]) => string,
) {
  const expected = selectExpectedHeroEvidence();
  return [
    `${label} · ${expected.netValueRealized.source} · ${asOfPrefix(expected.netValueRealized)}`,
    `${label} · ${expected.roi.source} · ${asOfPrefix(expected.roi)}`,
    `${label} · ${expected.roi.source} · ${asOfPrefix(expected.roi)}`,
  ];
}

describe('StartHero', () => {
  it('renders exactly three non-duplicated hero figures from the approved BVA evidence fields and the live site-capacity summary', async () => {
    const summary = await goldenSourceClient.loadSiteCapacitySummary(GOLDEN_THREAD_SCOPE, 'demo');
    const expected = selectExpectedHeroEvidence();
    renderHero();

    expect(await screen.findByText(new RegExp(summary.peakWard, 'i'))).toBeInTheDocument();

    expect(screen.getByRole('heading', { name: /See the squeeze before it happens/i })).toBeInTheDocument();
    expect(screen.getByText(metricPattern(expected.netValueRealized.value, expected.netValueRealized.unit))).toBeInTheDocument();
    expect(screen.getByText(metricPattern(expected.roi.value, expected.roi.unit))).toBeInTheDocument();
    expect(screen.getAllByTestId('hero-metric-figure').map((node) => node.textContent?.trim())).toEqual(
      expected.figures,
    );
    expect(new Set(expected.figures).size).toBe(3);
    expect(screen.getAllByText(expected.roi.targetLabel)).toHaveLength(1);
    expect(screen.getAllByTestId('hero-metric-caption').map((node) => node.textContent?.trim())).toEqual(
      expectedHeroCaptions('ROM estimate', (payload) => `as of ${payload.asOf.slice(0, 10)}`),
    );

    expect(screen.getAllByText(new RegExp(`${summary.peakPct}%`))).not.toHaveLength(0);
    expect(screen.getByText(new RegExp(String(Math.abs(summary.siteGapBeds))))).toBeInTheDocument();
    expect(screen.getByText(summary.provenance === 'live' ? /live data/i : /simulated data/i)).toBeInTheDocument();

    // Only the secondary CTA remains a real navigation link to Backstage; the
    // primary CTA now scrolls to the hospitals section (button, not a link).
    const backstageLinks = screen.getAllByRole('link');
    expect(backstageLinks.every((link) => link.getAttribute('href') === '/backstage')).toBe(true);
    expect(screen.getByRole('button', { name: /meet the three hospitals/i })).toBeInTheDocument();
  });

  it('localizes the hero provenance caption', async () => {
    await i18n.changeLanguage('de');
    vi.spyOn(goldenSourceClient, 'loadSiteCapacitySummary').mockImplementation(
      () => new Promise(() => {}),
    );

    renderHero();

    expect(screen.getAllByTestId('hero-metric-caption').map((node) => node.textContent?.trim())).toEqual(
      expectedHeroCaptions('ROM-Schätzung', (payload) => `Stand ${payload.asOf.slice(0, 10)}`),
    );
  });

  it('shows an explicit loading state while the capacity summary is pending', () => {
    vi.spyOn(goldenSourceClient, 'loadSiteCapacitySummary').mockImplementation(
      () => new Promise(() => {}),
    );

    renderHero();

    expect(screen.getByText(/Loading site capacity/i)).toBeInTheDocument();
  });

  it('renders the mockup Swiss-hands quote without disturbing the tested hook heading', () => {
    renderHero();

    expect(screen.getByTestId('hero-quote')).toHaveTextContent(
      /every patient.s path, in swiss hands\./i,
    );
    // Regression guard: the S37 hook heading remains the primary hero headline.
    expect(
      screen.getByRole('heading', { name: /See the squeeze before it happens/i }),
    ).toBeInTheDocument();
  });
});
