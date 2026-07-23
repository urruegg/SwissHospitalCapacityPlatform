import i18n from '../../../../i18n';
import type { GroundedReco } from '../../../../copilot-rail/reco';
import type { RoleBoard, RoleBoardData, ContextInsight } from '../../../../journey/RoleBoard';
import type { OrSteeringPayload } from '../../../../data/roleboard/or-steering-data';
import { loadOrSteering } from '../../../../data/roleboard/golden-source-client';

/** Sprint 3 (parity) — the orsa RoleBoard implementation (OR steering). */
export const orSteeringBoard: RoleBoard<OrSteeringPayload> = {
  agent: 'orsa-agent',
  ceiling: 'write',
  load: (scope, mode) => loadOrSteering(scope, mode),
  insights: (data: RoleBoardData<OrSteeringPayload>) =>
    data.payload.cases
      .filter((c) => c.deferable === true)
      .map((c) => ({
        id: c.id,
        label: i18n.t('insight.orDefer', { specialty: c.specialty }),
        context: {
          case: c.id,
          specialty: c.specialty,
          slot: c.slot,
          bedsImpact: c.bedsImpact,
        },
      })),
  askAbout: [
    'What changed since last shift?',
    'Where is the biggest pressure?',
  ],
  defaultReco(): GroundedReco {
    return {
      agentLabel: 'OR Steering Copilot',
      contextChip: { subject: 'Shift summary', tone: 'ok' },
      read: 'No proactive recommendation wired for this board yet (parity build focuses on occupancy).',
      levers: [],
      citations: [],
      provenance: 'simulated',
    };
  },
  recoFor(insight: ContextInsight): GroundedReco {
    return {
      agentLabel: 'OR Steering Copilot',
      contextChip: { subject: insight.label, tone: 'watch' },
      read: `Context picked up for ${insight.label}. Detailed recommendation lands in a later sprint.`,
      levers: [],
      citations: [],
      provenance: 'simulated',
    };
  },
  toHandoff: (data: RoleBoardData<OrSteeringPayload>) => ({
    fromAgent: 'orsa-agent',
    headline: `${data.payload.casesDeferred} elective cases deferred, site still ${data.payload.residualBeds} beds`,
    metrics: { casesDeferred: data.payload.casesDeferred, deltaBeds: data.payload.residualBeds },
  }),
  fromHandoff: (prev) => ({
    situation: prev ? prev.headline : 'OR steering',
    loopBackToOoa: false,
  }),
};
