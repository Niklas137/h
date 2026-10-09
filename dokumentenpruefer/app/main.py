"""Web-Dienst des Dokumentenprüfers: Seiten, Anmeldung, Konten, Einstellungen, Prüfung, Berichte."""
from __future__ import annotations

import asyncio
import hashlib
import io
import json
import logging
import platform
import re
import shutil
import subprocess
import uuid
import zipfile
from pathlib import Path
from typing import Any, Callable

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from . import auth, config, db, einstellungen, mail, meldungen
from .pruefer import berichte, lesen, pruefung, regeln, texte

log = logging.getLogger("dokumentenpruefer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Dokumentenprüfer", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=str(config.STATIC)), name="static")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.on_event("startup")
def start() -> None:
    db.init_db()
    with db.transaktion() as con:
        n = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if n == 0:
        log.warning("Noch kein Konto vorhanden. Admin anlegen: python -m app.verwaltung admin --email ... --name ...")
    fehlend = [k for k, v in regeln.vorhanden().items() if not v]
    if fehlend:
        log.warning("Regeldateien fehlen oder sind ungültig in %s: %s", config.REGELN, ", ".join(regeln.DATEIEN[k] for k in fehlend))


# ---------------------------------------------------------------- Hilfen


def _sprache(request: Request) -> str:
    """Sprache der Oberfläche aus dem Kopf X-Sprache; ohne Kopf Deutsch."""
    return meldungen.sprache_aus(request.headers.get("x-sprache"))


def _m(request: Request, schluessel: str, **werte: Any) -> str:
    return meldungen.t(_sprache(request), schluessel, **werte)


def _lesefehler_text(sprache: str, e: lesen.LeseFehler) -> str:
    return meldungen.t(sprache, e.schluessel) if e.schluessel else str(e)


def _fehler(status: int, meldung: str, **extra: Any) -> JSONResponse:
    return JSONResponse({"fehler": meldung, **extra}, status_code=status)


def _cookie_setzen(antwort: Response, token: str, merken: bool) -> None:
    antwort.set_cookie(
        config.COOKIE_NAME,
        token,
        max_age=config.SITZUNG_TAGE * 86400 if merken else None,
        httponly=True,
        samesite="lax",
        secure=config.COOKIE_SECURE,
        path="/",
    )


def _cookie_loeschen(antwort: Response) -> None:
    antwort.delete_cookie(config.COOKIE_NAME, path="/")


def aktueller_benutzer(request: Request) -> dict[str, Any]:
    token = request.cookies.get(config.COOKIE_NAME)
    with db.transaktion() as con:
        user = auth.sitzung_pruefen(con, token)
    if user is None:
        raise HTTPException(status_code=401, detail="anmelden_fehlt")
    return user


def admin_benutzer(user: dict[str, Any] = Depends(aktueller_benutzer)) -> dict[str, Any]:
    if user["rolle"] != "admin":
        raise HTTPException(status_code=403, detail="nur_admin")
    return user


async def _json(request: Request) -> dict[str, Any]:
    try:
        daten = await request.json()
    except Exception:
        return {}
    return daten if isinstance(daten, dict) else {}


def _geraet(request: Request) -> str:
    ua = request.headers.get("user-agent", "")
    teile = []
    for name in ("iPhone", "iPad", "Android", "Macintosh", "Windows", "Linux"):
        if name in ua:
            teile.append("Mac" if name == "Macintosh" else name)
            break
    for name in ("Safari", "Chrome", "Firefox", "Edg"):
        if name in ua and not (name == "Safari" and "Chrome" in ua):
            teile.append("Edge" if name == "Edg" else name)
            break
    return " · ".join(teile) or "Unbekanntes Gerät"


@app.exception_handler(HTTPException)
async def http_fehler(request: Request, exc: HTTPException):
    # Ein bekannter Schlüssel wird in der Sprache der Oberfläche ausgegeben, sonst der Text selbst.
    text = exc.detail if not isinstance(exc.detail, str) or exc.detail not in meldungen.TEXTE["de"] else _m(request, exc.detail)
    return JSONResponse({"fehler": text}, status_code=exc.status_code)


# ---------------------------------------------------------------- Seite


def _static_version() -> str:
    """Kurze Prüfsumme der Oberflächendateien: ändert sich mit jedem Stand, der Browser lädt dann neu."""
    h = hashlib.sha256()
    for name in ("index.html", "app.js", "i18n.js", "app.css"):
        pfad = config.STATIC / name
        if pfad.exists():
            h.update(pfad.read_bytes())
    return h.hexdigest()[:10]


@app.middleware("http")
async def static_ohne_cache(request: Request, call_next):
    """Oberflächendateien immer beim Server nachfragen, damit nach einem Update kein alter Stand hängen bleibt."""
    antwort = await call_next(request)
    if request.url.path.startswith("/static/"):
        antwort.headers["Cache-Control"] = "no-cache"
    return antwort


@app.get("/", response_class=HTMLResponse)
def startseite() -> HTMLResponse:
    html = (config.STATIC / "index.html").read_text(encoding="utf-8")
    v = _static_version()
    for name in ("app.css", "i18n.js", "app.js"):
        html = html.replace(f"/static/{name}\"", f"/static/{name}?v={v}\"")
    return HTMLResponse(html, headers={"Cache-Control": "no-store"})


@app.get("/api/status")
def status() -> dict[str, Any]:
    return {
        "version": "1.0.0",
        "verifizierung": config.VERIFIZIERUNG,
        "regeln": regeln.vorhanden(),
        "sprachen": config.SPRACHEN,
        "support": {"adresse": config.SUPPORT_ADRESSE, "telefon": config.SUPPORT_TELEFON, "zeiten": config.SUPPORT_ZEITEN},
        "berichtKopf": config.BERICHT_KOPF,
        "maxDateien": config.MAX_DATEIEN,
    }


# ---------------------------------------------------------------- Anmeldung


@app.post("/api/anmelden")
async def anmelden(request: Request, antwort: Response):
    daten = await _json(request)
    email = str(daten.get("email", "")).strip().lower()
    passwort = str(daten.get("passwort", ""))
    merken = bool(daten.get("merken", False))
    with db.transaktion() as con:
        user = auth.benutzer_per_email(con, email)
        if user is None or not passwort:
            return _fehler(401, _m(request, "login_falsch"))
        if auth.gesperrt(user):
            return _fehler(423, _m(request, "gesperrt", min=config.SPERRE_MINUTEN))
        if user["status"] == "einmal":
            return _fehler(409, _m(request, "erst_noetig"), erstanmeldung=True)
        if user["status"] != "aktiv" or not auth.passwort_stimmt(user["passwort_hash"], passwort):
            auth.fehlversuch(con, user)
            return _fehler(401, _m(request, "login_falsch"))
        auth.erfolg(con, user["id"])
        token = auth.sitzung_anlegen(con, user["id"], _geraet(request))
        einst = einstellungen.lesen(con, user["id"])
    antwort = JSONResponse({"benutzer": auth.oeffentlich(user), "einstellungen": einst})
    _cookie_setzen(antwort, token, merken)
    return antwort


@app.post("/api/abmelden")
def abmelden(request: Request):
    with db.transaktion() as con:
        auth.sitzung_beenden(con, request.cookies.get(config.COOKIE_NAME))
    antwort = JSONResponse({"ok": True})
    _cookie_loeschen(antwort)
    return antwort


@app.get("/api/ich")
def ich(request: Request, user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        einst = einstellungen.lesen(con, user["id"])
    return {"benutzer": auth.oeffentlich(user), "einstellungen": einst}


@app.patch("/api/ich")
async def ich_aendern(request: Request, user: dict[str, Any] = Depends(aktueller_benutzer)):
    daten = await _json(request)
    name = str(daten.get("name", "")).strip()
    if len(name) < 2 or len(name) > 80:
        return _fehler(400, _m(request, "name_laenge"))
    with db.transaktion() as con:
        con.execute("UPDATE users SET name = ? WHERE id = ?", (name, user["id"]))
        neu = auth.benutzer_per_id(con, user["id"])
    return {"benutzer": auth.oeffentlich(neu)}


# ---------------------------------------------------------------- Erstanmeldung


@app.post("/api/erstanmeldung/start")
async def erst_start(request: Request):
    daten = await _json(request)
    email = str(daten.get("email", "")).strip().lower()
    einmal = str(daten.get("einmalPasswort", "")).strip()
    with db.transaktion() as con:
        user = auth.benutzer_per_email(con, email)
        if user is not None and auth.gesperrt(user):
            return _fehler(423, _m(request, "gesperrt_einmal", min=config.SPERRE_MINUTEN))
        if user is None or not auth.einmal_passwort_stimmt(user, einmal):
            if user is not None:
                auth.fehlversuch(con, user)
            return _fehler(401, _m(request, "einmal_falsch"))
        if config.VERIFIZIERUNG == "code":
            code = auth.code_setzen(con, user["id"])
            gesendet = mail.code_senden(user["email"], code, user["name"])
            ergebnis: dict[str, Any] = {"verifizierung": True, "gesendet": gesendet, "minuten": config.CODE_MINUTEN}
            if config.ENTWICKLUNG:
                ergebnis["code"] = code
            return ergebnis
    return {"verifizierung": False}


@app.post("/api/erstanmeldung/code")
async def erst_code(request: Request):
    daten = await _json(request)
    email = str(daten.get("email", "")).strip().lower()
    code = str(daten.get("code", "")).strip()
    with db.transaktion() as con:
        user = auth.benutzer_per_email(con, email)
        if user is None or not auth.code_stimmt(con, user, code):
            return _fehler(401, _m(request, "code_falsch"))
    return {"ok": True}


@app.post("/api/erstanmeldung/abschluss")
async def erst_abschluss(request: Request):
    daten = await _json(request)
    email = str(daten.get("email", "")).strip().lower()
    einmal = str(daten.get("einmalPasswort", "")).strip()
    code = str(daten.get("code", "")).strip()
    name = str(daten.get("name", "")).strip()
    passwort = str(daten.get("passwort", ""))
    passwort2 = str(daten.get("passwort2", ""))
    if len(name) < 2:
        return _fehler(400, _m(request, "name_fehlt"), feld="name")
    verletzt = auth.passwort_regel(passwort)
    if verletzt:
        return _fehler(400, _m(request, "pwd_regel"), regel=verletzt)
    if passwort != passwort2:
        return _fehler(400, _m(request, "pwd_ungleich"), regel=["wiederholung"])
    with db.transaktion() as con:
        user = auth.benutzer_per_email(con, email)
        if user is not None and auth.gesperrt(user):
            return _fehler(423, _m(request, "gesperrt_einmal", min=config.SPERRE_MINUTEN))
        if user is None or not auth.einmal_passwort_stimmt(user, einmal):
            return _fehler(401, _m(request, "einmal_falsch"))
        if config.VERIFIZIERUNG == "code" and not auth.code_stimmt(con, user, code):
            return _fehler(401, _m(request, "code_falsch"))
        auth.konto_abschliessen(con, user["id"], name, passwort)
        einstellungen.anlegen(con, user["id"])
        token = auth.sitzung_anlegen(con, user["id"], _geraet(request))
        neu = auth.benutzer_per_id(con, user["id"])
        einst = einstellungen.lesen(con, user["id"])
    antwort = JSONResponse({"benutzer": auth.oeffentlich(neu), "einstellungen": einst})
    _cookie_setzen(antwort, token, True)
    return antwort


# ---------------------------------------------------------------- Einstellungen, Passwort, Sitzungen


@app.patch("/api/ich/einstellungen")
async def einstellungen_aendern(request: Request, user: dict[str, Any] = Depends(aktueller_benutzer)):
    daten = await _json(request)
    gueltig, fehler = einstellungen.pruefen(daten)
    if fehler:
        return _fehler(400, _m(request, "einstellung_ungueltig"), felder=fehler)
    with db.transaktion() as con:
        einst = einstellungen.schreiben(con, user["id"], gueltig)
    return {"einstellungen": einst}


@app.get("/api/regeln")
def regeln_liste(request: Request, user: dict[str, Any] = Depends(aktueller_benutzer)):
    """Alle wählbaren Prüfpunkte je Regelsatz, dazu die vom Konto ausgelassenen."""
    saetze: dict[str, Any] = {}
    sprache = _sprache(request)
    namen = {"basis": "Basisprüfung", "din": "DIN 82079-1", "ce": "CE / EU-Konformität"}
    for k in config.REGELSAETZE:
        name_anzeige = texte.normlogik(sprache, namen[k])
        try:
            punkte = [
                dict(p, bereichAnzeige=texte.bereich(sprache, {"Bereich": p["bereich"], **p}), empfehlungAnzeige=texte.empfehlung(sprache, {"Empfehlung": p["empfehlung"], **p}), klasseAnzeige=texte.klasse(sprache, p["fehlerklasse"]))
                for p in pruefung.punkte(k)
            ]
            saetze[k] = {"name": namen[k], "nameAnzeige": name_anzeige, "vorhanden": True, "punkte": punkte}
        except regeln.RegelFehler as e:
            saetze[k] = {"name": namen[k], "nameAnzeige": name_anzeige, "vorhanden": False, "punkte": [], "fehler": str(e)}
    with db.transaktion() as con:
        ausgelassen = einstellungen.pruefpunkte_lesen(con, user["id"])
    return {"regelsaetze": saetze, "ausgelassen": ausgelassen}


@app.put("/api/ich/pruefpunkte")
async def pruefpunkte_setzen(request: Request, user: dict[str, Any] = Depends(aktueller_benutzer)):
    """Merkt je Konto, welche Prüfpunkte bewusst ausgelassen werden (Liste von IDs)."""
    daten = await _json(request)
    ids = daten.get("ausgelassen")
    if not isinstance(ids, list) or any(not isinstance(x, str) for x in ids):
        return _fehler(400, _m(request, "punkte_liste"))
    bekannt = {p["id"] for k in config.REGELSAETZE if regeln.vorhanden().get(k) for p in pruefung.punkte(k)}
    unbekannt = sorted(set(ids) - bekannt)
    if unbekannt:
        return _fehler(400, _m(request, "punkt_unbekannt", ids=", ".join(unbekannt)))
    with db.transaktion() as con:
        gespeichert = einstellungen.pruefpunkte_schreiben(con, user["id"], ids)
    return {"ausgelassen": gespeichert}


@app.post("/api/ich/passwort")
async def passwort_aendern(request: Request, user: dict[str, Any] = Depends(aktueller_benutzer)):
    daten = await _json(request)
    alt = str(daten.get("alt", ""))
    neu = str(daten.get("neu", ""))
    neu2 = str(daten.get("neu2", ""))
    if not auth.passwort_stimmt(user["passwort_hash"], alt):
        return _fehler(401, _m(request, "pwd_alt_falsch"))
    verletzt = auth.passwort_regel(neu)
    if verletzt:
        return _fehler(400, _m(request, "pwd_neu_regel"), regel=verletzt)
    if neu != neu2:
        return _fehler(400, _m(request, "pwd_ungleich"), regel=["wiederholung"])
    with db.transaktion() as con:
        auth.passwort_setzen(con, user["id"], neu)
        auth.alle_sitzungen_beenden(con, user["id"], ausser_hash=user.get("sitzung_hash"))
    return {"ok": True}


@app.get("/api/ich/sitzungen")
def sitzungen(user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        liste = auth.sitzungen_des_benutzers(con, user["id"], user.get("sitzung_hash"))
    return {"sitzungen": liste}


@app.delete("/api/ich/sitzungen/{kurz_id}")
def sitzung_beenden(kurz_id: str, user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        n = auth.sitzung_loeschen_per_kurz_id(con, user["id"], kurz_id)
    return {"beendet": n}


# ---------------------------------------------------------------- Verwaltung (Admin)


@app.get("/api/benutzer")
def benutzer_liste(user: dict[str, Any] = Depends(admin_benutzer)):
    with db.transaktion() as con:
        rows = db.zeilen(con.execute("SELECT u.*, (SELECT COUNT(*) FROM pruefungen p WHERE p.user_id = u.id) AS pruefungen FROM users u ORDER BY angelegt_am").fetchall())
    return {"benutzer": [dict(auth.oeffentlich(r), pruefungen=r["pruefungen"]) for r in rows]}


def _inhaber_geschuetzt(request: Request, ziel: dict[str, Any], user: dict[str, Any]) -> JSONResponse | None:
    """Das Inhaber-Konto darf nur der Inhaber selbst anfassen."""
    if ziel.get("inhaber") and ziel["id"] != user["id"]:
        return _fehler(403, _m(request, "inhaber_schutz"))
    return None


@app.post("/api/benutzer")
async def benutzer_anlegen(request: Request, user: dict[str, Any] = Depends(admin_benutzer)):
    daten = await _json(request)
    email = str(daten.get("email", "")).strip().lower()
    name = str(daten.get("name", "")).strip()
    rolle = str(daten.get("rolle", "mitglied"))
    if not EMAIL_RE.match(email):
        return _fehler(400, _m(request, "email_ungueltig"), feld="email")
    if len(name) < 2:
        return _fehler(400, _m(request, "name_fehlt"), feld="name")
    if rolle not in ("admin", "mitglied"):
        return _fehler(400, _m(request, "rolle_ungueltig"), feld="rolle")
    with db.transaktion() as con:
        if auth.benutzer_per_email(con, email):
            return _fehler(409, _m(request, "email_vergeben"))
        neu, einmal = auth.benutzer_anlegen(con, email, name, rolle)
    return {"benutzer": auth.oeffentlich(neu), "einmalPasswort": einmal, "gueltigTage": config.EINMAL_PASSWORT_TAGE}


@app.post("/api/benutzer/{user_id}/einmal-passwort")
def einmal_neu(user_id: int, request: Request, user: dict[str, Any] = Depends(admin_benutzer)):
    with db.transaktion() as con:
        ziel = auth.benutzer_per_id(con, user_id)
        if ziel is None:
            return _fehler(404, _m(request, "konto_fehlt"))
        if (schutz := _inhaber_geschuetzt(request, ziel, user)) is not None:
            return schutz
        einmal = auth.einmal_passwort_erneuern(con, user_id)
        auth.alle_sitzungen_beenden(con, user_id)
    return {"einmalPasswort": einmal, "gueltigTage": config.EINMAL_PASSWORT_TAGE}


@app.patch("/api/benutzer/{user_id}")
async def benutzer_aendern(user_id: int, request: Request, user: dict[str, Any] = Depends(admin_benutzer)):
    daten = await _json(request)
    with db.transaktion() as con:
        ziel = auth.benutzer_per_id(con, user_id)
        if ziel is None:
            return _fehler(404, _m(request, "konto_fehlt"))
        if (schutz := _inhaber_geschuetzt(request, ziel, user)) is not None:
            return schutz
        if "rolle" in daten:
            if daten["rolle"] not in ("admin", "mitglied"):
                return _fehler(400, _m(request, "rolle_ungueltig"))
            if ziel["id"] == user["id"] and daten["rolle"] != "admin":
                return _fehler(400, _m(request, "admin_selbst"))
            con.execute("UPDATE users SET rolle = ? WHERE id = ?", (daten["rolle"], user_id))
        if "status" in daten and daten["status"] in ("aktiv", "gesperrt") and ziel["status"] != "einmal":
            if ziel["id"] == user["id"]:
                return _fehler(400, _m(request, "sperren_selbst"))
            con.execute("UPDATE users SET status = ? WHERE id = ?", (daten["status"], user_id))
            if daten["status"] == "gesperrt":
                auth.alle_sitzungen_beenden(con, user_id)
        neu = auth.benutzer_per_id(con, user_id)
    return {"benutzer": auth.oeffentlich(neu)}


@app.delete("/api/benutzer/{user_id}")
def benutzer_loeschen(user_id: int, request: Request, user: dict[str, Any] = Depends(admin_benutzer)):
    """Nur der Inhaber. Löscht Konto, Sitzungen, Einstellungen und die Prüfungen samt Berichten.

    Abgelegte Berichte im Ordner output bleiben liegen.
    """
    if not user.get("inhaber"):
        return _fehler(403, _m(request, "loeschen_inhaber"))
    with db.transaktion() as con:
        ziel = auth.benutzer_per_id(con, user_id)
        if ziel is None:
            return _fehler(404, _m(request, "konto_fehlt"))
        if ziel["id"] == user["id"]:
            return _fehler(400, _m(request, "loeschen_selbst"))
        ordner = [r["ordner"] for r in db.zeilen(con.execute("SELECT ordner FROM pruefungen WHERE user_id = ?", (user_id,)).fetchall())]
        con.execute("DELETE FROM users WHERE id = ?", (user_id,))  # Sitzungen, Einstellungen, Prüfungen hängen daran
    for pfad in ordner:
        shutil.rmtree(pfad, ignore_errors=True)
    log.info("Konto %s gelöscht durch %s, %d Prüfungen entfernt", ziel["email"], user["email"], len(ordner))
    return {"geloescht": auth.oeffentlich(ziel), "pruefungen": len(ordner)}


# ---------------------------------------------------------------- Prüfung


def _sprachen(user_einst: dict[str, Any], zusatz: str | None) -> list[str]:
    basis = user_einst.get("language") if user_einst.get("language") in config.SPRACHEN else "de"
    liste = [basis]
    if zusatz and zusatz in config.SPRACHEN and zusatz != basis:
        liste.append(zusatz)
    return liste


def _pruefung_laden(con, user: dict[str, Any], pruef_id: str) -> dict[str, Any]:
    row = db.zeile(con.execute("SELECT * FROM pruefungen WHERE id = ? AND user_id = ?", (pruef_id, user["id"])).fetchone())
    if row is None:
        raise HTTPException(status_code=404, detail="pruefung_fehlt")
    return row


def _pdf_pfad(row: dict[str, Any], art: str, sprache: str) -> Path:
    ordner = Path(row["ordner"])
    ordner.mkdir(parents=True, exist_ok=True)
    pfad = ordner / berichte.dateiname(art, row["dateiname"], sprache, row["erstellt"])
    if not pfad.exists():
        ergebnis = db.json_laden(row["ergebnis"], {})
        meta = {"dateiname": row["dateiname"], "erstellt": row["erstellt"], "pruefer": row.get("pruefer_name", "")}
        pfad.write_bytes(berichte.erzeugen(art, ergebnis, meta, sprache))
    return pfad


def _pdf_liste(row: dict[str, Any]) -> list[dict[str, str]]:
    sprachen = db.json_laden(row["sprachen"], ["de"])
    liste = []
    for art in ("pruef", "fach"):
        for sp in sprachen:
            liste.append({"bericht": art, "sprache": sp, "url": f"/api/pruefung/{row['id']}/pdf/{art}/{sp}", "dateiname": berichte.dateiname(art, row["dateiname"], sp, row["erstellt"])})
    return liste


def _anzeige(fund: dict[str, Any], sprache: str) -> dict[str, Any]:
    """Fund plus Anzeigetexte in der Oberflächensprache (die Rohfelder bleiben deutsch)."""
    return dict(
        fund,
        bereichAnzeige=texte.bereich(sprache, fund),
        empfehlungAnzeige=texte.empfehlung(sprache, fund),
        klasseAnzeige=texte.klasse(sprache, fund.get("Fehlerklasse")),
        bewertungAnzeige=texte.bewertung(sprache, fund),
    )


def _pruefung_antwort(row: dict[str, Any], sprache: str = "de") -> dict[str, Any]:
    ergebnis = db.json_laden(row["ergebnis"], {})
    fazit = texte.fazit(sprache, [tuple(x) for x in ergebnis.get("fazitTeile", [])]) if ergebnis.get("fazitTeile") else ""
    return {
        "id": row["id"],
        "dateiname": row["dateiname"],
        "erstellt": row["erstellt"],
        "score": row["score"],
        "ampel": row["ampel"],
        "stunden": row["stunden"],
        "fundeAnzahl": row["funde"],
        "sprachen": db.json_laden(row["sprachen"], ["de"]),
        "regelsaetze": db.json_laden(row["regelsaetze"], []),
        "ausgelassen": [dict(a, bereich=texte.bereich(sprache, {"Bereich": a.get("bereich", ""), **a})) for a in ergebnis.get("ausgelassen", [])],
        "punkteGesamt": ergebnis.get("punkteGesamt"),
        "punkteGeprueft": ergebnis.get("punkteGeprueft"),
        "fazit": fazit or ergebnis.get("fazit", ""),
        "klassen": ergebnis.get("klassen", {}),
        "funde": [_anzeige(f, sprache) for f in ergebnis.get("funde", [])],
        "todos": ergebnis.get("todos", []),
        "regelnVorhanden": ergebnis.get("regelnVorhanden", {}),
        "lesehinweise": [texte.lesehinweis(sprache, h) for h in ergebnis.get("lesehinweise", [])],
        "pruefstatus": ergebnis.get("pruefstatus", "altbestand"),
        "freigabe": False,
        "suchtrefferAnzahl": ergebnis.get("suchtrefferAnzahl", 0),
        "regelpruefungen": ergebnis.get("regelpruefungen", []),
        "bewertungsart": ergebnis.get("bewertungsart", "altbestand"),
        "pdfs": _pdf_liste(row),
        "zip": f"/api/pruefung/{row['id']}/zip",
    }


def _pruefung_durchfuehren(
    name: str,
    inhalt: bytes,
    gewaehlt: list[str],
    sprachen: list[str],
    user: dict[str, Any],
    melden: Callable[[str, dict[str, Any]], None],
    lauf_id: str | None = None,
    ausgelassen: list[str] | None = None,
    sprache: str = "de",
) -> dict[str, Any]:
    """Läuft in einem Arbeitsfaden, damit der Server währenddessen bedienbar bleibt.

    melden(phase, daten) berichtet den Fortschritt: lesen, pruefen, berichte (mit n von N).
    Die Datenbanktransaktion bleibt kurz; die PDFs entstehen danach.
    """
    melden("lesen", {})
    struktur, lesehinweise = lesen.lesen_mit_hinweisen(name, inhalt)
    melden("pruefen", {})
    ergebnis = pruefung.pruefen(struktur, gewaehlt, ausgelassen)
    ergebnis["pruefer"] = user["name"]
    ergebnis["lesehinweise"] = lesehinweise
    with db.transaktion() as con:
        pruef_id = uuid.uuid4().hex[:12]
        ordner = config.PRUEFUNGEN / pruef_id
        ordner.mkdir(parents=True, exist_ok=True)
        con.execute(
            "INSERT INTO pruefungen (id, user_id, dateiname, score, ampel, stunden, funde, sprachen, regelsaetze, erstellt, ergebnis, ordner, lauf)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                pruef_id,
                user["id"],
                name,
                ergebnis["score"],
                ergebnis["ampel"],
                ergebnis["stunden"],
                len(ergebnis["funde"]),
                json.dumps(sprachen),
                json.dumps(gewaehlt),
                db.jetzt(),
                json.dumps(ergebnis, ensure_ascii=False),
                str(ordner),
                lauf_id,
            ),
        )
        row = _pruefung_laden(con, user, pruef_id)
    row["pruefer_name"] = user["name"]
    # Berichte sofort erzeugen, damit Pop-up und Knöpfe ohne Wartezeit funktionieren.
    auftraege = [(art, sp) for art in ("pruef", "fach") for sp in sprachen]
    for i, (art, sp) in enumerate(auftraege, 1):
        melden("berichte", {"n": i, "von": len(auftraege)})
        _pdf_pfad(row, art, sp)
    return _pruefung_antwort(row, sprache)


def _lauf_antwort(lauf_id: str, ergebnisse: list[dict[str, Any]], fehler: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "lauf": lauf_id,
        "dateien": len(ergebnisse) + len(fehler),
        "ergebnisse": ergebnisse,
        "fehler": fehler,
        "pdfAnzahl": sum(len(e["pdfs"]) for e in ergebnisse),
        "zip": f"/api/lauf/{lauf_id}/zip",
        "ablegen": f"/api/lauf/{lauf_id}/ablegen",
    }


def _lauf_durchfuehren(
    dateien: list[tuple[str, bytes]],
    gewaehlt: list[str],
    sprachen: list[str],
    user: dict[str, Any],
    melden: Callable[[str, dict[str, Any]], None],
    ausgelassen: list[str] | None = None,
    sprache: str = "de",
) -> dict[str, Any]:
    """Prüft alle Dateien eines Laufs nacheinander. Ein unlesbares Dokument stoppt die anderen nicht.

    Nur defekte Regeldateien brechen den ganzen Lauf ab, weil dann kein Ergebnis verlässlich wäre.
    """
    lauf_id = uuid.uuid4().hex[:12]
    ergebnisse: list[dict[str, Any]] = []
    fehler: list[dict[str, Any]] = []
    anzahl = len(dateien)
    for i, (name, inhalt) in enumerate(dateien, 1):
        stand = {"dokument": i, "dokumente": anzahl, "datei": name}

        def melden_dokument(phase: str, daten: dict[str, Any], _stand: dict[str, Any] = stand) -> None:
            melden(phase, {**_stand, **daten})

        try:
            antwort = _pruefung_durchfuehren(name, inhalt, gewaehlt, sprachen, user, melden_dokument, lauf_id, ausgelassen, sprache)
        except lesen.LeseFehler as e:
            fehler.append({**stand, "fehler": _lesefehler_text(sprache, e), "status": 422})
            melden("ergebnis", fehler[-1])
            continue
        except regeln.RegelFehler:
            raise
        except Exception:
            log.exception("Prüfung von %s fehlgeschlagen", name)
            fehler.append({**stand, "fehler": meldungen.t(sprache, "pruefung_fehlgeschlagen"), "status": 500})
            melden("ergebnis", fehler[-1])
            continue
        ergebnisse.append(antwort)
        melden("ergebnis", {**stand, "ergebnis": antwort})
    return _lauf_antwort(lauf_id, ergebnisse, fehler)


@app.post("/api/pruefung")
async def pruefung_starten(
    request: Request,
    datei: list[UploadFile] = File(...),
    regelsaetze: str = Form("basis,din,ce"),
    sprachen: str = Form(""),
    zusatzsprache: str = Form(""),
    fortschritt: str = Form(""),
    ausgelassen: str = Form(""),
    user: dict[str, Any] = Depends(aktueller_benutzer),
):
    """Eine oder mehrere Dateien (Feld „datei“ mehrfach) in einem Lauf prüfen.

    Antwort bei einer Datei: die Prüfung selbst. Bei mehreren: der Lauf mit Ergebnissen und Fehlern je Datei.
    Mit fortschritt=1 kommt ein Zeilenstrom (NDJSON): Phasen je Dokument, ein „ergebnis“ je Dokument, zuletzt „fertig“.
    """
    if len(datei) > config.MAX_DATEIEN:
        return _fehler(400, _m(request, "zu_viele_dateien", n=config.MAX_DATEIEN))
    dateien: list[tuple[str, bytes]] = []
    for d in datei:
        name = Path(d.filename or "dokument").name
        if not name.lower().endswith((".docx", ".pdf")):
            return _fehler(400, _m(request, "dateityp", name=name))
        inhalt = await d.read()
        if len(inhalt) > config.UPLOAD_MAX_BYTES:
            return _fehler(413, _m(request, "zu_gross", name=name))
        dateien.append((name, inhalt))
    gewaehlt = list(dict.fromkeys(r.strip() for r in regelsaetze.split(",") if r.strip()))
    if not gewaehlt or any(r not in config.REGELSAETZE for r in gewaehlt):
        return _fehler(400, _m(request, "regelsaetze_ungueltig"))
    sprache = _sprache(request)
    # Berichtssprachen: ein bis zwei, frei gewählt und unabhängig von der Oberfläche. Ohne Angabe wie
    # früher: Oberflächensprache als Basis plus optionale Zusatzsprache.
    if sprachen.strip():
        sprachen_liste = list(dict.fromkeys(s.strip().lower() for s in sprachen.split(",") if s.strip()))
        if not 1 <= len(sprachen_liste) <= 2 or any(s not in config.SPRACHEN for s in sprachen_liste):
            return _fehler(400, _m(request, "sprachen_ungueltig"))
    else:
        with db.transaktion() as con:
            einst = einstellungen.lesen(con, user["id"])
        sprachen_liste = _sprachen(einst, zusatzsprache.strip() or None)
    ohne = [x.strip() for x in ausgelassen.split(",") if x.strip()]
    # Auswahl vorab prüfen, damit ein Fehler als 400 kommt und nicht erst im Lauf je Dokument.
    try:
        pruefung.pruefen([], gewaehlt, ohne)
    except pruefung.AuswahlFehler as e:
        return _fehler(400, meldungen.t(sprache, e.schluessel, **e.werte))
    except regeln.RegelFehler:
        pass  # meldet der Lauf selbst: 503 als JSON oder als letzte Zeile im Strom

    if fortschritt != "1":
        try:
            lauf = await run_in_threadpool(_lauf_durchfuehren, dateien, gewaehlt, sprachen_liste, user, lambda phase, daten: None, ohne, sprache)
        except regeln.RegelFehler as e:
            return _fehler(503, str(e))
        if len(dateien) == 1:
            if lauf["fehler"]:
                return _fehler(lauf["fehler"][0]["status"], lauf["fehler"][0]["fehler"])
            return dict(lauf["ergebnisse"][0], lauf=lauf["lauf"])
        return lauf

    # Fortschritt als Zeilenstrom (NDJSON): Phasen je Dokument, ein „ergebnis“ je Dokument, zuletzt „fertig“ oder ein Fehler.
    loop = asyncio.get_running_loop()
    ereignisse: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    def melden(phase: str, daten: dict[str, Any]) -> None:
        loop.call_soon_threadsafe(ereignisse.put_nowait, {"phase": phase, **daten})

    async def arbeiten() -> None:
        try:
            lauf = await run_in_threadpool(_lauf_durchfuehren, dateien, gewaehlt, sprachen_liste, user, melden, ohne, sprache)
            await ereignisse.put({"phase": "fertig", "lauf": lauf})
        except regeln.RegelFehler as e:
            await ereignisse.put({"fehler": str(e), "status": 503})
        except Exception:
            log.exception("Prüflauf fehlgeschlagen")
            await ereignisse.put({"fehler": meldungen.t(sprache, "pruefung_fehlgeschlagen"), "status": 500})

    async def zeilen():
        aufgabe = asyncio.create_task(arbeiten())
        try:
            while True:
                ereignis = await ereignisse.get()
                yield json.dumps(ereignis, ensure_ascii=False) + "\n"
                if ereignis.get("phase") == "fertig" or "phase" not in ereignis:
                    break
        finally:
            await aufgabe

    return StreamingResponse(zeilen(), media_type="application/x-ndjson", headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})


def _lauf_laden(con, user: dict[str, Any], lauf_id: str) -> list[dict[str, Any]]:
    rows = db.zeilen(con.execute("SELECT * FROM pruefungen WHERE lauf = ? AND user_id = ? ORDER BY erstellt, rowid", (lauf_id, user["id"])).fetchall())
    if not rows:
        raise HTTPException(status_code=404, detail="lauf_fehlt")
    for row in rows:
        row["pruefer_name"] = user["name"]
    return rows


def _ablegen(row: dict[str, Any]) -> list[str]:
    """Kopiert alle Berichte einer Prüfung nach output; nie überschreiben, gleicher Inhalt wird wiederverwendet."""
    config.OUTPUT.mkdir(parents=True, exist_ok=True)
    abgelegt = []
    for eintrag in _pdf_liste(row):
        quelle = _pdf_pfad(row, eintrag["bericht"], eintrag["sprache"])
        ziel = berichte.freier_dateiname(config.OUTPUT, eintrag["bericht"], row["dateiname"], eintrag["sprache"], row["erstellt"], quelle.read_bytes())
        if not ziel.exists():
            shutil.copy2(quelle, ziel)
        abgelegt.append(str(ziel))
    return abgelegt


def _zip_bauen(rows: list[dict[str, Any]]) -> bytes:
    puffer = io.BytesIO()
    vergeben: set[str] = set()
    with zipfile.ZipFile(puffer, "w", zipfile.ZIP_DEFLATED) as z:
        for row in rows:
            for eintrag in _pdf_liste(row):
                pfad = _pdf_pfad(row, eintrag["bericht"], eintrag["sprache"])
                name, n = pfad.name, 1
                while name in vergeben:  # gleiche Datei zweimal im Lauf
                    n += 1
                    name = f"{pfad.stem}_{n}{pfad.suffix}"
                vergeben.add(name)
                z.write(pfad, name)
    return puffer.getvalue()


@app.get("/api/lauf/{lauf_id}")
def lauf_lesen(lauf_id: str, request: Request, user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        rows = _lauf_laden(con, user, lauf_id)
    return _lauf_antwort(lauf_id, [_pruefung_antwort(r, _sprache(request)) for r in rows], [])


@app.get("/api/lauf/{lauf_id}/zip")
def lauf_zip(lauf_id: str, user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        rows = _lauf_laden(con, user, lauf_id)
    datum = rows[0]["erstellt"][:10]
    name = f"{datum}_Prueflauf_{len(rows)}_Dokumente_Berichte.zip"
    return Response(_zip_bauen(rows), media_type="application/zip", headers={"Content-Disposition": f'attachment; filename="{name}"'})


@app.post("/api/lauf/{lauf_id}/ablegen")
def lauf_ablegen(lauf_id: str, user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        rows = _lauf_laden(con, user, lauf_id)
    abgelegt = [pfad for row in rows for pfad in _ablegen(row)]
    return {"abgelegt": abgelegt, "ordner": str(config.OUTPUT), "dokumente": len(rows)}


@app.get("/api/pruefungen")
def pruefungen(user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        rows = db.zeilen(
            con.execute(
                "SELECT id, dateiname, score, ampel, stunden, funde, sprachen, erstellt, lauf FROM pruefungen WHERE user_id = ? ORDER BY erstellt DESC, rowid DESC LIMIT 20",
                (user["id"],),
            ).fetchall()
        )
    return {"pruefungen": [dict(r, sprachen=db.json_laden(r["sprachen"], ["de"])) for r in rows]}


@app.get("/api/pruefung/{pruef_id}")
def pruefung_lesen(pruef_id: str, request: Request, user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        row = _pruefung_laden(con, user, pruef_id)
    return _pruefung_antwort(row, _sprache(request))


@app.get("/api/pruefung/{pruef_id}/pdf/{art}/{sprache}")
def pruefung_pdf(pruef_id: str, art: str, sprache: str, user: dict[str, Any] = Depends(aktueller_benutzer)):
    if art not in ("pruef", "fach") or sprache not in config.SPRACHEN:
        raise HTTPException(status_code=404, detail="bericht_fehlt")
    with db.transaktion() as con:
        row = _pruefung_laden(con, user, pruef_id)
    if sprache not in db.json_laden(row["sprachen"], ["de"]):
        raise HTTPException(status_code=404, detail="bericht_sprache")
    row["pruefer_name"] = user["name"]
    pfad = _pdf_pfad(row, art, sprache)
    return FileResponse(str(pfad), media_type="application/pdf", filename=pfad.name)


@app.get("/api/pruefung/{pruef_id}/zip")
def pruefung_zip(pruef_id: str, user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        row = _pruefung_laden(con, user, pruef_id)
    row["pruefer_name"] = user["name"]
    name = berichte.dateiname("pruef", row["dateiname"], "de", row["erstellt"]).replace("_Pruefbericht_DE_v01.pdf", "_Berichte.zip")
    return Response(_zip_bauen([row]), media_type="application/zip", headers={"Content-Disposition": f'attachment; filename="{name}"'})


@app.post("/api/pruefung/{pruef_id}/ablegen")
def pruefung_ablegen(pruef_id: str, user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        row = _pruefung_laden(con, user, pruef_id)
    row["pruefer_name"] = user["name"]
    return {"abgelegt": _ablegen(row), "ordner": str(config.OUTPUT)}


@app.post("/api/pruefung/{pruef_id}/mail-entwurf")
async def pruefung_mail(pruef_id: str, request: Request, user: dict[str, Any] = Depends(aktueller_benutzer)):
    """Legt auf dem Mac einen Entwurf in Apple Mail an (Fachbericht angehängt). Sendet nie."""
    daten = await _json(request)
    with db.transaktion() as con:
        row = _pruefung_laden(con, user, pruef_id)
    row["pruefer_name"] = user["name"]
    sprachen = db.json_laden(row["sprachen"], ["de"])
    anhaenge = [_pdf_pfad(row, "fach", sp) for sp in sprachen]
    betreff = f"Fachbericht Dokumentenprüfung: {Path(row['dateiname']).stem}"
    empfaenger = str(daten.get("an", "")).strip()
    text = (
        "Guten Tag,\n\n"
        f"anbei der Fachbericht zur Prüfung des Dokuments {row['dateiname']} "
        f"({', '.join(config.SPRACHNAMEN_DE.get(s, s) for s in sprachen)}).\n\n"
        f"Ergebnis: {row['score']} %, {texte.ampel('de', row['ampel'])}.\n"
        f"{texte.t('de', 'hinweis_vorpruefung', firma=config.BERICHT_KOPF)}\n\n"
        "Bei Fragen melden Sie sich gern.\n\n"
        f"Mit freundlichen Grüßen\n{user['name']}\n{config.BERICHT_KOPF}"
    )
    if platform.system() == "Darwin":
        skript = _applescript_entwurf(betreff, text, empfaenger, anhaenge)
        try:
            subprocess.run(["osascript", "-e", skript], check=True, capture_output=True, timeout=30)
            return {"entwurf": "mail", "betreff": betreff, "anhaenge": [a.name for a in anhaenge]}
        except Exception as e:  # pragma: no cover (nur auf dem Mac)
            log.warning("Apple Mail Entwurf fehlgeschlagen: %s", e)
    return {"entwurf": "text", "betreff": betreff, "text": text, "anhaenge": [a.name for a in anhaenge]}


def _applescript_entwurf(betreff: str, text: str, empfaenger: str, anhaenge: list[Path]) -> str:
    def q(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    zeilen = [
        'tell application "Mail"',
        f'set neu to make new outgoing message with properties {{subject:"{q(betreff)}", content:"{q(text)}" & return & return, visible:true}}',
    ]
    if empfaenger:
        zeilen.append(f'tell neu to make new to recipient at end of to recipients with properties {{address:"{q(empfaenger)}"}}')
    for a in anhaenge:
        zeilen.append(f'tell neu to make new attachment with properties {{file name:(POSIX file "{q(str(a))}")}} at after the last paragraph')
    zeilen.append("end tell")
    return "\n".join(zeilen)
