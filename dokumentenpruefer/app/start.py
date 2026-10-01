"""Lokaler Start mit Portprüfung, Erstkonto und Browser erst nach erfolgreichem Start."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import socket
import sys
import threading
import time
import urllib.request
import webbrowser

from . import auth, config, db


def eigene_instanz(url: str) -> bool:
    try:
        # Der lokale Dienst läuft auf Loopback, unabhängig von Firmen-Proxys.
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url + "/api/status", timeout=1) as r:
            status = json.load(r)
        return (status.get("anwendung") == "fsh-dokumentenpruefer" and
                status.get("installation") == hashlib.sha256(str(config.DATEN.resolve()).encode()).hexdigest()[:16])
    except (OSError, ValueError, AttributeError):
        return False


def konto_vorbereiten() -> bool:
    db.init_db()
    with db.transaktion() as con:
        if con.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            return True
    if not sys.stdin.isatty():
        print("Noch kein Konto vorhanden. Im Terminal starten oder python -m app.verwaltung admin --email ... --name ... ausführen.", file=sys.stderr)
        return False
    print("Noch kein Konto vorhanden. Admin-Konto anlegen:")
    email = input("E-Mail-Adresse: ").strip().lower()
    name = input("Name: ").strip()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or not 2 <= len(name) <= 80:
        print("Bitte eine gültige E-Mail-Adresse und einen Namen mit 2 bis 80 Zeichen eingeben.", file=sys.stderr)
        return False
    with db.transaktion() as con:
        _, einmal = auth.benutzer_anlegen(con, email, name, "admin")
    print(f"Admin angelegt: {email}")
    print(f"Einmal-Passwort (gilt {config.EINMAL_PASSWORT_TAGE} Tage): {einmal}")
    print("Jetzt notieren. Es wird nicht erneut angezeigt.")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dokumentenprüfer lokal starten")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--ohne-browser", action="store_true")
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("Port muss zwischen 1 und 65535 liegen.")
    url = f"http://127.0.0.1:{args.port}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", args.port))
            sock.listen(128)
        except OSError:
            if eigene_instanz(url):
                print(f"Dokumentenprüfer läuft bereits unter {url}. Es wird keine zweite Instanz gestartet.")
                if not args.ohne_browser:
                    webbrowser.open(url)
                return 0
            print(f"Port {args.port} ist bereits belegt. Die dort laufende Anwendung bleibt unverändert. Bitte erst die andere Instanz beenden oder --port wählen.", file=sys.stderr)
            return 2
        if not konto_vorbereiten():
            return 2
        import uvicorn
        server = uvicorn.Server(uvicorn.Config("app.main:app", host="127.0.0.1", port=args.port))
        def bereit():
            for _ in range(200):
                if server.should_exit:
                    return
                if server.started:
                    print(f"Dokumentenprüfer läuft unter {url} (Beenden mit Ctrl+C)", flush=True)
                    if not args.ohne_browser:
                        webbrowser.open(url)
                    return
                time.sleep(0.05)
        threading.Thread(target=bereit, daemon=True).start()
        try:
            server.run(sockets=[sock])
        except KeyboardInterrupt:
            pass  # Uvicorn hat den Dienst bei Ctrl+C bereits geordnet beendet.
        return 0 if server.started else 1


if __name__ == "__main__":
    raise SystemExit(main())
