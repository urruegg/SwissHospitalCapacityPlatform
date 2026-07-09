import { makeStyles, tokens, Body1, Caption1, Badge } from '@fluentui/react-components';
import type { ConversationTurn } from './AgentInvoker';

const useStyles = makeStyles({
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
    marginBottom: tokens.spacingVerticalM,
  },
  user: {
    alignSelf: 'flex-end',
    backgroundColor: tokens.colorBrandBackground2,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusMedium,
  },
  agent: {
    alignSelf: 'flex-start',
    backgroundColor: tokens.colorNeutralBackground3,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusMedium,
  },
  citations: { marginTop: tokens.spacingVerticalXS },
});

/** Sprint 13 T6 — renders conversation turns + citation footer per agent reply. */
export function ConversationView({ turns }: { turns: ConversationTurn[] }) {
  const styles = useStyles();
  return (
    <div className={styles.list} data-testid="conversation">
      {turns.map((turn, i) => (
        <div key={i} className={turn.role === 'user' ? styles.user : styles.agent}>
          {turn.refused ? <Badge color="danger">refused</Badge> : null}
          <Body1>{turn.text}</Body1>
          {turn.citations && turn.citations.length > 0 ? (
            <Caption1 className={styles.citations} data-testid="citations">
              Quellen: {turn.citations.join(', ')}
            </Caption1>
          ) : null}
        </div>
      ))}
    </div>
  );
}
