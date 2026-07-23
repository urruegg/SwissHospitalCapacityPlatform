import { useTranslation } from 'react-i18next';
import {
  Badge,
  Body1,
  Body2,
  Button,
  Caption1,
  CounterBadge,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { ArrowLeftRegular, ArrowRightRegular, PlayRegular, OpenRegular } from '@fluentui/react-icons';
import { chipBadgeColor, impactBadgeColor, type GroundedReco, type RecoCta } from './reco';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalS },
  chipRow: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalXS, flexWrap: 'wrap' },
  agentLine: { color: tokens.colorBrandForeground1 },
  levers: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS, margin: 0, padding: 0, listStyle: 'none' },
  lever: { display: 'flex', alignItems: 'flex-start', gap: tokens.spacingHorizontalXS },
  leverText: { flex: 1 },
  projection: { color: tokens.colorNeutralForeground3 },
  cites: { color: tokens.colorNeutralForeground4 },
});

function CtaIcon({ kind }: { kind: RecoCta['kind'] }) {
  if (kind === 'handoff') return <ArrowRightRegular />;
  if (kind === 'action') return <PlayRegular />;
  return <OpenRegular />;
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
      </div>
      <Caption1 className={s.agentLine}>{t('reco.agentLine', { agent: reco.agentLabel })}</Caption1>
      <Body1>{reco.read}</Body1>
      {reco.levers.length > 0 && (
        <ul className={s.levers}>
          {reco.levers.map((lv, i) => (
            <li key={lv.text} className={s.lever}>
              <CounterBadge count={i + 1} appearance="filled" color="brand" />
              <Body2 className={s.leverText}>{lv.text}</Body2>
              {lv.impact && (
                <Badge appearance="tint" color={impactBadgeColor(lv.impact.tone)}>{lv.impact.label}</Badge>
              )}
            </li>
          ))}
        </ul>
      )}
      {reco.primaryCta && (
        <Button
          appearance="primary"
          icon={<CtaIcon kind={reco.primaryCta.kind} />}
          iconPosition="after"
          onClick={() => onCta(reco.primaryCta!)}
        >
          {reco.primaryCta.label}
        </Button>
      )}
      {reco.projection && <Caption1 className={s.projection}>{t('reco.projection', { text: reco.projection })}</Caption1>}
      {reco.citations.length > 0 && <Caption1 className={s.cites}>{reco.citations.join(' \u00b7 ')}</Caption1>}
    </div>
  );
}
