import { describe, it, expect, beforeAll } from 'vitest';
import i18n from '../../src/i18n';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MainSubNav } from '../../src/workspaces/main/MainSubNav';
import { RoleProvider } from '../../src/context/role-context';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function renderSubNav(roles: string[]) {
  return render(
    <MemoryRouter initialEntries={['/main/occupancy']}>
      <RoleProvider testRoles={roles as never[]} testHomeSite="usz">
        <MainSubNav />
      </RoleProvider>
    </MemoryRouter>,
  );
}

describe('MainSubNav', () => {
  it('lists all six role boards for an admin', () => {
    renderSubNav(['HCC.PlatformAdmin']);
    ['Occupancy', 'Discharge', 'Bed management', 'OR steering', 'Staffing', 'Scenario'].forEach((n) =>
      expect(screen.getByRole('tab', { name: n })).toBeInTheDocument(),
    );
  });

  it('enables the Scenario board for a bed manager (now gated on main nav)', () => {
    renderSubNav(['HCC.BedManager']);
    expect(screen.getByRole('tab', { name: 'Scenario' })).not.toBeDisabled();
    expect(screen.getByRole('tab', { name: 'Occupancy' })).not.toBeDisabled();
  });
});
