import { Caption1, makeStyles, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { CIO_DECISIONS } from './start-content';

const useStyles = makeStyles({
  root: {
    minWidth: 0,
  },
  viewport: {
    overflowX: 'auto',
    paddingBottom: tokens.spacingVerticalXS,
  },
  table: {
    width: '100%',
    minWidth: '680px',
    borderCollapse: 'collapse',
    tableLayout: 'fixed',
  },
  caption: {
    captionSide: 'top',
    textAlign: 'left',
    color: tokens.colorNeutralForeground3,
    paddingBottom: tokens.spacingVerticalS,
  },
  header: {
    width: '28%',
    textAlign: 'left',
    padding: `${tokens.spacingVerticalS} ${tokens.spacingHorizontalM}`,
    borderBottom: `2px solid ${tokens.colorNeutralStroke1}`,
    color: tokens.colorNeutralForeground2,
    verticalAlign: 'top',
    overflowWrap: 'anywhere',
  },
  cell: {
    padding: `${tokens.spacingVerticalM} ${tokens.spacingHorizontalM}`,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    verticalAlign: 'top',
    overflowWrap: 'anywhere',
  },
  decision: {
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  preview: {
    color: tokens.colorBrandForeground1,
    backgroundColor: tokens.colorBrandBackground2,
  },
});

export function CioChallengerSection() {
  const styles = useStyles();
  const { t } = useTranslation();

  return (
    <div className={styles.root}>
      <div className={styles.viewport}>
        <table
          className={styles.table}
          aria-label={t('start.frontier.cioWhyNow.tableLabel')}
        >
          <caption className={styles.caption}>
            <Caption1>{t('start.frontier.cioWhyNow.caption')}</Caption1>
          </caption>
          <thead>
            <tr>
              <th className={styles.header} scope="col">
                {t('start.frontier.cioWhyNow.columns.decision')}
              </th>
              <th className={styles.header} scope="col">
                {t('start.frontier.cioWhyNow.columns.today')}
              </th>
              <th className={styles.header} scope="col">
                {t('start.frontier.cioWhyNow.columns.preview')}
              </th>
            </tr>
          </thead>
          <tbody>
            {CIO_DECISIONS.map((decision) => (
              <tr key={decision.id} data-testid="cio-decision-row">
                <th className={`${styles.cell} ${styles.decision}`} scope="row">
                  {t(decision.decisionKey)}
                </th>
                <td className={styles.cell}>{t(decision.todayKey)}</td>
                <td className={`${styles.cell} ${styles.preview}`}>
                  {t(decision.previewKey)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
