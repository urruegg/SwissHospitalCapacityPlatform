import i18n from '../../src/i18n';
import { render, screen, act } from '@testing-library/react';
import { beforeAll, describe, it, expect } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AppShell } from '../../src/shell/AppShell';
import { ThemeModeProvider } from '../../src/theme/theme-context';
import { ModeProvider } from '../../src/context/mode-context';
import { CopilotRailProvider } from '../../src/copilot-rail/rail-context';
import { RoleProvider } from '../../src/context/role-context';
import { HospitalProvider } from '../../src/context/hospital-context';
import { parseClaims } from '../../src/auth/claim-parser';

// Sprint 20 M7 — the agent affordance label is asserted in English.
beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function renderShell(path = '/start') {
  return render(
    <ThemeModeProvider>
      <ModeProvider>
        <CopilotRailProvider>
          <RoleProvider>
            <HospitalProvider claims={parseClaims(undefined)}>
              <MemoryRouter initialEntries={[path]}>
                <Routes>
                  <Route element={<AppShell />}>
                    <Route path="/start" element={<div>start-content</div>} />
                  </Route>
                </Routes>
              </MemoryRouter>
            </HospitalProvider>
          </RoleProvider>
        </CopilotRailProvider>
      </ModeProvider>
    </ThemeModeProvider>,
  );
}

describe('AppShell', () => {
  it('renders the four persistent planes and the routed main content', () => {
    renderShell();
    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByRole('contentinfo')).toBeInTheDocument();
    expect(screen.getByText('start-content')).toBeInTheDocument();
    // The agent plane starts collapsed (icon rail); opening it reveals the
    // complementary landmark.
    act(() => screen.getByRole('button', { name: /open agent/i }).click());
    expect(screen.getByRole('complementary')).toBeInTheDocument();
  });
});
