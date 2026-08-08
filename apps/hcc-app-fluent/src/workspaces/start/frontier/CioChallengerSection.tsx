import { Caption1, makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { useShowcaseStyles } from '../../shared/narrative/showcase-styles';
import { useCopilotRail } from '../../../copilot-rail/rail-context';
import { enrichWithLiveAnswer, startInsight, startReco } from './start-rail';
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
    minWidth: '680px',
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
  },
  preview: {
    color: tokens.colorBrandForeground1,
    backgroundColor: tokens.colorBrandBackground2,
  },
  rowButton: {
    display: 'block',
    width: '100%',
    textAlign: 'left',
    background: 'none',
    border: 'none',
    padding: 0,
    margin: 0,
    font: 'inherit',
    color: 'inherit',
    cursor: 'pointer',
    ':hover': { color: tokens.colorBrandForeground1 },
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: '2px',
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '2px',
    },
  },
});

export function CioChallengerSection() {
  const styles = useStyles();
  const sc = useShowcaseStyles();
  const { t } = useTranslation();
  let rail: ReturnType<typeof useCopilotRail> | null = null;
  try {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    rail = useCopilotRail();
  } catch {
    rail = null;
  }

  return (
    <div className={styles.root}>
      <div className={sc.panel}>
        <div className={styles.viewport}>
          <table
            className={mergeClasses(sc.table, styles.table)}
            aria-label={t('start.frontier.cioWhyNow.tableLabel')}
          >
            <caption className={styles.caption}>
              <Caption1>{t('start.frontier.cioWhyNow.caption')}</Caption1>
            </caption>
            <thead>
              <tr>
                <th className={mergeClasses(sc.th, styles.header)} scope="col">
                  {t('start.frontier.cioWhyNow.columns.decision')}
                </th>
                <th className={mergeClasses(sc.th, styles.header)} scope="col">
                  {t('start.frontier.cioWhyNow.columns.today')}
                </th>
                <th className={mergeClasses(sc.th, styles.header)} scope="col">
                  {t('start.frontier.cioWhyNow.columns.preview')}
                </th>
              </tr>
            </thead>
            <tbody>
              {CIO_DECISIONS.map((decision) => (
                <tr key={decision.id} data-testid="cio-decision-row">
                  <th className={mergeClasses(sc.td, sc.tdName)} scope="row">
                    <button
                      type="button"
                      className={styles.rowButton}
                      data-testid="cio-decision-row-trigger"
                      onClick={() => {
                        rail?.openWithReco(
                          startInsight(`cio-${decision.id}`, t(decision.decisionKey)),
                          startReco(
                            t(decision.decisionKey),
                            t(decision.previewKey),
                            [t(decision.todayKey)],
                            ['hcp:CioWhyNow'],
                          ),
                        );
                        if (rail) {
                          void enrichWithLiveAnswer(t(decision.previewKey), rail).catch((error) => {
                            console.error('PO agent live enrichment failed', error);
                          });
                        }
                      }}
                    >
                      {t(decision.decisionKey)}
                    </button>
                  </th>
                  <td className={sc.td}>{t(decision.todayKey)}</td>
                  <td className={mergeClasses(sc.td, styles.preview)}>
                    {t(decision.previewKey)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
