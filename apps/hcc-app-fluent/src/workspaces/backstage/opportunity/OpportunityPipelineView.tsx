import {
  Badge,
  Body1Strong,
  Caption1,
  Card,
  Text,
  Title3,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import {
  getOpportunityPipeline,
  getStatusCounts,
  listOpportunities,
  type OpportunityRow,
  type OpportunityStatus,
} from '../../../data/opportunity/opportunity-service';

const STATUS_ORDER: OpportunityStatus[] = [
  'new',
  'evaluating',
  'qualified',
  'onboarding',
  'won',
  'disqualified',
  'lost',
];

const STATUS_COLOR: Record<OpportunityStatus, 'brand' | 'danger' | 'important' | 'informative' | 'severe' | 'subtle' | 'success' | 'warning'> = {
  new: 'informative',
  evaluating: 'warning',
  qualified: 'brand',
  onboarding: 'brand',
  won: 'success',
  disqualified: 'subtle',
  lost: 'danger',
};

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalL },
  intro: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS },
  metrics: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: tokens.spacingHorizontalM,
  },
  metricCard: { gap: tokens.spacingVerticalXS },
  metricValue: { fontSize: tokens.fontSizeBase600, fontWeight: tokens.fontWeightSemibold },
  statusGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: tokens.spacingHorizontalS,
  },
  statusCard: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXXS,
    padding: tokens.spacingHorizontalM,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderRadius: tokens.borderRadiusMedium,
  },
  tableWrap: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalS },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: {
    textAlign: 'left',
    padding: tokens.spacingVerticalXS,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    color: tokens.colorNeutralForeground3,
    fontWeight: tokens.fontWeightSemibold,
  },
  td: { padding: tokens.spacingVerticalXS, borderBottom: `1px solid ${tokens.colorNeutralStroke2}` },
  hospital: { fontWeight: tokens.fontWeightSemibold },
  muted: { color: tokens.colorNeutralForeground3 },
});

function formatRoi(value: number | null): string {
  return value === null ? 'n/a' : `${value.toFixed(2)}%`;
}

function OpportunityTable({ opportunities }: { opportunities: OpportunityRow[] }) {
  const styles = useStyles();
  return (
    <div className={styles.tableWrap}>
      <Body1Strong>Opportunity list</Body1Strong>
      <table className={styles.table}>
        <thead>
          <tr>
            <th className={styles.th}>Hospital</th>
            <th className={styles.th}>Archetype</th>
            <th className={styles.th}>Status</th>
            <th className={styles.th}>Language</th>
            <th className={styles.th}>ROI</th>
            <th className={styles.th}>PO verdict</th>
            <th className={styles.th}>Latest event</th>
          </tr>
        </thead>
        <tbody>
          {opportunities.map((row) => (
            <tr key={row.id}>
              <td className={`${styles.td} ${styles.hospital}`}>{row.hospitalName}</td>
              <td className={styles.td}>{row.archetype}</td>
              <td className={styles.td}>
                <Badge appearance="tint" color={STATUS_COLOR[row.status]}>
                  {row.status}
                </Badge>
              </td>
              <td className={styles.td}>{row.language.toUpperCase()}</td>
              <td className={styles.td}>{formatRoi(row.roiPct)}</td>
              <td className={styles.td}>{row.poVerdict ?? 'pending'}</td>
              <td className={styles.td}>{row.latestEvent?.event ?? 'none'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function OpportunityPipelineView() {
  const styles = useStyles();
  const pipeline = getOpportunityPipeline();
  const counts = getStatusCounts();
  const opportunities = listOpportunities();

  return (
    <section className={styles.root} data-testid="opportunity-pipeline-view">
      <div className={styles.intro}>
        <Title3>Opportunity pipeline</Title3>
        <Caption1 className={styles.muted}>
          Committed D5 fixture from {opportunities.length} synthetic BVA opportunities.
        </Caption1>
      </div>

      <div className={styles.metrics}>
        <Card appearance="filled" className={styles.metricCard}>
          <Caption1>Total opportunities</Caption1>
          <Text className={styles.metricValue}>{pipeline.total}</Text>
        </Card>
        <Card appearance="filled" className={styles.metricCard}>
          <Caption1>Open opportunities</Caption1>
          <Text className={styles.metricValue}>{pipeline.open}</Text>
        </Card>
        <Card appearance="filled" className={styles.metricCard}>
          <Caption1>Weighted ROI</Caption1>
          <Text className={styles.metricValue} data-testid="opportunity-weighted-roi">
            {formatRoi(pipeline.weightedRoiPct)}
          </Text>
        </Card>
      </div>

      <div className={styles.statusGrid} aria-label="Opportunity status counts">
        {STATUS_ORDER.map((status) => (
          <div className={styles.statusCard} key={status}>
            <Badge appearance="tint" color={STATUS_COLOR[status]}>
              {status}
            </Badge>
            <Text className={styles.metricValue} data-testid={`opportunity-status-${status}`}>
              {counts[status]}
            </Text>
          </div>
        ))}
      </div>

      <OpportunityTable opportunities={opportunities} />
    </section>
  );
}
