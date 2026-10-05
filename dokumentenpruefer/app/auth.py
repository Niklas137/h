"""Anmeldung, Einmal-Passwörter, Codes, Sitzungen und die Passwortregel."""
from __future__ import annotations

import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from . import config, db

_hasher = PasswordHasher()

# Zeichen ohne Verwechslungsgefahr (kein 0/O, 1/l/I)
_EINMAL_ZEICHEN = "ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789"


def hash_passwort(klartext: str) -> str:
    return _hasher.hash(klartext)


def passwort_stimmt(hashwert: str | None, klartext: str) -> bool:
    if not hashwert:
        return False
    try:
        return _hasher.verify(hashwert, klartext)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def passwort_regel(klartext: str) -> list[str]:
    """Gibt die verletzten Regeln zurück. Leer heißt: Passwort ist in Ordnung.

    Regel laut Niklas: mindestens 14 Zeichen, ein Großbuchstabe, ein Sonderzeichen.
    """
    verletzt: list[str] = []
    if len(klartext) < config.PASSWORT_MIN:
        verletzt.append("laenge")
    if not re.search(r"[A-ZÄÖÜ]", klartext):
        verletzt.append("grossbuchstabe")
    if not re.search(r"[^A-Za-z0-9ÄÖÜäöüß\s]", klartext):
        verletzt.append("sonderzeichen")
    return verletzt


def einmal_passwort_erzeugen() -> str:
    teile = ["".join(secrets.choice(_EINMAL_ZEICHEN) for _ in range(4)) for _ in range(3)]
    return "-".join(teile)


def code_erzeugen() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _utc(dt: datetime | None = None) -> datetime:
    return (dt or datetime.now(timezone.utc)).astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def _parse(text: str | None) -> datetime | None:
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


# ---------------------------------------------------------------- Benutzer


def benutzer_anlegen(con, email: str, name: str, rolle: str = "mitglied") -> tuple[dict[str, Any], str]:
    """Legt ein Konto an und gibt (Benutzer, Einmal-Passwort im Klartext) zurück.

    Das Einmal-Passwort wird nur hier im Klartext gezeigt, gespeichert wird ein Hash.
    """
    email = email.strip().lower()
    einmal = einmal_passwort_erzeugen()
    ablauf = _iso(_utc() + timedelta(days=config.EINMAL_PASSWORT_TAGE))
    # Das allererste Konto ist der Inhaber: nur er darf Konten löschen, niemand kann ihm die Rechte nehmen.
    inhaber = 1 if rolle == "admin" and con.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0 else 0
    con.execute(
        "INSERT INTO users (email, name, rolle, status, einmal_hash, einmal_ablauf, angelegt_am, inhaber)"
        " VALUES (?, ?, ?, 'einmal', ?, ?, ?, ?)",
        (email, name.strip(), rolle, hash_passwort(einmal), ablauf, db.jetzt(), inhaber),
    )
    user = db.zeile(con.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone())
    assert user is not None
    return user, einmal


def einmal_passwort_erneuern(con, user_id: int) -> str:
    einmal = einmal_passwort_erzeugen()
    ablauf = _iso(_utc() + timedelta(days=config.EINMAL_PASSWORT_TAGE))
    con.execute(
        "UPDATE users SET einmal_hash = ?, einmal_ablauf = ?, status = 'einmal', passwort_hash = NULL,"
        " code_hash = NULL, code_ablauf = NULL, code_versuche = 0, fehlversuche = 0, gesperrt_bis = NULL WHERE id = ?",
        (hash_passwort(einmal), ablauf, user_id),
    )
    return einmal


def benutzer_per_email(con, email: str) -> dict[str, Any] | None:
    return db.zeile(con.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),)).fetchone())


def benutzer_per_id(con, user_id: int) -> dict[str, Any] | None:
    return db.zeile(con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())


def oeffentlich(user: dict[str, Any]) -> dict[str, Any]:
    """Was die Oberfläche über ein Konto wissen darf. Nie ein Hash, nie ein Code."""
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "rolle": user["rolle"],
        "inhaber": bool(user.get("inhaber")),
        "status": user["status"],
        "angelegtAm": user["angelegt_am"],
        "letzteAnmeldung": user["letzte_anmeldung"],
    }


# ---------------------------------------------------------------- Sperre


def gesperrt(user: dict[str, Any]) -> bool:
    bis = _parse(user.get("gesperrt_bis"))
    return bis is not None and bis > _utc()


def fehlversuch(con, user: dict[str, Any]) -> None:
    # Eine laufende Sperre darf weder gelöscht noch durch weitere Aufrufe verlängert werden.
    if gesperrt(user):
        return
    n = int(user.get("fehlversuche") or 0) + 1
    sperre = None
    if n >= config.FEHLVERSUCHE_MAX:
        sperre = _iso(_utc() + timedelta(minutes=config.SPERRE_MINUTEN))
        n = 0
    con.execute("UPDATE users SET fehlversuche = ?, gesperrt_bis = ? WHERE id = ?", (n, sperre, user["id"]))


def erfolg(con, user_id: int) -> None:
    con.execute(
        "UPDATE users SET fehlversuche = 0, gesperrt_bis = NULL, letzte_anmeldung = ? WHERE id = ?",
        (db.jetzt(), user_id),
    )


# ---------------------------------------------------------------- Einmal-Passwort und Code


def einmal_passwort_stimmt(user: dict[str, Any], einmal: str) -> bool:
    if user["status"] != "einmal" or not user.get("einmal_hash"):
        return False
    ablauf = _parse(user.get("einmal_ablauf"))
    if ablauf is not None and ablauf < _utc():
        return False
    return passwort_stimmt(user["einmal_hash"], einmal.strip())


def code_setzen(con, user_id: int) -> str:
    code = code_erzeugen()
    ablauf = _iso(_utc() + timedelta(minutes=config.CODE_MINUTEN))
    con.execute(
        "UPDATE users SET code_hash = ?, code_ablauf = ?, code_versuche = 0 WHERE id = ?",
        (_sha(code), ablauf, user_id),
    )
    return code


def code_stimmt(con, user: dict[str, Any], code: str) -> bool:
    if not user.get("code_hash"):
        return False
    ablauf = _parse(user.get("code_ablauf"))
    if ablauf is not None and ablauf < _utc():
        return False
    if int(user.get("code_versuche") or 0) >= 5:
        return False
    ok = secrets.compare_digest(user["code_hash"], _sha(code.strip()))
    if not ok:
        con.execute("UPDATE users SET code_versuche = code_versuche + 1 WHERE id = ?", (user["id"],))
    return ok


def konto_abschliessen(con, user_id: int, name: str, passwort: str) -> None:
    con.execute(
        "UPDATE users SET name = ?, passwort_hash = ?, status = 'aktiv', einmal_hash = NULL, einmal_ablauf = NULL,"
        " code_hash = NULL, code_ablauf = NULL, code_versuche = 0, fehlversuche = 0, gesperrt_bis = NULL,"
        " letzte_anmeldung = ? WHERE id = ?",
        (name.strip(), hash_passwort(passwort), db.jetzt(), user_id),
    )


def passwort_setzen(con, user_id: int, passwort: str) -> None:
    con.execute("UPDATE users SET passwort_hash = ? WHERE id = ?", (hash_passwort(passwort), user_id))


# ---------------------------------------------------------------- Sitzungen


def sitzung_anlegen(con, user_id: int, geraet: str = "", tage: int | None = None) -> str:
    token = secrets.token_urlsafe(32)
    ablauf = _iso(_utc() + timedelta(days=tage or config.SITZUNG_TAGE))
    con.execute(
        "INSERT INTO sessions (token_hash, user_id, erstellt, ablauf, geraet) VALUES (?, ?, ?, ?, ?)",
        (_sha(token), user_id, db.jetzt(), ablauf, geraet[:200]),
    )
    return token


def sitzung_pruefen(con, token: str | None) -> dict[str, Any] | None:
    """Gibt den Benutzer zur Sitzung zurück oder None."""
    if not token:
        return None
    row = db.zeile(
        con.execute(
            "SELECT s.token_hash, s.ablauf, u.* FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token_hash = ?",
            (_sha(token),),
        ).fetchone()
    )
    if row is None:
        return None
    ablauf = _parse(row["ablauf"])
    if ablauf is not None and ablauf < _utc():
        con.execute("DELETE FROM sessions WHERE token_hash = ?", (row["token_hash"],))
        return None
    if row["status"] != "aktiv":
        return None
    row["sitzung_hash"] = row.pop("token_hash")
    row.pop("ablauf", None)
    return row


def sitzung_beenden(con, token: str | None) -> None:
    if token:
        con.execute("DELETE FROM sessions WHERE token_hash = ?", (_sha(token),))


def sitzungen_des_benutzers(con, user_id: int, aktuell_hash: str | None) -> list[dict[str, Any]]:
    rows = db.zeilen(
        con.execute(
            "SELECT token_hash, erstellt, ablauf, geraet FROM sessions WHERE user_id = ? ORDER BY erstellt DESC",
            (user_id,),
        ).fetchall()
    )
    return [
        {
            "id": r["token_hash"][:16],
            "erstellt": r["erstellt"],
            "ablauf": r["ablauf"],
            "geraet": r["geraet"],
            "aktuell": r["token_hash"] == aktuell_hash,
        }
        for r in rows
    ]


def sitzung_loeschen_per_kurz_id(con, user_id: int, kurz_id: str) -> int:
    rows = con.execute("SELECT token_hash FROM sessions WHERE user_id = ?", (user_id,)).fetchall()
    n = 0
    for r in rows:
        if r["token_hash"].startswith(kurz_id):
            con.execute("DELETE FROM sessions WHERE token_hash = ?", (r["token_hash"],))
            n += 1
    return n


def alle_sitzungen_beenden(con, user_id: int, ausser_hash: str | None = None) -> None:
    if ausser_hash:
        con.execute("DELETE FROM sessions WHERE user_id = ? AND token_hash != ?", (user_id, ausser_hash))
    else:
        con.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
