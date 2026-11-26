# Auftrag für Claude Code: Floorball Match weiterentwickeln

## Ausgangslage
- `floorball-match.html` ist das komplette Spiel in einer Datei (Three.js 0.160 über CDN, kein Build nötig).
- Der neue Teil steht unter dem Kommentar `MODUL: MATCH` (Objekt `Match`, Klasse `MSpieler`) und `MODUL: PAD-MENÜ` (Objekt `PadMenue`).
- Der Rest (Arena `Halle`, Figuren `Figur`, Animation `AnimMaschine`, Ton `Ton`, Teams `TeamDB`, Penalty-Modus `Spiel`) stammt aus „Floorball Penalty Showdown“ und soll weiter funktionieren.
- Ziel ist das Referenzvideo: Floorball-Spiel mit TV-Kamera von der Seite, blauem Boden, 5 gegen 5, voll mit Controller spielbar.

## Regeln für die Arbeit
1. Lies zuerst `MODUL: MATCH` komplett, bevor du etwas änderst.
2. Arbeite auf einem eigenen Branch, eine Aufgabe pro Commit.
3. Starte nach jeder Änderung einen lokalen Server (`python3 -m http.server`) und prüfe im Browser: Spiel startet, ein Tor fällt, Zeitlupe läuft, Konsole ohne Fehler.
4. Der Penalty-Modus darf nicht kaputtgehen.
5. Schreibe am Ende einen kurzen Prüfbericht: was geändert, was getestet, was offen.

## Aufgaben in dieser Reihenfolge
1. **Spielgefühl mit echtem Controller**: Tempo, Schusshärte, Passgeschwindigkeit, Torhüterstärke prüfen und nachstellen (Werte in `M_STUFEN`, `spielerSchritt`, `aktionSchritt`, `torwartSchritt`).
2. **Leistung auf dem Handy**: Bildrate messen; falls nötig Figuren-Detail und Spiegelung im Match senken.
3. **Seitenwechsel** nach jedem Drittel.
4. **Schiedsrichter** (zwei Figuren, orange) und **Spielerbänke** mit Auswechselspielern.
5. **Linienwechsel** (Taste/Knopf, zweite Reihe aus dem Teamkader).
6. **Strafen**: Stockschlag und Foul erkennen, 2 Minuten, Überzahl, Strafbank-Anzeige.
7. **Freischlag mit Abstand** statt des einfachen Einschlags (`ausball`).
8. **Zweiter Spieler** am zweiten Controller (Team B steuerbar).
9. **Animationen**: Ballannahme, Zweikampf, Gruppenjubel, Torhüter-Auswurf.
10. Optional: Datei in Module aufteilen (`match.js`, `eingabe.js`, …) mit Vite, wenn die eine Datei zu unhandlich wird.

## Steuerung (Ist-Stand, nicht ändern ohne Rückfrage)
Linker Stick laufen · RT Sprint · A Pass / Abwehr Spielerwechsel / Bully · X oder RB Schuss (halten) / Abwehr Stockcheck · Y hoher Pass · B Finte · rechter Stick hoch = hoch zielen · Select Kamera · Start Pause
