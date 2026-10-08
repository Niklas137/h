#!/usr/bin/env python3
"""Kader-Manager – kleiner Server ohne Abhängigkeiten (Python-Standardbibliothek).

Liefert die statischen Dateien des Moduls und bietet eine geschützte Schnittstelle zum Veröffentlichen:
  GET  /api/kader   → aktueller Stand (daten/kader.json)
  PUT  /api/kader   → neuen Stand speichern; nur mit Kopfzeile X-Admin-Token = KADER_ADMIN_TOKEN
Der Token kommt ausschließlich aus der Umgebungsvariable KADER_ADMIN_TOKEN (siehe .env.example),
nie aus einer Datei im Modul. Vor jedem Speichern wird eine Sicherung nach daten/sicherung/ geschrieben.

Start:  KADER_ADMIN_TOKEN='geheim' python3 server.py            (Port 8000)
        KADER_ADMIN_TOKEN='geheim' python3 server.py 8080
Ohne gesetzten Token ist das Veröffentlichen gesperrt; der Rest der Seite läuft normal.
"""
import hmac, json, os, shutil, sys, time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WURZEL = Path(__file__).resolve().parent
DATEI = WURZEL / 'daten' / 'kader.json'
SICHERUNG = WURZEL / 'daten' / 'sicherung'
MAX_BYTES = 2_000_000


def token_gueltig(kopf):
    soll = os.environ.get('KADER_ADMIN_TOKEN', '')
    return bool(soll) and bool(kopf) and hmac.compare_digest(soll, kopf)


def daten_pruefen(obj):
    """Grundprüfung auf dem Server; die vollständige Feldprüfung macht kader-daten.js vor dem Senden."""
    if not isinstance(obj, dict) or not isinstance(obj.get('players'), list):
        return 'Feld "players" fehlt oder ist keine Liste.'
    ids = set()
    for i, p in enumerate(obj['players'], 1):
        if not isinstance(p, dict) or not str(p.get('name', '')).strip():
            return f'Spieler {i}: Name fehlt.'
        try:
            n = int(p.get('number'))
        except (TypeError, ValueError):
            return f'Spieler {i}: Rückennummer fehlt.'
        if not 0 <= n <= 99:
            return f'Spieler {i}: Rückennummer {n} unzulässig.'
        pid = str(p.get('id', '')).strip().lower()
        if not pid or pid in ids:
            return f'Spieler {i}: ID fehlt oder ist doppelt.'
        ids.add(pid)
    return None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(WURZEL), **kw)

    def log_message(self, fmt, *args):  # knapper Log ohne Token
        sys.stderr.write('%s %s\n' % (self.address_string(), fmt % args))

    def antwort(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split('?')[0] == '/api/kader':
            try:
                self.antwort(200, json.loads(DATEI.read_text('utf-8')))
            except (OSError, ValueError) as f:
                self.antwort(500, {'fehler': f'Kaderdatei nicht lesbar: {f}'})
            return
        if self.path.startswith('/daten/sicherung'):
            self.send_error(404)
            return
        super().do_GET()

    def do_PUT(self):
        if self.path.split('?')[0] != '/api/kader':
            self.send_error(404)
            return
        if not token_gueltig(self.headers.get('X-Admin-Token')):
            self.antwort(403, {'fehler': 'Kein gültiger Admin-Token.'})
            return
        laenge = int(self.headers.get('Content-Length') or 0)
        if laenge <= 0 or laenge > MAX_BYTES:
            self.antwort(413, {'fehler': 'Daten fehlen oder sind zu groß.'})
            return
        try:
            obj = json.loads(self.rfile.read(laenge).decode('utf-8'))
        except ValueError:
            self.antwort(400, {'fehler': 'Kein gültiges JSON.'})
            return
        fehler = daten_pruefen(obj)
        if fehler:
            self.antwort(422, {'fehler': fehler})
            return
        SICHERUNG.mkdir(parents=True, exist_ok=True)
        if DATEI.exists():
            shutil.copy2(DATEI, SICHERUNG / time.strftime('kader-%Y-%m-%d_%H%M%S.json'))
        tmp = DATEI.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', 'utf-8')
        os.replace(tmp, DATEI)
        self.antwort(200, {'ok': True, 'spieler': len(obj['players'])})

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    if not os.environ.get('KADER_ADMIN_TOKEN'):
        print('Hinweis: KADER_ADMIN_TOKEN ist nicht gesetzt, Veröffentlichen ist gesperrt.', file=sys.stderr)
    print(f'Kader-Manager läuft auf http://localhost:{port}/  (Admin: /admin.html)', file=sys.stderr)
    ThreadingHTTPServer(('', port), Handler).serve_forever()
