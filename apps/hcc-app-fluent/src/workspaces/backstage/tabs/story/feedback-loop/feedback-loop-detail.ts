import type { FeedbackLoopDomainId } from './feedback-loop-model';

/**
 * Per-domain narrative for the Product Owner Agent panel — the four phases the
 * mockup shows (signal -> IQ -> action -> outcome). `value` is only set where a
 * grounded business-value figure exists; never invent numbers.
 */
export interface DomainDetail {
  kicker: string;
  signal: string;
  iq: string;
  action: string;
  outcome: string;
  value?: { label: string; figure: string };
}

export const DOMAIN_DETAIL: Record<FeedbackLoopDomainId, DomainDetail> = {
  'care-ecosystem': {
    kicker: 'Care ecosystem',
    signal: 'Referral demand, partner capacity and experience observations stream into IQ.',
    iq: 'Work context, semantic data and grounded reasoning connect the care network.',
    action: 'A coordinated placement recommendation returns for approval.',
    outcome: 'Continuity, access and experience become new evidence.',
  },
  'command-center': {
    kicker: 'Command center',
    signal: 'Occupancy, demand, ED arrivals and trusted hazards stream into IQ.',
    iq: 'Fabric connects meaning; Foundry reasons; Process locates the decision; Governance checks trust.',
    action: 'A governed recommendation travels back to the command center for human approval.',
    outcome: 'Wait time and utilization become the next evidence.',
  },
  'frontier-workforce': {
    kicker: 'Frontier workforce',
    signal: 'Skills, staffing, certifications and workload observations stream into IQ.',
    iq: 'Work context and ontology-grounded reasoning match qualified capacity to demand.',
    action: 'A roster-balancing recommendation returns to the responsible lead.',
    outcome: 'Workload and adoption become new evidence.',
  },
  'care-innovation': {
    kicker: 'Care innovation',
    signal: 'Outcomes, pathway gaps and service telemetry stream into IQ.',
    iq: 'Operational meaning and grounded knowledge identify care-delivery improvements.',
    action: 'A reviewed pathway or guidance improvement returns to the product team.',
    outcome: 'Quality and adoption become new evidence.',
  },
};
