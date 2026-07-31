import { useEffect, useMemo, useRef, useState } from 'react';
import { Body1, Title3, makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import {
  ArrowRightRegular,
  DataTrendingRegular,
  DiamondRegular,
  PeopleCommunityRegular,
  PeopleTeamRegular,
  RocketRegular,
  type FluentIcon,
} from '@fluentui/react-icons';
import { useTranslation } from 'react-i18next';
import {
  IQ_LAYERS,
  type DigitalFeedbackLoopProps,
  type FeedbackLoopDomain,
  type FeedbackLoopDomainId,
  type FeedbackLoopMode,
  type IqLayer,
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
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalL,
  },
  presentation: {
    padding: tokens.spacingHorizontalL,
    borderRadius: tokens.borderRadiusXLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow16,
    '@media screen and (max-width: 900px)': {
      padding: tokens.spacingHorizontalM,
    },
  },
  titlebar: {
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalL,
    flexWrap: 'wrap',
  },
  titleStack: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXXS,
    maxWidth: '680px',
  },
  headline: {
    margin: 0,
    fontSize: tokens.fontSizeBase600,
    lineHeight: tokens.lineHeightBase600,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  subhead: {
    margin: 0,
    fontSize: tokens.fontSizeBase300,
    color: tokens.colorNeutralForeground2,
  },
  legend: {
    display: 'flex',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalL,
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground3,
  },
  legendItem: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
    whiteSpace: 'nowrap',
  },
  legendArrow: {
    position: 'relative',
    width: '26px',
    height: '3px',
    borderRadius: '2px',
    backgroundColor: '#1FA9D6',
    '::after': {
      content: '""',
      position: 'absolute',
      right: '-1px',
      top: '-4px',
      borderTop: '5px solid transparent',
      borderBottom: '5px solid transparent',
      borderLeft: '7px solid #1FA9D6',
    },
  },
  legendArrowAction: {
    backgroundColor: '#17B890',
    '::after': {
      borderLeftColor: '#17B890',
    },
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
  canvas: {
    position: 'relative',
    width: '100%',
    aspectRatio: '1200 / 650',
    overflow: 'hidden',
    '@media screen and (max-width: 900px)': {
      aspectRatio: 'auto',
      display: 'flex',
      flexDirection: 'column',
      gap: tokens.spacingVerticalM,
      padding: 0,
    },
  },
  svg: {
    position: 'absolute',
    inset: 0,
    width: '100%',
    height: '100%',
    zIndex: 1,
    pointerEvents: 'none',
    '@media screen and (max-width: 900px)': {
      display: 'none',
    },
  },
  domainCard: {
    position: 'absolute',
    width: '25%',
    height: '32%',
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    padding: tokens.spacingHorizontalM,
    textAlign: 'left',
    borderRadius: tokens.borderRadiusLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderLeftWidth: '4px',
    backgroundColor: tokens.colorNeutralBackground1,
    color: tokens.colorNeutralForeground1,
    boxShadow: tokens.shadow2,
    zIndex: 3,
    cursor: 'pointer',
    overflow: 'hidden',
    fontFamily: 'inherit',
    transitionProperty: 'box-shadow, transform',
    transitionDuration: tokens.durationNormal,
    ':hover': {
      boxShadow: tokens.shadow4,
      transform: 'translateY(-2px)',
    },
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: '2px',
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '2px',
    },
    '@media screen and (max-width: 900px)': {
      position: 'static',
      width: '100%',
      height: 'auto',
    },
  },
  cornerTopLeft: {
    left: '2.4%',
    top: '4%',
    '@media screen and (max-width: 900px)': { order: 1 },
  },
  cornerTopRight: {
    right: '2.4%',
    top: '4%',
    '@media screen and (max-width: 900px)': { order: 2 },
  },
  cornerBottomLeft: {
    left: '2.4%',
    bottom: '4%',
    '@media screen and (max-width: 900px)': { order: 4 },
  },
  cornerBottomRight: {
    right: '2.4%',
    bottom: '4%',
    '@media screen and (max-width: 900px)': { order: 5 },
  },
  cardActive: {
    boxShadow: tokens.shadow16,
  },
  kicker: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
    color: tokens.colorNeutralForeground3,
    fontSize: '11px',
    fontWeight: tokens.fontWeightBold,
    letterSpacing: '0.06em',
    textTransform: 'uppercase',
  },
  kickerIcon: {
    display: 'grid',
    placeItems: 'center',
    width: '24px',
    height: '24px',
    borderRadius: tokens.borderRadiusSmall,
    backgroundColor: tokens.colorNeutralBackground3,
    color: '#365B7D',
    fontSize: '16px',
  },
  cardTitle: {
    margin: '4px 0 0',
    fontSize: tokens.fontSizeBase400,
    lineHeight: tokens.lineHeightBase300,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  cardMicro: {
    marginBottom: '4px',
    fontSize: '11px',
    color: tokens.colorNeutralForeground3,
  },
  row: {
    display: 'grid',
    gridTemplateColumns: '58px 1fr',
    gap: tokens.spacingHorizontalXS,
    paddingTop: '4px',
    borderTop: `1px solid ${tokens.colorNeutralStroke2}`,
    fontSize: tokens.fontSizeBase200,
    lineHeight: 1.3,
  },
  rowSignalLabel: {
    color: '#117A9F',
    fontSize: '10px',
    fontWeight: tokens.fontWeightBold,
    letterSpacing: '0.04em',
  },
  rowActionLabel: {
    color: '#0B8265',
    fontSize: '10px',
    fontWeight: tokens.fontWeightBold,
    letterSpacing: '0.04em',
  },
  rowOutcomeLabel: {
    color: '#8A6300',
    fontSize: '10px',
    fontWeight: tokens.fontWeightBold,
    letterSpacing: '0.04em',
  },
  rowText: {
    color: tokens.colorNeutralForeground2,
  },
  core: {
    position: 'absolute',
    left: '50%',
    top: '50%',
    transform: 'translate(-50%, -50%)',
    width: '24%',
    aspectRatio: '1 / 1',
    borderRadius: '50%',
    border: `2px solid #365B7D`,
    backgroundColor: tokens.colorNeutralBackground1,
    zIndex: 4,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    textAlign: 'center',
    padding: tokens.spacingHorizontalS,
    boxShadow: tokens.shadow28,
    '@media screen and (max-width: 900px)': {
      position: 'static',
      transform: 'none',
      width: '220px',
      height: '220px',
      alignSelf: 'center',
      order: 3,
    },
  },
  coreTitle: {
    margin: 0,
    fontSize: tokens.fontSizeBase500,
    fontWeight: tokens.fontWeightBold,
    color: tokens.colorNeutralForeground1,
  },
  coreSub: {
    margin: '2px 0 8px',
    fontSize: '11px',
    color: tokens.colorNeutralForeground3,
  },
  iqPills: {
    display: 'flex',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: '4px',
    width: '86%',
  },
  iqPill: {
    padding: '3px 7px',
    borderRadius: tokens.borderRadiusCircular,
    backgroundColor: tokens.colorNeutralBackground3,
    color: tokens.colorNeutralForeground3,
    fontSize: '10px',
    fontWeight: tokens.fontWeightBold,
    letterSpacing: '0.02em',
    textTransform: 'uppercase',
    transitionProperty: 'background-color, color',
    transitionDuration: tokens.durationFaster,
  },
  iqPillOn: {
    backgroundColor: '#365B7D',
    color: '#FFFFFF',
  },
  hitl: {
    marginTop: '8px',
    padding: '5px 10px',
    borderRadius: tokens.borderRadiusMedium,
    backgroundColor: 'rgba(232, 162, 0, 0.16)',
    color: '#8A6300',
    fontSize: '11px',
    fontWeight: tokens.fontWeightBold,
    display: 'inline-flex',
    alignItems: 'center',
    gap: '4px',
  },
  hitlDiamond: {
    color: '#E8A200',
    fontSize: '14px',
    display: 'inline-flex',
    alignItems: 'center',
  },
  journey: {
    position: 'absolute',
    left: '10%',
    right: '10%',
    bottom: '2.6%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '5px',
    zIndex: 5,
    fontSize: '11px',
    color: tokens.colorNeutralForeground3,
    '@media screen and (max-width: 900px)': {
      display: 'none',
    },
  },
  step: {
    padding: '3px 6px',
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderRadius: tokens.borderRadiusSmall,
    backgroundColor: tokens.colorNeutralBackground1,
    whiteSpace: 'nowrap',
  },
  stepNum: {
    color: tokens.colorNeutralForeground1,
    fontWeight: tokens.fontWeightBold,
  },
  chevron: {
    color: '#0B8265',
    fontWeight: tokens.fontWeightBold,
    fontSize: '16px',
    display: 'inline-flex',
    alignItems: 'center',
  },
  footer: {
    display: 'flex',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalL,
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground3,
  },
  footerStrong: {
    color: tokens.colorNeutralForeground1,
    fontWeight: tokens.fontWeightSemibold,
  },
  note: {
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusMedium,
    borderLeft: `3px solid #1FA9D6`,
    backgroundColor: tokens.colorNeutralBackground2,
    color: tokens.colorNeutralForeground2,
    fontSize: tokens.fontSizeBase200,
    lineHeight: 1.4,
  },
  noteStrong: {
    color: tokens.colorNeutralForeground1,
    fontWeight: tokens.fontWeightSemibold,
  },
  pathSignal: {
    fill: 'none',
    stroke: '#1FA9D6',
    strokeWidth: 4,
  },
  pathAction: {
    fill: 'none',
    stroke: '#17B890',
    strokeWidth: 4,
  },
  pathReturn: {
    fill: 'none',
    stroke: '#E8A200',
    strokeWidth: 2,
    strokeDasharray: '5 7',
    opacity: 0.7,
  },
  pathDim: {
    opacity: 0.14,
  },
  labelRect: {
    fill: tokens.colorNeutralBackground1,
    stroke: tokens.colorNeutralStroke2,
  },
  labelSignalText: {
    fill: '#117A9F',
    fontSize: '13px',
    fontWeight: tokens.fontWeightBold,
    letterSpacing: '0.5px',
  },
  labelActionText: {
    fill: '#0B8265',
    fontSize: '13px',
    fontWeight: tokens.fontWeightBold,
    letterSpacing: '0.5px',
  },
  pulse: {
    transformOrigin: 'center',
    transformBox: 'fill-box',
    animationDuration: '2400ms',
    animationIterationCount: 'infinite',
    animationTimingFunction: 'ease-in-out',
    animationName: {
      '0%': { transform: 'scale(0.82)', opacity: 0.45 },
      '50%': { transform: 'scale(1.28)', opacity: 1 },
      '100%': { transform: 'scale(0.82)', opacity: 0.45 },
    },
    '@media (prefers-reduced-motion: reduce)': {
      animationName: 'none',
    },
  },
  pulsePaused: {
    animationName: 'none',
    opacity: 0.72,
  },
  pulseInactive: {
    opacity: 0.12,
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

interface DomainGeometry {
  icon: FluentIcon;
  accent: string;
  corner: 'cornerTopLeft' | 'cornerTopRight' | 'cornerBottomLeft' | 'cornerBottomRight';
  signalPath: string;
  actionPath: string;
  returnPath: string;
  signalLabel: { x: number; y: number };
  actionLabel: { x: number; y: number };
  signalDot: { x: number; y: number };
  actionDot: { x: number; y: number };
}

const DOMAIN_META: Record<FeedbackLoopDomainId, DomainGeometry> = {
  'care-ecosystem': {
    icon: PeopleCommunityRegular,
    accent: '#17B890',
    corner: 'cornerTopLeft',
    signalPath: 'M330 144 C400 154 430 225 490 266',
    actionPath: 'M488 322 C430 286 405 205 330 195',
    returnPath: 'M496 238 C445 113 370 85 332 99',
    signalLabel: { x: 382, y: 151 },
    actionLabel: { x: 371, y: 218 },
    signalDot: { x: 455, y: 243 },
    actionDot: { x: 452, y: 300 },
  },
  'command-center': {
    icon: DataTrendingRegular,
    accent: '#1FA9D6',
    corner: 'cornerTopRight',
    signalPath: 'M870 144 C800 154 770 225 710 266',
    actionPath: 'M712 322 C770 286 795 205 870 195',
    returnPath: 'M704 238 C755 113 830 85 868 99',
    signalLabel: { x: 756, y: 151 },
    actionLabel: { x: 765, y: 218 },
    signalDot: { x: 745, y: 243 },
    actionDot: { x: 748, y: 300 },
  },
  'frontier-workforce': {
    icon: PeopleTeamRegular,
    accent: '#5A6CF0',
    corner: 'cornerBottomLeft',
    signalPath: 'M330 506 C400 496 430 425 490 384',
    actionPath: 'M488 328 C430 364 405 445 330 455',
    returnPath: 'M496 412 C445 537 370 565 332 551',
    signalLabel: { x: 382, y: 477 },
    actionLabel: { x: 371, y: 410 },
    signalDot: { x: 455, y: 407 },
    actionDot: { x: 452, y: 350 },
  },
  'care-innovation': {
    icon: RocketRegular,
    accent: '#365B7D',
    corner: 'cornerBottomRight',
    signalPath: 'M870 506 C800 496 770 425 710 384',
    actionPath: 'M712 328 C770 364 795 445 870 455',
    returnPath: 'M704 412 C755 537 830 565 868 551',
    signalLabel: { x: 756, y: 477 },
    actionLabel: { x: 765, y: 410 },
    signalDot: { x: 745, y: 407 },
    actionDot: { x: 748, y: 350 },
  },
};

const DEFAULT_GROUP: Record<FeedbackLoopDomainId, string> = {
  'care-ecosystem': 'Care ecosystem',
  'command-center': 'Command center',
  'frontier-workforce': 'Frontier workforce',
  'care-innovation': 'Care innovation',
};

const DOMAIN_SIGNAL_DEFAULT: Record<FeedbackLoopDomainId, string> = {
  'care-ecosystem': 'Referral demand · partner capacity · experience feedback',
  'command-center': 'Occupancy · 72h demand · ED arrivals · trusted hazards',
  'frontier-workforce': 'Staffing · workload · skills · certifications',
  'care-innovation': 'Outcomes · pathway gaps · agent and service telemetry',
};

const DOMAIN_ACTION_DEFAULT: Record<FeedbackLoopDomainId, string> = {
  'care-ecosystem': 'Coordinate placement · connect the next care setting',
  'command-center': 'Rebalance beds · prepare scenario · coordinate discharge',
  'frontier-workforce': 'Balance roster · mobilize qualified capacity',
  'care-innovation': 'Improve pathway · knowledge · agent guidance',
};

const DOMAIN_LOOPBACK_DEFAULT: Record<FeedbackLoopDomainId, string> = {
  'care-ecosystem': 'Continuity, access and experience become new evidence',
  'command-center': 'Wait time, utilization and avoided delay feed the loop',
  'frontier-workforce': 'Workload, adoption and decision feedback refine support',
  'care-innovation': 'Quality and adoption measurements start the next cycle',
};

const IQ_PILL_LABEL: Record<IqLayer, string> = {
  work: 'Work IQ',
  foundry: 'Foundry IQ',
  fabric: 'Fabric IQ',
  process: 'Process IQ',
  governance: 'Governance IQ',
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
  const mode: FeedbackLoopMode = 'all';
  const playing = true;

  const selectedDomain = useMemo(
    () => domains.find((domain) => domain.id === selectedId) ?? domains[0],
    [domains, selectedId],
  );

  const svgRef = useRef<SVGSVGElement>(null);
  useEffect(() => {
    const svg = svgRef.current;
    if (!svg || typeof svg.pauseAnimations !== 'function') return;
    if (playing && !reducedMotion) svg.unpauseAnimations();
    else svg.pauseAnimations();
  }, [playing, reducedMotion]);

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
      aria-label="Digital feedback loop"
      data-testid="digital-feedback-loop"
    >
      <div
        className={styles.canvas}
        data-testid="feedback-loop-canvas"
        data-stream-mode={mode}
        data-playing={String(playing)}
        data-reduced-motion={String(reducedMotion)}
      >
        <svg
          ref={svgRef}
          className={styles.svg}
          viewBox="0 0 1200 650"
          preserveAspectRatio="none"
          aria-hidden="true"
          focusable="false"
        >
          {domains.map((domain, i) => {
            const geo = DOMAIN_META[domain.id];
            const active = mode === 'all' || domain.id === selectedDomain?.id;
            const dimClass = !active ? styles.pathDim : undefined;
            const sigBegin = `${(-0.4 * i).toFixed(2)}s`;
            const actBegin = `${(1.3 - 0.2 * i).toFixed(2)}s`;
            const retBegin = `${(2.0 - 0.2 * i).toFixed(2)}s`;
            return (
              <g key={domain.id} data-domain-id={domain.id}>
                <path
                  id={`dfl-ret-${domain.id}`}
                  className={mergeClasses(styles.pathReturn, dimClass)}
                  d={geo.returnPath}
                />
                <path
                  id={`dfl-sig-${domain.id}`}
                  className={mergeClasses(styles.pathSignal, dimClass)}
                  d={geo.signalPath}
                />
                <path
                  id={`dfl-act-${domain.id}`}
                  className={mergeClasses(styles.pathAction, dimClass)}
                  d={geo.actionPath}
                />
                <g className={dimClass} transform={`translate(${geo.signalLabel.x} ${geo.signalLabel.y})`}>
                  <rect className={styles.labelRect} width="62" height="22" rx="5" />
                  <text className={styles.labelSignalText} x="9" y="15">
                    SIGNAL
                  </text>
                </g>
                <g className={dimClass} transform={`translate(${geo.actionLabel.x} ${geo.actionLabel.y})`}>
                  <rect className={styles.labelRect} width="64" height="22" rx="5" />
                  <text className={styles.labelActionText} x="8" y="15">
                    ACTION
                  </text>
                </g>
                {!reducedMotion && (
                  <g className={dimClass}>
                    <circle r="5" fill="#1FA9D6">
                      <animateMotion dur="3.2s" repeatCount="indefinite" begin={sigBegin}>
                        <mpath href={`#dfl-sig-${domain.id}`} />
                      </animateMotion>
                    </circle>
                    <rect width="12" height="8" rx="2" fill="#17B890">
                      <animateMotion dur="3.2s" repeatCount="indefinite" begin={actBegin}>
                        <mpath href={`#dfl-act-${domain.id}`} />
                      </animateMotion>
                    </rect>
                    <circle r="4" fill="#E8A200">
                      <animateMotion
                        dur="3.2s"
                        repeatCount="indefinite"
                        begin={retBegin}
                        keyPoints="1;0"
                        keyTimes="0;1"
                        calcMode="linear"
                      >
                        <mpath href={`#dfl-ret-${domain.id}`} />
                      </animateMotion>
                    </circle>
                  </g>
                )}
              </g>
            );
          })}
        </svg>

        {domains.map((domain) => {
          const geo = DOMAIN_META[domain.id];
          const DomainIcon = geo.icon;
          const selected = domain.id === selectedDomain?.id;
          const label = domainLabel(domain, t);
          return (
            <button
              key={domain.id}
              type="button"
              className={mergeClasses(styles.domainCard, styles[geo.corner], selected && styles.cardActive)}
              style={{ borderLeftColor: geo.accent }}
              aria-label={label}
              aria-pressed={selected}
              data-domain-id={domain.id}
              onClick={() => handleDomainSelect(domain)}
            >
              <span className={styles.kicker}>
                <span className={styles.kickerIcon} aria-hidden="true" style={{ color: geo.accent }}>
                  <DomainIcon />
                </span>
                {t(domain.groupLabelKey, DEFAULT_GROUP[domain.id])}
              </span>
              <span className={styles.cardTitle}>{label}</span>
              <span className={styles.cardMicro}>{microsoftLabel(domain, t)}</span>
              <span className={styles.row}>
                <span className={styles.rowSignalLabel}>SIGNAL</span>
                <span className={styles.rowText}>
                  {t(
                    `backstage.story.feedbackLoop.domain.${domain.id}.signalText`,
                    DOMAIN_SIGNAL_DEFAULT[domain.id],
                  )}
                </span>
              </span>
              <span className={styles.row}>
                <span className={styles.rowActionLabel}>ACTION</span>
                <span className={styles.rowText}>
                  {t(
                    `backstage.story.feedbackLoop.domain.${domain.id}.actionText`,
                    DOMAIN_ACTION_DEFAULT[domain.id],
                  )}
                </span>
              </span>
              <span className={styles.row}>
                <span className={styles.rowOutcomeLabel}>OUTCOME</span>
                <span className={styles.rowText}>
                  {t(
                    `backstage.story.feedbackLoop.domain.${domain.id}.loopBack`,
                    DOMAIN_LOOPBACK_DEFAULT[domain.id],
                  )}
                </span>
              </span>
            </button>
          );
        })}

        <section
          className={styles.core}
          data-testid="feedback-loop-core"
          aria-label={t('backstage.story.feedbackLoop.iqCore.caption', 'Microsoft IQ core')}
        >
          <p className={styles.coreTitle}>{t('backstage.story.feedbackLoop.iqCore.name', 'Microsoft IQ')}</p>
          <p className={styles.coreSub}>
            {t('backstage.story.feedbackLoop.iqCore.sub', 'data \u00b7 knowledge \u00b7 context \u00b7 decisions')}
          </p>
          <div className={styles.iqPills} aria-label="Active IQ layers">
            {IQ_LAYERS.map((layer) => {
              const on = activeLayers.includes(layer);
              return (
                <span key={layer} className={mergeClasses(styles.iqPill, on && styles.iqPillOn)}>
                  {t(`backstage.story.feedbackLoop.iq.${layer}`, IQ_PILL_LABEL[layer])}
                </span>
              );
            })}
          </div>
          <div className={styles.hitl}>
            <span className={styles.hitlDiamond} aria-hidden="true">
              <DiamondRegular />
            </span>
            {t('backstage.story.feedbackLoop.iqCore.hitl', 'Human approval before action')}
          </div>
        </section>

        <div className={styles.journey} aria-hidden="true">
          <span className={styles.step}>{t('backstage.story.feedbackLoop.journey.dataPoints', 'Data points')}</span>
          <span className={styles.chevron}><ArrowRightRegular /></span>
          <span className={styles.step}>{t('backstage.story.feedbackLoop.journey.iq', 'Microsoft IQ')}</span>
          <span className={styles.chevron}><ArrowRightRegular /></span>
          <span className={styles.step}>{t('backstage.story.feedbackLoop.journey.actionPacket', 'Action packet')}</span>
          <span className={styles.chevron}><ArrowRightRegular /></span>
          <span className={styles.step}>{t('backstage.story.feedbackLoop.journey.approval', 'Human approval')}</span>
          <span className={styles.chevron}><ArrowRightRegular /></span>
          <span className={styles.step}>{t('backstage.story.feedbackLoop.journey.outcome', 'Measured outcome')}</span>
        </div>
      </div>

      <div className={styles.note}>
        <span className={styles.noteStrong}>
          {t('backstage.story.feedbackLoop.note.label', 'Animation behaviour:')}
        </span>{' '}
        {t(
          'backstage.story.feedbackLoop.note.body',
          'cyan circles are incoming signal observations; the green packet is a proposed action leaving Microsoft IQ; the amber point returns the measured outcome. Motion stops when you pause or request reduced motion.',
        )}
      </div>
    </section>
  );
}
