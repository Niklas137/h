# Dokumentenprüfer auf dem Mac: Schritt für Schritt im Terminal

Stand: 2. Oktober 2026, Phase-1-Prüfstand 1.1.0. Jeder Schritt hat eine Kontrolle.
Bei einer abweichenden Ausgabe stoppen und die Fehlermeldung weitergeben.

## 1. Terminal öffnen

Spotlight (⌘ + Leertaste), „Terminal" tippen, Enter.

## 2. In den Ordner h wechseln

`cd ` tippen (mit Leerzeichen), dann den Ordner h aus dem Finder ins Terminal-Fenster ziehen, Enter.

Kontrolle: `ls` zeigt unter anderem `CLAUDE.md`, `app.py`, `dokumentenpruefer`.

Falls h noch nicht auf dem Mac liegt: in den gewünschten Oberordner wechseln und
`git clone https://github.com/Niklas137/h.git`, dann `cd h`.

## 3. Separaten Prüfstand holen

```bash
git fetch origin
git worktree add --detach ../h-phase1 origin/codex/dokumentenpruefer
cd ../h-phase1
```

Damit entsteht eine eigene Arbeitskopie. Die bisherige Installation, ihr Datenordner und Claudes
Branch werden nicht verändert. `git log -1 --oneline` zeigt den geprüften Codex-Stand.
Existiert `h-phase1` bereits, nicht löschen oder überschreiben; einen neuen Ordnernamen verwenden.

## 4. Python-Umgebung anlegen (einmalig, 1 bis 3 Minuten)

```bash
cd dokumentenpruefer
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

Benötigt wird Python ab 3.10; die Abnahme läuft mit Python 3.12.
Kontrolle: `./.venv/bin/python -m pytest tests -q -p no:warnings` meldet ausschließlich bestandene Tests.

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

Beenden: im Terminal Ctrl + C. Mit eingerichtetem Konto reicht später ein Doppelklick auf
`start.command` im Finder. Neue Erstanmeldungen benötigen SMTP; für lokale Tests kann erneut
`DP_DEV=1` verwendet werden. Codes werden nicht mehr in `codes.log` gespeichert.
Lässt macOS den Doppelklick nicht zu: Rechtsklick,
„Öffnen", bestätigen.

## 7. Entwicklung getrennt halten

Claude arbeitet auf `claude/dokumentenpruefer-webapp` in seiner bisherigen Arbeitskopie.
Codex arbeitet auf `codex/dokumentenpruefer` in einer separaten Kopie. Diese Anleitung legt
zusätzlich einen isolierten Prüfstand an. Änderungen werden erst nach Vergleich zusammengeführt.

Eine Prüfung des Teststands verändert keine Ergebnisse der bisherigen Installation. Eigene,
neuere Regelkataloge vor einem Wechsel sichern und vergleichen.

## 8. Wenn etwas hakt

- `python3: command not found`: Python 3 von python.org installieren, Terminal neu öffnen, ab Schritt 4.
- Port belegt: Die Startprüfung öffnet eine bereits laufende eigene Instanz. Bei einer anderen Installation diese im zugehörigen Terminal mit Ctrl + C beenden oder den Prüfstand mit `DP_DEV=1 ./start.command --port 8766` auf einem anderen Port starten.
- Nur DIN-Funde, keine Basis- und CE-Funde: `ls regeln` muss drei JSON-Dateien zeigen.
- Code fehlt: Bei eingerichtetem SMTP im E-Mail-Postfach nachsehen; beim lokalen Test mit `DP_DEV=1` steht er direkt in der Oberfläche. Ohne beides zeigt die App eine klare Fehlermeldung.

## 9. Sicherung und Wiederherstellung

Im Programmordner:

```bash
./.venv/bin/python -m app.sicherung sichern --ziel "$HOME/Documents/Dokumentenpruefer-Sicherungen/phase1.zip"
./.venv/bin/python -m app.sicherung pruefen "$HOME/Documents/Dokumentenpruefer-Sicherungen/phase1.zip"
./.venv/bin/python -m app.sicherung wiederherstellen "$HOME/Documents/Dokumentenpruefer-Sicherungen/phase1.zip" --ziel "$HOME/Documents/Dokumentenpruefer-Wiederhergestellt"
```

Für jede weitere Sicherung einen neuen Dateinamen wählen. Der Wiederherstellungsordner darf noch
nicht existieren. Danach den Server beenden und den ausgegebenen Startbefehl verwenden.
Die Sicherung enthält Konten, Einstellungen, Ergebnisse, PDFs und Regeln. Originaldokumente und
SMTP-Konfiguration separat sichern. Alte Sitzungen werden bei der Wiederherstellung beendet.

## 10. Abschließender Mac-Durchlauf

1. Mit einem Testkonto anmelden und eine Word-Datei mit Tabelle prüfen.
2. Eine zusätzliche Berichtssprache wählen; beide Berichtstypen und ZIP öffnen.
3. Zweimal ablegen. Vorhandene Berichte dürfen nicht überschrieben werden.
4. Ein gemischtes PDF prüfen und den Hinweis auf nicht lesbare Seiten kontrollieren.
5. Hilfe und Einstellungen öffnen, Helligkeit und Textgröße speichern, Seite neu laden.
6. Server mit Ctrl + C beenden und neu starten. Anmeldung, Historie und Berichte kontrollieren.
7. Sicherung erstellen und in einen neuen Ordner wiederherstellen. Dort anmelden und Berichte öffnen.
8. Auf dem Mac die Übergabe eines Fachberichts an Apple Mail als Entwurf prüfen. Nichts versenden.
9. Abschließend `start.command` per Finder starten und einen Doppelstart prüfen.

Dies ist die lokale Bedienabnahme. Ein automatischer Test ersetzt weder die Kontrolle von
Finder/Apple Mail noch die fachliche Freigabe des konkreten Kundendokuments.
