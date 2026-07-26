import { useTranslation } from 'react-i18next';
import {
  Badge,
  Body1,
  Body2,
  Caption1,
  Tooltip,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import type { AdmissionEvent } from '../../../../data/roleboard/bed-manager-data';

const useStyles = makeStyles({
  wrap: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS },
  hint: { color: tokens.colorNeutralForeground3 },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    padding: 0,
    margin: 0,
    listStyle: 'none',
  },
  item: {
    display: 'flex',
    gap: tokens.spacingHorizontalS,
    alignItems: 'center',
    padding: `${tokens.spacingVerticalXXS} ${tokens.spacingHorizontalXS}`,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    borderRadius: tokens.borderRadiusSmall,
  },
  clickable: {
    cursor: 'pointer',
    ':hover': { backgroundColor: tokens.colorNeutralBackground1Hover },
    ':focus-visible': { boxShadow: `0 0 0 2px ${tokens.colorStrokeFocus2}` },
  },
  ts: { color: tokens.colorNeutralForeground3, flexShrink: 0 },
  // General pattern: the FIRST COLUMN (here the time) is the hover trigger that
  // reveals the row's detail popup (mirrors the RQ column in the placement worklist).
  tsTrigger: { borderBottom: `1px dotted ${tokens.colorNeutralStroke1}`, cursor: 'help' },
  card: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXXS, maxWidth: '260px' },
  cardHead: { fontWeight: tokens.fontWeightSemibold },
  muted: { color: tokens.colorNeutralForeground3 },
});

interface AdmissionsEventstreamProps {
  admissions: AdmissionEvent[];
  /** Click/Enter routes the event to the Copilot as a steering prompt (with context). */
  onSelectAdmission?: (ev: AdmissionEvent) => void;
}

export function AdmissionsEventstream({ admissions, onSelectAdmission }: AdmissionsEventstreamProps) {
  const s = useStyles();
  const { t } = useTranslation();
  const interactive = Boolean(onSelectAdmission);
  return (
    <div className={s.wrap}>
      <Caption1 className={s.hint}>{t('bmca.stream.hint')}</Caption1>
      <ul className={s.list} aria-label={t('bmca.stream.title')}>
        {admissions.map((ev) => (
          <li
            key={ev.id}
            className={interactive ? mergeClasses(s.item, s.clickable) : s.item}
            role={interactive ? 'button' : undefined}
            tabIndex={interactive ? 0 : undefined}
            aria-label={interactive ? `${ev.message} — ${t('bmca.stream.copilotHint')}` : undefined}
            onClick={interactive ? () => onSelectAdmission!(ev) : undefined}
            onKeyDown={
              interactive
                ? (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onSelectAdmission!(ev);
                    }
                  }
                : undefined
            }
          >
            {/* First column = time = hover trigger for the row's detail popup. */}
            <Tooltip
              withArrow
              positioning="after"
              relationship="description"
              content={
                <div className={s.card}>
                  <Body2 className={s.cardHead}>{ev.ward} · {ev.patient}</Body2>
                  <Caption1>{ev.detail}</Caption1>
                  {interactive && <Caption1 className={s.muted}>{t('bmca.stream.copilotHint')}</Caption1>}
                </div>
              }
            >
              <Caption1 className={mergeClasses(s.ts, s.tsTrigger)}>{ev.ts}</Caption1>
            </Tooltip>
            <Badge appearance="tint" color={ev.kind === 'admit' ? 'informative' : 'success'}>
              {ev.kind}
            </Badge>
            <Body1>{ev.message}</Body1>
          </li>
        ))}
      </ul>
    </div>
  );
}
