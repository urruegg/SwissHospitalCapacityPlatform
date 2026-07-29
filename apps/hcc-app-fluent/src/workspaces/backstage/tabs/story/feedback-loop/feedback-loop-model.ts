export const IQ_LAYERS = [
  'work',
  'foundry',
  'fabric',
  'process',
  'governance',
] as const;

export type IqLayer = (typeof IQ_LAYERS)[number];
export type FeedbackLoopMode = 'all' | 'selected';
export type FeedbackLoopDomainId =
  | 'care-ecosystem'
  | 'command-center'
  | 'frontier-workforce'
  | 'care-innovation';

export interface FeedbackLoopDomain {
  id: FeedbackLoopDomainId;
  curaviasLabelKey: string;
  microsoftLabelKey: string;
  groupLabelKey: string;
  signalIds: readonly string[];
  proposedActionId: string;
  outcomeId: string;
  iqLayers: readonly IqLayer[];
  citations: readonly string[];
}

export interface DigitalFeedbackLoopProps {
  domains: readonly FeedbackLoopDomain[];
  onDomainSelect?: (domain: FeedbackLoopDomain) => void;
  presentationMode?: boolean;
}

const FEEDBACK_LOOP_CITATIONS = [
  'docs/PRD.md#fr-poa-001',
  'docs/PRD.md#fr-poa-002',
  'docs/ARCHITECTURE.md',
  'docs/adr/0043-product-owner-agent-foundry-iq-domain.md',
] as const;

export const FEEDBACK_LOOP_DOMAINS = [
  {
    id: 'care-ecosystem',
    curaviasLabelKey: 'backstage.story.feedbackLoop.domain.care-ecosystem.curavias',
    microsoftLabelKey: 'backstage.story.feedbackLoop.domain.care-ecosystem.microsoft',
    groupLabelKey: 'backstage.story.feedbackLoop.domain.care-ecosystem.group',
    signalIds: ['referrals', 'partner-capacity'],
    proposedActionId: 'coordinate-placement',
    outcomeId: 'continuity-access',
    iqLayers: ['work', 'fabric', 'process', 'governance'],
    citations: FEEDBACK_LOOP_CITATIONS,
  },
  {
    id: 'command-center',
    curaviasLabelKey: 'backstage.story.feedbackLoop.domain.command-center.curavias',
    microsoftLabelKey: 'backstage.story.feedbackLoop.domain.command-center.microsoft',
    groupLabelKey: 'backstage.story.feedbackLoop.domain.command-center.group',
    signalIds: ['occupancy', '72-hour-demand'],
    proposedActionId: 'rebalance-coordinate',
    outcomeId: 'wait-time-utilization',
    iqLayers: ['foundry', 'fabric', 'process', 'governance'],
    citations: FEEDBACK_LOOP_CITATIONS,
  },
  {
    id: 'frontier-workforce',
    curaviasLabelKey: 'backstage.story.feedbackLoop.domain.frontier-workforce.curavias',
    microsoftLabelKey: 'backstage.story.feedbackLoop.domain.frontier-workforce.microsoft',
    groupLabelKey: 'backstage.story.feedbackLoop.domain.frontier-workforce.group',
    signalIds: ['skills', 'staffing', 'workload'],
    proposedActionId: 'mobilize-capacity',
    outcomeId: 'workload-adoption',
    iqLayers: ['work', 'fabric', 'process', 'governance'],
    citations: FEEDBACK_LOOP_CITATIONS,
  },
  {
    id: 'care-innovation',
    curaviasLabelKey: 'backstage.story.feedbackLoop.domain.care-innovation.curavias',
    microsoftLabelKey: 'backstage.story.feedbackLoop.domain.care-innovation.microsoft',
    groupLabelKey: 'backstage.story.feedbackLoop.domain.care-innovation.group',
    signalIds: ['outcomes', 'telemetry'],
    proposedActionId: 'improve-pathway',
    outcomeId: 'quality-adoption',
    iqLayers: ['foundry', 'fabric', 'process', 'governance'],
    citations: FEEDBACK_LOOP_CITATIONS,
  },
] as const satisfies readonly FeedbackLoopDomain[];
