import type { SiteContent } from './types';

// EN — translated from the DE-CH source of truth (src/i18n/de.ts).
// Advisory voice: "previews / recommends / suggests", never "decides / diagnoses".
export const en: SiteContent = {
  locale: 'en',
  htmlLang: 'en',
  meta: {
    title: 'Curavias — The AI copilot platform for daily hospital operations',
    description:
      'Curavias is a Microsoft Innovation Hub Zürich showcase: reliable preview, explainable recommendation, the human decides. Advisory-only AI, synthetic data, not a medical device.',
  },
  nav: {
    items: [
      { href: '#kurzueberblick', label: 'Overview' },
      { href: '#agenten', label: 'Agents' },
      { href: '#erlebnisse', label: 'Experiences' },
      { href: '#sicherheit', label: 'Security' },
      { href: '#nutzen', label: 'Value' },
    ],
    cta: 'See the demo',
    skip: 'Skip to content',
    langLabel: 'Language',
  },
  hero: {
    eyebrow: 'Swiss Hospital Capacity Copilot · Product overview',
    headline: 'The AI copilot platform for daily hospital operations',
    subhead: 'Reliable preview. Explainable recommendation. The human decides.',
    ctaPrimary: 'See the demo',
    ctaSecondary: 'Watch the video',
  },
  disclaimer: {
    badge: 'Showcase',
    text: 'Not a real product. Curavias is a Microsoft Innovation Hub Zürich showcase — synthetic data, advisory-only AI, not a medical device and not for clinical use.',
  },
  kpis: {
    heading: 'Curavias in numbers',
    items: [
      { value: '≈ CHF 3.5m', label: 'annual target benefit (ROM)' },
      { value: '127 %', label: 'ROI over 3 years' },
      { value: '7', label: 'specialised AI copilots' },
    ],
  },
  summary: {
    eyebrow: 'The essentials',
    heading: 'Where will we be under pressure tomorrow — and what can we do today?',
    question:
      '“Where will we be under pressure tomorrow and the day after — and what can we already do today?”',
    body:
      'Curavias answers the core question of every hospital leadership with a reliable 3–7-day preview across bed occupancy, OR utilisation, emergency arrivals, discharge potential and staffing. Every recommendation is advisory and released by a human (human-in-the-loop).',
  },
  challenger: {
    eyebrow: 'CIO challenger',
    heading: 'Seven operational decisions — today vs. with the Curavias preview',
    quote:
      '“Which operational decisions could be made better today if the future capacity and utilisation situation were known 3 to 7 days in advance with high reliability?”',
    tableHead: { decision: 'Operational decision', today: 'Today', withCuravias: 'With the Curavias preview' },
    rows: [
      { decision: 'Bed allocation', today: 'Reactive on the morning of admission, under time pressure', withCuravias: '3–7 days ahead — planned instead of improvised' },
      { decision: 'OR slot usage', today: 'Cancellations/empty slots discovered on the day of surgery', withCuravias: 'Cancellation risk & re-allocation visible days ahead' },
      { decision: 'Staffing coverage', today: 'Short-notice pool, expensive agency surcharges', withCuravias: 'Rosters aligned to forecast demand' },
      { decision: 'Discharge steering', today: 'Not assessable in the morning', withCuravias: 'Candidates with blockers & handoff 24–72 h ahead' },
      { decision: 'Transfers / admission stop', today: 'Ad-hoc, communication under time pressure', withCuravias: 'Cascades simulated, partners engaged early' },
      { decision: 'Crisis & scenario responses', today: 'Doctrine sits in a folder', withCuravias: 'Doctrine-based, scenario-driven recommendations' },
      { decision: 'Data-quality alerts', today: 'Only surface in the KPI report', withCuravias: 'Gates alert before a metric flows into decisions' },
    ],
  },
  path: {
    eyebrow: 'The Curavias patient path',
    heading: 'From admission to recovery',
    intro: 'Roles and AI agents along the treatment — from emergency admission to recovery.',
    steps: [
      { index: '1', phase: 'Emergency & admission', role: 'Emergency lead', agent: 'OOA', focus: '72-h forecast' },
      { index: '2', phase: 'Bed allocation', role: 'Bed management', agent: 'BMCA', focus: 'Bed pressure & candidates' },
      { index: '3', phase: 'OR & treatment', role: 'OR coordination', agent: 'ORSA', focus: 'OR-slate steering' },
      { index: '4', phase: 'Care & staffing', role: 'Staff planning', agent: 'SBA', focus: 'Roster vs. forecast' },
      { index: '5', phase: 'Discharge', role: 'Discharge coordination', agent: 'DCA', focus: 'Ranking & handoff' },
      { index: '✓', phase: 'Success', role: 'Patient has recovered', agent: '—', focus: 'Goal reached' },
    ],
    laneLabel: 'Cross-cutting agents',
    lanes: ['CSA — crisis & scenarios', 'DQ — data quality (gates)'],
    governance: 'Human-in-the-loop — every action with external effect is released. The human decides.',
  },
  agents: {
    eyebrow: 'The seven Curavias agents',
    heading: 'Seven specialised copilots — one shared principle',
    intro: 'Each agent advises a specific role with explainable suggestions. Actions with external effect pass a human-in-the-loop gate.',
    gateLabel: 'HITL gate',
    items: [
      { name: 'Bed-management copilot', code: 'BMCA', role: 'Bed management', delivers: 'Occupancy, bed pressure, transfer and same-day candidates — explainable.', gate: 'Bed transfer' },
      { name: 'Occupancy & forecast copilot', code: 'OOA', role: 'Emergency lead, ops lead', delivers: '72-h forecast of arrivals & occupancy per specialty.', gate: 'Capacity' },
      { name: 'Discharge copilot', code: 'DCA', role: 'Discharge coordination', delivers: 'Ranking of discharge candidates with blockers & handoff status.', gate: 'Cross-org handoff' },
      { name: 'OR-steering copilot', code: 'ORSA', role: 'OR coordination', delivers: 'Empty OR slots, slate re-allocation, cancellation risk.', gate: 'OR-slate change' },
      { name: 'Staff-balance copilot', code: 'SBA', role: 'Staff planning', delivers: 'Heatmap of staffing gaps, roster-vs-forecast delta.', gate: 'Staffing' },
      { name: 'Crisis & scenario copilot', code: 'CSA', role: 'Crisis / on-call', delivers: 'Scenario assessment against the Swiss situation classifier.', gate: 'Policy exception' },
      { name: 'Data-quality agent', code: 'DQ', role: 'Data / ontology steward', delivers: 'Bronze→Silver→Gold gates, drift alerts; PHI gates cannot be disabled.', gate: 'PHI exception' },
    ],
  },
  experiences: {
    eyebrow: 'The three experiences',
    heading: 'How Curavias feels',
    items: [
      { title: 'Copilot drawer', body: 'Ask in natural language, get a grounded answer with its source.' },
      { title: 'Whiteboard', body: 'A configurable live command centre per role.' },
      { title: 'Human-in-the-loop', body: 'Every action with external effect is logged and released.' },
    ],
  },
  trust: {
    eyebrow: 'Data sovereignty, security, regulatory',
    heading: 'In Swiss hands — trustworthy from day one',
    pillars: [
      { title: 'Provider-internal deployment', body: 'One instance per hospital provider, no shared tenancy.' },
      { title: 'Swiss region', body: 'Operated on Microsoft Azure in Swiss data centres (Switzerland North); data residency solved.' },
      { title: 'PHI protection built in', body: 'Bronze→Silver→Gold pipeline with non-overridable PHI gates; grounded copilot answers.' },
      { title: 'HL7 FHIR-native', body: 'Standardised interoperability with HIS, lab and post-acute-care partners.' },
      { title: 'Entra-based identity', body: 'Hospital roles mapped to app roles; every action authenticated and auditable.' },
      { title: 'Advisory-only doctrine', body: 'Agents do not decide, they advise the person with decision authority.' },
    ],
    keyMessage: 'Reliable preview + explainable recommendation + human-in-the-loop = robust for FADP, ISO 27001 and Swiss compliance from day one.',
  },
  value: {
    eyebrow: 'Business value (BVA)',
    heading: 'Business value — 3-year ROM (±30 %)',
    tableHead: { lever: 'Value lever', amount: 'Annual benefit (CHF)', rationale: 'Rationale' },
    rows: [
      { lever: 'Fewer blocked bed-days & discharge delays', amount: "1'650'000", rationale: 'Faster coordination, earlier handoffs' },
      { lever: 'Command-centre productivity', amount: "980'000", rationale: '120 peak users, less manual triage' },
      { lever: 'Fewer overtime & agency surcharges', amount: "620'000", rationale: 'Forecast-informed staff planning' },
      { lever: 'Compliance & audit efficiency', amount: "220'000", rationale: 'Evidence-ready controls' },
      { lever: 'Annual gross benefit', amount: "≈ 3'470'000", rationale: 'Sum of value levers', emphasis: true },
      { lever: '3-year net value', amount: "6'410'000", rationale: 'after TCO over 3 years', emphasis: true },
      { lever: 'ROI (base ROM, 3 years)', amount: '127 %', rationale: 'Balanced-adoption profile', emphasis: true },
    ],
    caveat: 'ROM figures for business-case conversations, not a final basis for an offer.',
  },
  cta: {
    eyebrow: 'Next steps',
    heading: 'To a Curavias discovery in three steps',
    steps: [
      { title: 'Review session (60 min)', body: 'A joint look at the preview and recommendation logic against your questions.' },
      { title: 'Discovery along the 7 agents', body: 'Which copilots create the greatest value in your operations?' },
      { title: 'Roadmap sketch', body: 'A pragmatic path from showcase to pilot — with your constraints.' },
    ],
    contact: 'Interested in a review session?',
    contactCta: 'Get in touch',
  },
  footer: {
    tagline: 'Curavias — reliable preview. Explainable recommendation. The human decides.',
    origin: 'Microsoft Innovation Hub Zürich — Showcase',
    poweredBy: 'Powered by Microsoft',
    legalHeading: 'Legal notice',
    legal: 'Not a real product. Curavias is a showcase with synthetic data, advisory-only AI, not a medical device and not for clinical use.',
    imprint: 'Imprint',
    privacy: 'Privacy',
  },
};
