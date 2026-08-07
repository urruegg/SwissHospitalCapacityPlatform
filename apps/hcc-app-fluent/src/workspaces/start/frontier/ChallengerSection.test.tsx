import '../../../i18n';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../../i18n';
import { ChallengerSection } from './ChallengerSection';
import { CHALLENGER_PERSONAS } from './start-content';

function renderChallenger() {
  return render(
    <MemoryRouter initialEntries={['/start']}>
      <FluentProvider theme={webLightTheme}>
        <ChallengerSection />
      </FluentProvider>
    </MemoryRouter>,
  );
}

beforeEach(async () => {
  await i18n.changeLanguage('en');
});

afterEach(async () => {
  await i18n.changeLanguage('en');
});

describe('ChallengerSection', () => {
  it('renders one tab per challenger persona in the mockup order', () => {
    renderChallenger();

    const tabs = screen.getAllByRole('tab');
    expect(tabs).toHaveLength(CHALLENGER_PERSONAS.length);
    expect(CHALLENGER_PERSONAS.map((p) => p.id)).toEqual([
      'coo',
      'cio',
      'cto',
      'ciso',
      'ops',
      'it',
    ]);
    CHALLENGER_PERSONAS.forEach((persona) => {
      expect(screen.getByTestId(`challenger-tab-${persona.id}`)).toBeInTheDocument();
    });
  });

  it('shows the COO pane by default with quote, addressed, value and adapted content', () => {
    renderChallenger();

    const pane = screen.getByTestId('challenger-pane-coo');
    expect(within(pane).getByText(/Rebekka Hatzung/)).toBeInTheDocument();
    expect(within(pane).getByText(/business case is plausible/i)).toBeInTheDocument();
    expect(within(pane).getByText('How we addressed the challenges')).toBeInTheDocument();
    expect(within(pane).getByText('Business value delivered')).toBeInTheDocument();
    expect(within(pane).getByText('What we adapted in the product')).toBeInTheDocument();
    expect(within(pane).getByText(/127% ROI over three years/)).toBeInTheDocument();
    // Only the selected persona pane is mounted.
    expect(screen.queryByTestId('challenger-pane-ciso')).not.toBeInTheDocument();
  });

  it('switches to another persona pane on tab select and keeps the quote verbatim', () => {
    renderChallenger();

    fireEvent.click(screen.getByTestId('challenger-tab-ciso'));

    const pane = screen.getByTestId('challenger-pane-ciso');
    expect(within(pane).getByText(/Daniel von B/)).toBeInTheDocument();
    // German-origin quote stays verbatim (with its English gloss beneath).
    expect(within(pane).getByText(/Für eine Bettenplanung/)).toBeInTheDocument();
    expect(within(pane).getByText(/no personal or patient data/i)).toBeInTheDocument();
    expect(screen.queryByTestId('challenger-pane-coo')).not.toBeInTheDocument();
  });

  it('renders the closing synthetic-tenant disclaimer with a Backstage link', () => {
    renderChallenger();

    const disclaimer = screen.getByTestId('challenger-disclaimer');
    expect(within(disclaimer).getByText(/synthetic/i)).toBeInTheDocument();
    const link = within(disclaimer).getByRole('link');
    expect(link).toHaveAttribute('href', '/backstage');
  });

  it('localises the pane sub-headings (de) while keeping the authentic quote', async () => {
    await i18n.changeLanguage('de');
    renderChallenger();

    const pane = screen.getByTestId('challenger-pane-coo');
    expect(
      within(pane).getByText('Wie wir die Herausforderungen angegangen sind'),
    ).toBeInTheDocument();
    expect(within(pane).getByText('Gelieferter Geschäftswert')).toBeInTheDocument();
    expect(within(pane).getByText('Was wir am Produkt angepasst haben')).toBeInTheDocument();

    fireEvent.click(screen.getByTestId('challenger-tab-cio'));
    // Real attributed German quote is never machine-translated.
    expect(
      screen.getByText(/Welche operativen Entscheidungen könnten heute besser/),
    ).toBeInTheDocument();
  });

  it('localises the challenger role tabs in fr and it (never falls back to English)', async () => {
    await i18n.changeLanguage('fr');
    const fr = renderChallenger();
    expect(
      within(screen.getByTestId('challenger-tab-coo')).getByText(
        'Analyse de rentabilité & adoption',
      ),
    ).toBeInTheDocument();
    expect(
      within(screen.getByTestId('challenger-tab-ops')).getByText('Exploitation hospitalière'),
    ).toBeInTheDocument();
    fr.unmount();

    await i18n.changeLanguage('it');
    renderChallenger();
    expect(
      within(screen.getByTestId('challenger-tab-coo')).getByText('Business case & adozione'),
    ).toBeInTheDocument();
    expect(
      within(screen.getByTestId('challenger-tab-ops')).getByText('Operazioni ospedaliere'),
    ).toBeInTheDocument();
  });
});
