import '../../../i18n';
import { afterEach, beforeAll, beforeEach, describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../../i18n';
import { StartHero } from './StartHero';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

beforeEach(async () => {
  await i18n.changeLanguage('en');
});

afterEach(async () => {
  await i18n.changeLanguage('en');
});

function renderHero() {
  return render(
    <MemoryRouter>
      <FluentProvider theme={webLightTheme}>
        <StartHero />
      </FluentProvider>
    </MemoryRouter>,
  );
}

describe('StartHero', () => {
  it('renders the mockup hero narrative: headline, Journai lead, Swiss-hands quote, trust pills, and CTAs', () => {
    renderHero();

    expect(
      screen.getByRole('heading', { name: /the hospital of the future is a Frontier Firm/i }),
    ).toBeInTheDocument();

    expect(screen.getByTestId('hero-quote')).toHaveTextContent(
      /every patient.s path, in swiss hands\./i,
    );

    // Two links: the external Journai reference in the lead + the Backstage secondary CTA.
    const hrefs = screen.getAllByRole('link').map((link) => link.getAttribute('href'));
    expect(hrefs).toContain('/backstage');
    expect(hrefs).toContain('https://www.journai.ch/');

    // Primary CTA remains a scroll button, not a link.
    expect(screen.getByRole('button', { name: /meet the three hospitals/i })).toBeInTheDocument();

    // Mockup trust pills replace the legacy Fabric/advisory/PHI badges.
    expect(screen.getByText(/advisory-only/i)).toBeInTheDocument();
    expect(screen.getByText(/swiss-resident/i)).toBeInTheDocument();
    expect(screen.getByText(/switzerland north/i)).toBeInTheDocument();
  });

  it('omits the BVA value tiles and the site-capacity aside (single-column mockup hero)', () => {
    renderHero();

    // BVA value tiles (Net Value Realized / ROI % / ROM context) are gone.
    expect(screen.queryByTestId('hero-metric-tile')).toBeNull();
    expect(screen.queryByTestId('hero-metric-figure')).toBeNull();
    expect(screen.queryByTestId('hero-metric-caption')).toBeNull();

    // "Site capacity - next 72h" aside is gone.
    expect(screen.queryByText(/site capacity/i)).toBeNull();
    expect(screen.queryByText(/next 72h/i)).toBeNull();
  });

  it('localizes the hero headline and trust pills in German', async () => {
    await i18n.changeLanguage('de');
    renderHero();

    expect(
      screen.getByRole('heading', { name: /Das Spital der Zukunft ist eine Frontier Firm/i }),
    ).toBeInTheDocument();
    // Exact strings target the pill-label spans only. A loose /Nur beratend/i
    // would also match the German disclaimer ("Nur beratend — für ...").
    expect(screen.getByText('Nur beratend')).toBeInTheDocument();
    expect(screen.getByText('In der Schweiz gehostet')).toBeInTheDocument();
  });
});
