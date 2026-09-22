# Livegang der neuen Website, Schritt für Schritt

Stand 22.09.2026. Ergänzt `website/README.md` (Bau und Pflege) um die Schritte, die nur der Betreiber
ausführen kann: Hosting wählen, Testadresse, DNS umstellen, Search Console, Weiterleitung der .de.
Die Reihenfolge ist so gewählt, dass die alte Canva-Seite bis zum letzten Schritt online bleibt und
sich jeder Schritt zurücknehmen lässt.

## 1. Empfehlung und Entscheidung

| | GitHub Pages (empfohlen) | STRATO-Webspace | Cloudflare Pages |
|---|---|---|---|
| Aufwand | gering: zwei Einstellungen im Repo, drei DNS-Einträge bei Canva | mittel: Domain-Umzug der .com zu STRATO nötig | mittel: Nameserver-Wechsel zu Cloudflare |
| Kosten | 0 € (Repo ist öffentlich) | im bestehenden STRATO-Paket, falls Webspace enthalten | 0 € |
| Veröffentlichung | automatisch bei jedem Push nach `main` (Workflow liegt bereit) | von Hand per SFTP | automatisch aus dem Repo |
| HTTPS | automatisch (Let's Encrypt) | STRATO-Zertifikat („SSL erzwingen") | automatisch |
| Serverstandort | USA (GitHub, Inc.; Datenschutz-Variante `github`) | Deutschland (Variante `strato`) | weltweit (Variante `cloudflare`) |
| Testadresse vorher | `https://niklas137.github.io/h/` | über die .de-Domain | `*.pages.dev` |

Empfehlung: **GitHub Pages**. Die Website liegt schon im Repo, der Workflow `.github/workflows/website.yml`
baut und prüft sie bei jedem Push und veröffentlicht sie, sobald eine Repository-Variable gesetzt ist.
Die .com-Domain bleibt bei Canva registriert; nur drei DNS-Einträge ändern sich. Wer einen deutschen
Serverstandort will, nimmt STRATO (Abschnitt 4); das setzt aber den Umzug der .com zu STRATO voraus,
weil STRATO-Webspace keine fremd verwalteten Domains aufschaltet.

Vor dem Start festlegen und in `website/inhalt/site.json` eintragen:

- `hosting`: `github`, `strato` oder `cloudflare` (steuert die Datenschutzerklärung, Abschnitte 2 und 5).
- Offene Punkte aus `website/README.md`: Kundennamen auf der Startseite, Seite Redaktionssysteme ST4,
  Titel der Regionalseite, Bildnachweise. Rechtstexte prüfen lassen (keine Rechtsberatung).
- Danach `python3 website/build.py --pruefen` laufen lassen und das Ergebnis committen.

## 2. Was vor der DNS-Umstellung zu sichern ist

1. Bei Canva anmelden → Startseite → Zahnrad **Einstellungen** → **Domains** → neben
   `fsh-documentation.com` auf **Verwalten** → **DNS-Einträge**. Alle vorhandenen Einträge
   (A, AAAA, CNAME, TXT, MX) als Screenshot sichern. Das ist der Rückweg, falls etwas schiefgeht.
2. Notieren, welche Einträge Canva für die Website gesetzt hat (A-Eintrag `@` auf eine Canva-Adresse,
   CNAME `www`). Genau diese werden später ersetzt; alles andere bleibt.
3. Wissen, dass die .com heute HSTS sendet: Browser, die die Seite schon besucht haben, verlangen
   HTTPS. Der neue Hoster muss deshalb vom ersten Aufruf an ein gültiges Zertifikat liefern. Bei
   GitHub Pages dauert das nach der DNS-Prüfung einige Minuten bis etwa eine Stunde; in dieser Zeit
   zeigen manche Browser eine Zertifikatswarnung. Umstellung deshalb abends oder am Wochenende.

## 3. Weg A: GitHub Pages

### 3.1 Testadresse einrichten (die alte Seite bleibt online)

1. Im Repo `Niklas137/h` → **Settings** → **Pages** → unter „Build and deployment" bei **Source**
   „GitHub Actions" wählen.
2. **Settings** → **Secrets and variables** → **Actions** → Reiter **Variables** → **New repository variable**:
   - Name `WEBSITE_HOSTING`, Wert `github`
   - Name `WEBSITE_BUILD_ARGS`, Wert `--relativ --noindex`
   `--relativ` macht die Links so, dass die Seite auch unter `/h/` funktioniert; `--noindex` sorgt dafür,
   dass Google die Testadresse nicht aufnimmt (Meta-Robots noindex, robots.txt sperrt, keine Sitemap).
3. **Actions** → Workflow **Website** → **Run workflow** → **Run workflow**. Nach etwa einer Minute
   steht die Seite unter `https://niklas137.github.io/h/`.
4. Testadresse durchgehen (Checkliste in Abschnitt 7).

### 3.2 Eigene Domain aufschalten

1. **Settings** → **Pages** → **Custom domain**: `fsh-documentation.com` eintragen → **Save**.
   GitHub meldet zunächst „DNS check unsuccessful", das ist bis zum nächsten Schritt normal.
2. Bei Canva (Einstellungen → Domains → Verwalten → DNS-Einträge) die Website-Einträge von Canva
   ersetzen (Quelle: GitHub-Dokumentation „Managing a custom domain"):
   - den vorhandenen A-Eintrag `@` (Canva) löschen und vier neue A-Einträge `@` anlegen:
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - vier AAAA-Einträge `@`: `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`,
     `2606:50c0:8003::153`
   - den vorhandenen CNAME `www` (Canva) durch CNAME `www` → `niklas137.github.io` ersetzen
   - alle übrigen Einträge (TXT, MX, falls vorhanden) unverändert lassen.
   Ab diesem Moment ist die Canva-Seite unter der .com nicht mehr erreichbar.
3. Zurück in **Settings** → **Pages**: warten, bis der DNS-Check grün ist (Minuten bis eine Stunde),
   dann **Enforce HTTPS** anhaken. `https://www.fsh-documentation.com` leitet danach auf die
   Hauptadresse um.
4. Repository-Variable `WEBSITE_BUILD_ARGS` auf leer setzen (oder löschen) und den Workflow erneut
   starten: Jetzt werden absolute Links, Sitemap und `robots.txt` mit Freigabe gebaut.
5. Prüfen, im Terminal oder in einem Online-Header-Check:

```bash
curl -sI https://fsh-documentation.com/ | head -5          # erwartet: HTTP/2 200
curl -sI https://www.fsh-documentation.com/ | head -3      # erwartet: 301 auf https://fsh-documentation.com/
curl -s https://fsh-documentation.com/robots.txt            # erwartet: Allow: / und Sitemap-Zeile
curl -s https://fsh-documentation.com/sitemap.xml | grep -c "<loc>"   # erwartet: 11
```

6. Bei Canva die alte Website auf „Veröffentlichung aufheben" setzen, damit sie nicht unter einer
   `my.canva.site`-Adresse als Kopie weiterlebt. Die Domain selbst bleibt bei Canva registriert
   (Verlängerung laut Phase 2 am 23.04.2027, automatische Verlängerung eingeschaltet lassen).

Ab jetzt gilt: Jeder Push nach `main`, der `website/` ändert, baut, prüft und veröffentlicht die Seite
automatisch. Schlägt die Prüfung fehl (zum Beispiel ein toter interner Link), wird nichts veröffentlicht
und der Workflow zeigt den Fehler.

## 4. Weg B: STRATO-Webspace

Nur sinnvoll, wenn das STRATO-Paket Webspace enthält (Kundenlogin → Paket → **Verwaltung** →
Webspace, siehe STRATO-FAQ „Ihren Webspace im Paket verwalten"). Die .com muss zu STRATO umziehen,
weil STRATO-Webspace keine bei einem anderen Anbieter verwalteten Domains aufschaltet.

1. **Test über die .de:** `site.json` auf `"hosting": "strato"` stellen, bauen mit
   `python3 website/build.py --pruefen --noindex`, den Inhalt von `website/dist/` (inklusive
   `.htaccess`) per SFTP in ein Unterverzeichnis laden, zum Beispiel `/fsh`. Auf der neuen
   STRATO-Plattform muss das Ziel ein Unterverzeichnis sein, das Wurzelverzeichnis `/` ist nicht
   mehr zulässig (STRATO-FAQ „Alles zur Domainumleitung").
2. Kundenlogin → Paket → **Domains verwalten** → Zahnrad bei `fsh-documentation.de` → Umleitungsziel
   von „Platzhalter" auf das Verzeichnis `/fsh` (interne Umleitung) stellen; **SSL verwalten** → „SSL
   erzwingen". Dann ist die neue Seite unter `https://fsh-documentation.de/` sichtbar, für Google
   gesperrt. Checkliste aus Abschnitt 7 durchgehen. E-Mail über die .de ist davon nicht betroffen.
3. **Domain-Umzug:** Bei Canva (Einstellungen → Domains → Verwalten) den Transfer freischalten und
   den Auth-Code anfordern; bei STRATO „Domain umziehen" mit diesem Code starten. Der Umzug dauert
   in der Regel bis zu fünf Tage; während dieser Zeit bleibt die Canva-Seite erreichbar.
4. Nach dem Umzug: `fsh-documentation.com` bei STRATO ebenfalls auf `/fsh` stellen, „SSL erzwingen".
   Neu bauen **ohne** `--noindex`, per SFTP hochladen (überschreibt die Testfassung).
5. Die .de auf externe Weiterleitung 301 nach `https://fsh-documentation.com/` umstellen (Abschnitt 6).

## 5. Weg C: Cloudflare Pages

Setzt voraus, dass die DNS-Zone der .com zu Cloudflare wechselt (Cloudflare-Dokumentation: eine
Apex-Domain wie `fsh-documentation.com` lässt sich nur aufschalten, wenn die Zone im eigenen
Cloudflare-Konto liegt).

1. Cloudflare-Konto anlegen → **Add a site** → `fsh-documentation.com`, Tarif Free. Cloudflare liest die
   vorhandenen DNS-Einträge ein; Liste mit dem Screenshot aus Abschnitt 2 vergleichen.
2. **Workers & Pages** → **Create** → **Pages** → **Connect to Git** → Repo `Niklas137/h`;
   Build command `python3 website/build.py --noindex`, Build output directory `website/dist`.
   Nach dem ersten Build steht die Testadresse `https://<projekt>.pages.dev` bereit (Abschnitt 7).
3. Bei Canva (Einstellungen → Domains → Verwalten → **Nameserver**) die beiden von Cloudflare
   genannten Nameserver eintragen. Wirksam nach Minuten bis 24 Stunden. E-Mail-Einträge (MX) hat
   Cloudflare beim Einlesen übernommen; für die .com gibt es laut Phase 2 keine.
4. Im Pages-Projekt **Custom domains** → `fsh-documentation.com` und `www.fsh-documentation.com`
   hinzufügen; Cloudflare legt die DNS-Einträge selbst an.
5. Build command auf `python3 website/build.py` (ohne `--noindex`) ändern, `site.json` auf
   `"hosting": "cloudflare"`, neu bauen lassen. Prüfen wie in Abschnitt 3.2, Schritt 5.

## 6. STRATO: Weiterleitung der .de auf die .com

Aus Phase 2, Abschnitt 7a, hier nur die Kurzfassung:

1. STRATO-Kundenlogin → **Domains** → **Domainverwaltung** → Zahnrad bei `fsh-documentation.de` →
   **Webserver** → „Umleitung einrichten".
2. Von „Platzhalter aktiviert" (oder dem Testverzeichnis aus Abschnitt 4) auf **Externe Weiterleitung**
   stellen, Ziel `https://fsh-documentation.com/`, Typ 301 (dauerhaft), speichern.
3. `www.fsh-documentation.de` unterhalb der Domain über das Zahnrad genauso einstellen.
4. Falls der HTTPS-Aufruf der .de weiter den Platzhalter oder eine Zertifikatswarnung zeigt: erst
   **SSL verwalten** → „SSL erzwingen", sonst STRATO-Support fragen.
5. Test, alle vier Varianten müssen `301` mit `Location: https://fsh-documentation.com/` liefern:

```bash
for u in http://fsh-documentation.de/ https://fsh-documentation.de/ http://www.fsh-documentation.de/ https://www.fsh-documentation.de/; do curl -sI "$u" | grep -iE "^(HTTP|location)"; done
```

## 7. Checkliste für die Testadresse

- Startseite, alle sieben Unterseiten, Impressum, Datenschutz, AGB und eine falsche Adresse
  (404-Seite) aufrufen; Fußzeilen-Links und „Verwandte Leistungen" anklicken.
- Handy-Breite prüfen (Browserfenster schmal ziehen oder Handy): Menü über das Symbol oben rechts,
  keine seitliche Scrollbewegung.
- Schalter **Auto / Dunkel / Hell** in der Kopfzeile; Logo bleibt in beiden Schemata lesbar.
- „E-Mail schreiben" öffnet das Mailprogramm mit Betreff, Telefonnummer ist auf dem Handy antippbar.
- Bilder: Porträt und Zahnräder-Foto auf der Startseite, Logo überall.
- Browser-Entwicklerwerkzeuge → Netzwerk: alle Anfragen gehen an die eigene Adresse, keine an
  Google, Canva oder Cloudflare (bei GitHub Pages und Cloudflare Pages ist der Hoster selbst die
  Ausnahme).
- Im Quelltext der Startseite: `<title>FSH-Documentation – Technische Dokumentation Teltow</title>`,
  `<link rel="canonical" href="https://fsh-documentation.com/">`, beim Test zusätzlich
  `<meta name="robots" content="noindex, nofollow">`; live darf diese Zeile nicht mehr da sein.

## 8. Google Search Console

Aus Phase 2, Abschnitt 7c, angepasst an den neuen Hoster:

1. `https://search.google.com/search-console` → **Property hinzufügen** → Typ **Domain** →
   `fsh-documentation.com`. Google zeigt einen TXT-Eintrag `google-site-verification=…`.
2. Diesen TXT-Eintrag dort anlegen, wo die DNS der .com verwaltet wird: bei Canva (Weg A),
   bei STRATO (Weg B) oder bei Cloudflare (Weg C). Name `@`, Wert wie angezeigt. Nach einigen Minuten
   in der Search Console **Bestätigen**.
3. **Sitemaps** → `https://fsh-documentation.com/sitemap.xml` eintragen → Senden. Erwartet: „Erfolgreich",
   11 gefundene URLs.
4. **URL-Prüfung** → Startseite eingeben → **Indexierung beantragen**; danach dasselbe für die sieben
   Unterseiten. Das beschleunigt die Aufnahme der neuen Seiten um Tage.
5. Nach einer Woche unter **Seiten** kontrollieren, dass die 11 URLs als indexiert geführt werden und
   keine „Alternative Seite mit kanonischem Tag"-Meldungen auf die alte Canva-Adresse zeigen.

## 9. Nach dem Livegang

- Kontrolle mit den Audit-Werkzeugen (wie beim Freitags-Audit):
  `node seo-audit/tools/fetch_rendered.js https://fsh-documentation.com/ home.html` und
  `python3 seo-audit/tools/onpage_check.py home.html --url https://fsh-documentation.com/`.
- Das Freitags-Audit (7:30 und 16:00) läuft unverändert weiter und prüft ab dem nächsten Lauf die
  neue Seite; die Befunde B2 bis B11 aus dem Maßnahmenpaket sollten dann als erledigt erscheinen,
  B1 (Weiterleitung der .de) nach Abschnitt 6.
- Google-Unternehmensprofil anlegen (Phase 2, Abschnitt 7d) und dort `https://fsh-documentation.com/`
  eintragen; SPF für die .de setzen (Phase 2, Abschnitt 6).
- Canva-Abo: Das Website-Hosting wird nicht mehr gebraucht; die Domain-Registrierung bei Canva bleibt,
  bis sie umgezogen wird (bei Weg B) oder weiterläuft (Weg A und C).

## 10. Rückweg

Solange die Canva-Seite nicht deaktiviert ist, genügt es, die DNS-Einträge aus dem Screenshot in
Abschnitt 2 wiederherzustellen: A `@` und CNAME `www` auf die Canva-Werte, die GitHub-Einträge löschen.
Wirksam innerhalb von Minuten bis einer Stunde. Bei Weg C zusätzlich die Nameserver bei Canva auf die
ursprünglichen Werte zurücksetzen.

Quellen: GitHub-Dokumentation „Managing a custom domain for your GitHub Pages site"; Cloudflare
„Custom domains" für Pages; Canva-Hilfe „Add, edit, or delete your domain's DNS records" und
„Website DNS settings"; STRATO-FAQ „Alles zur Domainumleitung" und „Ihren Webspace im Paket
verwalten"; Maßnahmenpaket Phase 2 (`seo-audit/massnahmen/2026-09-21-phase-2.md`), Abschnitte 6, 7a, 7c, 7d.
