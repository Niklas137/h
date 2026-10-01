# Erledigen: alle Klick-Schritte an einem Ort

Stand 01.10.2026. Alles, was nur mit deinen Logins geht, in der Reihenfolge, die am meisten bringt.
Jeder Block ist in sich abgeschlossen; du kannst nach jedem Block aufhören. Werte zum Kopieren stehen
in Codeblöcken. Nach einem Block kurz hier im Chat melden („A fertig“), ich prüfe dann per DNS und
Abruf und setze die Befunde im nächsten Freitagsbericht auf erledigt.

Logins, die du brauchst: STRATO-Kundenlogin (.de), Canva (.com und das alte Design), Google-Konto der
Firma, GitHub-Konto `Niklas137`.

## A. STRATO (15 Minuten, löst B12 und B1)

**A0. Vorher in Apple Mail prüfen.** Einstellungen → Accounts → Konto `fsh-documentation.de` →
Servereinstellungen. Ausgangsserver muss `smtp.strato.de` sein. Steht da iCloud oder Gmail: stopp,
hier melden, nichts eintragen.

**A1. DNS, drei TXT-Einträge.** Domains → Domainverwaltung → Zahnrad bei `fsh-documentation.de` →
Reiter DNS → „TXT- und CNAME-Records verwalten“. Bei DMARC vorher „Keine STRATO DMARC-Regel“ wählen.

| Name | Typ | Wert |
|---|---|---|
| leer oder `@` | TXT | `v=spf1 include:_spf.strato.com -all` |
| `_dmarc` (vorhandenen Eintrag ersetzen) | TXT | `v=DMARC1; p=reject; rua=mailto:niklas.heinzmann@fsh-documentation.de; fo=1` |
| `fsh-documentation.com._report._dmarc` | TXT | `v=DMARC1` |

**A2. Weiterleitung der .de.** Gleiche Domain → Reiter Webserver → „Umleitung einrichten“: von
„Platzhalter aktiviert“ auf „Externe Weiterleitung“, Ziel `https://fsh-documentation.com/`, Typ 301
dauerhaft, speichern. Subdomain `www` über ihr eigenes Zahnrad genauso. Zeigt `https://fsh-documentation.de/`
danach noch den Platzhalter oder eine Zertifikatswarnung: „SSL verwalten“ → „SSL erzwingen“.

Rückmeldung: „A fertig“. Ich prüfe mit `seo-audit/tools/mail_dns_check.py` und per Abruf der .de.

## B. Canva (15 Minuten, löst B12 für die .com; B2 und B8 nur als Zwischenlösung)

**B1. DNS, zwei TXT-Einträge.** Einstellungen → Domains → Verwalten bei `fsh-documentation.com` →
DNS-Einträge. Diese Einträge bleiben auch nach dem Umzug der Website bestehen.

| Name | Typ | Wert |
|---|---|---|
| `@` | TXT | `v=spf1 -all` |
| `_dmarc` (vorhandenen Eintrag ersetzen) | TXT | `v=DMARC1; p=reject; rua=mailto:niklas.heinzmann@fsh-documentation.de` |

**B2 bis B4 nur, wenn die neue Website nicht innerhalb von vier Wochen live geht.** Sonst überspringen,
die neue Website hat das alles schon eingebaut.

**B2. Seitentitel und Beschreibung** (Canva-Design → Seiteneinstellungen; „Magic SEO“ nicht benutzen,
es überschreibt ohne Rückweg):

```
FSH-Documentation – Technische Dokumentation Teltow
```

```
FSH-Documentation aus Teltow: Betriebsanleitungen, CE-/UKCA-Konformität, Risikobeurteilung, MDR-Dokumentation nach IEC/IEEE 82079-1. Erstreaktion in 24 h.
```

**B3. Alt-Texte** (Element auswählen → Mehr … → „Alternativtext“). Drei Bilder bekommen Text, alle
Icons und Button-Hintergründe werden „als dekorativ“ markiert oder bekommen einen leeren Text.

| Bild | Alt-Text |
|---|---|
| Logo | `Logo FSH-Documentation – Fast. Simple. High Quality.` |
| Porträt | `Sascha Falk Heinzmann, Geschäftsführer von FSH-Documentation` |
| Zahnräder-Foto | `Offene Hand hält drei leuchtende Zahnräder – Sinnbild für den Dokumentationsprozess` |

**B4. Toter Link.** Der mailto-Link `info@fsh-documentation.com` auf der Startseite führt ins Leere (die
.com kann keine Mail empfangen). Entscheidung mit Falk offen: auf `info@fsh-documentation.de` oder
`Falk.Heinzmann@fsh-documentation.de` ändern, einheitlich mit dem sichtbaren Text daneben.

Rückmeldung: „B fertig“ (oder „B1 fertig“).

## C. Google-Unternehmensprofil (30 Minuten plus Wartezeit, löst B6)

Anleitung mit allen Entscheidungen und fertigen Texten: `website/google-und-email-dns.md`, Abschnitt 2.
Kurz: `business.google.com` mit dem Firmen-Google-Konto, Name `FSH-Documentation`, Art
Dienstleistungsunternehmen, Adresse eingeben, aber nicht anzeigen, Einzugsgebiet Teltow, Potsdam,
Berlin, Kleinmachnow, Stahnsdorf, Potsdam-Mittelmark, Teltow-Fläming; Telefon `+49 172 9795939`,
Website `https://fsh-documentation.com/`. Bestätigung dauert bis zu fünf Werktage.

Rückmeldung: „C beantragt“, später „C bestätigt“.

## D. Neue Website live (löst B3, B4, B7, B9, B10, B11 und endgültig B2, B8)

**D1. GitHub-Support fragen** (15 Minuten, dann warten). `https://support.github.com/request`, Vorlage
in `website/offene-punkte.md`, Abschnitt A. Antwort als PDF in `website/nachweise/` ablegen.

**D2. Testadresse einschalten** (10 Minuten, geht schon vor der Support-Antwort). Im Repo
`Niklas137/h`:

1. Settings → Pages → Source: „GitHub Actions“.
2. Settings → Secrets and variables → Actions → Variables → New repository variable, zweimal:
   `WEBSITE_HOSTING` = `github` und `WEBSITE_BUILD_ARGS` = `--relativ --noindex`.
3. Actions → Workflow „Website“ → Run workflow. Nach einer Minute: `https://niklas137.github.io/h/`.

Rückmeldung: „D2 läuft“. Ich gehe dann die Checkliste aus `website/livegang.md`, Abschnitt 7, selbst
durch und melde Befunde.

**D3. Vier Freigaben** (eine Nachricht reicht):

- GitHub: ja oder nein, dazu der Satz zum Data Protection Agreement.
- Referenz „rund 40 % schnellere Inhaltserstellung“: gemessen oder Ziel?
- freelance.de-Profil: Sprachen angleichen, oder Website anpassen?
- Rechtstexte (`website/pruefpaket-rechtstexte.pdf`): freigegeben, oder Änderungen folgen?
- Zusatz: LinkedIn-Profil `de.linkedin.com/in/sascha-falk-heinzmann-a589961b7` in die Website
  aufnehmen (Fußzeile, strukturierte Daten)? Ja oder nein.

**D4. Livegang** (nach D1 „ja“ und D3). Ich baue ohne `--noindex`, dann du: `WEBSITE_BUILD_ARGS`
leeren, DNS der .com bei Canva nach `website/livegang.md`, Abschnitt 3.2, Search Console nach
Abschnitt 8. Danach übernimmt das Freitags-Audit die Kontrolle der neuen Seite.

## E. Postfach sortieren (nur auf dem MacBook)

Nicht aus dieser Session möglich. Auf dem Mac die Claude-Desktop-App öffnen oder im Repo-Ordner
`claude remote-control` starten und beauftragen: „Lies nur das Postfach niklas.heinzmann@fsh-documentation.de
in Apple Mail, Falks Konto nicht anfassen. Erst Kategorien vorschlagen, noch nichts verschieben.“

## Was danach noch offen bleibt

Nur Punkte, die Falk entscheidet: toter Link `info@fsh-documentation.com` (B4), Kundennamen auf der
Website (entschieden: keine), Plattformwechsel ist mit D erledigt.
