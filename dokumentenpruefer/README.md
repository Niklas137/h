# Dokumentenprüfer (Web-App)

Prüft technische Dokumente (Word, PDF) gegen die Regelsätze Basisprüfung, DIN 82079-1 und
CE / EU-Konformität. Mehrere Benutzer mit eigenem Konto und eigenen Einstellungen, Oberfläche im
Look von FSH-Documentation, Berichte als PDF in Deutsch, Englisch, Ukrainisch und Russisch.

Die bisherige Streamlit-App `app.py` im Ordner darüber bleibt unverändert als Rückfall. Die
Prüflogik ist 1:1 übernommen (Schlüsselwörter, Gewichtung, Score, Ampel, Fazit, CE-To-dos).
Die Prüfung ist eine automatische Vorprüfung per Schlüsselwortsuche. Die fachliche Prüfung und
Freigabe bleibt bei FSH-Documentation; jeder Bericht und die Kundenmail sagen das in einem Satz.

## Start auf dem Mac

1. Ordner `dokumentenpruefer` öffnen, Doppelklick auf `start.command`.
   Beim ersten Start wird eine Python-Umgebung angelegt (`.venv`), die Pakete werden installiert
   und ein Admin-Konto wird abgefragt (E-Mail-Adresse, Name). Das Einmal-Passwort wird einmal im
   Terminal angezeigt.
2. Der Browser öffnet `http://localhost:8765`.
3. "Erstanmeldung mit Einmal-Passwort": E-Mail-Adresse und Einmal-Passwort eingeben, Code aus der
   E-Mail (oder aus `daten/codes.log`, solange kein SMTP eingerichtet ist), dann Name und eigenes
   Passwort setzen (mindestens 14 Zeichen, ein Großbuchstabe, ein Sonderzeichen).

Von Hand statt per `start.command`:

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m app.verwaltung admin --email niklas@firma.de --name "Niklas"
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8765
```

## Regeldateien

Die Regelsätze liegen im Ordner `regeln/`:

| Datei                 | Regelsatz          | Status                              |
|-----------------------|--------------------|-------------------------------------|
| `pruefkatalog.json`   | Basisprüfung       | enthalten (Stand 21. Mai 2026), Übersetzungen en/uk/ru seit 5. Oktober |
| `normlogik_82079.json`| DIN 82079-1        | enthalten, mit Übersetzungen        |
| `ce_logik.json`       | CE / EU-Konformität| enthalten (Stand 21. Mai 2026), Übersetzungen en/uk/ru seit 5. Oktober |

Fehlt eine gewählte Regeldatei oder ist sie ungültig, bricht die Prüfung ohne Ergebnis und ohne
Berichte ab. Validiert werden JSON, nicht leere Regellisten, eindeutige IDs, Suchwörter, Pflichtfelder,
Fehlerklassen und Gewichtungen. Nicht ausgewählte Regelsätze dürfen fehlen. Unbekannte Regelsatznamen
werden abgewiesen, auch zusammen mit gültigen Namen. Für
Empfehlungen in anderen Sprachen kann jede Regel die Felder `empfehlung_en`, `empfehlung_uk`,
`empfehlung_ru` (und `bereich_en` usw.) tragen. Ohne Übersetzung wird der deutsche Text genommen.
Seit dem 5. Oktober tragen alle 24 Regeln Bereich und Empfehlung in en, uk und ru; ein Test stellt
sicher, dass in fremdsprachigen Berichten kein deutscher Regeltext steht. Zitate aus dem geprüften
Dokument (Fundstellen, zu lange Sätze) bleiben in der Sprache des Dokuments. Die ukrainischen und
russischen Fassungen sind von Niklas fachlich gegenzulesen.

Einzelne Prüfpunkte: `GET /api/regeln` liefert je Regelsatz alle Punkte (die Basisprüfung
enthält zusätzlich den eingebauten Punkt `TXT-001` Satzlänge). Auf der Prüfseite lassen sich
Punkte abwählen; die Auswahl wird je Konto gespeichert (`PUT /api/ich/pruefpunkte`) und bei der
Prüfung als Feld `ausgelassen` (IDs, kommagetrennt) mitgeschickt, in der Kommandozeile mit
`--ohne CHK-008,DIN-008`. Ausgelassene Punkte zählen nicht in den Score; Ergebnis und beide
Berichte nennen „n von N geprüft“ und die ausgelassenen Punkte. Ein Regelsatz ohne aktiven Punkt
und unbekannte IDs sind ein Fehler (400), bevor etwas geprüft wird.

## Konten und Rollen

- Inhaber: das erste Konto (angelegt mit `app.verwaltung admin`). Nur der Inhaber löscht Konten;
  dabei gehen Sitzungen, Einstellungen und die Prüfungen samt Berichten der Person mit, abgelegte
  Berichte in `output/` bleiben. Niemand außer dem Inhaber selbst kann sein Konto ändern, sperren
  oder ihm ein neues Einmal-Passwort geben; sich selbst löschen kann er nicht. In bestehenden
  Datenbanken wird beim Start das älteste Admin-Konto Inhaber.
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

## Oberfläche in vier Sprachen

Der Schalter „Sprache“ in der Kopfzeile stellt die ganze Oberfläche um (Deutsch, Englisch,
Ukrainisch, Russisch) und ist zugleich die Basissprache der Berichte. Die Texte liegen in
`app/static/i18n.js` (ein Schlüssel je Text, Deutsch als Quelle); Elemente in `index.html` tragen
`data-i18n`, dynamische Texte laufen in `app.js` über `t(schluessel, werte)`. Die Oberfläche
schickt ihre Sprache als Kopf `X-Sprache` mit; die API antwortet dann mit Meldungen
(`app/meldungen.py`) und Anzeigetexten (Fazit, Bereiche, Empfehlungen, Klassen, Bewertungen,
Lesehinweise) in dieser Sprache. Ohne Kopf bleibt alles deutsch, so laufen Tests und Skripte
unverändert. Auf der Anmeldeseite wählen vier Knöpfe die Sprache; nach der Anmeldung gilt die
Kontosprache. Ukrainisch und Russisch sind von Niklas fachlich gegenzulesen.

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

Eine Prüfung nimmt eine oder mehrere Dateien, bis zu 20 (`DP_MAX_DATEIEN`), je bis 25 MB. Die
Dateien eines Aufrufs bilden einen Lauf: Jedes Dokument wird einzeln gelesen, geprüft und bekommt
seine eigenen Berichte; ein unlesbares Dokument wird mit Fehlermeldung übersprungen, die anderen
laufen weiter. Nur defekte Regeldateien brechen den ganzen Lauf ab.

Lesen, Prüfen und PDF-Erzeugung laufen in einem Arbeitsfaden, der Server bleibt währenddessen
bedienbar. Die Datenbanktransaktion je Dokument ist kurz, die PDFs entstehen danach. Die
Oberfläche fragt die Prüfung mit `fortschritt=1` an und bekommt einen Zeilenstrom (NDJSON): je
Dokument Zeilen für die Phasen `lesen`, `pruefen`, `berichte` (mit `n` von `von`), jeweils mit
`dokument`, `dokumente` und `datei`; nach jedem Dokument eine Zeile `ergebnis` (mit `ergebnis` oder
`fehler`); zuletzt `fertig` mit dem Lauf. Das Statuspanel zeigt „Dokument n von N“ und die Phasen;
es erscheint erst, wenn die Prüfung länger als 400 ms dauert, und nennt keinen erfundenen
Prozentwert. Ohne `fortschritt` antwortet die Route mit JSON: bei einer Datei die Prüfung selbst,
bei mehreren der Lauf (`ergebnisse`, `fehler`, `pdfAnzahl`, `zip`, `ablegen`).

Lauf-Routen: `GET /api/lauf/{id}` (alle Prüfungen des Laufs), `GET /api/lauf/{id}/zip` (alle PDFs),
`POST /api/lauf/{id}/ablegen` (alle Berichte nach `output/`). Die Oberfläche zeigt bei mehreren
Dokumenten zuerst die Tabelle des Laufs (Dokument, Score, Ampel, Funde, Aufwand), darunter die
Einzelheiten des gewählten Dokuments; „Ansehen“ wechselt.

## Was gelesen wird

- Word: Absätze und Tabellen in Dokumentreihenfolge, auch verschachtelte Tabellen. Tabellenzellen
  tragen in der Fundstelle den Zusatz „(Tabelle)".
- PDF: Text je Seite, erst PyPDF2, bei leeren Seiten zusätzlich pdfplumber. Seiten ohne Textebene
  (Scans) werden nicht geprüft und als Lesehinweis genannt: im Ergebnis, in beiden Berichten und
  in der Kommandozeile. Ein PDF ganz ohne Text wird mit einer Fehlermeldung abgewiesen.
- Ablage in `output/` überschreibt nie: Gleicher Inhalt wird wiederverwendet, sonst entsteht die
  nächste Version (`_v02`, `_v03`). Gilt für die Oberfläche und die Kommandozeile.

## Ergebnis und Weitergabe

1. Ergebnis: Score, Ampel, Funde, Aufwand, Fazit.
2. Berichte: PDF je Sprache für Prüfbericht und Fachbericht.
3. Weitergabe: E-Mail-Entwurf an den Kunden (auf dem Mac in Apple Mail, wird nie gesendet),
   alle PDFs als ZIP, Berichte in `output/` ablegen, Prüfung abschließen.

Dateinamen: `JJJJ-MM-TT_Dokument_Pruefbericht_DE_v01.pdf`.

## Prüfung ohne Browser

Für Claude Code oder Skripte prüft `app/cli.py` Dokumente direkt und legt die PDFs ab:

```bash
./.venv/bin/python -m app.cli pruefen ../inbox/Anleitung.docx --sprachen de,en --ausgabe ../output
./.venv/bin/python -m app.cli pruefen ../inbox/*.docx --regelsaetze basis,din
```

Mehrere Dateien werden nacheinander geprüft; eine unlesbare Datei wird gemeldet, die anderen laufen
weiter. Der Exitcode ist der schlechteste je Datei (0 gut, 2 Aufruf, 3 Datei, 4 Regeldateien).
`--sprachen` nimmt die Basissprache und höchstens eine Zusatzsprache, `--regelsaetze` standardmäßig
`basis,din,ce`, `--json` gibt die Zusammenfassung maschinenlesbar aus (eine Datei: Objekt, mehrere:
Liste).

## Konfiguration (Umgebungsvariablen, alle optional)

| Variable            | Bedeutung                                                     |
|---------------------|---------------------------------------------------------------|
| `DP_DATEN`          | Datenordner (Standard `daten/`): Datenbank, Berichte, Geheimnis |
| `DP_OUTPUT`         | Ablageordner für "in output ablegen" (Standard `output/`)     |
| `DP_VERIFIZIERUNG`  | `code` (Standard) oder `aus` (kein Code bei der Erstanmeldung) |
| `DP_SMTP_HOST`, `DP_SMTP_PORT`, `DP_SMTP_USER`, `DP_SMTP_PASSWORT`, `DP_SMTP_ABSENDER` | Versand des Codes. Ohne SMTP steht der Code in `daten/codes.log`. |
| `DP_SUPPORT`, `DP_TELEFON`, `DP_ZEITEN` | Kontaktangaben in der Hilfe                       |
| `DP_DEV=1`          | Entwicklungsmodus: Code wird in der Oberfläche angezeigt      |
| `DP_COOKIE_SECURE=1`| Cookie nur über HTTPS (für Betrieb hinter einem Proxy)        |

Zugangsdaten gehören nicht ins Projekt. SMTP-Daten nur als Umgebungsvariable setzen.

## Tests

```bash
./.venv/bin/python -m pytest tests -q
```

Die Bestandstests prüfen Erstanmeldung, Passwortregel, Sperre, Einstellungen, Verwaltung, Rechte,
Word-Prüfung, PDFs in vier Sprachen, ZIP, Ablage, Mail-Entwurf, CLI, Fortschritts-Zeilenstrom und
Läufe mit mehreren Dateien (auch mit einer unlesbaren darunter, Höchstzahl, Lauf-ZIP und -Ablage),
Inhaber und Konto löschen, Auswahl einzelner Prüfpunkte bis in den Bericht, fremdsprachige Berichte
ohne deutschen Regeltext, API-Meldungen und Anzeigetexte je Sprachkopf.
`tests/test_p0.py` ergänzt Gegenproben für ungültige Regeldateien (auch nach einer gültigen
Ladung), ungültige Regelsatz-Auswahl, Sperrumgehung und den Vorprüfungssatz in beiden
Berichtstypen und allen vier Sprachen.

## Vorprüfung und Regelprüfung

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
app/mail.py            Versand des Codes (SMTP oder Protokoll)
app/verwaltung.py      Kommandozeile für Konten
app/cli.py             Kommandozeile: Dokumente prüfen, PDFs ablegen
app/pruefer/lesen.py   Word und PDF einlesen
app/pruefer/regeln.py  Regeldateien laden
app/pruefer/pruefung.py Prüflogik (aus app.py übernommen), Regelsätze vorher validiert
app/pruefer/texte.py   Berichtstexte in de, en, uk, ru
app/pruefer/berichte.py PDF-Erzeugung (reportlab, IBM Plex Sans)
app/static/            Oberfläche: index.html, app.js, i18n.js (Texte in vier Sprachen), app.css, Schriften, Marke
app/meldungen.py       API-Meldungen in vier Sprachen
regeln/                Regeldateien
tests/                 pytest
daten/, output/        werden zur Laufzeit angelegt, nicht versioniert
```

## Offen

- Regeldateien `pruefkatalog.json` und `ce_logik.json`: Stand vom 21. Mai 2026 aus der Git-Historie. Gibt es auf dem Mac eine neuere Fassung, diese hierher kopieren (die Übersetzungen vom 5. Oktober dann übernehmen).
- Ukrainische und russische Texte in Regeldateien, `texte.py`, `meldungen.py` und `i18n.js` fachlich gegenlesen (Niklas).
- Impressum und Datenschutz unter Einstellungen → Rechtliches mit den eigenen Texten füllen
  (`app/static/index.html`, Bereich `data-pane="recht"`).
  Impressum nach DDG: Firma, Anschrift, vertretungsberechtigte Person, E-Mail, Telefon, Registereintrag, Umsatzsteuer-ID.
  Datenschutzerklärung: Verantwortlicher, Zwecke und Rechtsgrundlagen, gespeicherte Daten (Konto, Einstellungen, Prüfergebnisse), Speicherdauer, Rechte der Betroffenen, Kontakt.
- Kontaktangaben für die Hilfe setzen (`DP_SUPPORT`, `DP_TELEFON`, `DP_ZEITEN`).
- SMTP für den Code einrichten oder `DP_VERIFIZIERUNG=aus` setzen.
