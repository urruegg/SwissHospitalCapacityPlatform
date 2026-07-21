import type { SiteContent } from './types';

// FR — traduit à partir de la source DE-CH (src/i18n/de.ts).
// Voix consultative : « prévoit / recommande / suggère », jamais « décide / diagnostique ».
export const fr: SiteContent = {
  locale: 'fr',
  htmlLang: 'fr',
  meta: {
    title: 'Curavias — La plateforme copilote IA pour le quotidien hospitalier',
    description:
      "Curavias est une vitrine du Microsoft Innovation Hub Zürich : prévision fiable, recommandation explicable, l'humain décide. IA consultative, données synthétiques, pas un dispositif médical.",
  },
  nav: {
    items: [
      { href: '#kurzueberblick', label: 'Aperçu' },
      { href: '#agenten', label: 'Agents' },
      { href: '#erlebnisse', label: 'Expériences' },
      { href: '#sicherheit', label: 'Sécurité' },
      { href: '#nutzen', label: 'Valeur' },
    ],
    cta: 'Voir la démo',
    skip: 'Aller au contenu',
    langLabel: 'Langue',
  },
  hero: {
    eyebrow: 'Swiss Hospital Capacity Copilot · Aperçu du produit',
    headline: 'La plateforme copilote IA pour le quotidien hospitalier',
    subhead: "Prévision fiable. Recommandation explicable. L'humain décide.",
    ctaPrimary: 'Voir la démo',
    ctaSecondary: 'Voir la vidéo',
  },
  disclaimer: {
    badge: 'Vitrine',
    text: "Pas un produit réel. Curavias est une vitrine du Microsoft Innovation Hub Zürich — données synthétiques, IA consultative uniquement, pas un dispositif médical et non destiné à un usage clinique.",
  },
  kpis: {
    heading: 'Curavias en chiffres',
    items: [
      { value: '≈ 3,5 mio CHF', label: 'bénéfice cible annuel (ROM)' },
      { value: '127 %', label: 'ROI sur 3 ans' },
      { value: '7', label: 'copilotes IA spécialisés' },
    ],
  },
  summary: {
    eyebrow: "L'essentiel",
    heading: 'Où serons-nous sous pression demain — et que pouvons-nous faire aujourd’hui ?',
    question:
      '« Où serons-nous sous pression demain et après-demain — et que pouvons-nous déjà faire aujourd’hui ? »',
    body:
      "Curavias répond à la question centrale de toute direction hospitalière par une prévision fiable à 3–7 jours sur l’occupation des lits, l’utilisation du bloc, les arrivées aux urgences, le potentiel de sortie et la dotation. Chaque recommandation est consultative et validée par un humain (human-in-the-loop).",
  },
  challenger: {
    eyebrow: 'Question du CIO',
    heading: 'Sept décisions opérationnelles — aujourd’hui vs. avec la prévision Curavias',
    quote:
      '« Quelles décisions opérationnelles pourraient être mieux prises aujourd’hui si la situation future de capacité et de charge était connue 3 à 7 jours à l’avance avec une grande fiabilité ? »',
    tableHead: { decision: 'Décision opérationnelle', today: "Aujourd'hui", withCuravias: 'Avec la prévision Curavias' },
    rows: [
      { decision: 'Attribution des lits', today: "Réactive le matin de l'admission, sous pression", withCuravias: '3–7 jours à l’avance — planifié plutôt qu’improvisé' },
      { decision: 'Utilisation des créneaux du bloc', today: 'Annulations/créneaux vides découverts le jour de l’opération', withCuravias: 'Risque d’annulation & réallocation visibles des jours à l’avance' },
      { decision: 'Couverture en personnel', today: 'Pool de dernière minute, surcoûts d’agence élevés', withCuravias: 'Plannings alignés sur la demande prévue' },
      { decision: 'Pilotage des sorties', today: 'Non estimable le matin', withCuravias: 'Candidats avec blocages & transfert 24–72 h à l’avance' },
      { decision: 'Transferts / arrêt des admissions', today: 'Ad hoc, communication sous pression', withCuravias: 'Cascades simulées, partenaires impliqués tôt' },
      { decision: 'Réponses de crise & scénarios', today: 'La doctrine dort dans un classeur', withCuravias: 'Recommandations fondées sur la doctrine, pilotées par scénario' },
      { decision: 'Alertes de qualité des données', today: 'N’apparaissent que dans le rapport KPI', withCuravias: 'Les gates alertent avant qu’un indicateur n’influence les décisions' },
    ],
  },
  path: {
    eyebrow: 'Le parcours patient Curavias',
    heading: "De l'admission à la guérison",
    intro: "Rôles et agents IA tout au long du traitement — de l'admission aux urgences à la guérison.",
    steps: [
      { index: '1', phase: 'Urgences & admission', role: 'Direction des urgences', agent: 'OOA', focus: 'Prévision 72 h' },
      { index: '2', phase: 'Attribution des lits', role: 'Gestion des lits', agent: 'BMCA', focus: 'Pression & candidats' },
      { index: '3', phase: 'Bloc & traitement', role: 'Coordination du bloc', agent: 'ORSA', focus: 'Pilotage du programme' },
      { index: '4', phase: 'Soins & personnel', role: 'Planification du personnel', agent: 'SBA', focus: 'Planning vs. prévision' },
      { index: '5', phase: 'Sortie', role: 'Coordination des sorties', agent: 'DCA', focus: 'Classement & transfert' },
      { index: '✓', phase: 'Succès', role: 'Le patient est guéri', agent: '—', focus: 'Objectif atteint' },
    ],
    laneLabel: 'Agents transversaux',
    lanes: ['CSA — crise & scénarios', 'DQ — qualité des données (gates)'],
    governance: "Human-in-the-loop — toute action à effet externe est validée. L'humain décide.",
  },
  agents: {
    eyebrow: 'Les sept agents Curavias',
    heading: 'Sept copilotes spécialisés — un principe commun',
    intro: "Chaque agent conseille un rôle précis avec des suggestions explicables. Les actions à effet externe passent par un gate human-in-the-loop.",
    gateLabel: 'Gate HITL',
    items: [
      { name: 'Copilote de gestion des lits', code: 'BMCA', role: 'Gestion des lits', delivers: 'Occupation, pression, candidats au transfert et sortie le jour même — explicable.', gate: 'Transfert de lit' },
      { name: 'Copilote occupation & prévision', code: 'OOA', role: 'Direction des urgences, ops', delivers: 'Prévision à 72 h des arrivées & de l’occupation par spécialité.', gate: 'Capacité' },
      { name: 'Copilote de sortie', code: 'DCA', role: 'Coordination des sorties', delivers: 'Classement des candidats à la sortie avec blocages & statut de transfert.', gate: 'Transfert inter-org.' },
      { name: 'Copilote de pilotage du bloc', code: 'ORSA', role: 'Coordination du bloc', delivers: 'Créneaux vides, réallocation du programme, risque d’annulation.', gate: 'Modif. du programme' },
      { name: 'Copilote d’équilibre du personnel', code: 'SBA', role: 'Planification du personnel', delivers: 'Carte thermique des manques, écart planning-vs-prévision.', gate: 'Personnel' },
      { name: 'Copilote crise & scénarios', code: 'CSA', role: 'Crise / astreinte', delivers: 'Évaluation de scénarios selon le classificateur suisse de situation.', gate: 'Exception politique' },
      { name: 'Agent de qualité des données', code: 'DQ', role: 'Data / ontology steward', delivers: 'Gates Bronze→Argent→Or, alertes de dérive ; gates PHI non désactivables.', gate: 'Exception PHI' },
    ],
  },
  experiences: {
    eyebrow: 'Les trois expériences',
    heading: 'Ce que Curavias vous fait ressentir',
    items: [
      { title: 'Tiroir copilote', body: 'Posez une question en langage naturel, obtenez une réponse ancrée avec sa source.' },
      { title: 'Whiteboard', body: 'Un centre de commande en direct, configurable par rôle.' },
      { title: 'Human-in-the-loop', body: 'Toute action à effet externe est journalisée et validée.' },
    ],
  },
  trust: {
    eyebrow: 'Souveraineté des données, sécurité, réglementation',
    heading: 'En mains suisses — digne de confiance dès le premier jour',
    pillars: [
      { title: 'Déploiement interne au fournisseur', body: 'Une instance par fournisseur hospitalier, pas de tenance partagée.' },
      { title: 'Région suisse', body: 'Exploité sur Microsoft Azure dans des centres de données suisses (Switzerland North) ; résidence des données résolue.' },
      { title: 'Protection PHI intégrée', body: 'Pipeline Bronze→Argent→Or avec gates PHI non contournables ; réponses copilote ancrées.' },
      { title: 'Natif HL7 FHIR', body: 'Interopérabilité standardisée avec le SIH, le laboratoire et les partenaires de soins de suite.' },
      { title: 'Identité basée sur Entra', body: 'Rôles hospitaliers mappés aux rôles applicatifs ; chaque action authentifiée et auditable.' },
      { title: 'Doctrine consultative', body: 'Les agents ne décident pas, ils conseillent la personne décisionnaire.' },
    ],
    keyMessage: 'Prévision fiable + recommandation explicable + human-in-the-loop = robuste pour la LPD, l’ISO 27001 et la conformité suisse dès le premier jour.',
  },
  value: {
    eyebrow: 'Valeur économique (BVA)',
    heading: 'Valeur économique — ROM sur 3 ans (±30 %)',
    tableHead: { lever: 'Levier de valeur', amount: 'Bénéfice annuel (CHF)', rationale: 'Justification' },
    rows: [
      { lever: 'Moins de journées-lits bloquées & de retards de sortie', amount: "1'650'000", rationale: 'Coordination plus rapide, transferts plus précoces' },
      { lever: 'Productivité du centre de commande', amount: "980'000", rationale: '120 utilisateurs de pointe, moins de tri manuel' },
      { lever: 'Moins d’heures supplémentaires & surcoûts d’agence', amount: "620'000", rationale: 'Planification informée par la prévision' },
      { lever: 'Efficacité conformité & audit', amount: "220'000", rationale: 'Contrôles prêts pour la preuve' },
      { lever: 'Bénéfice brut annuel', amount: "≈ 3'470'000", rationale: 'Somme des leviers', emphasis: true },
      { lever: 'Valeur nette sur 3 ans', amount: "6'410'000", rationale: 'après TCO sur 3 ans', emphasis: true },
      { lever: 'ROI (ROM de base, 3 ans)', amount: '127 %', rationale: 'Profil d’adoption équilibré', emphasis: true },
    ],
    caveat: 'Valeurs ROM pour les échanges de business case, non comme base finale d’offre.',
  },
  cta: {
    eyebrow: 'Prochaines étapes',
    heading: 'Vers un discovery Curavias en trois étapes',
    steps: [
      { title: 'Session de revue (60 min)', body: 'Un examen commun de la logique de prévision et de recommandation sur vos questions.' },
      { title: 'Discovery le long des 7 agents', body: 'Quels copilotes créent le plus de valeur dans votre exploitation ?' },
      { title: 'Esquisse de feuille de route', body: 'Un parcours pragmatique de la vitrine au pilote — avec vos contraintes.' },
    ],
    contact: 'Intéressé·e par une session de revue ?',
    contactCta: 'Prendre contact',
  },
  footer: {
    tagline: "Curavias — prévision fiable. Recommandation explicable. L'humain décide.",
    origin: 'Microsoft Innovation Hub Zürich — Vitrine',
    poweredBy: 'Powered by Microsoft',
    legalHeading: 'Mention légale',
    legal: 'Pas un produit réel. Curavias est une vitrine avec données synthétiques, IA consultative uniquement, pas un dispositif médical et non destiné à un usage clinique.',
    imprint: 'Mentions légales',
    privacy: 'Confidentialité',
  },
};
