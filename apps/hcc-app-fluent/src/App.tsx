import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import './i18n';
import { ThemeModeProvider } from './theme/theme-context';
import { ModeProvider } from './context/mode-context';
import { CopilotRailProvider } from './copilot-rail/rail-context';
import { HospitalProvider } from './context/hospital-context';
import { RoleProvider } from './context/role-context';
import { DataSourceProvider } from './context/data-source-context';
import { ContextEnvelopeSync } from './context/context-envelope-sync';
import { parseClaims, type ParsedClaims, type RawClaims } from './auth/claim-parser';
import { routes } from './shell/router';

const router = createBrowserRouter(routes);

/**
 * Sprint 20 — Curavias five-plane app root.
 *
 * The MSAL session injects `rawClaims` from `main.tsx`. When absent (anonymous
 * demo.guest shell / CI), the parser falls back to aggregated-only, dev env —
 * so no hospital-specific data is ever shown without a claim.
 *
 * The five-plane shell (Header / Navigation / Main / Agent / Footer) and its
 * routed surfaces live behind `RouterProvider`; the legacy AppRail / TopBar /
 * WorkspaceRouter shell was removed in the M4 cutover. `ThemeModeProvider` is
 * supplied here so the app is self-contained for both bootstrap and tests.
 */
export function App({ rawClaims }: { rawClaims?: RawClaims }) {
  const claims: ParsedClaims = parseClaims(rawClaims);

  return (
    <ThemeModeProvider>
      <ModeProvider>
        <CopilotRailProvider>
          <RoleProvider claims={claims}>
            <HospitalProvider claims={claims}>
              <DataSourceProvider>
                <ContextEnvelopeSync />
                <RouterProvider router={router} />
              </DataSourceProvider>
            </HospitalProvider>
          </RoleProvider>
        </CopilotRailProvider>
      </ModeProvider>
    </ThemeModeProvider>
  );
}

export default App;
