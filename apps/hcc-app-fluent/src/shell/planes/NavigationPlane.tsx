import { TabList, Tab } from '@fluentui/react-components';
import {
  HomeRegular,
  GridRegular,
  DataTrendingRegular,
  SettingsRegular,
} from '@fluentui/react-icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useRoleLens } from '../../context/role-context';

const ITEMS = [
  { key: 'start', to: '/start', icon: <HomeRegular />, label: 'Start' },
  { key: 'main', to: '/main', icon: <GridRegular />, label: 'Main' },
  { key: 'backstage', to: '/backstage', icon: <DataTrendingRegular />, label: 'Backstage' },
  { key: 'settings', to: '/settings', icon: <SettingsRegular />, label: 'Settings' },
] as const;

export function NavigationPlane() {
  const { capabilities } = useRoleLens();
  const nav = useNavigate();
  const loc = useLocation();
  const { t } = useTranslation();
  const selected = ITEMS.find((i) => loc.pathname.startsWith(i.to))?.key ?? 'start';
  const canNavigate = (key: string) => Boolean((capabilities.nav as Record<string, boolean>)[key]);

  return (
    <nav aria-label="Primary">
      <TabList
        vertical
        selectedValue={selected}
        onTabSelect={(_, d) => {
          const it = ITEMS.find((i) => i.key === d.value);
          if (it && canNavigate(it.key)) nav(it.to);
        }}
      >
        {ITEMS.map((i) => (
          <Tab key={i.key} value={i.key} icon={i.icon} disabled={!canNavigate(i.key)}>
            {t(`nav.${i.key}`, i.label)}
          </Tab>
        ))}
      </TabList>
    </nav>
  );
}
