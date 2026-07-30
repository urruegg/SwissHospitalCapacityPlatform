import type { TFunction } from 'i18next';
import type { ContextInsight } from '../../../../../journey/RoleBoard';
import type { GroundedReco } from '../../../../../copilot-rail/reco';
import type { FeedbackLoopDomain } from './feedback-loop-model';
import { DOMAIN_DETAIL } from './feedback-loop-detail';

function listLabels(ids: readonly string[], keyPrefix: string, t: TFunction) {
  return ids.map((id) => t(`${keyPrefix}.${id}`, id)).join(', ');
}

export function buildInsight(domain: FeedbackLoopDomain, label: string): ContextInsight {
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

export function buildReco(
  domain: FeedbackLoopDomain,
  domainLabel: string,
  t: TFunction,
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
  const detail = DOMAIN_DETAIL[domain.id];

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
      { text: `${t('backstage.story.feedbackLoop.poAgent.phase.signal', 'Signal packets arrive')}: ${detail.signal}` },
      { text: `${t('backstage.story.feedbackLoop.poAgent.phase.iq', 'Microsoft IQ makes sense')}: ${detail.iq}` },
      {
        text: `${t('backstage.story.feedbackLoop.poAgent.phase.action', 'Action returns')}: ${detail.action}`,
        impact: {
          label: t('backstage.story.feedbackLoop.reco.impactLabel', 'human decision'),
          tone: 'status',
        },
      },
      { text: `${t('backstage.story.feedbackLoop.poAgent.phase.outcome', 'Outcome closes the loop')}: ${detail.outcome}` },
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
