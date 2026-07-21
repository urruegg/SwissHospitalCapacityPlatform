import type { SiteContent } from './types';

// DE-CH — source of truth. Copy sourced from the Curavias context pack
// (docs/superpowers/ideas/curavias-product-webpage/curavias-bom/curavias-context.md).
export const de: SiteContent = {
  locale: 'de',
  htmlLang: 'de-CH',
  meta: {
    title: 'Curavias — Die AI-Copilot-Plattform für den operativen Alltag im Spital',
    description:
      'Curavias ist ein Showcase des Microsoft Innovation Hub Zürich: verlässliche Vorschau, erklärbare Empfehlung, der Mensch entscheidet. Beratende KI, synthetische Daten, kein Medizinprodukt.',
  },
  nav: {
    items: [
      { href: '#kurzueberblick', label: 'Überblick' },
      { href: '#agenten', label: 'Agenten' },
      { href: '#erlebnisse', label: 'Erlebnisse' },
      { href: '#sicherheit', label: 'Sicherheit' },
      { href: '#nutzen', label: 'Nutzen' },
    ],
    cta: 'Demo ansehen',
    skip: 'Zum Inhalt springen',
    langLabel: 'Sprache',
  },
  hero: {
    eyebrow: 'Swiss Hospital Capacity Copilot · Produktübersicht',
    headline: 'Die AI-Copilot-Plattform für den operativen Alltag im Spital',
    subhead: 'Verlässliche Vorschau. Erklärbare Empfehlung. Der Mensch entscheidet.',
    ctaPrimary: 'Demo ansehen',
    ctaSecondary: 'Video ansehen',
  },
  disclaimer: {
    badge: 'Showcase',
    text: 'Kein reales Produkt. Curavias ist ein Showcase des Microsoft Innovation Hub Zürich — synthetische Daten, beratende KI (advisory-only), kein Medizinprodukt und nicht für den klinischen Einsatz.',
  },
  kpis: {
    heading: 'Curavias in Zahlen',
    items: [
      { value: '≈ 3.5 Mio. CHF', label: 'jährlicher Zielnutzen (ROM)' },
      { value: '127 %', label: 'ROI über 3 Jahre' },
      { value: '7', label: 'spezialisierte AI-Copiloten' },
    ],
  },
  summary: {
    eyebrow: 'Das Wichtigste in Kürze',
    heading: 'Wo werden wir morgen unter Druck stehen — und was können wir heute tun?',
    question:
      '«Wo werden wir morgen und übermorgen unter Druck stehen — und was können wir heute schon tun?»',
    body:
      'Curavias beantwortet die Kernfrage jeder Spitalleitung mit einer verlässlichen 3–7-Tage-Vorschau über Bettenbelegung, OP-Auslastung, Notfall-Ankünfte, Entlassungspotenzial und Personaldeckung. Jede Empfehlung ist beratend und wird durch den Menschen (Human-in-the-Loop) freigegeben.',
  },
  challenger: {
    eyebrow: 'CIO-Challenger',
    heading: 'Sieben operative Entscheidungen — heute vs. mit Curavias-Vorschau',
    quote:
      '«Welche operativen Entscheidungen könnten heute besser getroffen werden, wenn die zukünftige Kapazitäts- und Auslastungssituation 3 bis 7 Tage im Voraus mit hoher Zuverlässigkeit bekannt wäre?»',
    tableHead: { decision: 'Operative Entscheidung', today: 'Heute', withCuravias: 'Mit Curavias-Vorschau' },
    rows: [
      { decision: 'Bettenzuweisung', today: 'Reaktiv am Aufnahmemorgen, unter Zeitdruck', withCuravias: '3–7 Tage vorausschauend — geplant statt improvisiert' },
      { decision: 'OP-Slot-Nutzung', today: 'Absagen/Leerslots werden am OP-Tag entdeckt', withCuravias: 'Ausfallrisiko & Umverteilung Tage im Voraus sichtbar' },
      { decision: 'Personalabdeckung', today: 'Kurzfristiger Pool, teure Agenturzuschläge', withCuravias: 'Dienstpläne auf prognostizierten Bedarf abgestimmt' },
      { decision: 'Entlassungssteuerung', today: 'Am Vormittag nicht abschätzbar', withCuravias: 'Kandidaten mit Blockern & Handoff 24–72 h vorher' },
      { decision: 'Verlegungen / Aufnahmestopp', today: 'Ad-hoc, Kommunikation unter Zeitdruck', withCuravias: 'Kaskaden simuliert, Partner früh eingebunden' },
      { decision: 'Krisen- & Szenario-Antworten', today: 'Doktrin liegt im Ordner', withCuravias: 'Doktrin-basierte Empfehlungen, szenariogetrieben' },
      { decision: 'Datenqualitäts-Alarme', today: 'Fallen erst im KPI-Report auf', withCuravias: 'Gates alarmieren, bevor eine Kennzahl in Entscheidungen fliesst' },
    ],
  },
  path: {
    eyebrow: 'Der Curavias Patienten-Pfad',
    heading: 'Vom Eintritt zum Erfolg',
    intro: 'Rollen und AI-Agenten entlang der Behandlung — von der Notfallaufnahme bis zur Genesung.',
    steps: [
      { index: '1', phase: 'Notfall & Aufnahme', role: 'Notfall-Leitung', agent: 'OOA', focus: '72-h-Forecast' },
      { index: '2', phase: 'Bettenzuweisung', role: 'Bettenmanagement', agent: 'BMCA', focus: 'Bettendruck & Kandidaten' },
      { index: '3', phase: 'OP & Behandlung', role: 'OP-Koordination', agent: 'ORSA', focus: 'OP-Slate-Steuerung' },
      { index: '4', phase: 'Pflege & Personal', role: 'Personalplanung', agent: 'SBA', focus: 'Roster vs. Forecast' },
      { index: '5', phase: 'Entlassung', role: 'Entlassungskoordination', agent: 'DCA', focus: 'Ranking & Handoff' },
      { index: '✓', phase: 'Erfolg', role: 'Patient ist genesen', agent: '—', focus: 'Ziel erreicht' },
    ],
    laneLabel: 'Querschnitts-Agenten',
    lanes: ['CSA — Krisen & Szenarien', 'DQ — Datenqualität (Gates)'],
    governance: 'Human-in-the-Loop — jede Aktion mit Aussenwirkung wird freigegeben. Der Mensch entscheidet.',
  },
  agents: {
    eyebrow: 'Die sieben Curavias-Agenten',
    heading: 'Sieben spezialisierte Copiloten — ein gemeinsamer Grundsatz',
    intro: 'Jeder Agent berät eine konkrete Rolle mit erklärbaren Vorschlägen. Aktionen mit Aussenwirkung durchlaufen ein Human-in-the-Loop-Gate.',
    gateLabel: 'HITL-Gate',
    items: [
      { name: 'Bettenmanagement-Copilot', code: 'BMCA', role: 'Bettenmanagement', delivers: 'Belegung, Bettendruck, Verlegungs- und Same-Day-Kandidaten — erklärbar.', gate: 'Bettenverlegung' },
      { name: 'Belegungs- & Forecast-Copilot', code: 'OOA', role: 'Notfall-Leitung, Ops Lead', delivers: '72-h-Prognose von Ankünften & Belegung je Fachbereich.', gate: 'Kapazität' },
      { name: 'Entlassungs-Copilot', code: 'DCA', role: 'Entlassungskoordination', delivers: 'Ranking der Entlassungskandidaten mit Blockern & Handoff-Status.', gate: 'Cross-org. Handoff' },
      { name: 'OP-Steuerungs-Copilot', code: 'ORSA', role: 'OP-Koordination', delivers: 'Leere OP-Slots, Slate-Umverteilung, Absagerisiko.', gate: 'OP-Slate-Änderung' },
      { name: 'Personal-Balance-Copilot', code: 'SBA', role: 'Personalplanung', delivers: 'Heatmap der Personallücken, Roster-vs-Forecast-Delta.', gate: 'Personal' },
      { name: 'Krisen- & Szenario-Copilot', code: 'CSA', role: 'Krisen-/Diensthabende', delivers: 'Szenario-Bewertung gegen den Schweizer Lage-Klassifikator.', gate: 'Politik-Ausnahme' },
      { name: 'Datenqualitäts-Agent', code: 'DQ', role: 'Data / Ontology Steward', delivers: 'Bronze→Silber→Gold-Gates, Drift-Alarme; PHI-Gates nicht deaktivierbar.', gate: 'PHI-Ausnahme' },
    ],
  },
  experiences: {
    eyebrow: 'Die drei Erlebnisse',
    heading: 'So fühlt sich Curavias an',
    items: [
      { title: 'Copilot-Drawer', body: 'Frage in natürlicher Sprache, geerdete Antwort mit Quelle.' },
      { title: 'Whiteboard', body: 'Konfigurierbares Live-Command-Center pro Rolle.' },
      { title: 'Human-in-the-Loop', body: 'Jede Aktion mit Aussenwirkung wird protokolliert und freigegeben.' },
    ],
  },
  trust: {
    eyebrow: 'Datenhoheit, Sicherheit, Regulatorik',
    heading: 'In Schweizer Händen — vertrauenswürdig ab Tag 1',
    pillars: [
      { title: 'Provider-internes Deployment', body: 'Eine Instanz pro Spital-Provider, keine geteilte Tenancy.' },
      { title: 'Schweizer Region', body: 'Betrieb auf Microsoft Azure in Schweizer Rechenzentren (Switzerland North); Datenresidenz gelöst.' },
      { title: 'PHI-Schutz eingebaut', body: 'Bronze→Silber→Gold-Pipeline mit nicht überschreibbaren PHI-Gates; geerdete Copilot-Antworten.' },
      { title: 'HL7 FHIR-nativ', body: 'Standardisierte Interoperabilität mit KIS, Labor und Nachversorgungs-Partnern.' },
      { title: 'Entra-basierte Identität', body: 'Spital-Rollen auf App-Rollen abgebildet; jede Aktion authentifiziert und im Audit-Log nachweisbar.' },
      { title: 'Advisory-only-Doktrin', body: 'Agenten entscheiden nicht, sie beraten die entscheidungsbefugte Person.' },
    ],
    keyMessage: 'Verlässliche Vorschau + erklärbare Empfehlung + Human-in-the-Loop = belastbar für DSG, ISO 27001 und Schweizer Compliance ab Tag 1.',
  },
  value: {
    eyebrow: 'Wirtschaftlicher Nutzen (BVA)',
    heading: 'Business Value — 3-Jahres-ROM (±30 %)',
    tableHead: { lever: 'Werthebel', amount: 'Jahresnutzen (CHF)', rationale: 'Begründung' },
    rows: [
      { lever: 'Weniger blockierte Bett-Tage & Entlassungs-Verzögerungen', amount: "1'650'000", rationale: 'Schnellere Koordination, frühere Handoffs' },
      { lever: 'Produktivität im Command-Center', amount: "980'000", rationale: '120 Spitzennutzer, weniger manuelle Triage' },
      { lever: 'Weniger Überstunden & Agentur-Zuschläge', amount: "620'000", rationale: 'Prognoseinformierte Personalplanung' },
      { lever: 'Effizienz in Compliance & Audit', amount: "220'000", rationale: 'Evidence-ready Controls' },
      { lever: 'Jährlicher Bruttonutzen', amount: "≈ 3'470'000", rationale: 'Werthebel-Summe', emphasis: true },
      { lever: '3-Jahres-Nettowert', amount: "6'410'000", rationale: 'nach TCO für 3 Jahre', emphasis: true },
      { lever: 'ROI (Base-ROM, 3 Jahre)', amount: '127 %', rationale: 'Balanced-Adoption-Profil', emphasis: true },
    ],
    caveat: 'ROM-Werte für Business-Case-Gespräche, nicht als finale Angebots-Grundlage.',
  },
  cta: {
    eyebrow: 'Nächste Schritte',
    heading: 'In drei Schritten zum Curavias-Discovery',
    steps: [
      { title: 'Review-Session (60 min)', body: 'Gemeinsame Sichtung der Vorschau- und Empfehlungslogik an Ihren Fragestellungen.' },
      { title: 'Discovery entlang der 7 Agenten', body: 'Welche Copiloten heben in Ihrem Betrieb den grössten Nutzen?' },
      { title: 'Roadmap-Skizze', body: 'Ein pragmatischer Fahrplan von Showcase zu Pilot — mit Ihren Rahmenbedingungen.' },
    ],
    contact: 'Interesse an einer Review-Session?',
    contactCta: 'Kontakt aufnehmen',
  },
  footer: {
    tagline: 'Curavias — verlässliche Vorschau. Erklärbare Empfehlung. Der Mensch entscheidet.',
    origin: 'Microsoft Innovation Hub Zürich — Showcase',
    poweredBy: 'Powered by Microsoft',
    legalHeading: 'Rechtlicher Hinweis',
    legal: 'Kein reales Produkt. Curavias ist ein Showcase mit synthetischen Daten, beratender KI (advisory-only), kein Medizinprodukt und nicht für den klinischen Einsatz.',
    imprint: 'Impressum',
    privacy: 'Datenschutz',
  },
};
