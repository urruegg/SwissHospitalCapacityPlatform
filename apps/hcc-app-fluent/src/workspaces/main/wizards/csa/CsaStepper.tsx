/**
 * Sprint 16.1 · S16.5 — CSA wizard stepper.
 *
 * Renders the 4 CSA phases as a horizontal TabList with:
 *   - Current step highlighted
 *   - Completed steps clickable to jump back
 *   - Future steps disabled until reached
 * Kept small + testable; the parent CsaWizard owns the current-step state.
 */
import { makeStyles, tokens, TabList, Tab } from '@fluentui/react-components';
import { CSA_STEPS, type CsaStepId } from './csa-steps';

const useStyles = makeStyles({
  root: {
    marginBottom: tokens.spacingVerticalL,
    paddingBottom: tokens.spacingVerticalS,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  progress: {
    marginTop: tokens.spacingVerticalXS,
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground3,
  },
});

interface CsaStepperProps {
  currentStep: CsaStepId;
  onStepChange: (step: CsaStepId) => void;
}

function stepIndex(id: CsaStepId): number {
  return CSA_STEPS.findIndex((s) => s.id === id);
}

export function CsaStepper({ currentStep, onStepChange }: CsaStepperProps) {
  const styles = useStyles();
  const currentIndex = stepIndex(currentStep);
  return (
    <div className={styles.root} data-testid="CsaStepper">
      <TabList
        selectedValue={currentStep}
        onTabSelect={(_e, data) => {
          const target = data.value as CsaStepId;
          const targetIndex = stepIndex(target);
          // Only allow navigating to past/current steps to keep the flow linear.
          if (targetIndex >= 0 && targetIndex <= currentIndex) {
            onStepChange(target);
          }
        }}
        aria-label="CSA wizard steps"
      >
        {CSA_STEPS.map((step, i) => (
          <Tab
            key={step.id}
            value={step.id}
            disabled={i > currentIndex}
            data-testid={`CsaStepperTab-${step.id}`}
          >
            {`${i + 1}. ${step.label}`}
          </Tab>
        ))}
      </TabList>
      <div className={styles.progress}>
        Step {currentIndex + 1} of {CSA_STEPS.length}
      </div>
    </div>
  );
}
