import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, within, act } from '@testing-library/react';
import type { ReactNode } from 'react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import i18n from '../../src/i18n';
import { AppShell } from '../../src/shell/AppShell';
import { ProductOwnerRail } from '../../src/shell/planes/ProductOwnerRail';
import { RoleProvider } from '../../src/context/role-context';
import { ModeProvider } from '../../src/context/mode-context';
import { ThemeModeProvider } from '../../src/theme/theme-context';
import { CopilotRailProvider } from '../../src/copilot-rail/rail-context';

const sendMock = vi.fn();

vi.mock('../../src/copilot-drawer/AgentInvoker', () => ({
  useAgentInvoker: vi.fn(() => ({
    busy: false,
    send: sendMock,
    turns: [
      {
        role: 'agent',
        text: 'Curavias is ready for a cited product-owner decision brief.',
        status: 'partial',
        confidence: 0.82,
        citations: ['docs/PRD.md#FR-POA-002'],
        chunks: [
          {
            classId: 'A',
            text: 'START and BACKSTAGE rail requirement.',
            citation: { sourceRef: 'docs/PRD.md#FR-POA-002' },
            asOf: '2026-07-25T12:00:00.000Z',
            liveness: 'live',
            status: 'verified',
            confidence: 0.91,
            language: 'en',
          },
        ],
      },
    ],
  })),
}));

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

beforeEach(() => {
  sendMock.mockClear();
});

function Providers({ children }: { children: ReactNode }) {
  return (
    <FluentProvider theme={webLightTheme}>
      <ThemeModeProvider>
        <ModeProvider>
          <CopilotRailProvider>
            <RoleProvider testRoles={['HCC.PlatformAdmin'] as never[]} testHomeSite="usz">
              {children}
            </RoleProvider>
          </CopilotRailProvider>
        </ModeProvider>
      </ThemeModeProvider>
    </FluentProvider>
  );
}

function renderShell(path: '/start' | '/backstage') {
  return render(
    <Providers>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/start" element={<div>start-content</div>} />
            <Route path="/backstage" element={<div>backstage-content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </Providers>,
  );
}

describe('ProductOwnerRail', () => {
  it('mounts as a docked full-height rail on START with proactive content', () => {
    renderShell('/start');

    const rail = screen.getByTestId('product-owner-rail');
    expect(rail).toHaveAttribute('data-layout', 'docked-full-height');
    expect(within(rail).getByRole('complementary', { name: /product owner agent/i })).toBeInTheDocument();
    expect(within(rail).getByText(/source-grounded product guidance/i)).toBeInTheDocument();
    expect(within(rail).getByTestId('conversation')).toBeInTheDocument();
  });

  it('mounts as a docked full-height rail on BACKSTAGE and never renders empty', () => {
    renderShell('/backstage');

    const rail = screen.getByTestId('product-owner-rail');
    expect(rail).toHaveAttribute('data-layout', 'docked-full-height');
    expect(within(rail).getByText(/source-grounded product guidance/i)).toBeInTheDocument();
    expect(rail).not.toHaveTextContent(/^\s*$/);
  });

  it('sends pre-formed product-owner questions from insight chips', () => {
    render(
      <Providers>
        <MemoryRouter>
          <ProductOwnerRail surface="start" />
        </MemoryRouter>
      </Providers>,
    );

    const sprint28Prompts = screen.getAllByText(/What changed for Sprint 28/i);
    act(() => sprint28Prompts[sprint28Prompts.length - 1].click());

    expect(sendMock).toHaveBeenCalledWith(expect.stringContaining('Sprint 28'));
  });

  it('renders grounded-answer status, confidence, and sourceRef citations from agent turns', () => {
    render(
      <Providers>
        <MemoryRouter>
          <ProductOwnerRail surface="start" />
        </MemoryRouter>
      </Providers>,
    );

    const card = screen.getByTestId('product-owner-answer-card-0');
    expect(card).toHaveTextContent(/partial/i);
    expect(card).toHaveTextContent(/82%/);
    expect(card).toHaveTextContent(/docs\/PRD\.md#FR-POA-002/);
  });

  it('supports the partner-scoped variant without exposing internal cost or security detail', () => {
    render(
      <Providers>
        <MemoryRouter>
          <ProductOwnerRail surface="backstage" partnerScoped />
        </MemoryRouter>
      </Providers>,
    );

    const rail = screen.getByTestId('product-owner-rail');
    expect(within(rail).getAllByText(/partner tier/i).length).toBeGreaterThan(0);
    expect(rail).not.toHaveTextContent(/internal cost\/security/i);
  });
});
