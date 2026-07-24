import { useTranslation } from 'react-i18next';
import { Badge, Body1, Caption1, makeStyles, tokens } from '@fluentui/react-components';
import { chipBadgeColor } from '../../../../copilot-rail/reco';
import type { BoardSignal } from '../../../../data/roleboard/occupancy-data';
import { space, radii, motion } from '../../../../theme/design-system';

const useStyles = makeStyles({
  wrap: { display: 'flex', flexDirection: 'column', gap: space.l },
  section: { display: 'flex', flexDirection: 'column', gap: space.xs },
  sectionHead: {
    color: tokens.colorNeutralForeground3,
    fontWeight: tokens.fontWeightSemibold,
    letterSpacing: '0.04em',
    textTransform: 'uppercase',
  },
  row: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: space.m,
    paddingTop: space.s,
    paddingBottom: space.s,
    paddingLeft: space.m,
    paddingRight: space.m,
    borderRadius: radii.control,
    backgroundColor: tokens.colorNeutralBackground2,
    transitionProperty: 'background-color',
    transitionDuration: motion.durationFast,
    ':hover': { backgroundColor: tokens.colorNeutralBackground2Hover },
  },
  rowMain: { display: 'flex', flexDirection: 'column', gap: space.xs, minWidth: 0 },
  detail: { color: tokens.colorNeutralForeground3 },
  badges: { display: 'flex', alignItems: 'center', gap: space.xs, flexShrink: 0 },
});

interface SignalsPanelProps {
  signals: BoardSignal[];
}

/**
 * Sprint 27 — OOA Signals panel: external Trust-A feeds + internal operational
 * feeds, each row carrying a RAG status badge and a live/simulated provenance
 * badge (mirrors the CSA signals treatment). All demo rows are `simulated`
 * (ADR-0016); a row flips to `live` when a real adapter binds.
 */
export function SignalsPanel({ signals }: SignalsPanelProps) {
  const s = useStyles();
  const { t } = useTranslation();
  const external = signals.filter((x) => x.scope === 'external');
  const internal = signals.filter((x) => x.scope === 'internal');
  const provText = (p: BoardSignal['provenance']) =>
    p === 'live' ? t('badge.liveData') : t('badge.simulatedData');

  const renderRow = (sig: BoardSignal) => (
    <div key={sig.id} className={s.row}>
      <div className={s.rowMain}>
        <Body1>
          {sig.label}
          {sig.detail ? <span className={s.detail}>{` \u00b7 ${sig.detail}`}</span> : null}
        </Body1>
      </div>
      <div className={s.badges}>
        <Badge appearance="tint" color={chipBadgeColor(sig.statusTone)}>
          {sig.statusLabel}
        </Badge>
        <Badge appearance="outline" color={sig.provenance === 'live' ? 'success' : 'warning'}>
          {provText(sig.provenance)}
        </Badge>
      </div>
    </div>
  );

  return (
    <div className={s.wrap} data-testid="ooa-signals-panel">
      <div className={s.section}>
        <Caption1 className={s.sectionHead}>
          {`${t('ooa.signals.external', 'External signals')} \u00b7 Trust-A`}
        </Caption1>
        {external.map(renderRow)}
      </div>
      <div className={s.section}>
        <Caption1 className={s.sectionHead}>{t('ooa.signals.internal', 'Internal signals')}</Caption1>
        {internal.map(renderRow)}
      </div>
    </div>
  );
}
