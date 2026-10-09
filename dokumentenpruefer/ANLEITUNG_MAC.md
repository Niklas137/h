# Dokumentenprüfer auf dem Mac: Schritt für Schritt im Terminal

Stand: 1. Oktober 2026. Jeder Schritt hat eine Kontrolle. Stimmt die Kontrolle nicht, an der Stelle
stoppen und die Ausgabe an Claude geben.

## 1. Terminal öffnen

Spotlight (⌘ + Leertaste), „Terminal" tippen, Enter.

## 2. In den Ordner h wechseln

`cd ` tippen (mit Leerzeichen), dann den Ordner h aus dem Finder ins Terminal-Fenster ziehen, Enter.

Kontrolle: `ls` zeigt unter anderem `CLAUDE.md`, `app.py`, `dokumentenpruefer`.

Falls h noch nicht auf dem Mac liegt: in den gewünschten Oberordner wechseln und
`git clone https://github.com/Niklas137/h.git`, dann `cd h`.

## 3. Branch holen

```bash
git fetch origin
git checkout claude/dokumentenpruefer-webapp
```

Kontrolle: `git branch --show-current` gibt `claude/dokumentenpruefer-webapp` aus.
Meldet Git lokale Änderungen, die den Wechsel blockieren: `git status` ausführen und die Ausgabe an Claude geben, nichts verwerfen.

## 4. Python-Umgebung anlegen (einmalig, 1 bis 3 Minuten)

```bash
cd dokumentenpruefer
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

Kontrolle: `./.venv/bin/python -m pytest tests -q -p no:warnings` endet mit `23 passed`.

Fragt macOS nach den „Command Line Tools", mit „Installieren" bestätigen und Schritt 4 danach wiederholen.

## 5. Ein Dokument ohne Browser prüfen

```bash
./.venv/bin/python -m app.cli pruefen "PFAD" --sprachen de,en --ausgabe output
```

Für PFAD die Word- oder PDF-Datei aus dem Finder ins Terminal ziehen (die Anführungszeichen davor
und danach stehen lassen). `--sprachen` nimmt die Basissprache und höchstens eine Zusatzsprache
(de, en, uk, ru).

Kontrolle: Im Terminal stehen Score, Ampel, Funde und Fazit. Im Ordner `dokumentenpruefer/output`
liegen vier PDFs: Prüfbericht und Fachbericht je Sprache.

## 6. Web-App starten

Beim ersten Mal im Terminal (im Ordner `dokumentenpruefer`):

```bash
DP_DEV=1 ./start.command
```

Das Skript fragt E-Mail-Adresse und Name für das Admin-Konto, zeigt einmal das Einmal-Passwort an
und öffnet den Browser unter http://localhost:8765. `DP_DEV=1` sorgt dafür, dass der Code für die
Erstanmeldung direkt auf der Seite steht, solange kein E-Mail-Versand eingerichtet ist.

Im Browser: „Erstanmeldung mit Einmal-Passwort", E-Mail-Adresse und Einmal-Passwort eingeben, Code
übernehmen, Name und eigenes Passwort setzen (mindestens 14 Zeichen, ein Großbuchstabe, ein Sonderzeichen).

Beenden: im Terminal Ctrl + C. Später reicht ein Doppelklick auf `start.command` im Finder, dann ohne
`DP_DEV`; der Code steht dann in `daten/codes.log`. Lässt macOS den Doppelklick nicht zu: Rechtsklick,
„Öffnen", bestätigen.

## 7. Claude Code im Ordner h nutzen

Im Terminal in den Ordner h wechseln (eine Ebene über `dokumentenpruefer`) und Claude Code starten:

```bash
cd ..
claude
```

Dann im Chat zum Beispiel `Prüftool prüfen PFAD en` eingeben (Pfad wie in Schritt 5 per Ziehen aus
dem Finder). Claude nutzt den Skill aus `.claude/skills/dokumentenpruefer`, prüft die Datei und legt
die PDFs in `dokumentenpruefer/output` ab. Weitere Aufträge: `Prüftool starten`, `Prüftool testen`,
`Prüftool ablage`.

## 8. Wenn etwas hakt

- `python3: command not found`: Python 3 von python.org installieren, Terminal neu öffnen, ab Schritt 4.
- `Address already in use` beim Start: läuft schon eine Instanz, im anderen Fenster mit Ctrl + C beenden.
- Nur DIN-Funde, keine Basis- und CE-Funde: `ls regeln` muss drei JSON-Dateien zeigen.
- Code für die Erstanmeldung nicht gefunden: `tail -1 daten/codes.log` im Ordner `dokumentenpruefer`.
