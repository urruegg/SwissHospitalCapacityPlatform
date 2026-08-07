import {
  Badge,
  Body1,
  Button,
  Caption1,
  Text,
  Title3,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  bvaHeadlineKpis,
  bvaPlanVsActual,
  bvaProofPoints,
  bvaSensitivityScenarios,
  bvaTrend,
  bvaValueLevers,
  type BvaHeadlineKpiPayload,
  type BvaProvenance,
  type BvaSensitivityScenarioPayload,
  type BvaTrendPoint,
} from '../../../data/bva/bva-evidence';
import { useCopilotRail } from '../../../copilot-rail/rail-context';
import type { GroundedReco } from '../../../copilot-rail/reco';
import type { ContextInsight } from '../../../journey/RoleBoard';
import { useShowcaseStyles } from '../../shared/narrative/showcase-styles';
import { scrollToSection } from '../../shared/narrative/NarrativeShell';

const useStyles = makeStyles({
  root: {
    display: 'grid',
    gap: tokens.spacingVerticalL,
  },
  kpiGrid: {
    display: 'grid',
    gap: tokens.spacingHorizontalM,
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
  },
  panelGrid: {
    display: 'grid',
    gap: tokens.spacingHorizontalM,
    gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 0.8fr)',
    '@media (max-width: 900px)': {
      gridTemplateColumns: '1fr',
    },
  },
  column: {
    display: 'grid',
    gap: tokens.spacingVerticalM,
    alignContent: 'start',
  },
  panel: {
    display: 'grid',
    gap: tokens.spacingVerticalS,
    padding: tokens.spacingHorizontalL,
    borderRadius: tokens.borderRadiusXLarge,
    backgroundColor: tokens.colorNeutralBackground1,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    boxShadow: tokens.shadow2,
    minWidth: 0,
  },
  // Final decision card: green left accent (mockup / backstage decision surface).
  finalCard: {
    borderLeftWidth: '4px',
    borderLeftColor: '#17B890',
  },
  panelTitle: {
    overflowWrap: 'anywhere',
  },
  metricTile: {
    display: 'grid',
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusLarge,
    backgroundColor: tokens.colorNeutralBackground1,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    boxShadow: tokens.shadow2,
    minWidth: 0,
  },
  metricValue: {
    // Deep, theme-adaptive green (AA on both light card + dark surface).
    // colorBrandForeground1 (#17b890) only reaches 2.53:1 on white, below the
    // 3:1 large-text threshold; colorPaletteGreenForeground1 clears it.
    color: tokens.colorPaletteGreenForeground1,
    overflowWrap: 'anywhere',
  },
  muted: {
    color: tokens.colorNeutralForeground3,
  },
  table: {
    tableLayout: 'fixed',
  },
  pills: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalXS,
  },
  pillButton: {
    borderRadius: tokens.borderRadiusCircular,
  },
  evidenceList: {
    margin: 0,
    paddingLeft: tokens.spacingHorizontalL,
    display: 'grid',
    gap: tokens.spacingVerticalXS,
  },
  evidenceItem: {
    display: 'grid',
    gap: tokens.spacingVerticalXXS,
  },
  decisionCard: {
    display: 'grid',
    gap: tokens.spacingVerticalM,
  },
  decisionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalS,
    alignItems: 'flex-start',
    flexWrap: 'wrap',
  },
  ctaRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
    alignItems: 'center',
  },
});

interface EvidenceEntry {
  id: string;
  title: string;
  summary: string;
  provenance: BvaProvenance;
}

function formatHeadlineValue(payload: BvaHeadlineKpiPayload) {
  return payload.unit ? `${payload.value} ${payload.unit}` : payload.value;
}

function formatCurrency(value: number, currency: string) {
  return `${currency} ${new Intl.NumberFormat('de-CH', { maximumFractionDigits: 0 }).format(value)}`;
}

function formatVariance(value: number) {
  return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
}

function formatTrendValue(value: number, unit?: string) {
  return `${new Intl.NumberFormat('de-CH', {
    minimumFractionDigits: value % 1 === 0 ? 0 : 2,
    maximumFractionDigits: 2,
  }).format(value)}${unit ? ` ${unit}` : ''}`;
}

function romCaption(
  t: ReturnType<typeof useTranslation>['t'],
  provenance: BvaProvenance,
) {
  return `${t('start.valueTiles.romLabel')} · ${provenance.source} · ${t('start.capacityTeaser.asOf', {
    time: provenance.asOf.slice(0, 10),
  })}`;
}

function selectedScenarioSummary(
  t: ReturnType<typeof useTranslation>['t'],
  scenario: BvaSensitivityScenarioPayload,
) {
  return t('start.frontier.bva.sensitivitySummary', {
    benefit: formatCurrency(scenario.annualBenefit, scenario.currency),
    tco: formatCurrency(scenario.threeYearTco, scenario.currency),
    roi: `${scenario.threeYearRoiPct}%`,
  });
}

function buildInsight(title: string, selectedScenarioName: string): ContextInsight {
  return {
    id: 'start-bva-decision',
    label: title,
    context: {
      source: 'start-bva-decision-section',
      headlineMeasures: bvaHeadlineKpis.map((payload) => payload.measure),
      tcoMeasure: bvaPlanVsActual.measure,
      valueLevers: bvaValueLevers.map((lever) => lever.lever),
      selectedSensitivityScenario: selectedScenarioName,
    },
  };
}

function buildReco(
  t: ReturnType<typeof useTranslation>['t'],
  latestTrendPoint: BvaTrendPoint,
  selectedScenario: BvaSensitivityScenarioPayload,
): GroundedReco {
  return {
    agentLabel: 'product-owner-agent',
    contextChip: {
      subject: t('start.frontier.bva.title'),
      qualifiers: [selectedScenario.scenario],
      status: t('start.frontier.guardrails.advisory'),
      tone: 'signal',
    },
    read: t('start.frontier.bva.railRead', {
      netValue: formatHeadlineValue(bvaHeadlineKpis[0]),
      roi: formatHeadlineValue(bvaHeadlineKpis[1]),
      tcoMeasure: bvaPlanVsActual.measure,
      trend: `${latestTrendPoint.label} ${formatTrendValue(latestTrendPoint.value, bvaTrend.unit)}`,
    }),
    levers: [
      {
        text: t('start.frontier.bva.cta'),
        impact: { label: t('start.valueTiles.romLabel'), tone: 'trust' },
      },
    ],
    citations: Array.from(
      new Set([
        bvaHeadlineKpis[0].source,
        bvaPlanVsActual.source,
        selectedScenario.source,
        bvaTrend.source,
      ]),
    ),
    provenance: 'simulated',
    followUps: [
      t('start.frontier.bva.followUps.provenance'),
      t('start.frontier.bva.followUps.budget'),
      t('start.frontier.bva.followUps.sensitivity'),
    ],
  };
}

/**
 * Distinct proof/evidence entries for the "Proof & evidence" panel: the
 * latest `bvaTrend` reading plus the qualitative `bvaProofPoints` governance
 * claims. Deliberately excludes `bvaHeadlineKpis` / `bvaPlanVsActual` — those
 * already have their own panels (KPI tiles, TCO table) and must not be
 * duplicated here.
 */
function proofEntries(
  latestTrendPoint: BvaTrendPoint,
): EvidenceEntry[] {
  return [
    {
      id: bvaTrend.measure,
      title: bvaTrend.measure,
      summary: `${latestTrendPoint.label} · ${formatTrendValue(latestTrendPoint.value, bvaTrend.unit)}`,
      provenance: bvaTrend,
    },
    ...bvaProofPoints.map((payload) => ({
      id: payload.id,
      title: payload.claim,
      summary: `${payload.target} · ${payload.cadence}`,
      provenance: payload,
    })),
  ];
}

export function BvaDecisionSection() {
  const styles = useStyles();
  const sc = useShowcaseStyles();
  const { t } = useTranslation();
  const defaultScenario =
    bvaSensitivityScenarios.find((scenario) => scenario.scenario === 'Base ROM') ??
    bvaSensitivityScenarios[0];
  const [selectedScenarioId, setSelectedScenarioId] = useState(defaultScenario?.id ?? '');
  const selectedScenario =
    bvaSensitivityScenarios.find((scenario) => scenario.id === selectedScenarioId) ?? defaultScenario;
  const latestTrendPoint = bvaTrend.points[bvaTrend.points.length - 1];

  let rail: ReturnType<typeof useCopilotRail> | null = null;
  try {
    rail = useCopilotRail();
  } catch {
    rail = null;
  }

  const evidence = useMemo(
    () => (latestTrendPoint ? proofEntries(latestTrendPoint) : []),
    [latestTrendPoint],
  );

  if (!selectedScenario || !latestTrendPoint) {
    return null;
  }

  return (
    <div className={styles.root} data-testid="bva-decision-section">
      <div className={styles.kpiGrid} data-testid="bva-kpi-grid">
        {bvaHeadlineKpis.map((payload) => (
          <article key={payload.measure} className={styles.metricTile}>
            <Text weight="semibold">{payload.measure}</Text>
            <Title3 as="span" className={styles.metricValue} data-testid="bva-kpi-figure">
              {formatHeadlineValue(payload)}
            </Title3>
            {payload.targetLabel ? <Body1>{payload.targetLabel}</Body1> : null}
            <Caption1 className={styles.muted} data-testid="bva-rom-caption">
              {romCaption(t, payload)}
            </Caption1>
          </article>
        ))}
      </div>

      <div className={styles.panelGrid}>
        <div className={styles.column}>
          <section className={styles.panel}>
            <Title3 as="h3" className={styles.panelTitle}>
              {t('start.frontier.bva.tcoTitle')}
            </Title3>
            <table className={mergeClasses(sc.table, styles.table)} data-testid="bva-tco-table">
              <thead>
                <tr>
                  <th className={sc.th}>{t('start.frontier.bva.columns.figure')}</th>
                  <th className={sc.th}>{t('start.frontier.bva.columns.value')}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className={sc.td}>{bvaPlanVsActual.measure}</td>
                  <td className={sc.td}>{formatCurrency(bvaPlanVsActual.plan, bvaPlanVsActual.currency)}</td>
                </tr>
                <tr>
                  <td className={sc.td}>{t('start.frontier.bva.tcoActual')}</td>
                  <td className={sc.td}>{formatCurrency(bvaPlanVsActual.actual, bvaPlanVsActual.currency)}</td>
                </tr>
                <tr>
                  <td className={sc.td}>{t('start.frontier.bva.tcoVariance')}</td>
                  <td className={sc.td}>{formatVariance(bvaPlanVsActual.variancePct)}</td>
                </tr>
              </tbody>
            </table>
            <Caption1 className={styles.muted} data-testid="bva-rom-caption">
              {romCaption(t, bvaPlanVsActual)}
            </Caption1>
          </section>

          <section className={styles.panel}>
            <Title3 as="h3" className={styles.panelTitle}>
              {t('start.frontier.bva.valueLeversTitle')}
            </Title3>
            <table className={mergeClasses(sc.table, styles.table)} data-testid="bva-value-levers-table">
              <thead>
                <tr>
                  <th className={sc.th}>{t('start.frontier.bva.columns.lever')}</th>
                  <th className={sc.th}>{t('start.frontier.bva.columns.annualBenefit')}</th>
                  <th className={sc.th}>{t('start.frontier.bva.columns.valueLogic')}</th>
                </tr>
              </thead>
              <tbody>
                {bvaValueLevers.map((payload) => (
                  <tr key={payload.id}>
                    <td className={sc.td}>{payload.lever}</td>
                    <td className={sc.td}>{formatCurrency(payload.annualBenefit, payload.currency)}</td>
                    <td className={sc.td}>{payload.valueLogic}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <Caption1 className={styles.muted} data-testid="bva-rom-caption">
              {romCaption(t, bvaValueLevers[0])}
            </Caption1>
          </section>
        </div>

        <div className={styles.column}>
          <section className={styles.panel}>
            <Title3 as="h3" className={styles.panelTitle}>
              {t('start.frontier.bva.sensitivityTitle')}
            </Title3>
            <div className={styles.pills} data-testid="bva-sensitivity-controls">
              {bvaSensitivityScenarios.map((scenario) => (
                <Button
                  key={scenario.id}
                  className={styles.pillButton}
                  appearance={scenario.id === selectedScenario.id ? 'primary' : 'secondary'}
                  size="small"
                  aria-pressed={scenario.id === selectedScenario.id}
                  onClick={() => setSelectedScenarioId(scenario.id)}
                >
                  {scenario.scenario}
                </Button>
              ))}
            </div>
            <Text data-testid="bva-sensitivity-value">
              {selectedScenarioSummary(t, selectedScenario)}
            </Text>
            <Body1>{selectedScenario.comment}</Body1>
            <Caption1 className={styles.muted} data-testid="bva-rom-caption">
              {romCaption(t, selectedScenario)}
            </Caption1>
          </section>

          <section className={styles.panel}>
            <Title3 as="h3" className={styles.panelTitle}>
              {t('start.frontier.bva.proofTitle')}
            </Title3>
            <ul className={styles.evidenceList} data-testid="bva-proof-list">
              {evidence.map((entry) => (
                <li key={entry.id} className={styles.evidenceItem}>
                  <Text weight="semibold">{entry.title}</Text>
                  <Body1>{entry.summary}</Body1>
                  <Caption1 className={styles.muted}>
                    {entry.provenance.source} · {t('start.capacityTeaser.asOf', { time: entry.provenance.asOf.slice(0, 10) })}
                    {entry.provenance.powerBiEmbedFallback
                      ? ` · ${t('start.frontier.bva.proofFallback')}`
                      : ''}
                  </Caption1>
                </li>
              ))}
            </ul>
            <Caption1 className={styles.muted} data-testid="bva-rom-caption">
              {romCaption(t, bvaTrend)}
            </Caption1>
          </section>

          <section className={`${styles.panel} ${styles.finalCard}`} data-testid="bva-final-card">
            <div className={styles.decisionCard}>
              <div className={styles.decisionHeader}>
                <Title3 as="h3" className={styles.panelTitle}>
                  {t('start.frontier.bva.finalTitle')}
                </Title3>
                <Badge appearance="tint" color="informative">
                  {t('start.frontier.bva.finalBadge')}
                </Badge>
              </div>
              <Body1>
                {t('start.frontier.bva.finalRead', {
                  netValue: formatHeadlineValue(bvaHeadlineKpis[0]),
                  roi: formatHeadlineValue(bvaHeadlineKpis[1]),
                  budget: `${formatCurrency(bvaPlanVsActual.actual, bvaPlanVsActual.currency)} (${formatVariance(
                    bvaPlanVsActual.variancePct,
                  )})`,
                  trend: `${latestTrendPoint.label} ${formatTrendValue(latestTrendPoint.value, bvaTrend.unit)}`,
                })}
              </Body1>
              <div className={styles.ctaRow}>
                <Button
                  appearance="primary"
                  data-testid="bva-launch-cta"
                  onClick={() => scrollToSection('ninety-day')}
                >
                  {t('start.frontier.bva.launchCta')}
                </Button>
                <Button
                  appearance="secondary"
                  data-testid="bva-decision-cta"
                  onClick={() =>
                    rail?.openWithReco(
                      buildInsight(t('start.frontier.bva.title'), selectedScenario.scenario),
                      buildReco(t, latestTrendPoint, selectedScenario),
                    )
                  }
                >
                  {t('start.frontier.bva.cta')}
                </Button>
              </div>
              <Caption1 className={styles.muted} data-testid="bva-rom-caption">
                {romCaption(t, bvaPlanVsActual)}
              </Caption1>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
