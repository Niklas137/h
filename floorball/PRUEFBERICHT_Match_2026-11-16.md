# Prüfbericht Floorball Match – 2026-11-16

Auftrag: `CLAUDE-CODE-AUFTRAG.md`. Branch `claude/player-jersey-animation-cn15wc`, eine Aufgabe je Commit.
Geändert wurde nur `floorball-match.html` (Module MATCH und PAD-MENÜ, dazu kleine Ergänzungen in FIGUREN und BILD).
Prüfskripte liegen in `pruefung/` (Anleitung dort).

## Was geändert wurde

| Nr. | Aufgabe | Ergebnis |
| --- | --- | --- |
| 1 | Spielgefühl | Werte zentral in `M_GEFUEHL` und `M_STUFEN`: runde Stick-Totzone mit Kennlinie, schnellere Wende, Schuss 70–113 km/h, Ladezeit 0,6 s, Pass nach Distanz. |
| 2 | Leistung Handy | Grafikprofil „sparsam“ (automatisch auf Handy/niedriger Qualität): Figuren mit weniger Dreiecken, ohne Schattenwurf, ohne Bodenspiegel. Menüpunkt „Grafik“. |
| 3 | Seitenwechsel | Nach jedem Drittel und vor der Verlängerung; Torzuordnung, Aufstellung, Kamera und Zeitlupe richten sich nach der Seite. |
| 4 | Schiedsrichter, Bänke | Zwei Schiedsrichter in Orange laufen an den Längsseiten mit, pfeifen und zeigen. Bänke mit je fünf Ersatzspielern gegenüber der TV-Kamera. |
| 5 | Linienwechsel | Steuerkreuz ↑ oder Taste L (oder automatisch, Menü). KI-Team wechselt selbst. Frische sinkt auf dem Feld, müde Linie bis 12 % langsamer. |
| 6 | Strafen | Stockschlag, Halten, Stoßen. Freischlag, bei schweren oder wiederholten Fouls 2 Minuten mit Strafbank und Überzahl, Überzahltor beendet die Strafe. Anzeige unter der Tafel. |
| 7 | Freischlag | Statt Einschlag: Ball ruht, Gegner 3 m weg (Kreis), nur schlagen, Uhr steht, nicht direkt am Torraum. |
| 8 | Zweiter Spieler | Menü „Gegner steuert: 2. Controller“. Gleiche Belegung, roter Ring, KI übernimmt beim Trennen. |
| 9 | Animationen | Ballannahme, Zweikampf-Kontakt, Gruppenjubel im Kreis, Torhüter-Auswurf mit Ausholen. |
| 10 | Module mit Vite | Nicht umgesetzt, Entscheidung Niklas 2026-11-26 (siehe unten). |

**Steuerung:** Die bestehende Belegung ist unverändert. Neu belegt wurden nur bisher freie Eingaben: Steuerkreuz ↑ / Taste L für den Linienwechsel und der zweite Controller. **Bitte bestätigen.**

## Was getestet wurde

Kopfloses Chromium mit emulierten Controllern (Gamepad-API), Simulation ohne Grafiklast, Fotos mit echtem Rendering.

- **Regel 3 nach jeder Aufgabe** (`basis.mjs`): Spiel startet, Tor fällt, Zeitlupe läuft, Konsole ohne Fehler, Penalty-Modus läuft durch. Letzter Lauf: 7 von 7 OK.
- **Funktionstests je Aufgabe**, letzter Gesamtlauf:

  | Skript | OK |
  | --- | --- |
  | seite | 11/11 |
  | neben | 5/5 |
  | linie | 10/10 |
  | strafe | 11/11 |
  | frei | 12/12 |
  | zwei | 12/12 |
  | anim | 10/10 |

  Einzelne Abläufe enthalten Zufall (Schussgenauigkeit, KI); das Testtor wird daher bis zu viermal versucht.
- **Messwerte**:

  | Messung | Ausgangsstand | Jetzt |
  | --- | --- | --- |
  | Laufen / Sprint | 21 / 26 km/h | 21,9 / 27,6 km/h |
  | Mit Ball / Sprint | 19 / 24 km/h | 20–21,8 / 25,1 km/h |
  | 180°-Wende | 0,58 s | 0,52 s |
  | Schuss | 64–96 km/h | 70–113 km/h |
  | Ladezeit | 0,75 s | 0,6 s |
  | Pass 5/10/15 m | 11,7 / 15,9 / 17,9 m/s | 11 / 15,2 / 18,4 m/s |

  KI-Torhüter (Stufe mittel, 150 Schüsse aus dem Slot): hält 73 %. Der eigene Torhüter hält 82 %.
- **Leistung**, CPU 4-fach gedrosselt als Näherung für ein Mittelklasse-Handy:

  | | Rechenzeit je Bild (Median / 95 %) | Zeichenaufrufe | Dreiecke |
  | --- | --- | --- | --- |
  | Desktop | 4,7 / 8,4 ms | 806 | 1,47 Mio. |
  | Handy (sparsam) | 4,7 / 7,9 ms | 404 | 0,53 Mio. |

  Vor den Schiedsrichtern und Bänken: Handy 237 Aufrufe, Desktop 581.

## Was offen ist

1. **Echter Controller und echtes Handy:** Gefühl und Bildrate konnten hier nur gemessen, nicht gespielt werden. Bitte am Gerät prüfen; Stellschrauben in `M_GEFUEHL` und `M_STUFEN`.
2. **Zeichenlast Handy:** Schiedsrichter und zehn Bankspieler kosten auf dem Handy rund 170 Zeichenaufrufe. Ist das Handy zu langsam, kann man die Bankspieler im Sparprofil ausblenden.
3. **Regelvereinfachungen:**
   - Nur 2-Minuten-Strafen, keine Vorteilsregel.
   - Der Torraum-Abstand beim Freischlag ist als 5,5 m zur Tormitte angenähert.
   - Die Strafzeit ist auf die Drittellänge umgerechnet (10 %, bei 3-Minuten-Dritteln 18 s).
   - Beide Teams sitzen auf der Bank ihrer Abwehrseite und tauschen mit dem Seitenwechsel.
4. **Ersatzspieler:** Ohne Feld `reserve` in den Teamdaten werden sie fest aus der Team-Kennung erzeugt. Im Team-Editor sind sie nicht bearbeitbar.
5. **Zweiter Spieler:** Name und Ausdauer zeigt die Anzeige nur für Spieler 1. Spieler 2 braucht einen Controller, Tastatur geht nicht.
6. **Vite (Aufgabe 10):** Empfehlung: vorerst nicht aufteilen. Die Datei hat 5 810 Zeilen und 479 KB und läuft ohne Build. Vite brächte npm und einen Build-Schritt dazu. Wird sie zu unhandlich, ist der kleinere Schritt eine Aufteilung in native ES-Module ohne Bundler. **Entschieden (Niklas, 2026-11-26): nicht umsetzen, eine Datei ohne Build bleibt.**
