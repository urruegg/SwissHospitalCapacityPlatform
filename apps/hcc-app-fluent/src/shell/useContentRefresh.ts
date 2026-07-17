import { useEffect } from 'react';

/**
 * Sprint 20 M5 Task 5.6 — refresh content when role/hospital/route changes.
 *
 * Thin `useEffect` over a dependency tuple: any change in the supplied
 * dependency array (typically `[role, hospital, route]`) re-runs `onRefresh`,
 * so surfaces re-fetch when the active lens changes.
 */
export function useContentRefresh(
  deps: ReadonlyArray<string>,
  onRefresh: () => void,
) {
  useEffect(() => {
    onRefresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}
