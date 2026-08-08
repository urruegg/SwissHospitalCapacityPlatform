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
  it('renders the Curavias brandlock (mark symbol + wordmark + descriptor + tagline)', () => {
    renderVision();

    const lock = screen.getByTestId('vision-brandlock');
    expect(within(lock).getByText('Curavias')).toBeInTheDocument();
    expect(within(lock).getByText('Swiss Hospital Command Center powered by Copilot')).toBeInTheDocument();
    expect(within(lock).getByText(/Every patient's path, in Swiss hands\./)).toBeInTheDocument();
    // The rising-path mark renders inline as an accessible image.
    expect(within(lock).getByRole('img', { name: /Curavias symbol/i })).toBeInTheDocument();
  });

  it('renders the Curavias mark glyph inside the mark card', () => {
    renderVision();

    const glyph = screen.getByTestId('vision-mark-glyph');
    expect(glyph).toBeInTheDocument();
    // Accessible name comes from the SVG aria-label.
    expect(screen.getByRole('img', { name: /Curavias mark/i })).toBeInTheDocument();
  });

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

  it('renders vision + mission statements in the selected language (en) — no bilingual echo', () => {
    renderVision();

    const vision = screen.getByTestId('vision-statement');
    expect(within(vision).getByText('Vision')).toBeInTheDocument();
    expect(
      within(vision).getByText('A Swiss healthcare system where capacity never decides who waits.'),
    ).toBeInTheDocument();
    // No German echo line renders under en.
    expect(within(vision).queryByText(/Ein Schweizer Gesundheitswesen/)).not.toBeInTheDocument();

    const mission = screen.getByTestId('mission-statement');
    expect(within(mission).getByText('Mission')).toBeInTheDocument();
    expect(
      within(mission).getByText(/Empower every care team in every Swiss hospital/),
    ).toBeInTheDocument();
    expect(
      within(mission).queryByText(/Jedes Behandlungsteam in jedem Schweizer Spital/),
    ).not.toBeInTheDocument();
  });

  it('renders the time-currency line and the three guarantee pills (single language)', () => {
    renderVision();

    const timeCurrency = screen.getByTestId('vision-time-currency');
    expect(within(timeCurrency).getByText(/Time is the currency of capacity/)).toBeInTheDocument();

    const pills = screen.getAllByTestId('vision-pill');
    expect(pills).toHaveLength(VISION_PILLS.length);
    expect(screen.getByText('Advisory, never autonomous')).toBeInTheDocument();
    expect(screen.getByText('The human decides, always')).toBeInTheDocument();
    expect(screen.getByText('Swiss data, Swiss hosting, no patient data')).toBeInTheDocument();
    // The German echo copy is gone under en.
    expect(screen.queryByText('Beratend, nie autonom')).not.toBeInTheDocument();
  });

  it('localises the vision/mission statements and pills in de (no English fallback)', async () => {
    await i18n.changeLanguage('de');
    renderVision();

    // Chrome (headings) localises...
    expect(screen.getByText('Das Wort')).toBeInTheDocument();
    expect(screen.getByText('Unsere Vision & Mission')).toBeInTheDocument();
    // ...and the vision statement now renders in German, not English.
    expect(
      screen.getByText(
        'Ein Schweizer Gesundheitswesen, in dem nie die Kapazität entscheidet, wer warten muss.',
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByText('A Swiss healthcare system where capacity never decides who waits.'),
    ).not.toBeInTheDocument();
    // Guarantee pill localises too.
    expect(screen.getByText('Beratend, nie autonom')).toBeInTheDocument();
  });
});
