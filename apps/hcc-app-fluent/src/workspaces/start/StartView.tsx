import { makeStyles, tokens, Title1, Body1, MessageBar, MessageBarBody } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';

const useStyles = makeStyles({
  root: {
    padding: tokens.spacingHorizontalXXL,
    display: 'grid',
    gap: tokens.spacingVerticalL,
    maxWidth: '860px',
  },
});

/**
 * Sprint 20 M5 — Start surface.
 *
 * Vision/mission landing with the mandatory Microsoft Innovation Hub Showcase
 * disclaimer (simulated, generic data — demo only) per design spec §2.1. Copy
 * is driven through i18n keys with inline English defaults; DE/FR/IT strings
 * land in M6 (four-language i18n).
 */
export function StartView() {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <section className={s.root} data-testid="start-view">
      <Title1 as="h1">{t('start.title', 'Curavias')}</Title1>
      <Body1>
        {t('start.mission', 'Coordinating hospital capacity across the Swiss care network.')}
      </Body1>
      <MessageBar intent="info">
        <MessageBarBody>
          {t(
            'start.disclaimer',
            'Microsoft Innovation Hub Showcase — pure simulated and generic data for demo purposes only.',
          )}
        </MessageBarBody>
      </MessageBar>
    </section>
  );
}
