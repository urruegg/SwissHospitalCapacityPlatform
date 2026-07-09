import type { CardModel } from '../../../../cards/card-types';

/**
 * Sprint 13 T3 — mock data for the BedManager @ USZ reference whiteboard.
 *
 * Mock only — real Fabric Gold data lands via T6/Sprint 14+ (design spec §2.3).
 * No PHI: figures are synthetic aggregates, no patient identifiers (ADR-0016).
 */
export const bedManagerCards: CardModel[] = [
  {
    id: 'kpi-occupancy',
    type: 'KpiCard',
    title: 'Bettenauslastung',
    position: { x: 24, y: 24 },
    payload: { value: '87', unit: '%', rag: 'neutral', delta: '+3% ggü. Vortag' },
  },
  {
    id: 'kpi-free-beds',
    type: 'KpiCard',
    title: 'Freie Betten',
    position: { x: 312, y: 24 },
    payload: { value: '18', rag: 'good', delta: 'Ziel: > 12' },
  },
  {
    id: 'kpi-pending-discharges',
    type: 'KpiCard',
    title: 'Offene Austritte',
    position: { x: 600, y: 24 },
    payload: { value: '9', rag: 'bad', delta: 'SLA-Risiko' },
  },
  {
    id: 'pbi-ward-heatmap',
    type: 'PowerBITile',
    title: 'Stations-Heatmap',
    position: { x: 24, y: 220 },
    payload: {
      reportName: 'capacity-dashboard',
      embedPlaceholder: 'Power BI Embed (Direct Lake, RLS by hospital) — mock',
    },
  },
  {
    id: 'agent-bmca',
    type: 'AgentPanel',
    title: 'BMCA-Empfehlung',
    position: { x: 312, y: 220 },
    payload: {
      agent: 'bmca-agent',
      lastRecommendation:
        'Verlege 2 Betten von Station B nach Notaufnahme (HITL-02 erforderlich).',
    },
  },
  {
    id: 'live-admissions',
    type: 'LiveStreamCard',
    title: 'Live-Zugänge',
    position: { x: 600, y: 220 },
    payload: {
      source: 'eventstream: admissions',
      events: [
        { ts: '11:02', message: 'Zugang Station A' },
        { ts: '11:06', message: 'Austritt Station C' },
      ],
    },
  },
  {
    id: 'responsible-charge-nurse',
    type: 'ResponsibleCard',
    title: 'Verantwortlich',
    position: { x: 24, y: 420 },
    payload: {
      name: 'Stationsleitung USZ',
      role: 'Charge Nurse — Dienst',
      contact: 'Pager 4412 (Demo)',
    },
  },
  {
    id: 'scenario-surge',
    type: 'ScenarioCard',
    title: 'Szenario',
    position: { x: 312, y: 420 },
    payload: {
      scenario: 'Grippewelle +15% Zugänge',
      status: 'draft',
      summary: 'Vorbereitet für CSA-Auswertung (Sprint 16).',
    },
  },
];
