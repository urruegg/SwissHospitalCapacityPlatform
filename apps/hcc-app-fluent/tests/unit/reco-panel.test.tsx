import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act, within, fireEvent } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { RecoPanel } from '../../src/copilot-rail/RecoPanel';
import type { GroundedReco } from '../../src/copilot-rail/reco';
import type { DecisionOutcome } from '../../src/data/iq-client';

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

  it('renders the A4 metric trio (now -> forecast -> gap)', () => {
    const withMetrics: GroundedReco = {
      ...reco,
      metrics: [
        { label: 'Now', value: '96%' },
        { label: '72 h', value: '102%' },
        { label: 'Gap', value: '-6 beds', tone: 'beds' },
      ],
    };
    render(
      <FluentProvider theme={webLightTheme}>
        <RecoPanel reco={withMetrics} showBack={false} onBack={vi.fn()} onCta={vi.fn()} />
      </FluentProvider>,
    );
    const trio = screen.getByTestId('metric-trio');
    expect(within(trio).getByText('96%')).toBeInTheDocument();
    expect(within(trio).getByText('102%')).toBeInTheDocument();
    expect(within(trio).getByText('-6 beds')).toBeInTheDocument();
    expect(within(trio).getByText('Gap')).toBeInTheDocument();
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

/**
 * Sprint 39 P2 (B2) — the copilot accept/deny decision surface. When the board
 * registers a live `onDecision` handler AND the reco requires approval, the
 * single CTA becomes an Accept + Deny pair that submits the human decision and
 * renders the returned outcome side-by-side. Without `onDecision` the render is
 * the unchanged presentational single CTA (NFR-UXL-001: the app never applies
 * directly; it only submits the decision).
 */
describe('RecoPanel — accept/deny decision surface (Sprint 39 P2)', () => {
  const approvalReco: GroundedReco = {
    ...reco,
    primaryCta: { label: 'Unblock barriers', kind: 'action', requiresApproval: true },
    provenance: 'live',
  };

  const acceptOutcome: DecisionOutcome = {
    contract: 'DC-SIM-OUTCOME-v1',
    plan_id: 'plan-1',
    golden_thread: 'gt-plan-1',
    lever_id: 'DCA-UNBLOCK-BARRIER',
    applied_ts: '1970-01-01T00:00:00Z',
    predicted_impact: { metric: 'beds', value: 3 },
    realised_impact: { metric: 'beds', value: 3 },
    state_delta: { beds_freed: ['C3'], patients_discharged: ['PT-1'], patients_promoted: [] },
    divergence: 0,
    provenance: 'live',
    applied: true,
    branch: 'accept',
    decision: 'accept',
    approver: 'oid-123',
  };

  const denyOutcome: DecisionOutcome = {
    ...acceptOutcome,
    realised_impact: { metric: 'beds', value: 0 },
    state_delta: { beds_freed: [], patients_discharged: [], patients_promoted: [] },
    applied: false,
    branch: 'deny',
    decision: 'deny',
  };

  function renderWith(onDecision: (d: 'accept' | 'deny') => Promise<DecisionOutcome>) {
    return render(
      <FluentProvider theme={webLightTheme}>
        <RecoPanel reco={approvalReco} showBack={false} onBack={vi.fn()} onCta={vi.fn()} role="dca" onDecision={onDecision} />
      </FluentProvider>,
    );
  }

  it('renders Accept + Deny when a live handler is present on an approval reco', () => {
    renderWith(vi.fn().mockResolvedValue(acceptOutcome));
    expect(screen.getByTestId('decision-actions')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Accept' })).toBeEnabled();
    expect(screen.getByRole('button', { name: 'Deny' })).toBeEnabled();
    // The advisory-only disclaimer stays present alongside the decision surface.
    expect(screen.getByText(/advisory only/i)).toBeInTheDocument();
  });

  it('accept submits the decision and renders the outcome side-by-side, accept branch active', async () => {
    const onDecision = vi.fn().mockResolvedValue(acceptOutcome);
    renderWith(onDecision);
    fireEvent.click(screen.getByRole('button', { name: 'Accept' }));
    expect(onDecision).toHaveBeenCalledWith('accept');
    const outcome = await screen.findByTestId('decision-outcome');
    // Both branches rendered (side-by-side); the accept branch is highlighted.
    expect(within(outcome).getByTestId('outcome-accept')).toHaveAttribute('aria-current', 'true');
    expect(within(outcome).getByTestId('outcome-deny')).toBeInTheDocument();
    expect(within(outcome).getByText(/3 beds freed/i)).toBeInTheDocument();
    expect(within(outcome).getByText(/breach persists/i)).toBeInTheDocument();
  });

  it('deny submits the decision and highlights the deny branch (breach persists)', async () => {
    const onDecision = vi.fn().mockResolvedValue(denyOutcome);
    renderWith(onDecision);
    fireEvent.click(screen.getByRole('button', { name: 'Deny' }));
    expect(onDecision).toHaveBeenCalledWith('deny');
    const outcome = await screen.findByTestId('decision-outcome');
    expect(within(outcome).getByTestId('outcome-deny')).toHaveAttribute('aria-current', 'true');
    expect(within(outcome).getByText(/breach persists/i)).toBeInTheDocument();
  });

  it('surfaces a refusal (403) as an alert and applies no change — no outcome, no retry', async () => {
    const onDecision = vi.fn().mockRejectedValue(new Error('decision failed: 403'));
    renderWith(onDecision);
    fireEvent.click(screen.getByRole('button', { name: 'Accept' }));
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent(/refused/i);
    expect(screen.queryByTestId('decision-outcome')).not.toBeInTheDocument();
    expect(onDecision).toHaveBeenCalledTimes(1); // no retry
  });

  it('without a handler the render is the unchanged presentational single CTA', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <RecoPanel reco={approvalReco} showBack={false} onBack={vi.fn()} onCta={vi.fn()} />
      </FluentProvider>,
    );
    expect(screen.queryByTestId('decision-actions')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Unblock barriers' })).toBeInTheDocument();
  });
});
