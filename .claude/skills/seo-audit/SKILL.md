---
name: seo-audit
description: SEO-Audit der Website von FSH-Documentation (fsh-documentation.com und .de). Prüft Erreichbarkeit, Technik, On-Page, Sichtbarkeit im Suchindex, Marke und lokale Einträge, vergleicht mit dem letzten Lauf und erzeugt Bericht-JSON, beide PDFs und den Verlauf unter seo-audit/. Verwenden, wenn der Nutzer „SEO-Audit" schreibt, die Freitags-Routine feuert oder ein SEO-Status, Sichtbarkeitsbericht oder eine Prüfung der Website gewünscht ist.
argument-hint: "[optional: freitag-0730 | freitag-1600 | manuell]"
allowed-tools: Read, Glob, Grep, Write, Edit, WebSearch, WebFetch, ToolSearch, PushNotification, Bash(date:*), Bash(mkdir:*), Bash(ls:*), Bash(curl:*), Bash(python3 seo-audit/tools/onpage_check.py:*), Bash(python3 seo-audit/tools/render_report.py:*), Bash(git pull:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*)
---

# SEO-Audit für FSH-Documentation

Du prüfst die Website von FSH-Documentation und schreibst das Ergebnis als Bericht-JSON, aus der
`seo-audit/tools/render_report.py` den A4-Bericht und die einseitige Kurzfassung erzeugt. Jeder Lauf
wird mit dem vorherigen verglichen. Alle Parameter stehen fest. Nicht nachfragen.

## Feste Parameter

- Website: `https://fsh-documentation.com/` (Startseite laut Suchindex). Zweitdomain
  `fsh-documentation.de` (E-Mail-Domain der Firma, Stand 19.09.2026 ohne indexierte Inhalte).
- Firma: FSH-Documentation UG (haftungsbeschränkt), Bäckerstraße 2 D, 14513 Teltow. Technische
  Dokumentation, CE-/UKCA-Konformität, Risikobeurteilung, Normenmanagement, ST4.
- Zielmarkt: Deutschland, regional Teltow, Potsdam, Berlin, Brandenburg.
- Kernbegriffe (feste Abfragen, siehe Prüfkatalog): technische Dokumentation, Betriebsanleitung,
  CE-Konformität, technische Redaktion, jeweils mit und ohne Region.
- Beobachtete Wettbewerber (nur als Vergleich, nie als Empfehlung): mt-redaktion.de,
  ce-koordination.de, unique-doc.de, wiessneth.de, kerntecdoc.com, winklergmbh.de, dogrel.com.
- Ausgabe: Bericht-JSON in `seo-audit/berichte/`, PDFs in `seo-audit/`, Zeile in
  `seo-audit/verlauf.md`.

## Dateien (vor jedem Lauf lesen)

| Datei | Inhalt |
|---|---|
| `seo-audit/README.md` | Überblick, Parameter, Aufbau der Routine |
| `seo-audit/verlauf.md` | eine Zeile pro Lauf: Erreichbarkeit, Indexstand, Befunde, Änderungen |
| `seo-audit/berichte/` | eine JSON pro Lauf; die alphabetisch letzte ist der Vergleichsstand |
| `seo-audit/tools/render_report.py` | prüft die JSON (`--check`) und erzeugt beide PDFs; Feldliste im Kopf der Datei |
| `seo-audit/tools/onpage_check.py` | liest eine gespeicherte HTML-Seite und gibt die On-Page-Merkmale als JSON aus |

## Ablauf

1. **Lauf bestimmen:** `TZ=Europe/Berlin date "+%F %H:%M %A"`. Kennung aus dem Auftrag:
   `freitag-0730` (Wochenaudit), `freitag-1600` (Zwischenstand), sonst `manuell`. Dateiname
   `seo-audit/berichte/JJJJ-MM-TT-<kennung>.json`; existiert er schon, `-2`, `-3` anhängen.
   In der Routine-Session vorher `git pull --ff-only origin main`.
2. **Vergleichsstand laden:** die alphabetisch letzte JSON in `seo-audit/berichte/` (beim Lauf
   `freitag-1600` der `freitag-0730`-Lauf desselben Tages, falls vorhanden). Sie liefert die
   Befund-IDs, die Formulierungen und die Zahlen, gegen die verglichen wird.
3. **Erreichbarkeit prüfen** (Befehle im Prüfkatalog). Antwortet der Proxy mit `000` oder `403`
   beim Verbindungsaufbau, ist der Abruf gesperrt: Technik und On-Page bleiben „offen“, und der
   Prüfumfang nennt das ausdrücklich. Keine Umgehung über fremde Dienste.
4. **Technik** (nur bei Erreichbarkeit): robots.txt, sitemap.xml, Weiterleitungen http→https,
   www und Zweitdomain, Antwortzeit, 404-Verhalten, Stichprobe der Sitemap-URLs.
5. **On-Page** (nur bei Erreichbarkeit): Startseite und bis zu zehn Unterseiten speichern und
   mit `onpage_check.py` auswerten. Bewerten: Title mit Marke, Leistung und Ort; Meta-Description;
   genau eine H1; Alt-Texte; Canonical; JSON-LD (Organization/LocalBusiness); Links zu Impressum
   und Datenschutz.
6. **Suchindex:** die festen Abfragen des Prüfkatalogs mit WebSearch ausführen (fehlt das
   Werkzeug, per ToolSearch `select:WebSearch` laden). Je Abfrage festhalten: erscheint eine URL
   von fsh-documentation.com oder .de, welche, mit welchem Titel und Snippet, welche Wettbewerber
   stehen davor. Der Operator `site:` wird nicht zuverlässig beachtet – nach den URLs in den
   Treffern urteilen, nicht nach der Zusammenfassung des Werkzeugs.
7. **Marke und lokale Einträge:** Abfragen zum Firmennamen; Einträge (Handelsregister,
   Creditreform, freelance.de, Branchenbuch, Google-Unternehmensprofil, falls sichtbar) und die
   Schreibweise von Name, Adresse und Telefon (NAP) vergleichen.
8. **Bewerten und vergleichen:** Prüfstatus je Bereich (Indexierung, Kernbegriffe, Marke,
   Domains, Lokale Signale, Technik, On-Page; ohne Seitenabruf die letzten beiden als eine Zeile
   „Technik & On-Page“ mit Status `offen`). Befunde aus dem Vergleichsstand übernehmen und
   `entwicklung` setzen: `unverändert`, `verbessert`, `erledigt` (ein erledigter Befund erscheint
   genau noch einmal, danach entfällt er), neue Befunde mit `neu` und fortlaufender ID (IDs nie neu
   vergeben). `veraenderungen` listet jede konkrete Abweichung zum Vergleichsstand; gibt es keine,
   bleibt die Liste leer, und die Zusammenfassung sagt „keine Änderung gegenüber <Datum, Lauf>“.
9. **JSON schreiben** nach der Feldliste im Kopf von `render_report.py`; Vorlage ist der
   Vergleichsstand. Texte deutsch, jede Aussage mit Beleg, nichts schätzen, nichts erfinden; ohne
   Seitenabruf steht bei Inhalten „laut Suchindex“. Dann
   `python3 seo-audit/tools/render_report.py <json> --check` bis keine Fehler mehr kommen.
10. **PDFs erzeugen:** `python3 seo-audit/tools/render_report.py <json> --out seo-audit`
    (überschreibt `SEO-Audit-FSH-Documentation.pdf` und `…-Kurzfassung.pdf`).
11. **Verlauf pflegen:** Zeile in `seo-audit/verlauf.md` ergänzen (Vorlage dort).
12. **Ausgabe im Chat:** Zusammenfassung, Veränderungen, Befundliste (ID, Titel, Priorität,
    Entwicklung), Pfad der JSON und der PDFs.
13. **Commit:** `SEO-Audit JJJJ-MM-TT HH:MM (Wochenaudit|Zwischenstand|manuell)`, alle Dateien
    unter `seo-audit/`. In der Routine-Session auf `main` pushen, sonst auf den aktuellen
    Branch, wenn er ein Remote-Branch (`claude/…`) ist oder der Nutzer es wünscht. Kein Pull Request.
14. **Melden:** Falls PushNotification verfügbar ist, unter 200 Zeichen: Lauf, Erreichbarkeit
    (ja/gesperrt), Zahl der offenen Befunde nach Priorität, Änderungen oder „keine Änderung“.

## Unbeaufsichtigter Lauf (Routine)

Die Freitags-Läufe laufen ohne Menschen. Deshalb: keine Rückfragen, keine Optionen anbieten,
keine Bestätigung abwarten. Unklarheiten durch eine Annahme lösen und die Annahme im Prüfumfang
nennen. Schlägt ein Schritt fehl (WebSearch nicht verfügbar, PDF-Erzeugung bricht ab, Push
abgelehnt), das Erreichte trotzdem schreiben und committen (JSON und Verlauf vor den PDFs) und den
Fehler am Ende klar benennen, auch in der Push-Nachricht. Ohne WebSearch keinen Bericht erfinden:
dann nur Erreichbarkeit prüfen, das Fehlen des Werkzeugs im Prüfumfang festhalten und melden.

## Prüfkatalog

### Erreichbarkeit und Technik (Befehle)

```bash
mkdir -p /tmp/seo
UA="Mozilla/5.0 (compatible; FSH-SEO-Audit/1.0)"
for u in https://fsh-documentation.com/ https://www.fsh-documentation.com/ http://fsh-documentation.com/ \
         https://fsh-documentation.de/ https://www.fsh-documentation.de/; do
  curl -sS -L -m 25 -A "$UA" -o /dev/null -w "$u -> %{http_code} %{url_effective} %{time_total}s\n" "$u" || true
done
curl -sS -L -m 25 -A "$UA" -o /tmp/seo/home.html -w "%{http_code} %{url_effective} %{time_total}s\n" https://fsh-documentation.com/
curl -sS -L -m 25 -A "$UA" -o /tmp/seo/robots.txt -w "robots %{http_code}\n" https://fsh-documentation.com/robots.txt
curl -sS -L -m 25 -A "$UA" -o /tmp/seo/sitemap.xml -w "sitemap %{http_code}\n" https://fsh-documentation.com/sitemap.xml
curl -sS -L -m 25 -A "$UA" -o /dev/null -w "404-Test %{http_code}\n" https://fsh-documentation.com/gibt-es-nicht-4711
```

Bewertung: `301` von http auf https und zwischen www und non-www in eine Richtung; Zweitdomain per
`301` auf die Hauptdomain; robots.txt vorhanden und ohne `Disallow: /`; Sitemap vorhanden, URLs
antworten mit `200`; 404-Test liefert `404`, nicht `200`; Antwortzeit der Startseite unter 1,5 s.

### On-Page

```bash
python3 seo-audit/tools/onpage_check.py /tmp/seo/home.html --url https://fsh-documentation.com/
```

Richtwerte: Title 30–60 Zeichen mit Marke und Leistung, auf der Startseite auch Ort;
Meta-Description 70–160 Zeichen; genau eine H1; alle Bilder mit Alt-Text; Canonical auf die
eigene URL; JSON-LD `Organization` oder `LocalBusiness` mit `sameAs`; Impressum und Datenschutz
von jeder Seite verlinkt; mehrsprachige Seiten mit `hreflang`.

### Suchindex-Abfragen (fest, in dieser Reihenfolge)

1. `site:fsh-documentation.com`
2. `site:fsh-documentation.de`
3. `"FSH-Documentation"`
4. `FSH-Documentation Teltow`
5. `Technische Dokumentation Teltow`
6. `Technische Dokumentation Potsdam Berlin Dienstleister`
7. `Technische Redaktion CE-Konformität Betriebsanleitung Dienstleister Berlin Brandenburg`
8. `Betriebsanleitung erstellen lassen Maschinenbau CE`
9. der exakte Seitentitel der Startseite in Anführungszeichen (Stand 19.09.2026:
   `"Technische Dokumentation auf Premium-Niveau"`)
10. `FSH documentation` (Markenkollision beobachten)

Je Abfrage zählen: Treffer von fsh-documentation.com oder .de (ja/nein, URL, Position, sofern
erkennbar), Wettbewerber unter den Treffern, Auffälligkeiten (neue Unterseiten, geänderter Titel).

### Bewertungsregeln

- `hoch`: verhindert Auffindbarkeit oder Vertrauen (Domain-Split ohne Weiterleitung, nur die
  Startseite im Index, Title ohne Marke und Leistung, `noindex`, kaputtes HTTPS, keine Treffer für
  Kernbegriffe).
- `mittel`: schwächt (Markenmehrdeutigkeit, fehlende strukturierte Daten, uneinheitliche NAP-Daten,
  fehlendes Google-Unternehmensprofil, fehlende Meta-Description).
- `niedrig`: Feinschliff (Alt-Texte einzelner Bilder, Title-Länge, Ladezeit knapp über Richtwert).
- Prüfstatus: `geprueft` = Bereich mit Beleg bewertet, `teilweise` = nur zum Teil prüfbar,
  `offen` = in diesem Lauf nicht prüfbar.

### Vorlage der Bericht-JSON

Feldliste und Regeln stehen im Kopf von `seo-audit/tools/render_report.py`. Beispiel mit allen
Feldern: `seo-audit/berichte/2026-09-19-manuell.json`. Die Kurzfassung zeigt höchstens vier
Befunde (`kurzfassung.befunde`, sonst die vier mit höchster Priorität), den Prüfstatus und ein bis
drei nächste Schritte.

## Checkliste vor dem Commit

- [ ] Erreichbarkeit geprüft und im Prüfumfang benannt (erreichbar oder gesperrt)
- [ ] alle zehn Suchindex-Abfragen ausgeführt, Treffer nach URLs beurteilt
- [ ] jeder Befund mit Beleg und Empfehlung, Priorität nach den Bewertungsregeln
- [ ] Befund-IDs aus dem Vergleichsstand übernommen, `entwicklung` gesetzt, neue IDs fortlaufend
- [ ] `veraenderungen` gefüllt oder ausdrücklich „keine Änderung“ in der Zusammenfassung
- [ ] `render_report.py --check` ohne Fehler, beide PDFs neu erzeugt
- [ ] Zeile in `verlauf.md`, Commit-Nachricht nach Muster, Push-Nachricht unter 200 Zeichen
