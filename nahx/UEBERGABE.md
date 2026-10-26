# NAHX Technologies – Übergabe (Stand 2026-10-26, Überarbeitung mit Testdaten)

Diese Datei fasst den kompletten bisherigen Claude-Code-Chat zur Website von **NAHX Technologies** zusammen,
damit ein neues Projekt ohne Zugriff auf den alten Chat nahtlos weiterarbeiten kann.

## 1. Wo alles liegt

- **Repository:** `Niklas137/h`, Ordner `nahx/`. Cyan-Stand: Branch `claude/nahx-website-concept-34tlvk`.
  **Mint-Stand (aktuell):** Branch `claude/nahx-mint` (abgezweigt von `f9464cf`), Flug ab Commit `a0da6c6`.
- **Vorschau (Claude-Artefakt, für jeden mit dem Link freigegeben, noindex):** https://claude.ai/artifact/Gr2LmKRN3EEmCko43L77bh
  (Version 28 = Chat im Handy als Demo; 27 = Überarbeitung nach Kundensicht-Prüfbericht mit Testdaten; 22 = Mint mit Flug durch A-Portale;
  21 = Mint ohne Flug; 20 = letzter Cyan-Stand, alle über den Versionsverlauf).
- **Aufgabenkatalog für Niklas und Falk (Claude-Artefakt, privat, Status und Notizen gemeinsam gespeichert):**
  https://claude.ai/artifact/KsKynwTEwnXxWeXT1Qdw4u – Quelle `nahx/katalog/` (Daten `aufgaben.json`, Lesefassung `KATALOG.md`).
- **Kein Pull Request**, kein Merge nach `main`. Beides nur nach ausdrücklicher Freigabe durch Niklas.

```
nahx/
  build.py            Generator (Python 3, nur Standardbibliothek)
  inhalt/site.json    gemeinsame Daten: Sprachen, Seitenreihenfolge, Fotos mit Alt-Texten, Schriften
  inhalt/de.json      alle deutschen Texte (unter /de/)
  inhalt/en.json      alle englischen Texte (Startsprache unter /, gleiche Seitenschlüssel wie de.json)
  assets/site.css     Designsystem „Leinwand“
  assets/bewegung.js  Menü, Einblenden, Scroll-Fortschritt, Zähler, Inspektionslicht
  assets/szene3d.js   WebGL-3D-Szene des NAHX-A (ohne Bibliothek)
  assets/fonts/       Outfit (Titel) und Source Sans 3 (Text), beide SIL Open Font License
  assets/img/         Logo-Set (SVG, Favicon, Apple-Touch, 512er Icon, OG-Bild), foto/ mit 7 Fotos
  dist/               fertige Website (wird von build.py erzeugt und mit eingecheckt)
  katalog/            Aufgabenkatalog Niklas/Falk (aufgaben.json, vorlage.html, bauen.py, KATALOG.md)
  assets/assistent.js Chat im Handy (Demo ohne Server, Live-Modus nach dem Protokoll des FSH-Assistenten)
  README.md           ausführliche Anleitung
```

## 2. Bauen und prüfen

```
python3 nahx/build.py --pruefen                                   # baut nach nahx/dist/ und prüft
python3 nahx/build.py --relativ --noindex --ausgabe /pfad/vorschau # Vorschau mit relativen Links
python3 nahx/build.py --basis-url https://example.org             # erst wenn die Domain feststeht
```

Die Prüfung kontrolliert lang-Attribut, genau eine h1, Überschriftenfolge, Title bis 60 Zeichen,
Description 150 bis 160 Zeichen, Alt-Texte, JSON-LD, interne Links und Anker. Ohne Basis-URL werden
Canonical, hreflang, og:url und Sitemap bewusst weggelassen, weil die Domain noch offen ist.

## 3. Verbindliche Entscheidungen von Niklas

- **Marke:** NAHX Technologies, persönliche Geschäftsbezeichnung, keine Gesellschaft.
- **Claim:** „Technik verstehen. Lösungen schaffen.“ / „Understand Technology. Create Solutions.“
- **Sprachen:** seit 2026-10-26 Englisch Startsprache unter `/`, Deutsch unter `/de/` (Zielmarkt außerhalb Deutschlands,
  Befund 4 des Prüfberichts; Bestätigung durch Niklas steht im Katalog). Vorher Deutsch unter `/`, Englisch unter `/en/`.
- **Domain:** später. Keine Domain im Code einbauen.
- **E-Mail:** echte Adresse folgt mit der Domain. Bis dahin steht in der Vorschau die als Test markierte Adresse
  `hello@nahx-technologies.example` (Auftrag „Testdaten einfüllen“). Keine echte Adresse erfinden.
- **Kontakt:** E-Mail, dazu seit 2026-10-26 der Chat im Handy (Wunsch Niklas: „den Chatbot besser auf der Webseite und in einer
  Handy-Ansicht, dass man direkt in einem Handy schreibt“). Kein Formular. In der Vorschau läuft der Chat als Demo ohne Server.
- **Logo:** Geometrie beibehalten. Wortmarke NAHX mit silbernen Buchstaben, **mintfarbenem A**
  (Verlauf `#2BFFD3` → `#00C99A`, seit 2026-10-26; vorher Cyan), Schriftzug TECHNOLOGIES, Mint-Linie, dunkler Grund.
  Als echte Vektoren aus der Vorlage nachgemessen (`WORTMARKE` in build.py, Dateien in assets/img).
- **Keine erfundenen Fakten:** keine erfundenen Kunden, Mitarbeiter, Referenzen, Kennzahlen oder
  Erfolgsversprechen. Kundennamen aus den Repos (z. B. aus FSH-Projekten) werden nicht genannt.
  Der Wohnsitz wird nicht erwähnt.
- **Dokumentenprüfer heißt „614 One“** (Entscheidung Niklas 2026-10-26): Produkt aus dem Hause NAHX Technologies,
  erster Pilotkunde und Tester ist FSH Documentation. Ersetzt die frühere Regel, ihn nicht als eigenes Produkt zu zeigen.
- **Keine Secrets**, kein automatisch abgespieltes Video mit Ton.

## 4. Verlauf der Gestaltung (damit klar ist, was schon verworfen wurde)

1. Erste Fassung nach Konzepttext. Von Niklas als „zu nah an FSH“ verworfen.
2. Zahnrad-Mechanik als Animation. Verworfen: „sieht cool aus, ist aber nicht meins“.
3. Mehrere Farbpaletten (Mint, Smaragd-Grün aus einem Ancola-Bild). Später zurück zu Schwarz/Navy/Cyan
   nach dem Master-Prompt. Die Schrift Ancola ist kommerziell, deshalb **Outfit** als freie Alternative.
4. WebGL-3D-Szene des A („muss 3D und realistisch sein“): Glasstein mit leuchtenden Rissen, Schatten,
   Spiegelboden, Bloom. Sie lebt heute als Markenbühne auf der Startseite.
5. „Visual Master Direction“: filmisch, fotografisch, redaktionell, echte Architektur- und Industriefotos.
6. **Referenzvideo** (Instagram-Reel von rinai.vis, Luxus-Architekturseite „NØR“ auf einem Laptop).
   Auftrag: „bauen wie im Video“. Daraus entstand das heutige Designsystem „Leinwand“.
7. Rückmeldung „Texte besser lesbar, mehr Animation, etwas Einzigartiges“. Umgesetzt im letzten Commit.
8. 2026-10-26: Markenboard „Clean Tech“ in Mint, Entscheidung „auf Mint umsteigen, ohne Gebäude“ (Abschnitt 9).
   Mint ist damit nicht mehr verworfen, sondern die gültige Richtung.

## 5. Heutiges Design „Leinwand“

- Jede Hauptszene ist eine Vollbild-Leinwand: Foto, kurzer Absatz oben rechts (im dunklen Glasblock),
  große leichte Versal-Überschrift unten links, Glaskarte unten rechts, Pfeil-Links statt Buttons.
- Transparenter Kopf mit Haarlinie, wird beim Scrollen zur dunklen Glasleiste.
- Farben seit 2026-10-26 (Mint): Grund `#030907`, Fläche `#06110D`/`#0A1713`, Mint `#00F0BE` / `#8CFFDA`, Mint Glow
  `#E8FFF7`, Deep Teal Gray `#34524A`, Midnight Green `#06130F`, Text `#F2FAF7`, Grau `#C2D1CB`. (Vorher Cyan auf Navy.)
- Startseite in sechs Szenen: Aufmacher → Collage „Drei Bereiche, ein Ansatz“ (03 Bereiche, 05 Projekte,
  DE · EN, nur zählbare Angaben der Website selbst) → Projektbühne mit drei Glas-Markierungen auf echte
  Projekte → Ablauf (5 Schritte) und Prinzipien als Haarlinienlisten → 3D-Markenbühne → Kontaktszene.
- Unterseiten: gleicher Aufmacher mit eigener Glaskarte, darunter Haarlinien statt Kacheln.

**Bewegung (eigene Sprache, `assets/bewegung.js`):**
Vorhang über festgeklemmtem Aufmacher; Schärfe-Einlauf der Überschriften Zeile für Zeile; Fotos ziehen
mit dem Scroll-Fortschritt; Collage mit eigenem Tempo, Neigung zum Zeiger und Wisch-Öffnung; hochzählende
Zahlen; Projektmarkierungen nacheinander (Punkt, Linie, Karte); Inspektionslicht folgt der Maus über Fotos;
Seitenübergänge per View Transitions. Bei `prefers-reduced-motion` ist alles aus. Kein Skript-Smooth-Scroll.

## 6. Seiten und Inhalte

Start, Leistungen, Projekte, Über mich, Zusammenarbeit, Kontakt, Impressum, Datenschutz (beide noindex,
Platzhalter). Drei Leistungsbereiche: Technical Documentation, Software & Web Applications, Automation & AI.

Fünf echte Projekte auf der Projektseite (je Ausgangssituation, Herausforderung, Beitrag, Lösungsansatz,
Technologien, Status, Ablaufkette):
1. 614 One – Dokumentenprüfung von NAHX Technologies (Pilotkunde und Tester: FSH Documentation)
2. Trikotwand – interaktive Kaderseite für einen Floorballverein (bis 2026-10-26 „Kader-Manager“, umbenannt:
   „ist was Individuelles und sollte nicht als Kader-Manager verkauft werden“)
3. Website-Relaunch und wöchentliches SEO-Audit
4. Mail-Triage und Tagesrunde (eigenes Werkzeug)
5. Diese Website

## 7. Fotos und Lizenzen

Sieben Fotos von Unsplash unter der Unsplash License (kommerziell nutzbar, keine Namensnennung nötig,
geprüft am 2026-10-25, keine Unsplash+-Bilder). Fotografen: Yusuf Onuk
(fabrik), EnCata PD (blaupause), Mohammad Rahmani (code), Compare Fibre (faser), Kashish Lamba (bokeh),
Vooglam Eyewear (designer). Quellen in `assets/img/foto/QUELLEN.md` und im Bildnachweis der Fußzeile.
Je Bild WebP und JPEG in mehreren Breiten, Aufmacher eager, alles andere lazy.

## 8. Qualitätsprüfung (bisher)

Mit Playwright in Chromium geprüft: kein horizontaler Überlauf von 320 bis 1440 px, keine Konsolenfehler,
keine fehlgeschlagenen Anfragen, Mobilmenü mit Escape, Tab-Reihenfolge, Lazy Loading, reduzierte Bewegung,
Überschriften ohne Überlauf. **Grenzen:** nur virtuelle Umgebung, keine echten Geräte, 3D-Szene dort nur per
Software-Rendering, keine Bildraten-Messung, kein Sicherheitsscan (kein API-Schlüssel).

## 9. Umstellung auf Mint (2026-10-26, Branch `claude/nahx-mint`)

Entscheidung Niklas: „Auf Mint umsteigen, da ich was anderes brauche als die FSH von Falk“, Vorlage ist das
Markenboard „Hauptlogo · Variante 1 · Clean Tech“ (Beschreibung im Projektdokument `claude/NAHX_REFERENZEN.md`),
Zusatz: **ohne das Gebäude**. Umgesetzt:
- Farbsystem, Logo-SVGs, Favicon, App-Icons, OG-Bild (neu gerendert mit `werkzeuge/marke_rendern.py`), 3D-Szene.
- Fotos in Mint-Lichtstimmung (`werkzeuge/foto_mint.py`, einmalig); Gebäudefoto „kopenhagen“ entfernt; neues
  Aufmacherbild „lichtleiter“ (gespiegelte Fassung von „faser“).
- Startseite nach Board: Claim als Kicker, Überschrift „Komplexe Technik. *Klare Lösungen.*“, gefüllte Mint-Taste,
  drei Leistungskarten, Ablauf „Verstehen. Konzipieren. *Umsetzen.* Prüfen.“ mit fünf Schritten.
- Überschriften kräftig in normaler Schreibweise statt leicht in Versalien.
- Fehler behoben: `@font-face` fehlte in `site.css`, Outfit und Source Sans 3 wurden nie geladen (nur Systemschrift).
- 404-Seite zeigt jetzt die Schaltfläche „Zur Startseite“ (vorher griff die Ersetzung in `build.py` nicht).

**Flug durch A-Portale (2026-10-26):** Wunsch „realistischer, mehrere Ebenen, durch jede schweben, eine krasse
Website wie im Video“. Gewählt: A-Portale aus dem Logo (statt Foto-Tafeln, Technik-Schichten oder Zahnrad-Tunnel).
Die Startseite beginnt mit einem scrollgesteuerten 3D-Flug durch fünf Szenen (Aufmacher, drei Bereiche, Ansatz),
Beschreibung in `README.md`. Grenze der Prüfung: Testbrowser nur mit Software-Rendering (dort rund 6 Bilder/s),
echte Geräte noch nicht geprüft.

**3D-A schärfer und kräftiger (2026-10-26):** Ursache der Unschärfe war die feste Renderauflösung 0,7 (auf Retina
effektiv 0,35 Gerätepixel, gemessen 1008 × 490 für 1440 × 700). Jetzt nach Pixeldichte (gemessen 1800 × 875) mit
Leistungsregelung, Mint-Kontur wie im Logo, ACES-Tonkurve.
Danach: kein Zittern mehr (Pixelversatz, Korn und Hoch-/Runterregeln entfernt), keine Reaktion auf Maus, Finger oder
Scrollen, das A bewegt sich nur von selbst; Leuchtlinien dezenter. Auch der Flug neigt sich nicht mehr mit der Maus.

## 10. Offene Punkte (Entscheidung Niklas) – Stand vor der Überarbeitung, heute im Katalog gepflegt

- Domain festlegen, dann mit `--basis-url` bauen (Canonical, hreflang, Sitemap kommen automatisch).
- Impressum und Datenschutz mit echten Angaben füllen (keine Rechtsberatung).
- Freigaben für Kundennamen, Screenshots oder Referenzen.
- Rückmeldung zur Bewegung: welche Effekte stärker oder schwächer.
- Prüfung auf echten Geräten (iPhone, Mac), besonders Flug durch die A-Portale (Flüssigkeit) und 3D-Markenbühne.
- Merge nach `main` bzw. Pull Request erst nach Freigabe.
- Mint-Stand: Board-Leitsatz „Weiterentwickeln“ statt „Prüfen“? (Heute „Prüfen“, passend zu den fünf freigegebenen Schritten.)
- Mint-Stand: Foto „Industriehalle“ (Projektbühne, Projekteseite) behalten oder ersetzen? Zeigt ein Zahnrad.

## 11. Name für den Dokumentenprüfer: „614 One“ (entschieden 2026-10-26)

Niklas: „Das Dokumentenprüftool bekommt den Namen 614 One aus dem Hause NAHX Technologies, erster Pilotkunde und
Tester ist FSH.“ Auf der Website umgesetzt (Projektbühne, Projekteseite, Über mich, DE/EN). Die Abwägung von vorher:

Falk schlug „614 One“ vor. Abgleich mit dem Code (`dokumentenpruefer/`):
- **4** passt: Berichte in Deutsch, Englisch, Ukrainisch, Russisch.
- **1** passt: ein Ergebnis mit Score, Ampel und PDF-Bericht.
- **6** passt heute nicht: es gibt drei Regelsätze (Basisprüfung, DIN 82079-1, CE / EU-Konformität)
  mit je acht Prüfbereichen. OCR, ANSI-Warnhinweise oder eine Normenmatrix gibt es im Code nicht.
- Versteckte Lesart: 6 = F, 14 = N, also Falk und Niklas; einzeln 6-1-4 = F-A-D.
- EN 614 existiert („Sicherheit von Maschinen – Ergonomische Gestaltungsgrundsätze“), das Tool prüft
  aber nicht danach. Verwechslungsgefahr bei Fachkunden.
- Empfehlung (weiter offen): Untertitel „614 One – Dokumentenprüfung“ ist so umgesetzt; Marken- und Domaincheck
  (DPMA, EUIPO) steht noch aus. Keine Rechtsberatung.
- Offen: ob der Name auch in der App selbst (Oberfläche, PDF-Berichte, Branch `claude/dokumentenpruefer-webapp`) erscheint.

## 12. Überarbeitung mit Testdaten (2026-10-26, Version 27)

Auftrag Niklas: „Überarbeite einmal alles, fülle noch mal Testdaten ein … den Rest tauschen wir dann, wenn alles
feststeht … setze dazu einen Katalog für mich (Niklas) und Falk zum Abarbeiten auf.“ Grundlage: Prüfbericht
`claude/NAHX_KUNDENSICHT_PRUEFBERICHT.md`. Umgesetzt:

- **Testdaten-Kennzeichnung:** `<mark class="test">` (gestrichelt, hochgestelltes „Test“) plus Hinweis unten auf
  jeder Seite (`site.json` → `testdaten`). Markiert sind Preise, Lieferzeiten, Anschrift, Telefon, E-Mail,
  Antwortzeit, Steuerstatus, Hosting, Speicherdauer, Rechtsgrundlagen, Aufsichtsbehörde, Porträt, LinkedIn, Termin.
- **Englisch als Startsprache**, Deutsch unter `/de/`; `x-default` folgt der ersten Sprache in `site.json`.
- **Startseite:** Flug mit „Intro überspringen“ und Zeile „Remote für Kunden in Europa · Deutsch und Englisch“,
  danach drei Einstiegsangebote (neuer Abschnittstyp `angebote`), Projektbühne mit Foto „code“, „Stimmen“ mit zwei
  Platzhaltern (Typ `stimmen`), Ablauf, 3D-Markenbühne, Kontaktband. Arbeitsprinzipien nur noch auf „Über mich“.
- **Kopf:** Taste „Projekt besprechen“ / „Discuss a Project“ ab 1100 px fest im Kopf.
- **Über mich:** Porträt-Block mit NH-Monogramm und Fakten (Typ `portraet`), Texte ohne „keine Agentur/Gesellschaft“.
- **Kontakt:** weitere Wege als Platzhalter (LinkedIn, Erstgespräch), Antwortzeit als Testwert.
- **Projekte:** eigene Bilder statt Stockfotos bei 614 One (Fachbericht aus erfundenem Testdokument), Trikotwand
  (Testspieler) und NAHX-Website (Screenshot); Fabrikfoto entfernt; Mail-Triage heißt „E-Mail-Vorsortierung mit
  Freigabe“. Ein FSH-Website-Screenshot liegt nicht im Repo und wird erst nach Freigabe durch FSH erstellt.
- **Ton:** „keine Garantie“, „keine Agentur“, „keine Technologieliste“ u. ä. ersetzt; „Wir prüfen“ → „Ich prüfe“.
- **Fehler behoben:** Zähler zeigen ohne JavaScript die echte Zahl statt „00“; Pfeil in der Kopf-Taste.
- **Seitentitel:** „NAHX Technologies – Documentation, Software, Automation“ (DE analog).

Prüfung: `build.py --pruefen` ohne Befund, Playwright 18 Seiten × 5 Breiten ohne Überlauf und ohne Konsolenfehler,
reduzierte Bewegung, Tastatur und Menü geprüft, Sichtprüfung der neuen Abschnitte auf 1440 und 390 px.

**Livegang-Weg:** alle `mark class="test"` ersetzen, `testdaten` aus `site.json` löschen, Basis-URL setzen, ohne
`--noindex` bauen. Was dafür fehlt, steht im Katalog (32 Punkte: Niklas 18, Falk 6, gemeinsam 3, Claude 5).

## 13. Chat im Handy (2026-10-26, Version 28)

Niklas: „Dazu haben wir ja schon einen Chatbot. Den möchte ich noch besser auf der Webseite haben und in einer
Handy-Ansicht, also dass man direkt in einem Handy schreibt.“ Der vorhandene Bot ist der **FSH-Assistent** im Repo
`Niklas137/fsh-website` (Cloudflare Worker `src/assistent/`, Claude Haiku, D1-Datenbank, Klick-Kalender, Mail an Falk,
Fenster `quelle/assistent/assistent/widget.js`). Er nimmt nur Anfragen von den FSH-Domains an (`HERKUNFT` in
`src/assistent/konfig.js`) und arbeitet mit FSH-Texten, deshalb wurde er auf der NAHX-Seite **nicht** angeschlossen.
Die FSH-Website wurde nicht verändert.

Umgesetzt in `nahx/`:
- Abschnittstyp `assistent` (Start nach den Angeboten, Kontakt): Text links, **Handy** rechts (Rahmen, Dynamic Island,
  Statusleiste mit Uhrzeit, Kopf mit Mint-A, Blasen, Vorschläge, Eingabe, Home-Leiste). Man schreibt direkt ins Handy.
- Auf Bildschirmen unter 700 px öffnet ein Tippen ins Feld den Chat **bildschirmfüllend wie einen Messenger**
  (Zurück-Pfeil, Tastaturhöhe über `visualViewport`).
- Auf allen übrigen Seiten ein **Chat-Knopf** unten rechts; auf dem Desktop schwebt das Handy unten rechts, auf dem Handy
  Vollbild. Der Verlauf bleibt beim Seitenwechsel im selben Tab (sessionStorage).
- **Demo-Modus**, solange `site.json` → `assistent.api` leer ist: vorbereitete Antworten nach Stichworten
  (`inhalt/<sprache>.json` → `assistent.demo.wissen`), Testpreise markiert, Klick-Kalender mit Testterminen, nichts wird
  gesendet. Mit Adresse: dasselbe Protokoll wie der FSH-Assistent (GET bereit, POST Nachricht, GET /termine).
- Datenschutz: Abschnitt „Chat-Assistent“ mit markierten Angaben für den Livebetrieb; Satz „speichert nichts im Browser“
  angepasst.
- Katalog um sechs Punkte ergänzt (eigene NAHX-Instanz, Inhalte, WhatsApp, Code-Nutzung, Referenz, Anschluss): 38 Punkte.

Prüfung: Bau ohne Befund, Playwright 18 Seiten × 5 Breiten ohne Überlauf und Konsolenfehler, Chatablauf auf Desktop
(Vorschlag, Freitext, Kalender, Termin, Seitenwechsel mit schwebendem Handy) und auf 390 px mit Touch (Vollbild, Senden,
Zurück), ohne JavaScript (Feld gesperrt, Knopf verborgen). Nicht geprüft: echtes iPhone mit Bildschirmtastatur.
