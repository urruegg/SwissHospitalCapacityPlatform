import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Button,
  Badge,
  Body1,
  Input,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { BotRegular, DismissRegular } from '@fluentui/react-icons';
import { ConversationView } from '../../copilot-drawer/ConversationView';
import { useAgentInvoker } from '../../copilot-drawer/AgentInvoker';
import { agentForRoute } from './agent-context-map';
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
 * Sprint 20 M7 — dockable, context-aware Agent plane.
 *
 * Collapsed it is a 48px icon rail; open it is a 360px docked panel that shows
 * the context agent for the active route (see `agentForRoute`), the caller's
 * action-ceiling badge derived from the role lens, and the reused conversation
 * engine (`ConversationView` + `useAgentInvoker`). The conversation UI is
 * embedded inline rather than as an overlay drawer because the plane already
 * owns the right-hand shell column.
 */
export function AgentPlane() {
  const s = useStyles();
  const { t } = useTranslation();
  const loc = useLocation();
  const { capabilities } = useRoleLens();
  const agent = agentForRoute(loc.pathname);
  const { turns, busy, send } = useAgentInvoker(agent);
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState('');

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
