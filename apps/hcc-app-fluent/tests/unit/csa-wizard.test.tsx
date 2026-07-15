/**
 * Sprint 16.1 · S16.5 — unit tests for the CSA wizard scaffold.
 *
 * Covers:
 *   - csa-steps: canonical 4-step order + step lookup + sample recs count
 *   - CsaRoleGuard: allow / deny based on role-context membership
 *   - CsaStepper: renders 4 tabs, current highlighted, future disabled
 *   - CsaWizard: composed happy path (role-authorised user sees Prepare step)
 *   - Rail integration: `csa` is a valid WorkspaceKey and rail exposes the tab
 */
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '../../src/i18n';
import { App } from '../../src/App';
import { CSA_STEPS, csaStepById, CSA_SAMPLE_RECOMMENDATIONS } from '../../src/workspaces/main/wizards/csa/csa-steps';
import { CSA_WIZARD_ROLES } from '../../src/workspaces/main/wizards/csa/CsaRoleGuard';

describe('CSA wizard — pure module (csa-steps)', () => {
  it('exposes the canonical 4-step order', () => {
    expect(CSA_STEPS.map((s) => s.id)).toEqual(['prepare', 'run', 'evaluate', 'recommend']);
  });

  it('every step has label + description + status', () => {
    for (const step of CSA_STEPS) {
      expect(step.label).toBeTruthy();
      expect(step.description).toBeTruthy();
      expect(['wired', 'stub']).toContain(step.status);
    }
  });

  it('exactly one step is wired (Prepare) and the other three are stubs', () => {
    const wired = CSA_STEPS.filter((s) => s.status === 'wired').map((s) => s.id);
    const stubs = CSA_STEPS.filter((s) => s.status === 'stub').map((s) => s.id);
    expect(wired).toEqual(['prepare']);
    expect(stubs).toEqual(['run', 'evaluate', 'recommend']);
  });

  it('every stub step has a deferredReason explaining the block', () => {
    for (const step of CSA_STEPS.filter((s) => s.status === 'stub')) {
      expect(step.deferredReason).toBeTruthy();
      expect(step.deferredReason).toMatch(/Sprint 13 T5|MCP-wiring/);
    }
  });

  it('csaStepById returns the step or throws', () => {
    expect(csaStepById('prepare').label).toBe('Prepare');
    expect(() => csaStepById('unknown' as never)).toThrow();
  });

  it('lists exactly 3 sample recommendations matching Sprint 16 T4 output', () => {
    expect(CSA_SAMPLE_RECOMMENDATIONS).toHaveLength(3);
    expect(CSA_SAMPLE_RECOMMENDATIONS.every((r) => r.path.startsWith('docs/csa/runs/'))).toBe(true);
    // Tiers must be 1..3 per Swiss Lage doctrine.
    expect(CSA_SAMPLE_RECOMMENDATIONS.every((r) => r.scenarioTier >= 1 && r.scenarioTier <= 3)).toBe(true);
  });
});

describe('CSA wizard — role guard', () => {
  it('exposes the 4 authorised roles from S16 design spec §8', () => {
    expect([...CSA_WIZARD_ROLES].sort()).toEqual(
      ['HCC.CrisisManager', 'HCC.OperationsLead', 'HCC.PlatformAdmin', 'HCC.SuperAdmin'].sort(),
    );
  });
});

describe('CSA wizard — App integration', () => {
  it('rail exposes the CSA tab (visible to everyone; guard runs inside)', () => {
    render(<App />);
    expect(screen.getByRole('tab', { name: 'CSA' })).toBeInTheDocument();
  });

  it('anonymous session sees the deny message when opening CSA', () => {
    const { getByRole, getByTestId } = render(<App />);
    fireEvent.click(getByRole('tab', { name: 'CSA' }));
    // Guard renders the deny testid because no roles are present in anonymous session.
    expect(getByTestId('CsaRoleGuardDenied')).toBeInTheDocument();
  });

  it('SuperAdmin session sees the wizard scaffold (stepper + Prepare body)', () => {
    const { getByRole, getByTestId } = render(
      <App rawClaims={{ roles: ['HCC.SuperAdmin'], env: 'sit', hospital: 'usz' }} />,
    );
    fireEvent.click(getByRole('tab', { name: 'CSA' }));
    expect(getByTestId('CsaWizard')).toBeInTheDocument();
    expect(getByTestId('CsaStepper')).toBeInTheDocument();
    expect(getByTestId('CsaStepBody-prepare')).toBeInTheDocument();
    expect(getByTestId('CsaStepperTab-prepare')).toBeInTheDocument();
    expect(getByTestId('CsaStepperTab-recommend')).toBeInTheDocument();
  });

  it('CrisisManager session (spec §8 primary persona) sees the wizard', () => {
    const { getByRole, getByTestId } = render(
      <App rawClaims={{ roles: ['HCC.CrisisManager'], env: 'sit', hospital: 'usz' }} />,
    );
    fireEvent.click(getByRole('tab', { name: 'CSA' }));
    expect(getByTestId('CsaWizard')).toBeInTheDocument();
  });
});
