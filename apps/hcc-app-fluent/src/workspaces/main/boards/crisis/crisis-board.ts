import i18n from '../../../../i18n';
import type { GroundedReco } from '../../../../copilot-rail/reco';
import type { RoleBoard, RoleBoardData, ContextInsight } from '../../../../journey/RoleBoard';
import type { CrisisPayload } from '../../../../data/roleboard/crisis-data';
import { loadCrisis } from '../../../../data/roleboard/golden-source-client';

/** Sprint 4 (parity) — the csa RoleBoard implementation (crisis readiness). */
export const crisisBoard: RoleBoard<CrisisPayload> = {
  agent: 'csa-agent',
  ceiling: 'deploy',
  load: (scope, mode) => loadCrisis(scope, mode),
  insights: (data: RoleBoardData<CrisisPayload>) =>
    data.payload.scenarios.map((s) => ({
      id: s.id,
      label: i18n.t('insight.stressTest', { scenario: s.label }),
      context: {
        scenario: s.id,
        probability: s.probability,
        bedDayImpact: s.bedDayImpact,
      },
    })),
  askAbout: [
    'What changed since last shift?',
    'Where is the biggest pressure?',
  ],
  defaultReco(): GroundedReco {
    return {
      agentLabel: 'Crisis Copilot',
      contextChip: { subject: 'Shift summary', tone: 'ok' },
      read: 'No proactive recommendation wired for this board yet (parity build focuses on occupancy).',
      levers: [],
      citations: [],
      provenance: 'simulated',
    };
  },
  recoFor(insight: ContextInsight): GroundedReco {
    return {
      agentLabel: 'Crisis Copilot',
      contextChip: { subject: insight.label, tone: 'watch' },
      read: `Context picked up for ${insight.label}. Detailed recommendation lands in a later sprint.`,
      levers: [],
      citations: [],
      provenance: 'simulated',
    };
  },
  toHandoff: (data: RoleBoardData<CrisisPayload>) => {
    const top = data.payload.scenarios.reduce((best, s) =>
      s.probability > best.probability ? s : best,
    );
    return {
      fromAgent: 'csa-agent',
      headline: `${top.label} p=${top.probability} would add ${top.bedDayImpact} bed-days - loop back to occupancy`,
      metrics: { probability: top.probability, bedDayImpact: top.bedDayImpact },
    };
  },
  fromHandoff: (prev) => ({
    situation: prev ? prev.headline : 'Crisis readiness',
    loopBackToOoa: true,
  }),
};
