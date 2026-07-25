import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Badge,
  Body1,
  Button,
  Divider,
  InteractionTag,
  InteractionTagPrimary,
  TagGroup,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { DismissRegular, AddRegular, SendRegular } from '@fluentui/react-icons';
import { CopilotIcon } from '../CopilotIcon';
import { ConversationView } from '../../copilot-drawer/ConversationView';
import { useAgentInvoker } from '../../copilot-drawer/AgentInvoker';
import { useCopilotRail } from '../../copilot-rail/rail-context';
import { RecoPanel } from '../../copilot-rail/RecoPanel';
import type { RecoCta } from '../../copilot-rail/reco';
import { agentForRoute } from './agent-context-map';
import { boardForRoute } from './board-registry';
import { useRoleLens } from '../../context/role-context';

const useStyles = makeStyles({
  fab: {
    position: 'fixed',
    right: '24px',
    bottom: '24px',
    zIndex: 1000,
    boxShadow: tokens.shadow16,
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
  inputBar: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
    marginTop: tokens.spacingVerticalM,
    marginLeft: tokens.spacingHorizontalM,
    marginRight: tokens.spacingHorizontalM,
    marginBottom: tokens.spacingVerticalM,
    paddingTop: tokens.spacingVerticalXS,
    paddingBottom: tokens.spacingVerticalXS,
    paddingLeft: tokens.spacingHorizontalS,
    paddingRight: tokens.spacingHorizontalXS,
    borderRadius: tokens.borderRadiusXLarge,
    border: `1px solid ${tokens.colorNeutralStroke1}`,
    backgroundColor: tokens.colorNeutralBackground1,
    ':focus-within': { boxShadow: `0 0 0 2px ${tokens.colorBrandStroke1}` },
  },
  textInput: {
    flexGrow: 1,
    minWidth: 0,
    border: 'none',
    backgroundColor: 'transparent',
    font: 'inherit',
    fontSize: tokens.fontSizeBase300,
    color: tokens.colorNeutralForeground1,
  },
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
  const { capabilities } = useRoleLens();
  const agent = agentForRoute(loc.pathname);
  const board = boardForRoute(loc.pathname);
  const { turns, busy, send } = useAgentInvoker(agent);
  const { open, setOpen, activeReco, defaultReco, backToDefault, resetReco } = useCopilotRail();
  const [draft, setDraft] = useState('');

  // Reco state is app-global; clear it when leaving a board so one board's
  // grounded recommendation never leaks onto another. Runs on route change
  // (cleanup fires before the next board's async default-reco seed).
  useEffect(() => resetReco, [loc.pathname, resetReco]);

  if (!open) {
    return (
      <Button
        className={s.fab}
        aria-label={t('agent.open', 'Open agent')}
        icon={<CopilotIcon />}
        appearance="primary"
        shape="circular"
        size="large"
        onClick={() => setOpen(true)}
      />
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
          <CopilotIcon />
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
      <div className={s.inputBar}>
        <Button
          appearance="subtle"
          size="small"
          shape="circular"
          icon={<AddRegular />}
          aria-label={t('copilot.add', 'Add')}
        />
        <input
          className={s.textInput}
          value={draft}
          placeholder={t('copilot.placeholder')}
          aria-label={t('copilot.placeholder')}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') submit();
          }}
        />
        <Button
          appearance="subtle"
          size="small"
          shape="circular"
          icon={<SendRegular />}
          aria-label={t('copilot.send')}
          disabled={busy || draft.trim().length === 0}
          onClick={submit}
        />
      </div>
    </aside>
  );
}
