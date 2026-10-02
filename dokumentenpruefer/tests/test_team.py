"""Mitarbeiterverwaltung: Rechte serverseitig, CRUD, Deaktivieren, weiches Löschen, letzter Admin, Protokoll."""
import secrets

import pytest
from fastapi.testclient import TestClient

from app import auth, db, team
from app.main import app
from tests.conftest import PASSWORT


def _konto(email, rolle="mitglied", aktiv=True, name="Test Person"):
    """Legt ein Konto direkt in der Datenbank an, optional fertig eingerichtet."""
    with db.transaktion() as con:
        user, einmal = auth.benutzer_anlegen(con, email, name, rolle)
        if aktiv:
            auth.konto_abschliessen(con, user["id"], name, PASSWORT)
        return auth.benutzer_per_id(con, user["id"]), einmal


def _als(email):
    """Eigener Client, angemeldet als dieses Konto."""
    c = TestClient(app)
    c.__enter__()
    r = c.post("/api/anmelden", json={"email": email, "passwort": PASSWORT})
    assert r.status_code == 200, r.text
    return c


@pytest.fixture
def mitglied_client():
    email = f"m-{secrets.token_hex(4)}@test.local"
    _konto(email, "mitglied")
    c = _als(email)
    yield c
    c.__exit__(None, None, None)


@pytest.fixture
def ziel():
    email = f"ziel-{secrets.token_hex(4)}@test.local"
    user, _ = _konto(email, "mitglied", name="Ziel Person")
    return user


# ---------------------------------------------------------------- Rechte: nur Admin, nur mit Sitzung


ADMIN_ROUTEN = [
    ("GET", "/api/benutzer", None),
    ("POST", "/api/benutzer", {"email": "x@test.local", "name": "X Y"}),
    ("PATCH", "/api/benutzer/1", {"name": "Neu"}),
    ("DELETE", "/api/benutzer/1", {"bestaetigung": "x"}),
    ("POST", "/api/benutzer/1/einmal-passwort", None),
    ("POST", "/api/benutzer/1/wiederherstellen", None),
    ("GET", "/api/protokoll", None),
]


@pytest.mark.parametrize("methode,url,body", ADMIN_ROUTEN)
def test_ohne_anmeldung_401(methode, url, body):
    with TestClient(app) as c:
        r = c.request(methode, url, json=body)
        assert r.status_code == 401, (methode, url, r.text)


@pytest.mark.parametrize("methode,url,body", ADMIN_ROUTEN)
def test_mitglied_bekommt_403(mitglied_client, ziel, methode, url, body):
    url = url.replace("/1", f"/{ziel['id']}")
    r = mitglied_client.request(methode, url, json=body)
    assert r.status_code == 403, (methode, url, r.text)
    assert "benutzer" not in r.json() or isinstance(r.json().get("benutzer"), dict) is False
    # Nichts ist passiert: das Zielkonto ist unverändert.
    with db.transaktion() as con:
        u = auth.benutzer_per_id(con, ziel["id"])
    assert u["name"] == "Ziel Person" and u["status"] == "aktiv" and u["geloescht_am"] is None


def test_mitglied_sieht_eigenen_datensatz_ohne_adminfelder(mitglied_client):
    d = mitglied_client.get("/api/ich").json()["benutzer"]
    assert d["rolle"] == "mitglied"
    assert "passwort_hash" not in d and "einmal_hash" not in d


# ---------------------------------------------------------------- Admin: anlegen, ändern, deaktivieren, löschen


def test_admin_legt_an_und_protokolliert(client, admin):
    email = f"neu-{secrets.token_hex(4)}@test.local"
    r = client.post("/api/benutzer", json={"email": email, "name": "Neue Person", "rolle": "mitglied"})
    assert r.status_code == 200, r.text
    assert r.json()["benutzer"]["status"] == "einmal"
    assert client.post("/api/benutzer", json={"email": email, "name": "Noch mal", "rolle": "mitglied"}).status_code == 409
    assert client.post("/api/benutzer", json={"email": "kaputt", "name": "Neue Person"}).status_code == 400
    assert client.post("/api/benutzer", json={"email": "ok@test.local", "name": "N"}).status_code == 400
    assert client.post("/api/benutzer", json={"email": "ok2@test.local", "name": "N P", "rolle": "chef"}).status_code == 400
    p = client.get("/api/protokoll").json()["protokoll"]
    e = next(x for x in p if x["aktion"] == "angelegt" and x["ziel"]["email"] == email)
    assert e["akteur"]["email"] == admin["email"] and e["details"] == {"rolle": "mitglied"}


def test_admin_aendert_name_und_rolle(client, admin, ziel):
    r = client.patch(f"/api/benutzer/{ziel['id']}", json={"name": "Umbenannt Person", "rolle": "admin"})
    assert r.status_code == 200, r.text
    b = r.json()["benutzer"]
    assert b["name"] == "Umbenannt Person" and b["rolle"] == "admin"
    assert client.patch(f"/api/benutzer/{ziel['id']}", json={"name": "x"}).status_code == 400
    assert client.patch(f"/api/benutzer/{ziel['id']}", json={"rolle": "chef"}).status_code == 400
    assert client.patch(f"/api/benutzer/{ziel['id']}", json={"farbe": "blau"}).status_code == 400
    assert client.patch(f"/api/benutzer/{ziel['id']}", json={"passwort_hash": "x"}).status_code == 400
    aktionen = [x["aktion"] for x in client.get("/api/protokoll").json()["protokoll"] if x["ziel"]["id"] == ziel["id"]]
    assert "geaendert" in aktionen and "rolle" in aktionen
    # zurück zum Mitglied, geht, weil der Test-Admin weiter aktiv ist
    assert client.patch(f"/api/benutzer/{ziel['id']}", json={"rolle": "mitglied"}).status_code == 200


def test_deaktivieren_beendet_sitzung_und_sperrt_anmeldung(client, admin, ziel):
    with _als(ziel["email"]) as zc:
        assert zc.get("/api/ich").status_code == 200
        r = client.patch(f"/api/benutzer/{ziel['id']}", json={"status": "gesperrt"})
        assert r.status_code == 200 and r.json()["benutzer"]["status"] == "gesperrt"
        # laufende Sitzung ist sofort beendet
        assert zc.get("/api/ich").status_code == 401
        # Anmeldung mit richtigem Passwort wird abgelehnt, mit klarer Meldung
        r = zc.post("/api/anmelden", json={"email": ziel["email"], "passwort": PASSWORT})
        assert r.status_code == 403 and "deaktiviert" in r.json()["fehler"]
        # falsches Passwort verrät nicht, dass das Konto existiert und deaktiviert ist
        r = zc.post("/api/anmelden", json={"email": ziel["email"], "passwort": "Falsch-falsch-falsch-1!"})
        assert r.status_code == 401
        # wieder aktivieren
        r = client.patch(f"/api/benutzer/{ziel['id']}", json={"status": "aktiv"})
        assert r.status_code == 200 and r.json()["benutzer"]["status"] == "aktiv"
        assert zc.post("/api/anmelden", json={"email": ziel["email"], "passwort": PASSWORT}).status_code == 200
    aktionen = [x["aktion"] for x in client.get("/api/protokoll").json()["protokoll"] if x["ziel"]["id"] == ziel["id"]]
    assert aktionen[:2] == ["aktiviert", "deaktiviert"]


def test_reaktivierung_ohne_passwort_fuehrt_zur_erstanmeldung(client, admin):
    email = f"einmal-{secrets.token_hex(4)}@test.local"
    user, _ = _konto(email, aktiv=False)
    assert client.patch(f"/api/benutzer/{user['id']}", json={"status": "gesperrt"}).status_code == 200
    r = client.patch(f"/api/benutzer/{user['id']}", json={"status": "aktiv"})
    assert r.status_code == 200 and r.json()["benutzer"]["status"] == "einmal"


def test_loeschen_ist_weich_und_braucht_bestaetigung(client, admin, ziel):
    # Eine Prüfung des Kontos muss nach dem Löschen erhalten bleiben.
    with db.transaktion() as con:
        con.execute(
            "INSERT INTO pruefungen (id, user_id, dateiname, score, ampel, stunden, funde, sprachen, regelsaetze, erstellt, ergebnis, ordner)"
            " VALUES (?, ?, 'Alt.docx', 80, 'gruen', 1.0, 0, '[\"de\"]', '[\"din\"]', ?, '{}', '/tmp/x')",
            (secrets.token_hex(6), ziel["id"], db.jetzt()),
        )
    r = client.request("DELETE", f"/api/benutzer/{ziel['id']}", json={})
    assert r.status_code == 400 and r.json()["feld"] == "bestaetigung"
    r = client.request("DELETE", f"/api/benutzer/{ziel['id']}", json={"bestaetigung": "falsch@test.local"})
    assert r.status_code == 400
    with _als(ziel["email"]) as zc:
        r = client.request("DELETE", f"/api/benutzer/{ziel['id']}", json={"bestaetigung": ziel["email"].upper()})
        assert r.status_code == 200, r.text
        assert r.json()["benutzer"]["geloeschtAm"]
        assert zc.get("/api/ich").status_code == 401
        assert zc.post("/api/anmelden", json={"email": ziel["email"], "passwort": PASSWORT}).status_code == 403
    # nicht in der Standardliste, aber mit geloeschte=1; Daten bleiben
    ids = [b["id"] for b in client.get("/api/benutzer").json()["benutzer"]]
    assert ziel["id"] not in ids
    alle = client.get("/api/benutzer", params={"geloeschte": "1"}).json()["benutzer"]
    assert any(b["id"] == ziel["id"] and b["geloeschtAm"] for b in alle)
    with db.transaktion() as con:
        assert con.execute("SELECT COUNT(*) FROM pruefungen WHERE user_id = ?", (ziel["id"],)).fetchone()[0] == 1
    # gelöschte Konten: nicht ändern, kein Einmal-Passwort, E-Mail bleibt belegt
    assert client.patch(f"/api/benutzer/{ziel['id']}", json={"name": "Neu Name"}).status_code == 409
    assert client.post(f"/api/benutzer/{ziel['id']}/einmal-passwort").status_code == 409
    assert client.request("DELETE", f"/api/benutzer/{ziel['id']}", json={"bestaetigung": ziel["email"]}).status_code == 409
    r = client.post("/api/benutzer", json={"email": ziel["email"], "name": "Neu Angelegt"})
    assert r.status_code == 409 and "gelöscht" in r.json()["fehler"]
    # wiederherstellen: zurück als deaktiviertes Konto
    r = client.post(f"/api/benutzer/{ziel['id']}/wiederherstellen")
    assert r.status_code == 200 and r.json()["benutzer"]["geloeschtAm"] is None and r.json()["benutzer"]["status"] == "gesperrt"
    assert client.post(f"/api/benutzer/{ziel['id']}/wiederherstellen").status_code == 409
    aktionen = [x["aktion"] for x in client.get("/api/protokoll").json()["protokoll"] if x["ziel"]["id"] == ziel["id"]]
    assert "geloescht" in aktionen


def test_admin_schuetzt_sich_selbst(client, admin):
    me = client.get("/api/ich").json()["benutzer"]["id"]
    assert client.patch(f"/api/benutzer/{me}", json={"rolle": "mitglied"}).status_code == 400
    assert client.patch(f"/api/benutzer/{me}", json={"status": "gesperrt"}).status_code == 400
    assert client.request("DELETE", f"/api/benutzer/{me}", json={"bestaetigung": admin["email"]}).status_code == 400
    assert client.get("/api/ich").status_code == 200


def test_letzter_aktiver_admin_bleibt_erhalten(client, admin):
    """Ein zweiter Admin wird kurz der einzige aktive Admin; dann greift der Schutz."""
    email = f"admin2-{secrets.token_hex(4)}@test.local"
    zweiter, _ = _konto(email, "admin", name="Zweiter Admin")
    me = client.get("/api/ich").json()["benutzer"]["id"]
    with _als(email) as c2:
        # Der zweite Admin deaktiviert den Test-Admin: erlaubt, es gibt ja noch ihn selbst.
        assert c2.patch(f"/api/benutzer/{me}", json={"status": "gesperrt"}).status_code == 200
        assert c2.get("/api/benutzer").json()["aktiveAdmins"] == 1
        # Jetzt ist er der letzte: niemand darf ihn deaktivieren, löschen oder herabstufen.
        with db.transaktion() as con:
            assert team.aktive_admins(con) == 1
            akteur = {"id": 0, "email": "system@test.local"}
            for aufruf in (
                lambda: team.aendern(con, akteur, zweiter["id"], {"status": "gesperrt"}),
                lambda: team.aendern(con, akteur, zweiter["id"], {"rolle": "mitglied"}),
                lambda: team.loeschen(con, akteur, zweiter["id"], email),
            ):
                with pytest.raises(team.TeamFehler) as e:
                    aufruf()
                assert e.value.status == 409 and "letzte aktive Admin" in str(e.value)
            u = auth.benutzer_per_id(con, zweiter["id"])
            assert u["status"] == "aktiv" and u["rolle"] == "admin" and u["geloescht_am"] is None
        # Test-Admin wieder aktivieren, damit die übrigen Tests weiterlaufen.
        assert c2.patch(f"/api/benutzer/{me}", json={"status": "aktiv"}).status_code == 200
    r = client.post("/api/anmelden", json={"email": admin["email"], "passwort": admin["passwort"], "merken": True})
    assert r.status_code == 200
    # Mit zwei aktiven Admins darf der zweite deaktiviert werden.
    assert client.patch(f"/api/benutzer/{zweiter['id']}", json={"status": "gesperrt"}).status_code == 200


def test_protokoll_enthaelt_keine_geheimnisse(client, admin, ziel):
    client.post(f"/api/benutzer/{ziel['id']}/einmal-passwort")
    p = client.get("/api/protokoll").json()["protokoll"]
    e = next(x for x in p if x["aktion"] == "einmal_passwort" and x["ziel"]["id"] == ziel["id"])
    assert set(e) == {"id", "zeit", "akteur", "aktion", "aktionText", "ziel", "details"}
    assert e["details"] == {}
    with db.transaktion() as con:
        for row in con.execute("SELECT details FROM audit_log").fetchall():
            assert "hash" not in row["details"].lower() and "$argon2" not in row["details"]


def test_migration_haengt_spalte_an(tmp_path):
    """Eine Datenbank aus der ersten Fassung bekommt die neue Spalte beim Start."""
    import sqlite3
    pfad = tmp_path / "alt.sqlite3"
    alt = db.SCHEMA.replace("CREATE TABLE IF NOT EXISTS audit_log", "CREATE TABLE IF NOT EXISTS unbenutzt_x")
    with sqlite3.connect(pfad) as con:
        con.executescript(alt.split("CREATE TABLE IF NOT EXISTS unbenutzt_x")[0])
        assert "geloescht_am" not in {r[1] for r in con.execute("PRAGMA table_info(users)")}
    db.init_db(pfad)
    with sqlite3.connect(pfad) as con:
        assert "geloescht_am" in {r[1] for r in con.execute("PRAGMA table_info(users)")}
        assert con.execute("SELECT name FROM sqlite_master WHERE name='audit_log'").fetchone()
    db.init_db(pfad)  # zweiter Lauf ändert nichts
