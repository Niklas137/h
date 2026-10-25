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
| `assets/img/` | Platzhalter-Monogramm „N“ als Logo und Favicon (SVG) |
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

## Platzhalter und offene Entscheidungen

Alles in eckigen Klammern ist bewusst sichtbarer Platzhalter und wird vor dem Livegang ersetzt:

- **Domain**: `basis_url` in `site.json` steht auf `https://nahx.example`; vor dem Livegang ersetzen oder mit `--basis-url` bauen.
- **E-Mail-Adresse**: `email` in `de.json` und `en.json`. Solange kein `@` enthalten ist, wird der Text als Platzhalter ohne `mailto`-Link gezeigt.
- **Kontaktformular**: Felder stehen (Name, Unternehmen optional, E-Mail, Thema, Nachricht), der Senden-Knopf ist deaktiviert, ein Hinweis verweist auf die E-Mail. Für den Versand braucht es einen Dienst (statisches Hosting hat keinen Server) oder ein kleines Backend; die Wahl bestimmt den Text der Datenschutzerklärung.
- **Impressum und Datenschutz**: Vorlagen mit Platzhaltern, als `noindex` markiert. Keine Rechtsberatung; vor dem Livegang prüfen (siehe `website/pruefpaket-rechtstexte.md` als Muster für die Prüfung).
- **Logo**: Das Monogramm ist ein Platzhalter, bis eine Wort-Bild-Marke vorliegt.
- **Projekte**: Nur die drei Kurzbeschreibungen aus dem Konzept. Details zu DocumentCheck & ComplianceCheck kommen erst nach Prüfung von Vertraulichkeit, Rechten und Zuordnung zu FSH Documentation.
- **Open-Graph-Bild**: noch keines hinterlegt (`og:image` wird nicht ausgegeben), bis ein Bild vorliegt.

## Veröffentlichen

`dist/` auf einen beliebigen statischen Hoster laden (GitHub Pages, Cloudflare Pages, Netlify, STRATO-Webspace).
Die Pfade enden mit `/` (Ordner mit `index.html`) und funktionieren ohne Serverkonfiguration; `404.html` im
Stamm wird von GitHub Pages, Cloudflare Pages und Netlify automatisch als Fehlerseite genommen.
Für ein GitHub-Pages-Deployment kann `.github/workflows/website.yml` als Vorlage dienen (Pfad `nahx/` statt `website/`).
