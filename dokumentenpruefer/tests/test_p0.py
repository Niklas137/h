"""Gegenproben: keine Freigabe aus Suchwörtern, Regeln vollständig, Sperre wirksam."""
import copy
import io
import json
import secrets

import pytest
from docx import Document
from fastapi.testclient import TestClient
from PyPDF2 import PdfReader

from app import auth, cli, config, db
from app.main import app
from app.pruefer import berichte, pruefung, regeln, texte


def struktur(*texteingaben):
    return [{"text": t, "heading": "Prüfkapitel"} for t in texteingaben]


def docx_bytes():
    doc = Document()
    doc.add_paragraph("Kurzer Prüftext.")
    puffer = io.BytesIO()
    doc.save(puffer)
    return puffer.getvalue()


@pytest.fixture
def katalog():
    return {k: copy.deepcopy(regeln.laden(k)) for k in config.REGELSAETZE}


@pytest.mark.parametrize("inhalt", [None, "{kaputt", "{}", "[]", '[null]', '[{}]'])
def test_ungueltige_regeln_stoppen_pruefung(tmp_path, monkeypatch, inhalt):
    monkeypatch.setattr(config, "REGELN", tmp_path)
    if inhalt is not None:
        (tmp_path / regeln.DATEIEN["din"]).write_text(inhalt)
    with pytest.raises(ValueError, match="Regelsatz"):
        pruefung.pruefen(struktur("Kurzer Text."), ["din"])


@pytest.mark.parametrize("feld,wert", [
    ("id", ""), ("keywords", "warnung"), ("keywords", []),
    ("keywords", [""]), ("fehlerklasse", "unbekannt"),
    ("gewichtung", -1), ("gewichtung", True), ("gewichtung", float("nan")),
    ("gewichtung", 10**1000),
    ("pflicht", "false"), ("empfehlung", None),
])
def test_regelschema_wird_geprueft(tmp_path, monkeypatch, katalog, feld, wert):
    katalog["din"][0][feld] = wert
    (tmp_path / regeln.DATEIEN["din"]).write_text(json.dumps(katalog["din"]))
    monkeypatch.setattr(config, "REGELN", tmp_path)
    with pytest.raises(ValueError, match="Regelsatz"):
        pruefung.pruefen(struktur("Text."), ["din"])


def test_doppelte_regel_id_ist_fehler(tmp_path, monkeypatch, katalog):
    katalog["din"].append(katalog["din"][0])
    (tmp_path / regeln.DATEIEN["din"]).write_text(json.dumps(katalog["din"]))
    monkeypatch.setattr(config, "REGELN", tmp_path)
    with pytest.raises(ValueError, match="Regelsatz"):
        pruefung.pruefen(struktur("Text."), ["din"])


def test_defekte_datei_wird_nach_gueltigem_laden_nicht_aus_cache_ersetzt(tmp_path, monkeypatch, katalog):
    import os
    pfad = tmp_path / regeln.DATEIEN["din"]
    pfad.write_text(json.dumps(katalog["din"]))
    monkeypatch.setattr(config, "REGELN", tmp_path)
    zeit = pfad.stat().st_mtime_ns
    assert regeln.laden("din")
    pfad.write_bytes(b"\xff")
    os.utime(pfad, ns=(zeit, zeit))
    assert regeln.vorhanden()["din"] is False
    with pytest.raises(ValueError, match="Regelsatz"):
        pruefung.pruefen(struktur("Text."), ["din"])


def test_ungueltiger_teil_der_auswahl_wird_nicht_ignoriert(client, admin, tmp_path, capsys):
    r = client.post("/api/pruefung", files={"datei": ("probe.docx", docx_bytes())},
                    data={"regelsaetze": "din,nix"})
    assert r.status_code == 400
    datei = tmp_path / "probe.docx"
    datei.write_bytes(docx_bytes())
    assert cli.main(["pruefen", str(datei), "--regelsaetze", "din,nix"]) == 2
    assert "--regelsaetze" in capsys.readouterr().err


def test_nicht_gewaehlte_regeln_duerfen_fehlen(tmp_path, monkeypatch, katalog):
    (tmp_path / regeln.DATEIEN["din"]).write_text(json.dumps(katalog["din"]))
    monkeypatch.setattr(config, "REGELN", tmp_path)
    erg = pruefung.pruefen(struktur("Text."), ["din"])
    assert erg["regelsaetze"] == ["din"]
    assert erg["regelnVorhanden"] == {"basis": False, "din": True, "ce": False}


def test_stichwortliste_ist_keine_freigabe(katalog):
    # Alle Suchwörter kommen vor, der Score ist 100. Die Ampel folgt dem Score (Grün),
    # die fachliche Freigabe bleibt trotzdem offen und wird als Daten mitgegeben.
    woerter = [r["keywords"][0] + " fehlt." for rs in katalog.values() for r in rs]
    erg = pruefung.pruefen(struktur(*woerter))
    assert erg["score"] == 100 and erg["ampel"] == "gruen"
    assert erg["freigabe"] is False
    assert erg["pruefstatus"] == "fachlich_offen"
    assert erg["suchtrefferAnzahl"] == 24
    assert "grundsätzlich verwendbar" in erg["fazit"]


def test_kritischer_befund_steht_im_fazit(katalog):
    # Ampel nach Score wie in app.py; der kritische Fund wird im Fazit genannt.
    woerter = [r["keywords"][0] for rs in katalog.values() for r in rs if r["id"] != "CE-001"]
    erg = pruefung.pruefen(struktur(*woerter))
    assert erg["score"] == 95
    assert erg["klassen"]["Kritisch"] == 1
    assert erg["ampel"] == "gruen"
    assert erg["fazitTeile"][0][0] == "fazit_gruen"
    assert "1 kritische Abweichung" in erg["fazit"]
    assert "CE wurde 1 Nachweislücke" in erg["fazit"]


@pytest.mark.parametrize("stream", [False, True])
def test_api_regelfehler_ohne_pruefung_oder_berichte(client, admin, tmp_path, monkeypatch, stream):
    with db.transaktion() as con:
        vorher = con.execute("SELECT COUNT(*) FROM pruefungen").fetchone()[0]
    ordner_vorher = set(config.PRUEFUNGEN.iterdir())
    monkeypatch.setattr(config, "REGELN", tmp_path)
    r = client.post("/api/pruefung", files={"datei": ("probe.docx", docx_bytes())},
                    data={"regelsaetze": "din", "fortschritt": "1" if stream else ""})
    if stream:
        ereignisse = [json.loads(z) for z in r.text.splitlines()]
        assert ereignisse[-1]["status"] == 503
        assert not any(e.get("phase") in ("fertig", "berichte") for e in ereignisse)
        assert "Regelsatz" in ereignisse[-1]["fehler"]
    else:
        assert r.status_code == 503
        assert "Regelsatz" in r.json()["fehler"]
    with db.transaktion() as con:
        assert con.execute("SELECT COUNT(*) FROM pruefungen").fetchone()[0] == vorher
    assert set(config.PRUEFUNGEN.iterdir()) == ordner_vorher


def test_cli_regelfehler_ohne_pdf(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(config, "REGELN", tmp_path / "fehlt")
    datei = tmp_path / "probe.docx"
    datei.write_bytes(docx_bytes())
    ziel = tmp_path / "berichte"
    assert cli.main(["pruefen", str(datei), "--ausgabe", str(ziel)]) != 0
    assert not ziel.exists()
    assert "Regelsatz" in capsys.readouterr().err


@pytest.mark.parametrize("sprache", ["de", "en", "uk", "ru"])
@pytest.mark.parametrize("art", ["pruef", "fach"])
def test_pdf_kennzeichnet_vorpruefung_und_ungeprueftes(katalog, sprache, art):
    erg = pruefung.pruefen(struktur(*(r["keywords"][0] for r in katalog["din"])), ["din"])
    pdf = berichte.erzeugen(art, erg, {"dateiname": "Probe.docx", "pruefer": "Test"}, sprache)
    text = " ".join(" ".join(p.extract_text().split()) for p in PdfReader(io.BytesIO(pdf)).pages)
    assert " ".join(texte.t(sprache, "hinweis_vorpruefung", firma=config.BERICHT_KOPF).split()) in text
    assert texte.t(sprache, "ce_nicht_geprueft") in text
    assert texte.t(sprache, "bewertung") in text


def test_erstanmeldung_hebt_sperre_nicht_auf():
    with TestClient(app) as c:
        email = secrets.token_hex(8) + "@example.invalid"
        passwort = secrets.token_urlsafe(24) + "A!"
        with db.transaktion() as con:
            user, _ = auth.benutzer_anlegen(con, email, "Sperrtest")
            auth.konto_abschliessen(con, user["id"], "Sperrtest", passwort)
        for _ in range(config.FEHLVERSUCHE_MAX):
            assert c.post("/api/anmelden", json={"email": email, "passwort": "falsch"}).status_code == 401
        with db.transaktion() as con:
            sperre = auth.benutzer_per_email(con, email)["gesperrt_bis"]
        for _ in range(config.FEHLVERSUCHE_MAX + 1):
            c.post("/api/erstanmeldung/start", json={"email": email, "einmalPasswort": "falsch"})
        with db.transaktion() as con:
            assert auth.benutzer_per_email(con, email)["gesperrt_bis"] == sperre
        assert c.post("/api/anmelden", json={"email": email, "passwort": passwort}).status_code == 423
        # Eine regulär abgelaufene Sperre muss die Anmeldung wieder erlauben.
        with db.transaktion() as con:
            con.execute("UPDATE users SET gesperrt_bis = ? WHERE id = ?", ("2000-01-01T00:00:00+00:00", user["id"]))
        assert c.post("/api/anmelden", json={"email": email, "passwort": passwort}).status_code == 200
