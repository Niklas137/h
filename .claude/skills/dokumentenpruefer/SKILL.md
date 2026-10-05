---
name: dokumentenpruefer
description: Arbeit am Dokumentenprüfer von FSH-Documentation, der Web-App unter dokumentenpruefer/ (FastAPI, Konten, Einstellungen, PDF-Berichte in de/en/uk/ru). Verwenden, wenn der Nutzer „Dokumentenprüfer", „Prüftool" oder „Web-App prüfen" schreibt, ein Dokument gegen DIN 82079-1 oder CE prüfen lassen will, die App starten, testen, ändern oder an Falk übergeben möchte, oder fragt, wo Code, Plan und Berichte abgelegt sind. Auch bei Fragen zu Konten, Einmal-Passwort, Berichtssprache oder Prüfbericht und Fachbericht diesen Skill nehmen.
argument-hint: "[optional: starten | testen | prüfen inbox/Datei.docx en | ablage | übergabe]"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(date:*), Bash(ls:*), Bash(mkdir:*), Bash(python3:*), Bash(./.venv/bin/*:*), Bash(dokumentenpruefer/.venv/bin/*:*), Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(git fetch:*), Bash(git checkout:*)
---

# Dokumentenprüfer (Web-App)

Du arbeitest an der Web-App unter `dokumentenpruefer/` im Repo h. Sie prüft Word- und PDF-Dokumente
gegen die Regelsätze Basisprüfung, DIN 82079-1 und CE und erzeugt Prüfbericht (intern) und
Fachbericht (Kunde) als PDF. Die alte Streamlit-App `app.py` im Repo-Stamm bleibt unberührt als Rückfall.

Lies zuerst `dokumentenpruefer/README.md` (Aufbau, Konfiguration, Befehle) und bei Fragen zu Ablage,
Entscheidungen oder offenen Punkten `references/ablage.md` in diesem Skill-Ordner.

## Was der Auftrag meint

| Auftrag | Ablauf unten |
|---|---|
| „starten", „läuft das?" | Starten |
| „testen", „prüfen ob alles geht", nach jeder Code-Änderung | Testen |
| „prüf das Dokument", eine Datei aus `inbox/` oder ein Pfad | Dokument prüfen |
| „ändere", „baue ein", Fehler beheben | Ändern |
| „wo liegt", „ablage", „Stand" | `references/ablage.md` lesen und knapp antworten |
| „übergabe", „ZIP für Falk" | Übergabe |

Regeln aus dem Projekt gelten immer: Deutsch, „du", keine Passwörter oder Einmal-Passwörter in Dateien,
Logs oder Commits, nie E-Mails senden, Originale in `inbox/` nicht verändern, technische und rechtliche
Entscheidungen bleiben bei Niklas.

## Umgebung

- Python-Umgebung: `dokumentenpruefer/.venv`. Fehlt sie: `python3 -m venv dokumentenpruefer/.venv`
  und `dokumentenpruefer/.venv/bin/pip install -r dokumentenpruefer/requirements.txt`.
- Alle Befehle aus dem Ordner `dokumentenpruefer/` heraus ausführen oder mit `cd dokumentenpruefer &&` davor.
- Datenordner `daten/` (SQLite, Berichte, Geheimnis) und `output/` sind nicht versioniert. Für Tests und
  Probeläufe nie den echten Datenordner nehmen, sondern `DP_DATEN` auf einen Temp-Ordner setzen.
- In der Claude-Desktop-VM gibt es keinen Browser und kein Apple Mail: der Mail-Entwurf kommt dann als Text zurück.

## Starten

1. `cd dokumentenpruefer && ./.venv/bin/python -m app.verwaltung liste` zeigt, ob Konten existieren.
   Ohne Konto: Niklas nach E-Mail-Adresse und Name fragen, dann `python -m app.verwaltung admin --email … --name …`.
   Das Einmal-Passwort erscheint einmal im Terminal. Es wird Niklas im Chat genannt und nirgends gespeichert.
2. Server: `./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8765` (auf dem Mac genügt Doppelklick
   auf `start.command`). Erreichbar unter http://localhost:8765.
3. Fehlen Regeldateien, meldet das Log beim Start „Regeldateien fehlen". Alle drei liegen in `regeln/`;
   fehlt eine, darauf hinweisen und nicht erfinden.

## Testen

Nach jeder Änderung, bevor etwas als fertig gilt:

```bash
cd dokumentenpruefer && ./.venv/bin/python -m pytest tests -q -p no:warnings
```

Alle Tests müssen grün sein (Stand 5. Oktober 2026: 73). Zusätzlich `./.venv/bin/python -m pyflakes app tests`,
wenn pyflakes installiert ist. Bei Änderungen an `app/static/` die Seite im Browser oder mit Playwright
durchklicken: Erstanmeldung, Prüfung, Einstellungen, Handy-Breite 390 px. Was nicht geprüft wurde, wird
im Ergebnis als ungeprüft genannt.

## Dokument prüfen

Ohne Browser, direkt aus dem Terminal, mit `app/cli.py`:

```bash
cd dokumentenpruefer && ./.venv/bin/python -m app.cli pruefen "../inbox/Datei.docx" --sprachen de,en --ausgabe ../output
```

- `--sprachen`: Basissprache zuerst, optional eine Zusatzsprache (de, en, uk, ru).
- `--regelsaetze`: Standard `basis,din,ce`.
- Ausgabe: Zusammenfassung (Score, Ampel, Funde, Aufwand, Fazit) im Terminal, PDFs nach `--ausgabe`
  mit Namen `JJJJ-MM-TT_Dokument_Pruefbericht_DE_v01.pdf`.
- Ergebnis im Chat als Kompakttabelle zeigen: Score, Ampel, Funde je Klasse, Aufwand, erzeugte Dateien.
  Der Fachbericht geht an Kunden; der Prüfbericht mit Gewichtung und Aufwand bleibt intern.
- Ein Protokollsatz (Datum, Datei, Score, Dateien) gehört nach `logs/`, wenn der Ordner im Projekt existiert.

Liefert das Einlesen leeren Text, ist das PDF vermutlich ein Scan ohne Textebene: melden statt raten.

## Ändern

1. `git status` und `git log --oneline -3` prüfen. Arbeit liegt auf dem Branch `claude/dokumentenpruefer-webapp`,
   bis Niklas den Merge nach `main` entscheidet.
2. Vor der Änderung in einem Satz sagen, was geändert wird. Prüflogik in `app/pruefer/pruefung.py` nur
   ändern, wenn Niklas es ausdrücklich will: sie ist 1:1 aus `app.py` übernommen, damit alte und neue
   Ergebnisse vergleichbar bleiben.
3. Orientierung: `app/main.py` (API), `app/auth.py` (Konten), `app/einstellungen.py`, `app/pruefer/berichte.py`
   (PDF), `app/pruefer/texte.py` (Berichtstexte in vier Sprachen), `app/static/` (Oberfläche, nur HTML, CSS, JS).
   Oberfläche hält sich an das FSH-Design: dunkel führend, Gold `#dda440` als einziger Akzent, IBM Plex Sans
   lokal, Rundungen 2/4/8 px, keine Schatten, keine Pillen. Umbruchpunkte 1024 px und 640 px.
4. Testen (oben). Dann Commit auf dem Branch mit deutscher Betreffzeile und Push. Keine Modellnamen in
   Commits, keine Zugangsdaten.

## Übergabe

ZIP ohne Datenbank, Umgebung und Ausgaben:

```bash
zip -r output/JJJJ-MM-TT_Dokumentenpruefer_Freigabe_v01.zip dokumentenpruefer \
  -x "dokumentenpruefer/.venv/*" "dokumentenpruefer/daten/*" "dokumentenpruefer/output/*" "*/__pycache__/*" "*.pyc" "*/.pytest_cache/*"
```

Vorher: Tests grün, README aktuell, `git status` sauber. Nachher: Ablageort und Prüfsumme (`shasum -a 256`)
nennen. Die Übergabe an Falk folgt dem Plan (Phase 5) in `references/ablage.md`.
