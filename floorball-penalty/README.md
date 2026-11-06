# Floorball Penalty Showdown

3D-Penaltyschießen im Floorball (Unihockey). Alles steckt in **einer Datei**: `index.html`.
Zum Starten die Datei doppelklicken. Three.js 0.160 wird einmalig vom CDN (jsdelivr) geladen, deshalb braucht der erste Start Internet.
Alle anderen Inhalte (Geometrie, Texturen, Ton) entstehen prozedural.

## Bedienung

**Schütze** (eine Eingabe: zeigen und halten)
- **Maus oder Finger zeigt auf die Stelle im Tor**, wo der Ball hin soll. Das gelbe Fadenkreuz folgt, der Spieler dribbelt automatisch in diese Richtung. Tastatur: WASD/Pfeile verschieben das Fadenkreuz, Gamepad: linker Stick.
- **In Schussnähe** (Ring am Boden) **gedrückt halten**: Der Power-Ring füllt sich, eine gestrichelte Linie zeigt die Flugbahn. Kurz = Handgelenkschuss, mittel = Schlenzer, lang = Schlagschuss (stärker, aber ungenauer). Tastatur: J oder Enter halten.
- **Loslassen** löst den Schuss aus.
- **Lupfer**: rechte Maustaste halten, Shift, oder beim Loslassen nach oben wischen.
- **Finte**: Leertaste oder Doppeltipp.

**Torhüter** (Timing entscheidet)
- Das Stellungsspiel läuft automatisch. A/D, Pfeile oder Stick verschieben selbst, nach vorn = herauskommen.
- **Parade**: Im richtigen Moment dorthin **tippen oder klicken, wo der Ball ins Tor fliegt**. Der Torhüter wählt die passende Parade (Hechtsprung, Fußabwehr, Butterfly, Fangen). Alternativ Richtung + Leertaste oder wischen.
- In der Stufe **Einsteiger** läuft beim Schuss ein kurzes Zeitlupenfenster.

**Allgemein**: **T** oder ⚙ öffnet das Tuning (auch im Spiel), **C** oder 🎥 wechselt die Kamera, **Esc/P** oder ⏸ pausiert. Ein Tipp überspringt Intro und Wiederholung.
Gamepad: A = Schuss/Parade, B = Finte, X = Lupfer, Y = Kamera, Start = Pause. Die Tasten lassen sich unter *Einstellungen* frei belegen.

## Modi
- **Schnelles Spiel**: Hauptmenü → Schnelles Spiel → Anpfiff (Zufallsgegner ist vorgewählt). Du schießt und hältst abwechselnd. „KI gegen KI“ lässt dich nur zuschauen.
- **Turnier**: 4 oder 8 Teams, Gruppenphase optional, danach K.-o. bis zum Finale. KI-Spiele lassen sich ansehen oder sofort simulieren. Mit Tabelle, Statistik und Siegerehrung. Der Stand wird gespeichert.
- **Training**: Schießen auf Zielscheiben (mit oder ohne Torhüter) oder Halten, ohne Wertung.
- **Teams**: Editor mit Live-3D-Vorschau, Import und Export als JSON. Importierte Daten werden gesäubert (Farben, Wertebereiche, HTML wird maskiert).

## Tuning und Tests
Alle Werte in `Config` wirken sofort. Es gibt die Presets Arcade, Realistisch und Simulation, eigene Presets, JSON-Export/-Import und eine Debug-Ansicht (Ballvektor, Hitboxen, Reichweite, Heatmap, Physikwerte).
Der Knopf **„Regeltests ausführen“** prüft 13 Fälle: Stopp- und Rückwärtsregel, Nachschuss, Torlinie, Tunnelsicherheit, Shootout-Ende und Sudden Death.

## Bekannte Grenzen
- Ohne Internet startet das Spiel nicht, weil Three.js vom CDN kommt. Abhilfe: `three.module.js` neben die Datei legen und die Importmap anpassen.
- Figuren sind prozedural: gehäuteter Körper (SkinnedMesh) mit modelliertem Kopf, Ausrüstung aus Grundkörpern. Kein echtes 3D-Modell, aus der Nähe bleibt der Puppenlook sichtbar. Das Trikot schwingt nur am Saum nach.
- Zuschauer sind instanzierte Sitzfiguren (drei Meshes für alle), Hallenmodell und Torhüter-Hitboxen (Kapseln) sind vereinfacht.
- Die Torraum-Regel (Schütze darf vor dem Schuss nicht in den Torraum) und die Lage des Torhüterraums sind nach bestem Wissen umgesetzt, aber nicht am Regelwerk verifiziert. Die Torraum-Regel ist im Tuning abschaltbar.
- Getestet nur in Chromium (Desktop und emulierter Pixel-7-Touch), ohne echte GPU. Firefox, Safari, Edge, echte Smartphones und die 60 FPS auf realer Hardware sind nicht geprüft.
