/**
 * Sprint 16.1 · S16.5 — CSA wizard step body renderer.
 *
 * Renders the current wizard step's body:
 *   - `prepare`: text input + submit → posts a scenario draft to csa-agent chat
 *   - `run` / `evaluate`: stub scaffold with the deferred-reason badge
 *   - `recommend`: read-only list of the 3 sample recommendation PRs
 *
 * The Copilot Drawer is owned by the parent wizard so the drawer stays open
 * across steps (matches design spec §8 "drawer stays open in the right rail").
 */
import { useState } from 'react';
import {
  Badge,
  Body1,
  Button,
  Caption1,
  Card,
  CardHeader,
  Divider,
  Input,
  Link,
  makeStyles,
  MessageBar,
  Subtitle1,
  tokens,
} from '@fluentui/react-components';
import { useAgentInvoker } from '../../../../copilot-drawer/AgentInvoker';
import {
  csaStepById,
  CSA_SAMPLE_RECOMMENDATIONS,
  type CsaStepId,
} from './csa-steps';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalM },
  inputRow: { display: 'flex', gap: tokens.spacingHorizontalS, alignItems: 'stretch' },
  reply: { marginTop: tokens.spacingVerticalS },
  sampleList: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalS },
});

interface CsaStepBodyProps {
  step: CsaStepId;
  onAdvance: (next: CsaStepId) => void;
}

const NEXT_STEP: Record<CsaStepId, CsaStepId | null> = {
  prepare: 'run',
  run: 'evaluate',
  evaluate: 'recommend',
  recommend: null,
};

export function CsaStepBody({ step, onAdvance }: CsaStepBodyProps) {
  const styles = useStyles();
  const meta = csaStepById(step);

  return (
    <section className={styles.root} data-testid={`CsaStepBody-${step}`}>
      <div>
        <Subtitle1>{meta.label}</Subtitle1>
        <Body1 as="p">{meta.description}</Body1>
        {meta.status === 'stub' && (
          <Badge appearance="tint" color="warning" style={{ marginTop: tokens.spacingVerticalS }}>
            Stub — Sprint 13 T5 wiring pending
          </Badge>
        )}
      </div>
      <Divider />
      {step === 'prepare' && <PrepareBody onAdvance={() => onAdvance(NEXT_STEP.prepare!)} />}
      {step === 'run' && <RunBody meta={meta.deferredReason} onAdvance={() => onAdvance(NEXT_STEP.run!)} />}
      {step === 'evaluate' && (
        <EvaluateBody meta={meta.deferredReason} onAdvance={() => onAdvance(NEXT_STEP.evaluate!)} />
      )}
      {step === 'recommend' && <RecommendBody meta={meta.deferredReason} />}
    </section>
  );
}

/**
 * Prepare — real behaviour: posts the scenario text to csa-agent chat and shows
 * the (mock or live) grounded reply. Uses the same useAgentInvoker hook that
 * powers the Copilot Drawer so answers stay consistent.
 */
function PrepareBody({ onAdvance }: { onAdvance: () => void }) {
  const styles = useStyles();
  const { turns, busy, send } = useAgentInvoker('csa-agent');
  const [draft, setDraft] = useState('');

  const submit = async () => {
    if (!draft.trim()) return;
    await send(draft);
    setDraft('');
  };
  const lastReply = [...turns].reverse().find((t) => t.role === 'agent');
  return (
    <div className={styles.root}>
      <div className={styles.inputRow}>
        <Input
          placeholder="Describe the scenario, e.g. 'RSV surge in pediatrics Q3'"
          value={draft}
          onChange={(_e, data) => setDraft(data.value)}
          style={{ flexGrow: 1 }}
          data-testid="CsaPrepareInput"
        />
        <Button appearance="primary" onClick={submit} disabled={busy} data-testid="CsaPrepareSubmit">
          {busy ? 'Preparing…' : 'Prepare scenario'}
        </Button>
      </div>
      {lastReply && (
        <Card className={styles.reply} data-testid="CsaPrepareReply">
          <CardHeader header={<Subtitle1>csa-agent reply</Subtitle1>} />
          <Body1 as="p">{lastReply.text}</Body1>
          {lastReply.citations && lastReply.citations.length > 0 && (
            <Caption1>Grounded in: {lastReply.citations.join(', ')}</Caption1>
          )}
        </Card>
      )}
      <Button appearance="secondary" onClick={onAdvance} data-testid="CsaPrepareAdvance">
        Next: Run
      </Button>
    </div>
  );
}

/** Run — stub: displays the exact MCP-wiring blocker + a manual advance button. */
function RunBody({ meta, onAdvance }: { meta?: string; onAdvance: () => void }) {
  return (
    <div>
      <MessageBar intent="info">
        <Body1 as="p">
          Live simulation run: <strong>not wired yet</strong>. {meta}
        </Body1>
      </MessageBar>
      <Body1 as="p" style={{ marginTop: tokens.spacingVerticalS }}>
        Once MCP wiring lands, this step will trigger <code>csa-simulate.ipynb</code> on
        the Fabric medallion notebook and surface the <code>runId</code>.
      </Body1>
      <Button
        appearance="secondary"
        onClick={onAdvance}
        style={{ marginTop: tokens.spacingVerticalM }}
        data-testid="CsaRunAdvance"
      >
        Skip to Evaluate (stub)
      </Button>
    </div>
  );
}

/** Evaluate — stub: same shape as Run. */
function EvaluateBody({ meta, onAdvance }: { meta?: string; onAdvance: () => void }) {
  return (
    <div>
      <MessageBar intent="info">
        <Body1 as="p">
          Simulation output evaluation: <strong>not wired yet</strong>. {meta}
        </Body1>
      </MessageBar>
      <Body1 as="p" style={{ marginTop: tokens.spacingVerticalS }}>
        The tier classifier + bed-day summariser will render here once the polling
        + cosmos-mcp read is wired.
      </Body1>
      <Button
        appearance="secondary"
        onClick={onAdvance}
        style={{ marginTop: tokens.spacingVerticalM }}
        data-testid="CsaEvaluateAdvance"
      >
        Skip to Recommend (stub)
      </Button>
    </div>
  );
}

/**
 * Recommend — read-only sample view. Links to the 3 physical recommendation
 * PRs shipped during Sprint 16 T4 so the demo shows the output shape today
 * without requiring live MCP execution.
 */
function RecommendBody({ meta }: { meta?: string }) {
  const styles = useStyles();
  return (
    <div className={styles.root}>
      <MessageBar intent="info">
        <Body1 as="p">
          Live recommendation-draft PR: <strong>not wired yet</strong>. {meta}
        </Body1>
      </MessageBar>
      <Body1 as="p">
        Reference — 3 recommendation PRs merged during Sprint 16 T4:
      </Body1>
      <div className={styles.sampleList} data-testid="CsaRecommendSamples">
        {CSA_SAMPLE_RECOMMENDATIONS.map((rec) => (
          <Card key={rec.slug}>
            <CardHeader
              header={<Subtitle1>{rec.title}</Subtitle1>}
              description={<Caption1>Scenario tier: {rec.scenarioTier}</Caption1>}
            />
            <Link href={`https://github.com/urruegg/SwissHospitalCapacityPlatform/blob/main/${rec.path}`}>
              View recommendation source
            </Link>
          </Card>
        ))}
      </div>
    </div>
  );
}
