import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import type { ContextInsight } from '../journey/RoleBoard';

interface CopilotRailValue {
  open: boolean;
  activeContext: ContextInsight | null;
  openWithContext: (insight: ContextInsight) => void;
  setOpen: (open: boolean) => void;
  close: () => void;
}

const CopilotRailContext = createContext<CopilotRailValue | undefined>(undefined);

export function CopilotRailProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [activeContext, setActiveContext] = useState<ContextInsight | null>(null);
  const value = useMemo<CopilotRailValue>(
    () => ({
      open,
      activeContext,
      openWithContext: (insight: ContextInsight) => {
        setActiveContext(insight);
        setOpen(true);
      },
      setOpen,
      close: () => setOpen(false),
    }),
    [open, activeContext],
  );
  return <CopilotRailContext.Provider value={value}>{children}</CopilotRailContext.Provider>;
}

export function useCopilotRail(): CopilotRailValue {
  const ctx = useContext(CopilotRailContext);
  if (!ctx) throw new Error('useCopilotRail must be used within a CopilotRailProvider');
  return ctx;
}
