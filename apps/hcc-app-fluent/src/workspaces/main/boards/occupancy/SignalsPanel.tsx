import { useTranslation } from 'react-i18next';
import { Badge, Body1, Caption1, makeStyles, tokens } from '@fluentui/react-components';
import {
  WeatherSunnyRegular,
  PulseRegular,
  AlertRegular,
  GlobeRegular,
  PeopleRegular,
  HeartPulseRegular,
  ArrowSwapRegular,
  ClockRegular,
  BeakerRegular,
  LiveRegular,
  CircleRegular,
  type FluentIcon,
} from '@fluentui/react-icons';
import { chipBadgeColor } from '../../../../copilot-rail/reco';
import type { BoardSignal } from '../../../../data/roleboard/occupancy-data';
import { space, radii, motion } from '../../../../theme/design-system';
import { ragColors } from '../../../../theme/curavias-theme';

const SIGNAL_ICONS: Record<string, FluentIcon> = {
  weather: WeatherSunnyRegular,
  pulse: PulseRegular,
  alert: AlertRegular,
  seismic: GlobeRegular,
  people: PeopleRegular,
  heartpulse: HeartPulseRegular,
  swap: ArrowSwapRegular,
  clock: ClockRegular,
};

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
    gap: space.s,
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
  leadIcon: {
    display: 'inline-flex',
    alignItems: 'center',
    fontSize: '20px',
    color: tokens.colorNeutralForeground2,
    flexShrink: 0,
  },
  main: { flexGrow: 1, minWidth: 0 },
  detail: { color: tokens.colorNeutralForeground3 },
  badges: { display: 'flex', alignItems: 'center', gap: space.s, flexShrink: 0 },
  provIcon: { display: 'inline-flex', alignItems: 'center', fontSize: '18px' },
});

interface SignalsPanelProps {
  signals: BoardSignal[];
}

/**
 * Sprint 27 — OOA Signals panel: external Trust-A feeds + internal operational
 * feeds. Each row is [signal icon] name · detail — [RAG status badge] [provenance
 * icon]. Provenance is icon-only (beaker = simulated, live = live) with an
 * accessible label. All demo rows are `simulated` (ADR-0016); a row flips to
 * `live` when a real adapter binds.
 */
export function SignalsPanel({ signals }: SignalsPanelProps) {
  const s = useStyles();
  const { t } = useTranslation();
  const external = signals.filter((x) => x.scope === 'external');
  const internal = signals.filter((x) => x.scope === 'internal');

  const renderRow = (sig: BoardSignal) => {
    const LeadIcon = SIGNAL_ICONS[sig.iconKey] ?? CircleRegular;
    const isLive = sig.provenance === 'live';
    const ProvIcon = isLive ? LiveRegular : BeakerRegular;
    const provLabel = isLive ? t('badge.liveData') : t('badge.simulatedData');
    return (
      <div key={sig.id} className={s.row}>
        <span className={s.leadIcon} aria-hidden="true"><LeadIcon /></span>
        <Body1 className={s.main}>
          {sig.label}
          {sig.detail ? <span className={s.detail}>{` \u00b7 ${sig.detail}`}</span> : null}
        </Body1>
        <div className={s.badges}>
          <Badge appearance="tint" color={chipBadgeColor(sig.statusTone)}>
            {sig.statusLabel}
          </Badge>
          <span
            className={s.provIcon}
            role="img"
            aria-label={provLabel}
            title={provLabel}
            style={{ color: isLive ? ragColors.good : ragColors.neutral }}
          >
            <ProvIcon />
          </span>
        </div>
      </div>
    );
  };

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
