import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';

export type Mode = 'demo' | 'user';
const STORAGE_KEY = 'hcc.mode';

interface ModeContextValue {
  mode: Mode;
  setMode: (m: Mode) => void;
}

const ModeContext = createContext<ModeContextValue | undefined>(undefined);

function readInitial(): Mode {
  const stored = typeof localStorage !== 'undefined' ? localStorage.getItem(STORAGE_KEY) : null;
  return stored === 'user' ? 'user' : 'demo';
}

export function ModeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<Mode>(readInitial);
  const value = useMemo<ModeContextValue>(
    () => ({
      mode,
      setMode: (m: Mode) => {
        setModeState(m);
        try {
          localStorage.setItem(STORAGE_KEY, m);
        } catch {
          /* storage unavailable — in-memory only */
        }
      },
    }),
    [mode],
  );
  return <ModeContext.Provider value={value}>{children}</ModeContext.Provider>;
}

export function useMode(): ModeContextValue {
  const ctx = useContext(ModeContext);
  const [fallbackMode, setFallbackMode] = useState<Mode>(readInitial);
  const fallback = useMemo<ModeContextValue>(
    () => ({
      mode: fallbackMode,
      setMode: (m: Mode) => {
        setFallbackMode(m);
        try {
          localStorage.setItem(STORAGE_KEY, m);
        } catch {
          /* storage unavailable — in-memory only */
        }
      },
    }),
    [fallbackMode],
  );
  return ctx ?? fallback;
}
