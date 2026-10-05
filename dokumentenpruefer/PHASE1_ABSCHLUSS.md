# Phase 1 – Abschlussstand, 5. Oktober 2026

## Status

Die verfügbaren technischen Phase-1-Arbeiten sind umgesetzt. Die lokale Python-Abnahme
besteht mit 231 Tests. Die erweiterte CI-Abnahme wird vor Abschluss dieses Arbeitsstands
anhand ihrer Logs bestätigt. Eine vollständige Freigabe der Nutzerinstallation oder eine
fachliche Normkonformitätsfreigabe wird hiermit nicht erklärt.

## Abgleich mit dem ursprünglichen Dokumentenprüfer

Quelle ist das öffentliche Repository `Niklas137/h`, Commit
`15c06f4b2b53395aaf02fce15f7b44b7d5ea52c2` vom 21. Mai 2026.
Alle 24 Regeln sind übernommen: acht Basisregeln, acht DIN-Regeln und acht CE-Regeln.
ID, Suchwörter, Bereich, Fehlerklasse, deutsche Empfehlung, Gewichtung und vorhandene
Pflichtfelder stimmen überein. Ergänzte Übersetzungen ändern diese Felder nicht.
Die Referenz und ihr Quellcommit sind in `tests/fixtures/originalregeln.json` festgehalten;
`tests/test_regelbestand.py` prüft diesen Abgleich dauerhaft.

Das bestätigt die vollständige Übernahme des vorhandenen Regelwerks, nicht dessen
normative Vollständigkeit. Der ursprüngliche Prüfer und die Web-App verwenden
Schlüsselwortregeln. Eine möglicherweise neuere, nur lokal vorhandene Regelfassung
kann ohne diese Datei nicht abgeglichen werden.

## Abgesicherter Funktionsumfang

- Konten, Erstanmeldung, Passwortregeln, Sperre, Sitzungen und Rollen.
- Word/PDF, Tabellen, Scan-Hinweise, ungültige Dateien und Regelkataloge.
- PDF-Berichte in vier Sprachen, ZIP, Ablage, Neustart und Wiederherstellung.
- Bedienung auf schmalen Bildschirmen, Einstellungen und Kontentrennung nach Logout.
- Leere Überschriften, häufige Negationen, PDF-Zeilen und Satzlängen.
- Positive und negative technische Sollfälle für jede der 24 Regeln.
- Zusätzlicher Fehler behoben: Eine Überschrift darf einen im Absatz negierten Treffer
  nicht nachträglich wieder als vorhanden bewerten. Vor der Korrektur schlugen alle
  24 entsprechenden Gegenproben fehl; danach bestehen sie.
- Lokale Abnahme über `abnahme.command`, mit isolierten Testdaten und Protokoll.
- Browserabnahme für Chromium und WebKit im Linux-/macOS-Workflow. WebKit ist der
  Safari zugrunde liegende Browsermotor; der Test ist kein Test der installierten Safari-App.

Score, Gewichte, Ampelschwellen und der offene fachliche Freigabestatus bleiben erhalten.
Phase-2-Funktionen (Passwortanfrage, MFA, vollständige Oberflächenübersetzung) sind nicht Teil
von Phase 1.

## Was für eine vollständige Freigabe noch tatsächlich erfolgen muss

| Punkt | Zuständigkeit / Nachweis |
| --- | --- |
| Tatsächliche Mac-Installation | Separaten Stand nach ANLEITUNG_MAC.md übernehmen und `abnahme.command` ausführen. |
| Native Bedienung | Finder-Start, Doppelstart, Safari sowie Apple-Mail-Entwurf mit Anhang auf dem Nutzer-Mac prüfen. Nichts versenden. |
| Installationseinstellungen | Eigene Kontaktangaben, freigegebene Rechtstexte und Verifizierungsverfahren festlegen; SMTP nur mit echten, extern gehaltenen Zugangsdaten. |
| Fachliche Abnahme | Technische Sollfälle sind kein Ersatz für persönlich freigegebene Sollbefunde an echten Dokumenten. |
| Produktive Übernahme | Bestehende Daten sichern, lokale Regeln vergleichen und die getrennten Entwicklungsstände bewusst übernehmen. |

Diese Punkte können aus der Entwicklungsumgebung nicht als erledigt bestätigt werden.
Die Anleitung benennt die konkreten Handlungen; Konten, Rechtstexte und Zugangsdaten
wurden nicht erfunden. Der Claude-Branch, main und die ursprüngliche App bleiben unberührt.
