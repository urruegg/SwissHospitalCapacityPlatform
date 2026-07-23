import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { RecoPanel } from '../../src/copilot-rail/RecoPanel';
import type { GroundedReco } from '../../src/copilot-rail/reco';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

const reco: GroundedReco = {
  agentLabel: 'Occupancy Copilot',
  contextChip: { subject: 'Medicine A', qualifiers: ['forecast'], status: 'OVER', tone: 'over' },
  read: 'Medicine A tips to 102% within 72h.',
  levers: [
    { text: 'Expedite 6 discharges', impact: { label: '-6 beds', tone: 'beds' } },
    { text: 'Divert 3 low-acuity admits', impact: { label: '+3 buffer', tone: 'buffer' } },
  ],
  primaryCta: { label: 'Open discharge worklist', kind: 'handoff', target: 'dca-agent' },
  projection: '102% -> 94%',
  citations: ['gold.fact_capacity_baseline'],
  provenance: 'simulated',
};

describe('RecoPanel', () => {
  it('renders reco content, numbered levers, and fires CTA + back', () => {
    const onBack = vi.fn();
    const onCta = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <RecoPanel reco={reco} showBack onBack={onBack} onCta={onCta} />
      </FluentProvider>,
    );
    expect(screen.getByText('Medicine A tips to 102% within 72h.')).toBeInTheDocument();
    expect(screen.getByText('Expedite 6 discharges')).toBeInTheDocument();
    expect(screen.getByText('-6 beds')).toBeInTheDocument();
    expect(screen.getByText(/102% -> 94%/)).toBeInTheDocument();

    act(() => screen.getByRole('button', { name: /Open discharge worklist/ }).click());
    expect(onCta).toHaveBeenCalledWith(reco.primaryCta);

    act(() => screen.getByRole('button', { name: /back to summary/i }).click());
    expect(onBack).toHaveBeenCalled();
  });

  it('hides the back button when showBack is false', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <RecoPanel reco={reco} showBack={false} onBack={vi.fn()} onCta={vi.fn()} />
      </FluentProvider>,
    );
    expect(screen.queryByRole('button', { name: /back to summary/i })).not.toBeInTheDocument();
  });

  it('renders an approval-required gate and keeps the CTA actionable', () => {
    const onCta = vi.fn();
    const approvalReco: GroundedReco = {
      ...reco,
      primaryCta: { label: 'Move PT-4003 to overflow', kind: 'action', requiresApproval: true },
    };
    render(
      <FluentProvider theme={webLightTheme}>
        <RecoPanel reco={approvalReco} showBack={false} onBack={vi.fn()} onCta={onCta} />
      </FluentProvider>,
    );
    expect(screen.getByText(/approval required/i)).toBeInTheDocument();
    expect(screen.getByText(/approved-to-apply/i)).toBeInTheDocument();
    const cta = screen.getByRole('button', { name: /Move PT-4003 to overflow/ });
    expect(cta).toBeEnabled();
    act(() => cta.click());
    expect(onCta).toHaveBeenCalledWith(approvalReco.primaryCta);
  });

  it('renders a refused badge and disables the CTA when refused', () => {
    const onCta = vi.fn();
    const refusedReco: GroundedReco = {
      ...reco,
      refused: true,
      read: 'Move refused: no compliant downstream bed available.',
      primaryCta: { label: 'Move PT-4004 to overflow', kind: 'action' },
    };
    render(
      <FluentProvider theme={webLightTheme}>
        <RecoPanel reco={refusedReco} showBack={false} onBack={vi.fn()} onCta={onCta} />
      </FluentProvider>,
    );
    expect(screen.getByText('Refused')).toBeInTheDocument();
    const cta = screen.getByRole('button', { name: /Move PT-4004 to overflow/ });
    expect(cta).toBeDisabled();
  });
});
