import '../../src/i18n';
import { render, screen } from '@testing-library/react';
import { SettingsView } from '../../src/workspaces/settings/SettingsView';
import { ThemeModeProvider } from '../../src/theme/theme-context';

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
