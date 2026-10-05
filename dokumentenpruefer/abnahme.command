#!/bin/bash
# Lokale technische Abnahme mit ausschließlich erzeugten Testdaten.
set -u
set -o pipefail
cd "$(dirname "$0")" || exit 1
umask 077

test_python=${DP_TEST_PYTHON:-.venv/bin/python}
if ! command -v "$test_python" >/dev/null 2>&1; then
  echo "Python-Umgebung fehlt. Zuerst die Schritte 3 und 4 in ANLEITUNG_MAC.md ausführen."
  exit 1
fi

protokollordner=$(mktemp -d "${TMPDIR:-/tmp}/dp-abnahme.XXXXXX") || exit 1
protokoll="$protokollordner/Abnahme.txt"
{
  echo "Dokumentenprüfer: lokale technische Abnahme"
  date -u '+Zeit (UTC): %Y-%m-%d %H:%M:%S'
  "$test_python" --version
  echo "Testdaten und Protokoll: $protokollordner"
  echo "Keine Prüfung der produktiven Konten oder SMTP-Verbindung."
} | tee "$protokoll"

if DP_DATEN="$protokollordner/daten" DP_OUTPUT="$protokollordner/output" DP_SMTP_HOST="" \
  "$test_python" -m pytest tests -q --tb=short --show-capture=no 2>&1 | tee -a "$protokoll"; then
  cat <<'TEXT' | tee -a "$protokoll"

AUTOMATISCHE PYTHON-ABNAHME: BESTANDEN
Noch nicht durch diesen Lauf bestätigt:
[ ] Anwendung im Safari-Browser öffnen und Word/PDF prüfen.
[ ] Beide Berichtstypen, Zusatzsprache und ZIP öffnen.
[ ] start.command per Finder starten, beenden und erneut starten.
[ ] Doppelstart öffnet die eigene laufende Installation.
[ ] Apple Mail öffnet den Entwurf mit richtigem Anhang; nichts senden.
[ ] Eigene Regeldateien mit dem ausgelieferten Stand vergleichen.
[ ] Support, Rechtstexte und Verifizierung für den vorgesehenen Betrieb festlegen.
[ ] Fachliche Sollbefunde und Abweichungen persönlich beurteilen.

Diese offenen Felder nur nach tatsächlicher Prüfung bestätigen.
TEXT
  echo "Protokoll: $protokoll"
else
  echo "ABNAHME FEHLGESCHLAGEN. Protokoll: $protokoll" | tee -a "$protokoll"
  exit 1
fi
