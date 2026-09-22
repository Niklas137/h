# Google-Unternehmensprofil und E-Mail-DNS: fertige Einträge und Texte

Stand 22.09.2026. Zwei Maßnahmen aus dem Maßnahmenpaket Phase 2 (Abschnitt 6 und 7d), die unabhängig
vom Website-Livegang gehen und beide nur der Betreiber ausführen kann. Alle Werte sind so vorbereitet,
dass sie eingetragen oder eingefügt werden können; der DNS-Stand wurde am 22.09.2026 per DNS-Abfrage
geprüft.

## 1. E-Mail-Authentifizierung: SPF und DMARC

### 1.1 Gemessener Stand (22.09.2026)

| Domain | MX | SPF | DKIM | DMARC |
|---|---|---|---|---|
| fsh-documentation.de | `smtpin.rzone.de` (STRATO) | **fehlt** | STRATO signiert (Selektoren `strato-dkim-0002` RSA und `strato-dkim-0003` Ed25519 vorhanden) | `v=DMARC1;p=reject;` ohne Berichtsadresse |
| fsh-documentation.com | keiner (kein Mailversand) | **fehlt** | keiner | `v=DMARC1; p=none` |

Was das bedeutet: Für die .de gilt bereits die strengste DMARC-Stufe (`p=reject`), aber ohne SPF und
ohne Berichte. Jede Mail, die nicht von STRATO DKIM-signiert wird (zum Beispiel aus einem anderen
Mailprogramm, über einen Newsletter- oder Formulardienst, oder bei einer DKIM-Störung), kann beim
Empfänger abgewiesen werden, und niemand erfährt davon. Die .com hat keinen Mailschutz: Jeder könnte
Mails mit Absender `@fsh-documentation.com` verschicken, ohne dass Empfänger sie ablehnen.

### 1.2 fsh-documentation.de bei STRATO

Weg im Kundenlogin: **Domains** → **Domainverwaltung** → Zahnrad bei `fsh-documentation.de` →
Reiter **DNS** → **TXT- und CNAME-Records verwalten** (STRATO-FAQ „DNS-Einträge bei STRATO verwalten“).

1. **SPF** anlegen. Entweder die vordefinierte „STRATO SPF-Regel“ einschalten oder als eigenen
   TXT-Eintrag für `fsh-documentation.de` (Name leer bzw. `@`) eintragen:

   ```
   v=spf1 include:_spf.strato.com ~all
   ```

   `_spf.strato.com` löst auf die Versandserver von STRATO auf (geprüft am 22.09.2026). Das `~all`
   (Softfail) ist der sichere Start; nach zwei Wochen ohne Probleme auf `-all` (Hardfail) umstellen.
   Wird später ein weiterer Versanddienst genutzt (Newsletter, CRM, Microsoft 365), kommt dessen
   `include:` in dieselbe Zeile; es darf nur einen SPF-Eintrag je Domain geben.
2. **DMARC** um eine Berichtsadresse ergänzen. STRATO bietet eine vordefinierte DMARC-Regel an; deren
   Inhalt ist nicht dokumentiert. Deshalb „Keine STRATO DMARC-Regel“ wählen und als TXT-Eintrag für
   `_dmarc.fsh-documentation.de` eintragen:

   ```
   v=DMARC1; p=reject; rua=mailto:dmarc@fsh-documentation.de; fo=1
   ```

   Vorher das Postfach `dmarc@fsh-documentation.de` bei STRATO anlegen oder als Weiterleitung auf
   `Falk.Heinzmann@fsh-documentation.de` einrichten. Die täglichen XML-Berichte zeigen, wer im Namen
   der Domain sendet und ob SPF und DKIM bestehen. Wer sie nicht selbst lesen will, trägt statt des
   eigenen Postfachs die Adresse eines kostenlosen DMARC-Auswertedienstes ein.
3. **DKIM** bleibt wie es ist: STRATO signiert automatisch, solange die Nameserver der .de bei STRATO
   liegen (`docks18.rzone.de`, `shades01.rzone.de`, geprüft).
4. **Test**: Eine Mail vom STRATO-Postfach an ein Gmail-Konto schicken, dort „Original anzeigen“ öffnen;
   erwartet: `SPF: PASS`, `DKIM: PASS`, `DMARC: PASS`. Alternativ eine Mail an die Adresse senden, die
   `https://www.mail-tester.com` anzeigt, und die Bewertung lesen.

### 1.3 fsh-documentation.com bei Canva

Die .com versendet keine Mails. Sie bekommt deshalb Einträge, die jeden Versand in ihrem Namen als
unberechtigt kennzeichnen. Weg: Canva → Einstellungen → **Domains** → **Verwalten** → **DNS-Einträge**
(Canva-Hilfe „Add, edit, or delete your domain's DNS records“). Diese Einträge bleiben beim späteren
Umzug der Website auf GitHub Pages unverändert (die Livegang-Anleitung ersetzt nur A, AAAA und CNAME).

1. TXT, Name `@`:

   ```
   v=spf1 -all
   ```

2. TXT, Name `_dmarc`:

   ```
   v=DMARC1; p=reject; rua=mailto:dmarc@fsh-documentation.de
   ```

3. Weil die Berichte an eine andere Domain gehen, muss die .de das erlauben. Bei STRATO für die .de
   einen weiteren TXT-Eintrag anlegen, Name `fsh-documentation.com._report._dmarc` (ergibt
   `fsh-documentation.com._report._dmarc.fsh-documentation.de`), Wert:

   ```
   v=DMARC1
   ```

4. Optional, falls das DNS-Formular bei Canva es zulässt: MX-Eintrag mit Priorität `0` und Ziel `.`
   (Null-MX nach RFC 7505). Dann weisen Mailserver Zustellversuche an `@fsh-documentation.com` sofort ab.

### 1.4 Prüfen

Nach dem Eintragen, frühestens nach einer Stunde, im Terminal:

```bash
nslookup -type=txt fsh-documentation.de          # erwartet: v=spf1 include:_spf.strato.com ~all
nslookup -type=txt _dmarc.fsh-documentation.de   # erwartet: v=DMARC1; p=reject; rua=mailto:dmarc@…
nslookup -type=txt fsh-documentation.com         # erwartet: v=spf1 -all
nslookup -type=txt _dmarc.fsh-documentation.com  # erwartet: v=DMARC1; p=reject; rua=mailto:dmarc@…
```

Oder ohne Terminal: `https://mxtoolbox.com/SuperTool.aspx`, dort `spf:fsh-documentation.de` und
`dmarc:fsh-documentation.de` eingeben. Das Freitags-Audit prüft die Einträge ab dem nächsten Lauf mit.

## 2. Google-Unternehmensprofil

### 2.1 Vorab entscheiden

- **Adresse anzeigen oder nicht.** Google verlangt: Wer keine Geschäftsräume mit Kundenverkehr hat,
  muss die Adresse im Profil ausblenden und stattdessen ein Einzugsgebiet angeben (Richtlinie
  „Dienstleistungsunternehmen“). Da FSH-Documentation beim Kunden und aus dem Büro arbeitet und in
  Teltow keine Kunden empfängt, ist die Empfehlung: **Adresse ausblenden, Einzugsgebiet setzen**. Die
  Anschrift wird bei der Einrichtung trotzdem eingegeben (Google braucht sie zur Bestätigung), nur nicht
  angezeigt.
- **Einzugsgebiet** (bis zu 20 Gebiete, Richtwert etwa zwei Stunden Fahrzeit): Teltow, Potsdam, Berlin,
  Kleinmachnow, Stahnsdorf, Landkreis Potsdam-Mittelmark, Landkreis Teltow-Fläming, Brandenburg an der
  Havel. Das Bundesland Brandenburg als Ganzes überschreitet die Zwei-Stunden-Regel im Osten und Norden;
  wer es trotzdem angibt, riskiert nichts weiter als eine Rückfrage bei der Prüfung.
- **Name.** Google will den Namen, unter dem das Unternehmen tatsächlich auftritt (Logo, Website):
  **FSH-Documentation**. Die Rechtsform gehört nicht in den Profilnamen; sie steht in der Beschreibung
  und im Impressum. Wer den vollen Firmennamen bevorzugt, nimmt „FSH-Documentation UG
  (haftungsbeschränkt)“; das ist zulässig, aber im Profil sperrig.
- **Schreibweise überall gleich** (Profil, Website, Impressum, freelance.de, spätere Verzeichnisse):
  FSH-Documentation · Bäckerstraße 2 D · 14513 Teltow · +49 172 9795939 ·
  Falk.Heinzmann@fsh-documentation.de · https://fsh-documentation.com/

### 2.2 Einrichten, Schritt für Schritt

1. `https://business.google.com` mit einem Google-Konto öffnen, das dauerhaft der Firma gehört (nicht
   ein privates); **Jetzt verwalten**.
2. Unternehmensname `FSH-Documentation` eingeben. Erscheint bereits ein Eintrag mit diesem Namen in
   Teltow, diesen **beanspruchen** statt neu anlegen.
3. Unternehmensart: **Dienstleistungsunternehmen** (kein Onlinehändler, kein lokales Geschäft).
4. Kategorie: im Feld nacheinander „Technische Dokumentation“, „Technischer Redakteur“, „Technische
   Redaktion“ tippen; Google zeigt nur vorhandene Kategorien. Gibt es keine passende, als primäre
   Kategorie **Beratungsunternehmen** wählen (Kern: Beratung und Erstellung technischer Dokumentation),
   als zweite Kategorie **Übersetzer** nur, wenn Übersetzung als eigene Leistung angeboten wird (die AGB
   nennen sie in § 1). Nicht mehr als zwei bis drei Kategorien; unpassende Kategorien gelten bei Google
   als Spam.
5. Adresse eingeben, Frage „Empfangen Sie Kunden an dieser Adresse?“ mit **Nein** beantworten,
   Einzugsgebiet aus 2.1 eintragen.
6. Telefon `+49 172 9795939`, Website `https://fsh-documentation.com/`.
7. Bestätigung: Google bietet je nach Fall Telefon/SMS, E-Mail, Video-Anruf, Videoaufzeichnung oder
   Postkarte an; bei ausgeblendeter Adresse meist Video. Dauer bis zu fünf Werktage. Bis dahin ist das
   Profil nicht öffentlich.
8. Nach der Bestätigung die Texte aus 2.3 eintragen, Fotos aus 2.4 hochladen, Öffnungszeiten setzen.
   Vorschlag für die Öffnungszeiten, falls keine festen Bürozeiten gelten: Montag bis Freitag
   09:00–17:00 Uhr; alternativ „Öffnungszeiten nicht angeben“ und im Profil „Termine nach Vereinbarung“.
9. Die Profil-URL (unter **Profil teilen** oder aus Google Maps) an mich geben. Ich trage sie auf der
   Regionalseite unter „Kontakt und Standort“ und in den strukturierten Daten (`sameAs`) ein.

### 2.3 Texte zum Einfügen

**Kurzbeschreibung** (Google erlaubt 750 Zeichen; dieser Text hat 715):

FSH-Documentation aus Teltow bei Berlin erstellt technische Dokumentation für Maschinen- und
Anlagenbau, Energie und Medizintechnik: Betriebs-, Montage- und Serviceanleitungen nach
DIN EN IEC/IEEE 82079-1 und EN ISO 20607, technische Unterlagen für die CE- und UKCA-Konformität,
Risikobeurteilungen nach ISO 12100 sowie Dokumentation für Medizinprodukte nach MDR und IVDR.
Dazu Dokumentencheck bestehender Anleitungen, Betreiberdokumente nach BetrSichV und
Redaktionssysteme wie SCHEMA ST4. Mehrsprachig in Deutsch, Englisch, Ukrainisch und Russisch.
Über 15 Jahre Erfahrung, Erstreaktion binnen 24 h an Werktagen, 30 Tage Service-Window nach der
Abnahme. Für Unternehmen in Berlin, Brandenburg und deutschlandweit.

**Dienstleistungen** (unter „Dienste“ je Eintrag Name und Beschreibung, höchstens 300 Zeichen):

| Name | Beschreibung |
|---|---|
| Betriebs- und Montageanleitungen | Betriebs-, Montage- und Serviceanleitungen nach DIN EN IEC/IEEE 82079-1 und EN ISO 20607, inklusive Ersatzteilkatalogen und Online-Hilfen, mehrsprachig DE/EN/UKR/RU. |
| CE-/UKCA-Konformität | Technische Unterlagen nach Maschinenrichtlinie und Maschinenverordnung (EU) 2023/1230, MDR, projektabhängig EMV, Niederspannung und Druckgeräte; auditfähige Nachweismappe. |
| Risikobeurteilung | Risikobeurteilung nach ISO 12100, ISO 13849-1 und IEC 62061 mit HAZOP, FMEA und SIL/LOPA; Risiko-Register, Maßnahmenplan und Abgleich mit der Betriebsanleitung. |
| Medizinprodukte MDR/IVDR | Technische Dokumentation nach Anhang II/III, Gebrauchsanweisung, Kennzeichnung und UDI, Risikomanagement nach ISO 14971, Usability nach IEC 62366-1, CEP/CER, PMCF. |
| Dokumentencheck | Prüfung bestehender Anleitungen auf Struktur, Rechtsbezug, Didaktik und Terminologie gegen DIN EN IEC/IEEE 82079-1 und EN ISO 20607; auf Wunsch Überarbeitung. |
| Redaktionssysteme SCHEMA ST4 | Vorbereitung und Einführung von Redaktionssystemen, Standardisierung, Modularisierung und mehrsprachige Workflows. |

**Erster Beitrag** (Google-Beitrag nach der Freischaltung, bis 1.500 Zeichen):

Ab dem 20. Januar 2027 gilt die neue Maschinenverordnung (EU) 2023/1230. Sie erlaubt digitale
Betriebsanleitungen, wenn der Zugriff auf der Maschine angegeben ist, die Anleitung herunterladbar
und druckbar bleibt und mindestens zehn Jahre online verfügbar ist. Wir prüfen bestehende Anleitungen
auf den neuen Rechtsrahmen und bereiten sie so auf, dass Papier und digitale Fassung aus einer Quelle
kommen. Erstreaktion binnen 24 h an Werktagen.

**Fragen und Antworten** (Google zeigt sie im Profil; die Antworten kann der Betreiber selbst vorab
eintragen):

- Arbeiten Sie nur in Berlin und Brandenburg? Nein, deutschlandweit; Kick-off und Abstimmungen laufen
  per Video, Vor-Ort-Termine nach Vereinbarung.
- In welchen Sprachen liefern Sie? Deutsch, Englisch, Ukrainisch und Russisch.
- Erstellen Sie auch Gebrauchsanweisungen für Medizinprodukte? Ja, nach MDR und IVDR, inklusive
  Risikomanagementakte nach ISO 14971.

### 2.4 Fotos

- Logo: `website/assets/img/icon-512.png` (quadratisch, 512 px) als Profillogo; `logo.png` als
  Titelbild ist zu klein, dafür das Zahnräder-Foto `dokumentationsprozess-1600.jpg` nehmen (Lizenz vorher
  klären, siehe README).
- Porträt `sascha-falk-heinzmann.jpg` unter „Team“ oder als weiteres Foto.
- Google empfiehlt mindestens 720 × 720 px, JPG oder PNG.

### 2.5 Danach

- Profil-URL an mich; ich ergänze Regionalseite und strukturierte Daten.
- Dieselbe Schreibweise in weiteren Verzeichnissen anlegen oder prüfen (Phase 2, 7d): tekom-
  Dienstleisterverzeichnis, Das Örtliche, 11880, wlw; freelance.de- und LinkedIn-Profil angleichen.
- Das Freitags-Audit prüft die Sichtbarkeit des Profils in der Markensuche ab dem nächsten Lauf.

Quellen: STRATO-FAQ „DNS-Einträge bei STRATO verwalten“; DNS-Abfragen am 22.09.2026 (`_spf.strato.com`,
MX/TXT/DKIM/DMARC beider Domains); Google-Hilfe „Richtlinien für die Präsentation Ihres Unternehmens auf
Google“, „Unternehmenskategorie verwalten“, „Dienstleistungen verwalten“, „Unternehmensprofile für
Dienstleistungsunternehmen“; Canva-Hilfe „Add, edit, or delete your domain's DNS records“;
Maßnahmenpaket Phase 2, Abschnitte 6 und 7d.
