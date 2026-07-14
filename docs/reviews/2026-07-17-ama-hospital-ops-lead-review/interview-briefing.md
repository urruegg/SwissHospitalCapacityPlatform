<p align="center">
  <img src="../../brandkit/logo/curavias-logo.svg" alt="Curavias" width="240"/>
</p>

# Interview-Briefing — Curavias-Review mit Spital Zollikerberg

| Feld | Wert |
| ---- | ---- |
| **Session-Datum** | 2026-07-17 |
| **Dauer** | 60 Minuten |
| **Sprache** | Deutsch |
| **Format** | Moderiertes Fach-Interview |
| **Vorbereitungsdokument (Kunde)** | [`curavias-produktubersicht.md`](curavias-produktubersicht.md) |
| **Version** | 1.0.0 |
| **Datum** | 2026-07-14 |
| **Autor** | @urruegg |
| **Status** | Vorbereitet |
| **Zielort für Nachbereitung** | [`docs/reviews/2026-07-17-ama-hospital-ops-lead-review.md`](../) — Full-Report nach dem Muster in [`docs/reviews/README.md`](../README.md) |

---

## 1. Session-Kontext

### Teilnehmer (Kundenseite)

- **Spital Zollikerberg** — Fachvertretung Operational Ops (Bettenmanagement / OP-Koordination / Personalplanung / CIO-Stellvertretung, je nach Verfügbarkeit)
- Rolle: Sparringpartner für Validierung des Curavias-Funktionsumfangs

### Teilnehmer (unsere Seite)

- @urruegg — Moderation, Facharchitektur
- Optional: Fachexperte je nach adressiertem Agenten-Cluster

### CIO-Challenger-Frage (der Anker)

> *„Welche operativen Entscheidungen könnten heute besser getroffen werden, wenn die zukünftige Kapazitäts- und Auslastungssituation 3 bis 7 Tage im Voraus mit hoher Zuverlässigkeit bekannt wäre?"*

Diese Frage ist die **Nordstern-Frage der gesamten Session**. Jede Antwort, jedes Beispiel, jede Priorisierung wird auf sie zurückgeführt.

---

## 2. Zielsetzung — was wir nach 60 Minuten wissen wollen

1. **Nutzeninventar validiert.** Die 7 operativen Entscheidungen aus der Produktübersicht (§2 dort) sind vom Kunden bestätigt, erweitert oder korrigiert — mit Beispielen aus dem eigenen Betrieb.
2. **Funktionsumfang validiert.** Für jeden der 7 Curavias-Agenten (BMCA, OOA, DCA, ORSA, SBA, CSA, DQ) wissen wir: **relevant / bedingt relevant / heute nicht priorisiert** — jeweils mit Begründung.
3. **Roadmap-Signal.** Wir kennen den Wunsch-Erst-Agenten (welche Rolle profitiert bei Zollikerberg am schnellsten) und die 2–3 Voraussetzungen (Daten, Systeme, Prozesse), die dafür bestehen oder fehlen.
4. **Blocker-Karte.** Wir wissen, was einer Pilotierung im Weg steht (Datenschutz, KIS-Zugriff, kantonale Vorgaben, Change-Management).

---

## 3. Agenda 60 Minuten (zeitgeboxt)

| Zeit | Blockname | Inhalt | Verantwortung |
| ---- | --------- | ------ | ------------- |
| 0–5 min | **Intro & Kontext** | Begrüssung, Ziele der Session, Rollen im Raum, DSG-Rahmen der Diskussion (keine PHI, keine geschützten Fallzahlen — nur Konzepte und Muster) | @urruegg |
| 5–15 min | **Curavias in 10 min** | Kompakte Präsentation der Produktübersicht §1–§3: was Curavias tut, 7-Agenten-Modell, Advisory-only-Doktrin | @urruegg |
| 15–35 min | **CIO-Challenger-Frage — strukturiertes Ausrollen** | Für jede der 7 operativen Entscheidungen: heutiger Zustand, konkreter Fall, geschätzter Nutzen bei 3–7-Tage-Vorschau, wer entscheidet | Kunde führt, wir moderieren |
| 35–50 min | **Discovery pro Agent** | Für BMCA / OOA / DCA / ORSA / SBA / CSA / DQ jeweils 2 min: Fit-Signal, Blocker, Vorbedingung | Wechselnd |
| 50–58 min | **Vorbedingungs- & Roadmap-Check** | KIS-Zugriff, Datenverfügbarkeit, Personazuordnung, kantonale Vorgaben, Change-Bereitschaft, Wunsch-Erst-Agent | Wir hören zu und clustern |
| 58–60 min | **Nächste Schritte** | Was wir mit dem Kunden verlassen (Follow-up, POC-Vorschlag, Datenschutz-Checkliste) | @urruegg |

---

## 4. Kernfragen zur CIO-Challenger-Frage

Diese Fragen decken die 7 operativen Entscheidungen aus der Produktübersicht §2 ab. Sie sind offen formuliert — der Kunde soll erzählen, nicht abnicken.

### 4.1 Bettenzuweisung

1. Wie wird bei Ihnen heute die Bettenzuweisung für die kommenden 24–72 h getroffen? Wer ist beteiligt, welche Systeme werden verwendet?
2. Nennen Sie ein Beispiel aus den letzten 4 Wochen, wo eine 3–7-Tage-Vorschau eine bessere Entscheidung ermöglicht hätte. Was wäre der konkrete Nutzen gewesen (weniger Verlegungen, keine Aufnahmesperre, weniger Überzeit)?
3. Welche Signale nutzen Sie heute (ED-Ankünfte, ADT-Events, Discharge-Ready-Status)? Welche fehlen?

### 4.2 OP-Slot-Nutzung

4. Wie oft passiert es, dass ein OP-Slot unterausgelastet ist oder eine Absage erst am OP-Morgen entdeckt wird? Was ist der monatliche Umfang?
5. Wie viele Stunden werden pro Woche für Slate-Rebalancing manuell aufgewendet?

### 4.3 Personalabdeckung

6. Wie hoch ist Ihr Anteil Ad-hoc-Pool-Einsätze und Agentur-Zuschlagsstunden pro Monat? Wo würde eine 3–7-Tage-Vorschau am stärksten Kosten sparen?
7. Welche Rolle hat Ihr Dienstplanungsteam heute in der Vorausplanung? Ist Prognose-Feedback ein etablierter Bestandteil des Rosterings?

### 4.4 Entlassungssteuerung

8. Wie viele Entlassungen pro Woche werden durch Nachversorger-Handoffs (Reha, Pflegeheim, Spitex) verzögert? Wo liegen die typischen Blocker?
9. Sind Handoff-Status heute im gleichen System sichtbar wie Bettenbelegung, oder muss man drei Systeme querlesen?

### 4.5 Verlegungen / Aufnahmestopp

10. Wie werden Verlegungsentscheidungen kommuniziert und dokumentiert (Kanton, andere Häuser, Rettungsdienst)? Wie viel Vorlaufzeit haben Sie üblicherweise?
11. Gab es in den letzten 6 Monaten einen Aufnahmestopp, den Sie mit besserer Vorschau hätten vermeiden oder verkürzen können?

### 4.6 Krisen- und Szenarioantworten

12. Wie oft üben Sie Ihre Krisen-Doktrin (Epidemie-Welle, IT-Ausfall, Personalengpass, Massenanfall)? Wird die Doktrin nach jedem Ereignis fortgeschrieben?
13. Wäre ein Copilot, der eine hypothetische Situation gegen die Doktrin abbildet und Vorschläge liefert, in Ihrem Betriebsalltag ein Werkzeug für den Diensthabenden — oder eher für die Retrospektive?

### 4.7 Datenqualitäts-Alarme

14. Wie oft passiert es, dass eine operative Entscheidung auf einer Kennzahl basiert, die sich später als falsch herausstellt (verspätete ADT-Events, fehlende Discharge-Status, doppelte Fallnummern)?
15. Wer im Haus ist heute verantwortlich für die Datenqualität der operativen KPIs? Existiert diese Rolle formal?

---

## 5. Discovery-Fragen pro Curavias-Agent

Für jeden Agenten: **eine Fit-Frage + eine Blocker-Frage + eine Vorbedingungs-Frage** (jeweils 2 min). Anhand der Antwort clustern wir *relevant / bedingt / nicht heute*.

### BMCA — Bettenmanagement-Copilot

- **Fit:** Wenn Ihr Bettenmanager pro Schicht 5 Fragen an Curavias stellen könnte, wären die drei häufigsten: …?
- **Blocker:** Was hindert Sie heute daran, einen AI-Copiloten in den Bettenmanagement-Workflow zu integrieren?
- **Vorbedingung:** Welche Kennzahlen (Belegung nach Station, Kandidatenliste, Same-Day-Discharge-Ready) sind heute strukturiert verfügbar?

### OOA — 72-h-Belegungs-Forecast-Copilot

- **Fit:** Für welche Fachbereiche und welche Zeitfenster (Werktag, Wochenende, Nacht) wäre eine 72-h-Prognose am wertvollsten?
- **Blocker:** Vertrauen Sie AI-Prognosen im operativen Betrieb heute schon irgendwo — oder wäre das ein Kulturwandel?
- **Vorbedingung:** Sind Ihre Ankunfts-, Belegungs- und Fall-Signale in einer analytischen Umgebung verfügbar oder nur transaktional im KIS?

### DCA — Entlassungs-Copilot

- **Fit:** Wie stark würde eine Liste mit gerankten Entlassungskandidaten + Blockern + Handoff-Status den Nachmittags-Bettendruck reduzieren?
- **Blocker:** Sind Nachversorger-Partner (Reha, Spitex, Pflegeheime) heute integriert oder nur telefonisch erreichbar?
- **Vorbedingung:** Gibt es einen digitalen Discharge-Readiness-Marker im KIS?

### ORSA — OP-Steuerungs-Copilot

- **Fit:** Wie viele Slate-Änderungen pro Woche werden reaktiv statt geplant getroffen? Welchen Zeitgewinn bringt eine 24-h-Vorschau?
- **Blocker:** Ist die OP-Slate-Änderung heute an mehrere Zustimmungen gebunden (Chirurgie, Anästhesie, Belegärzte)?
- **Vorbedingung:** Sind OP-Slot-, Fallliste- und Absage-Daten strukturiert exportierbar?

### SBA — Personal-Balance-Copilot

- **Fit:** Wenn Sie eine wöchentliche Heatmap „Roster vs. Forecast" pro Station hätten — welche Rolle würde sie am aktivsten nutzen?
- **Blocker:** Wie ist Ihr Personal-Dienstplan-System (Polypoint, ATOSS, Eigenentwicklung)? Ist ein API-Zugriff realistisch?
- **Vorbedingung:** Gibt es eine konsistente Rollen-Definition (Skill, Qualifikation), die mit dem Prognosemodell verknüpfbar ist?

### CSA — Krisen- & Szenario-Copilot

- **Fit:** Welches Krisenszenario der letzten 12 Monate hätte am meisten von einem Copilot-Sparringspartner profitiert?
- **Blocker:** Ist Ihre Krisen-Doktrin digital vorhanden oder in Papier-Ordnern verteilt?
- **Vorbedingung:** Existiert eine Verbindung zum Schweizer *Lage*-Klassifikator oder zum kantonalen Führungsstab?

### DQ — Datenqualitäts-Agent

- **Fit:** Wo im operativen KPI-Reporting würden Sie sich einen automatischen Drift-Alarm wünschen?
- **Blocker:** Wer trägt heute die Verantwortung, wenn eine operative Kennzahl falsch ist — Data-Ownership formal geregelt?
- **Vorbedingung:** Gibt es eine strukturierte Bronze/Silber/Gold-Datenschicht — oder liegt alles im operativen KIS?

---

## 6. Vorbedingungs-Checkliste (letzte 10 Minuten)

Kurz und direkt — offen abfragen, nicht abhaken lassen:

| Vorbedingung | Frage |
| ------------ | ----- |
| KIS-Integration | Welches KIS-System ist im Einsatz? Wer entscheidet über API/HL7-Zugriff? |
| Datenverfügbarkeit | Existiert eine analytische Datenumgebung (Data Warehouse, Fabric, Databricks) oder nur das transaktionale KIS? |
| Persona-Zuordnung | Sind die 7 Curavias-Rollen (Bettenmanager, ED-Lead, Entlassungskoordination, OP-Koordination, Personalplanung, Krisenmanagement, Data-Owner) im Haus formal etabliert? |
| Kantonale Vorgaben | Gibt es kantonale Datenschutz-, Berichts- oder Melde-Vorgaben, die Curavias explizit adressieren muss? |
| Governance-Bereitschaft | Ist eine Human-in-the-Loop-Kultur (Vier-Augen-Prinzip mit AI-Beratung) etabliert oder ein Kulturwandel? |
| Change-Bereitschaft | Wer wäre Sponsor / Pilot-Anwender im Haus? Welche Führungsrolle würde eine erste Curavias-Instanz begrüssen? |

---

## 7. Nächste Schritte (Session-Ausgang)

Am Ende der 60 min verlassen wir die Session mit **maximal drei konkreten Punkten** — sonst verwässert die Nachverfolgung:

1. **Wunsch-Erst-Agent identifiziert** (BMCA / OOA / DCA / ORSA / SBA / CSA / DQ) — dokumentiert mit Begründung
2. **2–3 Vorbedingungen** ausformuliert, die vor einem Pilot geklärt werden müssen
3. **Follow-up-Termin** vereinbart (Deep-Dive Datenschutz, POC-Scoping, Roadmap-Workshop)

---

## 8. Nachbereitung — Report-Struktur

Nach der Session dokumentieren wir das Ergebnis nach dem Muster in [`docs/reviews/README.md`](../README.md) §Minimum Review Report Structure:

1. Session metadata (Teilnehmer, Datum, Dauer, Ort)
2. Inputs reviewed (dieses Briefing, die Produktübersicht, Transcript falls aufgenommen)
3. Outcome summary (die max. 3 Punkte aus §7)
4. Key findings (was hat sich als hoher Nutzen bestätigt, was war überraschend)
5. Gaps and risks (Vorbedingungen, kantonale/regulatorische Blocker)
6. Recommendations and next actions (POC-Scope, Sponsor, Roadmap-Skizze)
7. Artefact traceability (Verweis auf PRD-Requirements, Agent-Packs, ADRs, die für den Wunsch-Erst-Agenten relevant sind)

Ziel-Datei: `docs/reviews/2026-07-17-ama-hospital-ops-lead-review.md`

---

## Anhang A — Grounding-Quellen für Faktentreue in der Session

Damit jede Aussage zu Curavias mit einem Repository-Artefakt belegbar ist:

| Aussage | Quelle |
| ------- | ------ |
| „72-Stunden-Prognose stündlich refresht" | [`docs/PRD.md`](../../PRD.md) `FR-FC-001`, `NFR-PERF-002` |
| „7 Agenten, jeweils Advisory-only" | [`agents/{bmca,ooa,dca,orsa,sba,csa,data-quality}-agent/AGENT.md`](../../../agents/) §1 Identity |
| „HITL-01 bis HITL-05 als deny-by-default" | [`docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md`](../../adr/0007-mvp-agent-runtime-and-hitl-release-gates.md) |
| „ROI 127 %, Year-1-Nettowert CHF 1.27 Mio." | [`docs/BVA.md`](../../BVA.md) §ROM Business Value Model |
| „PHI-Gates in der Datenpipeline nicht überschreibbar" | [`agents/data-quality-agent/AGENT.md`](../../../agents/data-quality-agent/AGENT.md) §1, [`docs/adr/0016-no-phi-in-mvp-demo-scope.md`](../../adr/0016-no-phi-in-mvp-demo-scope.md) |
| „Ein Provider = eine Instanz, keine geteilte Tenancy" | [`docs/PRD.md`](../../PRD.md) `FR-OM-001`, `FR-OM-002` |
| „Schweizer Region-Compliance" | [`docs/adr/0003-swiss-regional-inference-for-phi.md`](../../adr/0003-swiss-regional-inference-for-phi.md), [`docs/adr/0004-block-global-and-data-zone-for-phi.md`](../../adr/0004-block-global-and-data-zone-for-phi.md) |

---

<p align="center">
  <img src="../../brandkit/logo/curavias-symbol.svg" alt="Curavias Symbol" width="60"/>
</p>
