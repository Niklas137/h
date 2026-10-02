# Qualitätsvorgaben Dokumentenprüfer (nach ISO 25010)

Stand: 2. Oktober 2026. Gilt für jede Änderung an `dokumentenpruefer/`, egal ob von Niklas, Claude Code
oder Codex. Grundsatz: Eine Vorgabe zählt nur, wenn sie messbar ist und ein Test sie prüft.
„Schnell" ist keine Vorgabe, „unter 200 ms" schon. Jede neue Funktion bringt ihre Anforderung
hier und ihren Test unter `tests/` mit, bevor sie als fertig gilt.

Prüfbefehle:

```bash
./.venv/bin/python -m pytest tests -q -p no:warnings     # alle Vorgaben mit [T]
./.venv/bin/python -m pyflakes app tests                  # W1
node tests/browser_smoke.cjs                               # B1, B2, Z2 im echten Browser
```

Kennzeichnung: **[T]** automatisch geprüft durch den genannten Test, **[B]** nur Browser-Abnahme,
**[offen]** Vorgabe steht, Prüfung fehlt noch oder braucht eine Entscheidung von Niklas.

## 1. Funktionale Eignung

| Nr. | Vorgabe | Prüfung |
|---|---|---|
| F1 | Prüfung ist eine Vorprüfung per Schlüsselwortsuche; kein Bericht und keine Mail behauptet eine fachliche Freigabe | [T] `test_p0.py::test_stichwortliste_ist_keine_freigabe`, `test_pdf_kennzeichnet_vorpruefung_und_ungeprueftes` |
| F2 | Score, Ampel, Fazit, CE-To-dos stimmen mit der alten Streamlit-App überein | [T] `test_pruefung.py` |
| F3 | Je gewählter Sprache entstehen genau zwei PDFs (Prüfbericht, Fachbericht) | [T] `test_pruefung.py`, Browser-Abnahme |
| F4 | Scan-Seiten ohne Textebene werden gemeldet, nie stillschweigend als geprüft gezählt | [T] `test_pruefung.py`, `test_qualitaet.py::test_f4_scan_ohne_text_wird_abgewiesen` |

## 2. Leistungseffizienz

| Nr. | Vorgabe | Prüfung |
|---|---|---|
| L1 | `/api/status` und `/api/ich` antworten in unter 200 ms (Median aus 20 Aufrufen, lokal) | [T] `test_qualitaet.py::test_l1_api_antwortet_unter_200ms` |
| L2 | Ein Word-Dokument mit 200 Absätzen ist samt 4 PDFs in unter 10 s geprüft | [T] `test_qualitaet.py::test_l2_pruefung_200_absaetze_unter_10s` |
| L3 | Oberfläche ohne Framework: `index.html`, `app.js`, `app.css` zusammen unter 160 KB, kein externes Skript, keine externe Schrift | [T] `test_qualitaet.py::test_l3_oberflaeche_klein_und_offline` |
| L4 | Der Server bleibt während einer Prüfung bedienbar (Arbeitsfaden, kurze Transaktion) | [T] `test_pruefung.py` Fortschritts-Zeilenstrom; Browser-Abnahme „Langer Lauf" |

## 3. Kompatibilität

| Nr. | Vorgabe | Prüfung |
|---|---|---|
| K1 | Jede Fehlerantwort der API ist JSON mit dem Feld `fehler`, nie HTML und nie ein Stacktrace | [T] `test_qualitaet.py::test_k1_fehler_immer_json` |
| K2 | Eine Datenbank aus einer älteren Fassung läuft nach dem Start weiter (Spalten werden angehängt, nie Tabellen neu gebaut) | [T] `test_team.py::test_migration_haengt_spalte_an` |
| K3 | Gelesen werden `.docx` und `.pdf`; alles andere wird mit 400 abgewiesen, nicht mit 500 | [T] `test_qualitaet.py::test_k3_fremde_dateien_400` |
| K4 | Läuft auf macOS (Apple Silicon) und Linux mit Python 3.11+ ohne Compiler | Phase-1-Abnahme (README); [offen] automatischer macOS-Lauf |

## 4. Benutzerfreundlichkeit (Interaktionsfähigkeit)

| Nr. | Vorgabe | Prüfung |
|---|---|---|
| B1 | Kein horizontaler Überlauf bei 320, 390, 844 und 1365 px Breite | [B] `browser_smoke.cjs` |
| B2 | Jedes Eingabefeld hat ein sichtbares `label`, jeder Symbolknopf ein `aria-label` | [T] `test_qualitaet.py::test_b2_felder_beschriftet` |
| B3 | Fehlermeldungen sind deutsche Sätze, die sagen, was zu tun ist (kein „Error 500", keine Feldnamen aus dem Code) | [T] `test_qualitaet.py::test_b3_fehlermeldungen_sind_saetze` |
| B4 | Der aktive Menüpunkt trägt `aria-current="page"`; Löschen verlangt die E-Mail-Adresse zur Bestätigung | [B] `browser_smoke.cjs`; [T] `test_team.py::test_loeschen_ist_weich_und_braucht_bestaetigung` |
| B5 | Textgröße und Dichte sind je Konto einstellbar, Dunkel und Hell vollständig | [B] `browser_smoke.cjs` |

## 5. Zuverlässigkeit

| Nr. | Vorgabe | Prüfung |
|---|---|---|
| Z1 | Fehlerhafte oder fehlende Regeldateien brechen die Prüfung ab, ohne Datensatz und ohne halbe PDFs | [T] `test_p0.py::test_api_regelfehler_ohne_pruefung_oder_berichte` |
| Z2 | Nach Neustart sind Konten, Prüfungen und PDFs unverändert vorhanden | [T] `test_betrieb.py::test_echter_server_neustart_doppelstart_und_restore` |
| Z3 | Sicherung ist prüfsummengesichert; manipulierte Archive werden abgelehnt, Wiederherstellung nur in einen leeren Ordner | [T] `test_betrieb.py` |
| Z4 | Ablage überschreibt nie: gleicher Inhalt wird wiederverwendet, sonst nächste Version | [T] `test_pruefung.py`, `app/ablage.py` |
| Z5 | Kein Aufruf der API endet mit 500 bei ungültiger Eingabe (leerer Body, falscher Typ, fehlende Felder) | [T] `test_qualitaet.py::test_z5_ungueltige_eingaben_kein_500` |

## 6. Sicherheit

| Nr. | Vorgabe | Prüfung |
|---|---|---|
| S1 | Jede Admin-Route antwortet ohne Sitzung mit 401 und als Mitglied mit 403, für GET, POST, PATCH und DELETE | [T] `test_team.py::test_ohne_anmeldung_401`, `test_mitglied_bekommt_403` |
| S2 | Keine Antwort der API enthält `passwort_hash`, `einmal_hash`, `code_hash` oder einen Sitzungs-Token | [T] `test_qualitaet.py::test_s2_keine_geheimnisse_in_antworten` |
| S3 | Sitzungs-Cookie ist `HttpOnly` und `SameSite=Lax`; Sitzungen liegen nur als SHA-256-Hash in der Datenbank | [T] `test_qualitaet.py::test_s3_cookie_httponly_samesite` |
| S4 | Passwörter: argon2, mindestens 14 Zeichen, Großbuchstabe, Sonderzeichen; 8 Fehlversuche sperren 15 Minuten; Erstanmeldung hebt eine Sperre nicht auf | [T] `test_konto.py`, `test_p0.py::test_erstanmeldung_hebt_sperre_nicht_auf` |
| S5 | Der letzte aktive Admin kann nicht gelöscht, deaktiviert oder herabgestuft werden; niemand ändert sich selbst | [T] `test_team.py::test_letzter_aktiver_admin_bleibt_erhalten`, `test_admin_schuetzt_sich_selbst` |
| S6 | Codes und Einmal-Passwörter stehen in keinem Log und keiner Datei außerhalb von `daten/` | [T] `test_betrieb.py::test_verifizierungsschluessel_landeten_nicht_in_logs` |
| S7 | Jede Admin-Aktion steht im Protokoll mit Zeit, Akteur, Aktion und Ziel; das Protokoll enthält keine Geheimnisse | [T] `test_team.py::test_protokoll_enthaelt_keine_geheimnisse` |
| S8 | Uploads sind auf 25 MB begrenzt und werden nur im Speicher gelesen, nie dauerhaft abgelegt | [T] `test_qualitaet.py::test_s8_upload_grenze` |

## 7. Wartbarkeit

| Nr. | Vorgabe | Prüfung |
|---|---|---|
| W1 | `pyflakes app tests` ohne Befund; keine `TODO`/`FIXME` im Code | [T] `test_qualitaet.py::test_w1_pyflakes_und_keine_todos` |
| W2 | Keine Python-Datei über 800 Zeilen, keine Funktion über 120 Zeilen | [T] `test_qualitaet.py::test_w2_dateien_und_funktionen_begrenzt` |
| W3 | Jedes Modul unter `app/` steht mit einem Satz im Abschnitt „Aufbau" der README | [T] `test_qualitaet.py::test_w3_module_in_readme` |
| W4 | Jede Vorgabe in dieser Datei mit [T] nennt einen Test, den es gibt | [T] `test_qualitaet.py::test_w4_vorgaben_haben_tests` |
| W5 | Abhängigkeiten nur aus `requirements.txt`; die Oberfläche ohne Build-Schritt | [T] `test_qualitaet.py::test_w5_nur_erklaerte_abhaengigkeiten` |

## 8. Flexibilität (Portabilität, Anpassbarkeit)

| Nr. | Vorgabe | Prüfung |
|---|---|---|
| X1 | Alles Installationsabhängige kommt aus Umgebungsvariablen mit Präfix `DP_`; kein absoluter Pfad und kein Zugangsdatum im Code | [T] `test_qualitaet.py::test_x1_keine_absoluten_pfade_oder_zugangsdaten` |
| X2 | Regelsätze sind Daten (`regeln/*.json`); ein neuer Regelsatz braucht keine Codeänderung an der Prüflogik | [T] `test_p0.py::test_regelschema_wird_geprueft` (Schema), [offen] Test mit viertem Regelsatz |
| X3 | Berichtstexte für de, en, uk, ru liegen in `texte.py`; jede Kennung existiert in allen vier Sprachen | [T] `test_qualitaet.py::test_x3_texte_in_allen_sprachen` |

## 9. Betriebssicherheit (Safety)

| Nr. | Vorgabe | Prüfung |
|---|---|---|
| P1 | Die App sendet nie eine E-Mail an Kunden: der einzige SMTP-Versand ist der Verifizierungscode an das eigene Konto; der Mail-Entwurf bleibt Entwurf | [T] `test_qualitaet.py::test_p1_kein_mailversand_ausser_code` |
| P2 | Originaldokumente werden nie verändert; Prüfungen arbeiten auf einer Kopie im Speicher | [T] `test_qualitaet.py::test_p2_original_bleibt_unveraendert` |
| P3 | Löschen von Konten ist weich; Prüfungen bleiben zuordenbar | [T] `test_team.py::test_loeschen_ist_weich_und_braucht_bestaetigung` |
| P4 | Wiederherstellung einer Sicherung schreibt nie in einen bestehenden Ordner | [T] `test_betrieb.py::test_sicherung_wiederherstellung_mit_berichten` |

## Arbeitsregel für Agenten

1. Vor einer Änderung die betroffenen Zeilen dieser Datei lesen.
2. Neue Funktion: zuerst die Vorgabe mit Zahl oder klarer Bedingung hier eintragen, dann den Test schreiben, dann den Code.
3. Fertig heißt: Vorgabe steht, Test läuft grün, Prüfbefehle oben ohne Befund.
4. Was sich nicht automatisch prüfen lässt, wird als [B] oder [offen] markiert und im Ergebnis genannt.
