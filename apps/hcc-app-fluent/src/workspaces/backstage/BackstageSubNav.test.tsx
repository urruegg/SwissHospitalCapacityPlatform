import '../../i18n';
import { beforeEach, describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../i18n';
import { BackstageSubNav, BACKSTAGE_PARTS } from './BackstageSubNav';

function renderNav() {
  return render(
    <MemoryRouter initialEntries={['/backstage/bva']}>
      <FluentProvider theme={webLightTheme}>
        <BackstageSubNav />
      </FluentProvider>
    </MemoryRouter>,
  );
}

describe('BackstageSubNav', () => {
  beforeEach(async () => {
    await i18n.changeLanguage('en');
  });

  it('orders parts bva … ninety-day with no six-lane section (D1)', () => {
    // Changes 1-9: BVA moved to Backstage first (change 2), 90-day moved to Backstage last (change 3).
    expect(BACKSTAGE_PARTS[0].key).toBe('bva');
    expect(BACKSTAGE_PARTS[BACKSTAGE_PARTS.length - 1].key).toBe('ninety-day');
    // D1: the existing Frontier Architecture stays as `solution-design`; no six-lane section is added.
    const keys = BACKSTAGE_PARTS.map((p) => p.key);
    expect(keys).toContain('solution-design');
    expect(keys).not.toContain('six-lanes');
  });

  it('localises every sub-nav tab label (de) instead of falling back to English', async () => {
    await i18n.changeLanguage('de');
    renderNav();

    expect(screen.getByTestId('backstage-nav-success-framework')).toHaveTextContent(
      'Erfolgsframework',
    );
    expect(screen.getByTestId('backstage-nav-solution-design')).toHaveTextContent('Lösungsdesign');
    expect(screen.getByTestId('backstage-nav-devsecops-loop')).toHaveTextContent('DevSecOps');
    expect(screen.getByTestId('backstage-nav-review-sessions')).toHaveTextContent('Review');
    expect(screen.getByTestId('backstage-nav-po-classes')).toHaveTextContent('Product Owner');
    // Guard: the previously-missing de keys must not surface the English fallback label.
    expect(screen.getByTestId('backstage-nav-success-framework')).not.toHaveTextContent(
      'Success Framework',
    );
  });
});
