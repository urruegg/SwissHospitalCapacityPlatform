import { useState } from 'react';
import { makeStyles, tokens } from '@fluentui/react-components';
import { Sidebar, type BackstageTabKey } from './Sidebar';
import { RolesTab } from './tabs/roles/RolesTab';
import { EvidenceTab } from './tabs/evidence/EvidenceTab';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    gap: tokens.spacingHorizontalL,
  },
  content: { flexGrow: 1 },
});

/** Sprint 13 T4 — Backstage workspace router (Roles + S14.1 Evidence tabs). */
export function BackstageRouter() {
  const styles = useStyles();
  const [tab, setTab] = useState<BackstageTabKey>('roles');
  return (
    <div className={styles.root}>
      <Sidebar selected={tab} onSelect={setTab} />
      <div className={styles.content}>
        {tab === 'roles' && <RolesTab />}
        {tab === 'evidence' && <EvidenceTab />}
      </div>
    </div>
  );
}
