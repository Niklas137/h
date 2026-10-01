# Dokumentenprüfer (Web-App)

Prüft technische Dokumente (Word, PDF) gegen die Regelsätze Basisprüfung, DIN 82079-1 und
CE / EU-Konformität. Mehrere Benutzer mit eigenem Konto und eigenen Einstellungen, Oberfläche im
Look von FSH-Documentation, Berichte als PDF in Deutsch, Englisch, Ukrainisch und Russisch.

Die bisherige Streamlit-App `app.py` im Ordner darüber bleibt als historischer Vergleich unverändert.
Die Web-App verwendet weiterhin deren Suchregeln und Gewichtungen. Die P0-Korrektur vom
1. Oktober 2026 ändert bewusst die Bewertung: Schlüsselwortsuche ist eine automatische Vorprüfung,
kein Nachweis von Vollständigkeit, Richtigkeit oder Konformität und keine fachliche Freigabe.

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
bedienbar. Die Datenbanktransaktion ist kurz, die PDFs entstehen danach. Die Oberfläche fragt die
Prüfung mit `fortschritt=1` an und bekommt einen Zeilenstrom (NDJSON): je eine Zeile für die Phasen
`lesen`, `pruefen`, `berichte` (mit `n` von `von`), zuletzt `fertig` mit dem Ergebnis oder `fehler`.
Das Statuspanel zeigt diese Phasen; es erscheint erst, wenn die Prüfung länger als 400 ms dauert,
und nennt keinen erfundenen Prozentwert. Ohne `fortschritt` antwortet die Route wie bisher mit JSON.

## Ergebnis und Weitergabe

1. Ergebnis: Suchscore, Ampel, Prüfhinweise, geschätzter Aufwand, Fazit der Vorprüfung.
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

Die Bestandstests prüfen Erstanmeldung, Passwortregel, Sperre, Einstellungen, Verwaltung, Rechte,
Word-Prüfung, PDFs in vier Sprachen, ZIP, Ablage, Mail-Entwurf, CLI und Fortschritts-Zeilenstrom.
`tests/test_p0.py` ergänzt Gegenproben für ungültige Regeln (auch nach einer gültigen Ladung),
irreführende Stichwortlisten, kritische Hinweise bei hohem Suchscore, Sperrumgehung und die
Kennzeichnung in beiden Berichtstypen und allen vier Sprachen.

## Bewertungsgrenzen und P0-Korrekturen

- Der Suchscore bleibt rechnerisch `100 - Summe der Hinweisgewichtungen`, mindestens 0.
  Er wird als Punkte von 100 angezeigt, nicht als Qualitäts- oder Konformitätsprozent.
- Alle geprüften Regeln bleiben fachlich offen, auch wenn ein Suchwort vorkommt.
  API und gespeichertes Ergebnis nennen `pruefstatus=fachlich_offen`, `freigabe=false`,
  `bewertungsart=schluesselwortsuche` sowie den Suchstatus jeder Regel in `regelpruefungen`.
- Kritische Prüfhinweise oder weniger als 60 Suchpunkte ergeben Rot. Sonst gilt Gelb.
  Diese Automatik erzeugt niemals eine grüne Freigabe. Semantische Inhaltsprüfung und ein
  fachlicher Freigabeworkflow sind damit noch nicht implementiert.
- Regeldefekte liefern HTTP 503 im JSON-Modus, einen abschließenden Fehler mit Status 503
  im bereits begonnenen NDJSON-Strom oder Exitcode 4 in der CLI. Es entsteht keine neue Prüfung.
- Ein Aufruf der Erstanmeldung hebt eine laufende Anmeldesperre nicht mehr auf und verlängert
  sie auch nicht. Nach regulärem Ablauf ist eine korrekte Anmeldung wieder möglich.
- Berichte unterscheiden nicht gewählte CE-Prüfungen von einer gewählten CE-Suche ohne Hinweise.
- Bestehende Datenbanken brauchen keine Migration. Historische Ergebnisse und gespeicherte PDFs
  bleiben erhalten; die Oberfläche kennzeichnet geöffnete Altprüfungen. Für die neue Bewertung
  muss das Originaldokument erneut geprüft werden.
- Noch offen: Word-Tabellen, gemischte Scan-PDFs, Satzermittlung, Fundstellen im PDF,
  vollständige Regelübersetzungen, überschreibungsfreie Ablage und fachliche Vergleichsdokumente.

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
app/pruefer/pruefung.py Suchprüfung mit konservativer Bewertung, keine fachliche Freigabe
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
