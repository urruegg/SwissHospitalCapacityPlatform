import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';
import type { ContextInsight } from '../journey/RoleBoard';
import type { GroundedReco } from './reco';
import type { DecisionOutcome } from '../data/iq-client';

/**
 * Sprint 39 P2 — a human accept/deny handler registered by the live board. The
 * board owns the network call (`iqDecision`) + the worklist re-fetch; the rail
 * only renders the outcome. `null` means no live decision surface (simulated /
 * host unconfigured), so the rail keeps the presentational single-CTA path.
 */
export type DecisionHandler = (decision: 'accept' | 'deny') => Promise<DecisionOutcome>;

export interface CopilotRailValue {
  open: boolean;
  activeContext: ContextInsight | null;
  activeReco: GroundedReco | null;
  defaultReco: GroundedReco | null;
  /** Live accept/deny handler registered by the board, or `null` when simulated. */
  onDecision: DecisionHandler | null;
  openWithContext: (insight: ContextInsight) => void;
  openWithReco: (insight: ContextInsight, reco: GroundedReco) => void;
  /**
   * Sprint 41 WS-FE — progressive-enhancement swap-in. Replaces `activeReco`
   * in place with a live-grounded reco once it resolves; a no-op if the rail
   * has since moved on (no reco active). Never touches `open`/`activeContext`.
   */
  updateActiveReco: (reco: GroundedReco) => void;
  showDefault: (reco: GroundedReco) => void;
  backToDefault: () => void;
  resetReco: () => void;
  setDecisionHandler: (handler: DecisionHandler | null) => void;
  setOpen: (open: boolean) => void;
  close: () => void;
}

const CopilotRailContext = createContext<CopilotRailValue | undefined>(undefined);

export function CopilotRailProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [activeContext, setActiveContext] = useState<ContextInsight | null>(null);
  const [activeReco, setActiveReco] = useState<GroundedReco | null>(null);
  const [defaultReco, setDefaultReco] = useState<GroundedReco | null>(null);
  const [onDecision, setOnDecision] = useState<DecisionHandler | null>(null);
  const resetReco = useCallback(() => {
    setActiveReco(null);
    setActiveContext(null);
    setDefaultReco(null);
    setOnDecision(null);
  }, []);
  // Store the handler in a functional setState wrapper so a function value is
  // registered (not invoked) as state.
  const setDecisionHandler = useCallback((handler: DecisionHandler | null) => {
    setOnDecision(() => handler);
  }, []);
  const value = useMemo<CopilotRailValue>(
    () => ({
      open,
      activeContext,
      activeReco,
      defaultReco,
      onDecision,
      openWithContext: (insight: ContextInsight) => {
        setActiveContext(insight);
        setOpen(true);
      },
      openWithReco: (insight: ContextInsight, reco: GroundedReco) => {
        setActiveContext(insight);
        setActiveReco(reco);
        setOpen(true);
      },
      updateActiveReco: (reco: GroundedReco) => {
        setActiveReco((current) => (current ? reco : current));
      },
      showDefault: (reco: GroundedReco) => {
        setDefaultReco(reco);
      },
      backToDefault: () => {
        setActiveReco(null);
        setActiveContext(null);
      },
      resetReco,
      setDecisionHandler,
      setOpen,
      close: () => setOpen(false),
    }),
    [open, activeContext, activeReco, defaultReco, onDecision, resetReco, setDecisionHandler],
  );
  return <CopilotRailContext.Provider value={value}>{children}</CopilotRailContext.Provider>;
}

export function useCopilotRail(): CopilotRailValue {
  const ctx = useContext(CopilotRailContext);
  if (!ctx) throw new Error('useCopilotRail must be used within a CopilotRailProvider');
  return ctx;
}
