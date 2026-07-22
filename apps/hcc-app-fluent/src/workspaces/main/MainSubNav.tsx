import { TabList, Tab } from '@fluentui/react-components';
import { useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useRoleLens } from '../../context/role-context';

/** Sprint 1 (parity) — MAIN board sub-navigation for the six role surfaces. */
const BOARDS = [
  { key: 'occupancy', label: 'Occupancy', gate: 'main' as const },
  { key: 'discharge', label: 'Discharge', gate: 'main' as const },
  { key: 'bed-manager', label: 'Bed management', gate: 'main' as const },
  { key: 'or-steering', label: 'OR steering', gate: 'main' as const },
  { key: 'staffing', label: 'Staffing', gate: 'main' as const },
  { key: 'crisis', label: 'Crisis', gate: 'csa' as const },
];

export function MainSubNav() {
  const { capabilities } = useRoleLens();
  const nav = useNavigate();
  const { t } = useTranslation();
  const { board = 'bed-manager' } = useParams();
  const canSee = (gate: 'main' | 'csa') => Boolean((capabilities.nav as Record<string, boolean>)[gate]);

  return (
    <TabList
      selectedValue={board}
      onTabSelect={(_e, d) => {
        const b = BOARDS.find((x) => x.key === d.value);
        if (b && canSee(b.gate)) nav(`/main/${b.key}`);
      }}
    >
      {BOARDS.map((b) => (
        <Tab key={b.key} value={b.key} disabled={!canSee(b.gate)}>
          {t(`board.nav.${b.key}`, b.label)}
        </Tab>
      ))}
    </TabList>
  );
}
