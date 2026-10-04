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
- Seitenleiste (seit 2. Oktober): oben Konto mit Rolle, dann Prüfen, Verlauf, Einstellungen, Mitarbeiter (nur Admin),
  unten Sprache, Helligkeit, Hilfe, Abmelden. Kopfzeile nur Seitentitel, Kurztext und eine Aktion. Sprache und Helligkeit wirken sofort.
- Mitarbeiterverwaltung als eigene Seite: anlegen, bearbeiten, deaktivieren, weich löschen mit E-Mail-Bestätigung,
  wiederherstellen, Protokoll. Rechte serverseitig (401/403), letzter aktiver Admin geschützt.
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
- PDF-Layout: Seitenrand 16 mm, Tabellen füllen die Breite (`BREITE` in berichte.py). Fundtabelle 8 pt, Trennung an Bindestrichen (`embeddedHyphenation`), Spaltenbreiten gegen die längsten Wörter aller vier Sprachen geprüft; Fuß ohne Platzhalter. Bei neuen langen Wörtern in Regeln oder Übersetzungen Spaltenbreiten nachmessen.

## Heute (2. Oktober 2026)

- Arbeitsbranch `claude/explanation-code-example-2dt2yu` setzt auf `codex/dokumentenpruefer-satzlaenge` auf (Phase-1-Abnahme, 113 Tests).
  Der Claude-Commit `b4d6425` (Berichte: Tabellen ohne Umbruch im Wort, Fuß ohne Platzhalter) ist auf Niklas' Entscheidung
  übernommen und in `app/pruefer/berichte.py` von Hand mit der Codex-Fassung zusammengeführt: Codex' Fundstellenzeile,
  `deepcopy` der Story und `ablegen()` bleiben, Claudes Seitenrand, Silbentrennung und Spaltenbreiten kommen dazu.
  Dabei fehlende Singular-Texte `emp_satz_1` für uk und ru ergänzt (vom Qualitätstest X3 gefunden).

## Offen, braucht Niklas

- Name, E-Mail-Adresse und Rolle für die Konten von Niklas und Falk.
- Regeldateien Basis und CE: prüfen, ob auf dem Mac eine neuere Fassung als vom 21. Mai liegt; Übersetzungen der Empfehlungen (en, uk, ru) fehlen noch.
- Impressum und Datenschutz: am 4. Oktober aus den Website-Texten übernommen und auf die lokale App zugeschnitten
  (Bereich `data-pane="recht"` in `app/static/index.html`). Keine Rechtsberatung; vor der Übergabe an Falk vom Rechtsprüfer
  gegenlesen lassen, zusammen mit den Website-Texten.
- Telefonnummer, Zeiten und Support-Adresse für die Hilfe (`DP_SUPPORT`, `DP_TELEFON`, `DP_ZEITEN`).
- SMTP für den Code (nur als Umgebungsvariable) oder `DP_VERIFIZIERUNG=aus`.
- Merge des Branches nach `main`.
