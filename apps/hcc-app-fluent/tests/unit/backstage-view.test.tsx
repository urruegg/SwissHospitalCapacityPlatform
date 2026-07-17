import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import '../../src/i18n';
import { BackstageView } from '../../src/workspaces/backstage/BackstageView';
import { RoleProvider } from '../../src/context/role-context';

describe('BackstageView', () => {
  it('defaults to the evidence widget', () => {
    render(
      <MemoryRouter initialEntries={['/backstage']}>
        <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
          <Routes>
            <Route path="/backstage/:widget?" element={<BackstageView />} />
          </Routes>
        </RoleProvider>
      </MemoryRouter>,
    );
    expect(screen.getByTestId('widget-evidence')).toBeInTheDocument();
  });
});
