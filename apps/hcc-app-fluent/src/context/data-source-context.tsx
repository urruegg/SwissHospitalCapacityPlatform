import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';
import { getPreferredSource, setPreferredSource, type DataSourceMode } from '../data/data-source';
import { isGoldenSourceConfigured } from '../data/iq-client';

/**
 * Sprint 27 — data-source context. Backs the header toggle that switches board
 * data between live golden evidence (IQ layer) and simulated fixtures. Keeps the
 * pure data layer (`data/data-source`) in sync so `golden-source-client` reads
 * the preference without threading a param through the frozen RoleBoard contract.
 */
interface DataSourceValue {
  source: DataSourceMode;
  /** True when a golden source is configured (so `live` can serve real data). */
  liveConfigured: boolean;
  setSource: (mode: DataSourceMode) => void;
}

const DataSourceContext = createContext<DataSourceValue | undefined>(undefined);

export function DataSourceProvider({ children }: { children: ReactNode }) {
  const [source, setSourceState] = useState<DataSourceMode>(() => getPreferredSource());
  const setSource = useCallback((mode: DataSourceMode) => {
    setPreferredSource(mode); // keep the pure data layer in sync
    setSourceState(mode);
  }, []);
  const value = useMemo<DataSourceValue>(
    () => ({ source, liveConfigured: isGoldenSourceConfigured(), setSource }),
    [source, setSource],
  );
  return <DataSourceContext.Provider value={value}>{children}</DataSourceContext.Provider>;
}

/** Data-source preference; degrades to the module default when no provider (tests). */
export function useDataSource(): DataSourceValue {
  return (
    useContext(DataSourceContext) ?? {
      source: getPreferredSource(),
      liveConfigured: isGoldenSourceConfigured(),
      setSource: setPreferredSource,
    }
  );
}
