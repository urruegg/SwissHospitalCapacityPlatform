# Review-Report — Curavias-Fach-Interview mit Spital Zollikerberg (2026-07-17)

| Feld | Wert |
| ---- | ---- |
| **Version** | 1.0.0 |
| **Datum** | 2026-07-23 |
| **Autor** | @urruegg |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |
| **Intake-Kind** | `session` (moderiertes Fach-Interview, 60 Min, Deutsch) |
| **Quelle** | [`2026-07-17-ama-hospital-ops-lead-review-transcript-summary.md`](2026-07-17-ama-hospital-ops-lead-review/2026-07-17-ama-hospital-ops-lead-review-transcript-summary.md) (normalisierte Meeting-Notizen) |
| **Review-Pack** | [`README.md`](2026-07-17-ama-hospital-ops-lead-review/README.md) · [`interview-briefing.md`](2026-07-17-ama-hospital-ops-lead-review/interview-briefing.md) · [`curavias-produktubersicht.md`](2026-07-17-ama-hospital-ops-lead-review/curavias-produktubersicht.md) |

> Erstellt durch den [`review-session-agent`](../../agents/review-session-agent/AGENT.md) nach der
> Struktur in [`docs/reviews/README.md`](README.md) § *Minimum Review Report Structure*.

---

## 1. Session-Metadaten

| Feld | Wert |
| ---- | ---- |
| Session-Datum | 2026-07-17 |
| Dauer / Format | 60 Min, moderiertes Fach-Interview, Deutsch |
| Kunde | Spital Zollikerberg |
| Teilnehmende (Kundenseite) | **Christian Ernst** (Department Notfall / Akutmedizin), **Regula Adams** (Organisationsentwicklung) |
| Teilnehmende (unsere Seite) | **@urruegg** (Moderation, Facharchitektur) |
| Anker (CIO-Challenger-Frage) | *„Welche operativen Entscheidungen könnten heute besser getroffen werden, wenn die zukünftige Kapazitäts- und Auslastungssituation 3 bis 7 Tage im Voraus mit hoher Zuverlässigkeit bekannt wäre?"* |

---

## 2. Geprüfte Inputs

1. **Transcript-Summary** (primäre Quelle) — normalisierte Meeting-Notizen inkl. Follow-up-Tasks.
2. **Interview-Briefing** — Agenda, Kernfragen, Discovery-Fragen pro Agent, Vorbedingungs-Checkliste.
3. **Curavias-Produktübersicht** — 7 operative Entscheidungen (§2), 7-Agenten-Modell (§3), Advisory-only + HITL (§4), BVA (§6).
4. **Klickbarer Prototyp** — [`curavias-ux-ideas/prototype/index.html`](../superpowers/ideas/curavias-ux-ideas/prototype/index.html), 6 Rollen-Oberflächen (OOA · DCA · BMCA · ORSA · SBA · CSA) + START + BACKSTAGE. **Als Validierungs-Instrument gegen die im Interview genannten Herausforderungen und Bedenken eingesetzt** (siehe §4.3).
5. **Repository-Baseline** — `docs/PRD.md`, `agents/*/AGENT.md`, `docs/adr/0007` (HITL), `docs/adr/0016` (kein PHI), `docs/BVA.md`.

---

## 3. Outcome-Summary (die drei Kernpunkte)

Gemäss Briefing §7 verlässt die Session mit **maximal drei konkreten Punkten**:

1. **Nutzenhypothese bestätigt.** Ernst hat die 3–7-Tage-Vorschau ausdrücklich als **grossen finanziellen und planerischen Vorteil** bezeichnet und den vorgestellten agentenbasierten Patientenfluss als „grundsätzlich zutreffend" validiert. Die CIO-Challenger-Frage ist damit fachlich beantwortet, nicht nur abgenickt.
2. **Wunsch-Erst-Cluster identifiziert.** Der zentrale Schmerzpunkt ist die **Abstimmung zwischen OP-Auslastung, Bettenauslastung und Personalverteilung** — genau die gekoppelte Steuerung, die Curavias über die OOA→BMCA→ORSA→SBA-Kette abbildet. Der Einstieg mit **Bettendisposition + Personalplanung** wird durch die vermittelten Fachexperten (Scarcia, Anita) vertieft.
3. **Follow-up vereinbart.** Vermittlung an die operativen Verantwortlichen (Bettendisposition/OP-Planung, Personalmanagement) für ein Deep-Dive-Interview; Abklärung, ob ein Arbeitshandbuch / eine Prozessdokumentation für die Bettenzuweisung bereitgestellt werden kann; Einladung zum Innovation-Hub-Showcase nach Projektabschluss.

> **Schlüssel-Outcome (Design-Konsequenz):** Die im Interview bestätigten Herausforderungen
> — *Vorausschau, gekoppelte Steuerung, erklärbare Empfehlung, Mensch entscheidet* — sind
> direkt in ein Design überführt worden:
> [**Sprint 26 — Decision Ontology & Actionable-Insight Layer**](../superpowers/specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md).
> Dieses Design hebt die Fabric-IQ-Ebene von *deskriptiv* („was ist die Belegung jetzt")
> auf *prädiktiv + präskriptiv + koordiniert* (Signal → Verständnis → Empfehlung → Aktion →
> Koordination) und adressiert damit genau Ernsts Kernpunkt der gekoppelten OP-/Betten-/
> Personal-Steuerung.

---

## 4. Key Findings

### 4.1 Bestätigte Nutzenhebel (aus dem Transcript)

| # | Operative Entscheidung (Produktübersicht §2) | Befund aus dem Interview | Verdikt |
| - | -------------------------------------------- | ------------------------ | ------- |
| 1 | Bettenzuweisung | Heute reaktiv; Detailtiefe erfordert die Bettendisposition (Scarcia). Vorausplanung als klarer Nutzen bestätigt. | **relevant** |
| 2 | OP-Slot-Nutzung | Teil des zentralen Schmerzpunkts (OP-/Betten-/Personal-Abstimmung). | **relevant** |
| 3 | Personalabdeckung | Hoch relevant: Teams sind oft so **spezialisiert, dass ein Ausfall nicht einfach kompensierbar** ist — Vorausschau besonders wertvoll. | **relevant (hoch)** |
| 4 | Entlassungssteuerung | Im Modell bestätigt; unterschiedliche Eintrittspforten (Notfall vs. geplant) sind zu berücksichtigen. | **relevant** |
| 5 | Verlegungen / Aufnahmestopp | Nicht vertieft in dieser Session. | **Requires validation** |
| 6 | Krisen- & Szenario-Antworten | Konzeptionell vorgestellt (CSA); Doktrin-Digitalisierung nicht vertieft. | **bedingt / Requires validation** |
| 7 | Datenqualitäts-Alarme | Kennzahlen (Aufenthaltsdauer, Patientenzufriedenheit, -sicherheit/Stürze, Regulatorik) genannt; Data-Ownership nicht formal geklärt. | **bedingt** |

### 4.2 Zusätzliche Erkenntnisse

- **Unterschiedliche Eintrittspforten**: neben dem Notfall existieren geplante Pforten (Gynäkologie, Chirurgie) mit unterschiedlichem Standardisierungsgrad — relevant für das OOA-Prognosemodell und die Treiber-Zerlegung.
- **Spezialisierte Teams**: ärztliche und pflegerische Personalplanung ist nicht fungibel — verstärkt den Wert eines skill-bewussten SBA (Verknüpfung zu Sprint 23 Org-/Skills-Ontologie).
- **Metadaten-Ansatz akzeptiert**: „ausschliesslich Metadaten" zur DSG-Erfüllung, Cloud- **und** lokal-fähig, Integration in bestehende Systeme (**Epic** genannt) ohne Verletzung der Sicherheitsstandards. Deckt sich mit der Advisory-only-/kein-PHI-Doktrin.
- **Blaupausen-Ziel**: öffentlich verfügbare, adaptierbare Blaupause — bestätigt die Repository-first-/wiederverwendbare Plattform-Strategie.

### 4.3 Prototyp als Validierungs-Instrument

Der [**klickbare Prototyp**](../superpowers/ideas/curavias-ux-ideas/prototype/index.html) wurde
genutzt, um die im Interview genannten **Herausforderungen und Bedenken gegen eine konkrete
Oberfläche zu spiegeln**. Die Zuordnung Herausforderung → validierende Prototyp-Oberfläche:

| Herausforderung / Bedenken (Interview) | Validierende Prototyp-Oberfläche | Was der Prototyp zeigt |
| -------------------------------------- | -------------------------------- | ---------------------- |
| „Wo stehen wir morgen/übermorgen unter Druck?" (3–7-Tage-Vorschau) | `01-ooa-occupancy` | 72-h-Forecast (Medizin A 102 %), Treiber-Zerlegung (*+6 Zugänge Grippe vs. 2 Entlassungen*) |
| Gekoppelte OP-/Betten-/Personal-Steuerung (Ernsts Schmerzpunkt) | `03-bmca` → `04-orsa` → `05-sba` (Goldener Faden) | Koordinierter Plan über Rollen hinweg; Live-Sync *102 % → 94 %* |
| Nicht-kompensierbare, spezialisierte Teams | `05-sba-staffing` | Skill-basierte Zuordnung (Onkologie-RN), Schichtlücken, „keine Agentur" als Ziel |
| Entlassungs-Blocker sichtbar machen | `02-dca-discharge` | Gerankte Blocker-Tafel (8 Kandidaten → 5 systemische Blocker) statt flacher Liste |
| „Mensch entscheidet" / Governance-Vertrauen | `07-backstage` | HITL-Gate, `approved-to-apply`, kein Deploy ohne Freigabe, 0 echte PHI |
| Krisen-Sparring gegen Doktrin | `06-csa-crisis` | 6 Schocks druckgetestet, Trust-A-Signalquellen (MeteoSwiss/BAG/Alertswiss/SED), Sicherheit % |

**Ergebnis:** Der Prototyp hat das 5-Takt-Muster **Signal → Verständnis → Empfehlung → Aktion →
Koordination** greifbar gemacht und die Bedenken zur *Erklärbarkeit* und zur *Mensch-entscheidet*-
Doktrin adressiert. Die dabei sichtbar gewordene Lücke — die heutige Grounding-Ebene liefert nur
den *Signal*-Takt — ist der direkte Auslöser für [Sprint 26](../superpowers/specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md).

---

## 5. Gaps und Risiken

| Kategorie | Gap / Risiko | Auswirkung | Wahrsch. | Mitigation |
| --------- | ------------ | ---------- | -------- | ---------- |
| Operativ | Detailtiefe Bettendisposition & OP-Planung fehlt (nur High-Level bestätigt) | Prognose-/Lever-Kalibrierung ungenau | H | Deep-Dive mit Scarcia (Bettendisposition/OP) + Anita (Personal) |
| Daten | Analytische Datenumgebung vs. rein transaktionales KIS (**Epic**) unklar | Ohne Bronze/Silber/Gold-Schicht kein Foresight-Feed | H | Datenverfügbarkeits-Assessment als Pilot-Vorbedingung |
| Organisation | Data-Ownership für operative KPIs nicht formal geregelt | DQ-Agent ohne klaren Verantwortlichen | M | Rolle „Data-Owner" im Pilot-Scope klären |
| Regulatorik | Kantonale Datenschutz-/Melde-Vorgaben nicht abgefragt | Pilot-Blocker spät sichtbar | M | Datenschutz-Deep-Dive (Kanton Zürich) vor POC |
| Change | Human-in-the-Loop-Kultur vs. Kulturwandel bei AI-Prognosen | Adoption-Risiko | M | Advisory-only + HITL früh demonstrieren (Prototyp/Backstage) |
| Scope | Verlegungen/Aufnahmestopp (Entsch. 5) und Doktrin-Digitalisierung (CSA) nicht validiert | Roadmap-Priorität unsicher | L | In Follow-up-Interview nachfassen — **Requires validation** |

---

## 6. Empfehlungen und nächste Aktionen

| Prio | Aktion | Owner | Bezug |
| ---- | ------ | ----- | ----- |
| **H** | Deep-Dive-Interview mit **Scarcia** (Bettendisposition/OP-Planung) und **Anita** (Personalmanagement) vereinbaren | @urruegg | Follow-up-Task Transcript |
| **H** | **Arbeitshandbuch / Prozessdokumentation** Bettenzuweisung anfragen | Ernst | Follow-up-Task Transcript |
| **H** | Datenverfügbarkeits-Assessment (Epic → analytische Schicht) als Pilot-Vorbedingung | @urruegg | Gap §5 |
| **M** | **Sprint 26** (Decision Ontology & Actionable-Insight) umsetzen — bildet die gekoppelte Steuerung + erklärbare Empfehlung technisch ab | @urruegg | [Design](../superpowers/specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md) |
| **M** | Prototyp-gestützten Showcase (OOA→DCA Goldener Faden) für den Wunsch-Erst-Cluster vorbereiten | @urruegg | §4.3 |
| **M** | Datenschutz-/Kanton-Deep-Dive (DSG, kantonale Vorgaben) terminieren | @urruegg | Gap §5 |
| **L** | Entscheidungen 5 (Verlegungen) und 6 (CSA-Doktrin) im Folgegespräch validieren | @urruegg | Finding §4.1 |

---

## 7. Artefakt-Traceability

| Aussage / Outcome | Repository-Artefakt |
| ----------------- | ------------------- |
| 72-h-Prognose, stündlich refresht | [`docs/PRD.md`](../PRD.md) `FR-FC-001`, `NFR-PERF-002` |
| 7 Agenten, Advisory-only | [`agents/{bmca,ooa,dca,orsa,sba,csa,data-quality}-agent/AGENT.md`](../../agents/) §1 |
| HITL-01…HITL-05 deny-by-default | [`docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md`](../adr/0007-mvp-agent-runtime-and-hitl-release-gates.md) |
| Kein PHI / Metadaten-Ansatz | [`docs/adr/0016-no-phi-in-mvp-demo-scope.md`](../adr/0016-no-phi-in-mvp-demo-scope.md) |
| ROI 127 %, Jahresnutzen ≈ CHF 3.5 Mio. | [`docs/BVA.md`](../BVA.md) § ROM |
| Gekoppelte Steuerung + erklärbare Empfehlung (Design-Outcome) | [`2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md`](../superpowers/specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md) |
| Prototyp-Validierung (6 Rollen-Oberflächen) | [`curavias-ux-ideas/prototype/index.html`](../superpowers/ideas/curavias-ux-ideas/prototype/index.html) |
| Skill-bewusste Personalplanung (spezialisierte Teams) | Sprint 23 Org-/Skills-Ontologie ([#255](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/255)) |

---

## 8. Requires Validation (offene Punkte)

- Verlegungs-/Aufnahmestopp-Nutzen (Entscheidung 5) — im Interview nicht vertieft.
- CSA-Doktrin: digital vorhanden oder in Papier-Ordnern? — nicht abgefragt.
- KIS-Integrationsweg (Epic: HL7/FHIR-Zugriff, Verantwortlicher) — nur konzeptionell genannt.
- Kantonale Datenschutz-/Melde-Vorgaben — nicht abgefragt.
- Data-Ownership für operative KPIs — nicht formal geklärt.
