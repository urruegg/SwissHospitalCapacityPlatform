import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { ConversationView } from '../../src/copilot-drawer/ConversationView';
import type { ConversationTurn } from '../../src/copilot-drawer/AgentInvoker';
import { invokeAgent } from '../../src/copilot-drawer/agent-manifest';
import type { GroundedReco } from '../../src/copilot-rail/reco';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

const reco: GroundedReco = {
  agentLabel: 'Occupancy Copilot',
  contextChip: { subject: 'Medicine A', status: 'OVER', tone: 'over' },
  read: 'Medicine A tips to 102% within 72h.',
  levers: [{ text: 'Expedite 6 discharges', impact: { label: '-6 beds', tone: 'beds' } }],
  primaryCta: { label: 'Open discharge worklist', kind: 'handoff', target: 'dca-agent' },
  citations: ['gold.fact_occupancy_forecast'],
  provenance: 'simulated',
  followUps: ['What happens without action?', 'Compare Ward B'],
};

function renderView(turns: ConversationTurn[], onFollowUp?: (p: string) => void) {
  return render(
    <FluentProvider theme={webLightTheme}>
      <ConversationView turns={turns} onFollowUp={onFollowUp} />
    </FluentProvider>,
  );
}

const AGENTS = ['ooa-agent', 'bmca-agent', 'dca-agent', 'orsa-agent', 'sba-agent', 'csa-agent'] as const;

describe('A12 — per-reply follow-up chips', () => {
  it('renders the reco follow-ups after the latest agent reply and sends on click', () => {
    const onFollowUp = vi.fn();
    renderView([{ role: 'user', text: 'Status?' }, { role: 'agent', text: reco.read, reco }], onFollowUp);

    const group = screen.getByTestId('follow-ups');
    const chip = within(group).getByText('What happens without action?');
    act(() => chip.click());
    expect(onFollowUp).toHaveBeenCalledWith('What happens without action?');
  });

  it('shows follow-ups only under the LAST turn, not earlier replies', () => {
    renderView(
      [
        { role: 'user', text: 'Q1' },
        { role: 'agent', text: reco.read, reco }, // earlier reply — no chips
        { role: 'user', text: 'Q2' },
        { role: 'agent', text: reco.read, reco }, // latest reply — chips here
      ],
      vi.fn(),
    );
    // Only one follow-up group in the whole conversation.
    expect(screen.getAllByTestId('follow-ups')).toHaveLength(1);
  });

  it('hides follow-ups when no onFollowUp handler is provided', () => {
    renderView([{ role: 'agent', text: reco.read, reco }]);
    expect(screen.queryByTestId('follow-ups')).not.toBeInTheDocument();
  });

  it('renders nothing extra when the latest reply carries no follow-ups', () => {
    const bare: GroundedReco = { ...reco, followUps: undefined };
    renderView([{ role: 'agent', text: bare.read, reco: bare }], vi.fn());
    expect(screen.queryByTestId('follow-ups')).not.toBeInTheDocument();
  });

  it('every role agent supplies at least one grounded follow-up prompt', async () => {
    for (const a of AGENTS) {
      const reply = await invokeAgent(a, 'x');
      expect(reply.reco?.followUps?.length ?? 0).toBeGreaterThan(0);
    }
  });
});
