import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import '../../src/i18n';
import { MainView } from '../../src/workspaces/main/MainView';
import { RoleProvider } from '../../src/context/role-context';
import { ModeProvider } from '../../src/context/mode-context';
import { HospitalProvider } from '../../src/context/hospital-context';
import { CopilotRailProvider } from '../../src/copilot-rail/rail-context';
import { parseClaims } from '../../src/auth/claim-parser';

vi.mock('../../src/copilot-drawer/Drawer', () => ({
  CopilotDrawer: () => null,
}));

function renderMain(path: string) {
  const claims = parseClaims(undefined);
  return render(
    <MemoryRouter initialEntries={[path]}>
      <ModeProvider>
        <CopilotRailProvider>
          <HospitalProvider claims={claims}>
            <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
              <Routes>
                <Route path="/main/:board?" element={<MainView />} />
              </Routes>
            </RoleProvider>
          </HospitalProvider>
        </CopilotRailProvider>
      </ModeProvider>
    </MemoryRouter>,
  );
}

describe('MainView', () => {
  it('defaults to the role-first-eligible board (occupancy) when no board segment is present', async () => {
    renderMain('/main');
    expect(screen.getByTestId('board-occupancy-slot')).toBeInTheDocument();
    expect(await screen.findByTestId('board-occupancy')).toBeInTheDocument();
  });

  it('mounts the occupancy board for the occupancy segment', async () => {
    renderMain('/main/occupancy');
    expect(screen.getByTestId('board-occupancy-slot')).toBeInTheDocument();
    expect(await screen.findByTestId('board-occupancy')).toBeInTheDocument();
  });

  it('mounts the existing CSA view for the crisis segment', () => {
    renderMain('/main/crisis');
    expect(screen.getByTestId('board-crisis')).toBeInTheDocument();
    expect(screen.getByTestId('csa-view')).toBeInTheDocument();
  });
});
