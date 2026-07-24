import { TabList, Tab, makeStyles, tokens } from '@fluentui/react-components';
import {
  HomeRegular,
  GridRegular,
  DataTrendingRegular,
  SettingsRegular,
} from '@fluentui/react-icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useRoleLens } from '../../context/role-context';
import { space } from '../../theme/design-system';

const ITEMS = [
  { key: 'start', to: '/start', icon: <HomeRegular />, label: 'Start' },
  { key: 'main', to: '/main', icon: <GridRegular />, label: 'Main' },
  { key: 'backstage', to: '/backstage', icon: <DataTrendingRegular />, label: 'Backstage' },
  { key: 'settings', to: '/settings', icon: <SettingsRegular />, label: 'Settings' },
] as const;

const TOP = ITEMS.filter((i) => i.key !== 'settings');
const BOTTOM = ITEMS.filter((i) => i.key === 'settings');

const useStyles = makeStyles({
  nav: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    paddingTop: space.s,
    paddingBottom: space.s,
    backgroundColor: tokens.colorNeutralBackground1,
    borderRight: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  spacer: { flexGrow: 1 },
});

export function NavigationPlane() {
  const s = useStyles();
  const { capabilities } = useRoleLens();
  const nav = useNavigate();
  const loc = useLocation();
  const { t } = useTranslation();
  const selected = ITEMS.find((i) => loc.pathname.startsWith(i.to))?.key ?? 'start';
  const canNavigate = (key: string) => Boolean((capabilities.nav as Record<string, boolean>)[key]);
  const onSelect = (value: string) => {
    const it = ITEMS.find((i) => i.key === value);
    if (it && canNavigate(it.key)) nav(it.to);
  };

  return (
    <nav aria-label="Primary" className={s.nav}>
      <TabList vertical selectedValue={selected} onTabSelect={(_, d) => onSelect(d.value as string)}>
        {TOP.map((i) => (
          <Tab key={i.key} value={i.key} icon={i.icon} disabled={!canNavigate(i.key)}>
            {t(`nav.${i.key}`, i.label)}
          </Tab>
        ))}
      </TabList>
      <div className={s.spacer} />
      <TabList vertical selectedValue={selected} onTabSelect={(_, d) => onSelect(d.value as string)}>
        {BOTTOM.map((i) => (
          <Tab key={i.key} value={i.key} icon={i.icon} disabled={!canNavigate(i.key)}>
            {t(`nav.${i.key}`, i.label)}
          </Tab>
        ))}
      </TabList>
    </nav>
  );
}
