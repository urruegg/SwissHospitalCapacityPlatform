import type { ComponentType } from 'react';
import type { CardModel, CardType } from '../cards/card-types';
import { PowerBITile } from '../cards/PowerBITile';
import { AgentPanel } from '../cards/AgentPanel';
import { KpiCard } from '../cards/KpiCard';
import { LiveStreamCard } from '../cards/LiveStreamCard';
import { ResponsibleCard } from '../cards/ResponsibleCard';
import { ScenarioCard } from '../cards/ScenarioCard';
import { BvaHeadlineKpiCard } from '../cards/bva/BvaHeadlineKpiCard';
import { BvaPlanVsActualCard } from '../cards/bva/BvaPlanVsActualCard';
import { BvaTrendCard } from '../cards/bva/BvaTrendCard';
import { BomCard } from '../cards/evidence/BomCard';
import { AdrCard } from '../cards/evidence/AdrCard';
import { PrdRequirementCard } from '../cards/evidence/PrdRequirementCard';
import { GaEvidenceCard } from '../cards/evidence/GaEvidenceCard';
import { DependencyEdge } from '../cards/evidence/DependencyEdge';

/**
 * Sprint 13 T3 — card registry.
 *
 * Maps a {@link CardType} to its renderer so the whiteboard stays card-agnostic
 * (design spec §3). Adding a new card type is a one-line registration.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyCardComponent = ComponentType<{ card: CardModel<any> }>;

export const cardRegistry: Record<CardType, AnyCardComponent> = {
  PowerBITile,
  AgentPanel,
  KpiCard,
  LiveStreamCard,
  ResponsibleCard,
  ScenarioCard,
  BvaHeadlineKpiCard,
  BvaPlanVsActualCard,
  BvaTrendCard,
  BomCard,
  AdrCard,
  PrdRequirementCard,
  GaEvidenceCard,
  DependencyEdge,
};

export function resolveCard(type: CardType): AnyCardComponent {
  const component = cardRegistry[type];
  if (!component) throw new Error(`Unknown card type: ${type}`);
  return component;
}

export const registeredCardTypes = Object.keys(cardRegistry) as CardType[];
