# Ablage, Stand und Entscheidungen

Stand: 1. Oktober 2026. Bei Änderungen diese Datei mitpflegen.

## Wo was liegt

| Was | Wo |
|---|---|
| Code der Web-App | Repo h, Branch `claude/dokumentenpruefer-webapp`, Ordner `dokumentenpruefer/` |
| README (Installation, Konfiguration, Befehle) | `dokumentenpruefer/README.md` |
| Tests | `dokumentenpruefer/tests/` (pytest) |
| Regeldateien | `dokumentenpruefer/regeln/`: alle drei im Repo. `pruefkatalog.json` und `ce_logik.json` am 1. Oktober 2026 aus der Git-Historie (Commit vom 21. Mai 2026) wiederhergestellt; sie waren am 7. September im Commit „reg" versehentlich gelöscht worden |
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
- Berichtssprachen: ein bis zwei je Prüfung, frei auf der Prüfseite gewählt (seit 5. Oktober), unabhängig von der Oberflächensprache. API-Feld `sprachen`.
  Je Sprache zwei PDFs: Prüfbericht (intern, mit Gewichtung und Aufwand) und Fachbericht (Kunde, ohne beides).
- Ergebnis-Ansicht: ① Ergebnis, ② Berichte mit PDF je Sprache, ③ Weitergabe (E-Mail-Entwurf nie gesendet, ZIP,
  Ablage in output, Abschließen), Funde im Detail zum Aufklappen.
- Benachrichtigung: Pop-up „Prüfbericht fertig … Der Bericht liegt bereit.", keine Bestätigungs-E-Mails.
- Kontakttext in der Hilfe: Fassung A mit „Antwort innerhalb von 24 Stunden"; derselbe Text als Autoantwort des
  Support-Postfachs mit „Danke, deine Anfrage ist angekommen." davor. Für Kundenvorlagen die Sie-Fassung.
- Oberfläche und Berichte in de, en, uk, ru (seit 5. Oktober). Texte der Oberfläche in `app/static/i18n.js`, API-Meldungen in `app/meldungen.py`, Sprachkopf `X-Sprache`. Zitate aus dem Dokument bleiben in dessen Sprache; uk und ru von Niklas gegenlesen lassen.
- In Kundenkommunikation den Wohnsitz in der Ukraine nicht erwähnen.

## Phasen laut Plan

1. Konto-Modul bauen und testen: Tor 1 am 1. Oktober 2026 bestanden. Niklas hat die App auf dem Mac installiert, sich angemeldet, Word- und PDF-Dokumente geprüft, PDFs geöffnet.
2. Einbau in den Prüfer, Konten für Niklas und Falk: Prüfteil umgesetzt, Niklas' Konto aktiv, Konto für Falk offen (Tor 2).
3. Neutrale Kundenvorlage mit `kunde.json`, Abbott Bridge ansehen.
4. Präsentation für Falk, fünf bis sechs Minuten, live im Tool.
5. Übergabe als ZIP, Falk bestätigt Installation und Tests.

## Heute geklärt (1. Oktober 2026)

- Variante A aus der Videoanalyse umgesetzt: Prüfung im Arbeitsfaden, kurze Transaktion, Statuspanel mit Phasen. Jobschicht mit Abbruch und Figuren bewusst nicht gebaut.
- Auf dem Mac liegt ein `git stash` „Jobschicht-Versuch vom Mac, 1. Oktober" mit einem fremden, unfertigen Umbau (db.py, main.py, app.css, index.html). Nicht übernehmen, bei Bedarf ansehen.
- Im Stammordner von h liegen auf dem Mac zwei leere, unversionierte Dateien `ce_logik.json` und `pruefkatalog.json`; `.DS_Store` ist versehentlich versioniert. Beides beim Merge nach main aufräumen.

- Codex-Commit `d082a41` (1. Oktober, 23:46) auseinandergenommen, Entscheidung C von Niklas: Ampel Grün/Gelb/Rot nach Score wie in app.py, alte Wortwahl (Score, Funde, Fazit), ein Satz zur Vorprüfung in jedem Bericht und der Kundenmail; strenge Regelprüfung, abgesicherte Sperre und die Tests aus test_p0.py bleiben.
- Arbeitsregel seit 1. Oktober: Claude arbeitet nur auf `claude/dokumentenpruefer-webapp`, ChatGPT/Codex nur auf `codex/dokumentenpruefer` mit eigener Arbeitskopie. Zusammengeführt wird erst nach Prüfung.
- 2. Oktober: Codex-Frontend-Rest (`app.js`, Abbrechen-Knopf und Ladeoverlay) auf dem Mac als Stash „Jobschicht-Frontend vom Mac, 1. Oktober" abgelegt, neben dem Backend-Stash. Codex-Branch `codex/dokumentenpruefer` existiert seitdem auf GitHub.
- 5. Oktober, Auftrag von Niklas: (1) bis zu 20 Dateien je Prüfung, (2) Benutzer löschen nur als Inhaber, (3) einzelne Prüfpunkte wählbar, (4) Berichte vollständig übersetzt, (5) Oberfläche in vier Sprachen, (6) Abnahmetests mit seinen Beispieldokumenten, (7) später Regeln in der Verwaltung pflegen. Inhaber = erstes Konto; Löschen entfernt auch Prüfungen und Berichte der Person, output/ bleibt.
- PDF-Layout: Seitenrand 16 mm, Tabellen füllen die Breite (`BREITE` in berichte.py). Fundtabelle 8 pt, Trennung an Bindestrichen (`embeddedHyphenation`), Spaltenbreiten gegen die längsten Wörter aller vier Sprachen geprüft; Fuß ohne Platzhalter. Bei neuen langen Wörtern in Regeln oder Übersetzungen Spaltenbreiten nachmessen.

## Offen, braucht Niklas

- Name, E-Mail-Adresse und Rolle für die Konten von Niklas und Falk.
- Regeldateien Basis und CE: prüfen, ob auf dem Mac eine neuere Fassung als vom 21. Mai liegt. Übersetzungen (en, uk, ru) seit 5. Oktober in allen drei Dateien; uk und ru von Niklas gegenlesen lassen.
- Impressum und Datenschutz (Bereich `data-pane="recht"` in `app/static/index.html`).
- Telefonnummer, Zeiten und Support-Adresse für die Hilfe (`DP_SUPPORT`, `DP_TELEFON`, `DP_ZEITEN`).
- SMTP für den Code (nur als Umgebungsvariable) oder `DP_VERIFIZIERUNG=aus`.
- Merge des Branches nach `main`.
