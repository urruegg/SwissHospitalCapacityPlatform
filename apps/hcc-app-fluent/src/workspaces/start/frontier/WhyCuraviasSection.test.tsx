import '../../../i18n';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../../i18n';
import { WhyCuraviasSection } from './WhyCuraviasSection';
import { VISION_WORD_ROWS, VISION_MARK_STEPS, VISION_PILLS } from './start-content';

function renderVision() {
  return render(
    <MemoryRouter initialEntries={['/start']}>
      <FluentProvider theme={webLightTheme}>
        <WhyCuraviasSection />
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

describe('WhyCuraviasSection', () => {
  it('renders the cura + via + curavias etymology table (3 rows)', () => {
    renderVision();

    const table = screen.getByTestId('vision-word-table');
    const rows = within(table).getAllByTestId('vision-word-row');
    expect(rows).toHaveLength(VISION_WORD_ROWS.length);
    expect(VISION_WORD_ROWS.map((r) => r.id)).toEqual(['cura', 'via', 'curavias']);
    expect(within(table).getByText('cura')).toBeInTheDocument();
    expect(within(table).getByText('care, concern, healing')).toBeInTheDocument();
    expect(within(table).getByText(/The route through beds, OR, staff and discharge/)).toBeInTheDocument();
  });

  it('renders the three-step logo journey with the Success step highlighted', () => {
    renderVision();

    const list = screen.getByTestId('vision-mark');
    const steps = within(list).getAllByRole('listitem');
    expect(steps).toHaveLength(VISION_MARK_STEPS.length);
    expect(VISION_MARK_STEPS.map((s) => s.id)).toEqual(['start', 'care', 'success']);

    const success = screen.getByTestId('vision-mark-step-success');
    expect(success).toHaveAttribute('aria-current', 'step');
    expect(within(success).getByText('Success')).toBeInTheDocument();

    const start = screen.getByTestId('vision-mark-step-start');
    expect(start).not.toHaveAttribute('aria-current');
  });

  it('renders vision + mission as bilingual brand statements (EN primary + DE echo)', () => {
    renderVision();

    const vision = screen.getByTestId('vision-statement');
    expect(within(vision).getByText('Vision')).toBeInTheDocument();
    expect(
      within(vision).getByText('A Swiss healthcare system where capacity never decides who waits.'),
    ).toBeInTheDocument();
    expect(
      within(vision).getByText(/Ein Schweizer Gesundheitswesen, in dem nie die Kapazität/),
    ).toBeInTheDocument();

    const mission = screen.getByTestId('mission-statement');
    expect(within(mission).getByText('Mission')).toBeInTheDocument();
    expect(
      within(mission).getByText(/Empower every care team in every Swiss hospital/),
    ).toBeInTheDocument();
    expect(
      within(mission).getByText(/Jedes Behandlungsteam in jedem Schweizer Spital/),
    ).toBeInTheDocument();
  });

  it('renders the time-currency line and the three advisory/human/swiss guarantee pills', () => {
    renderVision();

    const timeCurrency = screen.getByTestId('vision-time-currency');
    expect(within(timeCurrency).getByText(/Time is the currency of capacity/)).toBeInTheDocument();

    const pills = screen.getAllByTestId('vision-pill');
    expect(pills).toHaveLength(VISION_PILLS.length);
    expect(screen.getByText('Advisory, never autonomous')).toBeInTheDocument();
    expect(screen.getByText('Beratend, nie autonom')).toBeInTheDocument();
    expect(screen.getByText('Swiss data, Swiss hosting, no patient data')).toBeInTheDocument();
  });

  it('localises the section chrome (de) while keeping the bilingual brand statements', async () => {
    await i18n.changeLanguage('de');
    renderVision();

    // Chrome (headings) localises...
    expect(screen.getByText('Das Wort')).toBeInTheDocument();
    expect(screen.getByText('Unsere Vision & Mission')).toBeInTheDocument();
    // ...while the deliberate bilingual brand statement stays identical in every locale.
    expect(
      screen.getByText('A Swiss healthcare system where capacity never decides who waits.'),
    ).toBeInTheDocument();
  });
});
