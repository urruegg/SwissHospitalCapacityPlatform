/**
 * Sprint 1 (parity) — maps the active MAIN board route to the role agent that
 * backs the Agent plane by default. BACKSTAGE is backed by the Product Owner
 * agent (Sprint 28 WS-X); remaining non-board surfaces fall through to the
 * orchestrator so every surface still has an agent.
 */
const BOARD_AGENTS: Record<string, string> = {
  occupancy: 'ooa-agent',
  discharge: 'dca-agent',
  'bed-manager': 'bmca-agent',
  'or-steering': 'orsa-agent',
  staffing: 'sba-agent',
  crisis: 'csa-agent',
};

export function agentForRoute(pathname: string): string {
  const board = pathname.match(/^\/main\/([^/]+)/)?.[1];
  if (board && BOARD_AGENTS[board]) return BOARD_AGENTS[board];
  if (pathname === '/start' || pathname.startsWith('/start/')) return 'product-owner-agent';
  if (pathname.startsWith('/backstage')) return 'product-owner-agent';
  return 'orchestrator';
}
