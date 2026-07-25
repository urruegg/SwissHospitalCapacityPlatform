import { makeStyles, tokens, Body1, Caption1, Badge } from '@fluentui/react-components';
import type { ConversationTurn } from './AgentInvoker';
import { RecoPanel } from '../copilot-rail/RecoPanel';

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
  /**
   * Structured agent reply. When a turn carries a grounded artefact (Foundry
   * Agent), it renders through the same RecoPanel block stack as the proactive
   * reco — one artefact vocabulary across both surfaces. Full-width card so the
   * levers + approval gate stay readable.
   */
  agentArtefact: {
    alignSelf: 'stretch',
    backgroundColor: tokens.colorNeutralBackground3,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusMedium,
  },
  citations: { marginTop: tokens.spacingVerticalXS },
});

const NOOP = () => {};

/** Sprint 13 T6 — renders conversation turns + citation footer per agent reply. */
export function ConversationView({ turns }: { turns: ConversationTurn[] }) {
  const styles = useStyles();
  return (
    <div className={styles.list} data-testid="conversation">
      {turns.map((turn, i) => {
        // Structured grounded reply → render the shared artefact stack.
        if (turn.role === 'agent' && turn.reco) {
          return (
            <div key={i} className={styles.agentArtefact} data-testid="agent-artefact">
              <RecoPanel reco={turn.reco} showBack={false} onBack={NOOP} onCta={NOOP} />
            </div>
          );
        }
        // Plain text reply (or user turn).
        return (
          <div key={i} className={turn.role === 'user' ? styles.user : styles.agent}>
            {turn.refused ? <Badge color="danger">refused</Badge> : null}
            <Body1>{turn.text}</Body1>
            {turn.citations && turn.citations.length > 0 ? (
              <Caption1 className={styles.citations} data-testid="citations">
                Quellen: {turn.citations.join(', ')}
              </Caption1>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
