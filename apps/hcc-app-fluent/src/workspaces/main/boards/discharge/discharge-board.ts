import i18n from '../../../../i18n';
import type { RoleBoard, RoleBoardData, ContextInsight } from '../../../../journey/RoleBoard';
import type { DischargePayload } from '../../../../data/roleboard/discharge-data';
import { loadDischarge } from '../../../../data/roleboard/golden-source-client';

/** Sprint 20 (parity) — the dca RoleBoard implementation (discharge readiness). */
export const dischargeBoard: RoleBoard<DischargePayload> = {
  agent: 'dca-agent',
  ceiling: 'write',
  load: (scope, mode) => loadDischarge(scope, mode),
  insights: (data: RoleBoardData<DischargePayload>): ContextInsight[] => {
    const seen = new Set<string>();
    const candidateInsights: ContextInsight[] = data.payload.candidates
      .filter((c) => c.readiness === 'READY')
      .map((c) => ({
        id: c.recoId,
        // Use ward + blocker so no two insight labels are identical even within the same ward
        label: i18n.t('insight.dischargeExpediteDetail', { ward: c.ward, blocker: c.blocker }),
        context: {
          candidate: c.id,
          ward: c.ward,
          blocker: c.blocker,
          bedsFreeable: c.bedsFreeable,
        },
      }));
    const gapInsight: ContextInsight = {
      id: 'discharge-gap',
      label: i18n.t('dca.gap.label'),
      context: { gapBeds: data.payload.residualBeds },
    };
    return [...candidateInsights, gapInsight].filter((ins) => {
      if (seen.has(ins.id)) return false;
      seen.add(ins.id);
      return true;
    });
  },
  askAbout: [
    i18n.t('dca.askAbout.readyCandidates'),
    i18n.t('dca.askAbout.spitexBarrier'),
    i18n.t('dca.askAbout.rehab'),
  ],
  defaultReco: (data: RoleBoardData<DischargePayload>) => data.payload.defaultReco,
  recoFor: (insight: ContextInsight, data: RoleBoardData<DischargePayload>) =>
    data.payload.recoById[insight.id] ?? data.payload.defaultReco,
  toHandoff: (data: RoleBoardData<DischargePayload>) => ({
    fromAgent: 'dca-agent',
    headline: `${data.payload.bedsFreeable} discharges free beds, site still ${data.payload.residualBeds} beds`,
    metrics: { bedsFreeable: data.payload.bedsFreeable, deltaBeds: data.payload.residualBeds },
  }),
  fromHandoff: () => ({
    situation: 'Discharge readiness',
    loopBackToOoa: false,
  }),
};
