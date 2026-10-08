# Vorschlag: zentrales Postfach info@fsh-documentation.de

Stand 01.10.2026, Vorschlag von Niklas zur Abstimmung mit Falk. Noch nicht eingerichtet.

## Warum

- **Eine Adresse für Anfragen.** Website, Rechtstexte, Profile und Signaturen nennen dieselbe Adresse;
  Kunden müssen nicht wissen, wer gerade zuständig ist.
- **Vertretung ohne Umbau.** Wer Urlaub hat oder ausfällt, wird im Postfach vertreten, nicht auf der Website.
- **Übersicht.** Kundenanfragen laufen getrennt von persönlicher Post und Rechnungen auf; die Sortierung in
  Kategorien (Anfrage, Angebot, Projekt, Rechnung, Sonstiges) wird einfacher.
- **Die Website nennt die Adresse heute schon.** In den ukrainischen Rechtstexten steht sichtbar
  `info@fsh-documentation.de`, das Postfach dazu gibt es nicht. Mails dorthin kommen zurück.

## Wie, bei STRATO (zehn Minuten)

1. Kundenlogin → E-Mail → E-Mail-Verwaltung → neue Adresse `info@fsh-documentation.de` anlegen.
2. Entweder als **Postfach** (eigener Posteingang, in Apple Mail bei Niklas und Falk einbinden) oder als
   **Weiterleitung** an `Falk.Heinzmann@fsh-documentation.de` und `niklas.heinzmann@fsh-documentation.de`
   (beide bekommen jede Mail, Antwort geht vom persönlichen Konto raus).
3. Empfehlung: Postfach, bei beiden eingebunden. Nur so bleibt sichtbar, wer schon geantwortet hat.
4. Antworten von `info@` aus: in Apple Mail das Postfach als eigenes Konto, Absendername
   „FSH-Documentation“. SPF, DKIM und DMARC gelten für die Domain, also automatisch auch für `info@`.

## Was sich danach ändert

| Stelle | Heute | Dann |
|---|---|---|
| Canva-Design, ukrainische Rechtstexte (zwei tote Links, Checkliste B4) | `mailto:info@fsh-documentation.com` und ein Tippfehler | beide Stellen `info@fsh-documentation.de` |
| Neue Website, Kontaktblock und Fußzeile (`website/inhalt/site.json`) | `Falk.Heinzmann@fsh-documentation.de` | wahlweise `info@`, eine Zeile ändern und neu bauen |
| Impressum | `Falk.Heinzmann@` | kann bleiben; eine persönliche Adresse im Impressum ist zulässig |
| Google-Unternehmensprofil, freelance.de, Signaturen | gemischt | einheitlich `info@` für Anfragen |

Entscheidet Falk dagegen, bleiben beide toten Links auf `Falk.Heinzmann@fsh-documentation.de` zu setzen, sonst
ändert sich nichts.
