# Website-Relaunch FSH-Documentation (statisch)

Neue Website für fsh-documentation.com als statisches HTML: acht Seiten nach dem Seitenplan aus
`seo-audit/massnahmen/2026-09-21-phase-2.md` (Abschnitt 4), dazu Impressum, Datenschutz, AGB und
eine 404-Seite. Gestaltung nach dem Relaunch-Entwurf auf dem Design-Canvas (Desktop, Handy, Unterseite).
Alles, was auf Canva nicht ging, ist hier eingebaut: serverseitiges HTML mit Überschriften, Title und
Description je Seite, Canonical, Open Graph (inklusive `og:url` und `og:image`), JSON-LD, Sitemap,
robots.txt, Alt-Texte, lokale Schriften, komprimierte Bilder, Lazy Loading, kein externes Skript.

## Ordner

| Pfad | Zweck |
|---|---|
| `build.py` | baut die Seiten aus `inhalt/` nach `dist/` (nur Python 3.8+, keine Pakete) |
| `inhalt/site.json` | Firmendaten, Navigation, Reihenfolge der Seiten, Hosting-Variante, Basis-URL |
| `inhalt/<seite>.json` | Inhalt je Seite (Text, Abschnitte, Title, Description, Kontaktblock) |
| `assets/site.css` | Stylesheet, Farbschema hell/dunkel |
| `assets/fonts/` | Poppins und Source Sans 3 als WOFF2 (SIL Open Font License, Lizenztexte liegen dabei) |
| `assets/img/` | Logo, Icons, Porträt, Zahnräder-Foto, Open-Graph-Bild |
| `dist/` | **fertige Website zum Hochladen** (wird von `build.py` komplett neu erzeugt) |

## Bauen und prüfen

```bash
python3 website/build.py --pruefen
```

Baut `website/dist/` und prüft: genau eine h1 je Seite, Überschriftenfolge, Title bis 60 Zeichen,
Description 150–160 Zeichen, Alt-Attribut an jedem Bild, Canonical, JSON-LD, alle internen Links und
Anker, Sitemap vollständig. Fehler ergeben Exit-Code 1.

Vorschau ohne Webserver (relative Links, `index.html` per Doppelklick öffnen):

```bash
python3 website/build.py --relativ --ausgabe /tmp/vorschau
```

Weitere Schalter: `--basis-url https://…` (Canonical, Open Graph, Sitemap), `--hosting strato|cloudflare|github`
(Textvariante der Datenschutzerklärung, Standard aus `site.json`) und `--noindex` für den Testbetrieb
(alle Seiten `noindex, nofollow`, `robots.txt` sperrt, keine Sitemap; vor dem Livegang ohne den Schalter
neu bauen).

Der Workflow `.github/workflows/website.yml` baut und prüft bei jedem Push nach `main`, der `website/`
berührt. Er veröffentlicht auf GitHub Pages, sobald die Repository-Variable `WEBSITE_HOSTING` den Wert
`github` hat; Bau-Schalter für den Test kommen aus `WEBSITE_BUILD_ARGS` (zum Beispiel `--relativ --noindex`).
Die Schritte für den Livegang (Hosting, Testadresse, DNS, Search Console, Weiterleitung der .de) stehen
in `livegang.md` (auch als `livegang.pdf`).

Gerenderte Seite zusätzlich mit den Audit-Werkzeugen prüfen (wie beim Freitags-Audit):

```bash
python3 seo-audit/tools/onpage_check.py website/dist/index.html --url https://fsh-documentation.com/
```

## Seiten

| Pfad | Datei | Title (Zeichen) |
|---|---|---|
| `/` | `start.json` | FSH-Documentation – Technische Dokumentation Teltow (51) |
| `/betriebsanleitungen/` | `betriebsanleitungen.json` | Betriebsanleitung erstellen lassen \| FSH-Documentation (54) |
| `/ce-ukca-konformitaet/` | `ce-ukca-konformitaet.json` | Dokumentation für CE-/UKCA-Konformität \| FSH-Documentation (58) |
| `/risikobeurteilung/` | `risikobeurteilung.json` | Risikobeurteilung erstellen lassen \| FSH-Documentation (54) |
| `/medizinprodukte-mdr-ivdr/` | `medizinprodukte-mdr-ivdr.json` | Technische Dokumentation MDR/IVDR \| FSH-Documentation (53) |
| `/redaktionssysteme-st4/` | `redaktionssysteme-st4.json` | SCHEMA ST4: Einführung, Modularisierung \| FSH-Documentation (59) |
| `/dokumentencheck/` | `dokumentencheck.json` | Dokumentencheck: Anleitung prüfen lassen \| FSH-Documentation (60) |
| `/technische-dokumentation-berlin-brandenburg/` | `technische-dokumentation-berlin-brandenburg.json` | Technische Dokumentation Berlin-Brandenburg \| FSH Teltow (56) |
| `/impressum/`, `/datenschutz/`, `/agb/` | `impressum.json`, `datenschutz.json`, `agb.json` | Impressum \| FSH-Documentation usw. |
| `/404.html` | in `site.json` (`fehlerseite`) | noindex |

Die Pfade enden mit `/` (Ordner mit `index.html`), damit sie auf jedem Hoster ohne Konfiguration
funktionieren; der Seitenplan nennt sie ohne Schrägstrich, das ist dieselbe Seite.

## Inhalte pflegen

Jede Seite ist eine JSON-Datei. Textfelder sind HTML-Fragmente (`<strong>`, `<a>`, `<br>`, `<code>`
erlaubt); ein nacktes `&` wird beim Bau automatisch zu `&amp;`. Deutsche Anführungszeichen als „…“
schreiben, nicht mit dem ASCII-Zeichen `"` schließen (das beendet den JSON-String). Schlüssel mit
Unterstrich (`_hinweise`) sind Notizen und werden ignoriert.

Aufbau einer Seite: `pfad`, `typ` (`start`, `leistung`, `region`, `recht`), `menue` (Name in Fuß und
Pfadnavigation), `kurz` (Text für Verweiskarten), `title`, `description`, `kicker`, `h1`, `einleitung`,
`cta`, `seitenkarte` (Kasten neben der Einleitung), `abschnitte`, `kontakt`.

Abschnittsarten (`art`): `karten` (Raster mit h3, optional `link`), `text` (`inhalt`: Absätze als
String, `{"liste": […]}`, `{"nummern": […]}`, `{"h3": "…"}`, `{"links": […]}`), `band` (dunkles Band mit
`punkte`), `schritte` (Ablauf aus `site.json` oder eigene), `fragen` (FAQ, erzeugt FAQPage-JSON-LD),
`referenzen`, `zahlen`, `ueber` (Porträt plus Text), `bild` (Foto in voller Breite), `verwandt`
(Karten auf andere Seiten).

Seite entfernen: JSON löschen, Namen aus `seiten` und `leistungsseiten` in `site.json` streichen,
`build.py --pruefen` meldet alle Links, die noch auf die Seite zeigen.

## Veröffentlichen

Die Website ist hosterneutral. Drei Wege, alle ohne Änderung an den Dateien:

1. **STRATO-Webspace** (die .de-Domain und die E-Mail liegen schon dort): Inhalt von `dist/` per SFTP in
   das Webverzeichnis laden, `fsh-documentation.com` im STRATO-Kundenmenü auf dieses Verzeichnis
   zeigen lassen, „SSL erzwingen“ einschalten. Die mitgelieferte `.htaccess` setzt UTF-8, 404-Seite und
   Cache-Header. Datenschutzerklärung: Variante `strato`.
2. **Cloudflare Pages**: Repo verbinden, Build-Befehl `python3 website/build.py`, Ausgabeordner
   `website/dist`; oder `dist/` direkt hochladen. Domain in Cloudflare umziehen oder per CNAME
   anbinden. `site.json` auf `"hosting": "cloudflare"` stellen und neu bauen.
3. **GitHub Pages** (gewählt): der Workflow `.github/workflows/website.yml` veröffentlicht `dist/`, sobald
   die Repository-Variable `WEBSITE_HOSTING` auf `github` steht; Domain als Custom Domain eintragen.
   `"hosting": "github"` ist in `site.json` gesetzt. Schritte in `livegang.md`, Abschnitt 3.

Reihenfolge beim Umzug: Website hochladen und unter einer Testadresse prüfen → DNS der .com auf den
neuen Hoster → HTTPS prüfen → in der Search Console Sitemap `https://fsh-documentation.com/sitemap.xml`
einreichen → STRATO-Weiterleitung der .de auf die .com (Phase 2, Abschnitt 7a) → nächstes
Freitags-Audit abwarten (`seo-audit/`): Technik- und On-Page-Prüfung laufen dann gegen die neue Seite.

## Vor der Veröffentlichung zu entscheiden oder zu prüfen

Alle Punkte stehen auch als `_hinweise` in der jeweiligen JSON-Datei.

- **Rechtstexte** (Impressum, Datenschutz, AGB): keine Rechtsberatung, vor dem Livegang prüfen lassen.
  Eingearbeitet sind die Korrekturen aus Phase 2, Abschnitt 6: § 5 DDG, § 18 Abs. 2 MStV, OS-Plattform
  gestrichen, AGB § 7 ohne Platzhalter („im Angebot festgelegter Umfang“, alternativ Stundenzahl
  eintragen), AGB § 16 gekürzt, Logfile-Liste, LDA-URL, Bearbeiterhinweise entfernt. „Stand“-Daten
  beim Veröffentlichen setzen.
- **Hosting** (`site.json` → `hosting`): entschieden am 22.09.2026: `github` (GitHub Pages); die
  Datenschutzerklärung beschreibt GitHub als Hosting-Anbieter, der Zugriffsdaten in eigener
  Verantwortung protokolliert (Drittlandtransfer USA, DPF). Zwei Punkte aus der Rechtsprüfung vom
  22.09.2026 vor dem Livegang klären: (1) Die GitHub-Pages-Bedingungen verbieten, damit ein „online
  business“ zu betreiben; eine reine Unternehmens-Informationsseite ohne Shop und Formular ist nach dem
  Wortlaut nicht klar erfasst, GitHub hat das nie bestätigt. Beim GitHub-Support schriftlich bestätigen
  lassen und ablegen, sonst Variante `cloudflare` oder `strato` (Texte und Bau liegen bereit).
  (2) Ob das GitHub Data Protection Agreement für ein kostenloses Konto gilt, ist offen.
  Bei einem Wechsel des Hosters die Variante umstellen und neu bauen.
- **Hauptdomain**: `basis_url` ist `https://fsh-documentation.com` (Empfehlung aus Phase 2: .com
  bleibt, .de leitet um). Bei Wechsel auf die .de nur `basis_url` ändern und neu bauen.
- **Bildrechte**: Porträt und Zahnräder-Stockfoto stammen von der heutigen Seite; Lizenz und
  Einwilligung nicht belegt. Urheber im Impressum nennen, falls die Lizenz das verlangt.
- **Korrekturrunde vom 22.09.2026** (vier Prüfer: Fakten, Konsistenz, Sprache, Recht und Normen;
  117 Befunde, davon 155 Einzeländerungen eingearbeitet). Vom Betreiber zu bestätigen oder bewusst
  zurückzunehmen:
  - „Abnahmegarantie“ von der alten Seite ist in den AGB nicht definiert (Garantie hat Rechtsfolgen,
    § 276 BGB, DL-InfoV); jetzt „Abnahme nach vereinbarten Freigabekriterien und 30 Tage
    Service-Window inklusive (AGB § 6 und § 7)“. Alternativ die Garantie in den AGB definieren lassen.
  - „Auditfest ab der ersten Lieferung“ (alte Seite) heißt jetzt „Auditfähig ab der ersten Lieferung“,
    weil „auditfest“ das Bestehen von Audits verspricht.
  - „Erstreaktion binnen 24 h“ trägt jetzt den Zusatz „an Werktagen“, passend zu AGB § 7a.
  - Zusagen „per Video“ und „vor Ort“ auf der Regionalseite sind gestrichen (nicht belegt); nur nach
    Freigabe wieder aufnehmen. Ebenso gestrichen: „Kunden in Berlin, Potsdam und Brandenburg“
    (regionale Kunden sind nicht belegt, Phase 2, Abschnitt 4.8).
  - Referenz „Technologieunternehmen (AT)“: Die alte Seite nennt „rund 40 % schnellere
    Inhaltserstellung“ als Ergebnis, der Werdegang dasselbe Mandat als Vorbereitung mit „Ziel: >40 %“.
    Bestätigen, ob die 40 % gemessen wurden; sonst als Ziel formulieren.
  - Das verlinkte freelance.de-Profil nennt „Englisch (Grundkenntnisse)“, die Website liefert Englisch
    über das Expertennetzwerk; Profil angleichen oder Rollen auf der Website benennen.
  - Dokumentencheck: Ergebnisform ist allgemein beschrieben („Befunde nach Priorität mit
    Empfehlungen, Umfang und Form im Angebot“); konkretisieren, sobald festgelegt.
  - Einzugsgebiet in den strukturierten Daten (`site.json` → `einzugsgebiet`: Teltow, Potsdam, Berlin,
    Brandenburg, Deutschland) und „deutschlandweit“ in den Einleitungen sind plausibel, aber nicht
    aus der alten Seite belegt (Phase 2, Abschnitt 7e).
  - AGB: sprachliche Änderungen (§ 7 Überschrift, „Service-Window“, § 7 Abs. 1 Satzbau, § 10 „dessen“,
    § 18 Überschrift) sowie auf Anweisung vom 22.09.2026 die Leistungsaufzählung in § 1 Abs. 1 (an die
    Website angeglichen) und ein Rückfallwert in § 7 Abs. 1 lit. b („andernfalls bis zu insgesamt vier
    Stunden“, Vorschlagswert, zu bestätigen oder zu ändern). Prüfhinweise stehen in `agb.json` unter
    `_hinweise`, Datenschutz-Hinweise in `datenschutz.json`. Alles vom Rechtsprüfer bestätigen lassen
    (keine Rechtsberatung).
  - Auf Anweisung vom 22.09.2026 gestrichen: „auf Premium-Niveau“ (Einleitung der Startseite) und
    „Keine Buzzwords.“ (Über uns).
- **Kundennamen**: entschieden am 22.09.2026: keine Kundennamen; die Startseite nennt Projekte nur
  anonymisiert (Zeile „Aus dem Werdegang außerdem“ in `start.json`).
- **Seite Redaktionssysteme ST4**: entschieden am 22.09.2026: bleibt als eigene Seite.
- **Regionalseite**: entschieden am 22.09.2026: kurzer Title mit „FSH Teltow“ (56 Zeichen). Offen bleiben
  die Zusage „auf Wunsch auch persönlich vor Ort“ und der Link auf das Google-Unternehmensprofil,
  sobald es existiert.
- **Dokumentencheck**: Ergebnisform der Prüfung ist allgemein beschrieben (Befunde nach Priorität mit
  konkreten Empfehlungen; Umfang, Form und Termin im Angebot); konkretisieren, sobald festgelegt. Das
  interne Prüfwerkzeug wird nicht genannt.
- **Profile**: JSON-LD `sameAs` und Fußzeile enthalten nur das geprüfte freelance.de-Profil. Das
  LinkedIn-Profil steht in `site.json` unter `_same_as_unbestaetigt` und wird erst nach Bestätigung in
  `same_as` übernommen.
- **Maschinenverordnung**: Geltungsbeginn 20.01.2027 stammt aus Sekundärquellen (EUR-Lex war aus
  der Umgebung nicht abrufbar); Wortlaut der Pflichten zu digitalen Anleitungen vor Veröffentlichung
  am Verordnungstext prüfen.
- **Schriften**: Poppins und Source Sans 3 kommen aus dem Google-Fonts-Archiv, liegen aber lokal
  (keine Verbindung zu Google beim Aufruf; die Datenschutzerklärung sagt das so).

## Stand 22.09.2026

Erster Bau: 12 Seiten, `build.py --pruefen` ohne Fehler und Warnungen; Chromium-Prüfung Desktop
(1280 px) und Handy (390 px) ohne horizontalen Überlauf, hell und dunkel; Menü- und
Farbschema-Schalter getestet. Seitengrößen: Startseite rund 33 KB HTML, CSS 12 KB, Schriften 116 KB,
größtes Bild (Porträt) 108 KB JPEG bzw. 94 KB WebP.
