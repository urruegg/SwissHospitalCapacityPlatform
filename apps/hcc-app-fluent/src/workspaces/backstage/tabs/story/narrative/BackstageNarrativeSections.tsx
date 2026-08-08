import { makeStyles, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import type { TFunction } from 'i18next';
import { useCopilotRail } from '../../../../../copilot-rail/rail-context';
import type { GroundedReco } from '../../../../../copilot-rail/reco';
import { SectionHeader, type SectionTitlePart } from '../../../../shared/narrative/SectionHeader';
import rebekkaHatzung from '../../../../../assets/reviewers/rebekka-hatzung.jpg';
import emanuelFurler from '../../../../../assets/reviewers/emanuel-furler.jpg';
import christianErnst from '../../../../../assets/reviewers/christian-ernst.jpg';
import regulaAdams from '../../../../../assets/reviewers/regula-adams.jpg';
import marcoRossi from '../../../../../assets/reviewers/marco-rossi.jpg';
import petrusJallo from '../../../../../assets/reviewers/petrus-jallo.jpg';
import reneRaeber from '../../../../../assets/reviewers/rene-raeber.jpg';
import danielVonBueren from '../../../../../assets/reviewers/daniel-von-bueren.jpg';
import marcoWeber from '../../../../../assets/reviewers/marco-weber.jpg';

// Sprint 36 intake (B2, B3, B5, B6) — Frontier-Firm Backstage narrative sections.

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalL },
  split: {
    display: 'grid',
    gridTemplateColumns: '1.05fr 0.95fr',
    gap: tokens.spacingHorizontalL,
    alignItems: 'start',
    '@media screen and (max-width: 900px)': { gridTemplateColumns: '1fr' },
  },
  panel: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalS,
    padding: tokens.spacingHorizontalL,
    borderRadius: tokens.borderRadiusLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
  },
  panelTitle: {
    margin: 0,
    fontSize: tokens.fontSizeBase500,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  note: { fontSize: tokens.fontSizeBase200, color: tokens.colorNeutralForeground3, lineHeight: 1.4 },

  sfRows: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalS },
  sfRow: {
    display: 'grid',
    gridTemplateColumns: '30px 1fr',
    gap: tokens.spacingHorizontalM,
    alignItems: 'start',
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderLeftWidth: '4px',
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
    textAlign: 'left',
    fontFamily: 'inherit',
    cursor: 'pointer',
    ':hover': { boxShadow: tokens.shadow4 },
    ':focus-visible': { outlineStyle: 'solid', outlineWidth: '2px', outlineColor: tokens.colorStrokeFocus2, outlineOffset: '2px' },
  },
  sfNum: {
    display: 'grid',
    placeItems: 'center',
    width: '26px',
    height: '26px',
    borderRadius: tokens.borderRadiusCircular,
    backgroundColor: '#17B890',
    color: '#FFFFFF',
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightBold,
  },
  sfTitle: { fontWeight: tokens.fontWeightSemibold, color: tokens.colorNeutralForeground1 },
  sfBody: { fontSize: tokens.fontSizeBase200, color: tokens.colorNeutralForeground2, marginTop: '2px' },

  statGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: tokens.spacingHorizontalM },
  statCell: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusLarge,
    backgroundColor: tokens.colorNeutralBackground2,
  },
  statValue: { fontSize: tokens.fontSizeBase600, fontWeight: tokens.fontWeightBold, color: '#365B7D' },
  statSub: { fontSize: tokens.fontSizeBase200, color: tokens.colorNeutralForeground3 },

  frameButton: {
    display: 'block',
    width: '100%',
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusXLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
    cursor: 'pointer',
    ':hover': { boxShadow: tokens.shadow4 },
    ':focus-visible': { outlineStyle: 'solid', outlineWidth: '2px', outlineColor: tokens.colorStrokeFocus2, outlineOffset: '2px' },
  },
  svg: { width: '100%', height: 'auto', display: 'block' },
  legend: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalL,
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground3,
  },
  legendItem: { display: 'inline-flex', alignItems: 'center', gap: '6px' },
  sw: { width: '14px', height: '14px', borderRadius: '3px', display: 'inline-block', flexShrink: 0 },

  table: { width: '100%', borderCollapse: 'collapse' },
  th: {
    textAlign: 'left',
    padding: '6px 8px',
    color: tokens.colorNeutralForeground3,
    fontWeight: tokens.fontWeightSemibold,
    textTransform: 'uppercase',
    fontSize: '11px',
    letterSpacing: '0.04em',
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  td: {
    padding: '8px',
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    color: tokens.colorNeutralForeground2,
    verticalAlign: 'top',
    fontSize: tokens.fontSizeBase200,
  },
  tdName: { color: tokens.colorNeutralForeground1, fontWeight: tokens.fontWeightSemibold },
  tdDate: { color: tokens.colorNeutralForeground3, fontSize: '11px', marginLeft: '4px', fontWeight: tokens.fontWeightRegular },

  roleStack: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalM },
  roleCard: {
    display: 'grid',
    gridTemplateColumns: '38px 1fr',
    gap: tokens.spacingHorizontalM,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
    textAlign: 'left',
    fontFamily: 'inherit',
    cursor: 'pointer',
    ':hover': { boxShadow: tokens.shadow4 },
    ':focus-visible': { outlineStyle: 'solid', outlineWidth: '2px', outlineColor: tokens.colorStrokeFocus2, outlineOffset: '2px' },
  },
  avatar: {
    display: 'grid',
    placeItems: 'center',
    width: '36px',
    height: '36px',
    borderRadius: tokens.borderRadiusCircular,
    color: '#FFFFFF',
    fontSize: tokens.fontSizeBase300,
    fontWeight: tokens.fontWeightBold,
  },
  roleTitle: { fontWeight: tokens.fontWeightSemibold, color: tokens.colorNeutralForeground1 },
  comp: { fontSize: tokens.fontSizeBase200, color: tokens.colorNeutralForeground3, marginTop: '2px' },
  chal: { fontSize: tokens.fontSizeBase200, color: '#8A6300', marginTop: '4px' },

  subhead: {
    margin: 0,
    fontSize: tokens.fontSizeBase400,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  peopleGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: tokens.spacingHorizontalM,
  },
  personCard: {
    display: 'grid',
    gridTemplateColumns: '38px 1fr',
    gap: tokens.spacingHorizontalM,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
  },
  personName: { fontWeight: tokens.fontWeightSemibold, color: tokens.colorNeutralForeground1 },
  personPhoto: {
    width: '38px',
    height: '38px',
    borderRadius: tokens.borderRadiusCircular,
    objectFit: 'cover',
    display: 'block',
  },
  lk: {
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorBrandForeground1,
    marginTop: '6px',
    display: 'inline-block',
    textDecorationLine: 'none',
    ':hover': { textDecorationLine: 'underline' },
  },
  disc: {
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground3,
    lineHeight: 1.4,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusMedium,
    backgroundColor: tokens.colorNeutralBackground2,
  },

  classGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
    gap: tokens.spacingHorizontalM,
  },
  classCard: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderLeftWidth: '4px',
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
    textAlign: 'left',
    fontFamily: 'inherit',
    cursor: 'pointer',
    ':hover': { boxShadow: tokens.shadow4 },
    ':focus-visible': { outlineStyle: 'solid', outlineWidth: '2px', outlineColor: tokens.colorStrokeFocus2, outlineOffset: '2px' },
  },
  classHead: { display: 'inline-flex', alignItems: 'center', gap: tokens.spacingHorizontalXS },
  letterTag: {
    display: 'grid',
    placeItems: 'center',
    width: '22px',
    height: '22px',
    borderRadius: '6px',
    color: '#FFFFFF',
    fontSize: '12px',
    fontWeight: tokens.fontWeightBold,
  },
  classTitle: { fontWeight: tokens.fontWeightSemibold, color: tokens.colorNeutralForeground1, fontSize: tokens.fontSizeBase400 },
  classBody: { fontSize: tokens.fontSizeBase200, color: tokens.colorNeutralForeground2 },
});

function useRail(): ReturnType<typeof useCopilotRail> | null {
  try {
    return useCopilotRail();
  } catch {
    return null;
  }
}

function reco(subject: string, read: string, levers: string[], citations: string[], t: TFunction): GroundedReco {
  return {
    agentLabel: 'product-owner-agent',
    contextChip: {
      subject,
      status: t('backstage.story.feedbackLoop.advisoryNote', 'Advisory only'),
      tone: 'signal',
    },
    read,
    levers: levers.map((text) => ({ text })),
    citations,
    provenance: 'simulated',
  };
}

function toTitleParts(title: string, accent?: string): SectionTitlePart[] | undefined {
  if (!accent || !title.includes(accent)) return undefined;
  const i = title.indexOf(accent);
  return [
    { text: title.slice(0, i) },
    { text: accent, tone: 'accent' as const },
    { text: title.slice(i + accent.length) },
  ].filter((part) => part.text.length > 0);
}

const SF_PRINCIPLES = [
  { n: 1, accent: '#17B890', title: 'Organize around outcomes, not roles', body: 'Every sprint is one tracker issue, small vertical slices, squash PRs. GitHub is the single control plane.' },
  { n: 2, accent: '#1FA9D6', title: 'Human-agent teams', body: 'Agents open, update and green pull requests in parallel worktrees; a human merges every PR, agents never self-merge.' },
  { n: 3, accent: '#5A6CF0', title: 'Trust & governance by design', body: 'ADRs, PR traceability, security & compliance gates, and PHI four-gate enforcement are native, not bolted on.' },
  { n: 4, accent: '#365B7D', title: 'Evidence-first, measurable', body: 'Every release is auditable; requirements map to FR/NFR IDs; value tracked against the BVA baseline.' },
] as const;

const SF_STATS = [
  { value: '1', sub: 'human orchestrating the build', color: '#12765F' },
  { value: '39', sub: 'sprints delivered end-to-end', color: undefined },
  { value: '398', sub: 'PRs approved and merged', color: undefined },
  { value: '100%', sub: 'PRs human-merged, CI-gated', color: undefined },
] as const;

export function SuccessFrameworkSection() {
  const s = useStyles();
  const { t } = useTranslation();
  const rail = useRail();
  const header = t('backstage.story.narrative.success.header', 'We have organized our own transformation against the Success Framework.');
  const titleParts = toTitleParts(
    header,
    t('backstage.story.narrative.success.accent', 'Success Framework'),
  );
  const ask = () =>
    rail?.openWithReco(
      { id: 'backstage-success-framework', label: 'Success Framework', context: { source: 'backstage-narrative', topic: 'success-framework' } },
      reco(
        'Success Framework',
        'Curavias was built on four transformation principles - organize around outcomes, human-agent teams, trust and governance by design, and evidence-first - delivered by one human agent-boss across 39 sprints through enterprise ALM, with 100% human-merged pull requests.',
        SF_PRINCIPLES.map((p) => p.title),
        ['docs/PRD.md', 'docs/ALM_PLAN.md', 'docs/adr/0002-runtime-is-github-copilot-coding-agent.md'],
        t,
      ),
    );
  return (
    <section className={s.root} data-testid="success-framework-section" aria-labelledby="success-framework-title">
      <SectionHeader
        id="success-framework"
        variant="eyebrow"
        {...(titleParts ? { titleParts } : { header })}
        tagline={t('backstage.story.narrative.success.tagline', 'Backstage \u00b7 Frontier Firm')}
        description={t('backstage.story.narrative.success.description', 'Curavias was built the way we ask hospitals to work: one human orchestrating a team of agents. The whole platform, spanning 39 sprints of requirements, architecture, code, infrastructure and compliance evidence, was delivered by a single person acting as an agent boss, with GitHub and Foundry agents doing the build.')}
      />
      <div className={s.split}>
        <div className={s.sfRows}>
          {SF_PRINCIPLES.map((p) => (
            <button key={p.n} type="button" className={s.sfRow} style={{ borderLeftColor: p.accent }} onClick={ask}>
              <span className={s.sfNum}>{p.n}</span>
              <span style={{ display: 'flex', flexDirection: 'column' }}>
                <span className={s.sfTitle}>{p.title}</span>
                <span className={s.sfBody}>{p.body}</span>
              </span>
            </button>
          ))}
        </div>
        <div className={s.panel}>
          <h3 className={s.panelTitle}>{t('backstage.story.narrative.success.numbersTitle', 'Our transformation, in numbers')}</h3>
          <div className={s.statGrid}>
            {SF_STATS.map((stat) => (
              <div key={stat.sub} className={s.statCell}>
                <span className={s.statValue} style={stat.color ? { color: stat.color } : undefined}>{stat.value}</span>
                <span className={s.statSub}>{stat.sub}</span>
              </div>
            ))}
          </div>
          <p className={s.note}>{t('backstage.story.narrative.success.numbersNote', 'Trunk-based parallel-sprint workflow: main is the baseline of truth, each sprint a worktree with its own Copilot CLI session, CI is the merge gate.')}</p>
        </div>
      </div>
    </section>
  );
}

export function DevSecOpsLoopSection() {
  const s = useStyles();
  const { t } = useTranslation();
  const rail = useRail();
  const header = t('backstage.story.narrative.devsecops.header', 'How the product is built and shipped');
  const titleParts = toTitleParts(
    header,
    t('backstage.story.narrative.devsecops.accent', 'built and shipped'),
  );
  const ask = () =>
    rail?.openWithReco(
      { id: 'backstage-devsecops', label: 'DevSecOps loop', context: { source: 'backstage-narrative', topic: 'devsecops' } },
      reco(
        'DevSecOps loop',
        'A product team of agents builds the platform through a governed DEV-OPS loop: plan, code, build and test on the DEV side; release, deploy, operate and monitor on the OPS side; with a Human-in-the-Loop gate (PR + Issue + approved-to-apply) at the centre and delivery promoted DEV to SIT to PROD behind an approval gate.',
        ['Human-in-the-loop gate (PR + Issue)', 'DEV to SIT to PROD promotion', 'Governance and security bands', 'GitHub + Copilot foundation'],
        ['docs/ALM_PLAN.md', 'docs/SECURITY.md'],
        t,
      ),
    );
  return (
    <section className={s.root} data-testid="devsecops-loop-section" aria-labelledby="devsecops-loop-title">
      <SectionHeader
        id="devsecops-loop"
        variant="eyebrow"
        {...(titleParts ? { titleParts } : { header })}
        tagline={t('backstage.story.narrative.devsecops.tagline', 'Backstage \u00b7 The Product Team (DevSecOps)')}
        description={t('backstage.story.narrative.devsecops.description', 'The DevSecOps team runs a governed DevOps loop. Superpowers turn an idea into a spec; security and compliance gates guard every change; a Human-in-the-Loop gate (PR + Issue) sits at the centre; delivery flows DEV to SIT to PROD behind an approval gate, all on a GitHub and Copilot foundation.')}
      />
      <button
        type="button"
        className={s.frameButton}
        onClick={ask}
        aria-label="Ask the Product Owner Agent about the DevSecOps loop"
      >
        <svg className={s.svg} viewBox="0 0 1000 560" role="img" aria-label="Curavias DevSecOps loop">
          <defs>
            <linearGradient id="dso-gd" x1="0" x2="1"><stop offset="0" stopColor="#22C08A" /><stop offset="1" stopColor="#17B890" /></linearGradient>
            <linearGradient id="dso-go" x1="0" x2="1"><stop offset="0" stopColor="#1FA9D6" /><stop offset="1" stopColor="#365B7D" /></linearGradient>
          </defs>
          <rect x="20" y="16" width="960" height="44" rx="10" fill="#f4f8fc" stroke="#dde6f1" />
          <text x="40" y="43" fill="#4453c9" fontSize="13" fontWeight="800">GOVERNANCE</text>
          <text x="150" y="43" fill="#516585" fontSize="12.5">{'Schemata \u00b7 Contracts \u00b7 Compliance gates \u00b7 ADRs'}</text>
          <text x="740" y="43" fill="#a97600" fontSize="12" fontWeight="700">{'SEC \u00b7 DSG \u00b7 PHI-Gates'}</text>
          <text x="40" y="96" fill="#0e8f6e" fontSize="12" fontWeight="800">{'SUPERPOWERS \u2014 PLAN gates'}</text>
          <rect x="40" y="106" width="120" height="34" rx="17" fill="#fff" stroke="#c7d5e6" /><text x="100" y="128" fill="#24405f" fontSize="12.5" textAnchor="middle">Brainstorm</text>
          <rect x="176" y="106" width="96" height="34" rx="17" fill="#fff" stroke="#c7d5e6" /><text x="224" y="128" fill="#24405f" fontSize="12.5" textAnchor="middle">Design</text>
          <rect x="288" y="106" width="80" height="34" rx="17" fill="#fff" stroke="#c7d5e6" /><text x="328" y="128" fill="#24405f" fontSize="12.5" textAnchor="middle">Spec</text>
          <path d="M160 123 h14 M272 123 h14" stroke="#17B890" strokeWidth="2" />
          <circle cx="330" cy="330" r="132" fill="none" stroke="url(#dso-gd)" strokeWidth="26" />
          <text x="330" y="322" textAnchor="middle" fill="#24405f" fontSize="40" fontWeight="800">DEV</text>
          <text x="330" y="352" textAnchor="middle" fill="#516585" fontSize="12.5">{'plan \u00b7 code \u00b7 build \u00b7 test'}</text>
          <g fontSize="11.5" fontWeight="700">
            <circle cx="330" cy="198" r="20" fill="#fff" stroke="#17B890" /><text x="330" y="202" textAnchor="middle" fill="#0e8f6e">PLAN</text>
            <circle cx="205" cy="290" r="20" fill="#fff" stroke="#17B890" /><text x="205" y="294" textAnchor="middle" fill="#0e8f6e">CODE</text>
            <circle cx="205" cy="378" r="20" fill="#fff" stroke="#17B890" /><text x="205" y="382" textAnchor="middle" fill="#0e8f6e">BUILD</text>
            <circle cx="330" cy="462" r="20" fill="#fff" stroke="#17B890" /><text x="330" y="466" textAnchor="middle" fill="#0e8f6e">TEST</text>
          </g>
          <circle cx="670" cy="330" r="132" fill="none" stroke="url(#dso-go)" strokeWidth="26" />
          <text x="670" y="322" textAnchor="middle" fill="#24405f" fontSize="40" fontWeight="800">OPS</text>
          <text x="670" y="352" textAnchor="middle" fill="#516585" fontSize="12.5">{'release \u00b7 deploy \u00b7 operate \u00b7 monitor'}</text>
          <g fontSize="10.5" fontWeight="700">
            <circle cx="670" cy="198" r="20" fill="#fff" stroke="#365B7D" /><text x="670" y="202" textAnchor="middle" fill="#365B7D">RELEASE</text>
            <circle cx="795" cy="290" r="20" fill="#fff" stroke="#365B7D" /><text x="795" y="294" textAnchor="middle" fill="#365B7D">DEPLOY</text>
            <circle cx="795" cy="378" r="20" fill="#fff" stroke="#365B7D" /><text x="795" y="382" textAnchor="middle" fill="#365B7D">OPERATE</text>
            <circle cx="670" cy="462" r="20" fill="#fff" stroke="#365B7D" /><text x="670" y="466" textAnchor="middle" fill="#365B7D">MONITOR</text>
          </g>
          <circle cx="500" cy="330" r="46" fill="#fff" stroke="#E8A200" strokeWidth="2.5" />
          <text x="500" y="326" textAnchor="middle" fill="#E8A200" fontSize="22" fontWeight="900">{'\u2713'}</text>
          <text x="500" y="345" textAnchor="middle" fill="#a97600" fontSize="9.5" fontWeight="800">HITL-GATE</text>
          <text x="500" y="404" textAnchor="middle" fill="#516585" fontSize="11">{'PR \u00b7 Issue \u00b7 approved-to-apply'}</text>
          <rect x="20" y="500" width="960" height="44" rx="10" fill="#f4f8fc" stroke="#dde6f1" />
          <text x="40" y="527" fill="#0e8f6e" fontSize="12" fontWeight="800">DELIVERY</text>
          <g fontSize="12.5" fontWeight="700">
            <rect x="140" y="510" width="70" height="24" rx="12" fill="#fff" stroke="#c7d5e6" /><text x="175" y="527" textAnchor="middle" fill="#24405f">DEV</text>
            <text x="222" y="527" fill="#7c8ca3">{'\u2192'}</text>
            <rect x="240" y="510" width="70" height="24" rx="12" fill="#fff" stroke="#c7d5e6" /><text x="275" y="527" textAnchor="middle" fill="#24405f">SIT</text>
            <rect x="326" y="508" width="96" height="28" rx="14" fill="#fff" stroke="#E8A200" /><text x="374" y="527" textAnchor="middle" fill="#a97600" fontSize="11">PR-GATE</text>
            <text x="436" y="527" fill="#7c8ca3">{'\u2192'}</text>
            <rect x="454" y="510" width="76" height="24" rx="12" fill="#fff" stroke="#c7d5e6" /><text x="492" y="527" textAnchor="middle" fill="#24405f">PROD</text>
          </g>
          <text x="620" y="527" fill="#516585" fontSize="11.5">{'Foundation: Platform landing zone \u00b7 GitHub DevOps \u00b7 GitHub Copilot \u00b7 Copilot CLI'}</text>
        </svg>
      </button>
      <div className={s.legend}>
        <span className={s.legendItem}><i className={s.sw} style={{ backgroundColor: '#17B890' }} />{' '}{'DEV loop \u2014 plan, code, build, test'}</span>
        <span className={s.legendItem}><i className={s.sw} style={{ background: 'linear-gradient(120deg,#1FA9D6,#365B7D)' }} />{' '}{'OPS loop \u2014 release, deploy, operate, monitor'}</span>
        <span className={s.legendItem}><i className={s.sw} style={{ backgroundColor: '#E8A200' }} />{' '}Human-in-the-loop gate</span>
        <span className={s.legendItem}><i className={s.sw} style={{ backgroundColor: '#5A6CF0' }} />{' '}Governance and security bands</span>
      </div>
    </section>
  );
}

const REVIEW_SESSIONS = [
  { id: 'coo', date: '2026-07-24' },
  { id: 'cio', date: '2026-07-17' },
  { id: 'ops', date: '2026-07-17' },
  { id: 'cto', date: '2026-06-09' },
  { id: 'ciso', date: '2026-06-10' },
  { id: 'it', date: '2026-06-08' },
] as const;

const PRACTITIONERS: {
  initials: string;
  color: string;
  name: string;
  role: string;
  href?: string;
  label?: string;
  photo?: string;
}[] = [
  { initials: 'RH', color: '#365B7D', name: 'Rebekka Hatzung', role: 'Chief Operation Officer / Stv. CEO, LUKS Luzern', href: 'https://www.luks.ch/spezialisten/rebekka-hatzung', label: 'Profile', photo: rebekkaHatzung },
  { initials: 'EF', color: '#17B890', name: 'Emanuel Furler', role: 'CIO, Leiter Informatik, Spitalleitung', href: 'https://spitalzollikerberg.ch/de/team/emanuel-furler', label: 'Profile', photo: emanuelFurler },
  { initials: 'CE', color: '#1FA9D6', name: 'Christian Ernst', role: 'Leiter Departement Notfall- und Akutmedizin, Spitalleitung', href: 'https://spitalzollikerberg.ch/de/team/christian-ernst', label: 'Profile', photo: christianErnst },
  { initials: 'RA', color: '#5A6CF0', name: 'Dr. Regula Adams', role: 'Senior Projektleiterin und Fachverantwortliche Organisationsentwicklung, Departement Notfall- und Akutmedizin', href: 'https://spitalzollikerberg.ch/de/team/regula-adams', label: 'Profile', photo: regulaAdams },
  { initials: 'MR', color: '#365B7D', name: 'Dr. med. Marco Rossi', role: 'Infektiologe und ehemaliger Chefarzt LUKS Luzern', href: 'https://www.luks.ch/newsroom/dr-med-marco-rossi-die-meisten-menschen-erholen-sich-wieder', label: 'Profile', photo: marcoRossi },
  { initials: 'PJ', color: '#17B890', name: 'Petrus Jallo', role: 'Cloud Solution Architect & Microsoft Technology Advisor', href: 'https://www.linkedin.com/in/petrus-jallo/', label: 'LinkedIn', photo: petrusJallo },
  { initials: 'RR', color: '#1FA9D6', name: 'Ren\u00e9 Raeber', role: 'CTO Microsoft Switzerland', href: 'https://www.linkedin.com/in/rraeber/', label: 'LinkedIn', photo: reneRaeber },
  { initials: 'DB', color: '#5A6CF0', name: 'Daniel von B\u00fcren', role: 'Swiss Security Officer & Solution Engineer, Microsoft Switzerland', href: 'https://www.linkedin.com/in/dvonbueren/', label: 'LinkedIn', photo: danielVonBueren },
  { initials: 'MW', color: '#17B890', name: 'Marco Weber', role: 'Cloud & AI Solution Engineer, Full-Stack Developer advisory', href: 'https://www.linkedin.com/in/marco-weber-ch/', label: 'LinkedIn', photo: marcoWeber },
];

export function ReviewSessionsSection() {
  const s = useStyles();
  const { t } = useTranslation();
  const header = t('backstage.story.narrative.reviews.header', 'Pressure-tested with real people, in real review sessions');
  const titleParts = toTitleParts(
    header,
    t('backstage.story.narrative.reviews.accent', 'real people'),
  );
  return (
    <section className={s.root} data-testid="review-sessions-section" aria-labelledby="review-sessions-title">
      <SectionHeader
        id="review-sessions"
        variant="eyebrow"
        {...(titleParts ? { titleParts } : { header })}
        tagline={t('backstage.story.narrative.reviews.tagline', 'Backstage \u00b7 this was a real exercise')}
        description={t('backstage.story.narrative.reviews.description', 'Curavias was challenged across a documented series of expert reviews and a named hospital field interview, each producing governance evidence.')}
      />
      <div className={s.panel}>
        <h3 className={s.panelTitle}>{t('backstage.story.narrative.reviews.tableTitle', 'Review sessions on record')}</h3>
        <table className={s.table}>
          <thead>
            <tr>
              <th className={s.th}>{t('backstage.story.narrative.reviews.colSession', 'Session')}</th>
              <th className={s.th}>{t('backstage.story.narrative.reviews.colDate', 'Date')}</th>
              <th className={s.th}>{t('backstage.story.narrative.reviews.colPerspective', 'Perspective challenged')}</th>
            </tr>
          </thead>
          <tbody>
            {REVIEW_SESSIONS.map((r) => (
              <tr key={r.id}>
                <td className={s.td}>
                  <span className={s.tdName}>{t(`backstage.story.narrative.reviews.sessions.${r.id}.name`)}</span>
                </td>
                <td className={s.td}>
                  <span className={s.tdDate}>{r.date}</span>
                </td>
                <td className={s.td}>{t(`backstage.story.narrative.reviews.sessions.${r.id}.persp`)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className={s.note}>{t('backstage.story.narrative.reviews.tableNote', 'Held at the Microsoft Innovation Hub, Zurich, and with hospital teams directly.')}</p>
      </div>
      <h3 className={s.subhead}>{t('backstage.story.narrative.reviews.peopleTitle', 'The real practitioners who took part')}</h3>
      <div className={s.peopleGrid}>
        {PRACTITIONERS.map((p) => (
          <div key={p.name} className={s.personCard}>
            {p.photo ? (
              <img className={s.personPhoto} src={p.photo} alt={p.name} width={38} height={38} />
            ) : (
              <span className={s.avatar} style={{ backgroundColor: p.color }}>{p.initials}</span>
            )}
            <span style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <span className={s.personName}>{p.name}</span>
              <span className={s.comp}>{p.role}</span>
              {p.href && (
                <a className={s.lk} href={p.href} target="_blank" rel="noopener noreferrer">
                  {p.label}
                </a>
              )}
            </span>
          </div>
        ))}
      </div>
      <p className={s.disc}>{t('backstage.story.narrative.reviews.attribution', 'Attribution note: named sessions and hospital references are drawn from the Curavias review record. Role-based challenge stances summarise what the sessions surfaced; several sessions recorded participants by role only. Named practitioners are shown with their consent to be credited.')}</p>
    </section>
  );
}

const PO_CLASSES = [
  { id: 'A', color: '#1FA9D6', name: 'Corpus', body: "The product's own documents and reviews - first-order source of truth." },
  { id: 'B', color: '#17B890', name: 'Live-proof', body: 'Read-only answers to reference questions, reconcile-and-flag.' },
  { id: 'C', color: '#E8A200', name: 'Cost', body: 'Effective PROD cloud + tooling cost reconciled to the BVA/TCO baseline.' },
  { id: 'D', color: '#5A6CF0', name: 'Ontology', body: 'Data questions answered with concept + data-binding citations.' },
] as const;

export function PoKnowledgeClassesSection() {
  const s = useStyles();
  const { t } = useTranslation();
  const rail = useRail();
  const header = t('backstage.story.narrative.poClasses.header', 'The Product Owner Agent handles the hard questions');
  const titleParts = toTitleParts(
    header,
    t('backstage.story.narrative.poClasses.accent', 'hard questions'),
  );
  const ask = () =>
    rail?.openWithReco(
      { id: 'backstage-po-classes', label: 'Product Owner Agent knowledge', context: { source: 'backstage-narrative', topic: 'po-classes' } },
      reco(
        'Product Owner Agent',
        'The docked Product Owner Agent grounds every answer on four knowledge classes: A corpus, B live-proof, C cost, and D ontology. Every answer is advisory-only, cited, in German and English, and never mutates a system.',
        PO_CLASSES.map((c) => `${c.id} - ${c.name}`),
        ['docs/adr/0043-product-owner-agent-foundry-iq-domain.md', 'docs/AI.md'],
        t,
      ),
    );
  return (
    <section className={s.root} data-testid="po-classes-section" aria-labelledby="po-classes-title">
      <SectionHeader
        id="po-classes"
        variant="eyebrow"
        {...(titleParts ? { titleParts } : { header })}
        tagline={t('backstage.story.narrative.poClasses.tagline', 'Backstage \u00b7 answers on demand')}
        description={t('backstage.story.narrative.poClasses.description', 'Embedded as a Copilot rail on the Start and Backstage surfaces, the PO Agent answers grounded on four knowledge classes, with mandatory citations, in German and English, advisory-only, and it never mutates a system.')}
      />
      <div className={s.classGrid}>
        {PO_CLASSES.map((c) => (
          <button key={c.id} type="button" className={s.classCard} style={{ borderLeftColor: c.color }} onClick={ask}>
            <span className={s.classHead}>
              <span className={s.letterTag} style={{ backgroundColor: c.color }}>{c.id}</span>
              <span className={s.classTitle}>{c.name}</span>
            </span>
            <span className={s.classBody}>{c.body}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
