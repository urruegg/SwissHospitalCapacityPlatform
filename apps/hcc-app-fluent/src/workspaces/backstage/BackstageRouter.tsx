import { useState } from 'react';
import { makeStyles, tokens } from '@fluentui/react-components';
import { Sidebar, type BackstageTabKey } from './Sidebar';
import { RolesTab } from './tabs/roles/RolesTab';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    gap: tokens.spacingHorizontalL,
  },
  content: { flexGrow: 1 },
});

/** Sprint 13 T4 — Backstage workspace router (Roles tab only in Sprint 13). */
export function BackstageRouter() {
  const styles = useStyles();
  const [tab, setTab] = useState<BackstageTabKey>('roles');
  return (
    <div className={styles.root}>
      <Sidebar selected={tab} onSelect={setTab} />
      <div className={styles.content}>{tab === 'roles' && <RolesTab />}</div>
    </div>
  );
}
