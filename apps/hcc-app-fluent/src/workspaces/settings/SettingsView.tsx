import { makeStyles, tokens, Title2, Card } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { ThemeToggle } from '../../shell/TopBar/ThemeToggle';
import { LanguageSelector } from '../../shell/TopBar/LanguageSelector';

/**
 * Sprint 20 M5 — Settings surface (app + user preferences).
 *
 * Reuses the header-plane theme and language controls so the preferences page
 * stays a single source of truth for those settings.
 */
const useStyles = makeStyles({
  root: {
    padding: tokens.spacingHorizontalXXL,
    display: 'grid',
    gap: tokens.spacingVerticalL,
    maxWidth: '640px',
  },
});

export function SettingsView() {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <section className={s.root} data-testid="settings-view">
      <Title2 as="h2">{t('settings.preferences', 'Preferences')}</Title2>
      <Card>
        <ThemeToggle />
      </Card>
      <Card>
        <LanguageSelector />
      </Card>
    </section>
  );
}
