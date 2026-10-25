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
| `assets/site.css` | Designsystem: Schwarz/Navy, Cyan-Akzent, Poppins und Source Sans 3 lokal |
| `assets/fonts/` | Poppins 600/700 und Source Sans 3 als WOFF2 (SIL Open Font License, Lizenztexte liegen dabei) |
| `assets/img/` | Logo-Satz (siehe unten), Favicons, Open-Graph-Bild, Logo-Vorlage |
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
| `nahx-logo.svg` | Hauptlogo für dunklen Grund: Wortmarke (Silberverlauf `#F9F9F9` → `#C9C8C8`, A in Cyan `#02EEFB` → `#00A4F7`), TECHNOLOGIES als Strichbuchstaben, Cyan-Linie |
| `nahx-logo-dunkel.svg` | dieselbe Geometrie mit dunklen Buchstaben für hellen Grund |
| `nahx-wortmarke.svg` | nur „NAHX“ |
| `favicon.svg`, `favicon.ico` (32/16), `apple-touch-icon.png` (180), `icon-512.png` | das Cyan-A auf Schwarz |
| `og-nahx.jpg` | Open-Graph-Bild 1200 × 630 aus dem Vektorlogo gerendert |

Im Seitenkopf und in der Fußzeile steht die Wortmarke inline (`WORTMARKE` in `build.py`, Buchstaben in
`currentColor`), daneben „Technologies“ als Text; unter 900 px nur die Wortmarke. Der Claim ist echter Text, nicht
Teil der SVG (für eine Claim-Fassung als Vektor fehlt ein Werkzeug, das Schrift in Pfade wandelt).

## Gestaltung

Schwarz `#05070C` und Navy `#0A0F1A`/`#0E1422`, Cyan `#00C2F8` nur als Akzent (Links, Kicker, Buttons, Piktogramme),
Text Weiß `#F4F6F8` und Hellgrau `#AEB8C6`. Poppins für Überschriften, Source Sans 3 für Text. Dezentes Raster im
Aufmacher, ein statisches Diagramm der drei Bereiche, Linien-Piktogramme. Einzige Bewegung: Inhalte blenden beim
ersten Erscheinen einmal weich ein; bei `prefers-reduced-motion` gar nicht. Keine Dauer-Animationen, kein Glühen,
kein Korn.

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
