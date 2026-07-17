import { renderHook } from '@testing-library/react';
import { vi } from 'vitest';
import { useContentRefresh } from '../../src/shell/useContentRefresh';

describe('useContentRefresh', () => {
  it('invokes the callback when any of role/hospital/route changes', () => {
    const cb = vi.fn();
    const { rerender } = renderHook(
      ({ deps }) => useContentRefresh(deps, cb),
      { initialProps: { deps: ['HCC.Viewer', 'usz', '/main'] } },
    );
    expect(cb).toHaveBeenCalledTimes(1);
    rerender({ deps: ['HCC.Viewer', 'luks', '/main'] });
    expect(cb).toHaveBeenCalledTimes(2);
  });

  it('does not invoke the callback when dependencies are unchanged', () => {
    const cb = vi.fn();
    const { rerender } = renderHook(
      ({ deps }) => useContentRefresh(deps, cb),
      { initialProps: { deps: ['HCC.Viewer', 'usz', '/main'] } },
    );
    expect(cb).toHaveBeenCalledTimes(1);
    rerender({ deps: ['HCC.Viewer', 'usz', '/main'] });
    expect(cb).toHaveBeenCalledTimes(1);
  });
});
