# Prüfskripte Floorball Match

Automatische Prüfungen für `../floorball-match.html` in einem kopflosen Chromium mit emulierten Controllern.
Die Simulation läuft im Prüfmodus ohne Grafiklast (`Bild.ohneRender`); für Fotos wird kurz echt gezeichnet.

## Start

```bash
cd floorball && python3 -m http.server 8790        # Spielseite bereitstellen (eigenes Terminal)
cd floorball/pruefung
npm install playwright-core                          # einmalig, oder PW_MODUL auf eine vorhandene Installation setzen
CHROMIUM=/pfad/zu/chrome node basis.mjs shots        # Ordner shots/ vorher anlegen
```

Umgebungsvariablen: `PW_MODUL` (Pfad zu playwright-core, Standard `playwright-core`), `CHROMIUM` (Browserdatei,
Standard: der zu Playwright passende Browser), `FB_URL` (Standard `http://localhost:8790/floorball-match.html`).

## Skripte

| Skript | Prüft |
| --- | --- |
| `basis.mjs` | Regel 3 des Auftrags: Spiel startet, Tor fällt, Zeitlupe läuft, Konsole ohne Fehler, Penalty-Modus läuft |
| `seite.mjs` | Aufgabe 3: Seitenwechsel nach jedem Drittel, Torzuordnung in jedem Drittel |
| `neben.mjs` | Aufgabe 4: Schiedsrichter, Bänke, Jubel der Bank |
| `linie.mjs` | Aufgabe 5: Linienwechsel per Knopf, Taste, Automatik, beim Bully |
| `strafe.mjs` | Aufgabe 6: 2 Minuten, Strafbank, Überzahl, Überzahltor, Fouls |
| `frei.mjs` | Aufgabe 7: Freischlag mit 3 m Abstand, Uhr, Einschlag, Lage am Tor |
| `zwei.mjs` | Aufgabe 8: zweiter Controller steuert Team B |
| `anim.mjs` | Aufgabe 9: Ballannahme, Zweikampf, Gruppenjubel, Torhüter-Auswurf (mit Nahaufnahmen) |
| `mess.mjs` | Aufgabe 1: Messwerte Spielgefühl (Tempo, Schuss, Pass, Torhüterquote je Stufe) |
| `sprint.mjs` | Laufwerte und 180°-Wende unter sauberen Bedingungen (ohne Freischlag/Fouls); maßgeblich für Tempo |
| `cpu.mjs`, `last.mjs` | Aufgabe 2: Rechenzeit je Bild bei gedrosselter CPU, Zeichenaufrufe und Dreiecke (`mobil` als Argument) |

Hinweis: Einzelne Abläufe enthalten Zufall (Schussgenauigkeit, KI). `erzwingeTor` versucht deshalb bis zu viermal.
Echte Bildraten auf Handys lassen sich hier nicht messen; dafür auf dem Gerät prüfen.
