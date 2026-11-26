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
- **Spiel 5 gegen 5**: echtes Floorballspiel mit fünf Feldspielern und einem Torhüter je Team, drei Drittel (1, 2, 3 oder 5 Minuten je Drittel, in der Teamwahl einstellbar).
  - Du steuerst einen Spieler von Team A; mit Ball schießt du wie beim Penalty (Maus zielt, halten = Kraft, loslassen = Schuss).
  - **Leertaste** (Touch: Knopf „Pass“, Gamepad: B): mit Ball passen zum Mitspieler in Lauf- bzw. Blickrichtung, ohne Ball kurz energisch zum Ball gehen (höhere Chance, ihn zu erobern).
  - **X** (Touch: „Wechsel“): Spieler wechseln. Bei Ballbesitz steuerst du automatisch den Ballführer, nach einem Pass den Empfänger.
  - **Assistenz**: Ohne Eingabe spielt die KI deinen Spieler nach 1,2 s weiter, bis du wieder lenkst, schießt oder passt.
  - Regeln vereinfacht: Bully zu Beginn jedes Drittels und nach Toren, Einschlag für das andere Team, wenn der Ball die Bande verlässt, Feldspieler dürfen nicht in die Torhüterräume, Torhüter fangen Bälle im Torhüterraum und werfen sie zu einem freien Mitspieler ab. Kein Abseits, keine Strafen.
  - Unentschieden nach drei Dritteln: Knopf „Penaltyschießen“ startet ein Shootout mit denselben Teams.
  - Kamera schräg hinter deinem Spieler (C wechselt zur seitlichen Fernsehansicht). KI gegen KI zeigt die Fernsehansicht.
  - Laufstil: echter Laufrhythmus mit tempoabhängiger Schrittfrequenz (Trab etwa 3, Sprint etwa 4 Schritte pro Sekunde), Flugphase im Sprint, Abrollen von der Ferse über den Ballen, Becken senkt sich in der Standphase und dreht zum vorderen Bein. Vorlage beim Antritt, tiefer Sitz mit flachen Stoppschritten beim Bremsen, Innenlage in Kurven, im Sprint schmalere Spur. Standfüße gleiten nicht und behalten ihre Richtung, Beine kreuzen nicht, Landepunkte bleiben in Beinreichweite.
  - Ballannahme: Kommt ein Ball auf einen Spieler zu, öffnet er den Körper zum Ball, geht tief und bringt das Blatt offen an den ersten erreichbaren Punkt der Ballbahn. Beim Kontakt federt das Blatt mit dem Ball zurück (10–38 cm je nach Tempo, gleichmäßig gebremst, nie bis in den Körper), danach geht der Ball weich ins Dribbling über. Harte Bälle können je nach Technik vom Schläger springen.
  - **Direktschuss**: Kommt ein Pass, Maustaste gedrückt halten. Der Spieler holt ohne Ball aus, der Schlag startet so, dass er den ankommenden Ball trifft, und wird bis kurz vor dem Kontakt nachgeführt. Ist der Ball nicht am Blatt, geht der Schlag ins Leere. Direktschüsse sind etwas schneller, aber ungenauer. Die KI schießt in Schussposition je nach Technik ebenfalls direkt.
  - **Schusstäuschung**: Leertaste während des Ausholens. Das Blatt kommt zum Ball und stoppt, der Ball bleibt am Schläger. Weiter gedrückt halten, um gleich mit einem Teil der Kraft abzuziehen. Ein Torhüter, der anbeißt, geht in den Butterfly und braucht über eine Sekunde, um wieder hochzukommen. Gilt auch im Penaltyschießen und für die KI.
  - **Zweikampf**: Der Verteidiger stößt den Ball mit dem Blatt vom Schläger (Stocherstoß), der Ball ist dann frei und wer schneller ist, holt ihn. Der Ballführer schirmt ab: Ball auf die vom Gegner abgewandte Seite, Schulter hinein. Körperkontakt wirkt nach Masse (Größe und Statur), harte Zusammenstöße bringen kurz ins Straucheln, Seite an Seite lehnen sich Gegner gegeneinander. Keine Strafen.
  - **KI-Taktik**: Angreifer ohne Ball laufen sich frei (Punkt mit Abstand zu Gegnern, offener Passlinie und Raumgewinn), Passgeber meiden verstellte Linien. Nach einem Pass startet der Passgeber oft in die Tiefe, steht er frei, kommt der Ball direkt zurück (Doppelpass). Verteidiger decken Mann gegen Mann torseitig mit stabiler Zuteilung, gehen am Mann mit statt hineinzurennen, und alle Spieler ohne Ball weichen vorausschauend aus.
  - **Mimik**: Spieler zeigen Freude (Jubel, Tor des eigenen Teams), Frust (gehaltener Penalty, Gegentor) und Anstrengung (Ausholen, Schuss, Täuschung, Sprint). Technisch eine kleine Gesichtsmaske über dem gemalten Gesicht (eigene Texturen je Ausdruck, 256 px), die weich ein- und ausgeblendet wird. Der Haaransatz ist je Frisur weich gemalt.
  - **Statur**: Jeder Spieler hat eine eigene Statur von schmal bis kräftig (Schultern, Brust, Arme, Oberschenkel, Waden, Nacken) über ein Morph-Ziel der geteilten Körpergeometrie, Größere sind im Schnitt etwas kräftiger.
  - Bewegungen: Pässe sind eine kurze Schlagbewegung von 0,15 s (Blatt zum Ball, dann verlässt der Ball die Kelle), Spieler ohne Ball stochern mit dem Schläger nach einem nahen, flachen Ball, Torhüter holen beim Abwurf sichtbar mit dem Arm aus. Feldspieler sind unterschiedlich groß (93–106 %), Arme und Beine passen sich an.
- **Parcours** (wie im Vorbild-Video, eine Werbung für ein Floorball-Handyspiel): drei Übungen und ein Schuss, auf Zeit und Punkte.
  1. **Slalom**: im Zickzack an den orangen Hütchen vorbei, die grünen Pfeile zeigen die Seite.
  2. **Volle Drehungen**: einmal ganz um jedes der zwei grünen Hütchen, die Punkte im Kreis füllen sich mit.
  3. **Durch die Tore**: durch zwei kleine blaue Tore.
  4. **Schuss**: erst jetzt ist der Schuss frei, vier Ziele hängen in den Torecken, ein Torhüter hält.
  - Wertung: Zeitbonus (35 s minus Zeit bis zum Schuss, mal 10), Tor +100, jedes getroffene Ziel +50, jeder Fehler −20 (Hütchen berührt, falsche Seite, ausgelassen, Tor verpasst). Der Bestwert wird gespeichert.
  - Ohne Eingabe bleibt der Spieler stehen, die Vorwärtsregel gilt hier nicht. Ausgelassene Übungen zählen als Fehler, nichts blockiert. Zeitlimit 60 s.
  - Kamera schräg von hinten oben mit Blick zum Tor, im Hochformat steiler und weiter. Der Boden ist im Parcours immer blau.
- **Penaltyschießen**: Hauptmenü → Penaltyschießen → Anpfiff (Zufallsgegner ist vorgewählt). Du schießt und hältst abwechselnd. „KI gegen KI“ lässt dich zuschauen.
- **Turnier**: 4 oder 8 Teams, Gruppenphase optional, danach K.-o. bis zum Finale. KI-Spiele lassen sich ansehen oder sofort simulieren. Mit Tabelle, Statistik und Siegerehrung. Der Stand wird gespeichert.
- **Training**: Schießen auf Zielscheiben (mit oder ohne Torhüter) oder Halten, ohne Wertung.
- **Freies Training** (Training → Freies Training): keine Regeln, kein Zeitlimit, keine Torhüterraum-Regel. Überall laufen, tricksen und schießen, so oft man will. Nach jedem Schuss zeigt eine kurze Meldung das Ergebnis, dann liegt der Ball wieder am Schläger. Bleibt der Ball liegen, kommt er nach 1,5 s zurück. Oben links zählen Schüsse, Tore, Paraden, Zielscheiben und der schnellste Schuss. Optional mit oder ohne Torhüter und mit den Parcours-Hütchen als Hindernisse (ohne Wertung).
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

`regression.js` prüft 43 Punkte (Regeltests, KI-Trefferquote, Kelle am Ball, Maus und Tastatur, Tricks, Torhüter, Parcours mit Testfahrer, freies Training, Spiel 5 gegen 5 bis zum Endstand, Laufstil (Fußgleiten, Beinreichweite, Knie, Kreuzen, Schrittfrequenz, Kurven- und Rücklage), Ballannahme (Blatt am Ball, Abfedern, Passquote), Schusstäuschung und Direktschuss als Mensch, Mimik und Statur, Zweikampf, KI-Taktik (Passlinien, Doppelpass, Manndeckung im Vergleich zur Formation), Turnier, Editor und Import, Tuning, HUD, Konsole). `touch.js` prüft Joystick, Zielen, Trick-Knöpfe und Parade auf einem emulierten Smartphone.

## Bekannte Grenzen
- Ohne Internet startet das Spiel nicht, weil Three.js vom CDN kommt. Abhilfe: `three.module.js` neben die Datei legen und die Importmap anpassen.
- Die Figuren sind prozedural: gehäuteter Körper, modellierter Kopf mit gemaltem Gesicht, Ausrüstung aus erzeugter Geometrie. Es gibt keine Mimik, die Finger sind starr, aus nächster Nähe bleibt der Look stilisiert.
- Zuschauer sind eine einfache, tausendfach instanzierte Sitzfigur ohne Gesicht. Die Torhüter-Trefferzonen sind Kapseln.
- Regelannahmen, nicht am IFF-Regelwerk verifiziert: Der Schütze darf in den Torraum (4 × 5 m), aber nicht in den Torhüterraum (1 × 2,5 m), sonst Fehlversuch (im Tuning abschaltbar). Der Torhüter bleibt auf den Torraum beschränkt. Der Zorro-Trick trägt den Ball unterhalb Kniehöhe.
- Das Spiel 5 gegen 5 ist vereinfacht: keine Strafen, kein Abseits (gibt es im Floorball ohnehin nicht), Pässe ohne eigene Schlaganimation, Zweikämpfe als Wahrscheinlichkeit nach Technik-Wert. Ein Turnier mit vollen Spielen gibt es noch nicht.
- Mit zwölf Figuren steigt die Zahl der Zeichenaufrufe deutlich; auf schwachen Geräten die Grafikstufe „Niedrig“ wählen.
- Die schmale Großschrift im Parcours nutzt Systemschriften (z. B. Avenir Next Condensed auf Apple-Geräten). Fehlen sie, erscheint eine fette Standardschrift.
- Geprüft nur in Chromium ohne echte Grafikkarte (Software-Rendering, Desktop und emuliertes Pixel 7). Firefox, Safari, Edge, echte Smartphones und die Bildrate auf realer Hardware sind nicht gemessen.
- In eingebetteten Vorschauen (z. B. Artefakt-Ansicht) können Datei-Downloads gesperrt sein. Dann wirken die Export-Knöpfe nicht.
