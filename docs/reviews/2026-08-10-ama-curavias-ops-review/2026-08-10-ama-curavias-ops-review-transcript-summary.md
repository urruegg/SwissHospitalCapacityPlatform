# Transcript-Summary — Curavias-Follow-up mit Dr. med. Marco Rossi (2026-08-10)

| Feld | Wert |
| ---- | ---- |
| **Version** | 1.0.0 |
| **Datum** | 2026-08-10 |
| **Autor** | @urruegg |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |
| **Quelle** | [`AMA Review Curavias Showcase.vtt`](AMA%20Review%20Curavias%20Showcase.vtt) / `.docx` (dieselbe Session) |

> Normalisierte Meeting-Notizen. Zeitangaben sind ungefähre VTT-Timecodes (mm:ss). Kleiner
> Talk zu Beginn (Wetter/Ferien, ~00:00–03:00) ist ausgelassen. Namentliche Nennung von
> Dr. med. Marco Rossi ist beabsichtigt — siehe Namenskonvention im Hauptreport
> [`2026-08-10-ama-curavias-ops-review.md`](../2026-08-10-ama-curavias-ops-review.md).

## Kontext und Einstieg (~03:00–07:30)

Urs stellt den Rahmen vor: kein fertiges Produkt, sondern ein "art of the possible"-Showcase,
gebaut mit öffentlich verfügbaren Referenz-Spitälern (USZ-Grössenordnung, Hirslanden-artiges
Privatspital, Spital Zollikerberg als kantonaler Querschnitt). Er fasst die bisherigen
Challenger-Reviews zusammen, die Marco bereits aus dem ersten Interview (17.07.2026) bekannt
sind: Rebekka Hatzung (Business Case plausibel, aber Datenqualität/Adoption entscheidend) und
Emanuel Furler (Warum nur 3 Tage Vorschau? → 72-h-Forecast heute, längerer Horizont als
Signal-Frage). Marco bestätigt: *"Ja, das sind gute Punkte."* (~06:28)

## Zeit für Patientenbetreuung — die Kernfrage erneut aufgegriffen (~09:12–14:55)

- Urs erinnert an das gebündelte erste Interview mit Christian Ernst und Regula Adams
  (17.07.2026): *"Wir müssen ein System haben, das sie unterstützt … und ihnen primär Zeit
  zurückgibt, damit man mit den Patienten arbeiten kann."* Die KPI-Idee: *"Share of Time",
  die wir zurückgeben können für die Patientenzeit.* (~09:36–10:00)
- Marco warnt vor einer zu einfachen Messung/Interpretation (~10:13–11:20): *"Das gibt
  manchmal ein Missverständnis, weil dann die Leute [meinen], alles, was sie im Büro machen,
  wäre unnötige Administration."* Sein Gegenbeispiel für **echte** Verschwendung: eine
  wiederholte Kostengutsprache für dieselbe Leistung.
- Er differenziert (~11:25–13:58): Datenauswertung mit KI zur Diagnosefindung,
  interdisziplinäre/interprofessionelle Absprachen — das ist **Patientenarbeit**, auch am
  Bildschirm. *"Die Medizin hat sich verändert. Ich will als Patient, dass mein
  Behandlungsteam sich auch nicht nur am Patienten [aufhält], sondern auch im Büro."*
  Sein Fazit: *"Es ist nicht ganz einfach zu trennen, was unnötige Administration ist."*
- Gemeinsame Schärfung der Formel (~14:06–14:55): Urs schlägt vor, dass es darum geht, dass
  man sich **optimal vorbereiten**, den Termin **optimal durchführen** und **optimal
  nachbearbeiten** kann — mit einem sauberen Handoff zwischen Disziplinen. Marco: *"Ich bin
  einverstanden."*

## Bestehendes Agenten-Modell (Walkthrough, ~19:11–31:00)

Urs erläutert das Agentenboss-Prinzip (Mensch delegiert, KI schlägt vor, Mensch entscheidet;
kein PHI-Design) und geht den Patientenfluss durch: Emergency-/Admission-Agent (Ersteinordnung,
egal ob ambulant/Notfall/geplant) → Betten-Zuweisung → OP-Koordination → Staffing Balance →
Discharge. Marco bestätigt zwischendurch mehrfach ("Ja", "Jawohl") und stellt punktuelle
Rückfragen (z. B. Überbelegungs-Handling über Standorte hinweg, ~25:07–25:18 — Rebekka habe
ihm bestätigt, dass die Lux-Gruppe das bereits nutzt).

## Intake-Triage — der Kern-Impuls dieser Session (~33:27–39:38)

- Marco leitet mit einer Strukturkritik ein: in Notaufnahmen arbeiten häufig die am wenigsten
  erfahrenen Kräfte (Lehrlinge, Ärzte in Weiterbildung) an vorderster Front; **umgekehrt**
  sollte die **erste Triage von einer Kaderärztin/einem Kaderarzt mit Schichtleitung und
  Pflege** gemeinsam gemacht werden (~33:50–34:24).
- Ziel dieser Ersteinschätzung: nicht Laborwerte im Detail, sondern früh erkennen, wie komplex
  ein Fall ist. Kontrastbeispiel: ein Schrittmacher-Patient kann ggf. am gleichen Tag nach
  Hause; ein Patient mit drei chronischen Erkrankungen, der sich über zwei Wochen
  verschlechtert hat, braucht mehrstufige Abklärungen und bleibt sicher mehrere Tage
  (~34:36–36:35).
- Befund: *"Solche Weichenstellungen werden … im Moment noch in unseren Notfallstationen zu
  wenig getroffen."* (~36:36)
- Lösungsvorschlag — KI-Triage-Assistent: anhand der ersten Patientendaten (nach ca. 30 Min)
  Muster vergleichbarer historischer Fälle erkennen — nicht die Inhalte der Untersuchungen,
  sondern **das Muster**, welche Untersuchungen gemacht wurden — um früh zu signalisieren:
  *"Das sind Patienten, die sind schnell wieder draussen, oder das sind Patienten, welche
  lange bleiben."* (~36:49–37:22)
- Ergänzender Befund — Entlassplanung beginnt zu spät: erst am Abend/nächsten Tag auf der
  Abteilung wird gefragt, was noch gebraucht wird; für das Spital ein Problem, weil die
  Austrittsplanung nicht bereits ab der Notfallpforte beginnt (~38:12–38:36).
- Bestätigung via Simulation: externe Signale haben einen kleineren Einfluss als gedacht;
  Staffing und Triage-Qualität sind die zwei primären Treiber. *"Je besser man die Triage
  macht, desto optimaler läuft es danach für alle Beteiligten."* Marco: *"Ja, da bin ich tief
  überzeugt, und dort sind wir auch noch nicht dort, wo wir sein können."* (~39:16–39:38)

## Methodische Parallele (~44:10–50:04)

Marco lobt den Discovery-Ansatz explizit ("Active Listening", "Peel the Onion" — Trennung von
Annahme und Fakt, nicht vorschnell zur Lösung springen, zuerst Ziel/Mehrwert definieren) und
zieht die Parallele zur Triage selbst: *"Das ist interessant, eigentlich bei der
Patientenbehandlung dasselbe, oder?"* Urs bestätigt: *"Genau, du machst bei der Triage genau
das gleiche."*

## Datenschutz-Reflexion und funktionale Machbarkeit zuerst (~44:10–53:21)

Marco reflektiert selbstkritisch, dass übervorsichtige Auslegung von Datenschutz-/
Swissmedic-Vorgaben teils zur Selbstblockade führt (*"Ich glaube, wir tun uns selber auch im
Weg stehen"*), betont aber: ein Nein braucht immer eine Alternativlösung. Er bestätigt den
Ansatz, fachliche Machbarkeit zuerst mit Beispieldaten zu beweisen (SwissNOSO-Beispiel),
bevor Cloud-/Infrastrukturfragen diskutiert werden.

## Abschluss (~53:45–55:14)

Marco: *"Ich habe ganz viel gelernt."* Er begrüsst, dass sich jemand organisatorisch/im
Spitalmanagement der Patientenfluss-Treiber annimmt, und betont erneut den advisory-only-
Rahmen: *"Datenbasiert, die die Entscheidungen nicht abnimmt, sondern die Entscheidungen
unterstützt."* Gegenseitige Einladung zu einem persönlichen Treffen; Marco erwähnt, gelegentlich
in Kloten zu sein (Tätigkeit für die Rega).

## Follow-up Tasks

1. Dieses Review-Report + Prep/Perform/Recap-Text-Erweiterung in START (dieser PR).
2. Zweite Backstage-Sitzung für Marco Rossi als eigene Zeile im "Review sessions on record"
   nachtragen (dieser PR).
3. Intake-Triage-Assistent als "discovered idea" für künftige Sprint-Planung vormerken
   (siehe Hauptreport §6.3) — **kein** Implementierungs-Scope in diesem PR.
4. Datenverfügbarkeits-Assessment für eine künftige Intake-Triage-Komponente (historische
   Untersuchungsmuster) — **Requires validation**, nicht Teil dieses PRs.
5. Persönliches Folgetreffen (Kloten) — organisatorisch, ausserhalb des Repository-Scopes.
