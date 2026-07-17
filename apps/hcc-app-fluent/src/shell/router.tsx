import { Navigate, type RouteObject } from 'react-router-dom';
import { AppShell } from './AppShell';

const Stub = ({ id }: { id: string }) => <div data-testid={id} />;

/**
 * Sprint 20 M2 — five-plane route table.
 *
 * The surface elements are temporary stubs; M5 replaces them with the real
 * Start / Main / CSA / Backstage / Settings surfaces. The router is mounted in
 * `App.tsx` in M4, once the legacy `TopBar`/`AppRail`/`WorkspaceRouter` shell
 * is removed, so the suite stays green through M2-M3.
 */
export const routes: RouteObject[] = [
  {
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="/start" replace /> },
      { path: 'start', element: <Stub id="start-view" /> },
      { path: 'main/:board?', element: <Stub id="main-view" /> },
      { path: 'csa', element: <Stub id="csa-view" /> },
      { path: 'backstage/:widget?', element: <Stub id="backstage-view" /> },
      { path: 'settings', element: <Stub id="settings-view" /> },
      { path: '*', element: <Navigate to="/start" replace /> },
    ],
  },
];
