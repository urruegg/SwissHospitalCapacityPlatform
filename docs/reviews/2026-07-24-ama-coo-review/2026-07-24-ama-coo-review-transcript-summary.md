# Transcript-Summary — Curavias Showcase-Interview mit COO (2026-07-24)

> **Anonymisiert.** Teilnehmernamen sind durch Rollenbezeichnungen ersetzt:
> **COO** (Kundenseite, operative Leitung) und **@urruegg** (Moderation /
> Solution Owner). Normalisierte Meeting-Notizen; das Roh-Transkript (VTT) und
> die unbearbeiteten Teams-AI-Notizen werden aus Datenschutzgründen **nicht**
> im Repository abgelegt.

## Meeting-Notizen

### Vorstellung und Zielsetzung

* @urruegg erläutert dem COO das Curavias-Projekt: Kapazitätsplanung und Patientenfluss im Spital durch KI-Agenten und Metadaten optimieren, ohne schützenswerte Patientendaten in die Cloud zu übertragen.
* „Curavias" ist ein neutral gewählter Arbeitstitel, keine reale Produktbezeichnung.
* Reale Personen und Rollen im Spitalbetrieb werden als KI-Agenten modelliert (Aufnahme bis Entlassung), die auf Basis von Metadaten agieren.
* Matching/Planung ausschliesslich mit Metadaten — keine PHI in der Cloud.

### Technische Umsetzung und Systemintegration

* Zugriff auf Patientendaten über Deep Links; die eigentlichen Daten verbleiben im lokalen KIS.
* Kompetenzmatching nutzt in Microsoft 365 / Office hinterlegte Mitarbeitenden-Informationen.
* Der COO weist auf die Schnittstellenproblematik hin: Polypoint (Dienstplanung) schwer integrierbar, Epic bietet gute Schnittstellen. @urruegg bestätigt dies aus bisherigen Integrationsversuchen.
* Spezialisierte Agenten für Datenqualitätsprüfung, Szenarienanalysen und proaktive Benachrichtigungen.

### Business Case und Wirtschaftlichkeit

* Business Case auf öffentlich zugänglichen Spitaldaten; 3 Spitäler aus verschiedenen Kantonen (regulatorische Unterschiede, Skalierbarkeit).
* Zielgrössen (COO): OP-Auslastung ≥ 85 %, minimale Wartezeiten; grösste Herausforderung im Notfallbereich (keine freigehaltenen Betten).
* Umsetzung scheitert oft an fehlenden IT-Ressourcen, hohen Kosten und mangelnder Datenqualität.
* Vorschlag @urruegg: Entwicklung mit 2 internen Personen in 90 Tagen; Hauptkosten im Personalaufwand.

### Datenqualität und menschlicher Faktor

* COO: Datenqualität oft unzureichend → Berichte/Analysen werden nicht akzeptiert, Nutzung bleibt eingeschränkt.
* System sieht Agenten vor, die proaktiv auf fehlerhafte/fehlende Daten hinweisen und Verantwortliche zur Nachbesserung auffordern.
* Menschlicher Wille, Schulung und Akzeptanz bleiben entscheidend; viele Prozesse scheitern an unzureichender Schulung oder wahrgenommener Komplexität.
* Delegation von Routineaufgaben an Agenten soll Fachpersonal für die Patientenversorgung entlasten.

### Change Management und Schulung

* COO betont gezieltes Change Management und umfassende Schulung als Voraussetzung für Akzeptanz.
* Mitarbeitende fühlen sich von Toolvielfalt/Komplexität überfordert; Schulungsangebote oft unzureichend.
* Praxisbeispiel: Selbst erfahrene Mitarbeitende haben Mühe mit Epic oder M365 und weichen auf traditionelle Arbeitsweisen aus.

### Szenarienmanagement und Simulationen

* @urruegg erläutert Was-wäre-wenn- und Krisensimulationen (Ausfälle, Personalmangel) über einen Szenarienagenten mit Handlungsempfehlungen.

### Rollen, Dokumentation und Anpassbarkeit

* @urruegg fragt nach Stellenbeschreibungen/Arbeitsanweisungen zur Feinjustierung der Agenten.
* COO: relevante Dokumente liegen in den Fachbereichen; offizielle Klärung nötig, bevor sie für die Entwicklung genutzt werden können.

## Follow-up Tasks

* **Beschaffung von Arbeitsanweisungen/Dokumenten (COO):** Abklären, ob und wie unter NDA relevante Arbeitsanweisungen/Dokumente aus den Fachbereichen bereitgestellt werden können, um die Lösung auf die aktuellen Prozesse anzupassen.
* **Zuständigkeit für Dokumentenzusammenstellung (COO):** Herausfinden, wer im Unternehmen die richtige Ansprechperson/Stelle ist, um das Vorhaben offiziell einzuspielen und die Dokumente zusammenzustellen.
