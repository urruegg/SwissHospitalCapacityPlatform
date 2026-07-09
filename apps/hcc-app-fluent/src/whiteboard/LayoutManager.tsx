import { useCallback, useState } from 'react';
import type { CardModel, CardPosition } from '../cards/card-types';

/**
 * Sprint 13 T3 — in-memory whiteboard layout manager.
 *
 * Holds card positions in React state only. Persistence (Cosmos/Fabric-backed)
 * is explicitly out of scope for Sprint 13 (design spec §2.3) — layout resets on
 * reload. Kept as a hook so a persistent implementation can be swapped in behind
 * the same interface later.
 */
export interface LayoutManager {
  cards: CardModel[];
  moveCard: (id: string, position: CardPosition) => void;
  reset: (cards: CardModel[]) => void;
}

export function useLayoutManager(initial: CardModel[]): LayoutManager {
  const [cards, setCards] = useState<CardModel[]>(initial);

  const moveCard = useCallback((id: string, position: CardPosition) => {
    setCards((prev) =>
      prev.map((c) => (c.id === id ? { ...c, position } : c)),
    );
  }, []);

  const reset = useCallback((next: CardModel[]) => setCards(next), []);

  return { cards, moveCard, reset };
}
