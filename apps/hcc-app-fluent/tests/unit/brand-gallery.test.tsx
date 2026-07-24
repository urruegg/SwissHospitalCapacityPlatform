import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
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
});
