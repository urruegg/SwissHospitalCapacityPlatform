import { useState } from 'react';
import {
  FluentProvider,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { helvionLightTheme } from './theme/helvion-theme';
import { TopBar } from './shell/TopBar';
import { AppRail, type WorkspaceKey } from './shell/AppRail';
import { WorkspaceRouter } from './shell/WorkspaceRouter';
import { HospitalProvider } from './context/hospital-context';
import { RoleProvider } from './context/role-context';
import { parseClaims, type ParsedClaims, type RawClaims } from './auth/claim-parser';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    backgroundColor: tokens.colorNeutralBackground1,
  },
  body: { display: 'flex', flexGrow: 1, minHeight: 0 },
});

/**
 * Sprint 13 — Fluent baseline app root.
 *
 * `rawClaims` are injected from the MSAL session in `main.tsx`. When absent
 * (anonymous demo.guest shell / CI), the parser falls back to aggregated-only,
 * dev env — so no hospital-specific data is ever shown without a claim.
 */
export function App({ rawClaims }: { rawClaims?: RawClaims }) {
  const styles = useStyles();
  const [workspace, setWorkspace] = useState<WorkspaceKey>('home');
  const claims: ParsedClaims = parseClaims(rawClaims);

  return (
    <FluentProvider theme={helvionLightTheme}>
      <RoleProvider claims={claims}>
        <HospitalProvider claims={claims}>
          <div className={styles.root}>
            <TopBar />
            <div className={styles.body}>
              <AppRail selected={workspace} onSelect={setWorkspace} />
              <WorkspaceRouter selected={workspace} />
            </div>
          </div>
        </HospitalProvider>
      </RoleProvider>
    </FluentProvider>
  );
}

export default App;
