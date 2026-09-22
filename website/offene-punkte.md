# Offene Punkte vor dem Livegang: was zu tun ist

Stand 22.09.2026. Vier Punkte brauchen eine Antwort des Betreibers oder des Rechtsprüfers. Für jeden
steht hier, worum es geht, was genau zu tun ist, welcher fertige Text dafür bereitliegt und welche
kurze Rückmeldung reicht, damit die Website angepasst werden kann.

## A. GitHub-Support: Bestätigung, dass die Website auf GitHub Pages erlaubt ist

**Worum es geht.** Die Zusatzbedingungen von GitHub sagen, GitHub Pages dürfe nicht genutzt werden,
„to run your online business, e-commerce site, or any other website that is primarily directed at
either facilitating commercial transactions or providing commercial software as a service“. Eine reine
Unternehmens-Informationsseite ohne Shop, ohne Formular und ohne Login ist davon nach dem Wortlaut nicht
klar erfasst, GitHub hat das aber nie öffentlich bestätigt. Ohne Bestätigung besteht das Risiko, dass
GitHub die Seite abschaltet; dann wären Impressum und Datenschutzerklärung nicht mehr erreichbar.
Im selben Ticket lässt sich die zweite offene Frage klären: ob das GitHub Data Protection Agreement
(Auftragsverarbeitungsvertrag) für ein kostenloses Konto mit GitHub Pages gilt.

**Was zu tun ist.**

1. `https://support.github.com/request` aufrufen, mit dem GitHub-Konto `Niklas137` anmelden.
2. Als Betreff und Text die Vorlage unten verwenden (Englisch, weil der Support auf Englisch antwortet).
3. Die Antwort als PDF oder Screenshot im Ordner `website/nachweise/` ablegen (Dateiname
   `github-support-JJJJ-MM-TT.pdf`) und committen; der Ordner ist dafür angelegt.
4. Rückmeldung an mich: „GitHub: ja“ oder „GitHub: nein“, dazu die Antwort zum Data Protection Agreement
   in einem Satz.

**Was dann passiert.** Bei „ja“ bleibt alles wie geplant. Bei „nein“ stelle ich `site.json` auf
`hosting: cloudflare`, baue neu und passe die Livegang-Anleitung an (Weg C, Cloudflare Pages; Texte und
Bau liegen bereit). Die Antwort zum Data Protection Agreement arbeite ich in Abschnitt 5 der
Datenschutzerklärung ein.

**Vorlage für das Ticket.**

Subject: GitHub Pages: is a static company information website permitted?

Hello GitHub Support,

I own the public repository Niklas137/h and plan to publish a static company website with GitHub Pages
under the custom domain fsh-documentation.com. The site consists of about twelve static HTML pages that
describe our technical-documentation services (operating manuals, CE conformity documentation, risk
assessments), plus the imprint, privacy policy and terms required by German law. It has no shop, no
checkout, no payments, no login, no user accounts, no forms and no software as a service; visitors can
only read the pages and use mailto and tel links to contact us.

The GitHub Terms for Additional Products and Features state that GitHub Pages is "not intended for or
allowed to be used as a free web-hosting service to run your online business, e-commerce site, or any
other website that is primarily directed at either facilitating commercial transactions or providing
commercial software as a service (SaaS)". Could you please confirm in writing that a static,
informational company website as described above is within the acceptable use of GitHub Pages?

Second question, for our privacy notice under the GDPR: when a GitHub Pages site is visited, GitHub logs
the visitor's IP address for security purposes. Does the GitHub Data Protection Agreement apply to a free
individual account that uses GitHub Pages, or does GitHub act solely as an independent controller for
these access logs? We need to describe GitHub's role correctly (Art. 13 and Art. 28 GDPR).

Thank you very much.

Sascha Falk Heinzmann
FSH-Documentation UG (haftungsbeschränkt), Teltow, Germany

## B. Referenz „rund 40 % schnellere Inhaltserstellung“

**Worum es geht.** Die alte Website nennt in der Fallstudie „Technologieunternehmen (AT)“ als Ergebnis
„~40 % schnellere Inhaltserstellung“. Der Werdegang auf derselben Seite beschreibt dasselbe Mandat
(März 2024) als „Grundlagen für die Einführung von ST4 schaffen, um die Inhaltserstellung deutlich zu
beschleunigen (Ziel: >40 %)“, also als Ziel bei der Vorbereitung. Beides zusammen passt nicht: Entweder
wurde der Wert nach der Einführung gemessen, oder er war das Projektziel. Die neue Website übernimmt
derzeit die Fassung „Ergebnis“ an fünf Stellen (Startseite, Regionalseite, ST4-Seite mit Description,
Einleitung und Praxiskasten).

**Was zu tun ist.** Eine Rückmeldung mit einem Wort: „40 %: gemessen“ oder „40 %: Ziel“.

**Was dann passiert.**

- „gemessen“: Die Texte bleiben. Empfehlung: die Messgrundlage (Zeitraum, Vergleichswert) in einer
  Notiz im Repo festhalten, falls ein Kunde oder Wettbewerber nachfragt.
- „Ziel“: Ich ändere die fünf Stellen so:
  - Startseite und Regionalseite, Referenz „Technologieunternehmen (AT)“, Ergebnis: „Ziel der Einführung:
    über 40 % schnellere Inhaltserstellung; Übersetzungskosten spürbar gesenkt.“
  - ST4-Seite, Description: „Vorbereitung und Einführung von SCHEMA ST4: Strukturkonzept,
    Standardisierung, Modularisierung, DE/EN-Workflow. Ziel der Referenz: über 40 % schnellere Erstellung.“
  - ST4-Seite, Einleitung: „Referenz: Vorbereitung und Einführung von SCHEMA ST4 mit dem Ziel, die
    Inhaltserstellung um über 40 % zu beschleunigen.“
  - ST4-Seite, Praxiskasten „Ergebnis“: „Ziel: über 40 % schnellere Inhaltserstellung; Übersetzungskosten
    spürbar gesenkt.“

## C. freelance.de-Profil und die Sprachen auf der Website

**Worum es geht.** Die neue Website verlinkt im Fuß jeder Seite und in den strukturierten Daten das
Profil `freelance.de/Freelancer/269905-Geschaeftsfuehrer-FSH-Documentation` (es ist das einzige online
bestätigte Profil; das LinkedIn-Profil war nicht abrufbar). Das Profil nennt „Englisch (Grundkenntnisse)“
sowie Deutsch, Ukrainisch und Russisch als Muttersprachen. Die Website verspricht Lieferung in Deutsch,
Englisch, Ukrainisch und Russisch und beschreibt das Team als „Kernteam und erprobtes Expertennetzwerk
(DE/EN/UKR/RU)“. Wer dem Link folgt, sieht eine Diskrepanz beim Englischen.

**Drei Möglichkeiten, eine reicht.**

1. **Profil angleichen.** Wenn Englisch über das Netzwerk geliefert wird: im freelance.de-Profil unter
   „Profil bearbeiten“ im Profiltext einen Satz ergänzen wie „Englische Dokumentation über ein erprobtes
   Expertennetzwerk“; die eigene Sprachkenntnis kann so stehen bleiben. Wenn die eigene Englischkenntnis
   höher ist als „Grundkenntnisse“: Stufe im Profil anheben. Rückmeldung: „Profil angepasst“.
2. **Website benennt die Rollen.** Ich ändere die Sprachangaben auf der Website in: „Deutsch, Ukrainisch
   und Russisch im Kernteam, Englisch über das erprobte Expertennetzwerk“ (Kontaktblock aller Seiten,
   Zahlenband und Team-Absatz der Startseite, Abschnitt „Mehrsprachig“ der Betriebsanleitungs-Seite,
   drei FAQ-Antworten). Rückmeldung: „Website: Rollen benennen“.
3. **Link entfernen.** Ich nehme den freelance.de-Link aus Fuß und strukturierten Daten. Nachteil: kein
   bestätigtes Profil mehr als Signal für Suchmaschinen. Rückmeldung: „Link raus“.

Empfehlung: Möglichkeit 1, weil sie die Website unverändert lässt und das Profil ohnehin gepflegt
werden sollte (es erscheint in Suchergebnissen zur Marke).

## D. Freigabe der Rechtstexte

**Worum es geht.** Impressum, Datenschutzerklärung und AGB wurden aus den heutigen Texten überarbeitet
(Gesetzesverweise, Hosting, Platzhalter, sprachliche Fehler) und maschinell gegen die Vorschriften
geprüft. Das ersetzt keine Prüfung durch eine Person mit Rechtskenntnis. Vor dem Livegang sollen die
drei Texte freigegeben werden.

**Was zu tun ist.**

1. Das Prüfpaket `website/pruefpaket-rechtstexte.pdf` an den Rechtsprüfer senden. Es enthält die drei
   Texte, die vollständige Änderungsliste gegenüber dem Stand 13.08.2025, zehn konkrete Fragen und eine
   E-Mail-Vorlage. Das Paket lässt sich jederzeit neu erzeugen:
   `python3 website/tools/pruefpaket.py` und dann
   `python3 seo-audit/tools/md_to_pdf.py website/pruefpaket-rechtstexte.md --out website/pruefpaket-rechtstexte.pdf`.
2. Die Antwort (Änderungswünsche mit Fundstelle und Wortlaut) an mich weitergeben; ich arbeite sie in
   `impressum.json`, `datenschutz.json` und `agb.json` ein, setze die „Stand“-Daten auf das
   Freigabedatum, baue neu und lege die Freigabe unter `website/nachweise/` ab.
3. Falls der Prüfer die Website-Aussagen (Frage 10 im Paket) beanstandet, ändere ich die betroffenen
   Seiten gleich mit.

**Bis die Freigabe vorliegt:** Testadresse einrichten ist unkritisch (Abschnitt 3.1 der
Livegang-Anleitung, mit `--noindex`); der Livegang unter fsh-documentation.com sollte auf die Freigabe
warten, weil die Rechtstexte ab dann öffentlich sind.

## Kurzfassung der Rückmeldungen

Eine Nachricht genügt, zum Beispiel:
„GitHub: ja, DPA gilt nicht · 40 %: gemessen · Profil angepasst · Rechtstexte: Änderungen folgen“.
