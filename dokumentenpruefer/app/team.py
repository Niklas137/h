"""Mitarbeiterverwaltung für Admins: Liste, Anlegen, Ändern, Deaktivieren, Löschen, Protokoll.

Regeln, die hier serverseitig gelten und nicht nur in der Oberfläche:
- Nur ein Admin ruft diese Funktionen auf (prüft main.py über admin_benutzer).
- Gelöscht wird weich: das Konto bekommt `geloescht_am`, Status `gesperrt`, alle Sitzungen enden.
  Prüfungen und Protokoll bleiben erhalten, die E-Mail-Adresse bleibt belegt.
- Der letzte aktive Admin kann weder gelöscht, deaktiviert noch zum Mitglied gemacht werden.
- Niemand ändert sich selbst über diese Funktionen (Rolle, Status, Löschen).
- Jede Änderung landet im Protokoll: Zeit, wer, was, an wem. Keine Hashes, keine Passwörter.
"""
from __future__ import annotations

import json
from typing import Any

from . import auth, db

ROLLEN = ("admin", "mitglied")
ROLLENNAMEN = {"admin": "Admin", "mitglied": "Mitglied"}

AKTIONEN = {
    "angelegt": "Mitarbeiter angelegt",
    "geaendert": "Mitarbeiter geändert",
    "rolle": "Rolle geändert",
    "deaktiviert": "Mitarbeiter deaktiviert",
    "aktiviert": "Mitarbeiter aktiviert",
    "geloescht": "Mitarbeiter gelöscht",
    "einmal_passwort": "Neues Einmal-Passwort",
}


class TeamFehler(ValueError):
    """Verständliche Ablehnung mit HTTP-Status."""

    def __init__(self, status: int, meldung: str, feld: str | None = None):
        super().__init__(meldung)
        self.status = status
        self.feld = feld


# ---------------------------------------------------------------- Lesen


def liste(con, mit_geloeschten: bool = False) -> list[dict[str, Any]]:
    sql = "SELECT * FROM users"
    if not mit_geloeschten:
        sql += " WHERE geloescht_am IS NULL"
    sql += " ORDER BY geloescht_am IS NOT NULL, lower(name), angelegt_am"
    return [auth.oeffentlich(r) for r in db.zeilen(con.execute(sql).fetchall())]


def laden(con, user_id: int) -> dict[str, Any]:
    ziel = auth.benutzer_per_id(con, user_id)
    if ziel is None:
        raise TeamFehler(404, "Konto nicht gefunden.")
    return ziel


def aktive_admins(con) -> int:
    return int(
        con.execute(
            "SELECT COUNT(*) FROM users WHERE rolle = 'admin' AND status = 'aktiv' AND geloescht_am IS NULL"
        ).fetchone()[0]
    )


def _ist_aktiver_admin(user: dict[str, Any]) -> bool:
    return user["rolle"] == "admin" and user["status"] == "aktiv" and not user.get("geloescht_am")


def _letzter_admin_schutz(con, ziel: dict[str, Any], vorhaben: str) -> None:
    """Der letzte aktive Admin bleibt erhalten, sonst sperrt sich das Team selbst aus."""
    if _ist_aktiver_admin(ziel) and aktive_admins(con) <= 1:
        raise TeamFehler(409, f"{ziel['name']} ist der letzte aktive Admin und kann nicht {vorhaben} werden.")


# ---------------------------------------------------------------- Protokoll


def protokollieren(con, akteur: dict[str, Any], aktion: str, ziel: dict[str, Any] | None, details: dict[str, Any] | None = None) -> None:
    assert aktion in AKTIONEN
    con.execute(
        "INSERT INTO audit_log (zeit, akteur_id, akteur_email, aktion, ziel_id, ziel_email, details) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            db.jetzt(),
            akteur.get("id"),
            akteur.get("email", ""),
            aktion,
            ziel.get("id") if ziel else None,
            ziel.get("email", "") if ziel else "",
            json.dumps(details or {}, ensure_ascii=False),
        ),
    )


def protokoll(con, limit: int = 200) -> list[dict[str, Any]]:
    rows = db.zeilen(con.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (max(1, min(limit, 1000)),)).fetchall())
    return [
        {
            "id": r["id"],
            "zeit": r["zeit"],
            "akteur": {"id": r["akteur_id"], "email": r["akteur_email"]},
            "aktion": r["aktion"],
            "aktionText": AKTIONEN.get(r["aktion"], r["aktion"]),
            "ziel": {"id": r["ziel_id"], "email": r["ziel_email"]},
            "details": db.json_laden(r["details"], {}),
        }
        for r in rows
    ]


# ---------------------------------------------------------------- Schreiben


def anlegen(con, akteur: dict[str, Any], email: str, name: str, rolle: str) -> tuple[dict[str, Any], str]:
    if rolle not in ROLLEN:
        raise TeamFehler(400, "Rolle muss admin oder mitglied sein.", "rolle")
    bestehend = auth.benutzer_per_email(con, email)
    if bestehend is not None:
        if bestehend.get("geloescht_am"):
            raise TeamFehler(409, "Diese E-Mail-Adresse gehört zu einem gelöschten Konto. Es kann unter „Gelöschte anzeigen“ wiederhergestellt werden.")
        raise TeamFehler(409, "Diese E-Mail-Adresse hat schon ein Konto.")
    neu, einmal = auth.benutzer_anlegen(con, email, name, rolle)
    protokollieren(con, akteur, "angelegt", neu, {"rolle": rolle})
    return neu, einmal


def aendern(con, akteur: dict[str, Any], user_id: int, daten: dict[str, Any]) -> dict[str, Any]:
    """Name, Rolle und Status. Nur mitgeschickte Felder werden geändert."""
    ziel = laden(con, user_id)
    if ziel.get("geloescht_am"):
        raise TeamFehler(409, "Dieses Konto ist gelöscht. Erst wiederherstellen, dann ändern.")
    selbst = ziel["id"] == akteur["id"]

    if "name" in daten:
        name = str(daten["name"]).strip()
        if len(name) < 2 or len(name) > 80:
            raise TeamFehler(400, "Der Name braucht 2 bis 80 Zeichen.", "name")
        if name != ziel["name"]:
            con.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
            protokollieren(con, akteur, "geaendert", ziel, {"feld": "name", "von": ziel["name"], "nach": name})

    if "rolle" in daten:
        rolle = str(daten["rolle"])
        if rolle not in ROLLEN:
            raise TeamFehler(400, "Rolle muss admin oder mitglied sein.", "rolle")
        if rolle != ziel["rolle"]:
            if selbst:
                raise TeamFehler(400, "Du kannst deine eigene Rolle nicht ändern.")
            if rolle != "admin":
                _letzter_admin_schutz(con, ziel, "zum Mitglied gemacht")
            con.execute("UPDATE users SET rolle = ? WHERE id = ?", (rolle, user_id))
            protokollieren(con, akteur, "rolle", ziel, {"von": ziel["rolle"], "nach": rolle})

    if "status" in daten:
        status = str(daten["status"])
        if status not in ("aktiv", "gesperrt"):
            raise TeamFehler(400, "Status muss aktiv oder gesperrt sein.", "status")
        if selbst:
            raise TeamFehler(400, "Du kannst dich nicht selbst deaktivieren.")
        if status == "gesperrt" and ziel["status"] != "gesperrt":
            _letzter_admin_schutz(con, ziel, "deaktiviert")
            con.execute("UPDATE users SET status = 'gesperrt' WHERE id = ?", (user_id,))
            auth.alle_sitzungen_beenden(con, user_id)
            protokollieren(con, akteur, "deaktiviert", ziel, {"vorher": ziel["status"]})
        elif status == "aktiv" and ziel["status"] == "gesperrt":
            # Ohne eigenes Passwort geht es zurück in die Erstanmeldung, sonst ist das Konto sofort nutzbar.
            neu_status = "aktiv" if ziel.get("passwort_hash") else "einmal"
            con.execute("UPDATE users SET status = ?, fehlversuche = 0, gesperrt_bis = NULL WHERE id = ?", (neu_status, user_id))
            protokollieren(con, akteur, "aktiviert", ziel, {"nachher": neu_status})

    return laden(con, user_id)


def einmal_passwort(con, akteur: dict[str, Any], user_id: int) -> str:
    ziel = laden(con, user_id)
    if ziel.get("geloescht_am"):
        raise TeamFehler(409, "Dieses Konto ist gelöscht.")
    einmal = auth.einmal_passwort_erneuern(con, user_id)
    auth.alle_sitzungen_beenden(con, user_id)
    protokollieren(con, akteur, "einmal_passwort", ziel)
    return einmal


def loeschen(con, akteur: dict[str, Any], user_id: int, bestaetigung: str) -> dict[str, Any]:
    """Weiches Löschen. Die Bestätigung ist die E-Mail-Adresse des Kontos, damit nichts aus Versehen passiert."""
    ziel = laden(con, user_id)
    if ziel["id"] == akteur["id"]:
        raise TeamFehler(400, "Du kannst dein eigenes Konto nicht löschen.")
    if ziel.get("geloescht_am"):
        raise TeamFehler(409, "Dieses Konto ist schon gelöscht.")
    if bestaetigung.strip().lower() != ziel["email"]:
        raise TeamFehler(400, "Zur Bestätigung bitte die E-Mail-Adresse des Kontos eingeben.", "bestaetigung")
    _letzter_admin_schutz(con, ziel, "gelöscht")
    con.execute(
        "UPDATE users SET geloescht_am = ?, status = 'gesperrt', einmal_hash = NULL, einmal_ablauf = NULL,"
        " code_hash = NULL, code_ablauf = NULL WHERE id = ?",
        (db.jetzt(), user_id),
    )
    auth.alle_sitzungen_beenden(con, user_id)
    protokollieren(con, akteur, "geloescht", ziel, {"rolle": ziel["rolle"]})
    return laden(con, user_id)


def wiederherstellen(con, akteur: dict[str, Any], user_id: int) -> dict[str, Any]:
    ziel = laden(con, user_id)
    if not ziel.get("geloescht_am"):
        raise TeamFehler(409, "Dieses Konto ist nicht gelöscht.")
    con.execute("UPDATE users SET geloescht_am = NULL, status = 'gesperrt' WHERE id = ?", (user_id,))
    protokollieren(con, akteur, "aktiviert", ziel, {"wiederhergestellt": True, "nachher": "gesperrt"})
    return laden(con, user_id)
