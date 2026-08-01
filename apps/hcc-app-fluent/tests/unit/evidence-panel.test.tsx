import { describe, it, expect, beforeAll } from 'vitest';
import { useState } from 'react';
import { render, screen, within, fireEvent } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { EvidenceTracePanel } from '../../src/workspaces/main/boards/evidence/EvidenceTracePanel';
import { evidenceTraceFixture } from '../../src/data/roleboard/evidence-fixture';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

/** Stateful harness: mirrors the board — swaps the fixture trace on branch change. */
function Harness() {
  const [branch, setBranch] = useState<'accept' | 'deny'>('accept');
  return (
    <FluentProvider theme={webLightTheme}>
      <EvidenceTracePanel trace={evidenceTraceFixture(branch)} branch={branch} onBranchChange={setBranch} />
    </FluentProvider>
  );
}

describe('EvidenceTracePanel', () => {
  it('renders the five-part proof for a step with the shared golden_thread', () => {
    render(<Harness />);
    // golden_thread visible.
    expect(screen.getByTestId('evidence-golden-thread')).toHaveTextContent('gt-evd-demo-USZ');
    // All five parts of the current step render.
    expect(screen.getByTestId('evidence-part-epic')).toBeInTheDocument();
    expect(screen.getByTestId('evidence-part-read')).toBeInTheDocument();
    expect(screen.getByTestId('evidence-part-reco')).toBeInTheDocument();
    expect(screen.getByTestId('evidence-part-copilot')).toBeInTheDocument();
    expect(screen.getByTestId('evidence-part-outcome')).toBeInTheDocument();
    // Part titles (proof narrative).
    expect(screen.getByText('EPIC input')).toBeInTheDocument();
    expect(screen.getByText('Agent read')).toBeInTheDocument();
    expect(screen.getByText('Recommendation')).toBeInTheDocument();
    expect(screen.getByText('Copilot decision')).toBeInTheDocument();
    expect(screen.getByText('Outcome')).toBeInTheDocument();
  });

  it('shows the accept branch outcome (applied) and per-part provenance badges', () => {
    render(<Harness />);
    // First step (OOA) accept outcome: applied + realised 3 beds.
    const outcome = screen.getByTestId('evidence-part-outcome');
    expect(within(outcome).getByText(/Realised impact: 3 beds/)).toBeInTheDocument();
    expect(within(outcome).getByText('Applied')).toBeInTheDocument();
    // B4 — the outcome references the same DC-SIM-OUTCOME-v1 contract + golden_thread.
    expect(screen.getByTestId('evidence-outcome-thread')).toHaveTextContent('DC-SIM-OUTCOME-v1');
    expect(screen.getByTestId('evidence-outcome-thread')).toHaveTextContent('gt-evd-demo-USZ');
    // Provenance is honestly simulated on every part (demo scope).
    const epic = screen.getByTestId('evidence-part-epic');
    expect(within(epic).getByText('Simulated')).toBeInTheDocument();
  });

  it('the branch toggle switches the trace to the deny branch (breach persists)', () => {
    render(<Harness />);
    // Accept branch first.
    expect(within(screen.getByTestId('evidence-part-outcome')).getByText('Applied')).toBeInTheDocument();
    // Toggle to deny.
    fireEvent.click(screen.getByRole('tab', { name: /Deny branch/ }));
    const outcome = screen.getByTestId('evidence-part-outcome');
    expect(within(outcome).getByText(/Realised impact: 0 beds/)).toBeInTheDocument();
    expect(within(outcome).getByText('Not applied')).toBeInTheDocument();
    // The copilot part reflects the deny decision.
    expect(within(screen.getByTestId('evidence-part-copilot')).getByText('Denied')).toBeInTheDocument();
  });

  it('the demo walk steps through the roles OOA -> DCA -> BMCA -> ORSA', () => {
    render(<Harness />);
    const stepper = screen.getByTestId('evidence-stepper');
    // Starts on OOA (step 1 of 4).
    expect(within(stepper).getByText(/Step 1 of 4 . OOA/)).toBeInTheDocument();
    expect(screen.getByTestId('evidence-step')).toHaveAttribute('data-role', 'ooa');
    // Next -> DCA.
    fireEvent.click(within(stepper).getByRole('button', { name: /Next role/ }));
    expect(screen.getByTestId('evidence-step')).toHaveAttribute('data-role', 'dca');
    // Walk to the last role (ORSA); Next becomes disabled.
    fireEvent.click(within(stepper).getByRole('button', { name: /Next role/ }));
    fireEvent.click(within(stepper).getByRole('button', { name: /Next role/ }));
    expect(screen.getByTestId('evidence-step')).toHaveAttribute('data-role', 'orsa');
    expect(within(stepper).getByRole('button', { name: /Next role/ })).toBeDisabled();
  });
});
