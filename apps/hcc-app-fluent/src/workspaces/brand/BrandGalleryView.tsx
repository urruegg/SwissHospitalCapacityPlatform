import { makeStyles, Text, Title3, tokens } from '@fluentui/react-components';
import { ds } from '../../theme/design-system';
import { useSurfaceStyles, useStateStyles } from '../../theme/design-system/recipes';
import copilotMarkUrl from '../../assets/brand/copilot.svg';
import { RecoPanel } from '../../copilot-rail/RecoPanel';
import type { GroundedReco } from '../../copilot-rail/reco';
import { ConversationView } from '../../copilot-drawer/ConversationView';
import type { ConversationTurn } from '../../copilot-drawer/AgentInvoker';

const NOOP = () => {};

/**
 * Sample grounded artefact exercising the A1–A10 + A12–A14 catalogue: attribution
 * (A1), context chip (A2), read (A3), metric trio (A4), levers + impact (A5) with
 * evidence (A13) and people (A14) popovers, projection (A6), CTA + approval gate
 * (A7), citations (A10), follow-ups (A12). English-only to match the gallery.
 */
const GALLERY_RECO: GroundedReco = {
  agentLabel: 'Occupancy Copilot',
  contextChip: { subject: 'Medicine A', qualifiers: ['72h forecast'], status: 'OVER', tone: 'over' },
  read: 'Medicine A reaches 102% within 72h — 6 flu admissions against 2 planned discharges.',
  metrics: [
    { label: 'Now', value: '96%' },
    { label: '72 h', value: '102%' },
    { label: 'Gap', value: '-6 beds', tone: 'beds' },
  ],
  levers: [
    {
      text: 'Expedite 6 discharge-ready patients before 17:00',
      impact: { label: '-6 beds', tone: 'beds' },
      evidence: {
        summary: '6 patients flagged discharge-ready (ward round complete).',
        detail: ['4 awaiting transport, 2 awaiting prescription', 'Window to 17:00 realistic'],
        citations: ['hcp:Encounter', 'gold.fact_discharge_readiness'],
      },
    },
    {
      text: 'Reallocate 2 pool nurses to the late shift',
      impact: { label: '+2 FTE', tone: 'status' },
      evidence: {
        summary: 'ICU late shift is 1.5 FTE below demand.',
        detail: ['Role: RN (dipl. HF)', 'Shift 15:00-23:00'],
        people: ['A. Weber (RN)', 'T. Meier (RN)', 'L. Kunz (Pool)'],
        citations: ['hcp:CareTeam', 'gold.fact_staffing_roster'],
      },
    },
    { text: 'Divert 3 low-acuity admits to Medicine B', impact: { label: '+3 buffer', tone: 'buffer' } },
  ],
  primaryCta: { label: 'Move to overflow', kind: 'action', requiresApproval: true },
  projection: '102% -> 94%',
  citations: ['hcp:CapacityUnit', 'gold.fact_occupancy_forecast'],
  provenance: 'simulated',
  refused: false,
  followUps: ['What happens without action?', 'Compare Ward B', 'Open discharge worklist'],
};

/** Sample guardrail refusal (A11) — verbatim reason, no levers, no CTA. */
const GALLERY_REFUSAL: GroundedReco = {
  agentLabel: 'Bed-Management Copilot',
  contextChip: { subject: 'Guardrail', status: 'Refused', tone: 'blocked' },
  read: 'Request refused: this action has a side effect and requires HITL approval (approved-to-apply) before it can run.',
  levers: [],
  citations: ['policy:HITL-02', 'AGENTS.md#4-confirmation-rule'],
  provenance: 'simulated',
  refused: true,
};

const GALLERY_TURNS: ConversationTurn[] = [
  { role: 'user', text: 'How does Medicine A look in 72h?' },
  { role: 'agent', text: GALLERY_RECO.read, reco: GALLERY_RECO },
];


/**
 * Sprint 27 M3 — dev-only design-system gallery.
 *
 * Route-only surface (mounted at `/brand`, not in any navigation menu). It
 * renders the semantic spacing/elevation tokens and the shared surface/state
 * recipes so we can eyeball the design system in isolation. Intentionally
 * English-only (no i18n) so it renders under `ThemeModeProvider` alone.
 */
const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: ds.space.xl,
    padding: ds.space.xl,
  },
  section: {
    display: 'flex',
    flexDirection: 'column',
    gap: ds.space.m,
  },
  row: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: ds.space.m,
    alignItems: 'flex-end',
  },
  swatch: {
    display: 'flex',
    flexDirection: 'column',
    gap: ds.space.xs,
    alignItems: 'center',
  },
  artefactGrid: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: ds.space.l,
    alignItems: 'flex-start',
  },
  artefactCard: {
    display: 'flex',
    flexDirection: 'column',
    gap: ds.space.s,
    padding: ds.space.l,
    borderRadius: ds.radii.card,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    width: '360px',
    maxWidth: '100%',
  },
  artefactCaption: { color: tokens.colorNeutralForeground3 },
});

export function BrandGalleryView() {
  const s = useStyles();
  const surface = useSurfaceStyles();
  const state = useStateStyles();

  return (
    <div data-testid="brand-gallery" className={s.root}>
      <section className={s.section} aria-label="Spacing">
        <Title3>Spacing</Title3>
        <div className={s.row}>
          {Object.entries(ds.space).map(([k, v]) => (
            <div key={k} className={s.swatch}>
              <div style={{ width: v, height: v, backgroundColor: tokens.colorBrandBackground }} />
              <Text size={200}>
                {k} · {v}
              </Text>
            </div>
          ))}
        </div>
      </section>

      <section className={s.section} aria-label="Elevation">
        <Title3>Elevation</Title3>
        <div className={s.row}>
          {Object.keys(ds.elevation).map((k) => (
            <div key={k} className={surface.surfaceCard}>
              <Text>{k}</Text>
            </div>
          ))}
        </div>
      </section>

      <section className={s.section} aria-label="Component states">
        <Title3>Component states</Title3>
        <div className={surface.statTile}>
          <Text>statTile</Text>
        </div>
        <div className={surface.provenanceBadge}>
          <Text size={200}>live</Text>
        </div>
        <div className={state.emptyState}>
          <Text>Empty state</Text>
        </div>
        <div className={state.loadingState}>
          <Text>Loading</Text>
        </div>
        <div className={state.errorState}>
          <Text>Error state</Text>
        </div>
      </section>

      <section className={s.section} aria-label="Copilot mark">
        <Title3>Copilot mark</Title3>
        <div className={s.row}>
          {[16, 24, 32, 48].map((px) => (
            <div key={px} className={s.swatch}>
              <img src={copilotMarkUrl} alt="Microsoft Copilot" width={px} height={px} />
              <Text size={200}>{px}px</Text>
            </div>
          ))}
        </div>
      </section>

      <section className={s.section} aria-label="Chat response artefacts">
        <Title3>Chat response artefacts</Title3>
        <Text size={200} className={s.artefactCaption}>
          The A1–A14 catalogue every Foundry-agent reply renders through — one
          artefact vocabulary across the proactive rail and the chat.
        </Text>
        <div className={s.artefactGrid}>
          <div className={s.artefactCard} data-testid="gallery-recommendation">
            <Text size={200} className={s.artefactCaption}>
              Recommendation — A1 attribution · A2 chip · A3 read · A4 metric trio ·
              A5 levers · A6 projection · A7 CTA + gate · A10 citations · A12
              follow-ups · A13/A14 evidence popovers (hover a badge)
            </Text>
            <ConversationView turns={GALLERY_TURNS} onFollowUp={NOOP} />
          </div>
          <div className={s.artefactCard} data-testid="gallery-refusal">
            <Text size={200} className={s.artefactCaption}>
              Guardrail refusal — A11 (verbatim reason, no levers, no CTA)
            </Text>
            <RecoPanel reco={GALLERY_REFUSAL} showBack={false} onBack={NOOP} onCta={NOOP} />
          </div>
        </div>
      </section>
    </div>
  );
}
