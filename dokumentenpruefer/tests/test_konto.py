"""Anmeldung, Erstanmeldung, Passwortregel, Einstellungen, Sitzungen, Verwaltung."""
from app import auth
from tests.conftest import PASSWORT


def test_status_ohne_anmeldung(client):
    r = client.get("/api/status")
    assert r.status_code == 200
    assert "sprachen" in r.json() or "regeln" in r.json() or r.json()


def test_ich_ohne_cookie_ist_401():
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as c:
        assert c.get("/api/ich").status_code == 401


def test_passwortregel():
    assert auth.passwort_regel("kurz") == ["laenge", "grossbuchstabe", "sonderzeichen"]
    assert auth.passwort_regel("nurkleinbuchstabenabcdef!") == ["grossbuchstabe"]
    assert auth.passwort_regel("Ohne Sonderzeichen 2026") == ["sonderzeichen"]
    assert auth.passwort_regel("Ärger-mit-Umlauten-1") == []
    assert auth.passwort_regel(PASSWORT) == []


def test_erstanmeldung_lehnt_schwaches_passwort_ab(client, admin):
    r = client.post(
        "/api/erstanmeldung/abschluss",
        json={"email": admin["email"], "einmalPasswort": admin["einmal"], "code": admin["code"],
              "name": "X Y", "passwort": "schwach", "passwort2": "schwach"},
    )
    assert r.status_code == 400
    assert "laenge" in r.json()["regel"]


def test_einmalpasswort_nach_abschluss_ungueltig(client, admin):
    r = client.post("/api/erstanmeldung/start", json={"email": admin["email"], "einmalPasswort": admin["einmal"]})
    assert r.status_code == 401


def test_ich_nach_erstanmeldung(client, admin):
    r = client.get("/api/ich")
    assert r.status_code == 200
    d = r.json()
    assert d["benutzer"]["email"] == admin["email"]
    assert d["benutzer"]["rolle"] == "admin"
    assert d["einstellungen"]["language"] == "de"
    assert "passwort_hash" not in d["benutzer"]


def test_abmelden_und_anmelden(client, admin):
    assert client.post("/api/abmelden").status_code == 200
    assert client.get("/api/ich").status_code == 401
    r = client.post("/api/anmelden", json={"email": admin["email"], "passwort": "falsch-Falsch-falsch!"})
    assert r.status_code == 401
    r = client.post("/api/anmelden", json={"email": admin["email"], "passwort": admin["passwort"], "merken": True})
    assert r.status_code == 200, r.text
    assert client.get("/api/ich").status_code == 200


def test_einstellungen_patch_nur_geaenderte_schluessel(client, admin):
    r = client.patch("/api/ich/einstellungen", json={"dark": False, "language": "uk", "textSize": "gross"})
    assert r.status_code == 200, r.text
    e = r.json()["einstellungen"]
    assert e["dark"] is False and e["language"] == "uk" and e["textSize"] == "gross"
    assert e["density"] == "normal"
    r = client.patch("/api/ich/einstellungen", json={"language": "klingonisch"})
    assert r.status_code == 400
    r = client.patch("/api/ich/einstellungen", json={"language": "de", "dark": True, "textSize": "normal"})
    assert r.status_code == 200
    assert client.get("/api/ich").json()["einstellungen"]["language"] == "de"


def test_name_aendern(client, admin):
    assert client.patch("/api/ich", json={"name": "A"}).status_code == 400
    r = client.patch("/api/ich", json={"name": "Test Admin"})
    assert r.status_code == 200 and r.json()["benutzer"]["name"] == "Test Admin"


def test_passwort_aendern(client, admin):
    neu = "Noch-sichereres-Passwort-7!"
    r = client.post("/api/ich/passwort", json={"alt": "falsch", "neu": neu, "neu2": neu})
    assert r.status_code in (400, 401)
    r = client.post("/api/ich/passwort", json={"alt": admin["passwort"], "neu": "zu kurz", "neu2": "zu kurz"})
    assert r.status_code == 400
    r = client.post("/api/ich/passwort", json={"alt": admin["passwort"], "neu": neu, "neu2": neu})
    assert r.status_code == 200, r.text
    # zurücksetzen, damit die übrigen Tests das bekannte Passwort nutzen können
    r = client.post("/api/ich/passwort", json={"alt": neu, "neu": admin["passwort"], "neu2": admin["passwort"]})
    assert r.status_code == 200, r.text


def test_sitzungen(client, admin):
    r = client.get("/api/ich/sitzungen")
    assert r.status_code == 200
    liste = r.json()["sitzungen"]
    assert len(liste) >= 1
    assert any(s.get("aktuell") for s in liste)


def test_verwaltung_benutzer_anlegen_und_erstanmeldung(client, admin):
    r = client.post("/api/benutzer", json={"email": "falk@test.local", "name": "Falk Test", "rolle": "mitglied"})
    assert r.status_code == 200, r.text
    d = r.json()
    einmal = d["einmalPasswort"]
    assert len(einmal) == 14 and einmal.count("-") == 2
    assert d["benutzer"]["status"] == "einmal"
    r = client.get("/api/benutzer")
    assert any(b["email"] == "falk@test.local" for b in r.json()["benutzer"])

    # Anmeldung mit normalem Passwort geht noch nicht
    r = client.post("/api/anmelden", json={"email": "falk@test.local", "passwort": einmal})
    assert r.status_code == 409 and r.json().get("erstanmeldung") is True

    # Neues Einmal-Passwort anfordern, altes ist dann ungültig
    uid = d["benutzer"]["id"]
    r = client.post(f"/api/benutzer/{uid}/einmal-passwort")
    assert r.status_code == 200
    einmal2 = r.json()["einmalPasswort"]
    r = client.post("/api/erstanmeldung/start", json={"email": "falk@test.local", "einmalPasswort": einmal})
    assert r.status_code == 401
    r = client.post("/api/erstanmeldung/start", json={"email": "falk@test.local", "einmalPasswort": einmal2})
    assert r.status_code == 200, r.text
    code = r.json()["code"]
    assert client.post("/api/erstanmeldung/code", json={"email": "falk@test.local", "code": "000000"}).status_code == 401
    assert client.post("/api/erstanmeldung/code", json={"email": "falk@test.local", "code": code}).status_code == 200


def test_mitglied_darf_keine_verwaltung(client, admin):
    with __import__("fastapi.testclient", fromlist=["TestClient"]).TestClient(__import__("app.main", fromlist=["app"]).app) as c:
        from app import db
        with db.transaktion() as con:
            _, einmal = auth.benutzer_anlegen(con, "mitglied@test.local", "Mit Glied", "mitglied")
        r = c.post("/api/erstanmeldung/start", json={"email": "mitglied@test.local", "einmalPasswort": einmal})
        code = r.json()["code"]
        r = c.post("/api/erstanmeldung/abschluss", json={"email": "mitglied@test.local", "einmalPasswort": einmal,
                                                         "code": code, "name": "Mit Glied", "passwort": PASSWORT, "passwort2": PASSWORT})
        assert r.status_code == 200, r.text
        assert c.get("/api/benutzer").status_code == 403


def test_sperre_nach_fehlversuchen(client, admin):
    from app import config
    with __import__("fastapi.testclient", fromlist=["TestClient"]).TestClient(__import__("app.main", fromlist=["app"]).app) as c:
        from app import db
        with db.transaktion() as con:
            auth.benutzer_anlegen(con, "sperre@test.local", "Sperre", "mitglied")
            con.execute("UPDATE users SET status='aktiv', passwort_hash=? WHERE email='sperre@test.local'", (auth.hash_passwort(PASSWORT),))
        for _ in range(config.FEHLVERSUCHE_MAX):
            r = c.post("/api/anmelden", json={"email": "sperre@test.local", "passwort": "Falsch-falsch-falsch-1!"})
            assert r.status_code == 401
        r = c.post("/api/anmelden", json={"email": "sperre@test.local", "passwort": PASSWORT})
        assert r.status_code == 423


def test_neues_einmal_passwort_hebt_sperre_auf(client, admin):
    from app import config, db
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as c:
        with db.transaktion() as con:
            u, einmal = auth.benutzer_anlegen(con, "sperre2@test.local", "Sperre Zwei", "mitglied")
        for _ in range(config.FEHLVERSUCHE_MAX):
            c.post("/api/erstanmeldung/start", json={"email": "sperre2@test.local", "einmalPasswort": "xxxx-xxxx-xxxx"})
        r = c.post("/api/erstanmeldung/start", json={"email": "sperre2@test.local", "einmalPasswort": einmal})
        assert r.status_code == 423
        with db.transaktion() as con:
            neu = auth.einmal_passwort_erneuern(con, u["id"])
        r = c.post("/api/erstanmeldung/start", json={"email": "sperre2@test.local", "einmalPasswort": neu})
        assert r.status_code == 200, r.text
