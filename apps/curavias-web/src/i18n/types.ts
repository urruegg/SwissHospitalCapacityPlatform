// Typed content model for the Curavias landing page.
// One object of this shape exists per locale (de/en/fr/it) under src/i18n/<locale>.ts.
// DE-CH is the source of truth; other locales are translated from it (Phase 3).

export type Locale = 'de' | 'en' | 'fr' | 'it';

export interface NavItem {
  href: string;
  label: string;
}

export interface Kpi {
  value: string;
  label: string;
}

export interface PathStep {
  index: string;
  phase: string;
  role: string;
  agent: string;
  focus: string;
}

export interface Agent {
  name: string;
  code: string;
  role: string;
  delivers: string;
  gate: string;
}

export interface Experience {
  title: string;
  body: string;
}

export interface DecisionRow {
  decision: string;
  today: string;
  withCuravias: string;
}

export interface TrustPillar {
  title: string;
  body: string;
}

export interface ValueRow {
  lever: string;
  amount: string;
  rationale: string;
  emphasis?: boolean;
}

export interface CtaStep {
  title: string;
  body: string;
}

export interface SiteContent {
  locale: Locale;
  htmlLang: string;
  meta: {
    title: string;
    description: string;
  };
  nav: {
    items: NavItem[];
    cta: string;
    skip: string;
    langLabel: string;
  };
  hero: {
    eyebrow: string;
    headline: string;
    subhead: string;
    ctaPrimary: string;
    ctaSecondary: string;
  };
  disclaimer: {
    badge: string;
    text: string;
  };
  kpis: {
    heading: string;
    items: Kpi[];
  };
  summary: {
    eyebrow: string;
    heading: string;
    question: string;
    body: string;
  };
  challenger: {
    eyebrow: string;
    heading: string;
    quote: string;
    tableHead: { decision: string; today: string; withCuravias: string };
    rows: DecisionRow[];
  };
  path: {
    eyebrow: string;
    heading: string;
    intro: string;
    steps: PathStep[];
    laneLabel: string;
    lanes: string[];
    governance: string;
  };
  agents: {
    eyebrow: string;
    heading: string;
    intro: string;
    gateLabel: string;
    items: Agent[];
  };
  experiences: {
    eyebrow: string;
    heading: string;
    items: Experience[];
  };
  trust: {
    eyebrow: string;
    heading: string;
    pillars: TrustPillar[];
    keyMessage: string;
  };
  value: {
    eyebrow: string;
    heading: string;
    tableHead: { lever: string; amount: string; rationale: string };
    rows: ValueRow[];
    caveat: string;
  };
  cta: {
    eyebrow: string;
    heading: string;
    steps: CtaStep[];
    contact: string;
    contactCta: string;
  };
  footer: {
    tagline: string;
    origin: string;
    poweredBy: string;
    legalHeading: string;
    legal: string;
    imprint: string;
    privacy: string;
  };
}
