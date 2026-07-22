import { describe, it, expect, beforeAll } from 'vitest';
import i18n from '../../src/i18n';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { NavigationPlane } from '../../src/shell/planes/NavigationPlane';
import { RoleProvider } from '../../src/context/role-context';

// Sprint 20 M6 — assert the language-independent English labels deterministically.
beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function renderNav(roles: string[]) {
  return render(
    <MemoryRouter>
      <RoleProvider testRoles={roles as never[]} testHomeSite="usz">
        <NavigationPlane />
      </RoleProvider>
    </MemoryRouter>,
  );
}

describe('NavigationPlane', () => {
  it('renders the four top-level destinations for an admin', () => {
    renderNav(['HCC.PlatformAdmin']);
    ['Start', 'Main', 'Backstage', 'Settings'].forEach((n) =>
      expect(screen.getByRole('tab', { name: n })).toBeInTheDocument(),
    );
    expect(screen.queryByRole('tab', { name: 'CSA' })).not.toBeInTheDocument();
  });

  it('disables Settings but keeps Main enabled for a bed manager', () => {
    renderNav(['HCC.BedManager']);
    expect(screen.getByRole('tab', { name: 'Settings' })).toBeDisabled();
    expect(screen.getByRole('tab', { name: 'Main' })).not.toBeDisabled();
    expect(screen.queryByRole('tab', { name: 'CSA' })).not.toBeInTheDocument();
  });
});
