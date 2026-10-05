"""SQLite-Zugriff ohne ORM. Eine Datei, drei Tabellen, kein Zauber."""
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
    letzte_anmeldung TEXT,
    inhaber INTEGER NOT NULL DEFAULT 0
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
    ordner TEXT NOT NULL,
    lauf TEXT
);
CREATE INDEX IF NOT EXISTS idx_pruefungen_user ON pruefungen(user_id, erstellt DESC);
CREATE INDEX IF NOT EXISTS idx_pruefungen_lauf ON pruefungen(lauf);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
"""


def jetzt() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def verbinden(pfad: Path | None = None) -> sqlite3.Connection:
    con = sqlite3.connect(str(pfad or config.DB_PFAD), check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA journal_mode = WAL")
    return con


# Spalten, die nach der ersten Fassung dazukamen: (Tabelle, Spalte, Definition).
NACHTRAEGE = [
    ("pruefungen", "lauf", "TEXT"),
    ("users", "inhaber", "INTEGER NOT NULL DEFAULT 0"),
]


def _nachtragen(con: sqlite3.Connection) -> None:
    """Ergänzt fehlende Spalten in bestehenden Datenbanken, ohne Daten anzufassen."""
    for tabelle, spalte, definition in NACHTRAEGE:
        vorhanden = {r[1] for r in con.execute(f"PRAGMA table_info({tabelle})").fetchall()}
        if spalte not in vorhanden:
            con.execute(f"ALTER TABLE {tabelle} ADD COLUMN {spalte} {definition}")
    # Genau ein Konto ist Inhaber: das älteste Admin-Konto, falls noch keines markiert ist.
    if con.execute("SELECT COUNT(*) FROM users WHERE inhaber = 1").fetchone()[0] == 0:
        con.execute("UPDATE users SET inhaber = 1 WHERE id = (SELECT id FROM users WHERE rolle = 'admin' ORDER BY angelegt_am, id LIMIT 1)")


def init_db(pfad: Path | None = None) -> None:
    with verbinden(pfad) as con:
        # CREATE TABLE IF NOT EXISTS legt neue Datenbanken vollständig an; bei alten fehlt eventuell eine Spalte.
        con.executescript(SCHEMA.split("CREATE INDEX", 1)[0])
        _nachtragen(con)
        con.executescript("CREATE INDEX" + SCHEMA.split("CREATE INDEX", 1)[1])


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
