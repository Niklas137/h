"""Befehle für die Konsole: Admin anlegen, Einmal-Passwort erneuern, Konten auflisten.

    python -m app.verwaltung admin --email name@firma.de --name "Vorname Nachname"
    python -m app.verwaltung einmal --email name@firma.de
    python -m app.verwaltung liste
"""
from __future__ import annotations

import argparse
import sys

from . import auth, config, db


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.verwaltung", description="Konten des Dokumentenprüfers verwalten")
    sub = parser.add_subparsers(dest="befehl", required=True)
    a = sub.add_parser("admin", help="Admin-Konto anlegen, gibt das Einmal-Passwort aus")
    a.add_argument("--email", required=True)
    a.add_argument("--name", required=True)
    e = sub.add_parser("einmal", help="Neues Einmal-Passwort für ein Konto")
    e.add_argument("--email", required=True)
    sub.add_parser("liste", help="Alle Konten anzeigen")
    args = parser.parse_args(argv)

    db.init_db()
    with db.transaktion() as con:
        if args.befehl == "admin":
            if auth.benutzer_per_email(con, args.email):
                print("Es gibt schon ein Konto mit dieser E-Mail-Adresse.", file=sys.stderr)
                return 1
            user, einmal = auth.benutzer_anlegen(con, args.email, args.name, "admin")
            print(f"Admin angelegt: {user['email']}")
            print(f"Einmal-Passwort (gilt {config.EINMAL_PASSWORT_TAGE} Tage, nur einmal anzeigen): {einmal}")
            return 0
        if args.befehl == "einmal":
            user = auth.benutzer_per_email(con, args.email)
            if user is None:
                print("Konto nicht gefunden.", file=sys.stderr)
                return 1
            einmal = auth.einmal_passwort_erneuern(con, user["id"])
            auth.alle_sitzungen_beenden(con, user["id"])
            print(f"Neues Einmal-Passwort für {user['email']}: {einmal}")
            return 0
        if args.befehl == "liste":
            rows = db.zeilen(con.execute("SELECT email, name, rolle, status, angelegt_am FROM users ORDER BY angelegt_am").fetchall())
            if not rows:
                print("Keine Konten vorhanden.")
            for r in rows:
                print(f"{r['email']:40} {r['name']:28} {r['rolle']:9} {r['status']:9} {r['angelegt_am'][:10]}")
            return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
