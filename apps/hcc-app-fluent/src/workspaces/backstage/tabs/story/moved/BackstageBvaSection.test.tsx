import { render, screen, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import * as goldenSourceClient from '../../../../../data/roleboard/golden-source-client';
import { BackstageBvaSection } from './BackstageBvaSection';

describe('BackstageBvaSection', () => {
  it('renders a Backstage header above the reused BVA decision body', () => {
    vi.spyOn(goldenSourceClient, 'loadSiteCapacitySummary').mockImplementation(
      () => new Promise(() => {}),
    );
    render(
      <FluentProvider theme={webLightTheme}>
        <MemoryRouter>
          <BackstageBvaSection />
        </MemoryRouter>
      </FluentProvider>,
    );
    const section = screen.getByTestId('backstage-bva-section');
    expect(within(section).getByTestId('bva-decision-section')).toBeInTheDocument();
    expect(within(section).getByRole('heading', { name: /BVA on ourselves/i })).toBeInTheDocument();
  });
});
