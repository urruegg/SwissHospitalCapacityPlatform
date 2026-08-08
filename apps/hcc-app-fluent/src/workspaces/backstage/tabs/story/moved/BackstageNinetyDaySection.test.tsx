import '../../../../../i18n';
import { render, screen, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import { beforeAll, describe, expect, it } from 'vitest';
import i18n from '../../../../../i18n';
import { BackstageNinetyDaySection } from './BackstageNinetyDaySection';

describe('BackstageNinetyDaySection', () => {
  beforeAll(async () => {
    await i18n.changeLanguage('en');
  });

  it('renders a Backstage header above the reused 90-day body with its PROD disclaimer', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <MemoryRouter>
          <BackstageNinetyDaySection />
        </MemoryRouter>
      </FluentProvider>,
    );
    const section = screen.getByTestId('backstage-ninety-day-section');
    expect(within(section).getByRole('heading', { name: /90 days/i })).toBeInTheDocument();
    expect(within(section).getByText(/live in PROD Switzerland North/i)).toBeInTheDocument();
  });
});
