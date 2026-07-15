/**
 * Sprint 16.1 · S16.5 — top-level CSA wizard component.
 *
 * Composes:
 *   - CsaRoleGuard (role gate: HCC.CrisisManager / OperationsLead / PlatformAdmin / SuperAdmin)
 *   - CsaStepper (4-step progress: Prepare → Run → Evaluate → Recommend)
 *   - CsaStepBody (per-step content; Prepare is wired live, Run/Evaluate stubs, Recommend read-only)
 *   - CopilotDrawer with `agent="csa-agent"` in the right rail
 *
 * The drawer stays open across steps as the design spec (§8) requires.
 * Wizard state (current step + drawer open) lives here; deep tests live in
 * CsaRoleGuard/CsaStepper unit files.
 */
import { useState } from 'react';
import {
  Body1,
  Button,
  makeStyles,
  Subtitle2,
  Title2,
  tokens,
} from '@fluentui/react-components';
import { CopilotDrawer } from '../../../../copilot-drawer/Drawer';
import { CsaRoleGuard } from './CsaRoleGuard';
import { CsaStepper } from './CsaStepper';
import { CsaStepBody } from './CsaStepBody';
import type { CsaStepId } from './csa-steps';

const useStyles = makeStyles({
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: tokens.spacingVerticalM,
  },
  subtitle: { marginBottom: tokens.spacingVerticalS, color: tokens.colorNeutralForeground2 },
});

export function CsaWizard() {
  const styles = useStyles();
  const [step, setStep] = useState<CsaStepId>('prepare');
  const [drawerOpen, setDrawerOpen] = useState(false);
  return (
    <CsaRoleGuard>
      <section aria-label="Crisis Scenario Analysis wizard" data-testid="CsaWizard">
        <div className={styles.header}>
          <div>
            <Title2>Crisis Scenario Analysis</Title2>
            <Subtitle2 as="p" className={styles.subtitle}>
              Prepare → Run → Evaluate → Recommend, guided by <code>csa-agent</code>.
            </Subtitle2>
          </div>
          <Button appearance="primary" onClick={() => setDrawerOpen(true)}>
            Ask csa-agent
          </Button>
        </div>
        <CsaStepper currentStep={step} onStepChange={setStep} />
        <CsaStepBody step={step} onAdvance={setStep} />
        <Body1 as="p" style={{ marginTop: tokens.spacingVerticalXL, color: tokens.colorNeutralForeground3 }}>
          Scaffold shipped as part of Sprint 16.1 (S16.5 close). Run/Evaluate/Recommend
          are stubs awaiting Sprint 13 T5 MCP-wiring completion; Prepare uses the live
          csa-agent chat endpoint via the same invoker as the drawer.
        </Body1>
        <CopilotDrawer agent="csa-agent" open={drawerOpen} onOpenChange={setDrawerOpen} />
      </section>
    </CsaRoleGuard>
  );
}
