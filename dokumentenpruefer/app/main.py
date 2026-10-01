"""Web-Dienst des Dokumentenprüfers: Seiten, Anmeldung, Konten, Einstellungen, Prüfung, Berichte."""
from __future__ import annotations

import asyncio
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

from . import auth, config, db, einstellungen, mail
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
        log.warning("Regeldateien fehlen in %s: %s", config.REGELN, ", ".join(regeln.DATEIEN[k] for k in fehlend))


# ---------------------------------------------------------------- Hilfen


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
        raise HTTPException(status_code=401, detail="Bitte zuerst anmelden.")
    return user


def admin_benutzer(user: dict[str, Any] = Depends(aktueller_benutzer)) -> dict[str, Any]:
    if user["rolle"] != "admin":
        raise HTTPException(status_code=403, detail="Nur für Admins")
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
    return JSONResponse({"fehler": exc.detail}, status_code=exc.status_code)


# ---------------------------------------------------------------- Seite


@app.get("/", response_class=HTMLResponse)
def startseite() -> HTMLResponse:
    html = (config.STATIC / "index.html").read_text(encoding="utf-8")
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
            return _fehler(401, "E-Mail-Adresse oder Passwort stimmt nicht.")
        if auth.gesperrt(user):
            return _fehler(423, f"Zu viele Fehlversuche. Bitte in {config.SPERRE_MINUTEN} Minuten erneut versuchen.")
        if user["status"] == "einmal":
            return _fehler(409, "Dieses Konto ist noch nicht eingerichtet. Bitte die Erstanmeldung mit dem Einmal-Passwort nutzen.", erstanmeldung=True)
        if user["status"] != "aktiv" or not auth.passwort_stimmt(user["passwort_hash"], passwort):
            auth.fehlversuch(con, user)
            return _fehler(401, "E-Mail-Adresse oder Passwort stimmt nicht.")
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
        return _fehler(400, "Der Name braucht 2 bis 80 Zeichen.")
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
        if user is None or auth.gesperrt(user) or not auth.einmal_passwort_stimmt(user, einmal):
            if user is not None:
                auth.fehlversuch(con, user)
            return _fehler(401, "E-Mail-Adresse oder Einmal-Passwort stimmt nicht, oder das Einmal-Passwort ist abgelaufen.")
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
            return _fehler(401, "Der Code stimmt nicht oder ist abgelaufen.")
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
        return _fehler(400, "Bitte einen Namen eingeben.", feld="name")
    verletzt = auth.passwort_regel(passwort)
    if verletzt:
        return _fehler(400, "Das Passwort erfüllt die Regel nicht.", regel=verletzt)
    if passwort != passwort2:
        return _fehler(400, "Die beiden Passwörter stimmen nicht überein.", regel=["wiederholung"])
    with db.transaktion() as con:
        user = auth.benutzer_per_email(con, email)
        if user is None or auth.gesperrt(user) or not auth.einmal_passwort_stimmt(user, einmal):
            return _fehler(401, "E-Mail-Adresse oder Einmal-Passwort stimmt nicht, oder das Einmal-Passwort ist abgelaufen.")
        if config.VERIFIZIERUNG == "code" and not auth.code_stimmt(con, user, code):
            return _fehler(401, "Der Code stimmt nicht oder ist abgelaufen.")
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
        return _fehler(400, "Diese Einstellung gibt es nicht oder der Wert ist nicht erlaubt.", felder=fehler)
    with db.transaktion() as con:
        einst = einstellungen.schreiben(con, user["id"], gueltig)
    return {"einstellungen": einst}


@app.post("/api/ich/passwort")
async def passwort_aendern(request: Request, user: dict[str, Any] = Depends(aktueller_benutzer)):
    daten = await _json(request)
    alt = str(daten.get("alt", ""))
    neu = str(daten.get("neu", ""))
    neu2 = str(daten.get("neu2", ""))
    if not auth.passwort_stimmt(user["passwort_hash"], alt):
        return _fehler(401, "Das bisherige Passwort stimmt nicht.")
    verletzt = auth.passwort_regel(neu)
    if verletzt:
        return _fehler(400, "Das neue Passwort erfüllt die Regel nicht.", regel=verletzt)
    if neu != neu2:
        return _fehler(400, "Die beiden Passwörter stimmen nicht überein.", regel=["wiederholung"])
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
        rows = db.zeilen(con.execute("SELECT * FROM users ORDER BY angelegt_am").fetchall())
    return {"benutzer": [auth.oeffentlich(r) for r in rows]}


@app.post("/api/benutzer")
async def benutzer_anlegen(request: Request, user: dict[str, Any] = Depends(admin_benutzer)):
    daten = await _json(request)
    email = str(daten.get("email", "")).strip().lower()
    name = str(daten.get("name", "")).strip()
    rolle = str(daten.get("rolle", "mitglied"))
    if not EMAIL_RE.match(email):
        return _fehler(400, "Bitte eine gültige E-Mail-Adresse eingeben.", feld="email")
    if len(name) < 2:
        return _fehler(400, "Bitte einen Namen eingeben.", feld="name")
    if rolle not in ("admin", "mitglied"):
        return _fehler(400, "Rolle muss admin oder mitglied sein.", feld="rolle")
    with db.transaktion() as con:
        if auth.benutzer_per_email(con, email):
            return _fehler(409, "Diese E-Mail-Adresse hat schon ein Konto.")
        neu, einmal = auth.benutzer_anlegen(con, email, name, rolle)
    return {"benutzer": auth.oeffentlich(neu), "einmalPasswort": einmal, "gueltigTage": config.EINMAL_PASSWORT_TAGE}


@app.post("/api/benutzer/{user_id}/einmal-passwort")
def einmal_neu(user_id: int, user: dict[str, Any] = Depends(admin_benutzer)):
    with db.transaktion() as con:
        ziel = auth.benutzer_per_id(con, user_id)
        if ziel is None:
            return _fehler(404, "Konto nicht gefunden.")
        einmal = auth.einmal_passwort_erneuern(con, user_id)
        auth.alle_sitzungen_beenden(con, user_id)
    return {"einmalPasswort": einmal, "gueltigTage": config.EINMAL_PASSWORT_TAGE}


@app.patch("/api/benutzer/{user_id}")
async def benutzer_aendern(user_id: int, request: Request, user: dict[str, Any] = Depends(admin_benutzer)):
    daten = await _json(request)
    with db.transaktion() as con:
        ziel = auth.benutzer_per_id(con, user_id)
        if ziel is None:
            return _fehler(404, "Konto nicht gefunden.")
        if "rolle" in daten:
            if daten["rolle"] not in ("admin", "mitglied"):
                return _fehler(400, "Rolle muss admin oder mitglied sein.")
            if ziel["id"] == user["id"] and daten["rolle"] != "admin":
                return _fehler(400, "Du kannst dir selbst die Admin-Rolle nicht entziehen.")
            con.execute("UPDATE users SET rolle = ? WHERE id = ?", (daten["rolle"], user_id))
        if "status" in daten and daten["status"] in ("aktiv", "gesperrt") and ziel["status"] != "einmal":
            if ziel["id"] == user["id"]:
                return _fehler(400, "Du kannst dich nicht selbst sperren.")
            con.execute("UPDATE users SET status = ? WHERE id = ?", (daten["status"], user_id))
            if daten["status"] == "gesperrt":
                auth.alle_sitzungen_beenden(con, user_id)
        neu = auth.benutzer_per_id(con, user_id)
    return {"benutzer": auth.oeffentlich(neu)}


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
        raise HTTPException(status_code=404, detail="Prüfung nicht gefunden.")
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


def _pruefung_antwort(row: dict[str, Any]) -> dict[str, Any]:
    ergebnis = db.json_laden(row["ergebnis"], {})
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
        "fazit": ergebnis.get("fazit", ""),
        "klassen": ergebnis.get("klassen", {}),
        "funde": ergebnis.get("funde", []),
        "todos": ergebnis.get("todos", []),
        "regelnVorhanden": ergebnis.get("regelnVorhanden", {}),
        "pdfs": _pdf_liste(row),
        "zip": f"/api/pruefung/{row['id']}/zip",
    }


def _pruefung_durchfuehren(
    name: str,
    inhalt: bytes,
    gewaehlt: list[str],
    zusatz: str | None,
    user: dict[str, Any],
    melden: Callable[[str, dict[str, Any]], None],
) -> dict[str, Any]:
    """Läuft in einem Arbeitsfaden, damit der Server währenddessen bedienbar bleibt.

    melden(phase, daten) berichtet den Fortschritt: lesen, pruefen, berichte (mit n von N).
    Die Datenbanktransaktion bleibt kurz; die PDFs entstehen danach.
    """
    melden("lesen", {})
    struktur = lesen.lesen(name, inhalt)
    melden("pruefen", {})
    ergebnis = pruefung.pruefen(struktur, gewaehlt)
    ergebnis["pruefer"] = user["name"]
    with db.transaktion() as con:
        einst = einstellungen.lesen(con, user["id"])
        sprachen = _sprachen(einst, zusatz)
        pruef_id = uuid.uuid4().hex[:12]
        ordner = config.PRUEFUNGEN / pruef_id
        ordner.mkdir(parents=True, exist_ok=True)
        con.execute(
            "INSERT INTO pruefungen (id, user_id, dateiname, score, ampel, stunden, funde, sprachen, regelsaetze, erstellt, ergebnis, ordner)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
            ),
        )
        row = _pruefung_laden(con, user, pruef_id)
    row["pruefer_name"] = user["name"]
    # Berichte sofort erzeugen, damit Pop-up und Knöpfe ohne Wartezeit funktionieren.
    auftraege = [(art, sp) for art in ("pruef", "fach") for sp in sprachen]
    for i, (art, sp) in enumerate(auftraege, 1):
        melden("berichte", {"n": i, "von": len(auftraege)})
        _pdf_pfad(row, art, sp)
    return _pruefung_antwort(row)


@app.post("/api/pruefung")
async def pruefung_starten(
    request: Request,
    datei: UploadFile = File(...),
    regelsaetze: str = Form("basis,din,ce"),
    zusatzsprache: str = Form(""),
    fortschritt: str = Form(""),
    user: dict[str, Any] = Depends(aktueller_benutzer),
):
    name = Path(datei.filename or "dokument").name
    if not name.lower().endswith((".docx", ".pdf")):
        return _fehler(400, "Nur Word (.docx) und PDF (.pdf) werden geprüft.")
    inhalt = await datei.read()
    if len(inhalt) > config.UPLOAD_MAX_BYTES:
        return _fehler(413, "Die Datei ist größer als 25 MB.")
    gewaehlt = [r for r in regelsaetze.split(",") if r in config.REGELSAETZE]
    if not gewaehlt:
        return _fehler(400, "Bitte mindestens einen Regelsatz wählen.")
    zusatz = zusatzsprache.strip() or None

    if fortschritt != "1":
        try:
            return await run_in_threadpool(_pruefung_durchfuehren, name, inhalt, gewaehlt, zusatz, user, lambda phase, daten: None)
        except lesen.LeseFehler as e:
            return _fehler(422, str(e))

    # Fortschritt als Zeilenstrom (NDJSON): eine Zeile je Phase, zuletzt das Ergebnis oder der Fehler.
    loop = asyncio.get_running_loop()
    ereignisse: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    def melden(phase: str, daten: dict[str, Any]) -> None:
        loop.call_soon_threadsafe(ereignisse.put_nowait, {"phase": phase, **daten})

    async def arbeiten() -> None:
        try:
            antwort = await run_in_threadpool(_pruefung_durchfuehren, name, inhalt, gewaehlt, zusatz, user, melden)
            await ereignisse.put({"phase": "fertig", "ergebnis": antwort})
        except lesen.LeseFehler as e:
            await ereignisse.put({"fehler": str(e), "status": 422})
        except Exception:
            log.exception("Prüfung von %s fehlgeschlagen", name)
            await ereignisse.put({"fehler": "Die Prüfung ist fehlgeschlagen. Bitte noch einmal versuchen.", "status": 500})

    async def zeilen():
        aufgabe = asyncio.create_task(arbeiten())
        try:
            while True:
                ereignis = await ereignisse.get()
                yield json.dumps(ereignis, ensure_ascii=False) + "\n"
                if "fehler" in ereignis or ereignis.get("phase") == "fertig":
                    break
        finally:
            await aufgabe

    return StreamingResponse(zeilen(), media_type="application/x-ndjson", headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})


@app.get("/api/pruefungen")
def pruefungen(user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        rows = db.zeilen(
            con.execute(
                "SELECT id, dateiname, score, ampel, stunden, funde, sprachen, erstellt FROM pruefungen WHERE user_id = ? ORDER BY erstellt DESC LIMIT 20",
                (user["id"],),
            ).fetchall()
        )
    return {"pruefungen": [dict(r, sprachen=db.json_laden(r["sprachen"], ["de"])) for r in rows]}


@app.get("/api/pruefung/{pruef_id}")
def pruefung_lesen(pruef_id: str, user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        row = _pruefung_laden(con, user, pruef_id)
    return _pruefung_antwort(row)


@app.get("/api/pruefung/{pruef_id}/pdf/{art}/{sprache}")
def pruefung_pdf(pruef_id: str, art: str, sprache: str, user: dict[str, Any] = Depends(aktueller_benutzer)):
    if art not in ("pruef", "fach") or sprache not in config.SPRACHEN:
        raise HTTPException(status_code=404, detail="Bericht nicht gefunden.")
    with db.transaktion() as con:
        row = _pruefung_laden(con, user, pruef_id)
    if sprache not in db.json_laden(row["sprachen"], ["de"]):
        raise HTTPException(status_code=404, detail="Für diese Sprache wurde bei der Prüfung kein Bericht gewählt.")
    row["pruefer_name"] = user["name"]
    pfad = _pdf_pfad(row, art, sprache)
    return FileResponse(str(pfad), media_type="application/pdf", filename=pfad.name)


@app.get("/api/pruefung/{pruef_id}/zip")
def pruefung_zip(pruef_id: str, user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        row = _pruefung_laden(con, user, pruef_id)
    row["pruefer_name"] = user["name"]
    puffer = io.BytesIO()
    with zipfile.ZipFile(puffer, "w", zipfile.ZIP_DEFLATED) as z:
        for eintrag in _pdf_liste(row):
            pfad = _pdf_pfad(row, eintrag["bericht"], eintrag["sprache"])
            z.write(pfad, pfad.name)
    puffer.seek(0)
    name = berichte.dateiname("pruef", row["dateiname"], "de", row["erstellt"]).replace("_Pruefbericht_DE_v01.pdf", "_Berichte.zip")
    return Response(puffer.getvalue(), media_type="application/zip", headers={"Content-Disposition": f'attachment; filename="{name}"'})


@app.post("/api/pruefung/{pruef_id}/ablegen")
def pruefung_ablegen(pruef_id: str, user: dict[str, Any] = Depends(aktueller_benutzer)):
    with db.transaktion() as con:
        row = _pruefung_laden(con, user, pruef_id)
    row["pruefer_name"] = user["name"]
    config.OUTPUT.mkdir(parents=True, exist_ok=True)
    abgelegt = []
    for eintrag in _pdf_liste(row):
        quelle = _pdf_pfad(row, eintrag["bericht"], eintrag["sprache"])
        ziel = config.OUTPUT / quelle.name
        shutil.copy2(quelle, ziel)
        abgelegt.append(str(ziel))
    return {"abgelegt": abgelegt, "ordner": str(config.OUTPUT)}


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
        f"Ergebnis: {row['score']} %, {texte.ampel('de', row['ampel'])}.\n\n"
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
