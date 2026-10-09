#!/usr/bin/env python3
"""Kader-Manager – kleiner Server ohne Abhängigkeiten (Python-Standardbibliothek).

Liefert die statischen Dateien des Moduls und bietet eine geschützte Schnittstelle zum Veröffentlichen:
  GET  /api/kader      → aktueller Stand (daten/kader.json)
  PUT  /api/kader      → neuen Stand speichern; nur mit Kopfzeile X-Admin-Token = KADER_ADMIN_TOKEN
  POST /api/anmelden   → 204 wenn der Token stimmt, sonst 403 (Anmeldefenster der Admin-Seite)
  POST /api/foto?spieler=<id> → Spielerfoto (JPEG/PNG/WebP, max. 3 MB) nach fotos/spieler/<id>.<ext>; nur mit Token
Der Token kommt ausschließlich aus der Umgebungsvariable KADER_ADMIN_TOKEN (siehe .env.example),
nie aus einer Datei im Modul. Vor jedem Speichern wird eine Sicherung nach daten/sicherung/ geschrieben.

Start:  KADER_ADMIN_TOKEN='geheim' python3 server.py            (Port 8000)
        KADER_ADMIN_TOKEN='geheim' python3 server.py 8080
Ohne gesetzten Token ist das Veröffentlichen gesperrt; der Rest der Seite läuft normal.
"""
import hmac, json, os, re, shutil, sys, time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

WURZEL = Path(__file__).resolve().parent
DATEI = WURZEL / 'daten' / 'kader.json'
SICHERUNG = WURZEL / 'daten' / 'sicherung'
FOTOS = WURZEL / 'fotos' / 'spieler'
MAX_BYTES = 2_000_000
FOTO_MAX_BYTES = 3_000_000
FOTO_ARTEN = {b'\xff\xd8\xff': 'jpg', b'\x89PNG\r\n\x1a\n': 'png'}   # Dateianfang → Endung; WebP unten gesondert
ID_MUSTER = re.compile(r'^[a-z0-9-]{1,60}$')


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

    def do_POST(self):
        pfad = urlsplit(self.path)
        if pfad.path == '/api/anmelden':
            if token_gueltig(self.headers.get('X-Admin-Token')):
                self.send_response(204)
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
            else:
                time.sleep(0.5)            # bremst Durchprobieren
                self.antwort(403, {'fehler': 'Kein gültiger Admin-Token.'})
            return
        if pfad.path == '/api/foto':
            self.foto_speichern(parse_qs(pfad.query))
            return
        self.send_error(404)

    def foto_speichern(self, abfrage):
        if not token_gueltig(self.headers.get('X-Admin-Token')):
            self.antwort(403, {'fehler': 'Kein gültiger Admin-Token.'})
            return
        kennung = (abfrage.get('spieler') or [''])[0].strip().lower()
        if not ID_MUSTER.match(kennung):
            self.antwort(400, {'fehler': 'Spieler-ID fehlt oder ist unzulässig.'})
            return
        laenge = int(self.headers.get('Content-Length') or 0)
        if laenge <= 0 or laenge > FOTO_MAX_BYTES:
            self.antwort(413, {'fehler': 'Foto fehlt oder ist größer als 3 MB.'})
            return
        roh = self.rfile.read(laenge)
        endung = next((e for anfang, e in FOTO_ARTEN.items() if roh.startswith(anfang)), None)
        if endung is None and roh[:4] == b'RIFF' and roh[8:12] == b'WEBP':
            endung = 'webp'
        if endung is None:
            self.antwort(415, {'fehler': 'Nur JPEG, PNG oder WebP.'})
            return
        FOTOS.mkdir(parents=True, exist_ok=True)
        for alt in FOTOS.glob(f'{kennung}.*'):          # alte Fassung mit anderer Endung entfernen
            if alt.suffix[1:] != endung:
                alt.unlink()
        ziel = FOTOS / f'{kennung}.{endung}'
        tmp = ziel.with_suffix(ziel.suffix + '.tmp')
        tmp.write_bytes(roh)
        os.replace(tmp, ziel)
        self.antwort(200, {'ok': True, 'pfad': f'fotos/spieler/{kennung}.{endung}?v={int(time.time())}', 'bytes': len(roh)})

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
