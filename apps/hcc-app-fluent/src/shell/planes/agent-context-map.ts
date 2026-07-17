/**
 * Sprint 20 M7 — maps the active route to the agent that should back the
 * Agent plane by default. Falls through to the orchestrator so every surface
 * (Start, Settings, and anything unmapped) still has an agent.
 */
export function agentForRoute(pathname: string): string {
  if (pathname.startsWith('/main')) return 'bmca-agent';
  if (pathname.startsWith('/csa')) return 'csa-agent';
  if (pathname.startsWith('/backstage')) return 'knowledge-agent';
  return 'orchestrator';
}
