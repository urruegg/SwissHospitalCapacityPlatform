import type { CardModel } from '../../cards/card-types';
import demo from './evidence-demo.json';
import type {
  EvidenceDataset,
  BomCardPayload,
  AdrCardPayload,
  PrdRequirementCardPayload,
  GaEvidenceCardPayload,
  DependencyEdgePayload,
} from './evidence-types';
import {
  bvaHeadlineKpis,
  bvaPlanVsActual,
  bvaTrend,
  type BvaHeadlineKpiPayload,
  type BvaPlanVsActualPayload,
  type BvaTrendPayload,
} from '../bva/bva-evidence';

/**
 * Sprint 14.1 · T5/T6 — Showcase Evidence data source for the presenter
 * whiteboard.
 *
 * Reads the committed `evidence-demo.json` fixture (generated from the seed
 * catalogs by `scripts/evidence/build_app_fixture.py`). This is the dev/CI
 * source; a future wiring can swap in the Fabric SQL endpoint / Direct Lake
 * REST behind {@link loadEvidenceDataset} without touching the cards
 * (ADR-0026 · design spec §5). No PHI — governance metadata only.
 */
export function loadEvidenceDataset(): EvidenceDataset {
  return demo as EvidenceDataset;
}

const COL_W = 280;
const ROW_H = 220;
const COLS = 6;

function gridPosition(index: number) {
  return {
    x: (index % COLS) * COL_W + 16,
    y: Math.floor(index / COLS) * ROW_H + 16,
  };
}

/** Preset presenter layouts (design spec §4 "shared demo layouts"). */
export type EvidencePreset = 'ch-north-tshow' | 'ga-parity' | 'bva';

export interface EvidenceLayout {
  key: EvidencePreset;
  labelKey: string;
  cards: CardModel[];
}

function bomCards(dataset: EvidenceDataset, offset: number): CardModel[] {
  return dataset.boms.map((payload: BomCardPayload, i) => ({
    id: `bom-card-${payload.id}`,
    type: 'BomCard' as const,
    title: payload.name,
    position: gridPosition(offset + i),
    payload,
  }));
}

function adrCards(dataset: EvidenceDataset, offset: number): CardModel[] {
  return dataset.adrs.map((payload: AdrCardPayload, i) => ({
    id: `adr-card-${payload.id}`,
    type: 'AdrCard' as const,
    title: payload.id,
    position: gridPosition(offset + i),
    payload,
  }));
}

function requirementCards(dataset: EvidenceDataset, offset: number): CardModel[] {
  return dataset.requirements.map((payload: PrdRequirementCardPayload, i) => ({
    id: `req-card-${payload.id}`,
    type: 'PrdRequirementCard' as const,
    title: payload.id,
    position: gridPosition(offset + i),
    payload,
  }));
}

function gaEvidenceCards(dataset: EvidenceDataset, offset: number): CardModel[] {
  return dataset.gaEvidence.map((payload: GaEvidenceCardPayload, i) => ({
    id: `ga-card-${payload.bomId}-${payload.region}`,
    type: 'GaEvidenceCard' as const,
    title: payload.bomId,
    position: gridPosition(offset + i),
    payload,
  }));
}

function dependencyCards(dataset: EvidenceDataset, offset: number): CardModel[] {
  return dataset.dependencies.map((payload: DependencyEdgePayload, i) => ({
    id: `edge-card-${payload.fromId}-${payload.toId}`,
    type: 'DependencyEdge' as const,
    title: `${payload.fromId} → ${payload.toId}`,
    position: gridPosition(offset + i),
    payload,
  }));
}

/**
 * Sprint 15.4 mini-scope — BVA card cluster on the Evidence whiteboard.
 *
 * Projects the 3 registered BVA card types (`BvaHeadlineKpiCard`,
 * `BvaPlanVsActualCard`, `BvaTrendCard`) from `data/bva/bva-evidence.ts` onto
 * whiteboard `CardModel` entries so the `bva` preset can render them. Payload
 * shapes are unchanged and provenance stamps are preserved (design spec §6/§7).
 */
function bvaCards(offset: number): CardModel[] {
  const cards: CardModel[] = [];
  bvaHeadlineKpis.forEach((payload: BvaHeadlineKpiPayload, i) => {
    cards.push({
      id: `bva-card-headline-${i}`,
      type: 'BvaHeadlineKpiCard' as const,
      title: payload.measure,
      position: gridPosition(offset + cards.length),
      payload,
    });
  });
  cards.push({
    id: 'bva-card-plan-vs-actual',
    type: 'BvaPlanVsActualCard' as const,
    title: (bvaPlanVsActual as BvaPlanVsActualPayload).measure,
    position: gridPosition(offset + cards.length),
    payload: bvaPlanVsActual,
  });
  cards.push({
    id: 'bva-card-trend',
    type: 'BvaTrendCard' as const,
    title: (bvaTrend as BvaTrendPayload).measure,
    position: gridPosition(offset + cards.length),
    payload: bvaTrend,
  });
  return cards;
}

/**
 * Build the full presenter card catalog for a preset. The `ch-north-tshow`
 * and `ga-parity` presets render the whole BOM + ADR + PRD-requirement catalog
 * and dependency edges (the E2E acceptance floor is >=25 BOM + >=10 ADR + >=1
 * PRD-req); the `ga-parity` preset additionally surfaces GA-evidence chips.
 *
 * The `bva` preset (Sprint 15.4 mini-scope) renders only the BVA card cluster
 * so the boardroom BVA view stays uncluttered by BOM/ADR/req context.
 */
export function buildEvidenceCards(
  preset: EvidencePreset,
  dataset: EvidenceDataset = loadEvidenceDataset(),
): CardModel[] {
  if (preset === 'bva') {
    return bvaCards(0);
  }
  const boms = bomCards(dataset, 0);
  const reqs = requirementCards(dataset, boms.length);
  const adrs = adrCards(dataset, boms.length + reqs.length);
  const edges = dependencyCards(dataset, boms.length + reqs.length + adrs.length);
  const base = [...boms, ...reqs, ...adrs, ...edges];
  if (preset === 'ga-parity') {
    return [...base, ...gaEvidenceCards(dataset, base.length)];
  }
  return base;
}

export function evidenceLayouts(dataset: EvidenceDataset = loadEvidenceDataset()): EvidenceLayout[] {
  return [
    {
      key: 'ch-north-tshow',
      labelKey: 'evidence.presetChNorthTShow',
      cards: buildEvidenceCards('ch-north-tshow', dataset),
    },
    {
      key: 'ga-parity',
      labelKey: 'evidence.presetGaParity',
      cards: buildEvidenceCards('ga-parity', dataset),
    },
    {
      key: 'bva',
      labelKey: 'evidence.presetBva',
      cards: buildEvidenceCards('bva', dataset),
    },
  ];
}
