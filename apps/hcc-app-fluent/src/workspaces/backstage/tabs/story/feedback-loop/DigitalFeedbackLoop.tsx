import { useEffect, useMemo, useState } from 'react';
import {
  Badge,
  Body1,
  Button,
  Caption1,
  Title3,
  Tooltip,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import { PauseRegular, PlayRegular } from '@fluentui/react-icons';
import { useTranslation } from 'react-i18next';
import type {
  DigitalFeedbackLoopProps,
  FeedbackLoopDomain,
  FeedbackLoopDomainId,
  FeedbackLoopMode,
} from './feedback-loop-model';

const DEFAULT_LABELS: Record<FeedbackLoopDomainId, string> = {
  'care-ecosystem': 'Engage care network',
  'command-center': 'Optimize patient flow',
  'frontier-workforce': 'Empower care teams',
  'care-innovation': 'Transform care delivery',
};

const DEFAULT_MICROSOFT_LABELS: Record<FeedbackLoopDomainId, string> = {
  'care-ecosystem': 'Engage customers',
  'command-center': 'Optimize operations',
  'frontier-workforce': 'Empower employees',
  'care-innovation': 'Transform products',
};

const useStyles = makeStyles({
  root: {
    display: 'grid',
    gridTemplateColumns: 'minmax(220px, 280px) minmax(360px, 1fr) minmax(220px, 280px)',
    gridTemplateRows: 'auto 1fr auto',
    gap: tokens.spacingHorizontalL,
    minHeight: '560px',
    padding: tokens.spacingHorizontalL,
    borderRadius: tokens.borderRadiusXLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow4,
    // A11y — the selected (primary/brand) domain button paints its secondary
    // Microsoft-vocabulary caption over the brand fill. `colorNeutralForeground3`
    // (grey) fails WCAG 2.1 AA contrast on that fill, so pin the caption on any
    // pressed control to near-black. Baked into the reusable component so every
    // embedding (Backstage + standalone presentation) inherits the fix.
    '& [aria-pressed="true"] .fui-Caption1': {
      color: '#0E0F11',
    },
    '@media screen and (max-width: 860px)': {
      gridTemplateColumns: '1fr',
      gridTemplateRows: 'auto auto auto auto',
      padding: tokens.spacingHorizontalM,
    },
  },
  presentation: {
    minHeight: '680px',
  },
  header: {
    gridColumnStart: 1,
    gridColumnEnd: 4,
    display: 'flex',
    alignItems: 'start',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalM,
    '@media screen and (max-width: 860px)': {
      gridColumnStart: 1,
      gridColumnEnd: 2,
      flexDirection: 'column',
    },
  },
  heading: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    maxWidth: '720px',
  },
  controls: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
  },
  modeGroup: {
    display: 'inline-flex',
    gap: tokens.spacingHorizontalXS,
    padding: tokens.spacingHorizontalXXS,
    borderRadius: tokens.borderRadiusLarge,
    backgroundColor: tokens.colorNeutralBackground3,
  },
  domainList: {
    display: 'grid',
    gridTemplateColumns: '1fr',
    gap: tokens.spacingVerticalS,
    alignContent: 'center',
    minWidth: 0,
    '@media screen and (max-width: 860px)': {
      order: 3,
    },
  },
  domainButton: {
    width: '100%',
    minHeight: '92px',
    justifyContent: 'flex-start',
    whiteSpace: 'normal',
  },
  domainButtonInner: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    gap: tokens.spacingVerticalXXS,
    textAlign: 'left',
  },
  microsoftLabel: {
    color: tokens.colorNeutralForeground3,
  },
  selectedBadge: {
    marginTop: tokens.spacingVerticalXXS,
  },
  canvas: {
    position: 'relative',
    display: 'grid',
    gridTemplateColumns: '1fr',
    gridTemplateRows: 'auto 1fr auto',
    alignItems: 'center',
    justifyItems: 'center',
    minHeight: '420px',
    aspectRatio: '1.45 / 1',
    borderRadius: tokens.borderRadiusXLarge,
    overflow: 'hidden',
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundImage: `radial-gradient(${tokens.colorNeutralStroke2} 1px, transparent 1px)`,
    backgroundSize: '22px 22px',
    '@media screen and (max-width: 860px)': {
      order: 2,
      minHeight: '360px',
      aspectRatio: '1 / 1',
    },
  },
  svg: {
    position: 'absolute',
    inset: 0,
    width: '100%',
    height: '100%',
  },
  core: {
    zIndex: 1,
    width: 'min(64%, 360px)',
    minHeight: '190px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: tokens.spacingVerticalS,
    padding: tokens.spacingHorizontalL,
    borderRadius: '999px',
    border: `2px solid #365B7D`,
    backgroundColor: 'rgba(255,255,255,0.92)',
    boxShadow: tokens.shadow16,
    textAlign: 'center',
    '@media screen and (max-width: 860px)': {
      width: 'min(88%, 360px)',
      order: 1,
    },
  },
  iqBadges: {
    display: 'flex',
    justifyContent: 'center',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalXS,
  },
  legend: {
    gridColumnStart: 1,
    gridColumnEnd: 4,
    display: 'grid',
    gridTemplateColumns: 'repeat(3, minmax(160px, 1fr))',
    gap: tokens.spacingHorizontalS,
    '@media screen and (max-width: 860px)': {
      gridColumnStart: 1,
      gridColumnEnd: 2,
      gridTemplateColumns: '1fr',
      order: 4,
    },
  },
  legendItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXXS,
    minHeight: '70px',
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusLarge,
    backgroundColor: tokens.colorNeutralBackground2,
  },
  legendSignal: {
    color: '#1FA9D6',
  },
  legendAction: {
    color: '#107C64',
  },
  legendOutcome: {
    color: '#946200',
  },
  rail: {
    fill: 'none',
    strokeWidth: 2.4,
    strokeLinecap: 'round',
    opacity: 0.78,
  },
  inbound: {
    stroke: '#1FA9D6',
  },
  outbound: {
    stroke: '#17B890',
  },
  returnPath: {
    stroke: '#E8A200',
    strokeDasharray: '6 8',
  },
  marker: {
    transitionProperty: 'opacity, transform',
    transitionDuration: tokens.durationNormal,
    opacity: 0.45,
    animationDuration: '2400ms',
    animationIterationCount: 'infinite',
    animationTimingFunction: 'ease-in-out',
    animationName: {
      '0%': { transform: 'scale(0.88)', opacity: 0.35 },
      '50%': { transform: 'scale(1.18)', opacity: 1 },
      '100%': { transform: 'scale(0.88)', opacity: 0.35 },
    },
    '@media (prefers-reduced-motion: reduce)': {
      animationName: 'none',
      transform: 'none',
    },
  },
  markerPaused: {
    animationName: 'none',
    opacity: 0.62,
  },
  markerInactive: {
    opacity: 0.16,
  },
  empty: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalS,
    minHeight: '220px',
    padding: tokens.spacingHorizontalL,
    borderRadius: tokens.borderRadiusLarge,
    border: `1px dashed ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground2,
  },
});

type DomainPosition = {
  anchor: { x: number; y: number };
  inbound: string;
  outbound: string;
  returnPath: string;
  signal: { x: number; y: number };
  action: { x: number; y: number };
  outcome: { x: number; y: number };
};

const DOMAIN_POSITIONS: Record<FeedbackLoopDomainId, DomainPosition> = {
  'care-ecosystem': {
    anchor: { x: 16, y: 26 },
    inbound: 'M 16 26 C 28 18, 38 20, 50 38',
    outbound: 'M 52 42 C 40 30, 28 28, 16 26',
    returnPath: 'M 16 26 C 30 9, 55 11, 72 28',
    signal: { x: 34, y: 25 },
    action: { x: 40, y: 34 },
    outcome: { x: 58, y: 18 },
  },
  'command-center': {
    anchor: { x: 84, y: 26 },
    inbound: 'M 84 26 C 72 18, 62 20, 50 38',
    outbound: 'M 48 42 C 60 30, 72 28, 84 26',
    returnPath: 'M 84 26 C 70 9, 45 11, 28 28',
    signal: { x: 66, y: 25 },
    action: { x: 60, y: 34 },
    outcome: { x: 42, y: 18 },
  },
  'frontier-workforce': {
    anchor: { x: 16, y: 74 },
    inbound: 'M 16 74 C 28 82, 38 80, 50 62',
    outbound: 'M 52 58 C 40 70, 28 72, 16 74',
    returnPath: 'M 16 74 C 30 91, 55 89, 72 72',
    signal: { x: 34, y: 75 },
    action: { x: 40, y: 66 },
    outcome: { x: 58, y: 82 },
  },
  'care-innovation': {
    anchor: { x: 84, y: 74 },
    inbound: 'M 84 74 C 72 82, 62 80, 50 62',
    outbound: 'M 48 58 C 60 70, 72 72, 84 74',
    returnPath: 'M 84 74 C 70 91, 45 89, 28 72',
    signal: { x: 66, y: 75 },
    action: { x: 60, y: 66 },
    outcome: { x: 42, y: 82 },
  },
};

function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
      return undefined;
    }

    const query = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReduced(query.matches);
    const handleChange = (event: MediaQueryListEvent) => setReduced(event.matches);
    query.addEventListener?.('change', handleChange);
    return () => query.removeEventListener?.('change', handleChange);
  }, []);

  return reduced;
}

function domainLabel(domain: FeedbackLoopDomain, t: ReturnType<typeof useTranslation>['t']) {
  return t(domain.curaviasLabelKey, DEFAULT_LABELS[domain.id]);
}

function microsoftLabel(domain: FeedbackLoopDomain, t: ReturnType<typeof useTranslation>['t']) {
  return t(domain.microsoftLabelKey, DEFAULT_MICROSOFT_LABELS[domain.id]);
}

export function DigitalFeedbackLoop({
  domains,
  onDomainSelect,
  presentationMode = false,
}: DigitalFeedbackLoopProps) {
  const styles = useStyles();
  const { t } = useTranslation();
  const reducedMotion = useReducedMotion();
  const [selectedId, setSelectedId] = useState<FeedbackLoopDomainId>('command-center');
  const [mode, setMode] = useState<FeedbackLoopMode>('all');
  const [playing, setPlaying] = useState(true);

  const selectedDomain = useMemo(
    () => domains.find((domain) => domain.id === selectedId) ?? domains[0],
    [domains, selectedId],
  );

  if (domains.length === 0) {
    return (
      <section className={styles.empty} aria-labelledby="feedback-loop-empty-title">
        <Title3 id="feedback-loop-empty-title">
          {t('backstage.story.feedbackLoop.empty.title', 'Digital feedback loop unavailable')}
        </Title3>
        <Body1>
          {t(
            'backstage.story.feedbackLoop.empty.body',
            'No feedback-loop domains are configured for this presentation.',
          )}
        </Body1>
      </section>
    );
  }

  const handleDomainSelect = (domain: FeedbackLoopDomain) => {
    setSelectedId(domain.id);
    onDomainSelect?.(domain);
  };

  const activeLayers = selectedDomain?.iqLayers ?? [];

  return (
    <section
      className={mergeClasses(styles.root, presentationMode && styles.presentation)}
      aria-labelledby="digital-feedback-loop-title"
      data-testid="digital-feedback-loop"
    >
      <div className={styles.header}>
        <div className={styles.heading}>
          <Title3 id="digital-feedback-loop-title">
            {t('backstage.story.feedbackLoop.title', 'Digital Feedback Loop')}
          </Title3>
          <Body1 as="p">
            {t(
              'backstage.story.feedbackLoop.purpose',
              'Signals become governed recommendations, return through human decision, and improve the next loop.',
            )}
          </Body1>
        </div>
        <div className={styles.controls}>
          <Badge appearance="tint" color={playing ? 'success' : 'subtle'}>
            {playing
              ? t('backstage.story.feedbackLoop.status.playing', 'Live simulation')
              : t('backstage.story.feedbackLoop.status.paused', 'Simulation paused')}
          </Badge>
          <div className={styles.modeGroup} role="group" aria-label="Feedback loop stream mode">
            <Button
              appearance={mode === 'all' ? 'primary' : 'subtle'}
              aria-pressed={mode === 'all'}
              onClick={() => setMode('all')}
            >
              All loops
            </Button>
            <Button
              appearance={mode === 'selected' ? 'primary' : 'subtle'}
              aria-pressed={mode === 'selected'}
              onClick={() => setMode('selected')}
            >
              Selected domain
            </Button>
          </div>
          <Tooltip content={playing ? 'Pause simulation' : 'Play simulation'} relationship="label">
            <Button
              icon={playing ? <PauseRegular /> : <PlayRegular />}
              aria-label={playing ? 'Pause simulation' : 'Play simulation'}
              onClick={() => setPlaying((value) => !value)}
            />
          </Tooltip>
        </div>
      </div>

      <div className={styles.domainList} aria-label="Curavias feedback-loop domains">
        {domains.map((domain) => {
          const selected = domain.id === selectedDomain?.id;
          const label = domainLabel(domain, t);
          return (
            <Button
              key={domain.id}
              className={styles.domainButton}
              appearance={selected ? 'primary' : 'outline'}
              aria-label={label}
              aria-pressed={selected}
              data-domain-id={domain.id}
              onClick={() => handleDomainSelect(domain)}
            >
              <span className={styles.domainButtonInner}>
                <span>{label}</span>
                <Caption1 className={styles.microsoftLabel}>{microsoftLabel(domain, t)}</Caption1>
                {selected && (
                  <Badge appearance="tint" color="success" size="small" className={styles.selectedBadge}>
                    {t('backstage.story.feedbackLoop.selected', 'Selected')}
                  </Badge>
                )}
              </span>
            </Button>
          );
        })}
      </div>

      <div
        className={styles.canvas}
        data-testid="feedback-loop-canvas"
        data-stream-mode={mode}
        data-playing={String(playing)}
        data-reduced-motion={String(reducedMotion)}
      >
        <svg className={styles.svg} viewBox="0 0 100 100" aria-hidden="true" focusable="false">
          {domains.map((domain) => {
            const position = DOMAIN_POSITIONS[domain.id];
            const active = mode === 'all' || domain.id === selectedDomain?.id;
            const markerClass = mergeClasses(
              styles.marker,
              (!playing || reducedMotion) && styles.markerPaused,
              !active && styles.markerInactive,
            );
            return (
              <g key={domain.id} data-domain-id={domain.id}>
                <path className={mergeClasses(styles.rail, styles.inbound)} d={position.inbound} />
                <path className={mergeClasses(styles.rail, styles.outbound)} d={position.outbound} />
                <path className={mergeClasses(styles.rail, styles.returnPath)} d={position.returnPath} />
                <circle className={markerClass} cx={position.signal.x} cy={position.signal.y} r="1.8" fill="#1FA9D6" />
                <circle className={markerClass} cx={position.action.x} cy={position.action.y} r="2.1" fill="#17B890" />
                <circle className={markerClass} cx={position.outcome.x} cy={position.outcome.y} r="1.8" fill="#E8A200" />
              </g>
            );
          })}
        </svg>

        <div className={styles.core}>
          <Caption1>{t('backstage.story.feedbackLoop.iqCore.caption', 'Microsoft IQ core')}</Caption1>
          <Title3 as="h4">{t('backstage.story.feedbackLoop.iqCore.title', 'Work + Foundry + Fabric + Process + Governance IQ')}</Title3>
          <div className={styles.iqBadges} aria-label="Active IQ layers">
            {['work', 'foundry', 'fabric', 'process', 'governance'].map((layer) => (
              <Badge
                key={layer}
                appearance={activeLayers.includes(layer as never) ? 'filled' : 'outline'}
                color={activeLayers.includes(layer as never) ? 'informative' : 'subtle'}
              >
                {t(`backstage.story.feedbackLoop.iq.${layer}`, `${layer[0].toUpperCase()}${layer.slice(1)} IQ`)}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      <div className={styles.legend} aria-label="Digital feedback-loop legend">
        <div className={styles.legendItem}>
          <Caption1 className={styles.legendSignal}>SIGNAL</Caption1>
          <Body1>{t('backstage.story.feedbackLoop.legend.signal', 'Operational observations flow into Microsoft IQ.')}</Body1>
        </div>
        <div className={styles.legendItem}>
          <Caption1 className={styles.legendAction}>ACTION</Caption1>
          <Body1>{t('backstage.story.feedbackLoop.legend.action', 'A grounded recommendation returns for human approval.')}</Body1>
        </div>
        <div className={styles.legendItem}>
          <Caption1 className={styles.legendOutcome}>OUTCOME</Caption1>
          <Body1>{t('backstage.story.feedbackLoop.legend.outcome', 'Measured outcomes close the loop and improve the next decision.')}</Body1>
        </div>
      </div>
    </section>
  );
}
