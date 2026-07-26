import { Fragment, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Caption1, Text, makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import {
  ArrowUpRegular,
  ArrowRightRegular,
  ArrowDownRegular,
  ChevronRightRegular,
  ChevronDownRegular,
  ErrorCircleFilled,
  WarningFilled,
  CheckmarkCircleFilled,
} from '@fluentui/react-icons';
import type { ChipTone } from '../../../../copilot-rail/reco';
import type { WardRow, WardTrend } from '../../../../data/roleboard/occupancy-data';
import { space, motion } from '../../../../theme/design-system';
import { ragColors } from '../../../../theme/curavias-theme';

const useStyles = makeStyles({
  wrap: { display: 'flex', flexDirection: 'column', gap: space.s },
  hint: { color: tokens.colorNeutralForeground3 },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: {
    textAlign: 'left',
    whiteSpace: 'nowrap',
    paddingTop: space.s,
    paddingBottom: space.s,
    paddingLeft: space.m,
    paddingRight: space.m,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    color: tokens.colorNeutralForeground3,
    fontWeight: tokens.fontWeightSemibold,
  },
  thIcon: { width: '48px', textAlign: 'center' },
  colToggle: { width: '28px', textAlign: 'center', paddingLeft: space.xs, paddingRight: space.xs },
  td: {
    paddingTop: space.s,
    paddingBottom: space.s,
    paddingLeft: space.m,
    paddingRight: space.m,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  iconCell: { textAlign: 'center' },
  row: {
    transitionProperty: 'background-color',
    transitionDuration: motion.durationFast,
    transitionTimingFunction: motion.easyEase,
    ':hover': { backgroundColor: tokens.colorNeutralBackground1Hover },
  },
  wardBtn: { justifyContent: 'flex-start', minWidth: 0, fontWeight: tokens.fontWeightSemibold },
  statusIcon: { display: 'inline-flex', alignItems: 'center', fontSize: '20px' },
  detailRow: { backgroundColor: tokens.colorNeutralBackground2 },
  detailCell: {
    paddingTop: space.m,
    paddingBottom: space.m,
    paddingLeft: space.m,
    paddingRight: space.m,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  detailGrid: { display: 'flex', flexWrap: 'wrap', gap: space.xl, marginBottom: space.s },
  detailItem: { display: 'flex', flexDirection: 'column', gap: space.xs },
  onto: { color: tokens.colorNeutralForeground3, fontStyle: 'italic' },
});

const TREND: Record<WardTrend, { Icon: typeof ArrowUpRegular; color: string }> = {
  rising: { Icon: ArrowUpRegular, color: ragColors.bad },
  flat: { Icon: ArrowRightRegular, color: ragColors.neutral },
  falling: { Icon: ArrowDownRegular, color: ragColors.good },
};

const FLAG: Partial<Record<ChipTone, { Icon: typeof ErrorCircleFilled; color: string }>> = {
  over: { Icon: ErrorCircleFilled, color: ragColors.bad },
  watch: { Icon: WarningFilled, color: ragColors.neutral },
  ok: { Icon: CheckmarkCircleFilled, color: ragColors.good },
};

function TrendIcon({ trend }: { trend: WardTrend }) {
  const s = useStyles();
  const { Icon, color } = TREND[trend];
  return (
    <span className={s.statusIcon} style={{ color }}>
      <Icon aria-label={trend} />
    </span>
  );
}

function FlagIcon({ flag }: { flag: ChipTone }) {
  const s = useStyles();
  const f = FLAG[flag] ?? FLAG.ok!;
  return (
    <span className={s.statusIcon} style={{ color: f.color }}>
      <f.Icon aria-label={flag.toUpperCase()} />
    </span>
  );
}

interface WardForecastTableProps {
  wards: WardRow[];
  onSelectWard: (ward: WardRow) => void;
}

export function WardForecastTable({ wards, onSelectWard }: WardForecastTableProps) {
  const s = useStyles();
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState<string | null>(null);
  const toggle = (id: string) => setExpanded((cur) => (cur === id ? null : id));

  return (
    <div className={s.wrap}>
      <Caption1 className={s.hint}>{t('ooa.table.hint')}</Caption1>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={mergeClasses(s.th, s.colToggle)} aria-label={t('ooa.table.details', 'Details')} />
            <th className={s.th}>{t('ooa.table.ward')}</th>
            <th className={s.th}>{t('ooa.table.now')}</th>
            <th className={`${s.th} ${s.thIcon}`}>{t('ooa.table.trend')}</th>
            <th className={s.th}>{t('ooa.table.forecast')}</th>
            <th className={`${s.th} ${s.thIcon}`}>{t('ooa.table.flag')}</th>
          </tr>
        </thead>
        <tbody>
          {wards.map((w) => {
            const isOpen = expanded === w.id;
            return (
              <Fragment key={w.id}>
                <tr className={s.row}>
                  <td className={mergeClasses(s.td, s.colToggle)}>
                    <Button
                      appearance="subtle"
                      size="small"
                      icon={isOpen ? <ChevronDownRegular /> : <ChevronRightRegular />}
                      aria-label={t('ooa.table.toggleDetails', 'Toggle ward details')}
                      aria-expanded={isOpen}
                      onClick={() => toggle(w.id)}
                    />
                  </td>
                  <td className={s.td}>
                    <Button
                      appearance="transparent"
                      className={s.wardBtn}
                      aria-label={`${w.label} ${w.forecastPct}%`}
                      onClick={() => onSelectWard(w)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') onSelectWard(w);
                        else if (e.key === ' ') { e.preventDefault(); onSelectWard(w); }
                      }}
                    >
                      {w.label}
                    </Button>
                  </td>
                  <td className={s.td}>{`${w.nowPct}%`}</td>
                  <td className={`${s.td} ${s.iconCell}`}><TrendIcon trend={w.trend} /></td>
                  <td className={s.td}>{`${w.forecastPct}%`}</td>
                  <td className={`${s.td} ${s.iconCell}`}><FlagIcon flag={w.flag} /></td>
                </tr>
                {isOpen && (
                  <tr className={s.detailRow}>
                    <td className={mergeClasses(s.detailCell, s.colToggle)} />
                    <td className={s.detailCell} colSpan={5}>
                      <div className={s.detailGrid}>
                        <div className={s.detailItem}>
                          <Caption1 className={s.hint}>{t('ooa.detail.beds', 'Beds')}</Caption1>
                          <Text weight="semibold">{`${w.bedsUsed} / ${w.bedsTotal}`}</Text>
                        </div>
                        <div className={s.detailItem}>
                          <Caption1 className={s.hint}>{t('ooa.table.now')}</Caption1>
                          <Text weight="semibold">{`${w.nowPct}%`}</Text>
                        </div>
                        <div className={s.detailItem}>
                          <Caption1 className={s.hint}>{t('ooa.table.forecast')}</Caption1>
                          <Text weight="semibold">{`${w.forecastPct}%`}</Text>
                        </div>
                        <div className={s.detailItem}>
                          <Caption1 className={s.hint}>{t('ooa.table.trend')}</Caption1>
                          <Text weight="semibold">{w.trend}</Text>
                        </div>
                      </div>
                      <Caption1 className={s.onto}>
                        {`hcp:Ward "${w.label}" \u2192 hcp:CapacityUnit(Bed)`}
                      </Caption1>
                    </td>
                  </tr>
                )}
              </Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
