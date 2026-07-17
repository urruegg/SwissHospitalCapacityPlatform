import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import { FluentProvider } from '@fluentui/react-components';
import { curaviasLightTheme, curaviasDarkTheme } from './curavias-theme';

type Mode = 'light' | 'dark';
const KEY = 'curavias.theme';
const Ctx = createContext<{ mode: Mode; toggle: () => void }>({ mode: 'light', toggle: () => {} });

export function ThemeModeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<Mode>(() => (localStorage.getItem(KEY) as Mode) ?? 'light');
  const value = useMemo(
    () => ({
      mode,
      toggle: () =>
        setMode((m) => {
          const next = m === 'light' ? 'dark' : 'light';
          localStorage.setItem(KEY, next);
          return next;
        }),
    }),
    [mode],
  );
  const theme = mode === 'dark' ? curaviasDarkTheme : curaviasLightTheme;
  return (
    <Ctx.Provider value={value}>
      <FluentProvider theme={theme}>{children}</FluentProvider>
    </Ctx.Provider>
  );
}

export const useThemeMode = () => useContext(Ctx);
