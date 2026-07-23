import {
  Badge,
  Body1,
  Card,
  makeStyles,
  MessageBar,
  MessageBarBody,
  Text,
  Title1,
  Title3,
  tokens,
} from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useMode } from '../../context/mode-context';
import { useRoleLens } from '../../context/role-context';
import { LAUNCHER_TILES } from './role-launcher';

const useStyles = makeStyles({
  root: {
    padding: tokens.spacingHorizontalXXL,
    display: 'grid',
    gap: tokens.spacingVerticalL,
    maxWidth: '860px',
  },
  launcher: {
    display: 'grid',
    gap: tokens.spacingVerticalM,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: tokens.spacingHorizontalM,
  },
  tileLink: {
    color: 'inherit',
    textDecorationLine: 'none',
  },
  tile: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingHorizontalM,
  },
  caption: {
    color: tokens.colorNeutralForeground3,
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
  const { mode } = useMode();
  const { capabilities } = useRoleLens();
  const visibleTiles = LAUNCHER_TILES.filter((tile) => !tile.requiresCsaNav || capabilities.nav.csa);

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
      <Badge appearance="filled" color={mode === 'demo' ? 'brand' : 'success'} data-testid="start-mode-badge">
        {mode === 'demo'
          ? t('start.mode.demo', 'Demo — simulated golden-thread showcase')
          : t('start.mode.user', 'User — live working mode')}
      </Badge>
      <div className={s.launcher}>
        <Title3 as="h2">{t('start.launcher.title', 'Enter a role board')}</Title3>
        <div className={s.grid}>
          {visibleTiles.map((tile) => (
            <Link
              key={tile.boardKey}
              className={s.tileLink}
              data-testid={`launch-${tile.boardKey}`}
              to={tile.route}
            >
              <Card className={s.tile} appearance="filled">
                <Text weight="semibold">{t(tile.labelKey)}</Text>
                <Text size={200} className={s.caption}>
                  {tile.agent} · {tile.ceiling}
                </Text>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
