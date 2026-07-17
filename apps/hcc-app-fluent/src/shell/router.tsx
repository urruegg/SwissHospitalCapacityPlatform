import { Navigate, type RouteObject } from 'react-router-dom';
import { AppShell } from './AppShell';
import { StartView } from '../workspaces/start/StartView';
import { MainView } from '../workspaces/main/MainView';

const Stub = ({ id }: { id: string }) => <div data-testid={id} />;

/**
 * Sprint 20 M2 — five-plane route table.
 *
 * The surface elements are being replaced by the real Start / Main / CSA /
 * Backstage / Settings surfaces in M5. The router is mounted in `App.tsx`
 * (M4 cutover), once the legacy `TopBar`/`AppRail`/`WorkspaceRouter` shell was
 * removed.
 */
export const routes: RouteObject[] = [
  {
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="/start" replace /> },
      { path: 'start', element: <StartView /> },
      { path: 'main/:board?', element: <MainView /> },
      { path: 'csa', element: <Stub id="csa-view" /> },
      { path: 'backstage/:widget?', element: <Stub id="backstage-view" /> },
      { path: 'settings', element: <Stub id="settings-view" /> },
      { path: '*', element: <Navigate to="/start" replace /> },
    ],
  },
];
