# SEO-Audit für FSH-Documentation

Wöchentliche Prüfung der Website fsh-documentation.com (und der Zweitdomain fsh-documentation.de),
automatisiert mit Claude Code. Auslöser ist das Wort **„SEO-Audit"** im Chat (oder `/seo-audit`).
Die Regeln stehen im Skill `.claude/skills/seo-audit/SKILL.md`, die Daten in diesem Ordner.

## So läuft eine Woche

1. Freitag 7:30 Uhr: Die Routine prüft Erreichbarkeit, Technik und On-Page (sofern die Seite
   abrufbar ist), Sichtbarkeit im Suchindex, Marke und lokale Einträge, vergleicht mit dem letzten
   Lauf, schreibt `berichte/JJJJ-MM-TT-freitag-0730.json`, erzeugt beide PDFs, committet nach
   `main` und schickt eine Push-Nachricht.
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
| `SEO-Audit-FSH-Documentation.pdf` | aktueller Bericht (A4, mehrseitig) |
| `SEO-Audit-FSH-Documentation-Kurzfassung.pdf` | aktuelle Kurzfassung (A4 quer, eine Seite) |
| `tools/render_report.py` | JSON prüfen (`--check`) und PDFs erzeugen |
| `tools/onpage_check.py` | On-Page-Merkmale einer gespeicherten HTML-Seite als JSON |
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
- **Grenze der Umgebung**: Die Netzwerkfreigabe der Claude-Umgebung sperrt den direkten Abruf der
  Website (Stand 19.09.2026). Bis die Domain freigegeben ist, prüft die Routine nur über den
  Suchindex; Technik und On-Page bleiben im Bericht als „offen" markiert. Sobald die Domain in der
  Umgebung erlaubt ist, laufen diese Prüfungen im nächsten Lauf automatisch mit.
- **Von Hand starten**: In der Session „SEO-Audit FSH (Routine)" einfach `SEO-Audit` schreiben.
  Nicht „Jetzt ausführen" der Routine benutzen (erzwungene Läufe starten ohne Repository).

## Stand 19.09.2026 (Erstaufnahme, manueller Lauf)

Nur die Startseite von fsh-documentation.com ist im Suchindex sichtbar, und nur über den
Firmennamen. Sechs Befunde: Domain-Split .com/.de (B1), Seitentitel ohne Marke, Ort und Leistung
(B2), nur die Startseite auffindbar (B3), keine Sichtbarkeit für Kernbegriffe (B4), Marke „FSH"
mehrdeutig (B5), lokale Einträge vorhanden, Google-Profil unklar (B6). Technik und On-Page konnten
nicht geprüft werden (Seitenabruf gesperrt). Datei: `berichte/2026-09-19-manuell.json`.
