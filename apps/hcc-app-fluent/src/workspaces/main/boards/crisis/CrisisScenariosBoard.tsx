import { useTranslation } from 'react-i18next';
import { Badge, Button, Caption1, makeStyles, tokens } from '@fluentui/react-components';
import { impactBadgeColor } from '../../../../copilot-rail/reco';
import { sortScenarios } from '../../../../data/roleboard/crisis-data';
import type { Scenario } from '../../../../data/roleboard/crisis-data';

const useStyles = makeStyles({
  wrap: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
  },
  hint: { color: tokens.colorNeutralForeground3 },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: {
    textAlign: 'left',
    padding: tokens.spacingVerticalXS,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    color: tokens.colorNeutralForeground3,
    fontWeight: tokens.fontWeightSemibold,
  },
  td: { padding: tokens.spacingVerticalXS, borderBottom: `1px solid ${tokens.colorNeutralStroke2}` },
  rankCell: { width: '2.5rem', textAlign: 'center' },
  probCell: { width: '5rem', textAlign: 'right' },
  bedCell: { width: '4rem', textAlign: 'right' },
});

interface CrisisScenariosBoardProps {
  scenarios: Scenario[];
  onSelectScenario: (scenario: Scenario) => void;
  onSimulateTop?: () => void;
}

/** Sprint 20 M5 (parity) — scenarios ranked by probability desc; row-click routes to simulation reco. */
export function CrisisScenariosBoard({ scenarios, onSelectScenario, onSimulateTop }: CrisisScenariosBoardProps) {
  const s = useStyles();
  const { t } = useTranslation();

  const sorted = sortScenarios(scenarios);

  return (
    <div className={s.wrap}>
      <div className={s.header}>
        <Caption1 className={s.hint}>{t('csa.scenarios.hint')}</Caption1>
        <Button appearance="primary" size="small" onClick={onSimulateTop}>
          {t('csa.scenarios.cta')}
        </Button>
      </div>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={`${s.th} ${s.rankCell}`}>{t('csa.scenarios.rank')}</th>
            <th className={s.th}>{t('csa.scenarios.name')}</th>
            <th className={`${s.th} ${s.probCell}`}>{t('csa.scenarios.probability')}</th>
            <th className={`${s.th} ${s.bedCell}`}>{t('csa.scenarios.bedImpact')}</th>
            <th className={s.th}>{t('csa.scenarios.spof')}</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((scenario, idx) => (
            <tr
              key={scenario.id}
              role="button"
              tabIndex={0}
              aria-label={scenario.name}
              onClick={() => onSelectScenario(scenario)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') onSelectScenario(scenario);
                if (e.key === ' ') { e.preventDefault(); onSelectScenario(scenario); }
              }}
              style={{ cursor: 'pointer' }}
            >
              <td className={`${s.td} ${s.rankCell}`}>
                <Badge appearance="tint" color="brand" shape="circular">
                  {idx + 1}
                </Badge>
              </td>
              <td className={s.td}>{scenario.name}</td>
              <td className={`${s.td} ${s.probCell}`}>
                <Badge appearance="tint" color={impactBadgeColor('probability')}>
                  {scenario.probability}%
                </Badge>
              </td>
              <td className={`${s.td} ${s.bedCell}`}>{scenario.bedImpact}</td>
              <td className={s.td}>
                {scenario.isSpof ? (
                  <Badge appearance="tint" color={impactBadgeColor('trust')}>SPOF</Badge>
                ) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
