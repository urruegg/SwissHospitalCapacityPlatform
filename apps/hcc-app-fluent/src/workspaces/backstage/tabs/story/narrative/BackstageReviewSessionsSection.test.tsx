import '../../../../../i18n';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../../../../i18n';
import { ReviewSessionsSection } from './BackstageNarrativeSections';

function renderReviews() {
  return render(
    <MemoryRouter initialEntries={['/backstage']}>
      <FluentProvider theme={webLightTheme}>
        <ReviewSessionsSection />
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

describe('ReviewSessionsSection', () => {
  it('renders the review table with three columns: Session, Date, Perspective challenged', () => {
    renderReviews();
    const headers = screen.getAllByRole('columnheader');
    expect(headers).toHaveLength(3);
    expect(headers[0]).toHaveTextContent(/session/i);
    expect(headers[1]).toHaveTextContent(/date/i);
    expect(headers[2]).toHaveTextContent(/perspective challenged/i);
  });

  it('harmonises the sessions with the start-plane "What we heard" seats (COO/CIO/CTO/CISO/Ops/IT)', () => {
    renderReviews();
    const section = screen.getByTestId('review-sessions-section');
    // One body row per harmonised seat (6), plus the header row.
    const rows = within(section).getAllByRole('row');
    expect(rows).toHaveLength(7);
    // Perspectives echo the start-plane persona sub-labels.
    expect(within(section).getByText(/Business case & adoption/i)).toBeInTheDocument();
    expect(within(section).getByText(/Cloud operating model/i)).toBeInTheDocument();
  });

  it('uses the shortened venue text (Microsoft Innovation Hub, not Technology Center)', () => {
    renderReviews();
    const section = screen.getByTestId('review-sessions-section');
    expect(within(section).getByText(/Microsoft Innovation Hub/i)).toBeInTheDocument();
    expect(within(section).queryByText(/Technology Center/i)).not.toBeInTheDocument();
  });

  it('rebuilds the practitioner cards to the authoritative nine-person roster with photos', () => {
    renderReviews();
    const section = screen.getByTestId('review-sessions-section');
    const roster = [
      'Rebekka Hatzung',
      'Emanuel Furler',
      'Christian Ernst',
      'Dr. Regula Adams',
      'Dr. med. Marco Rossi',
      'Petrus Jallo',
      'René Raeber',
      'Daniel von Büren',
      'Marco Weber',
    ];
    roster.forEach((name) => {
      expect(within(section).getByText(name)).toBeInTheDocument();
    });
    // Eight of nine ship a real photo; Marco Weber falls back to initials.
    const photos = within(section).getAllByRole('img');
    expect(photos.length).toBeGreaterThanOrEqual(8);
    expect(within(section).getByText('MW')).toBeInTheDocument();
    // Removed non-roster reviewers.
    expect(within(section).queryByText(/Döring-Wermelinger/i)).not.toBeInTheDocument();
    expect(within(section).queryByText(/AMA review panel/i)).not.toBeInTheDocument();
  });

  it('localises the table chrome in German', async () => {
    await i18n.changeLanguage('de');
    renderReviews();
    const section = screen.getByTestId('review-sessions-section');
    const headers = within(section).getAllByRole('columnheader');
    // German column headers (Sitzung / Datum / ...).
    expect(headers[0]).toHaveTextContent(/Sitzung/i);
    expect(headers[1]).toHaveTextContent(/Datum/i);
  });
});
