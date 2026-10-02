"""Konto-Einstellungen je Benutzer: Standardwerte, erlaubte Werte, Lesen und Schreiben."""
from __future__ import annotations

from typing import Any

from . import config, db

STANDARD: dict[str, Any] = {
    "dark": True,
    "textSize": "normal",
    "density": "normal",
    "language": "de",
    "notifyPopup": True,
    "notifyApp": True,
    "notifyWeekly": False,
}

ERLAUBT: dict[str, list[Any]] = {
    "textSize": ["klein", "normal", "gross"],
    "density": ["kompakt", "normal"],
    "language": list(config.SPRACHEN),
}

BOOLSCH = {"dark", "notifyPopup", "notifyApp", "notifyWeekly"}

_SPALTEN = {
    "dark": "dark",
    "textSize": "text_size",
    "density": "density",
    "language": "language",
    "notifyPopup": "notify_popup",
    "notifyApp": "notify_app",
    "notifyWeekly": "notify_weekly",
}


def pruefen(aenderung: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    """Trennt gültige Werte von Fehlern. Unbekannte Felder sind ein Fehler."""
    gueltig: dict[str, Any] = {}
    fehler: dict[str, str] = {}
    for schluessel, wert in aenderung.items():
        if schluessel not in STANDARD:
            fehler[schluessel] = "unbekanntes Feld"
            continue
        if schluessel in BOOLSCH:
            if isinstance(wert, bool):
                gueltig[schluessel] = wert
            else:
                fehler[schluessel] = "erwartet true oder false"
            continue
        erlaubt = ERLAUBT[schluessel]
        if wert in erlaubt:
            gueltig[schluessel] = wert
        else:
            fehler[schluessel] = "erlaubt: " + ", ".join(erlaubt)
    return gueltig, fehler


def anlegen(con, user_id: int) -> None:
    con.execute(
        "INSERT OR IGNORE INTO user_settings (user_id, dark, text_size, density, language, notify_popup, notify_app,"
        " notify_weekly, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            user_id,
            int(STANDARD["dark"]),
            STANDARD["textSize"],
            STANDARD["density"],
            STANDARD["language"],
            int(STANDARD["notifyPopup"]),
            int(STANDARD["notifyApp"]),
            int(STANDARD["notifyWeekly"]),
            db.jetzt(),
        ),
    )


def lesen(con, user_id: int) -> dict[str, Any]:
    row = db.zeile(con.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,)).fetchone())
    if row is None:
        anlegen(con, user_id)
        return dict(STANDARD, updatedAt=db.jetzt())
    return {
        "dark": bool(row["dark"]),
        "textSize": row["text_size"],
        "density": row["density"],
        "language": row["language"],
        "notifyPopup": bool(row["notify_popup"]),
        "notifyApp": bool(row["notify_app"]),
        "notifyWeekly": bool(row["notify_weekly"]),
        "updatedAt": row["updated_at"],
    }


def schreiben(con, user_id: int, gueltig: dict[str, Any]) -> dict[str, Any]:
    if gueltig:
        anlegen(con, user_id)
        setzer = ", ".join(f"{_SPALTEN[k]} = ?" for k in gueltig)
        werte = [int(v) if isinstance(v, bool) else v for v in gueltig.values()]
        con.execute(
            f"UPDATE user_settings SET {setzer}, updated_at = ? WHERE user_id = ?",
            (*werte, db.jetzt(), user_id),
        )
    return lesen(con, user_id)
