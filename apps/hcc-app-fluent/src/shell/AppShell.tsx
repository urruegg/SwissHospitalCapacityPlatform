import { Outlet } from 'react-router-dom';
import { makeStyles, tokens } from '@fluentui/react-components';
import { HeaderPlane } from './planes/HeaderPlane';
import { NavigationPlane } from './planes/NavigationPlane';
import { AgentPlane } from './planes/AgentPlane';
import { FooterPlane } from './planes/FooterPlane';

const useStyles = makeStyles({
  root: {
    display: 'grid',
    height: '100%',
    width: '100%',
    gridTemplateColumns: 'auto 1fr auto',
    gridTemplateRows: 'auto 1fr auto',
    gridTemplateAreas: `'header header header' 'nav main agent' 'footer footer footer'`,
    backgroundColor: tokens.colorNeutralBackground2,
  },
  header: { gridArea: 'header' },
  nav: { gridArea: 'nav' },
  main: { gridArea: 'main', overflow: 'auto', minWidth: 0 },
  agent: { gridArea: 'agent' },
  footer: { gridArea: 'footer' },
});

export function AppShell() {
  const s = useStyles();

  return (
    <div className={s.root}>
      <div className={s.header}>
        <HeaderPlane />
      </div>
      <div className={s.nav}>
        <NavigationPlane />
      </div>
      <main className={s.main}>
        <Outlet />
      </main>
      <div className={s.agent}>
        <AgentPlane />
      </div>
      <div className={s.footer}>
        <FooterPlane />
      </div>
    </div>
  );
}
