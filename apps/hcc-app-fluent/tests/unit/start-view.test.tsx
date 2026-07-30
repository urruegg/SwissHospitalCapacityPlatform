import '../../src/i18n';
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import i18n from '../../src/i18n';
import { ModeProvider } from '../../src/context/mode-context';
import { RoleProvider } from '../../src/context/role-context';
import { StartView } from '../../src/workspaces/start/StartView';
import { START_SECTIONS } from '../../src/workspaces/start/frontier/start-content';

vi.mock('../../src/workspaces/start/frontier/StartHero', () => ({
  StartHero: () => <div data-testid="start-hero-content">StartHero content</div>,
}));

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

beforeEach(() => {
  localStorage.setItem('hcc.mode', 'demo');
});

function renderStart() {
  return render(
    <MemoryRouter>
      <RoleProvider testRoles={['HCC.PlatformAdmin']}>
        <ModeProvider>
          <StartView />
        </ModeProvider>
      </RoleProvider>
    </MemoryRouter>,
  );
}

describe('StartView', () => {
  it('shows the frontier page header and visible guardrails', () => {
    renderStart();

    expect(screen.getByRole('heading', { name: /Curavias Start/i })).toBeInTheDocument();
    expect(screen.getByText(/synthetic, generic, non-PHI content only/i)).toBeInTheDocument();
    expect(screen.getByText(/Advisory only/i)).toBeInTheDocument();
    expect(screen.getByText(/No PHI/i)).toBeInTheDocument();
  });

  it('shows the demo mode badge by default', () => {
    renderStart();
    expect(screen.getByTestId('start-mode-badge')).toHaveTextContent(
      /Demo — simulated golden-thread showcase/i,
    );
  });

  it('renders the approved section shells in START_SECTIONS order', () => {
    renderStart();

    const sectionShells = Array.from(
      screen.getByTestId('start-view').querySelectorAll<HTMLElement>('[data-start-section]'),
    );
    expect(sectionShells).toHaveLength(7);
    const renderedIds = sectionShells.map((node) => node.dataset.startSection);

    expect(renderedIds).toEqual(START_SECTIONS.map(({ id }) => id));
  });

  it('removes the legacy launcher grid and teaser surface', () => {
    renderStart();

    expect(screen.queryByTestId('start-capacity-teaser')).not.toBeInTheDocument();
    expect(screen.queryByTestId('launch-occupancy')).not.toBeInTheDocument();
  });
});
