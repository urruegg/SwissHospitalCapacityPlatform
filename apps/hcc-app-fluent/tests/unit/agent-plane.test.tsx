import { describe, it, expect, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../src/i18n';
import { AgentPlane } from '../../src/shell/planes/AgentPlane';
import { RoleProvider } from '../../src/context/role-context';

// Sprint 20 M7 — assert the English affordance copy deterministically.
beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function renderAgent(roles: string[], path = '/csa') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <RoleProvider testRoles={roles as never[]} testHomeSite="usz">
        <AgentPlane />
      </RoleProvider>
    </MemoryRouter>,
  );
}

describe('AgentPlane', () => {
  it('starts collapsed (icon only) and opens on toggle', () => {
    renderAgent(['HCC.RegionalCrisisLead']);
    const toggle = screen.getByRole('button', { name: /open agent/i });
    expect(screen.queryByRole('complementary')).not.toBeInTheDocument();
    act(() => toggle.click());
    expect(screen.getByRole('complementary')).toBeInTheDocument();
  });

  it('shows the action ceiling badge derived from the active role', () => {
    renderAgent(['HCC.Viewer']);
    act(() => screen.getByRole('button', { name: /open agent/i }).click());
    expect(screen.getByText(/read/i)).toBeInTheDocument();
  });
});
