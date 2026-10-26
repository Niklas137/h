# NAHX Technologies – Website (statisch, zweisprachig)

Website zur persönlichen Geschäftsmarke NAHX Technologies (keine Gesellschaft). Claim „Technik verstehen. Lösungen
schaffen.“ / „Understand Technology. Create Solutions.“ Gleiche Bauweise wie `website/` (FSH-Documentation):
Inhalte als JSON, ein Python-Skript ohne Abhängigkeiten, fertige Dateien in `dist/`. Kein externes Skript, keine
externen Schriften, kein Tracking, kein Formular.

## Ordner

| Pfad | Zweck |
|---|---|
| `build.py` | baut die Seiten aus `inhalt/` nach `dist/` (Python 3.8+, keine Pakete) und prüft sie (`--pruefen`) |
| `inhalt/site.json` | gemeinsame Daten: Name, Basis-URL (leer, solange die Domain offen ist), Sprachen, Reihenfolge der Seiten |
| `inhalt/de.json`, `inhalt/en.json` | alle Texte je Sprache, gleiche Seitenschlüssel (`start`, `leistungen`, `projekte`, `ueber-mich`, `zusammenarbeit`, `kontakt`, `impressum`, `datenschutz`) |
| `assets/site.css` | Designsystem: Schwarz/Navy, Cyan-Akzent, Outfit und Source Sans 3 lokal |
| `assets/fonts/` | Outfit (variabel, TTF) für Überschriften und Source Sans 3 (WOFF2) für Text, beide SIL Open Font License, Lizenztexte liegen dabei |
| `assets/img/` | Logo-Satz (siehe unten), Favicons, Open-Graph-Bild, Logo-Vorlage |
| `assets/img/foto/` | Fotografien in responsiven Varianten, `QUELLEN.md` mit Fotografen und Lizenz |
| `assets/szene3d.js` | 3D-Szene der Markenbühne (WebGL) |
| `dist/` | **fertige Website zum Hochladen** (wird von `build.py` komplett neu erzeugt) |

## Bauen und prüfen

```bash
python3 nahx/build.py --pruefen
```

Prüft: `lang`-Attribut, genau eine h1 je Seite, Überschriftenfolge, Title bis 60 Zeichen, Description 150–160 Zeichen,
Alt-Attribute, JSON-LD, alle internen Links und Anker. Mit gesetzter Basis-URL zusätzlich Canonical, hreflang
(de, en, x-default) und Sitemap. Fehler ergeben Exit-Code 1.

Schalter: `--relativ --ausgabe /tmp/vorschau` (Vorschau ohne Webserver), `--basis-url https://…` (sobald die
Domain feststeht), `--noindex` (Testbetrieb: alle Seiten `noindex`, `robots.txt` sperrt).

## Domain offen: was zurückgestellt ist

`basis_url` in `site.json` ist leer (Entscheidung 2026-10-25: Domain später). Solange sie leer ist, erzeugt der Bau
**keine** Canonical-Links, keine hreflang-Alternates, kein `og:url`, keine Sitemap und keinen Sitemap-Eintrag in
`robots.txt`; `og:image` ist dann relativ. Alle internen Links sind pfadbezogen und domainunabhängig. Zum Livegang
die Basis-URL eintragen (oder `--basis-url`), neu bauen; der Prüflauf verlangt dann Canonical, hreflang und Sitemap.

## Seiten

| Deutsch | English | Inhalt |
|---|---|---|
| `/` | `/en/` | Aufmacher mit Diagramm der drei Bereiche, Leistungen, Projekte (Kurzkarten), Ablauf, Arbeitsprinzipien, Kontaktaufruf |
| `/leistungen/` | `/en/services/` | je Bereich: Beschreibung, typische Herausforderungen, Leistungen, Anwendungsfälle, für wen |
| `/projekte/` | `/en/projects/` | je Projekt: Ausgangssituation, Herausforderung, eigener Beitrag, Lösungsansatz, Technologien, Status |
| `/ueber-mich/` | `/en/about/` | Person hinter der Marke, Arbeitsweise |
| `/zusammenarbeit/` | `/en/how-we-work/` | fünf Schritte: Erstgespräch, Anforderungsklärung, Konzeption, Umsetzung, Prüfung und Übergabe |
| `/kontakt/` | `/en/contact/` | nur E-Mail (mailto), Hinweise für eine erste Anfrage |
| `/impressum/`, `/datenschutz/` (noindex) | `/en/legal-notice/`, `/en/privacy/` (noindex) | Vorlagen mit Platzhaltern |
| `/404.html` | `/en/404.html` | Fehlerseite |

## Marke und Logo

Vorlage: `assets/img/nahx-logo-vorlage.png` (Rasterbild 1672 × 941, geliefert 2026-10-25). Daraus wurden die
Buchstaben vermessen und als **echte Vektoren** nachgebaut, nicht verpackt:

| Datei | Verwendung |
|---|---|
| `nahx-logo.svg` | Hauptlogo für dunklen Grund (auch Open-Graph-Bild): Wortmarke (Silberverlauf `#F9F9F9` → `#C9C8C8`, A in Cyan `#02EEFB` → `#00A4F7`), TECHNOLOGIES als Strichbuchstaben, Linie |
| `nahx-logo-dunkel.svg` | dieselbe Geometrie mit dunklen Buchstaben für hellen Grund |
| `nahx-wortmarke.svg` | nur „NAHX“ |
| `favicon.svg`, `favicon.ico` (32/16), `apple-touch-icon.png` (180), `icon-512.png` | das Cyan-A auf Schwarz |
| `og-nahx.jpg` | Open-Graph-Bild 1200 × 630 aus dem Vektorlogo gerendert |

Im Seitenkopf und in der Fußzeile steht die Wortmarke inline (`WORTMARKE` in `build.py`, Buchstaben in
`currentColor`), daneben „Technologies“ als Text; unter 900 px nur die Wortmarke. Der Claim ist echter Text, nicht
Teil der SVG (für eine Claim-Fassung als Vektor fehlt ein Werkzeug, das Schrift in Pfade wandelt).

## Gestaltung (Visual Master Direction, 2026-10-26)

Filmische, fotografische Markenpräsentation: dunkle Farbräume (Schwarz `#05070B`, Navy `#0D121C`), kontrollierte
Cyan-Akzente aus dem Logo (`#17B8E6`, Verlauf `#00A4F7` → `#02EEFB` im A), Weiß und Hellgrau für Text, Outfit für
Überschriften, Source Sans 3 für Text. Redaktionelles Layout statt Kartenraster: Aufmacher mit großflächiger
Fotografie und dunkler Überlagerung für Lesbarkeit, Leistungsbereiche als wechselseitige Bild-Text-Reihen, Projekte
als Bildblöcke mit eigener Bildidentität, Foto-Bänder mit Überlagerung, Markenbühne mit der 3D-Szene.

**Fotografie**: sieben Fotografien von Unsplash unter der Unsplash License (kommerziell nutzbar, keine Namensnennung
verpflichtend, geprüft 2026-10-25; keine Unsplash+-Bilder). Fotografen und Quellen in `assets/img/foto/QUELLEN.md`
und im Bildnachweis der Fußzeile. Die Bilder zeigen Orte und Motive, keine Kundenprojekte. Je Bild drei bis vier
Breiten als WebP und JPEG (`<picture>` mit `srcset`/`sizes`), Aufmacherbild `eager` mit `fetchpriority="high"`,
alle übrigen `loading="lazy"`; Zuordnung über `bild` in den JSON-Dateien, Alt-Texte je Sprache in `site.json`.

**Bewegung**: einmaliges Einblenden beim Scrollen, leichte Parallaxe auf großen Bildern (nur `transform`,
`requestAnimationFrame`), Bildzoom beim Überfahren, Unterstreichung in der Navigation, Scroll-Hinweis im Aufmacher.
Bei `prefers-reduced-motion` entfällt alles davon.

**3D-Szene** (`assets/szene3d.js`, WebGL ohne Bibliothek) auf der Startseite in der Markenbühne „Das A steht für
den Anspruch“: Raymarching des NAHX-A als Körper aus dunklem Glasstein mit Mikrostruktur und leuchtenden Rissen,
Haupt- und Gegenlicht mit GGX-Glanz, Umgebungsreflexionen, weiche Schatten, Umgebungsverschattung, spiegelnder
Boden, zweites A in der Tiefe, Lichtnebel, Staub, Bloom, Farbsaum, Vignette, Filmkorn, zeitliche Glättung.
Reduzierte Auflösung (0,7 Desktop, 0,55 Handy), pausiert außerhalb des Bildes, Standbild bei reduzierter Bewegung,
ohne WebGL entfällt sie.

## Platzhalter und offene Punkte

- **Domain**: siehe oben.
- **E-Mail**: `email` in `de.json`/`en.json` ist die vorhandene Adresse `niklas.heinzmann@fsh-documentation.de` (Entscheidung: weiterverwenden). Steht kein `@` im Wert, wird er als sichtbarer Platzhalter ohne `mailto` gezeigt.
- **Impressum, Datenschutz**: Vorlagen mit Platzhaltern in eckigen Klammern (Name, Anschrift, Umsatzsteuer, Hosting-Anbieter, Rechtsgrundlage, Aufsichtsbehörde), `noindex`. Keine Rechtsberatung; vor dem Livegang prüfen.
- **Projekte**: nur geprüfte Kurzangaben mit Status; Technologien und Details folgen nach Freigabe. DocumentCheck & ComplianceCheck ist als „in Abstimmung mit FSH Documentation“ gekennzeichnet und wird nicht als eigenes Produkt dargestellt.
- **Reaktionszeit** „in der Regel innerhalb von zwei Werktagen“ auf der Kontaktseite ist eine Formulierung von 2026-10-25, keine Zusage aus dem Konzept; anpassen, falls sie nicht gelten soll.

## Veröffentlichen

`dist/` auf einen statischen Hoster laden (GitHub Pages, Cloudflare Pages, Netlify, Webspace). Pfade enden mit `/`
(Ordner mit `index.html`), `404.html` im Stamm wird von GitHub Pages, Cloudflare Pages und Netlify als Fehlerseite
genommen. Vor dem Livegang: Basis-URL setzen, Rechtstexte vervollständigen, ohne `--noindex` bauen und prüfen.
`.github/workflows/website.yml` kann als Vorlage dienen (Pfad `nahx/` statt `website/`).
