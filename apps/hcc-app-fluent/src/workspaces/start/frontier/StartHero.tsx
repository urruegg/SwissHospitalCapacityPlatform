import {
  Badge,
  Body1,
  Caption1,
  Text,
  Title1,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';
import { bvaHeadlineKpis, type BvaHeadlineKpiPayload } from '../../../data/bva/bva-evidence';
import { loadSiteCapacitySummary } from '../../../data/roleboard/golden-source-client';
import type { SiteCapacitySummary } from '../../../data/roleboard/occupancy-data';
import { GOLDEN_THREAD_SCOPE } from '../../../journey/golden-thread';
import type { Mode, Provenance } from '../../../journey/RoleBoard';
import { useStateStyles, useSurfaceStyles } from '../../../theme/design-system/recipes';

interface StartHeroProps {
  mode: Mode;
}

interface HeroMetric {
  id: string;
  label: string;
  value: string;
  note?: string;
  provenance: BvaHeadlineKpiPayload;
}

interface StartHeroEvidenceSelection {
  netValueRealized: BvaHeadlineKpiPayload;
  roi: BvaHeadlineKpiPayload & { targetLabel: string };
}

type CapacityState =
  | { status: 'loading' }
  | { status: 'ready'; summary: SiteCapacitySummary }
  | { status: 'error'; error: Error };

const useStyles = makeStyles({
  root: {
    display: 'grid',
    gap: tokens.spacingVerticalL,
    gridTemplateColumns: 'minmax(0, 1.35fr) minmax(280px, 1fr)',
    '@media (max-width: 900px)': {
      gridTemplateColumns: '1fr',
    },
  },
  heroColumn: {
    display: 'grid',
    gap: tokens.spacingVerticalM,
    alignContent: 'start',
  },
  eyebrow: {
    // Fluent's link-foreground token is intentional for non-link text: it preserves WCAG contrast in both themes.
    color: tokens.colorBrandForegroundLink,
    letterSpacing: '0.04em',
    textTransform: 'uppercase',
  },
  hook: {
    maxWidth: '16ch',
  },
  valueLine: {
    color: tokens.colorNeutralForeground2,
  },
  trustPills: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalXS,
  },
  metrics: {
    display: 'grid',
    gap: tokens.spacingHorizontalM,
    gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
  },
  metricTile: {
    display: 'grid',
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusLarge,
    backgroundColor: tokens.colorNeutralBackground2,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    minHeight: '156px',
    alignContent: 'start',
  },
  metricValue: {
    color: tokens.colorBrandForeground1,
    overflowWrap: 'anywhere',
  },
  metricCaption: {
    color: tokens.colorNeutralForeground3,
  },
  ctas: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
    alignItems: 'center',
  },
  ctaLink: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '40px',
    padding: `${tokens.spacingVerticalXS} ${tokens.spacingHorizontalM}`,
    borderRadius: tokens.borderRadiusMedium,
    fontWeight: tokens.fontWeightSemibold,
    textDecorationLine: 'none',
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: tokens.strokeWidthThick,
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '2px',
    },
  },
  ctaPrimary: {
    backgroundColor: tokens.colorBrandBackground,
    color: tokens.colorNeutralForegroundOnBrand,
  },
  ctaSecondary: {
    border: `1px solid ${tokens.colorNeutralStroke1}`,
    color: tokens.colorBrandForegroundLink,
  },
  disclaimer: {
    color: tokens.colorNeutralForeground3,
    display: 'block',
  },
  squeezeCard: {
    display: 'grid',
    gap: tokens.spacingVerticalM,
    padding: tokens.spacingHorizontalL,
    borderRadius: tokens.borderRadiusXLarge,
    background: `linear-gradient(135deg, ${tokens.colorBrandBackground2} 0%, ${tokens.colorNeutralBackground1} 62%)`,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    alignContent: 'start',
  },
  squeezeHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: tokens.spacingHorizontalS,
    flexWrap: 'wrap',
  },
  squeezeBig: {
    display: 'grid',
    gap: tokens.spacingVerticalXXS,
  },
  squeezePeak: {
    color: tokens.colorPaletteRedForeground1,
  },
  squeezeMeta: {
    display: 'grid',
    gap: tokens.spacingVerticalXXS,
  },
});

function metricDisplay(payload: BvaHeadlineKpiPayload): string {
  return payload.unit ? `${payload.value} ${payload.unit}` : payload.value;
}

function invariant(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

function selectHeroEvidence(kpis: readonly BvaHeadlineKpiPayload[]): StartHeroEvidenceSelection {
  const netValueRealized = kpis.find((payload) => payload.measure === 'Net Value Realized (3yr)');
  const roi = kpis.find((payload) => payload.measure === 'ROI %');

  invariant(
    netValueRealized,
    'StartHero requires the "Net Value Realized (3yr)" headline KPI to render the hero tiles.',
  );
  invariant(roi, 'StartHero requires the "ROI %" headline KPI to render the hero tiles.');
  invariant(
    roi.targetLabel,
    'StartHero requires the "ROI %" headline KPI targetLabel to render the third hero tile.',
  );

  return { netValueRealized, roi: { ...roi, targetLabel: roi.targetLabel } };
}

function metricTiles(t: (key: string, options?: Record<string, string | number>) => string): HeroMetric[] {
  const { netValueRealized, roi } = selectHeroEvidence(bvaHeadlineKpis);
  const tiles: HeroMetric[] = [
    {
      id: 'headline-net-value-realized',
      label: netValueRealized.measure,
      value: metricDisplay(netValueRealized),
      note: netValueRealized.targetLabel,
      provenance: netValueRealized,
    },
    {
      id: 'headline-roi',
      label: roi.measure,
      value: metricDisplay(roi),
      provenance: roi,
    },
    {
      id: 'headline-rom-context',
      label: t('start.frontier.hero.supportingMetricLabel'),
      value: roi.targetLabel,
      provenance: roi,
    },
  ];

  const figures = tiles.map((tile) => tile.value);
  invariant(figures.length === 3, 'StartHero must render exactly three hero metric figures.');
  invariant(
    new Set(figures).size === figures.length,
    'StartHero hero metric figures must remain distinct.',
  );
  invariant(
    !tiles.some((tile) => tile.note && figures.includes(tile.note)),
    'StartHero hero metric notes must not duplicate another displayed figure.',
  );

  return tiles;
}

function formatAsOf(asOf: string): string {
  return `${new Date(asOf).toISOString().slice(0, 16).replace('T', ' ')}Z`;
}

function provenanceLabel(t: (key: string) => string, provenance: Provenance): string {
  return provenance === 'live' ? t('badge.liveData') : t('badge.simulatedData');
}

export function StartHero({ mode }: StartHeroProps) {
  const styles = useStyles();
  const surface = useSurfaceStyles();
  const stateStyles = useStateStyles();
  const { t } = useTranslation();
  const [capacityState, setCapacityState] = useState<CapacityState>({ status: 'loading' });

  const scope = useMemo(
    () => (mode === 'demo' ? GOLDEN_THREAD_SCOPE : { ...GOLDEN_THREAD_SCOPE, pinned: false }),
    [mode],
  );
  const metrics = useMemo(() => metricTiles(t), [t]);

  useEffect(() => {
    let cancelled = false;
    setCapacityState({ status: 'loading' });
    loadSiteCapacitySummary(scope, mode)
      .then((summary) => {
        if (!cancelled) setCapacityState({ status: 'ready', summary });
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setCapacityState({
            status: 'error',
            error: error instanceof Error ? error : new Error(String(error)),
          });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [mode, scope]);

  return (
    <div className={styles.root}>
      <div className={styles.heroColumn}>
        <div className={styles.heroColumn}>
          <Caption1 className={styles.eyebrow}>{t('start.frontier.hero.eyebrow')}</Caption1>
          <Title1 as="h2" className={styles.hook}>
            {t('start.frontier.hero.hook')}
          </Title1>
          <Body1>{t('start.mission')}</Body1>
          <Text className={styles.valueLine}>{t('start.frontier.hero.valueLine')}</Text>
        </div>

        <div className={styles.trustPills}>
          <Badge appearance="filled" color="brand">
            {t('backstage.story.fabricFhir.title')}
          </Badge>
          <Badge appearance="tint" color="informative">
            {t('start.frontier.guardrails.advisory')}
          </Badge>
          <Badge appearance="tint" color="warning">
            {t('start.frontier.guardrails.noPhi')}
          </Badge>
        </div>

        <div className={styles.metrics}>
          {metrics.map((metric) => (
            <div key={metric.id} className={styles.metricTile} data-testid="hero-metric-tile">
              <Text weight="semibold">{metric.label}</Text>
              <Title1 as="span" className={styles.metricValue} data-testid="hero-metric-figure">
                {metric.value}
              </Title1>
              {metric.note ? <Body1>{metric.note}</Body1> : null}
              <Caption1 className={styles.metricCaption} data-testid="hero-metric-caption">
                {t('start.valueTiles.romLabel')} · {metric.provenance.source} ·{' '}
                {t('start.capacityTeaser.asOf', { time: metric.provenance.asOf.slice(0, 10) })}
              </Caption1>
            </div>
          ))}
        </div>

        <div className={styles.ctas}>
          <RouterLink
            to="/backstage"
            className={mergeClasses(styles.ctaLink, styles.ctaPrimary)}
          >
            {t('start.frontier.hero.ctaPrimary')}
          </RouterLink>
          <RouterLink
            to="/backstage"
            className={mergeClasses(styles.ctaLink, styles.ctaSecondary)}
          >
            {t('start.frontier.hero.ctaSecondary')}
          </RouterLink>
        </div>

        <Caption1 className={styles.disclaimer}>
          {t('start.frontier.guardrails.synthetic')} {t('start.frontier.guardrails.advisory')}
        </Caption1>
      </div>

      <aside className={mergeClasses(surface.surfaceCard, styles.squeezeCard)} aria-live="polite">
        <div className={styles.squeezeHeader}>
          <Caption1>{t('start.frontier.hero.capacityTitle')}</Caption1>
          {capacityState.status === 'ready' ? (
            <Badge
              appearance="tint"
              color={capacityState.summary.provenance === 'live' ? 'success' : 'warning'}
            >
              {provenanceLabel(t, capacityState.summary.provenance)}
            </Badge>
          ) : null}
        </div>

        {capacityState.status === 'loading' ? (
          <div className={stateStyles.loadingState}>
            <Text>{t('start.frontier.hero.capacityLoading')}</Text>
          </div>
        ) : null}

        {capacityState.status === 'error' ? (
          <div className={stateStyles.errorState}>
            <Text weight="semibold">{t('start.frontier.hero.capacityErrorTitle')}</Text>
            <Body1>{capacityState.error.message}</Body1>
          </div>
        ) : null}

        {capacityState.status === 'ready' ? (
          <>
            <div className={styles.squeezeBig}>
              <Text>{t('start.capacityTeaser.peakWard', { ward: capacityState.summary.peakWard, pct: capacityState.summary.peakPct })}</Text>
              <Title1 as="span" className={styles.squeezePeak}>
                {capacityState.summary.peakPct}%
              </Title1>
            </div>
            <Body1>
              {capacityState.summary.siteGapBeds < 0
                ? t('start.capacityTeaser.siteGapDeficit', { beds: Math.abs(capacityState.summary.siteGapBeds) })
                : t('start.capacityTeaser.siteGapSurplus', { beds: capacityState.summary.siteGapBeds })}
            </Body1>
            <div className={styles.squeezeMeta}>
              <Caption1>{t('start.capacityTeaser.breachEta', { hours: capacityState.summary.breachEtaHours })}</Caption1>
              <Caption1>{t('start.capacityTeaser.firstSurfacedBy', { agent: capacityState.summary.firstSurfacedBy })}</Caption1>
              <Caption1>{t('start.capacityTeaser.asOf', { time: formatAsOf(capacityState.summary.asOf) })}</Caption1>
            </div>
          </>
        ) : null}
      </aside>
    </div>
  );
}
