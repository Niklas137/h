# Ablage, Stand und Entscheidungen

Stand: 1. Oktober 2026. Bei Änderungen diese Datei mitpflegen.

## Wo was liegt

| Was | Wo |
|---|---|
| Code der Web-App | Repo h, Branch `claude/dokumentenpruefer-webapp`, Ordner `dokumentenpruefer/` |
| README (Installation, Konfiguration, Befehle) | `dokumentenpruefer/README.md` |
| Tests | `dokumentenpruefer/tests/` (pytest) |
| Regeldateien | `dokumentenpruefer/regeln/` (nur `normlogik_82079.json` im Repo; `pruefkatalog.json` und `ce_logik.json` liegen auf Niklas' Mac) |
| Alte Streamlit-App (Rückfall) | `app.py` im Repo-Stamm, `normlogik_82079.json` daneben |
| Google Drive | Ordner „Dokumenten prüfung / FSH Programm / Dokumentenpruefer_Web-App_2026-10-01" mit README, Plan und „Stand und Testprotokoll" als Google Docs |
| Plan (Claude Doc) | „Konto-Einstellungen Dokumentenprüfer: Schritt-für-Schritt-Plan", fünf Phasen, Infopool |
| Design-Canvas, Handy-Prototyp, FSH-Design-System | Claude-Artefakte, Links stehen im Plan |
| Laufzeitdaten | `dokumentenpruefer/daten/` (SQLite, Berichte je Prüfung, Geheimnis), nicht versioniert |
| Abgelegte Berichte | `dokumentenpruefer/output/` oder `DP_OUTPUT` |

## Entschiedene Punkte (nicht neu diskutieren)

- Technik: eigener Web-Dienst (FastAPI, SQLite, HTML/CSS/JS ohne Framework), kein Streamlit.
- Startmaske für alle gleich, dunkel. Erstanmeldung: Einmal-Passwort vom Admin, Code an die E-Mail-Adresse,
  dann eigenes Passwort (mindestens 14 Zeichen, ein Großbuchstabe, ein Sonderzeichen). Konten legt nur ein Admin an.
- Kopfleiste: Sprache, Helligkeit, Einstellungen, Hilfe. Sprache und Helligkeit wirken sofort.
- Einstellungen enthalten alles Weitere einschließlich Impressum, Datenschutz, Info. Speichern-Knopf oben, Zurück-Knopf.
- Kein Register „Prüfer-Vorgaben" in den Einstellungen. Unter „Sprachen" nur Nachlesen.
- Berichtssprache: Basis ist die Oberflächensprache; je Prüfung eine Zusatzsprache oder keine, Auswahl auf der Prüfseite.
  Je Sprache zwei PDFs: Prüfbericht (intern, mit Gewichtung und Aufwand) und Fachbericht (Kunde, ohne beides).
- Ergebnis-Ansicht: ① Ergebnis, ② Berichte mit PDF je Sprache, ③ Weitergabe (E-Mail-Entwurf nie gesendet, ZIP,
  Ablage in output, Abschließen), Funde im Detail zum Aufklappen.
- Benachrichtigung: Pop-up „Prüfbericht fertig … Der Bericht liegt bereit.", keine Bestätigungs-E-Mails.
- Kontakttext in der Hilfe: Fassung A mit „Antwort innerhalb von 24 Stunden"; derselbe Text als Autoantwort des
  Support-Postfachs mit „Danke, deine Anfrage ist angekommen." davor. Für Kundenvorlagen die Sie-Fassung.
- Oberfläche vorerst deutsch; Berichte in de, en, uk, ru. Oberfläche in den anderen Sprachen ist Phase 2.
- In Kundenkommunikation den Wohnsitz in der Ukraine nicht erwähnen.

## Phasen laut Plan

1. Konto-Modul bauen und testen: umgesetzt, wartet auf Niklas' Klick-Durchlauf (Tor 1).
2. Einbau in den Prüfer, Konten für Niklas und Falk: Prüfteil umgesetzt, Konten offen (Tor 2).
3. Neutrale Kundenvorlage mit `kunde.json`, Abbott Bridge ansehen.
4. Präsentation für Falk, fünf bis sechs Minuten, live im Tool.
5. Übergabe als ZIP, Falk bestätigt Installation und Tests.

## Offen, braucht Niklas

- Name, E-Mail-Adresse und Rolle für die Konten von Niklas und Falk.
- Regeldateien `pruefkatalog.json` und `ce_logik.json` nach `dokumentenpruefer/regeln/` kopieren.
- Impressum und Datenschutz (Bereich `data-pane="recht"` in `app/static/index.html`).
- Telefonnummer, Zeiten und Support-Adresse für die Hilfe (`DP_SUPPORT`, `DP_TELEFON`, `DP_ZEITEN`).
- SMTP für den Code (nur als Umgebungsvariable) oder `DP_VERIFIZIERUNG=aus`.
- Merge des Branches nach `main`.
