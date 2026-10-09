#!/bin/bash
# Startet den Dokumentenprüfer auf dem Mac. Doppelklick im Finder genügt.
# Beim ersten Start wird eine Python-Umgebung angelegt und die Pakete werden installiert.
cd "$(dirname "$0")" || exit 1

if [ ! -d ".venv" ]; then
  echo "Lege Python-Umgebung an ..."
  python3 -m venv .venv || { echo "Python 3 fehlt. Bitte python3 installieren."; read -r -p "Enter zum Schließen"; exit 1; }
  ./.venv/bin/pip install --quiet --upgrade pip
  ./.venv/bin/pip install --quiet -r requirements.txt
fi

# Erstes Konto: Admin anlegen, wenn noch keines da ist.
if ! ./.venv/bin/python -m app.verwaltung liste 2>/dev/null | grep -q "@"; then
  echo "Noch kein Konto vorhanden. Admin-Konto anlegen:"
  read -r -p "E-Mail-Adresse: " ADMIN_EMAIL
  read -r -p "Name: " ADMIN_NAME
  ./.venv/bin/python -m app.verwaltung admin --email "$ADMIN_EMAIL" --name "$ADMIN_NAME"
  echo "Das Einmal-Passwort oben notieren. Es wird nicht noch einmal angezeigt."
fi

echo "Dokumentenprüfer läuft unter http://localhost:8765 (Beenden mit Ctrl+C)"
( sleep 2; open "http://localhost:8765" ) &
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8765
