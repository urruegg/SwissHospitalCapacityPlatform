import { useTranslation } from 'react-i18next';
import { Fragment } from 'react';
import {
  Badge,
  Body1,
  Body2,
  Button,
  Caption1,
  CounterBadge,
  Popover,
  PopoverSurface,
  PopoverTrigger,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import {
  ArrowLeftRegular,
  ArrowRightRegular,
  PlayRegular,
  OpenRegular,
  ShieldTaskRegular,
  ProhibitedRegular,
} from '@fluentui/react-icons';
import { chipBadgeColor, impactBadgeColor, type GroundedReco, type RecoCta, type RecoLever } from './reco';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalS },
  chipRow: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalXS, flexWrap: 'wrap' },
  agentLine: { color: tokens.colorBrandForeground1 },
  metrics: { display: 'flex', alignItems: 'flex-end', gap: tokens.spacingHorizontalS, flexWrap: 'wrap' },
  metricCell: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXXS },
  metricValue: { fontWeight: tokens.fontWeightSemibold },
  metricLabel: { color: tokens.colorNeutralForeground3 },
  metricArrow: { color: tokens.colorNeutralForeground4, alignSelf: 'center', fontSize: tokens.fontSizeBase200 },
  levers: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS, margin: 0, padding: 0, listStyle: 'none' },
  lever: { display: 'flex', alignItems: 'flex-start', gap: tokens.spacingHorizontalXS },
  leverText: { flex: 1 },
  projection: { color: tokens.colorNeutralForeground3 },
  cites: { color: tokens.colorNeutralForeground4 },
  ctaWrap: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXXS },
  gateRow: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalXS, flexWrap: 'wrap' },
  gateHint: { color: tokens.colorNeutralForeground3 },
  refusedRead: { color: tokens.colorPaletteRedForeground1 },
  evidenceTrigger: {
    padding: 0,
    border: 'none',
    backgroundColor: 'transparent',
    cursor: 'pointer',
    font: 'inherit',
    display: 'inline-flex',
    borderRadius: tokens.borderRadiusSmall,
    ':focus-visible': { boxShadow: `0 0 0 2px ${tokens.colorStrokeFocus2}` },
  },
  evidenceCard: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS, maxWidth: '280px' },
  evidenceHead: { fontWeight: tokens.fontWeightSemibold },
  evidenceList: { margin: 0, paddingLeft: tokens.spacingHorizontalL, display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXXS },
  evidencePeople: { display: 'flex', flexWrap: 'wrap', gap: tokens.spacingHorizontalXS, marginTop: tokens.spacingVerticalXXS },
  evidenceMuted: { color: tokens.colorNeutralForeground3 },
});

function CtaIcon({ kind, requiresApproval }: { kind: RecoCta['kind']; requiresApproval?: boolean }) {
  if (requiresApproval) return <ShieldTaskRegular />;
  if (kind === 'handoff') return <ArrowRightRegular />;
  if (kind === 'action') return <PlayRegular />;
  return <OpenRegular />;
}

/**
 * Sprint 27 — impact badge with an optional evidence popover (hover/focus).
 * Responsible UI: the user sees the context, impact detail and affected people
 * behind the number before acting / approving.
 */
function ImpactBadge({ lever }: { lever: RecoLever }) {
  const s = useStyles();
  if (!lever.impact) return null;
  const badge = (
    <Badge appearance="tint" color={impactBadgeColor(lever.impact.tone)}>{lever.impact.label}</Badge>
  );
  const ev = lever.evidence;
  if (!ev) return badge;
  return (
    <Popover openOnHover withArrow mouseLeaveDelay={200} positioning="above">
      <PopoverTrigger disableButtonEnhancement>
        <button type="button" className={s.evidenceTrigger} aria-label={`Evidenz: ${lever.impact.label}`}>
          {badge}
        </button>
      </PopoverTrigger>
      <PopoverSurface>
        <div className={s.evidenceCard}>
          <Body2 className={s.evidenceHead}>{ev.summary}</Body2>
          {ev.detail && ev.detail.length > 0 && (
            <ul className={s.evidenceList}>
              {ev.detail.map((d) => (
                <li key={d}><Caption1>{d}</Caption1></li>
              ))}
            </ul>
          )}
          {ev.people && ev.people.length > 0 && (
            <div>
              <Caption1 className={s.evidenceMuted}>Betroffen</Caption1>
              <div className={s.evidencePeople}>
                {ev.people.map((p) => (
                  <Badge key={p} appearance="outline" color="informative">{p}</Badge>
                ))}
              </div>
            </div>
          )}
          {ev.citations && ev.citations.length > 0 && (
            <Caption1 className={s.evidenceMuted}>{ev.citations.join(' \u00b7 ')}</Caption1>
          )}
        </div>
      </PopoverSurface>
    </Popover>
  );
}

interface RecoPanelProps {
  reco: GroundedReco;
  showBack: boolean;
  onBack: () => void;
  onCta: (cta: RecoCta) => void;
}

export function RecoPanel({ reco, showBack, onBack, onCta }: RecoPanelProps) {
  const s = useStyles();
  const { t } = useTranslation();
  const chip = reco.contextChip;
  const chipText = [chip.subject, ...(chip.qualifiers ?? []), chip.status].filter(Boolean).join(' \u00b7 ');
  return (
    <div className={s.root}>
      {showBack && (
        <Button appearance="subtle" icon={<ArrowLeftRegular />} onClick={onBack}>
          {t('reco.back')}
        </Button>
      )}
      <div className={s.chipRow}>
        <Badge appearance="tint" color={chipBadgeColor(chip.tone)}>{chipText}</Badge>
        {reco.refused && (
          <Badge appearance="filled" color="danger" icon={<ProhibitedRegular />}>
            {t('reco.refused')}
          </Badge>
        )}
      </div>
      <Caption1 className={s.agentLine}>{t('reco.agentLine', { agent: reco.agentLabel })}</Caption1>
      <Body1 className={reco.refused ? s.refusedRead : undefined}>{reco.read}</Body1>
      {reco.metrics && reco.metrics.length > 0 && (
        <div className={s.metrics} data-testid="metric-trio">
          {reco.metrics.map((m, i) => (
            <Fragment key={m.label}>
              {i > 0 && <ArrowRightRegular className={s.metricArrow} aria-hidden />}
              <div className={s.metricCell}>
                {m.tone ? (
                  <Badge appearance="tint" color={impactBadgeColor(m.tone)}>{m.value}</Badge>
                ) : (
                  <Body1 className={s.metricValue}>{m.value}</Body1>
                )}
                <Caption1 className={s.metricLabel}>{m.label}</Caption1>
              </div>
            </Fragment>
          ))}
        </div>
      )}
      {reco.levers.length > 0 && (
        <ul className={s.levers}>
          {reco.levers.map((lv, i) => (
            <li key={lv.text} className={s.lever}>
              <CounterBadge count={i + 1} appearance="filled" color="brand" />
              <Body2 className={s.leverText}>{lv.text}</Body2>
              {lv.impact && <ImpactBadge lever={lv} />}
            </li>
          ))}
        </ul>
      )}
      {reco.primaryCta && (
        <div className={s.ctaWrap}>
          {reco.primaryCta.requiresApproval && !reco.refused && (
            <div className={s.gateRow}>
              <Badge appearance="tint" color="warning" icon={<ShieldTaskRegular />}>
                {t('reco.approvalRequired')}
              </Badge>
            </div>
          )}
          <Button
            appearance={reco.refused ? 'secondary' : 'primary'}
            disabled={reco.refused}
            icon={<CtaIcon kind={reco.primaryCta.kind} requiresApproval={reco.primaryCta.requiresApproval} />}
            iconPosition="after"
            onClick={() => onCta(reco.primaryCta!)}
          >
            {reco.primaryCta.label}
          </Button>
          {reco.primaryCta.requiresApproval && !reco.refused && (
            <Caption1 className={s.gateHint}>{t('reco.approvalHint')}</Caption1>
          )}
        </div>
      )}
      {reco.projection && <Caption1 className={s.projection}>{t('reco.projection', { text: reco.projection })}</Caption1>}
      {reco.citations.length > 0 && (
        <Caption1 className={s.cites} data-testid="citations">{reco.citations.join(' \u00b7 ')}</Caption1>
      )}
    </div>
  );
}
