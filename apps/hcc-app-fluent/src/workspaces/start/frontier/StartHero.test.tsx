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
  it('renders the marketing-approved hero: headline, art-of-the-possible lead, quote, and framebox', () => {
    renderHero();

    // Headline = ink prefix + green accent, one heading node (spaces inserted between spans).
    expect(
      screen.getByRole('heading', {
        name: /capacity forecasting is where it hurts\.\s*Here is what it looks like solved\./i,
      }),
    ).toBeInTheDocument();

    // Lead emphasis phrase + closing clause.
    expect(screen.getByText(/art-of-the-possible showcase/i)).toBeInTheDocument();
    expect(screen.getByText(/what it would take to make it yours/i)).toBeInTheDocument();

    // Swiss-hands brand quote is retained.
    expect(screen.getByTestId('hero-quote')).toHaveTextContent(
      /every patient.s path, in swiss hands\./i,
    );

    // "Before we start" framebox carries the reality/synthetic/no-PHI framing.
    const framebox = screen.getByTestId('hero-framebox');
    expect(framebox).toHaveTextContent(/before we start/i);
    expect(framebox).toHaveTextContent(/Switzerland North/i);
    expect(framebox).toHaveTextContent(/advisory-only, never deciding or diagnosing/i);
    expect(framebox).toHaveTextContent(/no PHI/i);
    expect(framebox).toHaveTextContent(/Epic core-system simulator/i);
  });

  it('renders the three mockup CTAs and drops the legacy Journai lead + trust pills', () => {
    renderHero();

    // Three CTAs: primary (challenger) + two ghost (hospitals, backstage).
    expect(
      screen.getByRole('button', { name: /start with what you told us/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /meet the three hospitals/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /see how it was built/i })).toBeInTheDocument();

    // No Journai external link any more (that narrative relocated to Backstage).
    const hrefs = screen.queryAllByRole('link').map((link) => link.getAttribute('href') ?? '');
    expect(hrefs.some((href) => href.includes('journai'))).toBe(false);

    // Legacy trust pills are gone (their info now lives in the framebox).
    expect(screen.queryByText(/swiss-resident/i)).toBeNull();
    // BVA value tiles and the site-capacity aside stay removed.
    expect(screen.queryByTestId('hero-metric-tile')).toBeNull();
    expect(screen.queryByText(/site capacity/i)).toBeNull();
  });

  it('localizes the hero headline and framebox in German', async () => {
    await i18n.changeLanguage('de');
    renderHero();

    expect(
      screen.getByRole('heading', {
        name: /Kapazitätsprognose ist der wunde Punkt\.\s*So sieht die Lösung aus\./i,
      }),
    ).toBeInTheDocument();

    const framebox = screen.getByTestId('hero-framebox');
    expect(framebox).toHaveTextContent(/Bevor wir beginnen/i);
    expect(framebox).toHaveTextContent(/nur beratend, nie entscheidend/i);
  });

  it('localizes the hero headline in French and Italian', async () => {
    await i18n.changeLanguage('fr');
    const fr = renderHero();
    expect(
      screen.getByRole('heading', {
        name: /Voici à quoi ressemble la solution\./i,
      }),
    ).toBeInTheDocument();
    fr.unmount();

    await i18n.changeLanguage('it');
    renderHero();
    expect(
      screen.getByRole('heading', {
        name: /Ecco come appare la soluzione\./i,
      }),
    ).toBeInTheDocument();
  });
});
