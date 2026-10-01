"""Sicherung/Wiederherstellung und echter HTTP-Neustart mit wegwerfbaren Testdaten."""
import io
import json
import os
from pathlib import Path
import signal
import socket
import sqlite3
import subprocess
import sys
import time
import zipfile

import httpx
import pytest
from docx import Document

from app import auth, config, db, mail, sicherung


def _dokument():
    d = Document(); d.add_paragraph("Installation und Wartung des Testgeräts.")
    b = io.BytesIO(); d.save(b)
    return b.getvalue()


def test_sicherung_wiederherstellung_mit_berichten(client, admin, tmp_path):
    r = client.post("/api/pruefung", files={"datei": ("Sicherung.docx", _dokument())}, data={"zusatzsprache": "en"})
    assert r.status_code == 200
    pid = r.json()["id"]
    client.post(f"/api/pruefung/{pid}/ablegen")
    archiv = tmp_path / "sicherung.zip"
    m = sicherung.sichern(archiv)
    assert sicherung.pruefen(archiv) == m
    assert not any("codes.log" in p for p in m["dateien"])
    ziel = tmp_path / "neu"
    sicherung.wiederherstellen(archiv, ziel)
    with sqlite3.connect(ziel / "daten/dokumentenpruefer.sqlite3") as con:
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert con.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 0
        assert con.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0
        ordner = Path(con.execute("SELECT ordner FROM pruefungen WHERE id=?", (pid,)).fetchone()[0])
        assert ordner == ziel / "daten/pruefungen" / pid
        assert len(list(ordner.glob("*.pdf"))) == 4
    with zipfile.ZipFile(archiv) as z:
        for name in m["dateien"]:
            if name.endswith(".pdf") or name.startswith("regeln/"):
                assert (ziel / name).read_bytes() == z.read(name)
    with pytest.raises(sicherung.SicherungsFehler, match="existiert"):
        sicherung.sichern(archiv)
    with pytest.raises(sicherung.SicherungsFehler, match="Zielordner"):
        sicherung.wiederherstellen(archiv, ziel)


def test_sicherung_erkennt_manipulation(client, admin, tmp_path):
    archiv = tmp_path / "gut.zip"
    sicherung.sichern(archiv)
    kaputt = tmp_path / "kaputt.zip"
    with zipfile.ZipFile(archiv) as src, zipfile.ZipFile(kaputt, "w") as dst:
        for name in src.namelist():
            dst.writestr(name, b"kaputt" if name.endswith("sqlite3") else src.read(name))
    with pytest.raises(sicherung.SicherungsFehler, match="Prüfsumme"):
        sicherung.wiederherstellen(kaputt, tmp_path / "nicht-anlegen")
    assert not (tmp_path / "nicht-anlegen").exists()


@pytest.mark.parametrize("name", ["../ausbruch", "/absolut", "daten/../../ausbruch", "daten\\ausbruch"])
def test_archivpfade_duerfen_nicht_ausbrechen(tmp_path, name):
    archiv = tmp_path / "falsch.zip"
    with zipfile.ZipFile(archiv, "w") as z:
        z.writestr(name, b"x")
        z.writestr("manifest.json", "{}")
    with pytest.raises(sicherung.SicherungsFehler):
        sicherung.wiederherstellen(archiv, tmp_path / "ziel")
    assert not (tmp_path / "ziel").exists()


def test_verifizierungsschluessel_landeten_nicht_in_logs(monkeypatch, tmp_path, caplog):
    monkeypatch.setattr(config, "DATEN", tmp_path)
    monkeypatch.setattr(config, "SMTP_HOST", "")
    code = auth.code_erzeugen()
    assert mail.code_senden("probe@example.invalid", code) is False
    assert code not in caplog.text
    assert not (tmp_path / "codes.log").exists()


def test_fehlendes_smtp_ist_verstaendlich(client, monkeypatch):
    with db.transaktion() as con:
        _, einmal = auth.benutzer_anlegen(con, "smtp-fehlt@example.invalid", "SMTP Test")
    monkeypatch.setattr(config, "ENTWICKLUNG", False)
    monkeypatch.setattr(config, "SMTP_HOST", "")
    r = client.post("/api/erstanmeldung/start", json={"email": "smtp-fehlt@example.invalid", "einmalPasswort": einmal})
    assert r.status_code == 503 and "nicht eingerichtet" in r.json()["fehler"]
    assert "code" not in r.json()


def test_smtp_fehler_ist_verstaendlich(client, monkeypatch):
    with db.transaktion() as con:
        _, einmal = auth.benutzer_anlegen(con, "smtp-kaputt@example.invalid", "SMTP Test")
    monkeypatch.setattr(mail, "smtp_konfiguriert", lambda: True)
    def kaputt(*args):
        raise OSError("Test: Server nicht erreichbar")
    monkeypatch.setattr(mail, "code_senden", kaputt)
    r = client.post("/api/erstanmeldung/start", json={"email": "smtp-kaputt@example.invalid", "einmalPasswort": einmal})
    assert r.status_code == 503 and "nicht versendet" in r.json()["fehler"]


def test_echter_server_neustart_doppelstart_und_restore(tmp_path):
    """Zwei echte Serverstarts, Persistenz und restaurierter Bestand über HTTP."""
    env = dict(os.environ, DP_DATEN=str(tmp_path / "daten"), DP_OUTPUT=str(tmp_path / "output"),
               DP_SMTP_HOST="", DP_DEV="0", DP_VERIFIZIERUNG="aus", PYTHONUNBUFFERED="1")
    # Nur Testkonten. Das Zufallspasswort wird weder ausgegeben noch gespeichert.
    import secrets
    passwort = secrets.token_urlsafe(30) + "A!"
    seed = """
import json,sys
from app import auth,db
db.init_db()
with db.transaktion() as con:
    u,_=auth.benutzer_anlegen(con,'neustart@example.invalid','Neustart Test','admin')
    auth.konto_abschliessen(con,u['id'],'Neustart Test',json.load(sys.stdin)['passwort'])
"""
    subprocess.run([sys.executable, "-c", seed], input=json.dumps({"passwort": passwort}), text=True,
                   env=env, check=True, capture_output=True)
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    kommando = [sys.executable, "-m", "app.start", "--ohne-browser", "--port", str(port)]

    def start(umgebung):
        prozess = subprocess.Popen(kommando, env=umgebung, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                if prozess.poll() is not None:
                    pytest.fail("Testserver wurde vorzeitig beendet")
                try:
                    if httpx.get(url + "/api/status", timeout=0.3, trust_env=False).status_code == 200:
                        return prozess
                except httpx.TransportError:
                    pass
                time.sleep(0.05)
            pytest.fail("Testserver nicht bereit")
        except BaseException:
            prozess.terminate(); prozess.wait(timeout=10)
            raise

    def stoppen(prozess):
        prozess.send_signal(signal.SIGINT)
        prozess.wait(timeout=10)
        assert prozess.returncode == 0

    prozess = start(env)
    try:
        doppel = subprocess.run(kommando, env=env, capture_output=True, text=True, timeout=10)
        assert doppel.returncode == 0 and "läuft bereits" in doppel.stdout
        with httpx.Client(base_url=url, trust_env=False) as c:
            assert c.post("/api/anmelden", json={"email": "neustart@example.invalid", "passwort": passwort}).status_code == 200
            r = c.post("/api/pruefung", files={"datei": ("Neustart.docx", _dokument())}, data={"zusatzsprache": "en"})
            assert r.status_code == 200
            erg = r.json()
            pdfs = {p["url"]: c.get(p["url"]).content for p in erg["pdfs"]}
            assert all(pdf.startswith(b"%PDF-") for pdf in pdfs.values())
    finally:
        stoppen(prozess)
    prozess = start(env)
    try:
        with httpx.Client(base_url=url, trust_env=False) as c:
            assert c.get("/api/pruefungen").status_code == 401
            assert c.post("/api/anmelden", json={"email": "neustart@example.invalid", "passwort": passwort}).status_code == 200
            assert any(p["id"] == erg["id"] for p in c.get("/api/pruefungen").json()["pruefungen"])
            for path, inhalt in pdfs.items():
                assert c.get(path).content == inhalt
        archiv = tmp_path / "neustart.zip"
        subprocess.run([sys.executable, "-m", "app.sicherung", "sichern", "--ziel", str(archiv)],
                       env=env, check=True, capture_output=True)
    finally:
        stoppen(prozess)
    ziel = tmp_path / "restauriert"
    subprocess.run([sys.executable, "-m", "app.sicherung", "wiederherstellen", str(archiv), "--ziel", str(ziel)],
                   env=env, check=True, capture_output=True)
    restore_env = dict(env, DP_DATEN=str(ziel / "daten"), DP_OUTPUT=str(ziel / "output"), DP_REGELN=str(ziel / "regeln"))
    prozess = start(restore_env)
    try:
        with httpx.Client(base_url=url, trust_env=False) as c:
            assert c.post("/api/anmelden", json={"email": "neustart@example.invalid", "passwort": passwort}).status_code == 200
            for path, inhalt in pdfs.items():
                assert c.get(path).content == inhalt
            assert c.get(erg["zip"]).status_code == 200
    finally:
        stoppen(prozess)
