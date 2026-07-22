import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import '../../src/i18n';
import { CsaView } from '../../src/workspaces/main/wizards/csa/CsaView';
import { RoleProvider } from '../../src/context/role-context';

vi.mock('../../src/copilot-drawer/Drawer', () => ({
  CopilotDrawer: () => null,
}));

describe('CsaView', () => {
  it('renders the CSA wizard for a crisis lead with the csa nav capability', () => {
    render(
      <MemoryRouter>
        <RoleProvider testRoles={['HCC.RegionalCrisisLead'] as never[]} testHomeSite="usz">
          <CsaView />
        </RoleProvider>
      </MemoryRouter>,
    );
    expect(screen.getByTestId('csa-view')).toBeInTheDocument();
    expect(screen.getByTestId('CsaWizard')).toBeInTheDocument();
    expect(screen.queryByTestId('CsaRoleGuardDenied')).not.toBeInTheDocument();
  });
});
