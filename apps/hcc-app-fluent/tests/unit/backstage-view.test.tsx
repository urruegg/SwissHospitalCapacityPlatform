import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import '../../src/i18n';
import { BackstageView } from '../../src/workspaces/backstage/BackstageView';
import { RoleProvider } from '../../src/context/role-context';

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
        <Routes>
          <Route path="/backstage/:widget?" element={<BackstageView />} />
        </Routes>
      </RoleProvider>
    </MemoryRouter>,
  );
}

describe('BackstageView', () => {
  it('defaults to the Digital Feedback Loop part', () => {
    renderAt('/backstage');
    expect(screen.getByTestId('widget-feedback-loop')).toBeInTheDocument();
    expect(screen.getByTestId('digital-feedback-loop-section')).toBeInTheDocument();
  });

  it('renders the Backstage header and sub-navigation', () => {
    renderAt('/backstage');
    expect(screen.getByTestId('backstage-surface')).toBeInTheDocument();
    expect(screen.getByTestId('backstage-nav-feedback-loop')).toBeInTheDocument();
    expect(screen.getByTestId('backstage-nav-opportunities')).toBeInTheDocument();
  });

  it('mounts the Opportunities part on its route', () => {
    renderAt('/backstage/opportunities');
    expect(screen.getByTestId('widget-opportunities')).toBeInTheDocument();
  });

  it('falls back to the Digital Feedback Loop part for an unknown widget', () => {
    renderAt('/backstage/does-not-exist');
    expect(screen.getByTestId('widget-feedback-loop')).toBeInTheDocument();
  });
});
