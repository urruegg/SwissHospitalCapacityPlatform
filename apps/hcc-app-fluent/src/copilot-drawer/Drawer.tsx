import { useMemo, useState } from 'react';
import {
  Drawer,
  DrawerHeader,
  DrawerHeaderTitle,
  DrawerBody,
  Button,
  Input,
  Caption1,
  tokens,
  makeStyles,
} from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { ConversationView } from './ConversationView';
import { useConversation } from './useConversation';
import { useRoleLens } from '../context/role-context';
import { useDataSource } from '../context/data-source-context';
import { buildEnvelope, type ContextEnvelope } from '../context/context-envelope';
import type { ParsedClaims } from '../auth/claim-parser';

const useStyles = makeStyles({
  inputRow: {
    display: 'flex',
    gap: tokens.spacingHorizontalS,
    marginTop: tokens.spacingVerticalM,
  },
  notice: { marginTop: tokens.spacingVerticalS },
});

interface CopilotDrawerProps {
  agent: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

/** Sprint 13 T6 — right-side Copilot Drawer that invokes one Sprint 11 agent. */
export function CopilotDrawer({ agent, open, onOpenChange }: CopilotDrawerProps) {
  const styles = useStyles();
  const { t } = useTranslation();
  const lens = useRoleLens();
  const { userOid } = lens;
  const { source } = useDataSource();
  // #424 M1 — agent-scoped envelope for this turn: user + role + hospitalScope +
  // dataSource from the lens, agent from the drawer. Seeds the Foundry thread
  // map in the send path when live threads are enabled.
  const env = useMemo<ContextEnvelope>(
    () =>
      buildEnvelope(
        { oid: userOid ?? undefined } as ParsedClaims,
        lens,
        source,
        agent as ContextEnvelope['agent'],
      ),
    [lens, source, agent, userOid],
  );
  const { turns, busy, send, rate } = useConversation(agent, userOid, env);
  const [draft, setDraft] = useState('');

  const submit = () => {
    void send(draft);
    setDraft('');
  };

  return (
    <Drawer
      type="overlay"
      position="end"
      open={open}
      onOpenChange={(_e, data) => onOpenChange(data.open)}
    >
      <DrawerHeader>
        <DrawerHeaderTitle>
          {t('copilot.title')} — {agent}
        </DrawerHeaderTitle>
      </DrawerHeader>
      <DrawerBody>
        <ConversationView turns={turns} onFollowUp={(q) => void send(q)} onRate={rate} />
        <div className={styles.inputRow}>
          <Input
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
        <Caption1 className={styles.notice}>{t('copilot.noPhiNotice')}</Caption1>
      </DrawerBody>
    </Drawer>
  );
}

export { CopilotDrawer as CopilotDrawerComponent };
