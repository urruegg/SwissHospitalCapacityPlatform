import {
  Body1,
  Button,
  Caption1,
  Text,
  Title3,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  bvaBuildCost,
  bvaHeadlineKpis,
  bvaPlanVsActual,
  bvaSensitivityScenarios,
  bvaValueLevers,
  type BvaHeadlineKpiPayload,
  type BvaProvenance,
  type BvaSensitivityScenarioPayload,
} from '../../../data/bva/bva-evidence';
import { BVA_CURRENCY } from '../../../data/bva/bva-figures';
import { useShowcaseStyles } from '../../shared/narrative/showcase-styles';

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
  panelFull: {
    gridColumn: '1 / -1',
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
  panelTitle: {
    margin: 0,
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
});

function formatHeadlineValue(payload: BvaHeadlineKpiPayload) {
  return payload.unit ? `${payload.value} ${payload.unit}` : payload.value;
}

function formatCurrency(value: number, currency: string) {
  return `${currency} ${new Intl.NumberFormat('de-CH', { maximumFractionDigits: 0 }).format(value)}`;
}

function formatVariance(value: number) {
  return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
}

function romCaption(
  t: ReturnType<typeof useTranslation>['t'],
  provenance: BvaProvenance,
) {
  return `${t('start.valueTiles.romLabel')} · ${provenance.source} · ${t('start.capacityTeaser.asOf', {
    time: provenance.asOf.slice(0, 10),
  })}`;
}

/**
 * Like {@link romCaption}, but for evidence that is not ROM — the measured
 * 90-day build cost carries `measured`/`estimated`/`mixed` labels instead.
 * Never reuse `romCaption` for this data: it would misrepresent a measured
 * figure as a ±30% planning estimate.
 */
function evidenceCaption(
  t: ReturnType<typeof useTranslation>['t'],
  evidenceStatus: string,
  provenance: BvaProvenance,
) {
  const label = t(`start.frontier.bva.evidenceStatus.${evidenceStatus}`, evidenceStatus);
  return `${label} · ${provenance.source} · ${t('start.capacityTeaser.asOf', {
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

export function BvaDecisionSection() {
  const styles = useStyles();
  const sc = useShowcaseStyles();
  const { t } = useTranslation();
  const defaultScenario =
    bvaSensitivityScenarios.find((scenario) => scenario.id === 'base-rom') ??
    bvaSensitivityScenarios[0];
  const [selectedScenarioId, setSelectedScenarioId] = useState(defaultScenario?.id ?? '');
  const selectedScenario =
    bvaSensitivityScenarios.find((scenario) => scenario.id === selectedScenarioId) ?? defaultScenario;

  if (!selectedScenario) {
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

        <section className={styles.panel} data-testid="bva-build-cost-panel">
          <Title3 as="h3" className={styles.panelTitle}>
            {t('start.frontier.bva.buildCostTitle', 'Cost to build this MVP')}
          </Title3>
          <Title3 as="span" className={styles.metricValue} data-testid="bva-build-cost-total">
            {formatCurrency(bvaBuildCost.totalChf, BVA_CURRENCY)}
          </Title3>
          <table className={mergeClasses(sc.table, styles.table)} data-testid="bva-build-cost-table">
            <thead>
              <tr>
                <th className={sc.th}>{t('start.frontier.bva.columns.figure')}</th>
                <th className={sc.th}>{t('start.frontier.bva.columns.value')}</th>
              </tr>
            </thead>
            <tbody>
              {bvaBuildCost.components.map((component) => (
                <tr key={component.label}>
                  <td className={sc.td}>{component.label}</td>
                  <td className={sc.td}>
                    {formatCurrency(component.amountChf, BVA_CURRENCY)} ({component.sharePct}%)
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <Caption1 className={styles.muted} data-testid="bva-build-cost-caption">
            {evidenceCaption(t, bvaBuildCost.totalEvidenceStatus, bvaBuildCost)}
          </Caption1>
        </section>

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

        <section className={mergeClasses(styles.panel, styles.panelFull)}>
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
    </div>
  );
}
