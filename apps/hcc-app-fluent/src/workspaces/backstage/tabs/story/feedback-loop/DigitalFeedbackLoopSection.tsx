import { Body1, makeStyles, Title3, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import type { ContextInsight } from '../../../../../journey/RoleBoard';
import { useCopilotRail } from '../../../../../copilot-rail/rail-context';
import type { GroundedReco } from '../../../../../copilot-rail/reco';
import { DigitalFeedbackLoop } from './DigitalFeedbackLoop';
import { FEEDBACK_LOOP_DOMAINS, type FeedbackLoopDomain } from './feedback-loop-model';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
  header: {
    maxWidth: '820px',
  },
  lead: {
    marginTop: tokens.spacingVerticalS,
    color: tokens.colorNeutralForeground2,
  },
});

function listLabels(ids: readonly string[], keyPrefix: string, t: ReturnType<typeof useTranslation>['t']) {
  return ids.map((id) => t(`${keyPrefix}.${id}`, id)).join(', ');
}

function buildInsight(domain: FeedbackLoopDomain, label: string): ContextInsight {
  return {
    id: `feedback-loop-${domain.id}`,
    label,
    context: {
      domainId: domain.id,
      signalIds: domain.signalIds,
      proposedActionId: domain.proposedActionId,
      outcomeId: domain.outcomeId,
      iqLayers: domain.iqLayers,
      source: 'backstage-digital-feedback-loop',
    },
  };
}

function buildReco(
  domain: FeedbackLoopDomain,
  domainLabel: string,
  t: ReturnType<typeof useTranslation>['t'],
): GroundedReco {
  const signalLabels = listLabels(domain.signalIds, 'backstage.story.feedbackLoop.signals', t);
  const actionLabel = t(
    `backstage.story.feedbackLoop.actions.${domain.proposedActionId}`,
    domain.proposedActionId,
  );
  const outcomeLabel = t(
    `backstage.story.feedbackLoop.outcomes.${domain.outcomeId}`,
    domain.outcomeId,
  );
  const iqLabels = listLabels(domain.iqLayers, 'backstage.story.feedbackLoop.iq', t);

  return {
    agentLabel: 'product-owner-agent',
    contextChip: {
      subject: domainLabel,
      qualifiers: [signalLabels],
      status: t('backstage.story.feedbackLoop.advisoryNote'),
      tone: 'signal',
    },
    read: t('backstage.story.feedbackLoop.reco.read', {
      domain: domainLabel,
      signals: signalLabels,
      action: actionLabel,
      outcome: outcomeLabel,
    }),
    levers: [
      {
        text: t('backstage.story.feedbackLoop.reco.lever', {
          action: actionLabel,
          outcome: outcomeLabel,
        }),
        impact: {
          label: t('backstage.story.feedbackLoop.reco.impactLabel'),
          tone: 'status',
        },
      },
    ],
    citations: [...domain.citations],
    provenance: 'simulated',
    followUps: [
      t('backstage.story.feedbackLoop.reco.followUps.evidence'),
      t('backstage.story.feedbackLoop.reco.followUps.iqLayers', { layers: iqLabels }),
      t('backstage.story.feedbackLoop.reco.followUps.businessValue'),
    ],
  };
}

export function DigitalFeedbackLoopSection() {
  const styles = useStyles();
  const { t } = useTranslation();
  let rail: ReturnType<typeof useCopilotRail> | null = null;
  try {
    rail = useCopilotRail();
  } catch {
    rail = null;
  }

  const handleDomainSelect = (domain: FeedbackLoopDomain) => {
    const mappedDomain = FEEDBACK_LOOP_DOMAINS.find((candidate) => candidate.id === domain.id);
    if (!mappedDomain) {
      if (import.meta.env.DEV) {
        console.warn(`No feedback-loop recommendation mapping found for domain "${domain.id}".`);
      }
      return;
    }

    const label = t(mappedDomain.curaviasLabelKey);
    rail?.openWithReco(buildInsight(mappedDomain, label), buildReco(mappedDomain, label, t));
  };

  return (
    <section
      className={styles.root}
      data-testid="digital-feedback-loop-section"
      aria-labelledby="digital-feedback-loop-section-title"
    >
      <div className={styles.header}>
        <Title3 id="digital-feedback-loop-section-title">
          {t('backstage.story.feedbackLoop.title')}
        </Title3>
        <Body1 as="p" className={styles.lead}>
          {t('backstage.story.feedbackLoop.lead')}
        </Body1>
      </div>
      <DigitalFeedbackLoop
        domains={FEEDBACK_LOOP_DOMAINS}
        onDomainSelect={handleDomainSelect}
        presentationMode={false}
      />
    </section>
  );
}
