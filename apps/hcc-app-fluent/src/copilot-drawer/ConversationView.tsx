import { Fragment } from 'react';
import {
  makeStyles,
  tokens,
  Body1,
  Caption1,
  Badge,
  Button,
  TagGroup,
  InteractionTag,
  InteractionTagPrimary,
} from '@fluentui/react-components';
import { ThumbLikeRegular, ThumbDislikeRegular } from '@fluentui/react-icons';
import { useTranslation } from 'react-i18next';
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
  /**
   * M2-app — thumbs rating under a captured agent reply. Left-aligned, subtle so
   * it never competes with the reply; emits a user-interaction event for the
   * turn's `interactionId` (advisory-only feedback signal).
   */
  rating: {
    alignSelf: 'flex-start',
    display: 'flex',
    gap: tokens.spacingHorizontalXS,
  },
  /**
   * A12 — per-reply follow-up chips ("what next"). Left-aligned under the latest
   * agent reply; clicking one sends it as the next ask.
   */
  followUps: {
    alignSelf: 'flex-start',
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalXS,
  },
});

const NOOP = () => {};

/** Sprint 13 T6 — renders conversation turns + citation footer per agent reply. */
export function ConversationView({
  turns,
  onFollowUp,
  onRate,
}: {
  turns: ConversationTurn[];
  /** A12 — send a follow-up prompt as the next ask. Chips are hidden when absent. */
  onFollowUp?: (prompt: string) => void;
  /** M2-app — emit a thumbs rating for a captured turn. Control hidden when absent. */
  onRate?: (interactionId: string, value: 'up' | 'down') => void;
}) {
  const styles = useStyles();
  const { t } = useTranslation();
  const lastIndex = turns.length - 1;
  return (
    <div className={styles.list} data-testid="conversation">
      {turns.map((turn, i) => {
        const isAgentReco = turn.role === 'agent' && Boolean(turn.reco);
        // A12: surface follow-ups only under the latest agent reply, so history
        // stays uncluttered and the chips always reflect the current answer.
        const followUps =
          onFollowUp && i === lastIndex && turn.role === 'agent'
            ? turn.reco?.followUps
            : undefined;

        const block = isAgentReco ? (
          <div className={styles.agentArtefact} data-testid="agent-artefact">
            <RecoPanel reco={turn.reco!} showBack={false} onBack={NOOP} onCta={NOOP} />
          </div>
        ) : (
          <div className={turn.role === 'user' ? styles.user : styles.agent}>
            {turn.refused ? <Badge color="danger">refused</Badge> : null}
            <Body1>{turn.text}</Body1>
            {turn.citations && turn.citations.length > 0 ? (
              <Caption1 className={styles.citations} data-testid="citations">
                Quellen: {turn.citations.join(', ')}
              </Caption1>
            ) : null}
          </div>
        );

        return (
          <Fragment key={i}>
            {block}
            {onRate && turn.role === 'agent' && turn.interactionId ? (
              <div
                className={styles.rating}
                data-testid="rating"
                role="group"
                aria-label={t('copilot.rateLabel', 'Rate this reply')}
              >
                <Button
                  size="small"
                  appearance="subtle"
                  icon={<ThumbLikeRegular />}
                  data-testid="rate-up"
                  aria-label={t('copilot.rateUp', 'Helpful')}
                  onClick={() => onRate(turn.interactionId!, 'up')}
                />
                <Button
                  size="small"
                  appearance="subtle"
                  icon={<ThumbDislikeRegular />}
                  data-testid="rate-down"
                  aria-label={t('copilot.rateDown', 'Not helpful')}
                  onClick={() => onRate(turn.interactionId!, 'down')}
                />
              </div>
            ) : null}
            {followUps && followUps.length > 0 ? (
              <TagGroup
                className={styles.followUps}
                data-testid="follow-ups"
                aria-label={t('copilot.followUps', 'Suggested follow-ups')}
              >
                {followUps.map((q) => (
                  <InteractionTag key={q} value={q} size="small">
                    <InteractionTagPrimary onClick={() => onFollowUp!(q)}>
                      {q}
                    </InteractionTagPrimary>
                  </InteractionTag>
                ))}
              </TagGroup>
            ) : null}
          </Fragment>
        );
      })}
    </div>
  );
}
