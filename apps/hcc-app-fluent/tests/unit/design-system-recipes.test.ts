import { describe, expect, it } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useSurfaceStyles, useStateStyles } from '../../src/theme/design-system/recipes';

describe('design-system recipes', () => {
  it('surface recipe returns card + grid + header classes', () => {
    const { result } = renderHook(() => useSurfaceStyles());
    expect(result.current.surfaceCard).toBeTypeOf('string');
    expect(result.current.boardGrid).toBeTypeOf('string');
    expect(result.current.sectionHeader).toBeTypeOf('string');
    expect(result.current.statTile).toBeTypeOf('string');
    expect(result.current.provenanceBadge).toBeTypeOf('string');
  });

  it('state recipe returns empty/loading/error classes', () => {
    const { result } = renderHook(() => useStateStyles());
    expect(result.current.emptyState).toBeTypeOf('string');
    expect(result.current.loadingState).toBeTypeOf('string');
    expect(result.current.errorState).toBeTypeOf('string');
  });
});
