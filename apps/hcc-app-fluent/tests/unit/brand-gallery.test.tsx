import { describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import '../../src/i18n';
import { ThemeModeProvider } from '../../src/theme/theme-context';
import { BrandGalleryView } from '../../src/workspaces/brand/BrandGalleryView';

describe('BrandGalleryView', () => {
  it('renders token and component-state sections', () => {
    render(
      <ThemeModeProvider>
        <BrandGalleryView />
      </ThemeModeProvider>,
    );
    expect(screen.getByTestId('brand-gallery')).toBeInTheDocument();
    expect(screen.getByText(/spacing/i)).toBeInTheDocument();
    expect(screen.getByText(/component states/i)).toBeInTheDocument();
  });

  it('renders the chat response artefacts section (recommendation + refusal)', () => {
    render(
      <ThemeModeProvider>
        <BrandGalleryView />
      </ThemeModeProvider>,
    );
    // Recommendation card exercises A4 metric trio + A12 follow-ups.
    const reco = screen.getByTestId('gallery-recommendation');
    const trio = within(reco).getByTestId('metric-trio');
    expect(trio).toBeInTheDocument();
    expect(within(reco).getByTestId('follow-ups')).toBeInTheDocument();
    expect(within(trio).getByText('-6 beds')).toBeInTheDocument();
    // Refusal card exercises A11 (no levers).
    const refusal = screen.getByTestId('gallery-refusal');
    expect(within(refusal).queryByRole('listitem')).not.toBeInTheDocument();
    expect(within(refusal).getByText(/approved-to-apply/i)).toBeInTheDocument();
  });
});
