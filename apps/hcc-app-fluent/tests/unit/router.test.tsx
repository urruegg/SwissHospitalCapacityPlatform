import '../../src/i18n';
import { vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RouterProvider, createMemoryRouter } from 'react-router-dom';
import { routes } from '../../src/shell/router';
import { ThemeModeProvider } from '../../src/theme/theme-context';
import { RoleProvider } from '../../src/context/role-context';
import { ModeProvider } from '../../src/context/mode-context';
import { CopilotRailProvider } from '../../src/copilot-rail/rail-context';
import { HospitalProvider } from '../../src/context/hospital-context';
import { parseClaims } from '../../src/auth/claim-parser';

vi.mock('../../src/copilot-drawer/Drawer', () => ({
  CopilotDrawer: () => null,
}));

function renderAt(path: string) {
  const router = createMemoryRouter(routes, { initialEntries: [path] });
  const claims = parseClaims(undefined);
  return render(
    <ThemeModeProvider>
      <ModeProvider>
        <CopilotRailProvider>
          <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
            <HospitalProvider claims={claims}>
              <RouterProvider router={router} />
            </HospitalProvider>
          </RoleProvider>
        </CopilotRailProvider>
      </ModeProvider>
    </ThemeModeProvider>,
  );
}

describe('routes', () => {
  it('defaults "/" to the Start surface', () => {
    renderAt('/');
    expect(screen.getByTestId('start-view')).toBeInTheDocument();
  });

  it('redirects unknown paths to Start', () => {
    renderAt('/nope');
    expect(screen.getByTestId('start-view')).toBeInTheDocument();
  });

  it('renders the crisis board under /main/crisis', () => {
    renderAt('/main/crisis');
    expect(screen.getByTestId('csa-view')).toBeInTheDocument();
  });

  it('retires the legacy top-level /csa route', () => {
    renderAt('/csa');
    expect(screen.getByTestId('start-view')).toBeInTheDocument();
    expect(screen.queryByTestId('csa-view')).not.toBeInTheDocument();
  });

  it('renders the design-system gallery under /brand', async () => {
    renderAt('/brand');
    expect(await screen.findByTestId('brand-gallery')).toBeInTheDocument();
  });
});
