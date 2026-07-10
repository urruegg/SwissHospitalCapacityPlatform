import { describe, it, expect } from 'vitest';
import { cardRegistry } from '../../src/whiteboard/CardRegistry';
import { bvaBoardCards } from '../../src/workspaces/main/boards/bva/mock-data';
import { budgetRag } from '../../src/data/bva/bva-evidence';
import type { CardType } from '../../src/cards/card-types';

const BVA_TYPES: CardType[] = ['BvaHeadlineKpiCard', 'BvaPlanVsActualCard', 'BvaTrendCard'];

describe('BVA cards (Sprint 15 T7)', () => {
  it('registers the three BVA card types', () => {
    for (const type of BVA_TYPES) {
      expect(cardRegistry[type]).toBeDefined();
      expect(typeof cardRegistry[type]).toBe('function');
    }
  });

  it('BVA board mock exercises all three BVA card types', () => {
    const used = new Set(bvaBoardCards.map((c) => c.type));
    expect([...used].sort()).toEqual([...BVA_TYPES].sort());
  });

  it('every BVA card resolves via the registry', () => {
    for (const card of bvaBoardCards) {
      expect(cardRegistry[card.type]).toBeDefined();
    }
  });

  it('every BVA card carries provenance (source + asOf) and the embed fallback flag', () => {
    for (const card of bvaBoardCards) {
      const p = card.payload as { source?: string; asOf?: string; powerBiEmbedFallback?: boolean };
      expect(p.source).toBeTruthy();
      expect(p.asOf).toMatch(/^\d{4}-\d{2}-\d{2}/);
      expect(p.powerBiEmbedFallback).toBe(true);
    }
  });

  it('contains no PHI identifiers', () => {
    const serialized = JSON.stringify(bvaBoardCards).toLowerCase();
    expect(serialized).not.toMatch(/patient|ahv|geburtsdatum|dob|ssn/);
  });

  it('budgetRag maps variance to RAG (under budget = good)', () => {
    expect(budgetRag(-2.9)).toBe('good');
    expect(budgetRag(0)).toBe('good');
    expect(budgetRag(5)).toBe('neutral');
    expect(budgetRag(15)).toBe('bad');
  });
});
