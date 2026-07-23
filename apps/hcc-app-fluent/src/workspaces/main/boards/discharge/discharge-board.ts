import i18n from '../../../../i18n';
import type { GroundedReco } from '../../../../copilot-rail/reco';
import type { RoleBoard, RoleBoardData, ContextInsight } from '../../../../journey/RoleBoard';
import type { DischargePayload } from '../../../../data/roleboard/discharge-data';
import { loadDischarge } from '../../../../data/roleboard/golden-source-client';

/** Sprint 2 (parity) — the dca RoleBoard implementation (discharge readiness). */
export const dischargeBoard: RoleBoard<DischargePayload> = {
  agent: 'dca-agent',
  ceiling: 'write',
  load: (scope, mode) => loadDischarge(scope, mode),
  insights: (data: RoleBoardData<DischargePayload>) =>
    data.payload.candidates
      .filter((c) => c.expedite === true)
      .map((c) => ({
        id: c.id,
        label: i18n.t('insight.dischargeExpedite', { ward: c.ward }),
        context: {
          candidate: c.id,
          ward: c.ward,
          blocker: c.blocker,
          bedsFreeable: c.bedsFreeable,
        },
      })),
  askAbout: [
    'What changed since last shift?',
    'Where is the biggest pressure?',
  ],
  defaultReco(): GroundedReco {
    return {
      agentLabel: 'Discharge Copilot',
      contextChip: { subject: 'Shift summary', tone: 'ok' },
      read: 'No proactive recommendation wired for this board yet (parity build focuses on occupancy).',
      levers: [],
      citations: [],
      provenance: 'simulated',
    };
  },
  recoFor(insight: ContextInsight): GroundedReco {
    return {
      agentLabel: 'Discharge Copilot',
      contextChip: { subject: insight.label, tone: 'watch' },
      read: `Context picked up for ${insight.label}. Detailed recommendation lands in a later sprint.`,
      levers: [],
      citations: [],
      provenance: 'simulated',
    };
  },
  toHandoff: (data: RoleBoardData<DischargePayload>) => ({
    fromAgent: 'dca-agent',
    headline: `${data.payload.bedsFreeable} discharges free beds, site still ${data.payload.residualBeds} beds`,
    metrics: { bedsFreeable: data.payload.bedsFreeable, deltaBeds: data.payload.residualBeds },
  }),
  fromHandoff: (prev) => ({
    situation: prev ? prev.headline : 'Discharge readiness',
    loopBackToOoa: false,
  }),
};
