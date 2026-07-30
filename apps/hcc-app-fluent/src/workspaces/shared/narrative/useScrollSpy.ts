import { useEffect, useState } from 'react';

/**
 * Returns the id of the section currently in view. Falls back to the first id
 * when `IntersectionObserver` is unavailable (e.g. jsdom under test).
 */
export function useScrollSpy(ids: readonly string[], rootMargin = '-45% 0px -50% 0px'): string {
  const [active, setActive] = useState<string>(ids[0] ?? '');
  const key = ids.join('|');

  useEffect(() => {
    if (typeof IntersectionObserver === 'undefined' || typeof document === 'undefined') {
      return undefined;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((entry) => entry.isIntersecting);
        if (visible.length > 0) {
          setActive(visible[0].target.id);
        }
      },
      { rootMargin, threshold: 0 },
    );
    ids.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, rootMargin]);

  return active;
}
