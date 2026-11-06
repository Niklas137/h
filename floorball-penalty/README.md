# Floorball Penalty Showdown

3D-Penaltyschießen im Floorball (Unihockey). Alles steckt in **einer Datei**: `index.html`.
Zum Starten die Datei doppelklicken. Three.js 0.160 wird einmalig vom CDN (jsdelivr) geladen, deshalb braucht der erste Start Internet.
Alle anderen Inhalte (Geometrie, Texturen, Ton) entstehen prozedural.

## Bedienung

**Schütze**
- **Ziehen** (Maus/Finger), **WASD/Pfeile** oder **linker Stick**: Laufrichtung und Tempo. Der Ball bleibt am Schläger, Vor- und Rückhand wechseln automatisch. Ohne Eingabe läuft der Schütze mit mittlerem Tempo geradeaus weiter.
- **In Schussnähe** (Ring am Boden pulsiert) **gedrückt halten**: Der Power-Ring füllt sich. Die Zugrichtung bestimmt das Ziel (seitlich = Ecke, nach oben = hoch), die gelbe Zielhilfe zeigt es im Tor an.
- **Loslassen** löst den Schuss aus. Kurz = Handgelenkschuss, mittel = Schlenzer, lang = Schlagschuss (stärker, aber ungenauer). Tastatur: **J** oder Enter halten.
- **Lupfer**: Shift halten oder beim Loslassen nach oben wischen.
- **Finte**: Leertaste oder Doppeltipp.

**Torhüter**
- Langsam ziehen, WASD oder Stick: seitlich verschieben, nach vorn ziehen = herauskommen.
- **Parade**: schnell in die Richtung wischen (Touch/Maus) oder Richtung + Leertaste/J drücken.
  - seitlich = Hechtsprung
  - seitlich unten = Fußabwehr
  - nur unten = Butterfly
  - nur oben = Fangen
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
- Figuren sind aus Grundkörpern gebaut (Gelenkhierarchie, kein Skinning). Das Trikot schwingt nur am Saum nach.
- Zuschauer, Hallenmodell und Torhüter-Hitboxen (Kapseln) sind vereinfacht.
- Die Torraum-Regel (Schütze darf vor dem Schuss nicht in den Torraum) und die Lage des Torhüterraums sind nach bestem Wissen umgesetzt, aber nicht am Regelwerk verifiziert. Die Torraum-Regel ist im Tuning abschaltbar.
- Getestet nur in Chromium (Desktop und emulierter Pixel-7-Touch), ohne echte GPU. Firefox, Safari, Edge, echte Smartphones und die 60 FPS auf realer Hardware sind nicht geprüft.
