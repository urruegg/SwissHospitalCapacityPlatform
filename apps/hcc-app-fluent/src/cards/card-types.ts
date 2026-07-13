/**
 * Sprint 13 T3 — shared card contract for the operational whiteboard.
 *
 * Cards are plugged into the whiteboard via the CardRegistry (design spec §3:
 * "cards are plugged in via a registry"). Each card owns its own data fetch; in
 * Sprint 13 the data is mock-only (real Fabric wiring is Sprint 14+).
 */
export type CardType =
  | 'PowerBITile'
  | 'AgentPanel'
  | 'KpiCard'
  | 'LiveStreamCard'
  | 'ResponsibleCard'
  | 'ScenarioCard'
  | 'BvaHeadlineKpiCard'
  | 'BvaPlanVsActualCard'
  | 'BvaTrendCard'
  | 'BomCard'
  | 'AdrCard'
  | 'PrdRequirementCard'
  | 'GaEvidenceCard'
  | 'DependencyEdge';

export interface CardPosition {
  x: number;
  y: number;
}

export interface CardModel<TPayload = unknown> {
  id: string;
  type: CardType;
  title: string;
  position: CardPosition;
  payload: TPayload;
}
