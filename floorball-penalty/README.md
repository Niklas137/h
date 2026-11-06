# Floorball Penalty Showdown

3D-Penaltyschießen im Floorball (Unihockey). Alles steckt in **einer Datei**: `index.html`.
Zum Starten die Datei doppelklicken. Three.js 0.160 wird einmalig vom CDN (jsdelivr) geladen, deshalb braucht der erste Start Internet.
Alle anderen Inhalte (Geometrie, Texturen, Ton) entstehen prozedural.

## Bedienung

**Schütze**
- **Laufen**: W/A/S/D, Pfeiltasten, linker Gamepad-Stick oder auf dem Handy der Joystick in der linken Bildschirmhälfte. Ohne Eingabe läuft der Spieler selbst Richtung Ziel.
- **Zielen**: Maus oder Touchpad zeigt auf die Stelle im Tor (gelbes Fadenkreuz); am Handy der Finger in der rechten Hälfte, am Gamepad der rechte Stick.
- **Schuss**: In Schussnähe (Ring am Boden) Maustaste bzw. Finger **halten** – der Ring füllt sich, eine gestrichelte Linie zeigt die Flugbahn. **Loslassen** schießt. Kurz = Handgelenkschuss, mittel = Schlenzer, lang = Schlagschuss.
- **Lupfer**: rechte Maustaste halten, Shift, oder beim Loslassen nach oben wischen.
- **Tricks beim Anlauf** (Tasten frei belegbar, am Handy die Knöpfe unten rechts):
  - **Täuschung** (Leertaste / Doppeltipp / B): Körpertäuschung, der Torhüter kann hineinfallen.
  - **Zieher** (Q / LB): der Ball wird mit gekippter Kelle quer vor dem Körper auf die andere Seite gezogen.
  - **Drehung** (E / RB): 360°-Drehung mit Ball, der Torhüter verliert kurz den Überblick.
  - **Zorro** (R / LT): der Ball wird auf die Kelle gehoben und getragen; der nächste Schuss geht aus der Luft (gut für die oberen Ecken).
  - Jeder Trick kann misslingen (abhängig vom Technik-Wert): dann verspringt der Ball kurz.

**Torhüter**
- **Bewegen** im ganzen Torraum (4 × 5 m): W/A/S/D, Pfeile, linker Stick oder Joystick links. Ohne Eingabe stellt er sich selbst.
- **Parade**: Im richtigen Moment dorthin tippen oder klicken, wo der Ball ins Tor fliegt. Alternativ Richtung + Leertaste oder wischen.
- **Raus!**: Kommt der Schütze zu nah, auf den Ball tippen/klicken, F, LT oder den roten Knopf drücken – der Torhüter springt dem Schützen entgegen und nimmt ihm den Ball ab. Berührt er den Ball, darf der Schütze nicht mehr nachschießen.
- KI-Torhüter kommen ebenfalls heraus, wenn man in den Torraum dribbelt (abhängig vom Wert „Mut“).
- In der Stufe **Einsteiger** läuft beim Schuss ein kurzes Zeitlupenfenster.

**Allgemein**: **T** oder ⚙ öffnet das Tuning (auch im Spiel), **C** oder 🎥 wechselt die Kamera, **Esc/P** oder ⏸ pausiert. Ein Tipp überspringt Intro und Wiederholung. Alle Tasten lassen sich unter *Einstellungen* frei belegen.

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
- Regelannahmen, nicht am IFF-Regelwerk verifiziert: Der Schütze darf in den Torraum (4 × 5 m), aber nicht in den Torhüterraum (1 × 2,5 m) – sonst Fehlversuch (im Tuning abschaltbar). Der Torhüter bleibt im Spiel auf den Torraum beschränkt. Der Zorro-Trick trägt den Ball unterhalb Kniehöhe.
- Getestet nur in Chromium (Desktop und emulierter Pixel-7-Touch), ohne echte GPU. Firefox, Safari, Edge, echte Smartphones und die 60 FPS auf realer Hardware sind nicht geprüft.
