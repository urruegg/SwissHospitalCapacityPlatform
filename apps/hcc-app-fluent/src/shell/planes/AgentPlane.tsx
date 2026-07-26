import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Badge,
  Body1,
  Button,
  Divider,
  Input,
  InteractionTag,
  InteractionTagPrimary,
  TagGroup,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { BotRegular, DismissRegular } from '@fluentui/react-icons';
import { ConversationView } from '../../copilot-drawer/ConversationView';
import { useConversation } from '../../copilot-drawer/useConversation';
import { useCopilotRail } from '../../copilot-rail/rail-context';
import { RecoPanel } from '../../copilot-rail/RecoPanel';
import type { RecoCta } from '../../copilot-rail/reco';
import { agentForRoute } from './agent-context-map';
import { boardForRoute } from './board-registry';
import { useRoleLens } from '../../context/role-context';

const useStyles = makeStyles({
  rail: {
    width: '48px',
    display: 'flex',
    justifyContent: 'center',
    paddingTop: tokens.spacingVerticalM,
    height: '100%',
    borderLeft: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
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
});

/**
 * Sprint 20 M7 — three-state dockable, context-aware Agent plane.
 *
 * Collapsed: 48px icon rail.
 * Open + default reco: shows proactive reco from the board, chips, chat.
 * Open + active reco: shows context reco with back button, chips, chat.
 */
export function AgentPlane() {
  const s = useStyles();
  const { t } = useTranslation();
  const loc = useLocation();
  const { capabilities, userOid } = useRoleLens();
  const agent = agentForRoute(loc.pathname);
  const board = boardForRoute(loc.pathname);
  const { turns, busy, send } = useConversation(agent, userOid);
  const { open, setOpen, activeReco, defaultReco, backToDefault, resetReco } = useCopilotRail();
  const [draft, setDraft] = useState('');

  // Reco state is app-global; clear it when leaving a board so one board's
  // grounded recommendation never leaks onto another. Runs on route change
  // (cleanup fires before the next board's async default-reco seed).
  useEffect(() => resetReco, [loc.pathname, resetReco]);

  if (!open) {
    return (
      <div className={s.rail}>
        <Button
          aria-label={t('agent.open', 'Open agent')}
          icon={<BotRegular />}
          appearance="subtle"
          onClick={() => setOpen(true)}
        />
      </div>
    );
  }

  const submit = () => {
    void send(draft);
    setDraft('');
  };

  const onCta = (_cta: RecoCta) => { /* Parity build: CTA presentational; handoff wiring later. */ };
  const shownReco = activeReco ?? defaultReco;

  return (
    <aside role="complementary" aria-label={t('agent.title', 'Agent')} className={s.panel}>
      <div className={s.header}>
        <div className={s.headTitle}>
          <BotRegular />
          <Body1>{agent}</Body1>
          <Badge appearance="tint">{capabilities.agentCeiling}</Badge>
        </div>
        <Button
          aria-label={t('agent.close', 'Close agent')}
          icon={<DismissRegular />}
          appearance="subtle"
          onClick={() => setOpen(false)}
        />
      </div>
      <div className={s.body}>
        {shownReco && (
          <RecoPanel
            reco={shownReco}
            showBack={activeReco != null}
            onBack={backToDefault}
            onCta={onCta}
          />
        )}
        {board && board.askAbout.length > 0 && (
          <TagGroup className={s.chips} aria-label={t('agent.askAbout', 'Ask about')}>
            {board.askAbout.map((q) => (
              <InteractionTag key={q} value={q}>
                <InteractionTagPrimary onClick={() => void send(q)}>{q}</InteractionTagPrimary>
              </InteractionTag>
            ))}
          </TagGroup>
        )}
        {turns.length > 0 && <Divider />}
        <ConversationView turns={turns} />
      </div>
      <div className={s.inputRow}>
        <Input
          className={s.input}
          value={draft}
          placeholder={t('copilot.placeholder')}
          aria-label={t('copilot.placeholder')}
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
  );
}
