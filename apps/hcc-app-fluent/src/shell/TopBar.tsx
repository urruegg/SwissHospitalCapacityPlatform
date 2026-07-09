import { makeStyles, tokens, Title3, Body1 } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { HospitalSelector } from './TopBar/HospitalSelector';
import { RoleSwitcher } from './TopBar/RoleSwitcher';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: '48px',
    paddingLeft: tokens.spacingHorizontalL,
    paddingRight: tokens.spacingHorizontalL,
    backgroundColor: tokens.colorBrandBackground,
    color: tokens.colorNeutralForegroundOnBrand,
  },
  brand: { color: tokens.colorNeutralForegroundOnBrand },
  right: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalM,
  },
});

/** Sprint 13 T1/T4 — top bar: brand, hospital selector, role switcher, user. */
export function TopBar() {
  const styles = useStyles();
  const { t } = useTranslation();
  return (
    <header className={styles.root} role="banner">
      <Title3 className={styles.brand}>{t('app.title')}</Title3>
      <div className={styles.right}>
        <HospitalSelector />
        <RoleSwitcher />
        <Body1 className={styles.brand} aria-label={t('topbar.search')}>
          {t('topbar.search')}
        </Body1>
      </div>
    </header>
  );
}
