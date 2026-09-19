#!/bin/bash
# Richtet Chromium für den Proxy der Claude-Umgebung ein: importiert die Proxy-CA in den
# NSS-Zertifikatspeicher, den das vollständige Chromium liest. Idempotent. Ohne Proxy-CA
# (lokale Umgebung) tut das Skript nichts. Aufruf: bash seo-audit/tools/browser_setup.sh
set -e
CA=/root/.ccr/agent-proxy-ca.crt
if [ ! -f "$CA" ]; then echo "keine Proxy-CA gefunden, nichts zu tun"; exit 0; fi
if ! command -v certutil >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get install -y -q libnss3-tools >/dev/null 2>&1 || { apt-get update -q >/dev/null 2>&1 && apt-get install -y -q libnss3-tools >/dev/null 2>&1; }
fi
DB="${HOME:-/root}/.pki/nssdb"
mkdir -p "$DB"
[ -f "$DB/cert9.db" ] || certutil -d "sql:$DB" -N --empty-password
if certutil -d "sql:$DB" -L 2>/dev/null | grep -q "^ccr-agent-proxy"; then
  echo "Proxy-CA bereits im NSS-Speicher"
else
  certutil -d "sql:$DB" -A -t "C,," -n ccr-agent-proxy -i "$CA" && echo "Proxy-CA importiert"
fi
