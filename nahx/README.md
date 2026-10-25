# NAHX Technologies – Website (statisch, zweisprachig)

Website zur persönlichen Marke NAHX Technologies, gebaut aus dem Website-Konzept vom 2026-10-25
(Claim „Technik verstehen. Lösungen schaffen.“ / „Understand Technology. Create Solutions.“).
Gleiche Bauweise wie `website/` (FSH-Documentation): Inhalte als JSON, ein Python-Skript ohne
Abhängigkeiten, fertige Dateien in `dist/`. Kein externes Skript, keine externen Schriften, kein Tracking.

## Ordner

| Pfad | Zweck |
|---|---|
| `build.py` | baut die Seiten aus `inhalt/` nach `dist/` (Python 3.8+, keine Pakete) |
| `inhalt/site.json` | gemeinsame Daten: Name, Basis-URL, Sprachen mit Wurzelpfad, Reihenfolge der Seiten |
| `inhalt/de.json`, `inhalt/en.json` | alle Texte je Sprache, gleiche Seitenschlüssel (`start`, `leistungen`, `projekte`, `ueber-mich`, `zusammenarbeit`, `kontakt`, `impressum`, `datenschutz`) |
| `assets/site.css` | Stylesheet, Farbschema hell/dunkel (automatisch oder per Schalter) |
| `assets/fonts/` | Poppins und Source Sans 3 als WOFF2 (SIL Open Font License, Lizenztexte liegen dabei) |
| `assets/img/` | `nahx-wortmarke.svg` (helle Wortmarke, Buchstaben als Pfade, A in Cyan `#22B8E0`), `favicon.svg`, `favicon.ico` (32/16 px), `apple-touch-icon.png` (180 px), `icon-512.png`, `og-nahx.jpg` (1200 × 630) |
| `dist/` | **fertige Website zum Hochladen** (wird von `build.py` komplett neu erzeugt) |

## Bauen und prüfen

```bash
python3 nahx/build.py --pruefen
```

Baut `nahx/dist/` und prüft: genau eine h1 je Seite, Überschriftenfolge, Title bis 60 Zeichen,
Description 150–160 Zeichen, Alt-Attribut an jedem Bild, Canonical, hreflang (de, en, x-default),
JSON-LD, alle internen Links und Anker, Sitemap vollständig. Fehler ergeben Exit-Code 1.

Weitere Schalter: `--relativ --ausgabe /tmp/vorschau` (Vorschau ohne Webserver, `index.html` per Doppelklick),
`--basis-url https://…` (Canonical, hreflang, Sitemap), `--noindex` für den Testbetrieb (alle Seiten
`noindex, nofollow`, `robots.txt` sperrt, keine Sitemap; vor dem Livegang ohne den Schalter neu bauen).

## Seiten

| Deutsch | English |
|---|---|
| `/` | `/en/` |
| `/leistungen/` | `/en/services/` |
| `/projekte/` | `/en/projects/` |
| `/ueber-mich/` | `/en/about/` |
| `/zusammenarbeit/` | `/en/how-we-work/` |
| `/kontakt/` | `/en/contact/` |
| `/impressum/` (noindex) | `/en/legal-notice/` (noindex) |
| `/datenschutz/` (noindex) | `/en/privacy/` (noindex) |
| `/404.html` | `/en/404.html` |

Jede Seite verweist per `hreflang` auf ihre Entsprechung in der anderen Sprache; der Sprachschalter im Kopf
führt auf dieselbe Seite in der anderen Sprache. Die Farbschema-Wahl wird nur lokal im Browser gespeichert.

## Marke und Logo

Die Wortmarke „NAHX“ besteht aus vier geometrischen Buchstaben als SVG-Pfade (kein Schriftbedarf), das A in
Cyan `#22B8E0`, die übrigen Buchstaben in `currentColor`. Im Seitenkopf und in der Fußzeile wird sie inline
ausgegeben (`WORTMARKE` in `build.py`), damit sie im hellen und dunklen Schema mitfärbt; der Kopf ist fest
dunkel. `assets/img/nahx-wortmarke.svg` ist die eigenständige helle Fassung für dunklen Grund. Favicon ist
das cyanblaue A auf Dunkelblau; PNG, ICO und Open-Graph-Bild wurden daraus gerendert. Der Zusatz
„Technologies“ steht als Text in Poppins daneben und wird unter 1100 px ausgeblendet.

## Platzhalter und offene Entscheidungen

Alles in eckigen Klammern ist bewusst sichtbarer Platzhalter und wird vor dem Livegang ersetzt:

- **Domain**: `basis_url` in `site.json` steht auf `https://nahx.example` (Entscheidung: später). Vor dem Livegang ersetzen oder mit `--basis-url` bauen; interne Links sind domainunabhängig.
- **E-Mail-Adresse**: `email` in `de.json` und `en.json`, derzeit die vorhandene Adresse `niklas.heinzmann@fsh-documentation.de` (Entscheidung: vorerst weiterverwenden). Solange kein `@` enthalten ist, würde der Text als Platzhalter ohne `mailto`-Link gezeigt. Impressum und Datenschutz nennen dieselbe Adresse im Text.
- **Kontakt**: nur per E-Mail (Entscheidung), kein Formular, kein Versanddienst, keine Eingabeverarbeitung auf der Website.
- **Impressum und Datenschutz**: Vorlagen mit Platzhaltern (Name, Anschrift, USt, Hosting-Anbieter, Rechtsgrundlage), als `noindex` markiert. Keine Rechtsberatung; vor dem Livegang prüfen.
- **Projekte**: Nur die drei Kurzbeschreibungen aus dem Konzept. Details zu DocumentCheck & ComplianceCheck kommen erst nach Prüfung von Vertraulichkeit, Rechten und Zuordnung zu FSH Documentation.

## Veröffentlichen

`dist/` auf einen beliebigen statischen Hoster laden (GitHub Pages, Cloudflare Pages, Netlify, STRATO-Webspace).
Die Pfade enden mit `/` (Ordner mit `index.html`) und funktionieren ohne Serverkonfiguration; `404.html` im
Stamm wird von GitHub Pages, Cloudflare Pages und Netlify automatisch als Fehlerseite genommen.
Für ein GitHub-Pages-Deployment kann `.github/workflows/website.yml` als Vorlage dienen (Pfad `nahx/` statt `website/`).
