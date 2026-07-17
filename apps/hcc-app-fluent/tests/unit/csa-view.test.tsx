import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import '../../src/i18n';
import { CsaView } from '../../src/workspaces/main/wizards/csa/CsaView';
import { RoleProvider } from '../../src/context/role-context';

describe('CsaView', () => {
  it('mounts the CSA surface with the existing role guard for a crisis lead', () => {
    render(
      <MemoryRouter>
        <RoleProvider testRoles={['HCC.RegionalCrisisLead'] as never[]} testHomeSite="usz">
          <CsaView />
        </RoleProvider>
      </MemoryRouter>,
    );
    expect(screen.getByTestId('csa-view')).toBeInTheDocument();
  });
});
