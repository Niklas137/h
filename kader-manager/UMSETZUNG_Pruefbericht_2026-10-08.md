# Umsetzung der Befunde aus dem Prüfbericht vom 08.10.2026

Bezug: KFK_Trikotanimation_Pruefbericht_2026-10-08.docx und KFK_Trikotanimation_Verbesserungsvorschlaege_2026-10-08.docx.
Stand des Moduls: kader-manager.zip vom 08.10.2026 (nach der Prüfung). Quelldateien: kader.js, kader.css, kader-daten.js, index.html, admin.js, fotos/.

| ID | Prio | Status | Umsetzung | Nachweis |
|---|---|---|---|---|
| A01 | P1 | behoben | Zustandsautomat `geschlossen → oeffnend → offen → schliessend` in kader.js. Jede Aktion erhöht eine Vorgangskennung; Timer und Animationsframes prüfen sie und verfallen sonst (`spaeter()`, `naechsterFrame()`). Filterwechsel ruft `sofortSchliessen()`. `wechseln()` und `haengerVon()` sind gegen null abgesichert. Kartenpfeile während des Schließens öffnen sauber neu. | Browsertest 08c: Esc + 50 ms + Öffnen B, Wechsel + Esc + Öffnen C, sieben Folgen mit 0/20/50/100/140/220/740 ms: Endzustand stets sauber (ein gewähltes Trikot, Karte und Kamera konsistent, kein Hash-Rest). |
| A02 | P1 | behoben | Abdunklung ist jetzt ein Pseudoelement innerhalb der Stange (`.stange-innen::after`) ohne Klickfläche; das gewählte Trikot liegt darüber (z-index). Klick auf freie Fläche schließt über einen Handler auf der Stange, Klick auf Nachbarn wechselt. | Test 08c: Nachbarklick bei offener Karte wechselt zu Dmytro Bondar; Klick auf die Wand schließt. |
| A03 | P1 | behoben | `trikotKonfigPruefen()` in kader-daten.js: Positionen und Größen nur als endliche Zahlen in festen Grenzen, Farben nur als Hex, Bildpfad nur `[\w./-]` ohne `..`. SVG-IDs werden auf `[a-z0-9-]` gefiltert. Die Filterdefinition steht nicht mehr im erzeugten Markup. | Node-Prüfung: `numberY` mit eingeschleustem `onpointerenter` wird auf den Standardwert gesetzt, kein `onpointer` im SVG. |
| A04 | P2 | behoben | Innenabstand der Stange links und rechts = halbe Szenenbreite minus halbe Trikotbreite; Start rollt das erste Trikot mittig; Größenänderung zentriert neu. | Test 08c: Abstand des ersten Trikots zur Mitte 0 px bei 1180 px Szenenbreite. |
| A05 | P2 | behoben | `ausHashOeffnen()` decodiert in try/catch, nutzt denselben Weg wie die Bedienung (`oeffnen`/`wechseln`), unbekannte oder weggefilterte IDs ändern nichts, leerer Hash schließt. | Test 08c: Hashwechsel → genau ein gewähltes Trikot; `#spieler=%` und unbekannte ID ohne Ausnahme und ohne Änderung. |
| A06 | P2 | behoben | `pruefen()` führt `spielerFehler()` für jeden Datensatz aus und erzwingt eindeutige, gültige IDs; bei Fehlern wird mit Datensatzbezug abgewiesen. Lokaler Speicher mit ungültigen Daten fällt auf die Datei zurück; der Admin-Import ersetzt den Kader nur nach bestandener Prüfung; Speichern meldet Fehler statt zu schreiben. | Node-Prüfung: doppelte ID und ungültiger Spieler (leerer Name, Nummer 120, negative Tore) werden abgewiesen. |
| A07 | P2 | behoben | Stangenpfeile sind bei offener Karte `disabled` und `aria-hidden`, zusätzlich `visibility:hidden`. Pfeiltasten wechseln bei offener Karte die Karte, bei geschlossener die Stange. Tastaturhandler nur aktiv, wenn der Fokus im Modul oder auf der Seite liegt. | Test 08c: beide Pfeile deaktiviert bei offener Karte; Pfeiltaste wechselt Karte und Leiste gemeinsam. |
| A08 | P2 | verbessert, Rest offen | Aufdruckfläche neu retuschiert: zeilenweiser Grundton aus beiden Seiten, Stoffstruktur aus einem sauberen Streifen daneben, weiche Kante (3,5 px). Weiß ist sauber; beim schwarzen Trikot bleibt bei starker Aufhellung eine etwas glattere Fläche. Empfehlung: saubere Rückansicht ohne Aufdruck von der Druckerei oder dem Designer (Vorlage ARTY) anfordern. | Sichtprüfung der Kontrollbilder bei 100 % und 2,2-facher Aufhellung. |
| A09 | P3 | behoben | Ein Filter `#kader-druck-stoff` einmal in index.html, CSS verweist darauf. | Test 08c: eine Filterdefinition, keine doppelten SVG-IDs. |

## Ergänzende Verbesserungen aus der Arbeitsliste

- Bildausfall: Das Trikotbild wird beim Start probegeladen; schlägt es fehl, wird das gezeichnete Trikot verwendet (Warnung in der Konsole).
- Ladehinweis „Kader wird geladen …“ und `<noscript>`-Hinweis.
- Touch: `touch-action: pan-x pan-y` auf der Stange; eigenes Ziehen nur für die Maus, Finger wischen nativ, vertikales Seitenscrollen bleibt.
- Tastaturhandler begrenzt (siehe A07).

## Zusätzlich umgesetzt (Empfehlungen vom 08.10.2026)

- Ukrainische Oberfläche (`sprache.js`, `team.language`), Heim-/Auswärtstrikot-Umschalter, „Link kopieren“ in der Karte.
- `server.py` mit tokengeschütztem Veröffentlichen und Sicherungskopien; Admin-Seite erkennt den Server automatisch.
- Browsertests dafür: Sprache, Trikotwechsel, Zwischenablage, Veröffentlichen mit richtigem und falschem Token.

## Offene Nachweise (R1–R4)

Nicht durch mich erbracht: Safari auf iPhone und Mac, Chrome auf Android, Firefox, echte Touch-Gesten, Bildrate auf schwachen Geräten, Einbau in die Zielseite, Zugriffsschutz des Admin-Bereichs, Übersetzung ins Ukrainische. Alle Browsertests liefen in Chromium (Playwright) bei 1280, 1024 und 390 px Breite, mit und ohne reduzierte Bewegung.
