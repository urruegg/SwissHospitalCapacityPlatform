import type { JSX } from 'react';
import { useParams } from 'react-router-dom';
import { EvidenceTab } from './tabs/evidence/EvidenceTab';
import { RolesTab } from './tabs/roles/RolesTab';

/**
 * Sprint 20 M5 — Backstage surface.
 *
 * Routes the existing evidence / roles tabs as widgets behind
 * `/backstage/:widget?`, defaulting to the evidence widget. Each tab owns its
 * own whiteboard `Canvas` (evidence) or content, so BackstageView only selects
 * and mounts the widget.
 */
const WIDGETS: Record<string, () => JSX.Element> = {
  evidence: () => (
    <div data-testid="widget-evidence">
      <EvidenceTab />
    </div>
  ),
  roles: () => (
    <div data-testid="widget-roles">
      <RolesTab />
    </div>
  ),
};

export function BackstageView() {
  const { widget = 'evidence' } = useParams();
  const W = WIDGETS[widget] ?? WIDGETS.evidence;
  return <W />;
}
