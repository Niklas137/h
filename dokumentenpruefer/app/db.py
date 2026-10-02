"""SQLite-Zugriff ohne ORM. Eine Datei, fünf Tabellen, kein Zauber."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL DEFAULT '',
    passwort_hash TEXT,
    rolle TEXT NOT NULL DEFAULT 'mitglied' CHECK (rolle IN ('admin', 'mitglied')),
    status TEXT NOT NULL DEFAULT 'einmal' CHECK (status IN ('einmal', 'aktiv', 'gesperrt')),
    einmal_hash TEXT,
    einmal_ablauf TEXT,
    code_hash TEXT,
    code_ablauf TEXT,
    code_versuche INTEGER NOT NULL DEFAULT 0,
    fehlversuche INTEGER NOT NULL DEFAULT 0,
    gesperrt_bis TEXT,
    angelegt_am TEXT NOT NULL,
    letzte_anmeldung TEXT
);
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    dark INTEGER NOT NULL DEFAULT 1,
    text_size TEXT NOT NULL DEFAULT 'normal',
    density TEXT NOT NULL DEFAULT 'normal',
    language TEXT NOT NULL DEFAULT 'de',
    notify_popup INTEGER NOT NULL DEFAULT 1,
    notify_app INTEGER NOT NULL DEFAULT 1,
    notify_weekly INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    erstellt TEXT NOT NULL,
    ablauf TEXT NOT NULL,
    geraet TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS pruefungen (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dateiname TEXT NOT NULL,
    score INTEGER NOT NULL,
    ampel TEXT NOT NULL,
    stunden REAL NOT NULL,
    funde INTEGER NOT NULL,
    sprachen TEXT NOT NULL,
    regelsaetze TEXT NOT NULL,
    erstellt TEXT NOT NULL,
    ergebnis TEXT NOT NULL,
    ordner TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zeit TEXT NOT NULL,
    akteur_id INTEGER,
    akteur_email TEXT NOT NULL DEFAULT '',
    aktion TEXT NOT NULL,
    ziel_id INTEGER,
    ziel_email TEXT NOT NULL DEFAULT '',
    details TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_pruefungen_user ON pruefungen(user_id, erstellt DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_zeit ON audit_log(zeit DESC);
"""

# Spalten, die nach der ersten Fassung dazugekommen sind. SQLite kann Spalten anhängen,
# aber keine CHECK-Regel ändern; deshalb bleibt "geloescht" ein eigenes Feld statt ein Status.
_NACHTRAEGLICH = {
    "users": [("geloescht_am", "TEXT")],
}


def jetzt() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def verbinden(pfad: Path | None = None) -> sqlite3.Connection:
    con = sqlite3.connect(str(pfad or config.DB_PFAD), check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA journal_mode = WAL")
    return con


def init_db(pfad: Path | None = None) -> None:
    with verbinden(pfad) as con:
        con.executescript(SCHEMA)
        for tabelle, spalten in _NACHTRAEGLICH.items():
            vorhanden = {r["name"] for r in con.execute(f"PRAGMA table_info({tabelle})").fetchall()}
            for name, typ in spalten:
                if name not in vorhanden:
                    con.execute(f"ALTER TABLE {tabelle} ADD COLUMN {name} {typ}")


@contextmanager
def transaktion(pfad: Path | None = None) -> Iterator[sqlite3.Connection]:
    con = verbinden(pfad)
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def zeile(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def zeilen(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(r) for r in rows]


def json_laden(text: str | None, standard: Any) -> Any:
    if not text:
        return standard
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return standard
