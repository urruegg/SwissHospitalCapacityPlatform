import type { SiteContent } from './types';

// IT — tradotto dalla fonte DE-CH (src/i18n/de.ts).
// Voce consultiva: « prevede / raccomanda / suggerisce », mai « decide / diagnostica ».
export const it: SiteContent = {
  locale: 'it',
  htmlLang: 'it',
  meta: {
    title: 'Curavias — La piattaforma copilota IA per la quotidianità ospedaliera',
    description:
      "Curavias è una vetrina del Microsoft Innovation Hub Zürich: previsione affidabile, raccomandazione spiegabile, l'essere umano decide. IA consultiva, dati sintetici, non un dispositivo medico.",
  },
  nav: {
    items: [
      { href: '#kurzueberblick', label: 'Panoramica' },
      { href: '#agenten', label: 'Agenti' },
      { href: '#erlebnisse', label: 'Esperienze' },
      { href: '#sicherheit', label: 'Sicurezza' },
      { href: '#nutzen', label: 'Valore' },
    ],
    cta: 'Guarda la demo',
    skip: 'Vai al contenuto',
    langLabel: 'Lingua',
  },
  hero: {
    eyebrow: 'Swiss Hospital Capacity Copilot · Panoramica del prodotto',
    headline: 'La piattaforma copilota IA per la quotidianità ospedaliera',
    subhead: "Previsione affidabile. Raccomandazione spiegabile. L'essere umano decide.",
    ctaPrimary: 'Guarda la demo',
    ctaSecondary: 'Guarda il video',
  },
  disclaimer: {
    badge: 'Vetrina',
    text: "Non è un prodotto reale. Curavias è una vetrina del Microsoft Innovation Hub Zürich — dati sintetici, IA solo consultiva, non un dispositivo medico e non destinato all'uso clinico.",
  },
  kpis: {
    heading: 'Curavias in cifre',
    items: [
      { value: '≈ 3,5 mln CHF', label: 'beneficio annuo target (ROM)' },
      { value: '127 %', label: 'ROI su 3 anni' },
      { value: '7', label: 'copiloti IA specializzati' },
    ],
  },
  summary: {
    eyebrow: "L'essenziale",
    heading: 'Dove saremo sotto pressione domani — e cosa possiamo fare oggi?',
    question:
      '« Dove saremo sotto pressione domani e dopodomani — e cosa possiamo già fare oggi? »',
    body:
      "Curavias risponde alla domanda centrale di ogni direzione ospedaliera con una previsione affidabile a 3–7 giorni su occupazione dei letti, utilizzo delle sale operatorie, arrivi al pronto soccorso, potenziale di dimissione e personale. Ogni raccomandazione è consultiva e rilasciata da un essere umano (human-in-the-loop).",
  },
  challenger: {
    eyebrow: 'Domanda del CIO',
    heading: 'Sette decisioni operative — oggi vs. con la previsione Curavias',
    quote:
      '« Quali decisioni operative potrebbero essere prese meglio oggi se la futura situazione di capacità e carico fosse nota con 3–7 giorni di anticipo e alta affidabilità? »',
    tableHead: { decision: 'Decisione operativa', today: 'Oggi', withCuravias: 'Con la previsione Curavias' },
    rows: [
      { decision: 'Assegnazione dei letti', today: "Reattiva la mattina del ricovero, sotto pressione", withCuravias: '3–7 giorni in anticipo — pianificato anziché improvvisato' },
      { decision: 'Utilizzo degli slot in sala operatoria', today: 'Cancellazioni/slot vuoti scoperti il giorno dell’intervento', withCuravias: 'Rischio di annullamento & riallocazione visibili con giorni di anticipo' },
      { decision: 'Copertura del personale', today: 'Pool dell’ultimo minuto, costosi supplementi di agenzia', withCuravias: 'Turni allineati alla domanda prevista' },
      { decision: 'Gestione delle dimissioni', today: 'Non stimabile al mattino', withCuravias: 'Candidati con blocchi & handoff 24–72 h prima' },
      { decision: 'Trasferimenti / stop ricoveri', today: 'Ad hoc, comunicazione sotto pressione', withCuravias: 'Cascate simulate, partner coinvolti in anticipo' },
      { decision: 'Risposte a crisi & scenari', today: 'La dottrina resta in un raccoglitore', withCuravias: 'Raccomandazioni basate sulla dottrina, guidate dagli scenari' },
      { decision: 'Allerte sulla qualità dei dati', today: 'Emergono solo nel report KPI', withCuravias: 'I gate allertano prima che un indicatore entri nelle decisioni' },
    ],
  },
  path: {
    eyebrow: 'Il percorso del paziente Curavias',
    heading: 'Dal ricovero alla guarigione',
    intro: 'Ruoli e agenti IA lungo il trattamento — dal ricovero in pronto soccorso alla guarigione.',
    steps: [
      { index: '1', phase: 'Emergenza & ricovero', role: 'Direzione pronto soccorso', agent: 'OOA', focus: 'Previsione 72 h' },
      { index: '2', phase: 'Assegnazione dei letti', role: 'Gestione letti', agent: 'BMCA', focus: 'Pressione & candidati' },
      { index: '3', phase: 'Sala operatoria & trattamento', role: 'Coordinamento sala operatoria', agent: 'ORSA', focus: 'Gestione del programma' },
      { index: '4', phase: 'Cura & personale', role: 'Pianificazione del personale', agent: 'SBA', focus: 'Turni vs. previsione' },
      { index: '5', phase: 'Dimissione', role: 'Coordinamento dimissioni', agent: 'DCA', focus: 'Classifica & handoff' },
      { index: '✓', phase: 'Successo', role: 'Il paziente è guarito', agent: '—', focus: 'Obiettivo raggiunto' },
    ],
    laneLabel: 'Agenti trasversali',
    lanes: ['CSA — crisi & scenari', 'DQ — qualità dei dati (gate)'],
    governance: "Human-in-the-loop — ogni azione con effetto esterno viene rilasciata. L'essere umano decide.",
  },
  agents: {
    eyebrow: 'I sette agenti Curavias',
    heading: 'Sette copiloti specializzati — un principio comune',
    intro: "Ogni agente assiste un ruolo preciso con suggerimenti spiegabili. Le azioni con effetto esterno passano da un gate human-in-the-loop.",
    gateLabel: 'Gate HITL',
    items: [
      { name: 'Copilota gestione letti', code: 'BMCA', role: 'Gestione letti', delivers: 'Occupazione, pressione, candidati a trasferimento e dimissione in giornata — spiegabile.', gate: 'Trasferimento letto' },
      { name: 'Copilota occupazione & previsione', code: 'OOA', role: 'Direzione PS, ops', delivers: 'Previsione a 72 h di arrivi & occupazione per specialità.', gate: 'Capacità' },
      { name: 'Copilota dimissioni', code: 'DCA', role: 'Coordinamento dimissioni', delivers: 'Classifica dei candidati alla dimissione con blocchi & stato di handoff.', gate: 'Handoff inter-org.' },
      { name: 'Copilota gestione sala operatoria', code: 'ORSA', role: 'Coordinamento sala operatoria', delivers: 'Slot vuoti, riallocazione del programma, rischio di annullamento.', gate: 'Modifica programma' },
      { name: 'Copilota bilanciamento personale', code: 'SBA', role: 'Pianificazione del personale', delivers: 'Mappa termica delle carenze, delta turni-vs-previsione.', gate: 'Personale' },
      { name: 'Copilota crisi & scenari', code: 'CSA', role: 'Crisi / reperibilità', delivers: 'Valutazione di scenari secondo il classificatore svizzero della situazione.', gate: 'Eccezione politica' },
      { name: 'Agente qualità dei dati', code: 'DQ', role: 'Data / ontology steward', delivers: 'Gate Bronzo→Argento→Oro, allerte di drift; gate PHI non disattivabili.', gate: 'Eccezione PHI' },
    ],
  },
  experiences: {
    eyebrow: 'Le tre esperienze',
    heading: 'Come si percepisce Curavias',
    items: [
      { title: 'Cassetto copilota', body: 'Fai una domanda in linguaggio naturale, ottieni una risposta ancorata con la sua fonte.' },
      { title: 'Whiteboard', body: 'Un centro di comando dal vivo, configurabile per ruolo.' },
      { title: 'Human-in-the-loop', body: 'Ogni azione con effetto esterno viene registrata e rilasciata.' },
    ],
  },
  trust: {
    eyebrow: 'Sovranità dei dati, sicurezza, regolamentazione',
    heading: 'In mani svizzere — affidabile fin dal primo giorno',
    pillars: [
      { title: 'Deployment interno al provider', body: "Un'istanza per provider ospedaliero, nessuna tenancy condivisa." },
      { title: 'Regione svizzera', body: 'Operato su Microsoft Azure in data center svizzeri (Switzerland North); residenza dei dati risolta.' },
      { title: 'Protezione PHI integrata', body: 'Pipeline Bronzo→Argento→Oro con gate PHI non aggirabili; risposte copilota ancorate.' },
      { title: 'Nativo HL7 FHIR', body: 'Interoperabilità standardizzata con SIO, laboratorio e partner di cure post-acuzie.' },
      { title: 'Identità basata su Entra', body: 'Ruoli ospedalieri mappati sui ruoli applicativi; ogni azione autenticata e verificabile.' },
      { title: 'Dottrina solo consultiva', body: 'Gli agenti non decidono, assistono la persona con autorità decisionale.' },
    ],
    keyMessage: 'Previsione affidabile + raccomandazione spiegabile + human-in-the-loop = solida per la LPD, la ISO 27001 e la conformità svizzera fin dal primo giorno.',
  },
  value: {
    eyebrow: 'Valore economico (BVA)',
    heading: 'Valore economico — ROM a 3 anni (±30 %)',
    tableHead: { lever: 'Leva di valore', amount: 'Beneficio annuo (CHF)', rationale: 'Motivazione' },
    rows: [
      { lever: 'Meno giornate-letto bloccate & ritardi di dimissione', amount: "1'650'000", rationale: 'Coordinamento più rapido, handoff più precoci' },
      { lever: 'Produttività del centro di comando', amount: "980'000", rationale: '120 utenti di picco, meno triage manuale' },
      { lever: 'Meno straordinari & supplementi di agenzia', amount: "620'000", rationale: 'Pianificazione informata dalla previsione' },
      { lever: 'Efficienza conformità & audit', amount: "220'000", rationale: 'Controlli pronti per la prova' },
      { lever: 'Beneficio lordo annuo', amount: "≈ 3'470'000", rationale: 'Somma delle leve', emphasis: true },
      { lever: 'Valore netto a 3 anni', amount: "6'410'000", rationale: 'dopo TCO su 3 anni', emphasis: true },
      { lever: 'ROI (ROM base, 3 anni)', amount: '127 %', rationale: 'Profilo di adozione bilanciato', emphasis: true },
    ],
    caveat: 'Valori ROM per conversazioni di business case, non come base finale di offerta.',
  },
  cta: {
    eyebrow: 'Prossimi passi',
    heading: 'Verso un discovery Curavias in tre passi',
    steps: [
      { title: 'Sessione di revisione (60 min)', body: 'Un esame congiunto della logica di previsione e raccomandazione sulle vostre domande.' },
      { title: 'Discovery lungo i 7 agenti', body: 'Quali copiloti creano il maggior valore nella vostra operatività?' },
      { title: 'Bozza di roadmap', body: 'Un percorso pragmatico dalla vetrina al pilota — con i vostri vincoli.' },
    ],
    contact: 'Interessati a una sessione di revisione?',
    contactCta: 'Contattaci',
  },
  footer: {
    tagline: "Curavias — previsione affidabile. Raccomandazione spiegabile. L'essere umano decide.",
    origin: 'Microsoft Innovation Hub Zürich — Vetrina',
    poweredBy: 'Powered by Microsoft',
    legalHeading: 'Nota legale',
    legal: "Non è un prodotto reale. Curavias è una vetrina con dati sintetici, IA solo consultiva, non un dispositivo medico e non destinato all'uso clinico.",
    imprint: 'Impronta',
    privacy: 'Privacy',
  },
};
