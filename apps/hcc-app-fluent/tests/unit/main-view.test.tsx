import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import '../../src/i18n';
import { MainView } from '../../src/workspaces/main/MainView';
import { RoleProvider } from '../../src/context/role-context';

describe('MainView', () => {
  it('defaults to the bed-manager board when no board segment is present', () => {
    render(
      <MemoryRouter initialEntries={['/main']}>
        <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
          <Routes>
            <Route path="/main/:board?" element={<MainView />} />
          </Routes>
        </RoleProvider>
      </MemoryRouter>,
    );
    expect(screen.getByTestId('board-bed-manager')).toBeInTheDocument();
  });
});
