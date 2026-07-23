import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import type { ContextInsight } from '../journey/RoleBoard';
import type { GroundedReco } from './reco';

interface CopilotRailValue {
  open: boolean;
  activeContext: ContextInsight | null;
  activeReco: GroundedReco | null;
  defaultReco: GroundedReco | null;
  openWithContext: (insight: ContextInsight) => void;
  openWithReco: (insight: ContextInsight, reco: GroundedReco) => void;
  showDefault: (reco: GroundedReco) => void;
  backToDefault: () => void;
  setOpen: (open: boolean) => void;
  close: () => void;
}

const CopilotRailContext = createContext<CopilotRailValue | undefined>(undefined);

export function CopilotRailProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [activeContext, setActiveContext] = useState<ContextInsight | null>(null);
  const [activeReco, setActiveReco] = useState<GroundedReco | null>(null);
  const [defaultReco, setDefaultReco] = useState<GroundedReco | null>(null);
  const value = useMemo<CopilotRailValue>(
    () => ({
      open,
      activeContext,
      activeReco,
      defaultReco,
      openWithContext: (insight: ContextInsight) => {
        setActiveContext(insight);
        setOpen(true);
      },
      openWithReco: (insight: ContextInsight, reco: GroundedReco) => {
        setActiveContext(insight);
        setActiveReco(reco);
        setOpen(true);
      },
      showDefault: (reco: GroundedReco) => {
        setDefaultReco(reco);
      },
      backToDefault: () => {
        setActiveReco(null);
        setActiveContext(null);
      },
      setOpen,
      close: () => setOpen(false),
    }),
    [open, activeContext, activeReco, defaultReco],
  );
  return <CopilotRailContext.Provider value={value}>{children}</CopilotRailContext.Provider>;
}

export function useCopilotRail(): CopilotRailValue {
  const ctx = useContext(CopilotRailContext);
  if (!ctx) throw new Error('useCopilotRail must be used within a CopilotRailProvider');
  return ctx;
}
