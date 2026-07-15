import { makeStyles, tokens, Tab, TabList } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';

export type WorkspaceKey = 'main' | 'backstage' | 'home' | 'askAgent' | 'settings' | 'csa';

const useStyles = makeStyles({
  rail: {
    display: 'flex',
    flexDirection: 'column',
    width: '160px',
    backgroundColor: tokens.colorNeutralBackground2,
    borderRight: `1px solid ${tokens.colorNeutralStroke2}`,
    paddingTop: tokens.spacingVerticalM,
  },
});

interface AppRailProps {
  selected: WorkspaceKey;
  onSelect: (key: WorkspaceKey) => void;
}

/** Sprint 13 T1 — left app rail: Main / Backstage / Home / Ask-Agent / Settings. */
export function AppRail({ selected, onSelect }: AppRailProps) {
  const styles = useStyles();
  const { t } = useTranslation();
  return (
    <nav className={styles.rail} aria-label={t('rail.main')}>
      <TabList
        vertical
        selectedValue={selected}
        onTabSelect={(_e, data) => onSelect(data.value as WorkspaceKey)}
      >
        <Tab value="home">{t('rail.home')}</Tab>
        <Tab value="main">{t('rail.main')}</Tab>
        <Tab value="csa">{t('rail.csa')}</Tab>
        <Tab value="backstage">{t('rail.backstage')}</Tab>
        <Tab value="askAgent">{t('rail.askAgent')}</Tab>
        <Tab value="settings">{t('rail.settings')}</Tab>
      </TabList>
    </nav>
  );
}
