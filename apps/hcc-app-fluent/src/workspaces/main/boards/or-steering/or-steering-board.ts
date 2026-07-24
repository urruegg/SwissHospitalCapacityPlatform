import i18n from '../../../../i18n';
import type { RoleBoard, RoleBoardData, ContextInsight } from '../../../../journey/RoleBoard';
import type { OrSteeringPayload } from '../../../../data/roleboard/or-steering-data';
import { loadOrSteering } from '../../../../data/roleboard/golden-source-client';

/** Sprint 20 (parity) — the orsa RoleBoard implementation (OR steering). */
export const orSteeringBoard: RoleBoard<OrSteeringPayload> = {
  agent: 'orsa-agent',
  ceiling: 'write',
  load: (scope, mode) => loadOrSteering(scope, mode),
  insights: (data: RoleBoardData<OrSteeringPayload>): ContextInsight[] => {
    const seen = new Set<string>();
    return data.payload.cases
      .filter((c) => c.deferable)
      .map((c) => ({
        id: c.recoId,
        label: i18n.t('insight.orDefer', { specialty: c.specialty }),
        context: {
          case: c.id,
          specialty: c.specialty,
          slot: c.slot,
          bedsImpact: c.bedsImpact,
        },
      }))
      .filter((ins) => {
        if (seen.has(ins.id)) return false;
        seen.add(ins.id);
        return true;
      });
  },
  askAbout: [
    i18n.t('orsa.askAbout.deferrableCases'),
    i18n.t('orsa.askAbout.orroomPressure'),
    i18n.t('orsa.askAbout.sbaHandoff'),
  ],
  defaultReco: (data: RoleBoardData<OrSteeringPayload>) => data.payload.defaultReco,
  recoFor: (insight: ContextInsight, data: RoleBoardData<OrSteeringPayload>) =>
    data.payload.recoById[insight.id] ?? data.payload.defaultReco,
  toHandoff: (data: RoleBoardData<OrSteeringPayload>) => ({
    fromAgent: 'orsa-agent',
    headline: `${data.payload.casesDeferred} cases deferred, site still ${data.payload.residualBeds} beds`,
    metrics: { casesDeferred: data.payload.casesDeferred, deltaBeds: data.payload.residualBeds },
  }),
  fromHandoff: (prev) => ({
    situation: prev ? prev.headline : 'OR steering',
    loopBackToOoa: true, // ORSA banner always loops back to OOA
  }),
};
