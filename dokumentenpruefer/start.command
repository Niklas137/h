#!/bin/bash
# Startet den Dokumentenprüfer auf dem Mac. Doppelklick im Finder genügt.
# Beim ersten Start wird eine Python-Umgebung angelegt und die Pakete werden installiert.
cd "$(dirname "$0")" || exit 1
umask 077

if [ ! -d ".venv" ]; then
  echo "Lege Python-Umgebung an ..."
  python3 -m venv .venv || { echo "Python 3 fehlt. Bitte python3 installieren."; read -r -p "Enter zum Schließen"; exit 1; }
  ./.venv/bin/pip install --quiet --upgrade pip || exit 1
fi

# Nach abgebrochener Installation beim nächsten Start erneut versuchen.
if [ ! -f .venv/dp-installiert ] || ! cmp -s requirements.txt .venv/dp-installiert; then
  ./.venv/bin/pip install --quiet -r requirements.txt || { echo "Installation fehlgeschlagen. Bitte die Fehlermeldung prüfen und erneut starten."; exit 1; }
  cp requirements.txt .venv/dp-installiert || exit 1
fi

exec ./.venv/bin/python -m app.start "$@"
