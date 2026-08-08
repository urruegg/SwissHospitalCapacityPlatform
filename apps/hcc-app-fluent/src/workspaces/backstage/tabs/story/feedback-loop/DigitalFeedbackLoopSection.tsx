import { makeStyles, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { useCopilotRail } from '../../../../../copilot-rail/rail-context';
import { enrichWithLiveAnswer } from '../../../../start/frontier/start-rail';
import { SectionHeader } from '../../../../shared/narrative/SectionHeader';
import { DigitalFeedbackLoop } from './DigitalFeedbackLoop';
import { FEEDBACK_LOOP_DOMAINS, type FeedbackLoopDomain } from './feedback-loop-model';
import { buildInsight, buildReco } from './build-reco';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
});

export function DigitalFeedbackLoopSection() {
  const styles = useStyles();
  const { t } = useTranslation();
  let rail: ReturnType<typeof useCopilotRail> | null = null;
  try {
    rail = useCopilotRail();
  } catch {
    rail = null;
  }

  // Selecting a domain opens the docked Copilot Product Owner Agent with the grounded response.
  const handleDomainSelect = (domain: FeedbackLoopDomain) => {
    const mapped = FEEDBACK_LOOP_DOMAINS.find((candidate) => candidate.id === domain.id);
    if (!mapped) return;
    const label = t(mapped.curaviasLabelKey);
    const domainReco = buildReco(mapped, label, t);
    rail?.openWithReco(buildInsight(mapped, label), domainReco);
    if (rail) {
      void enrichWithLiveAnswer(domainReco.read, rail).catch((error) => {
        console.error('PO agent live enrichment failed', error);
      });
    }
  };

  return (
    <section
      className={styles.root}
      data-testid="digital-feedback-loop-section"
      aria-labelledby="feedback-loop-title"
    >
      <SectionHeader
        id="feedback-loop"
        variant="eyebrow"
        header={t(
          'backstage.story.feedbackLoop.section.header',
          'Trusted signals become governed action through Microsoft IQ',
        )}
        tagline={t('backstage.story.feedbackLoop.section.tagline', 'Backstage \u00b7 The digital feedback loop')}
        description={t(
          'backstage.story.feedbackLoop.section.description',
          'Every domain sends signals into Microsoft IQ, gets a proposed action back, and returns a measured outcome \u2014 with a human approving before anything acts. Select any domain to ask the Product Owner Agent for grounded, cited detail.',
        )}
      />
      <DigitalFeedbackLoop
        domains={FEEDBACK_LOOP_DOMAINS}
        onDomainSelect={handleDomainSelect}
        presentationMode={false}
      />
    </section>
  );
}
