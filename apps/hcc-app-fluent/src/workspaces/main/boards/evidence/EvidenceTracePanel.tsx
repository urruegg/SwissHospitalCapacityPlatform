import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Badge,
  Body1,
  Body2,
  Button,
  Caption1,
  Divider,
  Tab,
  TabList,
  Title3,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import {
  ArrowLeftRegular,
  ArrowRightRegular,
  CheckmarkCircleRegular,
  DismissCircleRegular,
  DatabaseRegular,
  EyeRegular,
  LightbulbRegular,
  PersonRegular,
  FlowRegular,
} from '@fluentui/react-icons';
import type { EvidenceStep, EvidenceTrace } from '../../../../data/iq-client';
import type { Provenance } from '../../../../journey/RoleBoard';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalM },
  head: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS },
  headRow: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalS, flexWrap: 'wrap' },
  lead: { color: tokens.colorNeutralForeground2 },
  toolbar: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: tokens.spacingHorizontalM, flexWrap: 'wrap' },
  walk: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalS, flexWrap: 'wrap' },
  walkChips: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalXS, flexWrap: 'wrap' },
  stepLabel: { color: tokens.colorNeutralForeground2 },
  parts: { display: 'grid', gap: tokens.spacingVerticalS },
  part: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXXS,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusMedium,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
  },
  partOutcome: { borderLeft: `3px solid ${tokens.colorNeutralStroke1}` },
  partHead: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalXS, flexWrap: 'wrap' },
  partTitle: { fontWeight: tokens.fontWeightSemibold, color: tokens.colorNeutralForeground1 },
  partIndex: { color: tokens.colorNeutralForeground3 },
  metaRow: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalS, flexWrap: 'wrap' },
  muted: { color: tokens.colorNeutralForeground3 },
  cites: { color: tokens.colorNeutralForeground3 },
  value: { fontWeight: tokens.fontWeightSemibold },
  unify: { color: tokens.colorNeutralForeground2 },
});

/** AA-safe provenance chip — outline (never brand tint), reusing the shared
 * `dca.table.source.*` label. success == live golden evidence, informative ==
 * simulated demo fixture. */
function ProvenanceBadge({ provenance }: { provenance: Provenance }) {
  const { t } = useTranslation();
  return (
    <Badge appearance="outline" size="small" color={provenance === 'live' ? 'success' : 'informative'}>
      {t(`dca.table.source.${provenance}`)}
    </Badge>
  );
}

interface FivePartProofProps {
  step: EvidenceStep;
}

/** The five-part proof for one journey step (EPIC input -> read -> recommendation
 * -> copilot accept/deny -> outcome), each part carrying its own provenance. */
function FivePartProof({ step }: FivePartProofProps) {
  const s = useStyles();
  const { t } = useTranslation();
  const accepted = step.copilot.decision === 'accept';
  const ep = step.epic_input;
  const rc = step.recommendation;
  const oc = step.outcome;
  return (
    <div className={s.parts} data-testid="evidence-step" data-role={step.role}>
      {/* Part 1 — EPIC input */}
      <div className={s.part} data-testid="evidence-part-epic">
        <div className={s.partHead}>
          <DatabaseRegular aria-hidden />
          <Caption1 className={s.partIndex}>1/5</Caption1>
          <Body2 className={s.partTitle}>{t('evidence.part.epic')}</Body2>
          <ProvenanceBadge provenance={ep.provenance} />
        </div>
        <Body1>{t('evidence.epic.occupancy', { occupied: ep.occupiedBeds, capacity: ep.bedCapacity, ward: ep.wardId })}</Body1>
        {ep.citations.length > 0 && <Caption1 className={s.cites}>{ep.citations.join(' \u00b7 ')}</Caption1>}
      </div>

      {/* Part 2 — agent read */}
      <div className={s.part} data-testid="evidence-part-read">
        <div className={s.partHead}>
          <EyeRegular aria-hidden />
          <Caption1 className={s.partIndex}>2/5</Caption1>
          <Body2 className={s.partTitle}>{t('evidence.part.read')}</Body2>
          <ProvenanceBadge provenance={ep.provenance} />
        </div>
        <Body1>{step.agent_read.signal}</Body1>
      </div>

      {/* Part 3 — recommendation */}
      <div className={s.part} data-testid="evidence-part-reco">
        <div className={s.partHead}>
          <LightbulbRegular aria-hidden />
          <Caption1 className={s.partIndex}>3/5</Caption1>
          <Body2 className={s.partTitle}>{t('evidence.part.reco')}</Body2>
          <ProvenanceBadge provenance={ep.provenance} />
        </div>
        <Body1>{rc.insight_text}</Body1>
        <div className={s.metaRow}>
          {rc.lever_id ? (
            <Badge appearance="outline" size="small" color="informative">{rc.lever_id}</Badge>
          ) : (
            <Caption1 className={s.muted}>{t('evidence.reco.noLever')}</Caption1>
          )}
          <Caption1 className={s.muted}>
            {t('evidence.reco.predicted', { value: rc.predicted_impact.value, metric: rc.predicted_impact.metric })}
          </Caption1>
        </div>
      </div>

      {/* Part 4 — copilot accept/deny (the HITL gate) */}
      <div className={s.part} data-testid="evidence-part-copilot">
        <div className={s.partHead}>
          <PersonRegular aria-hidden />
          <Caption1 className={s.partIndex}>4/5</Caption1>
          <Body2 className={s.partTitle}>{t('evidence.part.copilot')}</Body2>
          {accepted ? (
            <Badge appearance="filled" size="small" color="important" icon={<CheckmarkCircleRegular />}>
              {t('evidence.copilot.accepted')}
            </Badge>
          ) : (
            <Badge appearance="outline" size="small" color="informative" icon={<DismissCircleRegular />}>
              {t('evidence.copilot.denied')}
            </Badge>
          )}
        </div>
        <Caption1 className={s.muted}>{t('evidence.copilot.requiresApproval')}</Caption1>
        {accepted && step.copilot.approver && (
          <Caption1 className={s.muted}>{t('evidence.copilot.approver', { approver: step.copilot.approver })}</Caption1>
        )}
      </div>

      {/* Part 5 — outcome (DC-SIM-OUTCOME-v1: the validation==UX contract, FR-UXL-004) */}
      <div className={mergeClasses(s.part, s.partOutcome)} data-testid="evidence-part-outcome">
        <div className={s.partHead}>
          <FlowRegular aria-hidden />
          <Caption1 className={s.partIndex}>5/5</Caption1>
          <Body2 className={s.partTitle}>{t('evidence.part.outcome')}</Body2>
          <ProvenanceBadge provenance={oc.provenance} />
          <Badge appearance="outline" size="small" color={(oc.applied ?? oc.realised_impact.value > 0) ? 'success' : 'informative'}>
            {(oc.applied ?? oc.realised_impact.value > 0) ? t('evidence.outcome.applied') : t('evidence.outcome.notApplied')}
          </Badge>
        </div>
        <Body1 className={s.value}>
          {t('evidence.outcome.realised', { value: oc.realised_impact.value, metric: oc.realised_impact.metric })}
        </Body1>
        <div className={s.metaRow}>
          <Caption1 className={s.muted}>{t('evidence.outcome.divergence', { value: oc.divergence })}</Caption1>
          <Caption1 className={s.muted}>{oc.contract}</Caption1>
        </div>
        {/* B4 — make the validation==UX link explicit: this outcome is the SAME
            contract + fields the copilot accept surface (B2) renders, keyed on
            the same golden_thread. */}
        <Caption1 className={s.unify} data-testid="evidence-outcome-thread">
          {t('evidence.outcome.sameContract', { thread: oc.golden_thread })}
        </Caption1>
      </div>
    </div>
  );
}

interface EvidenceTracePanelProps {
  trace: EvidenceTrace;
  branch: 'accept' | 'deny';
  onBranchChange: (branch: 'accept' | 'deny') => void;
  degraded?: boolean;
}

/**
 * Sprint 39 P2 (B3/B4) — presentational Closed-Loop Evidence panel. Renders a
 * DC-EVIDENCE-TRACE-v1: the shared `golden_thread`, a branch toggle (accept <->
 * deny), a demo walk stepper across the trace's steps (the canonical OOA -> DCA
 * -> BMCA -> ORSA order in the demo fixture), and the five-part proof for the
 * current step. Pure/controlled: data loading (Live endpoint vs bundled fixture)
 * lives in the board.
 */
export function EvidenceTracePanel({ trace, branch, onBranchChange, degraded }: EvidenceTracePanelProps) {
  const s = useStyles();
  const { t } = useTranslation();
  const total = trace.steps.length;
  const [stepIndex, setStepIndex] = useState(0);
  // Reset the walk to the first step whenever the trace (or branch) changes so a
  // toggle never leaves a stale index past the new step count.
  useEffect(() => {
    setStepIndex(0);
  }, [trace.golden_thread, branch, total]);

  const safeIndex = Math.min(stepIndex, Math.max(0, total - 1));
  const step = trace.steps[safeIndex];
  const roleLabel = (r: string) => r.toUpperCase();

  return (
    <div className={s.root} data-testid="evidence-panel">
      <div className={s.head}>
        <div className={s.headRow}>
          <Title3>{t('evidence.title')}</Title3>
          <Badge appearance="outline" color="informative">{trace.contract}</Badge>
        </div>
        <Body1 className={s.lead}>{t('evidence.lead')}</Body1>
        <div className={s.headRow}>
          <Badge appearance="filled" color="important" data-testid="evidence-golden-thread">
            {t('evidence.goldenThread', { thread: trace.golden_thread })}
          </Badge>
          <Caption1 className={s.muted}>
            {t('evidence.patient', { id: trace.patient.synthetic_id, specialty: trace.patient.specialty ?? '' })}
          </Caption1>
          <ProvenanceBadge provenance={trace.patient.provenance} />
        </div>
        {degraded && (
          <Caption1 className={s.muted} role="status">{t('evidence.degraded')}</Caption1>
        )}
      </div>

      {/* Branch toggle — accept <-> deny. */}
      <TabList
        selectedValue={branch}
        onTabSelect={(_e, d) => onBranchChange(d.value as 'accept' | 'deny')}
        data-testid="evidence-branch-toggle"
        aria-label={t('evidence.branch.label')}
      >
        <Tab value="accept" icon={<CheckmarkCircleRegular />}>{t('evidence.branch.accept')}</Tab>
        <Tab value="deny" icon={<DismissCircleRegular />}>{t('evidence.branch.deny')}</Tab>
      </TabList>

      <Divider />

      {/* Demo walk — step one synthetic patient through the roles. */}
      {step && (
        <>
          <div className={s.toolbar} data-testid="evidence-stepper">
            <div className={s.walk}>
              <Button
                appearance="secondary"
                icon={<ArrowLeftRegular />}
                disabled={safeIndex === 0}
                onClick={() => setStepIndex((i) => Math.max(0, i - 1))}
              >
                {t('evidence.walk.prev')}
              </Button>
              <Body2 className={s.stepLabel} aria-live="polite">
                {t('evidence.walk.step', { n: safeIndex + 1, total, role: roleLabel(step.role) })}
              </Body2>
              <Button
                appearance="secondary"
                icon={<ArrowRightRegular />}
                iconPosition="after"
                disabled={safeIndex >= total - 1}
                onClick={() => setStepIndex((i) => Math.min(total - 1, i + 1))}
              >
                {t('evidence.walk.next')}
              </Button>
            </div>
            <div className={s.walkChips} aria-hidden>
              {trace.steps.map((st, i) => (
                <Badge
                  key={`${st.role}-${i}`}
                  appearance={i === safeIndex ? 'filled' : 'outline'}
                  size="small"
                  color={i === safeIndex ? 'important' : 'informative'}
                >
                  {roleLabel(st.role)}
                </Badge>
              ))}
            </div>
          </div>

          <FivePartProof step={step} />
        </>
      )}
    </div>
  );
}
