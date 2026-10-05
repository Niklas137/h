# Dokumentenprüfer (Web-App)

Prüft technische Dokumente (Word, PDF) gegen die Regelsätze Basisprüfung, DIN 82079-1 und
CE / EU-Konformität. Mehrere Benutzer mit eigenem Konto und eigenen Einstellungen, Oberfläche im
Look von FSH-Documentation, Berichte als PDF in Deutsch, Englisch, Ukrainisch und Russisch.

Phase-1-Prüfstand 1.1.0: eigener Branch `codex/dokumentenpruefer`, eigene Arbeitskopie.
Der Claude-Branch bleibt unabhängig; Zusammenführen erst nach Prüfung.

Der aktuelle Abschlussstand steht in [PHASE1_ABSCHLUSS.md](PHASE1_ABSCHLUSS.md).
Die früheren Protokolle dokumentieren historische Zwischenstände. Für die automatische
lokale Abnahme steht `abnahme.command` bereit. Es verwendet ausschließlich Testdaten und
listet danach die noch persönlich zu prüfenden Punkte auf.

Die bisherige Streamlit-App `app.py` im Ordner darüber bleibt unverändert als Rückfall. Die
Schlüsselwortregeln, Gewichtung, Score, Ampel, Fazit und CE-To-dos sind übernommen.
Die Satzlängenprüfung wurde korrigiert: Sie zählt einzelne Sätze im Textabschnitt statt den
ganzen Absatz. Dadurch können neue Ergebnisse von früheren Fehlalarmen abweichen.
Die Prüfung ist eine automatische Vorprüfung per Schlüsselwortsuche. Die fachliche Prüfung und
Freigabe bleibt bei FSH-Documentation; jeder Bericht und die Kundenmail sagen das in einem Satz.

## Start auf dem Mac

1. Ordner `dokumentenpruefer` öffnen, Doppelklick auf `start.command`.
   Beim ersten Start wird eine Python-Umgebung angelegt (`.venv`), die Pakete werden installiert
   und ein Admin-Konto wird abgefragt (E-Mail-Adresse, Name). Das Einmal-Passwort wird einmal im
   Terminal angezeigt.
2. Der Browser öffnet `http://localhost:8765`.
3. "Erstanmeldung mit Einmal-Passwort": E-Mail-Adresse und Einmal-Passwort eingeben, Code aus der
   E-Mail, dann Name und eigenes
   Passwort setzen (mindestens 14 Zeichen, ein Großbuchstabe, ein Sonderzeichen).

Für einen lokalen Ersttest ohne SMTP: im Terminal `DP_DEV=1 ./start.command` starten.
Dann steht der Code in der Oberfläche. Ohne SMTP und ohne Entwicklungsmodus meldet die
App den fehlenden Versand ausdrücklich. Codes werden nie in Logs gespeichert.
Ein Doppelstart öffnet die bereits laufende eigene Instanz; ein fremder belegter Port wird gemeldet.

Von Hand statt per `start.command`:

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m app.verwaltung admin --email niklas@firma.de --name "Niklas"
./.venv/bin/python -m app.start
```

## Regeldateien

Die Regelsätze liegen im Ordner `regeln/`:

| Datei                 | Regelsatz          | Status                              |
|-----------------------|--------------------|-------------------------------------|
| `pruefkatalog.json`   | Basisprüfung       | Regelinhalt vom 21. Mai 2026, Übersetzungen de/en/uk/ru |
| `normlogik_82079.json`| DIN 82079-1        | enthalten, mit Übersetzungen        |
| `ce_logik.json`       | CE / EU-Konformität| Regelinhalt vom 21. Mai 2026, Übersetzungen de/en/uk/ru |

Fehlt eine gewählte Regeldatei oder ist sie ungültig, bricht die Prüfung ohne Ergebnis und ohne
Berichte ab. Validiert werden JSON, nicht leere Regellisten, eindeutige IDs, Suchwörter, Pflichtfelder,
Fehlerklassen und Gewichtungen. Nicht ausgewählte Regelsätze dürfen fehlen. Unbekannte Regelsatznamen
werden abgewiesen, auch zusammen mit gültigen Namen. Für
Empfehlungen in anderen Sprachen kann jede Regel die Felder `empfehlung_en`, `empfehlung_uk`,
`empfehlung_ru` (und `bereich_en` usw.) tragen. Ohne Übersetzung wird der deutsche Text genommen.

## Konten und Rollen

- `admin`: legt Benutzer an, vergibt neue Einmal-Passwörter, ändert Rollen und Status.
- `mitglied`: prüft Dokumente, verwaltet nur das eigene Konto.
- Neue Benutzer legt ein Admin unter Einstellungen → Verwaltung an. Er bekommt ein Einmal-Passwort
  (7 Tage gültig) und gibt es persönlich weiter.
- Passwort vergessen: Admin vergibt ein neues Einmal-Passwort, danach läuft die Erstanmeldung erneut.
- Nach 8 Fehlversuchen ist ein Konto 15 Minuten gesperrt. Ein neues Einmal-Passwort hebt die Sperre auf.

Befehle im Terminal (im Ordner `dokumentenpruefer`):

```bash
./.venv/bin/python -m app.verwaltung admin --email ... --name ...   # ersten Admin anlegen
./.venv/bin/python -m app.verwaltung einmal --email ...             # neues Einmal-Passwort
./.venv/bin/python -m app.verwaltung liste                          # alle Konten
```

## Einstellungen je Benutzer

Sprache (Deutsch, Englisch, Ukrainisch, Russisch) und Helligkeit sitzen in der Kopfleiste und
wirken sofort. Alles Weitere unter Einstellungen: Profil, Sicherheit (Passwort, Sitzungen),
Erscheinungsbild (Textgröße, Dichte), Sprachen (nur zum Nachlesen), Benachrichtigungen (Pop-up,
keine E-Mails), Verwaltung (Admin), Rechtliches (Impressum, Datenschutz), Info.

Die Oberflächensprache ist die Basissprache der Berichte. Eine zusätzliche Berichtssprache wird
je Prüfung auf der Prüfseite gewählt (eine oder keine). Je Sprache entstehen zwei PDFs:
Prüfbericht (intern, mit Gewichtung und Aufwand) und Fachbericht (für den Kunden).

Die Oberfläche selbst ist in dieser Version deutsch; die Spracheinstellung steuert die Berichte.

## Ablauf einer Prüfung

Lesen, Prüfen und PDF-Erzeugung laufen in einem Arbeitsfaden, der Server bleibt währenddessen
bedienbar. Erst wenn alle PDFs fertig sind, wird die Prüfung mit einer kurzen Datenbanktransaktion
in den Verlauf aufgenommen. Die Oberfläche fragt die
Prüfung mit `fortschritt=1` an und bekommt einen Zeilenstrom (NDJSON): je eine Zeile für die Phasen
`lesen`, `pruefen`, `berichte` (mit `n` von `von`), zuletzt `fertig` mit dem Ergebnis oder `fehler`.
Das Statuspanel zeigt diese Phasen; es erscheint erst, wenn die Prüfung länger als 400 ms dauert,
und nennt keinen erfundenen Prozentwert. Ohne `fortschritt` antwortet die Route wie bisher mit JSON.

## Was gelesen wird

- Word: Absätze und Tabellen in Dokumentreihenfolge, auch verschachtelte Tabellen. Tabellenzellen
  tragen in der Fundstelle den Zusatz „(Tabelle)".
- PDF: Text je Seite, erst PyPDF2, bei leeren Seiten zusätzlich pdfplumber. Seiten ohne Textebene
  (Scans) werden nicht geprüft und als Lesehinweis genannt: im Ergebnis, in beiden Berichten und
  in der Kommandozeile. Ein PDF ganz ohne Text wird mit einer Fehlermeldung abgewiesen.
- Ablage in `output/` überschreibt nie: Gleicher Inhalt wird wiederverwendet, sonst entsteht die
  nächste Version (`_v02`, `_v03`). Gilt für die Oberfläche und die Kommandozeile.
  Auch parallele Ablagen können keine vorhandene Datei ersetzen. Der Zielordner muss Hardlinks
  unterstützen (z. B. APFS auf dem Mac).
- Historie und Erfolgsmeldung erscheinen erst, wenn sämtliche PDFs fertig sind.
  Nach dem Abmelden werden verspätete Antworten verworfen. Eine laufende Arbeit auf dem Server
  kann weiterlaufen und bleibt dem ursprünglichen Konto zugeordnet.
- Verschachtelte Tabellen behalten ihre Reihenfolge; verbundene Zellen werden nur einmal gelesen.
  Der interne Prüfbericht enthält die verfügbaren Fundstellen.

## Ergebnis und Weitergabe

1. Ergebnis: Score, Ampel, Funde, Aufwand, Fazit.
2. Berichte: PDF je Sprache für Prüfbericht und Fachbericht.
3. Weitergabe: E-Mail-Entwurf an den Kunden (auf dem Mac in Apple Mail, wird nie gesendet),
   alle PDFs als ZIP, Berichte in `output/` ablegen, Prüfung abschließen.

Dateinamen: `JJJJ-MM-TT_Dokument_Pruefbericht_DE_v01.pdf`.

## Prüfung ohne Browser

Für Claude Code oder Skripte prüft `app/cli.py` ein Dokument direkt und legt die PDFs ab:

```bash
./.venv/bin/python -m app.cli pruefen ../inbox/Anleitung.docx --sprachen de,en --ausgabe ../output
```

`--sprachen` nimmt die Basissprache und höchstens eine Zusatzsprache, `--regelsaetze` standardmäßig
`basis,din,ce`, `--json` gibt die Zusammenfassung maschinenlesbar aus.

## Konfiguration (Umgebungsvariablen, alle optional)

| Variable            | Bedeutung                                                     |
|---------------------|---------------------------------------------------------------|
| `DP_DATEN`          | Datenordner (Standard `daten/`): Datenbank, Berichte, Geheimnis |
| `DP_OUTPUT`         | Ablageordner für "in output ablegen" (Standard `output/`)     |
| `DP_VERIFIZIERUNG`  | `code` (Standard) oder `aus` (kein Code bei der Erstanmeldung) |
| `DP_SMTP_HOST`, `DP_SMTP_PORT`, `DP_SMTP_USER`, `DP_SMTP_PASSWORT`, `DP_SMTP_ABSENDER` | Versand des Codes; ohne SMTP ist für den lokalen Test `DP_DEV=1` nötig. |
| `DP_SUPPORT`, `DP_TELEFON`, `DP_ZEITEN` | Kontaktangaben in der Hilfe                       |
| `DP_DEV=1`          | Entwicklungsmodus: Code wird in der Oberfläche angezeigt      |
| `DP_COOKIE_SECURE=1`| Cookie nur über HTTPS (für Betrieb hinter einem Proxy)        |

Zugangsdaten gehören nicht ins Projekt. SMTP-Daten nur als Umgebungsvariable setzen.

## Tests

```bash
./.venv/bin/python -m pytest tests -q
```

Die Bestandstests prüfen Erstanmeldung, Passwortregel, Sperre, Einstellungen, Verwaltung, Rechte,
Word-Prüfung, PDFs in vier Sprachen, ZIP, Ablage, Mail-Entwurf, CLI und Fortschritts-Zeilenstrom.
`tests/test_p0.py` ergänzt Gegenproben für ungültige Regeldateien (auch nach einer gültigen
Ladung), ungültige Regelsatz-Auswahl, Sperrumgehung und den Vorprüfungssatz in beiden
Berichtstypen und allen vier Sprachen.

`tests/test_satzlaenge.py` ergänzte zunächst 30 Fälle zur Absatzkorrektur: Satzzeichen, Abkürzungen,
Zahlen, die Grenze 25/26 Wörter, mehrere lange Sätze sowie Word-Absätze und Tabellenzellen.
Vor der Korrektur schlugen elf dieser Fälle fehl. Nach der Korrektur bestehen unter Linux
alle 113 Python-Tests. Die Abschlussprüfung ergänzt acht Regressionstests für lange
Punktfolgen und unveränderte Satzgrenzen (insgesamt 121 Python-Tests).

### Nachtest Satzlänge, 4. Oktober 2026

[GitHub-Actions-Lauf 37180806283](https://github.com/Niklas137/h/actions/runs/37180806283)
prüft den Commit `5e91281f4ff94c4479dbbd4a2286c313d7a95661` auf dem separaten Branch
`codex/dokumentenpruefer-satzlaenge`. Beide Jobs sind erfolgreich abgeschlossen.

| Umgebung | Python-Tests | Browserabnahme | Ergebnis |
|---|---|---|---|
| Ubuntu 24.04.5, Python 3.12.14 | 113 bestanden, 8,42 Sekunden | Chromium, Playwright 1.62.1; 8 Ablaufgruppen | Bestanden |
| macOS 26.6.2, Python 3.12.14 | 113 bestanden, 43,54 Sekunden | Chromium, Playwright 1.62.1; 8 Ablaufgruppen | Bestanden |

Die Browserprüfung umfasst Anmeldung, Word/PDF, Berichte/ZIP/Ablage, Einstellungen,
320/390 Pixel und Querformat, Fehlerfälle, Benutzerverwaltung und Kontentrennung nach Logout.
Zusätzlich werden drei kurze Sätze in einem Absatz ohne Fehlalarm und zwei lange Sätze mit
korrekter Anzahl geprüft. Beide Läufe melden keine JavaScript-Ausnahmen.
Screenshots und `browser-ergebnis.json` liegen in den Prüfartefakten des verlinkten Laufs.

Je vier Hinweise auf veraltete Schnittstellen wurden protokolliert: Starlette-TestClient mit
httpx, PyPDF2 und zweimal FastAPI `on_event`. Sie verursachten keine Testfehler.
Es wurden ausschließlich erzeugte Testdaten genutzt und keine E-Mails versendet.
Die macOS-Prüfung lief auf einem GitHub-Runner. Finder-Doppelklick, Apple Mail auf Niklas' Mac
und Safari waren nicht Teil dieses Nachtests. Die Grenzen der PDF-Satzrekonstruktion unten
bleiben bestehen. Zum Zeitpunkt dieses Laufs war PR #13 noch nicht zusammengeführt.

### Abschlussprüfung PR #13, 4. Oktober 2026

Die Review-Prüfung fand zwei zusätzliche Fehler: quadratische Laufzeit bei langen Punktfolgen
und übersehene lange Sätze mit Abkürzungen wie `z. B.,`. Beide sind korrigiert und durch
Regressionstests abgesichert. Punktfolgen werden vollständig gelesen und ihr Anschluss danach
geprüft; Komma, Semikolon und Doppelpunkt erhalten mehrteilige Abkürzungen.

[Abschließender Testlauf 37183103991](https://github.com/Niklas137/h/actions/runs/37183103991)
prüft Programmstand `9ded511bd7784f7c92574d16b74008cb60b5b9fd`:

| Umgebung | Python-Tests | Browserabnahme |
|---|---|---|
| Ubuntu, Python 3.12 | 121 bestanden, 10,33 Sekunden | Chromium; 8 Ablaufgruppen bestanden, keine JavaScript-Ausnahmen |
| macOS, Python 3.12 | 121 bestanden, 43,64 Sekunden | Chromium; 8 Ablaufgruppen bestanden, keine JavaScript-Ausnahmen |

Die jeweils vier Python-Deprecation-Warnungen bleiben bestehen. Die anschließende Änderung
betrifft nur diese Dokumentation. Die Prüfung belegt die technische Funktion des Teststands;
fachliche Zuverlässigkeit an echten Unterlagen und eine Prüfung auf dem Nutzer-Mac sind damit
nicht nachgewiesen. Die unten genannten heuristischen Grenzen bleiben offen.

## Vorprüfung und Regelprüfung

- Die Lesbarkeitsregel `TXT-001` meldet Sätze mit mehr als 25 durch Leerraum getrennten Wörtern.
  Mehrere kurze Sätze in einem Absatz lösen den Hinweis nicht aus. Die Trennung berücksichtigt
  Punkt, Frage- und Ausrufezeichen, schließende Anführungszeichen sowie übliche Abkürzungen
  (z. B. `z. B.`, `Nr.`, `ca.`) und deutsche Ordinalzahlen. Anzahl und Textauszug beziehen sich
  auf die erkannten Sätze; die bisherige Sammelgewichtung und Aufwandsschätzung bleiben gleich.
  Die Erkennung bleibt heuristisch. Die PDF-Aufbereitung verbindet passende Druckzeilen bereits vor der Satzprüfung.
  Bei `usw.` und `etc.` wird eine kleingeschriebene Fortsetzung berücksichtigt; mehrdeutige
  großgeschriebene Fortsetzungen bleiben eine Grenze.
  Nahe, gleich formatierte PDF-Zeilen werden inzwischen verbunden; Seitenwechsel bleiben eine Grenze.
- Score, Ampel und Fazit folgen der Vorgabe von Niklas und der alten App: Grün ab 80 %, Gelb ab
  60 %, sonst Rot. Score = 100 minus Summe der Gewichtungen aller Funde, mindestens 0.
- Die Schlüsselwortsuche ist eine Vorprüfung. Jeder Bericht trägt unter dem Kopf einen Satz,
  dass die fachliche Prüfung und Freigabe bei FSH-Documentation liegt; die Kundenmail ebenso.
  Die API liefert dazu `pruefstatus=fachlich_offen`, `freigabe=false`,
  `bewertungsart=schluesselwortsuche` und je Regel den Suchstatus in `regelpruefungen`.
- Gewählte Regeldateien werden vor jeder Prüfung vollständig validiert (JSON, nicht leere Liste,
  eindeutige IDs, Suchwörter, Fehlerklasse, Gewichtung, Pflichtfeld bei DIN). Ein Defekt bricht
  die Prüfung ab: HTTP 503 im JSON-Modus, Fehlerzeile mit Status 503 im Zeilenstrom, Exitcode 4
  in der Kommandozeile. Es entsteht keine Prüfung und kein PDF. Nicht gewählte Regelsätze dürfen fehlen.
- Berichte unterscheiden „CE nicht gewählt" von „CE gewählt, keine Funde".
- Eine laufende Anmeldesperre wird durch weitere Fehlversuche nicht verlängert. Ein neues
  Einmal-Passwort hebt sie auf.

## Aufbau

```
app/main.py            FastAPI: Seiten, API, Prüfung, Berichte
app/auth.py            Passwörter (argon2), Einmal-Passwort, Code, Sitzungen, Sperre
app/db.py              SQLite-Schema und Verbindung
app/einstellungen.py   Einstellungen je Benutzer
app/mail.py            Versand des Codes über SMTP, keine Codes in Logs
app/verwaltung.py      Kommandozeile für Konten
app/cli.py             Kommandozeile: Dokument prüfen, PDFs ablegen
app/start.py           Portprüfung, Erstkonto und lokaler Serverstart
app/sicherung.py       Geprüfte ZIP-Sicherung und Wiederherstellung in neuen Ordner
app/ablage.py          Atomare Dateiablage ohne Überschreiben
app/pruefer/lesen.py   Word und PDF einlesen
app/pruefer/regeln.py  Regeldateien laden
app/pruefer/pruefung.py Prüflogik (aus app.py übernommen), Regelsätze vorher validiert
app/pruefer/texte.py   Berichtstexte in de, en, uk, ru
app/pruefer/berichte.py PDF-Erzeugung (reportlab, IBM Plex Sans)
app/static/            Oberfläche: index.html, app.js, app.css, Schriften, Marke
regeln/                Regeldateien
tests/                 pytest
daten/, output/        werden zur Laufzeit angelegt, nicht versioniert
```

## Sicherung und Wiederherstellung

Die Sicherung enthält eine konsistente SQLite-Kopie, die zugehörigen PDFs, vorhandene
Regeldateien, das Installationsgeheimnis und PDFs aus dem Ausgabeordner. Jede Datei wird mit
SHA-256 geprüft. SMTP-Zugangsdaten und Programmdateien sind nicht enthalten. Das Archiv enthält
Kontodaten und Dokumentergebnisse; privat außerhalb des Git-Repositories aufbewahren.

Im Programmordner ausführen:

```bash
./.venv/bin/python -m app.sicherung sichern --ziel "$HOME/Documents/Dokumentenpruefer-Sicherungen/phase1.zip"
./.venv/bin/python -m app.sicherung pruefen "$HOME/Documents/Dokumentenpruefer-Sicherungen/phase1.zip"
./.venv/bin/python -m app.sicherung wiederherstellen "$HOME/Documents/Dokumentenpruefer-Sicherungen/phase1.zip" --ziel "$HOME/Documents/Dokumentenpruefer-Wiederhergestellt"
```

Bestehende Sicherungen und Wiederherstellungsordner werden nie überschrieben. Für jede neue
Sicherung einen neuen Namen wählen. Die Wiederherstellung zeigt den passenden Startbefehl an.
Die alten Daten bleiben unberührt. Alte Sitzungen und Verifizierungscodes werden nicht reaktiviert;
Passwörter, Konten, Einstellungen und Berichte bleiben erhalten. Originale hochgeladener Dokumente
speichert die App nicht; diese müssen separat gesichert werden. Sichern ist bei laufendem Server
möglich. Beim Umstieg auf die Wiederherstellung zuerst den Server beenden.

## Reproduzierbare Abnahme

`tests/test_phase1.py` und `tests/test_betrieb.py` ergänzen Berichtfehler, parallele Ablage,
Tabellen, Übersetzungen, Sicherungsfehler, echte Serverstarts, Doppelstart, Neustart und
wiederhergestellte Berichte über HTTP. Alle Testdaten werden separat erzeugt.

Der Workflow `Dokumentenpruefer Phase 1` führt Python-Tests und `tests/browser_smoke.cjs` auf
Linux und macOS aus. Der Browserlauf prüft Erstanmeldung, Word/PDF, Downloads, Einstellungen,
320/390 px, Querformat, große Schrift, Benutzerwechsel und späte Antworten nach Logout.
Screenshots und Ergebnisse liegen als Workflow-Artefakte vor. Ein vorhandener Workflow ist
noch kein bestandener Lauf; den jeweiligen Status beachten. Native Apple-Mail-Übergabe und
Finder-Doppelklick bleiben Bestandteil der Mac-Abnahme.

## Installationseinstellungen und Phase 2

- Regeldateien `pruefkatalog.json` und `ce_logik.json`: deutscher Regelinhalt vom 21. Mai 2026. Neuere lokale Kataloge vor einem Update sichern und fachlich vergleichen; nicht durch einen älteren Stand ersetzen. Ergänzte Übersetzungen ändern keine Prüfregel.
- Impressum und Datenschutz unter Einstellungen → Rechtliches mit den eigenen Texten füllen
  (`app/static/index.html`, Bereich `data-pane="recht"`).
  Impressum nach DDG: Firma, Anschrift, vertretungsberechtigte Person, E-Mail, Telefon, Registereintrag, Umsatzsteuer-ID.
  Datenschutzerklärung: Verantwortlicher, Zwecke und Rechtsgrundlagen, gespeicherte Daten (Konto, Einstellungen, Prüfergebnisse), Speicherdauer, Rechte der Betroffenen, Kontakt.
- Kontaktangaben für die Hilfe setzen (`DP_SUPPORT`, `DP_TELEFON`, `DP_ZEITEN`).
- SMTP für den Code einrichten oder `DP_VERIFIZIERUNG=aus` setzen.
- Oberfläche in Englisch, Ukrainisch und Russisch (Phase 2).
- Passwortanfrage per E-Mail, besonderer Admin-Passwortworkflow und Zwei-Faktor-Anmeldung (Phase 2).

## Inhaltsnachweise und PDF-Satzgrenzen (5. Oktober 2026)

Die Suchprüfung wertet Abschnitte statt eines zusammengeklebten Volltexts aus. Leere
Word-Überschriften, erkannte PDF-Überschriften und Inhaltsverzeichniszeilen zählen allein
nicht als Inhalt. Eine Überschrift kann einen gefüllten Folgeabsatz einordnen. Word-Tabellen
werden für Suchnachweise nur innerhalb derselben Zeile verbunden; Satzlängen bleiben je Absatz.
Häufige Aussagen wie „Sicherheitshinweise fehlen“ und Platzhalter werden ausgeschlossen.
Verbote wie „Vorsicht: Nicht berühren“ bleiben Suchtreffer.

PDF-Zeilen werden anhand von Position, Abstand und Schriftgröße zusammengeführt. Spalten,
Listenanfänge, Formatwechsel und Seitenwechsel begrenzen das Zusammenführen. Auch eng
positionierte Wörter ohne gespeicherte Leerzeichen sind getestet. Bei einem Layout-Lesefehler
bleibt der bisherige zeilenweise Textleser als Rückfall erhalten.

Grenzen: Das ist weiterhin eine deutschsprachige Schlüsselwort-Heuristik, keine semantische
oder normative Freigabe. Ungewöhnliche Verneinungen, komplexe Tabellen, Trennstriche,
Seitenwechsel mitten im Satz und mehrdeutige Abkürzungen brauchen eine Sichtprüfung.
Ein passendes Kapitel mit beliebigem Fließtext beweist noch keine fachliche Vollständigkeit.
Score-Gewichte, Ampelschwellen und Freigabestatus sind unverändert.

`tests/test_nachweise.py` enthält 35 gezielte Gegenproben. Der Browserlauf ergänzt leere
Kapitel, fehlende Inhalte und einen über PDF-Zeilen verteilten langen Satz. Zwei ältere
Score-Tests verwenden jetzt affirmative Testtexte; sie hatten zuvor absichtlich auch
fehlende Inhalte als Treffer erwartet. Kundendokumente sind keine Repository-Testdaten.
