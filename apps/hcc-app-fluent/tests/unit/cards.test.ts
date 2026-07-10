import { describe, it, expect } from 'vitest';
import { cardRegistry, registeredCardTypes, resolveCard } from '../../src/whiteboard/CardRegistry';
import { bedManagerCards } from '../../src/workspaces/main/boards/bed-manager/mock-data';
import type { CardType } from '../../src/cards/card-types';

const EXPECTED: CardType[] = [
  'PowerBITile',
  'AgentPanel',
  'KpiCard',
  'LiveStreamCard',
  'ResponsibleCard',
  'ScenarioCard',
  'BvaHeadlineKpiCard',
  'BvaPlanVsActualCard',
  'BvaTrendCard',
  'BomCard',
  'AdrCard',
  'PrdRequirementCard',
  'GaEvidenceCard',
  'DependencyEdge',
];

const OPERATIONAL: CardType[] = [
  'PowerBITile',
  'AgentPanel',
  'KpiCard',
  'LiveStreamCard',
  'ResponsibleCard',
  'ScenarioCard',
];

describe('CardRegistry', () => {
  it('registers all card types (design spec §5.2 + BVA T7)', () => {
    expect(registeredCardTypes.sort()).toEqual([...EXPECTED].sort());
  });

  it('resolves every registered card type to a component', () => {
    for (const type of EXPECTED) {
      expect(typeof resolveCard(type)).toBe('function');
    }
  });

  it('throws on an unknown card type', () => {
    // @ts-expect-error deliberately invalid type
    expect(() => resolveCard('Nope')).toThrow();
  });
});

describe('BedManager mock data', () => {
  it('exercises all 6 operational card types', () => {
    const used = new Set(bedManagerCards.map((c) => c.type));
    expect([...used].sort()).toEqual([...OPERATIONAL].sort());
  });

  it('contains no obvious PHI identifiers', () => {
    const serialized = JSON.stringify(bedManagerCards).toLowerCase();
    expect(serialized).not.toMatch(/patient|ahv|geburtsdatum|dob|ssn/);
  });

  it('every card resolves via the registry', () => {
    for (const card of bedManagerCards) {
      expect(cardRegistry[card.type]).toBeDefined();
    }
  });
});
