import { TabList, Tab, makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import {
  HomeRegular,
  GridRegular,
  DataTrendingRegular,
  SettingsRegular,
} from '@fluentui/react-icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useRoleLens } from '../../context/role-context';
import { useMode } from '../../context/mode-context';
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
    width: '232px',
    boxSizing: 'border-box',
    paddingTop: space.m,
    paddingBottom: space.m,
    paddingLeft: space.s,
    paddingRight: space.s,
    rowGap: space.m,
    backgroundColor: tokens.colorNeutralBackground1,
    borderRight: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  modeSwitch: {
    display: 'flex',
    columnGap: '2px',
    padding: '2px',
    borderRadius: tokens.borderRadiusLarge,
    backgroundColor: tokens.colorNeutralBackground3,
  },
  modeBtn: {
    flexGrow: 1,
    border: 'none',
    cursor: 'pointer',
    paddingTop: space.xs,
    paddingBottom: space.xs,
    borderRadius: tokens.borderRadiusMedium,
    backgroundColor: 'transparent',
    color: tokens.colorNeutralForeground2,
    font: 'inherit',
    fontWeight: tokens.fontWeightSemibold,
  },
  modeBtnActive: {
    backgroundColor: tokens.colorNeutralBackground1,
    color: tokens.colorNeutralForeground1,
    boxShadow: tokens.shadow2,
  },
  tab: {
    width: '100%',
    justifyContent: 'flex-start',
    borderRadius: tokens.borderRadiusMedium,
    ':hover': { backgroundColor: tokens.colorNeutralBackground1Hover },
  },
  tabSelected: {
    backgroundColor: tokens.colorBrandBackground2,
    ':hover': { backgroundColor: tokens.colorBrandBackground2Hover },
  },
  spacer: { flexGrow: 1 },
});

export function NavigationPlane() {
  const s = useStyles();
  const { capabilities } = useRoleLens();
  const { mode, setMode } = useMode();
  const nav = useNavigate();
  const loc = useLocation();
  const { t } = useTranslation();
  const selected = ITEMS.find((i) => loc.pathname.startsWith(i.to))?.key ?? 'start';
  const canNavigate = (key: string) => Boolean((capabilities.nav as Record<string, boolean>)[key]);
  const onSelect = (value: string) => {
    const it = ITEMS.find((i) => i.key === value);
    if (it && canNavigate(it.key)) nav(it.to);
  };
  const tabClass = (key: string) => mergeClasses(s.tab, selected === key && s.tabSelected);

  return (
    <nav aria-label="Primary" className={s.nav}>
      <div className={s.modeSwitch} role="group" aria-label={t('mode.toggle', 'Demo / User mode')}>
        <button
          type="button"
          className={mergeClasses(s.modeBtn, mode === 'demo' && s.modeBtnActive)}
          aria-pressed={mode === 'demo'}
          onClick={() => setMode('demo')}
        >
          {t('mode.demo', 'Demo')}
        </button>
        <button
          type="button"
          className={mergeClasses(s.modeBtn, mode === 'user' && s.modeBtnActive)}
          aria-pressed={mode === 'user'}
          onClick={() => setMode('user')}
        >
          {t('mode.user', 'User')}
        </button>
      </div>

      <TabList vertical selectedValue={selected} onTabSelect={(_, d) => onSelect(d.value as string)}>
        {TOP.map((i) => (
          <Tab key={i.key} className={tabClass(i.key)} value={i.key} icon={i.icon} disabled={!canNavigate(i.key)}>
            {t(`nav.${i.key}`, i.label)}
          </Tab>
        ))}
      </TabList>
      <div className={s.spacer} />
      <TabList vertical selectedValue={selected} onTabSelect={(_, d) => onSelect(d.value as string)}>
        {BOTTOM.map((i) => (
          <Tab key={i.key} className={tabClass(i.key)} value={i.key} icon={i.icon} disabled={!canNavigate(i.key)}>
            {t(`nav.${i.key}`, i.label)}
          </Tab>
        ))}
      </TabList>
    </nav>
  );
}
