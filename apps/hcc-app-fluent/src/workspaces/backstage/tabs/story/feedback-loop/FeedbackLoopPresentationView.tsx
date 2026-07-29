import {
  Badge,
  Body1,
  Caption1,
  Display,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { DigitalFeedbackLoop } from './DigitalFeedbackLoop';
import { FEEDBACK_LOOP_DOMAINS } from './feedback-loop-model';

const useStyles = makeStyles({
  root: {
    minHeight: '100vh',
    padding: 'clamp(24px, 4vw, 56px)',
    background:
      'radial-gradient(circle at top left, rgba(31, 169, 214, 0.16), transparent 34%), linear-gradient(135deg, #f8fbfc 0%, #eef7f5 100%)',
    color: tokens.colorNeutralForeground1,
    boxSizing: 'border-box',
    overflowX: 'hidden',
    '& [aria-pressed="true"] .fui-Caption1': {
      color: '#0E0F11',
    },
  },
  frame: {
    width: 'min(1440px, 100%)',
    margin: '0 auto',
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXL,
  },
  header: {
    display: 'grid',
    gridTemplateColumns: '1fr auto',
    gap: tokens.spacingHorizontalL,
    alignItems: 'start',
    '@media screen and (max-width: 720px)': {
      gridTemplateColumns: '1fr',
    },
  },
  wordmark: {
    color: '#365B7D',
    fontWeight: tokens.fontWeightSemibold,
    letterSpacing: '0.18em',
    textTransform: 'uppercase',
  },
  titleStack: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalS,
    maxWidth: '880px',
  },
  badges: {
    display: 'flex',
    justifyContent: 'flex-end',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
    '@media screen and (max-width: 720px)': {
      justifyContent: 'flex-start',
    },
  },
  legend: {
    display: 'grid',
    gridTemplateColumns: 'repeat(5, minmax(130px, 1fr))',
    gap: tokens.spacingHorizontalS,
    '@media screen and (max-width: 900px)': {
      gridTemplateColumns: '1fr',
    },
  },
  legendItem: {
    minWidth: 0,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusLarge,
    backgroundColor: 'rgba(255, 255, 255, 0.82)',
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    boxShadow: tokens.shadow2,
  },
  legendIndex: {
    color: '#107C64',
    fontWeight: tokens.fontWeightSemibold,
  },
});

const FLOW_STEPS = [
  'Data points',
  'Microsoft IQ',
  'Proposed action',
  'Human approval',
  'Measured outcome',
] as const;

export function FeedbackLoopPresentationView() {
  const styles = useStyles();

  return (
    <main className={styles.root} data-testid="feedback-loop-presentation">
      <section className={styles.frame} aria-labelledby="feedback-loop-presentation-title">
        <header className={styles.header}>
          <div className={styles.titleStack}>
            <Caption1 className={styles.wordmark}>Curavias</Caption1>
            <Display id="feedback-loop-presentation-title">Digital Feedback Loop</Display>
            <Body1 as="p">
              Synthetic operational signals become grounded recommendations, human-approved actions,
              and measured outcomes that improve the next capacity decision.
            </Body1>
          </div>
          <div className={styles.badges} aria-label="Presentation data posture">
            <Badge appearance="tint" color="success">
              Synthetic demo
            </Badge>
            <Badge appearance="tint" color="informative">
              No PHI
            </Badge>
          </div>
        </header>

        <div className={styles.legend} aria-label="Digital feedback-loop flow">
          {FLOW_STEPS.map((step, index) => (
            <div className={styles.legendItem} key={step}>
              <Caption1 className={styles.legendIndex}>{String(index + 1).padStart(2, '0')}</Caption1>
              <Body1>{step}</Body1>
            </div>
          ))}
        </div>

        <DigitalFeedbackLoop domains={FEEDBACK_LOOP_DOMAINS} presentationMode />
      </section>
    </main>
  );
}
