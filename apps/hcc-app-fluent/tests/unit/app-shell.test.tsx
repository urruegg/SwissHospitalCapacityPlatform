import '../../src/i18n';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AppShell } from '../../src/shell/AppShell';
import { ThemeModeProvider } from '../../src/theme/theme-context';
import { RoleProvider } from '../../src/context/role-context';

function renderShell(path = '/start') {
  return render(
    <ThemeModeProvider>
      <RoleProvider>
        <MemoryRouter initialEntries={[path]}>
          <Routes>
            <Route element={<AppShell />}>
              <Route path="/start" element={<div>start-content</div>} />
            </Route>
          </Routes>
        </MemoryRouter>
      </RoleProvider>
    </ThemeModeProvider>,
  );
}

describe('AppShell', () => {
  it('renders the four persistent planes and the routed main content', () => {
    renderShell();
    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByRole('complementary')).toBeInTheDocument();
    expect(screen.getByRole('contentinfo')).toBeInTheDocument();
    expect(screen.getByText('start-content')).toBeInTheDocument();
  });
});
