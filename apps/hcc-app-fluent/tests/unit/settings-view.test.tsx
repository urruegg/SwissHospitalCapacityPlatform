import { beforeAll } from 'vitest';
import i18n from '../../src/i18n';
import { render, screen } from '@testing-library/react';
import { SettingsView } from '../../src/workspaces/settings/SettingsView';
import { ThemeModeProvider } from '../../src/theme/theme-context';

// Sprint 20 M6 — assert the English preference-control copy deterministically.
beforeAll(async () => {
  await i18n.changeLanguage('en');
});

describe('SettingsView', () => {
  it('surfaces theme and language preference controls', () => {
    render(
      <ThemeModeProvider>
        <SettingsView />
      </ThemeModeProvider>,
    );
    expect(screen.getByTestId('settings-view')).toBeInTheDocument();
    expect(screen.getByText(/preferences/i)).toBeInTheDocument();
    expect(screen.getByLabelText('Theme')).toBeInTheDocument();
    expect(screen.getByLabelText('Language')).toBeInTheDocument();
  });
});
