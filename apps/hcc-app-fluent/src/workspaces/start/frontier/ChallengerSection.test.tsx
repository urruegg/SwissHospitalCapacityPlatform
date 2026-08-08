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
    expect(CHALLENGER_PERSONAS.map((p) => p.id)).toEqual(['coo', 'cio', 'ops', 'cto', 'ciso', 'it']);
    CHALLENGER_PERSONAS.forEach((persona) => {
      expect(screen.getByTestId(`challenger-tab-${persona.id}`)).toBeInTheDocument();
    });
    // The CIO seat (Emanuel Furler) is now rendered as tab #2, matching the updated mockup.
    expect(screen.getByTestId('challenger-tab-cio')).toBeInTheDocument();
  });

  it('shows the COO pane by default with photo, linked name, role chip and review date', () => {
    renderChallenger();

    const pane = screen.getByTestId('challenger-pane-coo');
    // Avatar photo carries the reviewer name as alt text (a11y).
    expect(within(pane).getByAltText('Rebekka Hatzung')).toBeInTheDocument();
    // Name links out to the real professional profile in a new tab.
    const nameLink = within(pane).getByRole('link', { name: 'Rebekka Hatzung' });
    expect(nameLink).toHaveAttribute('href', 'https://www.luks.ch/spezialisten/rebekka-hatzung');
    expect(nameLink).toHaveAttribute('target', '_blank');
    expect(nameLink).toHaveAttribute('rel', expect.stringContaining('noopener'));
    // Role chip + dated review provenance.
    expect(within(pane).getByText('COO')).toBeInTheDocument();
    expect(within(pane).getByText(/Review by 24\.07\.2026/)).toBeInTheDocument();

    expect(within(pane).getByText(/business case is plausible/i)).toBeInTheDocument();
    expect(within(pane).getByText('How we addressed the challenges')).toBeInTheDocument();
    expect(within(pane).getByText('Business value delivered')).toBeInTheDocument();
    expect(within(pane).getByText('What we adapted in the product')).toBeInTheDocument();
    expect(within(pane).getByText(/127% ROI over three years/)).toBeInTheDocument();
    // Only the selected persona pane is mounted.
    expect(screen.queryByTestId('challenger-pane-ciso')).not.toBeInTheDocument();
  });

  it('renders the three Hospital Operations reviewers as a linked people grid', () => {
    renderChallenger();

    fireEvent.click(screen.getByTestId('challenger-tab-ops'));

    const pane = screen.getByTestId('challenger-pane-ops');
    // Green "Hospital Operations" chip + shared review date.
    expect(within(pane).getByText('Hospital Operations')).toBeInTheDocument();
    expect(within(pane).getByText(/Review by 17\.07\.2026/)).toBeInTheDocument();
    // Three overlapping avatars, one per reviewer.
    expect(within(pane).getAllByRole('img')).toHaveLength(3);
    // Each reviewer name links out to their real profile.
    expect(within(pane).getByRole('link', { name: 'Christian Ernst' })).toHaveAttribute(
      'href',
      'https://spitalzollikerberg.ch/de/team/christian-ernst',
    );
    expect(within(pane).getByRole('link', { name: 'Dr. Regula Adams' })).toBeInTheDocument();
    expect(within(pane).getByRole('link', { name: 'Dr. med. Marco Rossi' })).toBeInTheDocument();
  });

  it('renders the three challenger insight patterns and the pick-a-seat cue', () => {
    renderChallenger();

    const section = screen.getByTestId('challenger-patterns');
    expect(within(section).getByText(/technology was never the objection/i)).toBeInTheDocument();
    expect(within(section).getByText(/no patient data/i)).toBeInTheDocument();
    expect(within(section).getByText(/human must stay in charge/i)).toBeInTheDocument();
    expect(screen.getByText(/Pick the seat you sit in/i)).toBeInTheDocument();
  });

  it('switches to another persona pane on tab select and keeps the quote verbatim', () => {
    renderChallenger();

    fireEvent.click(screen.getByTestId('challenger-tab-ciso'));

    const pane = screen.getByTestId('challenger-pane-ciso');
    expect(within(pane).getByAltText('Daniel von Büren')).toBeInTheDocument();
    expect(within(pane).getByRole('link', { name: 'Daniel von Büren' })).toBeInTheDocument();
    // German-origin quote stays verbatim (with its English gloss beneath).
    expect(within(pane).getByText(/Für eine Bettenplanung/)).toBeInTheDocument();
    expect(within(pane).getByText(/no personal or patient data/i)).toBeInTheDocument();
    expect(screen.queryByTestId('challenger-pane-coo')).not.toBeInTheDocument();
  });

  it('renders the CIO pane with the linked reviewer and the English gloss as the primary quote under en', () => {
    renderChallenger();

    fireEvent.click(screen.getByTestId('challenger-tab-cio'));

    const pane = screen.getByTestId('challenger-pane-cio');
    expect(within(pane).getByAltText('Emanuel Furler')).toBeInTheDocument();
    const nameLink = within(pane).getByRole('link', { name: 'Emanuel Furler' });
    expect(nameLink).toHaveAttribute(
      'href',
      'https://spitalzollikerberg.ch/de/team/emanuel-furler',
    );
    expect(within(pane).getByText('CIO')).toBeInTheDocument();
    // Selected language (en) is primary: the English gloss sits in the blockquote.
    expect(
      within(pane).getByText(/Which operational decisions could be made better today/i, {
        selector: 'blockquote',
      }),
    ).toBeInTheDocument();
    // The authentic German original is retained verbatim beneath.
    expect(within(pane).getByText(/Welche operativen Entscheidungen/)).toBeInTheDocument();
  });

  it('promotes the selected-language quote to the primary blockquote for German-origin seats', async () => {
    // en: the English gloss is the primary blockquote for the CISO seat.
    const en = renderChallenger();
    fireEvent.click(screen.getByTestId('challenger-tab-ciso'));
    expect(
      within(screen.getByTestId('challenger-pane-ciso')).getByText(/no personal or patient data/i, {
        selector: 'blockquote',
      }),
    ).toBeInTheDocument();
    en.unmount();

    // de: the authentic German quote becomes the primary blockquote.
    await i18n.changeLanguage('de');
    renderChallenger();
    fireEvent.click(screen.getByTestId('challenger-tab-ciso'));
    expect(
      within(screen.getByTestId('challenger-pane-ciso')).getByText(/Für eine Bettenplanung/, {
        selector: 'blockquote',
      }),
    ).toBeInTheDocument();
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

    fireEvent.click(screen.getByTestId('challenger-tab-ciso'));
    // Real attributed German quote is never machine-translated.
    expect(screen.getByText(/Für eine Bettenplanung/)).toBeInTheDocument();
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
