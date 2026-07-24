import { Fragment, useEffect, useState } from 'react';
import {
  Badge,
  Body1,
  Caption1,
  Card,
  makeStyles,
  MessageBar,
  MessageBarBody,
  Text,
  Title1,
  Title3,
  tokens,
} from '@fluentui/react-components';
import { ArrowRightRegular } from '@fluentui/react-icons';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useMode } from '../../context/mode-context';
import { useRoleLens } from '../../context/role-context';
import { LAUNCHER_TILES } from './role-launcher';
import { loadSiteCapacitySummary } from '../../data/roleboard/golden-source-client';
import type { SiteCapacitySummary } from '../../data/roleboard/occupancy-data';
import { bvaHeadlineKpis } from '../../data/bva/bva-evidence';
import { GOLDEN_THREAD_SCOPE } from '../../journey/golden-thread';
import type { ScenarioScope } from '../../journey/RoleBoard';

const WHY_NOW_ROWS = ['row1', 'row2', 'row3', 'row4', 'row5', 'row6'] as const;

const PATIENT_PATH_STEPS = [
  { key: 'admission', agent: 'ooa-agent', showCapacity: false },
  { key: 'triage', agent: 'bmca-agent', showCapacity: false },
  { key: 'treatment', agent: 'ooa-agent', showCapacity: true },
  { key: 'discharge', agent: 'dca-agent', showCapacity: false },
  { key: 'postAcute', agent: 'sba-agent', showCapacity: false },
] as const;

const useStyles = makeStyles({
  root: {
    padding: tokens.spacingHorizontalXXL,
    display: 'grid',
    gap: tokens.spacingVerticalL,
    maxWidth: '860px',
  },
  section: {
    display: 'grid',
    gap: tokens.spacingVerticalS,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: tokens.spacingHorizontalM,
  },
  tile: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingHorizontalM,
  },
  teaserRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalL,
    alignItems: 'flex-start',
  },
  teaserStat: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXXS,
  },
  caption: {
    color: tokens.colorNeutralForeground3,
  },
  tableCellHeader: {
    paddingTop: tokens.spacingVerticalXS,
    paddingBottom: tokens.spacingVerticalXS,
    paddingLeft: tokens.spacingHorizontalS,
    paddingRight: tokens.spacingHorizontalS,
    textAlign: 'left' as const,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground2,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  tableCell: {
    paddingTop: tokens.spacingVerticalXS,
    paddingBottom: tokens.spacingVerticalXS,
    paddingLeft: tokens.spacingHorizontalS,
    paddingRight: tokens.spacingHorizontalS,
    textAlign: 'left' as const,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  pathStrip: {
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
  },
  pathNode: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXXS,
    padding: tokens.spacingHorizontalM,
    minWidth: '100px',
  },
  arrow: {
    color: tokens.colorNeutralForeground3,
    flexShrink: 0,
  },
  launcher: {
    display: 'grid',
    gap: tokens.spacingVerticalM,
  },
  tileLink: {
    color: 'inherit',
    textDecorationLine: 'none',
  },
});

/**
 * Sprint 20 M5 — Start surface.
 *
 * Composes: hero + disclaimer + mode badge (existing) + live capacity teaser
 * (OOA golden source via loadSiteCapacitySummary) + value/ROI tiles (BVA data
 * product) + registry-derived copilot count + why-now decision table (editorial,
 * i18n) + patient-path strip + role launcher.
 *
 * Per FR-CX-004, FR-CX-006, NFR-GOV-006: every metric carries a live/simulated
 * badge + as-of/source provenance. No inline literals for value or capacity tiles.
 */
export function StartView() {
  const s = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { capabilities } = useRoleLens();
  const visibleTiles = LAUNCHER_TILES.filter((tile) => !tile.requiresCsaNav || capabilities.nav.csa);
  const copilotCount = LAUNCHER_TILES.length;

  const [siteCapacity, setSiteCapacity] = useState<SiteCapacitySummary | null>(null);

  useEffect(() => {
    let active = true;
    const scope: ScenarioScope =
      mode === 'demo' ? GOLDEN_THREAD_SCOPE : { hospital: 'aggregated', windowHours: 72, pinned: false };
    loadSiteCapacitySummary(scope, mode)
      .then((data) => {
        if (active) setSiteCapacity(data);
      })
      .catch(() => {
        // Teaser remains null — degraded gracefully per NFR-REL-003
      });
    return () => {
      active = false;
    };
  }, [mode]);

  return (
    <section className={s.root} data-testid="start-view">
      {/* Hero */}
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
      <Badge
        appearance="filled"
        color={mode === 'demo' ? 'brand' : 'success'}
        data-testid="start-mode-badge"
      >
        {mode === 'demo'
          ? t('start.mode.demo', 'Demo — simulated golden-thread showcase')
          : t('start.mode.user', 'User — live working mode')}
      </Badge>

      {/* Live capacity teaser — reads the same OOA golden source */}
      <div className={s.section} data-testid="start-capacity-teaser">
        <Title3 as="h2">{t('start.capacityTeaser.title', 'Site capacity')}</Title3>
        {siteCapacity && (
          <Card>
            <div className={s.teaserRow}>
              <div className={s.teaserStat}>
                <Text weight="semibold">
                  {t('start.capacityTeaser.peakWard', {
                    ward: siteCapacity.peakWard,
                    pct: siteCapacity.peakPct,
                    defaultValue: '{{ward}} → {{pct}}%',
                  })}
                </Text>
                <Badge
                  appearance="tint"
                  color={siteCapacity.provenance === 'live' ? 'success' : 'informative'}
                  data-testid="start-capacity-provenance-badge"
                >
                  {t(`handoff.${siteCapacity.provenance}`)}
                </Badge>
              </div>
              <div className={s.teaserStat}>
                <Text weight="semibold">
                  {siteCapacity.siteGapBeds < 0
                    ? t('start.capacityTeaser.siteGapDeficit', {
                        beds: Math.abs(siteCapacity.siteGapBeds),
                        defaultValue: 'Deficit {{beds}} beds',
                      })
                    : t('start.capacityTeaser.siteGapSurplus', {
                        beds: siteCapacity.siteGapBeds,
                        defaultValue: 'Surplus {{beds}} beds',
                      })}
                </Text>
              </div>
              <div className={s.teaserStat}>
                <Text weight="semibold">
                  {t('start.capacityTeaser.breachEta', {
                    hours: siteCapacity.breachEtaHours,
                    defaultValue: 'Breach ~{{hours}}h',
                  })}
                </Text>
              </div>
            </div>
            <Caption1 className={s.caption}>
              {t('start.capacityTeaser.firstSurfacedBy', {
                agent: siteCapacity.firstSurfacedBy,
                defaultValue: 'surfaced by {{agent}}',
              })}{' '}
              ·{' '}
              {t('start.capacityTeaser.asOf', {
                time: siteCapacity.asOf.slice(0, 16).replace('T', ' '),
                defaultValue: 'as of {{time}}',
              })}
            </Caption1>
          </Card>
        )}
      </div>

      {/* Value / ROI tiles — bound to bvaHeadlineKpis, no inline numbers */}
      <div className={s.section} data-testid="start-value-tiles">
        <Title3 as="h2">{t('start.valueTiles.title', 'Value & ROI')}</Title3>
        <div className={s.grid}>
          {bvaHeadlineKpis.map((kpi) => (
            <Card key={kpi.measure} className={s.tile}>
              <Caption1 className={s.caption}>{kpi.measure}</Caption1>
              <Text size={900} weight="semibold">
                {kpi.value}
                {kpi.unit ? ` ${kpi.unit}` : ''}
              </Text>
              {kpi.targetLabel && <Caption1>{kpi.targetLabel}</Caption1>}
              <Caption1 className={s.caption}>
                  {t('start.valueTiles.romLabel', 'ROM estimate')} · {kpi.source} · {kpi.asOf.slice(0, 10)}
              </Caption1>
            </Card>
          ))}
        </div>
      </div>

      {/* Copilot count — registry-derived from LAUNCHER_TILES, not a hardcoded number */}
      <Card className={s.tile} data-testid="start-copilot-count">
        <Text size={900} weight="semibold">
          {copilotCount}
        </Text>
        <Text weight="semibold">
          {t('start.copilotCount.label', { count: copilotCount, defaultValue: '{{count}} specialised copilots' })}
        </Text>
        <Caption1 className={s.caption}>
          {t('start.copilotCount.caption', 'Registry-derived — one per role board')}
        </Caption1>
      </Card>

      {/* Why-now decision table — editorial, all copy via i18n */}
      <div className={s.section} data-testid="start-why-now">
        <Title3 as="h2">{t('start.whyNow.title', 'Why now?')}</Title3>
        <Caption1 className={s.caption}>
          {t('start.whyNow.caption', 'Illustrative comparison — editorial content, not live metrics')}
        </Caption1>
        <table style={{ borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr>
              <th className={s.tableCellHeader}>{t('start.whyNow.colAspect', 'Dimension')}</th>
              <th className={s.tableCellHeader}>{t('start.whyNow.colToday', 'Today')}</th>
              <th className={s.tableCellHeader}>{t('start.whyNow.colCuravias', 'With Curavias')}</th>
            </tr>
          </thead>
          <tbody>
            {WHY_NOW_ROWS.map((rowKey) => (
              <tr key={rowKey}>
                <td className={s.tableCell}>
                  <Text size={200} weight="semibold">
                    {t(`start.whyNow.${rowKey}.aspect`)}
                  </Text>
                </td>
                <td className={s.tableCell}>
                  <Text size={200}>{t(`start.whyNow.${rowKey}.today`)}</Text>
                </td>
                <td className={s.tableCell}>
                  <Text size={200}>{t(`start.whyNow.${rowKey}.curavias`)}</Text>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Patient-path strip — composed Card + arrow icons; capacity node reuses live siteCapacity */}
      <div className={s.section} data-testid="start-patient-path">
        <Title3 as="h2">{t('start.patientPath.title', 'Copilot at every care step')}</Title3>
        <Caption1 className={s.caption}>
          {t(
            'start.patientPath.caption',
            'Illustrative — copilots support each stage without handling real patient data (PHI)',
          )}
        </Caption1>
        <div className={s.pathStrip}>
          {PATIENT_PATH_STEPS.map((step, idx) => (
            <Fragment key={step.key}>
              <Card className={s.pathNode}>
                <Text size={200} weight="semibold">
                  {t(`start.patientPath.${step.key}`)}
                </Text>
                <Caption1 className={s.caption}>{step.agent}</Caption1>
                {step.showCapacity && siteCapacity && (
                  <Caption1>
                    {t('start.patientPath.occupancyNote', {
                      ward: siteCapacity.peakWard,
                      pct: siteCapacity.peakPct,
                      defaultValue: '{{ward}} → {{pct}}% in 72h',
                    })}
                  </Caption1>
                )}
              </Card>
              {idx < PATIENT_PATH_STEPS.length - 1 && (
                <ArrowRightRegular className={s.arrow} aria-hidden="true" />
              )}
            </Fragment>
          ))}
        </div>
      </div>

      {/* Role launcher grid — kept as-is incl. RBAC-gated Crisis tile */}
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

