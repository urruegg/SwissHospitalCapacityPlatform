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
export type EvidencePreset = 'ch-north-tshow' | 'ga-parity';

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
 * Build the full presenter card catalog for a preset. Both presets render the
 * whole BOM + ADR + PRD-requirement catalog and dependency edges (the E2E
 * acceptance floor is >=25 BOM + >=10 ADR + >=1 PRD-req); the "GA-parity" preset
 * additionally surfaces the GA-evidence chips.
 */
export function buildEvidenceCards(
  preset: EvidencePreset,
  dataset: EvidenceDataset = loadEvidenceDataset(),
): CardModel[] {
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
  ];
}
