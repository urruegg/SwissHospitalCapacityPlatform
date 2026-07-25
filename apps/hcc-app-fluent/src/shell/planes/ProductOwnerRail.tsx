import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Badge,
  Body1,
  Body2,
  Button,
  Caption1,
  Divider,
  Dropdown,
  Input,
  InteractionTag,
  InteractionTagPrimary,
  Option,
  TagGroup,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { BotRegular } from '@fluentui/react-icons';
import { ConversationView } from '../../copilot-drawer/ConversationView';
import { useAgentInvoker, type ConversationTurn } from '../../copilot-drawer/AgentInvoker';
import { RecoPanel } from '../../copilot-rail/RecoPanel';
import { useCopilotRail } from '../../copilot-rail/rail-context';
import type { GroundedReco, RecoCta } from '../../copilot-rail/reco';
import { useRoleLens } from '../../context/role-context';

type ProductOwnerSurface = 'start' | 'backstage';
type GroundedStatus = 'verified' | 'partial' | 'requires-validation';
type GroundedLanguage = 'de' | 'en';

interface GroundedChunk {
  classId: 'A' | 'B' | 'C' | 'D';
  text: string;
  citation: {
    sourceRef: string;
    anchor?: string;
    conceptRef?: string;
    goldBinding?: string;
  };
  asOf: string;
  liveness: 'live' | 'snapshot';
  status: GroundedStatus;
  confidence: number;
  language: GroundedLanguage;
}

type GroundedTurn = ConversationTurn & {
  status?: GroundedStatus;
  confidence?: number;
  chunks?: GroundedChunk[];
  language?: GroundedLanguage;
};

const useStyles = makeStyles({
  host: {
    height: '100%',
  },
  panel: {
    width: '360px',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    borderLeft: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalS,
    padding: tokens.spacingHorizontalM,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  headTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
    minWidth: 0,
  },
  headerActions: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
  },
  lang: {
    minWidth: '78px',
  },
  body: {
    flex: 1,
    overflow: 'auto',
    padding: tokens.spacingHorizontalM,
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
  chips: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalXS,
  },
  inputRow: {
    display: 'flex',
    gap: tokens.spacingHorizontalS,
    padding: tokens.spacingHorizontalM,
    borderTop: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  input: { flex: 1 },
  answerCard: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusMedium,
    backgroundColor: tokens.colorNeutralBackground3,
  },
  answerMeta: {
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
  },
  citations: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXXS,
    color: tokens.colorNeutralForeground3,
  },
});

const ASK_ABOUT = [
  'poRail.ask.sprint28',
  'poRail.ask.evidence',
  'poRail.ask.partner',
  'poRail.ask.language',
] as const;

const INTERNAL_ASK_ABOUT = ['poRail.ask.costSecurity'] as const;

function statusColor(status: GroundedStatus): 'success' | 'warning' | 'danger' {
  if (status === 'verified') return 'success';
  if (status === 'partial') return 'warning';
  return 'danger';
}

function pct(confidence: number | undefined): string {
  return `${Math.round((confidence ?? 0) * 100)}%`;
}

function productOwnerReco(t: ReturnType<typeof useTranslation>['t'], partnerScoped: boolean): GroundedReco {
  const levers = [
    {
      text: t(
        'poRail.default.leverCitations',
        'Every answer stays tied to class A/B/C/D grounded chunks and sourceRef citations.',
      ),
      impact: { label: t('poRail.default.impactGrounded', 'grounded'), tone: 'trust' as const },
    },
    {
      text: t(
        'poRail.default.leverLanguage',
        'Switch DE/EN in the rail to ask the same product question in either language.',
      ),
      impact: { label: t('poRail.default.impactLanguage', 'DE/EN'), tone: 'status' as const },
    },
  ];

  if (!partnerScoped) {
    levers.push({
      text: t(
        'poRail.default.leverInternal',
        'Internal cost/security detail remains available only to entitled Curavias roles.',
      ),
      impact: { label: t('poRail.default.impactEntitlement', 'entitlement'), tone: 'trust' as const },
    });
  }

  return {
    agentLabel: t('poRail.agentLabel', 'Product Owner Agent'),
    contextChip: {
      subject: t('poRail.default.subject', 'PO Agent'),
      qualifiers: [partnerScoped ? t('poRail.partnerTier', 'Partner tier') : t('poRail.internalTier', 'Internal tier')],
      status: t('poRail.default.status', 'READY'),
      tone: 'signal',
    },
    read: partnerScoped
      ? t(
          'poRail.default.partnerRead',
          'Source-grounded product guidance is ready for partner-safe Curavias questions.',
        )
      : t(
          'poRail.default.read',
          'Source-grounded product guidance is ready across START and BACKSTAGE.',
        ),
    levers,
    primaryCta: {
      label: t('poRail.default.cta', 'Ask what changed for Sprint 28'),
      kind: 'action',
      target: t('poRail.ask.sprint28', 'What changed for Sprint 28 and which evidence supports it?'),
    },
    citations: ['FR-POA-002', 'FR-POA-008', 'FR-POA-009'],
    provenance: 'simulated',
  };
}

function citationRefs(turn: GroundedTurn): string[] {
  const chunkRefs = turn.chunks?.map((chunk) => chunk.citation.sourceRef) ?? [];
  return Array.from(new Set([...chunkRefs, ...(turn.citations ?? [])].filter(Boolean)));
}

function AnswerCards({ turns }: { turns: GroundedTurn[] }) {
  const s = useStyles();
  const { t } = useTranslation();
  const agentTurns = turns.filter((turn) => turn.role === 'agent');

  return (
    <>
      {agentTurns.map((turn, index) => {
        const status = turn.status ?? (turn.refused ? 'requires-validation' : 'verified');
        const refs = citationRefs(turn);
        return (
          <div
            key={`${turn.text}-${index}`}
            className={s.answerCard}
            data-testid={`product-owner-answer-card-${index}`}
          >
            <div className={s.answerMeta}>
              <Badge appearance="tint" color={statusColor(status)}>
                {t(`poRail.status.${status}`, status)}
              </Badge>
              <Caption1>
                {t('poRail.confidence', {
                  value: pct(turn.confidence),
                  defaultValue: 'Confidence {{value}}',
                })}
              </Caption1>
              {turn.chunks?.some((chunk) => chunk.liveness === 'snapshot') && (
                <Badge appearance="tint" color="warning">
                  {t('poRail.snapshot', 'snapshot')}
                </Badge>
              )}
            </div>
            {refs.length > 0 && (
              <div className={s.citations}>
                <Caption1>{t('poRail.citations', 'Citations')}</Caption1>
                {refs.map((ref) => (
                  <Caption1 key={ref}>{ref}</Caption1>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </>
  );
}

export function ProductOwnerRail({
  surface,
  partnerScoped = false,
}: {
  surface: ProductOwnerSurface;
  partnerScoped?: boolean;
}) {
  const s = useStyles();
  const { t, i18n } = useTranslation();
  const { capabilities } = useRoleLens();
  const { turns, busy, send } = useAgentInvoker('product-owner');
  const { activeReco, defaultReco, backToDefault, showDefault } = useCopilotRail();
  const [draft, setDraft] = useState('');
  const fallbackReco = useMemo(() => productOwnerReco(t, partnerScoped), [t, partnerScoped]);

  useEffect(() => {
    showDefault(fallbackReco);
  }, [fallbackReco, showDefault]);

  const submit = () => {
    void send(draft);
    setDraft('');
  };

  const onCta = (cta: RecoCta) => {
    void send(cta.target ?? cta.label);
  };

  const askKeys = partnerScoped ? ASK_ABOUT : [...ASK_ABOUT, ...INTERNAL_ASK_ABOUT];
  const groundedTurns = turns as GroundedTurn[];
  const shownReco = activeReco ?? defaultReco ?? fallbackReco;

  return (
    <div className={s.host} data-testid="product-owner-rail" data-layout="docked-full-height">
      <aside
        role="complementary"
        aria-label={t('poRail.title', 'Product Owner Agent')}
        className={s.panel}
        data-surface={surface}
      >
        <div className={s.header}>
          <div className={s.headTitle}>
            <BotRegular />
            <Body1>{t('poRail.title', 'Product Owner Agent')}</Body1>
            <Badge appearance="tint">{capabilities.agentCeiling}</Badge>
            {partnerScoped && <Badge appearance="tint">{t('poRail.partnerTier', 'Partner tier')}</Badge>}
          </div>
          <div className={s.headerActions}>
            <Caption1>{t('poRail.language', 'Language')}</Caption1>
            <Dropdown
              className={s.lang}
              aria-label={t('poRail.language', 'Language')}
              value={i18n.language.startsWith('de') ? 'DE' : 'EN'}
              selectedOptions={[i18n.language.startsWith('de') ? 'de' : 'en']}
              onOptionSelect={(_e, data) => {
                if (data.optionValue) void i18n.changeLanguage(data.optionValue);
              }}
            >
              <Option value="de">DE</Option>
              <Option value="en">EN</Option>
            </Dropdown>
          </div>
        </div>
        <div className={s.body}>
          <RecoPanel
            reco={shownReco}
            showBack={activeReco != null}
            onBack={backToDefault}
            onCta={onCta}
          />
          <TagGroup className={s.chips} aria-label={t('poRail.askAbout', 'Ask about')}>
            {askKeys.map((key) => {
              const question = t(key);
              return (
                <InteractionTag key={key} value={question}>
                  <InteractionTagPrimary onClick={() => void send(question)}>{question}</InteractionTagPrimary>
                </InteractionTag>
              );
            })}
          </TagGroup>
          {groundedTurns.length > 0 && <Divider />}
          <ConversationView turns={turns} />
          <AnswerCards turns={groundedTurns} />
          {groundedTurns.length === 0 && (
            <Body2>
              {t(
                'poRail.emptyGuard',
                'Ask a product question or start from a suggested prompt; the rail is ready.',
              )}
            </Body2>
          )}
        </div>
        <div className={s.inputRow}>
          <Input
            className={s.input}
            value={draft}
            placeholder={t('poRail.placeholder', 'Ask the Product Owner Agent')}
            aria-label={t('poRail.placeholder', 'Ask the Product Owner Agent')}
            onChange={(_e, data) => setDraft(data.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') submit();
            }}
          />
          <Button appearance="primary" disabled={busy} onClick={submit}>
            {t('copilot.send')}
          </Button>
        </div>
      </aside>
    </div>
  );
}
