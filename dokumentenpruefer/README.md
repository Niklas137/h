# Dokumentenprüfer (Web-App)

Prüft technische Dokumente (Word, PDF) gegen die Regelsätze Basisprüfung, DIN 82079-1 und
CE / EU-Konformität. Mehrere Benutzer mit eigenem Konto und eigenen Einstellungen, Oberfläche im
Look von FSH-Documentation, Berichte als PDF in Deutsch, Englisch, Ukrainisch und Russisch.

Die bisherige Streamlit-App `app.py` im Ordner darüber bleibt unverändert als Rückfall. Die
Prüflogik ist 1:1 übernommen (Schlüsselwörter, Gewichtung, Score, Ampel, Fazit, CE-To-dos).

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
| `pruefkatalog.json`   | Basisprüfung       | enthalten (Stand 21. Mai 2026), nur deutsch |
| `normlogik_82079.json`| DIN 82079-1        | enthalten, mit Übersetzungen        |
| `ce_logik.json`       | CE / EU-Konformität| enthalten (Stand 21. Mai 2026), nur deutsch |

Fehlt eine Datei, zeigt die App einen Hinweis und der Regelsatz liefert keine Funde. Für
Empfehlungen in anderen Sprachen kann jede Regel die Felder `empfehlung_en`, `empfehlung_uk`,
`empfehlung_ru` (und `bereich_en` usw.) tragen. Ohne Übersetzung wird der deutsche Text genommen.

## Konten und Rollen

- `admin`: legt Benutzer an, vergibt neue Einmal-Passwörter, ändert Rollen und Status.
- `mitglied`: prüft Dokumente, verwaltet nur das eigene Konto.
- Neue Benutzer legt ein Admin unter Einstellungen → Verwaltung an. Er bekommt ein Einmal-Passwort
  (7 Tage gültig) und gibt es persönlich weiter.
- Passwort vergessen: Admin vergibt ein neues Einmal-Passwort, danach läuft die Erstanmeldung erneut.
- Nach 8 Fehlversuchen ist ein Konto 15 Minuten gesperrt.

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
| `DP_SMTP_HOST`, `DP_SMTP_PORT`, `DP_SMTP_USER`, `DP_SMTP_PASSWORT`, `DP_SMTP_ABSENDER` | Versand des Codes. Ohne SMTP steht der Code in `daten/codes.log`. |
| `DP_SUPPORT`, `DP_TELEFON`, `DP_ZEITEN` | Kontaktangaben in der Hilfe                       |
| `DP_DEV=1`          | Entwicklungsmodus: Code wird in der Oberfläche angezeigt      |
| `DP_COOKIE_SECURE=1`| Cookie nur über HTTPS (für Betrieb hinter einem Proxy)        |

Zugangsdaten gehören nicht ins Projekt. SMTP-Daten nur als Umgebungsvariable setzen.

## Tests

```bash
./.venv/bin/python -m pytest tests -q
```

23 Tests: Erstanmeldung mit Code, Passwortregel, Sperre, Einstellungen, Verwaltung, Rechte,
Prüfung einer erzeugten Word-Datei, PDFs in vier Sprachen, ZIP, Ablegen, E-Mail-Entwurf, Kommandozeile.

## Aufbau

```
app/main.py            FastAPI: Seiten, API, Prüfung, Berichte
app/auth.py            Passwörter (argon2), Einmal-Passwort, Code, Sitzungen, Sperre
app/db.py              SQLite-Schema und Verbindung
app/einstellungen.py   Einstellungen je Benutzer
app/mail.py            Versand des Codes (SMTP oder Protokoll)
app/verwaltung.py      Kommandozeile für Konten
app/cli.py             Kommandozeile: Dokument prüfen, PDFs ablegen
app/pruefer/lesen.py   Word und PDF einlesen
app/pruefer/regeln.py  Regeldateien laden
app/pruefer/pruefung.py Prüflogik (aus app.py übernommen)
app/pruefer/texte.py   Berichtstexte in de, en, uk, ru
app/pruefer/berichte.py PDF-Erzeugung (reportlab, IBM Plex Sans)
app/static/            Oberfläche: index.html, app.js, app.css, Schriften, Marke
regeln/                Regeldateien
tests/                 pytest
daten/, output/        werden zur Laufzeit angelegt, nicht versioniert
```

## Offen

- Regeldateien `pruefkatalog.json` und `ce_logik.json`: Stand vom 21. Mai 2026 aus der Git-Historie. Gibt es auf dem Mac eine neuere Fassung, diese hierher kopieren. Übersetzungen (`empfehlung_en/uk/ru`) fehlen noch, Berichte in anderen Sprachen zeigen dort die deutsche Empfehlung.
- Impressum und Datenschutz unter Einstellungen → Rechtliches mit den eigenen Texten füllen
  (`app/static/index.html`, Bereich `data-pane="recht"`).
  Impressum nach DDG: Firma, Anschrift, vertretungsberechtigte Person, E-Mail, Telefon, Registereintrag, Umsatzsteuer-ID.
  Datenschutzerklärung: Verantwortlicher, Zwecke und Rechtsgrundlagen, gespeicherte Daten (Konto, Einstellungen, Prüfergebnisse), Speicherdauer, Rechte der Betroffenen, Kontakt.
- Kontaktangaben für die Hilfe setzen (`DP_SUPPORT`, `DP_TELEFON`, `DP_ZEITEN`).
- SMTP für den Code einrichten oder `DP_VERIFIZIERUNG=aus` setzen.
- Oberfläche in Englisch, Ukrainisch und Russisch (Phase 2).
