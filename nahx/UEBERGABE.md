# NAHX Technologies – Übergabe aus dem bisherigen Chat (Stand 2026-10-26)

Diese Datei fasst den kompletten bisherigen Claude-Code-Chat zur Website von **NAHX Technologies** zusammen,
damit ein neues Projekt ohne Zugriff auf den alten Chat nahtlos weiterarbeiten kann.

## 1. Wo alles liegt

- **Repository:** `Niklas137/h`, Branch `claude/nahx-website-concept-34tlvk`, Ordner `nahx/`.
- **Letzter Stand:** Commit `c449b12` („bessere Lesbarkeit und eigene Bewegungssprache“).
- **Vorschau (privat, Claude-Artefakt):** https://claude.ai/artifact/Gr2LmKRN3EEmCko43L77bh (Version 20).
- **Kein Pull Request**, kein Merge nach `main`. Beides nur nach ausdrücklicher Freigabe durch Niklas.

```
nahx/
  build.py            Generator (Python 3, nur Standardbibliothek)
  inhalt/site.json    gemeinsame Daten: Sprachen, Seitenreihenfolge, Fotos mit Alt-Texten, Schriften
  inhalt/de.json      alle deutschen Texte (Standardsprache)
  inhalt/en.json      alle englischen Texte (gleiche Seitenschlüssel wie de.json)
  assets/site.css     Designsystem „Leinwand“
  assets/bewegung.js  Menü, Einblenden, Scroll-Fortschritt, Zähler, Inspektionslicht
  assets/szene3d.js   WebGL-3D-Szene des NAHX-A (ohne Bibliothek)
  assets/fonts/       Outfit (Titel) und Source Sans 3 (Text), beide SIL Open Font License
  assets/img/         Logo-Set (SVG, Favicon, Apple-Touch, 512er Icon, OG-Bild), foto/ mit 7 Fotos
  dist/               fertige Website (wird von build.py erzeugt und mit eingecheckt)
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
- **Sprachen:** Deutsch Standard unter `/`, Englisch unter `/en/`.
- **Domain:** später. Keine Domain im Code einbauen.
- **E-Mail:** vorhandene Adresse `niklas.heinzmann@fsh-documentation.de`. Keine Adresse erfinden.
- **Kontakt:** nur per E-Mail. Kein Formular, keine externen Dienste.
- **Logo:** Richtung beibehalten. Wortmarke NAHX mit silbernen Buchstaben, cyanfarbenem A
  (Verlauf `#02EEFB` → `#00A4F7`), Schriftzug TECHNOLOGIES, dünne Cyan-Linie, dunkler Hintergrund.
  Als echte Vektoren aus der Vorlage nachgemessen (`WORTMARKE` in build.py, Dateien in assets/img).
- **Keine erfundenen Fakten:** keine erfundenen Kunden, Mitarbeiter, Referenzen, Kennzahlen oder
  Erfolgsversprechen. Kundennamen aus den Repos (z. B. aus FSH-Projekten) werden nicht genannt.
  Der Wohnsitz wird nicht erwähnt.
- **Dokumentenprüfer** nicht als ausschließlich eigenes Produkt bewerben (entstanden mit FSH Documentation).
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

## 5. Heutiges Design „Leinwand“

- Jede Hauptszene ist eine Vollbild-Leinwand: Foto, kurzer Absatz oben rechts (im dunklen Glasblock),
  große leichte Versal-Überschrift unten links, Glaskarte unten rechts, Pfeil-Links statt Buttons.
- Transparenter Kopf mit Haarlinie, wird beim Scrollen zur dunklen Glasleiste.
- Farben: Schwarz `#05070B`, Navy `#0D121C`, Cyan `#17B8E6` / `#5FD6F7`, Text `#F5F7FA`, Grau `#CBD2DC`.
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
1. Dokumentenprüfer: Vorprüfung technischer Dokumente (mit FSH Documentation; Rechte in Abstimmung)
2. Kader-Manager für eine Vereinswebsite
3. Website-Relaunch und wöchentliches SEO-Audit
4. Mail-Triage und Tagesrunde (eigenes Werkzeug)
5. Diese Website

## 7. Fotos und Lizenzen

Sieben Fotos von Unsplash unter der Unsplash License (kommerziell nutzbar, keine Namensnennung nötig,
geprüft am 2026-10-25, keine Unsplash+-Bilder). Fotografen: Sandro Katalina (kopenhagen), Yusuf Onuk
(fabrik), EnCata PD (blaupause), Mohammad Rahmani (code), Compare Fibre (faser), Kashish Lamba (bokeh),
Vooglam Eyewear (designer). Quellen in `assets/img/foto/QUELLEN.md` und im Bildnachweis der Fußzeile.
Je Bild WebP und JPEG in mehreren Breiten, Aufmacher eager, alles andere lazy.

## 8. Qualitätsprüfung (bisher)

Mit Playwright in Chromium geprüft: kein horizontaler Überlauf von 320 bis 1440 px, keine Konsolenfehler,
keine fehlgeschlagenen Anfragen, Mobilmenü mit Escape, Tab-Reihenfolge, Lazy Loading, reduzierte Bewegung,
Überschriften ohne Überlauf. **Grenzen:** nur virtuelle Umgebung, keine echten Geräte, 3D-Szene dort nur per
Software-Rendering, keine Bildraten-Messung, kein Sicherheitsscan (kein API-Schlüssel).

## 9. Offene Punkte (Entscheidung Niklas)

- Domain festlegen, dann mit `--basis-url` bauen (Canonical, hreflang, Sitemap kommen automatisch).
- Impressum und Datenschutz mit echten Angaben füllen (keine Rechtsberatung).
- Freigaben für Kundennamen, Screenshots oder Referenzen.
- Rückmeldung zur Bewegung: welche Effekte stärker oder schwächer.
- Prüfung auf echten Geräten (iPhone, Mac), besonders 3D-Szene und Vorhang-Effekt.
- Merge nach `main` bzw. Pull Request erst nach Freigabe.

## 10. Nebenthema: Name für den Dokumentenprüfer („614 One“)

Falk schlug „614 One“ vor. Abgleich mit dem Code (`dokumentenpruefer/`):
- **4** passt: Berichte in Deutsch, Englisch, Ukrainisch, Russisch.
- **1** passt: ein Ergebnis mit Score, Ampel und PDF-Bericht.
- **6** passt heute nicht: es gibt drei Regelsätze (Basisprüfung, DIN 82079-1, CE / EU-Konformität)
  mit je acht Prüfbereichen. OCR, ANSI-Warnhinweise oder eine Normenmatrix gibt es im Code nicht.
- Versteckte Lesart: 6 = F, 14 = N, also Falk und Niklas; einzeln 6-1-4 = F-A-D.
- EN 614 existiert („Sicherheit von Maschinen – Ergonomische Gestaltungsgrundsätze“), das Tool prüft
  aber nicht danach. Verwechslungsgefahr bei Fachkunden.
- Empfehlung: Untertitel „614 One – Dokumentenprüfung“, vorher Marken- und Domaincheck (DPMA, EUIPO).
