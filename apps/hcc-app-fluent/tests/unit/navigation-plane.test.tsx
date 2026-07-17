import { describe, it, expect } from 'vitest';
import '../../src/i18n';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { NavigationPlane } from '../../src/shell/planes/NavigationPlane';
import { RoleProvider } from '../../src/context/role-context';

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
  it('renders all five destinations for an admin', () => {
    renderNav(['HCC.PlatformAdmin']);
    ['Start', 'Main', 'CSA', 'Backstage', 'Settings'].forEach((n) =>
      expect(screen.getByRole('tab', { name: n })).toBeInTheDocument(),
    );
  });

  it('disables (but keeps visible) CSA/Settings for a bed manager', () => {
    renderNav(['HCC.BedManager']);
    expect(screen.getByRole('tab', { name: 'CSA' })).toBeDisabled();
    expect(screen.getByRole('tab', { name: 'Settings' })).toBeDisabled();
    expect(screen.getByRole('tab', { name: 'Main' })).not.toBeDisabled();
  });
});
