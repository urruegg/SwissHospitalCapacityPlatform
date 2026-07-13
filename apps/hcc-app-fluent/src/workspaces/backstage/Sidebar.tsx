import { makeStyles, tokens, Tab, TabList } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';

export type BackstageTabKey = 'roles' | 'evidence';

const useStyles = makeStyles({
  sidebar: {
    display: 'flex',
    flexDirection: 'column',
    width: '200px',
    paddingRight: tokens.spacingHorizontalM,
    borderRight: `1px solid ${tokens.colorNeutralStroke2}`,
  },
});

interface SidebarProps {
  selected: BackstageTabKey;
  onSelect: (key: BackstageTabKey) => void;
}

/** Sprint 13 T4 — Backstage left sidebar. "Roles" (S13) + "Evidence" (S14.1 T6). */
export function Sidebar({ selected, onSelect }: SidebarProps) {
  const styles = useStyles();
  const { t } = useTranslation();
  return (
    <nav className={styles.sidebar} aria-label={t('rail.backstage')}>
      <TabList
        vertical
        selectedValue={selected}
        onTabSelect={(_e, data) => onSelect(data.value as BackstageTabKey)}
      >
        <Tab value="roles">{t('backstage.roles')}</Tab>
        <Tab value="evidence">{t('backstage.evidence')}</Tab>
      </TabList>
    </nav>
  );
}
