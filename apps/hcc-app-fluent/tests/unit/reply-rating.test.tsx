import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { ConversationView } from '../../src/copilot-drawer/ConversationView';
import type { ConversationTurn } from '../../src/copilot-drawer/AgentInvoker';

/**
 * Sprint 30 M2-app — a thumbs up/down control under each captured agent reply
 * emits a user-interaction event for that turn's `interactionId`.
 */
beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function renderView(turns: ConversationTurn[], onRate?: (id: string, v: 'up' | 'down') => void) {
  return render(
    <FluentProvider theme={webLightTheme}>
      <ConversationView turns={turns} onRate={onRate} />
    </FluentProvider>,
  );
}

const agentTurn: ConversationTurn = {
  role: 'agent',
  text: 'Auslastung 92%.',
  interactionId: 'AIX-abc123',
};

describe('M2-app — reply rating control', () => {
  it('fires onRate with the turn interactionId and "up" when thumbs-up is clicked', () => {
    const onRate = vi.fn();
    renderView([{ role: 'user', text: 'Status?' }, agentTurn], onRate);
    act(() => screen.getByTestId('rate-up').click());
    expect(onRate).toHaveBeenCalledWith('AIX-abc123', 'up');
  });

  it('fires onRate with "down" when thumbs-down is clicked', () => {
    const onRate = vi.fn();
    renderView([agentTurn], onRate);
    act(() => screen.getByTestId('rate-down').click());
    expect(onRate).toHaveBeenCalledWith('AIX-abc123', 'down');
  });

  it('renders no rating control when onRate is absent', () => {
    renderView([agentTurn]);
    expect(screen.queryByTestId('rate-up')).not.toBeInTheDocument();
  });

  it('renders no rating control for a turn without an interactionId', () => {
    renderView([{ role: 'agent', text: 'no id' }], vi.fn());
    expect(screen.queryByTestId('rate-up')).not.toBeInTheDocument();
  });

  it('renders no rating control on a user turn', () => {
    renderView([{ role: 'user', text: 'hi', interactionId: 'AIX-x' }], vi.fn());
    expect(screen.queryByTestId('rate-up')).not.toBeInTheDocument();
  });
});
