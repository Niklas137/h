# Floorball Penalty Showdown

3D-Penaltyschießen im Floorball (Unihockey). Das ganze Spiel steckt in **einer Datei**: `index.html`.
Zum Starten die Datei doppelklicken. Three.js 0.160 wird einmalig vom CDN (jsdelivr) geladen, deshalb braucht der erste Start Internet.
Alle anderen Inhalte (Geometrie, Texturen, Ton) entstehen prozedural im Browser.

## Bedienung

**Schütze**
- **Laufen**: W/A/S/D, Pfeiltasten, linker Gamepad-Stick oder auf dem Handy der Joystick in der linken Bildschirmhälfte. Ohne Eingabe läuft der Spieler selbst Richtung Ziel.
- **Zielen**: Maus oder Touchpad zeigt auf die Stelle im Tor (gelbes Fadenkreuz). Am Handy zielt der Finger in der rechten Hälfte, am Gamepad der rechte Stick.
- **Schuss**: Maustaste bzw. Finger **halten** lädt die Kraft, **loslassen** schießt. Das geht überall nach dem Anpfiff. Der Bogen am Fadenkreuz zeigt die Kraft, der weiße Kreis die Streuung (mehr Kraft = ungenauer), die gestrichelte Linie die Flugbahn. Kurz = Handgelenkschuss, mittel = Schlenzer, lang = Schlagschuss. Nach dem Schuss erscheint das Tempo in km/h.
- **Lupfer**: rechte Maustaste halten, Shift, oder beim Loslassen nach oben wischen.
- **Tricks beim Anlauf** (Tasten frei belegbar, am Handy die Knöpfe rechts):
  - **Täuschung** (Leertaste / Doppeltipp / B): Körpertäuschung, der Torhüter kann hineinfallen.
  - **Zieher** (Q / LB): der Ball wird mit gekippter Kelle quer vor dem Körper auf die andere Seite gezogen.
  - **Drehung** (E / RB): 360°-Drehung mit Ball, der Torhüter verliert kurz den Überblick.
  - **Zorro** (R / LT): der Ball wird auf die Kelle gehoben und getragen, der nächste Schuss geht aus der Luft.
  - Ein während eines Tricks gedrückter Trick wird kurz vorgemerkt und folgt direkt danach. Jeder Trick kann misslingen (abhängig vom Technik-Wert), dann verspringt der Ball.

**Torhüter**
- **Bewegen** im ganzen Torraum (4 × 5 m): W/A/S/D, Pfeile, linker Stick oder Joystick links. Ohne Eingabe stellt er sich selbst.
- **Parade**: Im richtigen Moment dorthin tippen oder klicken, wo der Ball ins Tor fliegt. Alternativ Richtung + Leertaste oder wischen.
- **Raus!**: Kommt der Schütze zu nah, auf den Ball tippen/klicken, F, LT oder (am Handy) den roten Knopf drücken. Der Torhüter springt dem Schützen entgegen. Berührt er den Ball, darf der Schütze nicht mehr nachschießen.
- In der Stufe **Einsteiger** läuft beim Schuss ein kurzes Zeitlupenfenster.

**Allgemein**: **T** oder ⚙ öffnet das Tuning (auch im Spiel), **C** oder 🎥 wechselt die Kamera, **Esc/P** oder ⏸ pausiert. Ein Tipp überspringt Intro und Wiederholung. Alle Tasten lassen sich unter *Einstellungen* frei belegen.

## Modi
- **Schnelles Spiel**: Hauptmenü → Schnelles Spiel → Anpfiff (Zufallsgegner ist vorgewählt). Du schießt und hältst abwechselnd. „KI gegen KI“ lässt dich zuschauen.
- **Turnier**: 4 oder 8 Teams, Gruppenphase optional, danach K.-o. bis zum Finale. KI-Spiele lassen sich ansehen oder sofort simulieren. Mit Tabelle, Statistik und Siegerehrung. Der Stand wird gespeichert.
- **Training**: Schießen auf Zielscheiben (mit oder ohne Torhüter) oder Halten, ohne Wertung.
- **Teams**: Editor mit Live-3D-Vorschau, Import und Export als JSON. Importierte Daten werden gesäubert (Farben, Wertebereiche, HTML wird maskiert).

## Grafik und Ton
- **Arena**: Tribünen mit Sitzschalen und Treppen, Wände, Decke mit Strahlern, LED-Laufband, Banner, Anzeigewürfel. Die Fanlager tragen die Farben der beiden Teams und jubeln getrennt.
- **Qualitätsstufen** (Einstellungen oder Tuning → Grafik):
  - *Niedrig*: direktes Zeichnen ohne Effekte, kleine Texturen, weniger Zuschauer.
  - *Mittel*: HDR-Bild mit Bloom und Kantenglättung (Vorgabe auf Mobilgeräten).
  - *Hoch*: zusätzlich Bodenspiegelung, stärkere Kantenglättung, volle Texturauflösung (Vorgabe am Rechner).
- **Dynamische Auflösung**: Fällt die Bildrate länger ab, sinkt die interne Auflösung schrittweise und steigt bei Reserve wieder.
- **Hallenboden**: Parkett oder blauer Kunststoffbelag.
- **Figuren**: Jeder Spieler hat ein festes Aussehen (Hautton, Frisur, Gesicht, Bart, Stirnband, Schuhe), abgeleitet aus Name und Nummer. Torhüter tragen Gittermaske, gesteppte Kleidung und Handschuhe.
- **Ton**: vollständig synthetisch (Web Audio) mit Hallenakustik, Torhupe, Applaus und Publikum.
- Ohne Gleitkomma-Texturen im Browser schaltet das Spiel selbst auf direktes Zeichnen zurück.

## Tuning und Tests
Alle Werte in `Config` wirken sofort. Es gibt die Presets Arcade, Realistisch und Simulation, eigene Presets, JSON-Export/-Import und eine Debug-Ansicht (Ballvektor, Hitboxen, Reichweite, Heatmap, Physikwerte).
Der Knopf **„Regeltests ausführen“** prüft 13 Fälle: Stopp- und Rückwärtsregel, Nachschuss, Torlinie, Tunnelsicherheit, Shootout-Ende und Sudden Death. Die Tests laufen immer mit den Standardwerten, unabhängig vom gewählten Preset.

Im Ordner `pruefung/` liegen Prüfskripte für Playwright (Chromium):

```bash
node pruefung/regression.js
```

```bash
node pruefung/touch.js
```

`regression.js` prüft 18 Punkte (Regeltests, KI-Trefferquote, Kelle am Ball, Maus und Tastatur, Tricks, Torhüter, Turnier, Editor und Import, Tuning, HUD, Konsole). `touch.js` prüft Joystick, Zielen, Trick-Knöpfe und Parade auf einem emulierten Smartphone.

## Bekannte Grenzen
- Ohne Internet startet das Spiel nicht, weil Three.js vom CDN kommt. Abhilfe: `three.module.js` neben die Datei legen und die Importmap anpassen.
- Die Figuren sind prozedural: gehäuteter Körper, modellierter Kopf mit gemaltem Gesicht, Ausrüstung aus erzeugter Geometrie. Es gibt keine Mimik, die Finger sind starr, aus nächster Nähe bleibt der Look stilisiert.
- Zuschauer sind eine einfache, tausendfach instanzierte Sitzfigur ohne Gesicht. Die Torhüter-Trefferzonen sind Kapseln.
- Regelannahmen, nicht am IFF-Regelwerk verifiziert: Der Schütze darf in den Torraum (4 × 5 m), aber nicht in den Torhüterraum (1 × 2,5 m), sonst Fehlversuch (im Tuning abschaltbar). Der Torhüter bleibt auf den Torraum beschränkt. Der Zorro-Trick trägt den Ball unterhalb Kniehöhe.
- Geprüft nur in Chromium ohne echte Grafikkarte (Software-Rendering, Desktop und emuliertes Pixel 7). Firefox, Safari, Edge, echte Smartphones und die Bildrate auf realer Hardware sind nicht gemessen.
- In eingebetteten Vorschauen (z. B. Artefakt-Ansicht) können Datei-Downloads gesperrt sein. Dann wirken die Export-Knöpfe nicht.
