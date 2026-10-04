# Dokumentenprüfer: Vorführung für Falk (fünf bis sechs Minuten)

Stand: 4. Oktober 2026. Ablauf für Niklas, live im Werkzeug auf dem Mac. Falk bekommt den
Handzettel (`HANDZETTEL_FALK.md`) dazu.

## Vorbereitung am Vortag

1. Auf dem Mac `git pull origin main` im Ordner `h`, dann im Ordner `dokumentenpruefer` einmal
   `./start.command` starten und wieder beenden. Kontrolle: Unter Einstellungen → Rechtliches stehen
   Impressum und Datenschutzerklärung, in der Seitenleiste gibt es „Mitarbeiter“.
2. Ein echtes, unkritisches Testdokument bereitlegen: eine Betriebsanleitung als Word mit Tabelle,
   zehn bis dreißig Seiten. Dazu ein PDF, von dem eine Seite ein Scan ist, falls vorhanden.
3. Eigene Berichte aus Probeläufen unter „Verlauf“ lassen, damit die Seite nicht leer ist.
4. Falks E-Mail-Adresse und den Namen für das Konto klären.
5. Helligkeit auf Hell stellen, wenn ihr bei Tageslicht am Tisch sitzt. Textgröße auf Groß, wenn
   ihr zu zweit auf einen Bildschirm schaut.
6. Apple Mail geöffnet, damit der Entwurf am Ende sofort erscheint.

## Ablauf

| Zeit | Schritt | Was du zeigst und sagst |
|---|---|---|
| 0:00 | Einstieg | „Das ist eine automatische Vorprüfung per Schlüsselwortsuche. Sie findet Lücken gegen Basisprüfung, DIN 82079-1 und CE und schreibt zwei Berichte. Die fachliche Freigabe bleibt bei dir.“ Seitenleiste kurz zeigen: Prüfen, Verlauf, Einstellungen, Mitarbeiter. |
| 0:30 | Prüfung starten | Word-Datei in das Feld ziehen. Drei Regelsätze sind vorgewählt. Zusätzliche Berichtssprache „English“ wählen. „Prüfung starten“. Das Statusfeld zeigt Lesen, Prüfen, Berichte. |
| 2:00 | Ergebnis | Pop-up oben: Score und Ampel. Dann die drei Schritte: ① Ergebnis mit Funden und Fazit, ② Prüfbericht (intern, mit Gewichtung und Aufwand) und Fachbericht (Kunde, ohne beides), je Sprache ein PDF, ③ Weitergabe. „Funde im Detail“ aufklappen, zwei Funde erklären. |
| 3:30 | Weitergabe | Einen Fachbericht als PDF öffnen, kurz blättern. „Alle PDFs als ZIP“. „Berichte im Ordner output ablegen“, zweimal: nichts wird überschrieben. „E-Mail-Entwurf an den Kunden“: Apple Mail öffnet den Entwurf mit Anhang. Nicht senden. |
| 4:30 | Falks Konto | Seitenleiste → Mitarbeiter → „+ Mitarbeiter“. Name, E-Mail, Rolle Admin. Das Einmal-Passwort erscheint einmal; Falk schreibt es sich auf oder du kopierst es ihm. Erstanmeldung macht er auf seinem Mac, Ablauf steht auf dem Handzettel. |
| 5:30 | Grenzen und Nächstes | „Was er nicht kann: Inhalte verstehen, Scans lesen, Freigaben erteilen. Nächste Schritte: deine Regeln aus der Praxis ergänzen, Übergabe als ZIP auf deinen Mac, Rechtstexte gegenlesen lassen.“ |

## Wenn Falk fragt

- **„Woher kommt der Score?“** Jeder Fund zieht seine Gewichtung ab. Grün ab 80 Prozent, Gelb ab 60,
  Rot darunter. Die Zahl sagt, wie viele Pflichtinhalte fehlen, nicht ob der Text gut ist.
- **„Kann ich die Regeln ändern?“** Ja, sie sind Dateien im Ordner `regeln`: Basisprüfung, DIN 82079-1,
  CE. Jede Regel hat Suchwörter, Fehlerklasse, Gewichtung und Empfehlung. Eine kaputte Datei stoppt
  die Prüfung mit Meldung, statt falsch zu prüfen.
- **„Wo liegen meine Daten?“** Nur auf dem Mac, auf dem die App läuft. Kein Server, keine Cloud,
  keine E-Mails außer dem Code bei der Erstanmeldung. Hochgeladene Dokumente werden nicht gespeichert,
  nur Ergebnis und Berichte.
- **„Was ist mit dem Kundenbericht?“** Der Fachbericht enthält Fazit, To-do-Liste und Maßnahmen, aber
  keine Gewichtung und keinen Aufwand. In jedem Bericht steht ein Satz, dass es eine Vorprüfung ist.
- **„Kann ich Mitarbeiter sperren?“** Ja, Deaktivieren beendet sofort alle Sitzungen. Löschen braucht
  die E-Mail-Adresse als Bestätigung und ist umkehrbar. Der letzte Admin ist geschützt.
- **„Was passiert bei einem Scan?“** Seiten ohne Textebene werden gemeldet, nicht geprüft. Ein PDF
  ganz ohne Text wird abgewiesen.

## Nicht zeigen

- Protokoll der Admin-Aktionen und Einstellungen → Sicherheit: funktioniert, lenkt aber ab.
- Entwicklungsmodus mit `DP_DEV=1` und Terminalbefehle. Für Falk gilt: Doppelklick auf
  `start.command`.

## Nach dem Treffen

- Falks Rückmeldungen in `references/ablage.md` unter „Heute geklärt“ eintragen.
- Entscheidung zur Website-Optik (PR #15) notieren.
