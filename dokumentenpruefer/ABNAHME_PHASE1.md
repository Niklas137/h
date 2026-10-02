# Phase 1: Umsetzung und Abnahme

Stand: 1. Oktober 2026, 23:07 UTC. Version 1.1.0.

**Die technische Abnahme des hier beschriebenen lokalen Funktionsumfangs ist bestanden.**
Die Installation auf Niklas' Mac und die dortige Bedienabnahme wurden durch diesen Lauf nicht
ausgeführt. Eine vollständige Freigabe für Kundenbetrieb ist damit noch nicht erklärt.

Geprüfter Programmstand: `e33a2ccc50ed5236e4c9c6f7ad351424b2fa96ba` auf
`codex/dokumentenpruefer`, aufgebaut auf Claudes Stand `2cffdb957466d26988f8aee5cb2e72c08f73fc86`.
Der Claude-Branch und die ursprüngliche Streamlit-App wurden nicht verändert.

## Nachweis

[Bestandener GitHub-Actions-Lauf für Linux und macOS](https://github.com/Niklas137/h/actions/runs/36938876460)

| Umgebung | Python-Tests | Browser | Ergebnis |
|---|---:|---|---|
| Lokale Entwicklungsumgebung, Python 3.12 | 83 | Browserzugriff auf den lokalen Dienst hier blockiert | Python-Abnahme bestanden |
| GitHub Actions, Ubuntu, Python 3.12.14 | 83, 10,44 Sekunden | Chromium, Playwright 1.62.1; 7 Ablaufgruppen | Bestanden |
| GitHub Actions, macOS, Python 3.12.14 | 83, 42,98 Sekunden | Chromium, Playwright 1.62.1; 7 Ablaufgruppen | Bestanden |

Die Browserprotokolle melden auf beiden Systemen `javascriptErrors: []`. Screenshots und
`browser-ergebnis.json` liegen in den zwei Prüfartefakten dieses Laufs. Es wurden ausschließlich
erzeugte Testkonten und Testdokumente verwendet, keine echten Konten geändert und keine E-Mails versendet.

Der erste Browserlauf fand einen überbreiten Header bei 844 Pixeln und großer Schrift.
Die Kopfleiste wurde korrigiert; der zweite vollständige Lauf bestand auf beiden Systemen.
Die Syntax von Python, JavaScript und Startskript sowie die Änderungen auf Leerraumfehler wurden
kontrolliert. `pyflakes` war in der lokalen Umgebung nicht installiert; dafür wird kein Ergebnis behauptet.

## Abgenommene Abläufe

| Bereich | Gegenprobe |
|---|---|
| Konto | Erstanmeldung mit Einmal-Passwort, Code und eigenem Passwort; Anmeldung, Sperre, Passwortregeln, Sitzungen und Rollen in den automatischen Tests |
| Benutzerverwaltung | Admin legt zusätzliches Mitglied an; Mitglied erhält keinen Zugriff auf Verwaltung oder fremde Prüfung |
| Dokumentprüfung | Word, Absätze, Tabellen, verschachtelte und verbundene Zellen; PDF mit Text sowie mit einzelnen nicht lesbaren Seiten |
| Fehlerfälle | Defekte Datei, leere/ungültige Regelkataloge, ungültige Auswahl und Zusatzsprache, PDF-Erzeugungsfehler; anschließend erneute Prüfung möglich |
| Berichte | Interner Prüfbericht und Kunden-Fachbericht; Basissprache plus Zusatzsprache; PDF-Download und ZIP |
| Sprachen | Berichte in de/en/uk/ru; Empfehlungen und Bereiche der Basis- und CE-Regeln übersetzt; bestehende DIN-Übersetzungen erhalten |
| Ablage | Vorhandene PDFs werden nicht überschrieben; parallele Ablage erhält unterschiedliche Inhalte; identischer Inhalt wird wiederverwendet |
| Bedienung | Hilfe, Einstellungen, Helligkeit und große Schrift; Einstellungen nach Neuladen erhalten; Ansichten bei 320/390 Pixeln und 844 Pixeln im Querformat |
| Laufende Prüfung | Kopfleiste bedienbar; beim Abmelden werden laufender Transport und alte Anzeige verworfen; verspätete Antwort gelangt nicht zum nächsten Benutzer |
| Start und Neustart | Echter HTTP-Server, Doppelstart ohne zweite Instanz, geordnetes Beenden und erneuter Start; bestehende Berichte bytegleich erhalten |
| Wiederherstellung | Online-Sicherung der SQLite-Datenbank einschließlich Berichten und Regeln; Prüfsummen, beschädigte Archive und unzulässige Pfade; Wiederherstellung in neuen Ordner; Anmeldung und PDF/ZIP danach funktionieren |
| Verifizierung | Fehlender oder fehlerhafter SMTP-Versand wird verständlich gemeldet; Codes werden nicht in Logdateien geschrieben |

Zusätzlich wurden acht Muster-PDFs erzeugt: beide Berichtstypen in allen vier Sprachen. Ausgewählte
Seiten der deutschen, ukrainischen und russischen Berichte wurden gerendert und visuell geprüft.
Fundstellen stehen im internen Bericht, Überschriften bleiben beim Inhalt und Seitenzahlen zeigen
die Gesamtzahl. Das ist eine Layoutkontrolle mit Testmaterial, keine fachliche Prüfung von Kundenunterlagen.

## Wesentliche Änderungen

- Ein Ergebnis gelangt erst in die Historie, wenn alle zugehörigen PDFs vollständig erstellt sind.
  Bei einem Erzeugungsfehler wird der angelegte Berichtsordner wieder entfernt.
- PDF-Dateien werden vollständig und ohne Überschreiben veröffentlicht. Die Ablage benötigt ein
  Dateisystem mit Hardlink-Unterstützung, beispielsweise APFS.
- Der Start erkennt eine bereits laufende eigene Installation und öffnet sie. Bei einem anderen
  belegten Port erscheint eine verständliche Meldung; fremde Prozesse werden nicht beendet.
- Eine geprüfte ZIP-Sicherung und Wiederherstellung sind über `python -m app.sicherung` verfügbar.
  Die Wiederherstellung beendet alte Sitzungen und benötigt ein neues Zielverzeichnis.
- Vor der Anmeldung sind die vorhandenen rechtlichen Informationen erreichbar. Die Inhalte
  enthalten weiterhin die unten genannten Platzhalter.

Die beschlossene Variante C bleibt erhalten: Score, Ampel, Fazit und fachliche Prüflogik bleiben
wie vereinbart. Jeder Bericht enthält den Satz zur automatischen Vorprüfung und fachlichen
Freigabe bei FSH. Die Oberfläche bleibt deutsch. MFA und der besondere Passwort-Anfrageprozess
sind Phase 2. Es wurde keine Jobschicht mit Abbruchfunktion eingeführt.

## Vor der endgültigen Freigabe noch erforderlich

1. **Auf dem tatsächlichen Mac übernehmen und prüfen:** separaten Prüfstand nach
   [ANLEITUNG_MAC.md](ANLEITUNG_MAC.md) starten; Finder-Doppelklick und Übergabe eines Entwurfs mit
   Anhang an Apple Mail kontrollieren. Die automatisierte macOS-Abnahme ersetzt diese beiden
   Desktop-Integrationen nicht. Geschätzte Bedienzeit: 15–30 Minuten, zuzüglich Installation.
2. **Installationsangaben ergänzen:** echtes Impressum und Datenschutztext, Support-Adresse,
   Telefonnummer/Zeiten sowie SMTP für echten Codeversand. Diese Inhalte und Zugangsdaten
   wurden nicht erfunden. `DP_DEV=1` ist nur für den lokalen Test vorgesehen.
3. **Lokale Regelkataloge vergleichen:** falls auf dem Mac neuere Basis- oder CE-Regeln vorhanden
   sind, diese vor dem Wechsel sichern und mit dem geprüften Stand vergleichen.
4. **Änderungen prüfen und zusammenführen:** Codex- und Claude-Branch bleiben bis zur Prüfung
   getrennt. Produktive Daten müssen vor einem Wechsel gesichert werden.

Die Prüfung bleibt eine automatische Schlüsselwort-Vorprüfung. Nicht lesbare Scan-Seiten werden
gekennzeichnet, aber nicht per OCR ausgewertet. Die fachliche Freigabe bleibt beim Menschen.
Diese Abnahme ist weder ein vollständiges Sicherheitsgutachten noch ein Nachweis aller denkbaren
Dateien, Browser oder Lastzustände.

## Wiederholen

Im Programmordner nach Installation der Abhängigkeiten:

```bash
./.venv/bin/python -m pytest tests -q
```

Die Browserabnahme steht in `tests/browser_smoke.cjs`. Der Workflow
`.github/workflows/dokumentenpruefer.yml` richtet Python, Node und Chromium auf Linux und macOS
ein und führt beide Testsuiten aus. Eine Änderung am Programm muss erneut geprüft werden;
dieses Protokoll bezieht sich auf den oben genannten Commit.
