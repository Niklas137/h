# SEO-Audit für FSH-Documentation

Wöchentliche Prüfung der Website fsh-documentation.com (und der Zweitdomain fsh-documentation.de),
automatisiert mit Claude Code. Auslöser ist das Wort **„SEO-Audit"** im Chat (oder `/seo-audit`).
Die Regeln stehen im Skill `.claude/skills/seo-audit/SKILL.md`, die Daten in diesem Ordner.

## So läuft eine Woche

1. Freitag 7:30 Uhr: Die Routine prüft Erreichbarkeit, Technik und On-Page (sofern die Seite
   abrufbar ist), E-Mail-DNS (SPF, DMARC), Sichtbarkeit im Suchindex, Marke und lokale Einträge,
   vergleicht mit dem letzten Lauf, schreibt `berichte/JJJJ-MM-TT-freitag-0730.json`, erzeugt beide
   PDFs, committet nach `main` und schickt eine Push-Nachricht.
2. Freitag 16:00 Uhr: derselbe Ablauf als Zwischenstand vor dem Wochenende, verglichen mit dem
   7:30-Lauf desselben Tages (`…-freitag-1600.json`). Gibt es keine Änderung, sagt der Bericht das.
3. Von Hand jederzeit: `SEO-Audit` in einer Claude-Code-Session mit diesem Repo schreiben.

## Feste Parameter

- Website: https://fsh-documentation.com/ · Zweitdomain fsh-documentation.de (E-Mail-Domain)
- Firma: FSH-Documentation UG (haftungsbeschränkt), Teltow · Zielmarkt Deutschland, regional
  Teltow, Potsdam, Berlin, Brandenburg
- Kernbegriffe und Wettbewerber: Prüfkatalog im Skill
- Ausgabe: JSON je Lauf, zwei PDFs (Bericht A4 hoch, Kurzfassung A4 quer), Verlaufszeile

## Dateien

| Datei | Zweck |
|---|---|
| `README.md` | diese Übersicht, Aufbau der Routine |
| `verlauf.md` | eine Zeile pro Lauf |
| `berichte/JJJJ-MM-TT-<lauf>.json` | Bericht-Daten je Lauf; die letzte ist der Vergleichsstand |
| `massnahmen/JJJJ-MM-TT-phase-2.md` und `.pdf` | Maßnahmenpaket: Befundprüfung, Benchmark, Zielbegriffe, Seitenplan, Alt-Texte, Rechtsbefunde, 30-Tage-Plan |
| `SEO-Audit-FSH-Documentation.pdf` | aktueller Bericht (A4, mehrseitig) |
| `SEO-Audit-FSH-Documentation-Kurzfassung.pdf` | aktuelle Kurzfassung (A4 quer, eine Seite) |
| `tools/render_report.py` | JSON prüfen (`--check`) und PDFs erzeugen |
| `tools/onpage_check.py` | On-Page-Merkmale einer gespeicherten HTML-Seite als JSON |
| `tools/fetch_rendered.js` | gerenderter DOM, Ladezeiten und Screenshot einer Seite (Chromium über Playwright) |
| `tools/browser_setup.sh` | einmal je Container: Proxy-Zertifikat der Claude-Umgebung für Chromium einrichten |
| `tools/md_to_pdf.py` | setzt eine Markdown-Datei (zum Beispiel ein Maßnahmenpaket) als A4-PDF im Berichtsstil |
| `tools/fonts/` | IBM Plex (SIL Open Font License), damit die PDFs ohne Internet gleich aussehen |

PDFs von Hand erzeugen (braucht Node mit Playwright und Chromium, wie in der Claude-Code-Umgebung):

```bash
python3 seo-audit/tools/render_report.py seo-audit/berichte/2026-09-19-manuell.json --out seo-audit
```

## Freitags-Routine (automatisch)

Aufbau, Stand 19.09.2026, nach dem Muster der Wocheneinkauf-Routine:

- **Session „SEO-Audit FSH (Routine)"** in Claude Code: dauerhafte Session mit dem Repo auf
  `main`, pusht direkt nach `main`. Sie ist das Gedächtnis der Routine. Rückmeldungen (zum Beispiel
  „Domain ist jetzt freigegeben" oder „Title wurde geändert") gehören in diese Session.
- **Routine „SEO-Audit FSH (Fr 7:30)"**: schickt jeden Freitag um 7:30 Uhr Berlin das Wort
  „SEO-Audit" mit den Laufanweisungen in diese Session. Cron in UTC: `30 5 * * 5` (Sommerzeit)
  bzw. `30 6 * * 5` (Winterzeit, 26.10.2026 bis 27.03.2027).
- **Routine „SEO-Audit FSH Zwischenstand (Fr 16:00)"**: dasselbe um 16:00 Uhr Berlin als
  Zwischenstand. Cron in UTC: `0 14 * * 5` (Sommerzeit) bzw. `0 15 * * 5` (Winterzeit).
- **Zeitumstellung**: Die Umstellung beider Routinen am 26.10.2026 ist als Erinnerung hinterlegt,
  die Rückstellung am 29.03.2027 wird dabei angelegt. Bleibt eine Erinnerung aus, den Cron von
  Hand ändern.
- **Benachrichtigung**: Nach jedem Lauf eine Push-Nachricht mit Erreichbarkeit, offenen Befunden
  und Änderungen. Der vollständige Bericht liegt in `berichte/` und als PDF in diesem Ordner.
- **Voraussetzung**: Skill und Werkzeuge müssen auf `main` liegen, also PR #2 gemerged sein.
  Solange nicht, meldet der Lauf nur „PR #2 noch nicht gemerged" und erstellt nichts.
- **Netzwerk**: Die Umgebung „Default" steht seit dem 19.09.2026 auf vollem Netzwerkzugriff, die
  Website ist damit direkt abrufbar und Technik- und On-Page-Prüfung laufen mit. Fällt die Freigabe
  weg, prüft die Routine nur über den Suchindex und markiert Technik und On-Page als „offen".
  Für das Browser-Rendering muss je Container einmal `tools/browser_setup.sh` laufen (macht der
  Skill selbst); es importiert das Zertifikat des Umgebungs-Proxys in den Chromium-Speicher.
- **Von Hand starten**: In der Session „SEO-Audit FSH (Routine)" einfach `SEO-Audit` schreiben.
  Nicht „Jetzt ausführen" der Routine benutzen (erzwungene Läufe starten ohne Repository).

## Stand 19.09.2026 (Erstaufnahme, manueller Lauf)

Nur die Startseite von fsh-documentation.com ist im Suchindex sichtbar, und nur über den
Firmennamen. Sechs Befunde: Domain-Split .com/.de (B1), Seitentitel ohne Marke, Ort und Leistung
(B2), nur die Startseite auffindbar (B3), keine Sichtbarkeit für Kernbegriffe (B4), Marke „FSH"
mehrdeutig (B5), lokale Einträge vorhanden, Google-Profil unklar (B6). Technik und On-Page konnten
nicht geprüft werden (Seitenabruf gesperrt). Datei: `berichte/2026-09-19-manuell.json`.

## Stand 19.09.2026, zweiter Lauf (Vollprüfung)

Nach der Netzwerkfreigabe wurden Technik und On-Page nachgeholt. Die Seite ist eine Canva-Website:
Einseiter, Inhalt per JavaScript, 3.123 Wörter, aber keine Überschriften, keine Alt-Texte,
kein Canonical, keine strukturierten Daten, Sitemap mit einer URL, keine robots.txt, 3,1 MB und
3,8 bis 4,1 s Ladezeit im Labor (Desktop, vollständig geladen; Nachmessung in drei Läufen am
21.09.2026, der Erstwert 3,5 MB / 4,8 s vom 19.09. war nicht reproduzierbar).
fsh-documentation.de zeigt eine STRATO-Platzhalterseite. Elf Befunde (fünf hoch, fünf mittel,
einer niedrig; nach der Prüfung in Phase 2: drei hoch, sechs mittel, zwei niedrig).
Datei: `berichte/2026-09-19-manuell-2.json`.

## Stand 21.09.2026, Phase 2 (Maßnahmenpaket)

Ein Multi-Agent-Lauf hat jeden der elf Befunde von einem unabhängigen Skeptiker prüfen lassen
(Beleg, Relevanz, Umsetzbarkeit in Canva und STRATO), sieben Wettbewerber analysiert, acht
Abfragefamilien untersucht, die Rechtstexte zweifach geprüft und Alt-Texte für alle 19
Bildvorkommen geschrieben. Ergebnis: alle Befunde bestätigt, drei Prioritäten gesenkt (B2, B7, B8),
neue Verteilung 3 hoch / 6 mittel / 2 niedrig. Das Dokument wurde anschließend in zwei Runden von je
drei unabhängigen Kritikern (Faktentreue, Vollständigkeit, Konsistenz) gegengelesen; 74 der 84
Beanstandungen wurden eingearbeitet, drei als unbegründet zurückgewiesen. Daraus entstand ein
Seitenplan mit acht Seiten
(Title, H1, Description, Zielbegriffe, Gliederung, interne Links) und ein 30-Tage-Plan.
Datei: `massnahmen/2026-09-21-phase-2.md` und `.pdf`.
