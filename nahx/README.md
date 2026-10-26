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
| `assets/site.css` | Designsystem „Leinwand · Mint“: Midnight Green/Schwarz, Mint-Akzent, Outfit und Source Sans 3 lokal (`@font-face`) |
| `assets/fonts/` | Outfit (variabel, TTF) für Überschriften und Source Sans 3 (WOFF2) für Text, beide SIL Open Font License, Lizenztexte liegen dabei |
| `assets/img/` | Logo-Satz (siehe unten), Favicons, Open-Graph-Bild, Logo-Vorlage |
| `assets/img/foto/` | Fotografien in responsiven Varianten, `QUELLEN.md` mit Fotografen und Lizenz |
| `assets/szene3d.js` | 3D-Szene der Markenbühne (WebGL) |
| `werkzeuge/foto_mint.py` | einmalige Mint-Farbstimmung der Fotos (am 2026-10-26 angewendet, nicht erneut laufen lassen) |
| `werkzeuge/marke_rendern.py` | rendert OG-Bild, App-Icon, Apple-Touch-Icon und Favicon aus den SVGs (Playwright + Pillow) |
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

| English (Startsprache) | Deutsch | Inhalt |
|---|---|---|
| `/` | `/de/` | Flug durch A-Portale (Aufmacher, drei Bereiche, Ansatz), drei Einstiegsangebote, Projektbühne, Stimmen (Platzhalter), Ablauf, 3D-Markenbühne, Kontaktband |
| `/services/` | `/de/leistungen/` | je Bereich: Beschreibung, typische Herausforderungen, Leistungen, Anwendungsfälle, für wen |
| `/projects/` | `/de/projekte/` | je Projekt: Ausgangssituation, Herausforderung, eigener Beitrag, Lösungsansatz, Technologien, Status |
| `/about/` | `/de/ueber-mich/` | Person hinter der Marke, Porträt-Block (Platzhalter), Arbeitsweise |
| `/how-we-work/` | `/de/zusammenarbeit/` | fünf Schritte: Erstgespräch, Anforderungsklärung, Konzeption, Umsetzung, Prüfung und Übergabe |
| `/contact/` | `/de/kontakt/` | nur E-Mail (mailto), weitere Wege als Platzhalter, Hinweise für eine erste Anfrage |
| `/legal-notice/`, `/privacy/` (noindex) | `/de/impressum/`, `/de/datenschutz/` (noindex) | mit markierten Testdaten |
| `/404.html` | `/de/404.html` | Fehlerseite |

Seit 2026-10-26 ist Englisch Startsprache (Zielmarkt außerhalb Deutschlands); die Reihenfolge in `site.json` → `sprachen`
bestimmt Startsprache und `x-default`.

### Testdaten

Bis alles feststeht, stehen Testwerte in `<mark class="test">…</mark>` (gestrichelt umrandet, hochgestelltes „Test“).
Solange `site.json` einen Schlüssel `testdaten` hat, zeigt jede Seite unten zusätzlich einen Hinweis. Zum Livegang:
alle `<mark class="test">` in `inhalt/*.json` (dort als `class=\"test\"` maskiert) durch echte Angaben ersetzen und `testdaten` aus `site.json` löschen.
Neue Abschnittstypen: `angebote` (Karten mit Rahmen und Link), `stimmen` (Rückmeldungen), `portraet` (Porträt mit Fakten),
`assistent` (Chat im Handy, siehe unten);
Kontakt kennt `wege` (weitere Kontaktwege).

## Marke und Logo

Vorlage: `assets/img/nahx-logo-vorlage.png` (Rasterbild 1672 × 941, geliefert 2026-10-25). Daraus wurden die
Buchstaben vermessen und als **echte Vektoren** nachgebaut, nicht verpackt:

| Datei | Verwendung |
|---|---|
| `nahx-logo.svg` | Hauptlogo für dunklen Grund (auch Open-Graph-Bild): Wortmarke (Silberverlauf `#F9F9F9` → `#C9C8C8`, A in Mint `#2BFFD3` → `#00C99A`), TECHNOLOGIES als Strichbuchstaben, Linie |
| `nahx-logo-dunkel.svg` | dieselbe Geometrie für hellen Grund: Buchstaben Midnight Green `#06130F`, A in dunklerem Mint `#00C99A` → `#008F6C` |
| `nahx-wortmarke.svg` | nur „NAHX“ |
| `favicon.svg`, `favicon.ico` (32/16), `apple-touch-icon.png` (180), `icon-512.png` | das Mint-A auf Schwarz (Rasterfassungen mit `werkzeuge/marke_rendern.py`) |
| `og-nahx.jpg` | Open-Graph-Bild 1200 × 630 aus dem Vektorlogo gerendert |

Im Seitenkopf und in der Fußzeile steht die Wortmarke inline (`WORTMARKE` in `build.py`, Buchstaben in
`currentColor`), daneben „Technologies“ als Text; unter 900 px nur die Wortmarke. Der Claim ist echter Text, nicht
Teil der SVG (für eine Claim-Fassung als Vektor fehlt ein Werkzeug, das Schrift in Pfade wandelt).

## Gestaltung („Leinwand · Mint“, nach Markenboard 2026-10-26)

Umstellung am 2026-10-26 von Cyan auf **Mint** nach dem Markenboard „Hauptlogo · Variante 1 · Clean Tech“
(Entscheidung Niklas: klar unterscheidbar von FSH Documentation, deren Website Blau `#1B63A8`/`#43AEE8` nutzt).
Wunsch dazu: **ohne Gebäude** – das Gebäudefoto (Kopenhagen) ist entfernt.

Farben: Grund `#030907`, Fläche `#06110D`/`#0A1713`, Electric Mint `#00F0BE` (Akzent, Taste), Soft Neon Mint
`#8CFFDA` (Hover), Mint Glow `#E8FFF7`, Deep Teal Gray `#34524A`, Midnight Green `#06130F`, Text `#F2FAF7`,
Grau `#C2D1CB` und `#8FA59C`. Kontraste (WCAG): Text 18,9 : 1, Grau 12,7 : 1 und 7,7 : 1, Mint auf Grund 13,6 : 1,
Text auf Mint-Taste 12,8 : 1. Das Board nennt Electric Mint als `#00FFA3`, zeigt im Bild aber `#00F2C0`–`#00F8C2`;
übernommen ist der sichtbare Ton.

Aufbau: Kicker in Versalien (auf der Startseite der Claim), kräftige Überschriften in normaler Schreibweise
(Outfit 600), Akzentwort in Mint über `<em>` im Text (`Komplexe Technik. <em>Klare Lösungen.</em>`), Einleitung
unter der Überschrift, gefüllte Mint-Taste plus Kontur-Taste, Mint-Textlinks „Mehr erfahren →“. Startseite:
Aufmacher (Lichtleiter-Foto), **Leistungskarten** (`typ: leistungskarten`: Foto, Mint-Piktogramm im Kreis, Titel, Satz,
Link; ganze Karte klickbar, Lichtkante beim Überfahren), Projektbühne, **Ablauf** (`typ: ablauf`: Foto links,
Leitsatz „Verstehen. Konzipieren. <em>Umsetzen.</em> Prüfen.“, fünf Schritte mit großen Mint-Ziffern rechts),
Prinzipien, 3D-Markenbühne (Mint), Kontaktband mit Mint-Leuchten. Unterseiten behalten die Vollbild-Leinwand mit
Glaskarte. Nicht übernommen aus dem Board: das Gebäude, der Folienzähler „01 / 03“ (es gibt keinen Slider).

**Flug durch A-Portale** (Startseite, 2026-10-26, Wunsch Niklas: „mehrere Ebenen, durch jede schweben, eine
krasse Website wie im Video“; Motiv gewählt: A-Portale). `start.flug` in `de.json`/`en.json` ersetzt dort den
Aufmacher; gebaut von `Bau.flug()` in `build.py`, gesteuert in `assets/bewegung.js`. Eine klebende Bühne mit
CSS-Perspektive (1000 px), die Kamera fährt beim Scrollen in die Tiefe (`FLUG_TIEFE` = 1800 px je Szene) und wird
weich nachgeführt (Schweben). Fünf Szenen: Aufmacher, Technical Documentation, Software & Web Applications,
Automation & AI, Ansatz mit Licht am Ende. Jede Ebene hat eine eigene Tiefe: Text, Foto-Tafel (Glas, Lichtkante,
Tiefenunschärfe in der Ferne), A-Portal aus der Logo-Geometrie (Vorder- und Hinterkante, Lichthof), Lichtbahnen
an Boden und Decke, Staub in zehn Tiefen. Die Kamera verweilt an jeder Szene und gleitet dazwischen zügiger durch
das Portal; Maus und Finger haben keinen Einfluss (Wunsch 2026-10-26). Anzeige unten rechts: Szene „01 / 05“, Name, Fortschrittslinie.
Tastatur: Fokus in einer Szene fährt die Kamera dorthin. Ohne JavaScript oder bei `prefers-reduced-motion`
stehen dieselben Inhalte als normale Abschnitte untereinander (Foto neben Text). Der Scroll-Snap der Startseite ist
deshalb entfernt. Die Leistungskarten (`typ: leistungskarten`) bleiben als Abschnittstyp erhalten, stehen aber nicht
mehr auf der Startseite.

**Fotografie**: sechs Fotografien von Unsplash (plus eine gespiegelte Fassung) unter der Unsplash License (kommerziell nutzbar, keine Namensnennung
verpflichtend, geprüft 2026-10-25; keine Unsplash+-Bilder). Fotografen und Quellen in `assets/img/foto/QUELLEN.md`
und im Bildnachweis der Fußzeile. Die Bilder zeigen Orte und Motive, keine Kundenprojekte. Je Bild drei bis vier
Breiten als WebP und JPEG, alle in Mint-Lichtstimmung (`werkzeuge/foto_mint.py`) (`<picture>` mit `srcset`/`sizes`), Aufmacherbild `eager` mit `fetchpriority="high"`,
alle übrigen `loading="lazy"`; Zuordnung über `bild` in den JSON-Dateien, Alt-Texte je Sprache in `site.json`.

**Bewegung** (`assets/bewegung.js`, ohne Bibliothek): ein Scroll-Takt setzt je Szene den Fortschritt `--p`, der Rest
ist CSS. Eigene Bewegungssprache: der Aufmacher bleibt festgeklemmt, die nächste Szene schiebt sich wie ein Vorhang
darüber, während Text und Foto des Aufmachers leicht zurückweichen; Überschriften laufen Zeile für Zeile aus der
Unschärfe scharf ein (Schärfe-Einlauf, passend zu „Technik verstehen“); Fotos der Szenen ziehen mit dem Scrollen,
Leistungskarten heben sich beim Überfahren mit Mint-Lichtkante und Bildzoom; Zahlen in Glaskarten zählen einmal hoch; die Projektmarkierungen erscheinen nacheinander (Punkt, gezeichnete
Linie, Glaskarte); ein Inspektionslicht folgt dem Zeiger über Fotoszenen und hellt eine weiche Stelle auf (nur mit
Maus, nie bei Touch); Seitenwechsel blenden über (View Transitions, wo der Browser es kann). Keine Dauerbewegung:
der einzige Pulsring der Markierungen läuft dreimal und stoppt. Bei `prefers-reduced-motion` ist alles davon aus,
Zahlen stehen sofort, der Aufmacher klemmt nicht, kein Scroll-Snap.

**3D-Szene** (`assets/szene3d.js`, WebGL ohne Bibliothek) auf der Startseite in der Markenbühne „Das A steht für
den Anspruch“: Raymarching des NAHX-A als Körper aus dunklem Glasstein mit Mikrostruktur und leuchtenden Rissen,
Haupt- und Gegenlicht mit GGX-Glanz, Umgebungsreflexionen, weiche Schatten, Umgebungsverschattung, spiegelnder
Boden, zweites A in der Tiefe, Lichtnebel, Staub, Bloom, Farbsaum, Vignette, Filmkorn, zeitliche Glättung.
Seit 2026-10-26 („Logo schärfer, Farben stärker“): Auflösung nach Pixeldichte statt fest 0,7/0,55 (Retina-Desktop
1,25-fach, Handy 1,0-fach, Obergrenze 3,2 bzw. 1,4 Mio. Pixel), regelt bei Ruckeln herunter und bei Reserve
vorsichtig hoch; Mint-Kontur auf Vorder- und Rückseite des A wie im Logo, kräftigere Risse, ACES-Tonkurve, weniger
Nachziehen, Farbsaum und Korn, Lichtsaum nur noch vom A (Boden und Hintergrund bleiben dunkel). Pausiert außerhalb
des Bildes, Standbild bei reduzierter Bewegung, ohne WebGL entfällt sie. Nachgeschärft am selben Tag („Logo zappelt, bewegt
sich mit der Maus; Linien dezenter“): kein Einfluss von Maus, Finger oder Scrollen mehr, das A pendelt ruhig von selbst
(±31°) und schwebt leicht; kein Pixelversatz pro Bild, kein Filmkorn, Auflösung wird nur noch höchstens zweimal
abgesenkt und nie wieder angehoben (kein Springen); Risse und Kontur dezenter, auf den Seitenflächen kaum Risse.

## Platzhalter und offene Punkte

- **Domain**: siehe oben.
- **E-Mail**: `email` in `de.json`/`en.json` ist die vorhandene Adresse `niklas.heinzmann@fsh-documentation.de` (Entscheidung: weiterverwenden). Steht kein `@` im Wert, wird er als sichtbarer Platzhalter ohne `mailto` gezeigt.
- **Impressum, Datenschutz**: mit markierten Testdaten (Anschrift, Telefon, E-Mail, Umsatzsteuer, Hosting-Anbieter, Speicherdauer, Rechtsgrundlage, Aufsichtsbehörde), `noindex`. Keine Rechtsberatung; vor dem Livegang echte Angaben eintragen und prüfen lassen.
- **Projekte**: nur geprüfte Kurzangaben mit Status; Technologien und Details folgen nach Freigabe. DocumentCheck & ComplianceCheck ist als „in Abstimmung mit FSH Documentation“ gekennzeichnet und wird nicht als eigenes Produkt dargestellt.
- **Reaktionszeit** „in der Regel innerhalb von zwei Werktagen“ auf der Kontaktseite ist eine Formulierung von 2026-10-25, keine Zusage aus dem Konzept; anpassen, falls sie nicht gelten soll.

## Veröffentlichen

`dist/` auf einen statischen Hoster laden (GitHub Pages, Cloudflare Pages, Netlify, Webspace). Pfade enden mit `/`
(Ordner mit `index.html`), `404.html` im Stamm wird von GitHub Pages, Cloudflare Pages und Netlify als Fehlerseite
genommen. Vor dem Livegang: Basis-URL setzen, Rechtstexte vervollständigen, ohne `--noindex` bauen und prüfen.
`.github/workflows/website.yml` kann als Vorlage dienen (Pfad `nahx/` statt `website/`).

## Chat im Handy (`assets/assistent.js`)

Abschnitt `assistent` zeigt Text und ein Handy, in das man direkt schreibt; unter 700 px öffnet es sich bildschirmfüllend.
Seiten ohne den Abschnitt bekommen einen Chat-Knopf und ein schwebendes Handy. Texte und Demo-Antworten stehen in
`inhalt/<sprache>.json` → `assistent` (`texte`, `demo.wissen` mit `stichworte`, `antwort`, `chips`, optional `kalender`;
`=wort` heißt ganzes Wort, sonst Wortanfang; `{{test:…}}` markiert Testwerte in einer Antwort).
`site.json` → `assistent.api` leer = Demo ohne Server. Mit Adresse eines Assistenten nach dem Protokoll des FSH-Assistenten
(`GET` → `{bereit}`, `POST {sitzung, nachricht, sprache}` → `{antwort, kalender}`, `GET …/termine?sprache=`) antwortet die KI;
der Server muss die NAHX-Domain als Herkunft zulassen.

## Startseite nach FORGE-Video und Effekte (`assets/effekte.js`, 2026-10-26)

Neue Abschnittstypen: `bildkarte` (bild, kicker, h2, text), `galerie` (kicker, h2, text, ende{h3, text, link}; Karten kommen
aus der Projektliste), `stapel` (kicker, h2, tafeln[{wort, titel, text}]), `zahlen` (kicker, h2, karten[{zahl, einheit, text,
ring 0–1, hervor}]), `abschluss` (kicker, h2, text, cta, cta2, riese, riese_bild), `wortbuehne` (kicker, titel, woerter).
Jede Szene hat eine ruhige Fassung ohne JavaScript und bei reduzierter Bewegung; effekte.js schaltet die bewegte Fassung
mit Klassen (`.bk-an`, `.gl-an`, `.wb-an`, `.fx`) zu. Nur 2D-Transformationen, damit Handys nicht überlastet werden.
