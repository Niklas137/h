"""Testaufbau: eigene Datenablage im Temp-Ordner, Entwicklungsmodus (Code kommt in der API zurück)."""
import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="dp-test-"))
os.environ["DP_DATEN"] = str(_TMP / "daten")
os.environ["DP_OUTPUT"] = str(_TMP / "output")
os.environ["DP_DEV"] = "1"
os.environ["DP_VERIFIZIERUNG"] = "code"
os.environ["DP_SMTP_HOST"] = ""  # Tests versenden niemals E-Mails.

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import auth, db  # noqa: E402
from app.main import app  # noqa: E402

PASSWORT = "Sicheres-Passwort-2026!"


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def admin(client):
    """Admin-Konto über die Erstanmeldung komplett einrichten und angemeldet lassen."""
    with db.transaktion() as con:
        user, einmal = auth.benutzer_anlegen(con, "admin@test.local", "Test Admin", "admin")
    r = client.post("/api/erstanmeldung/start", json={"email": "admin@test.local", "einmalPasswort": einmal})
    assert r.status_code == 200, r.text
    code = r.json()["code"]
    r = client.post("/api/erstanmeldung/code", json={"email": "admin@test.local", "code": code})
    assert r.status_code == 200, r.text
    r = client.post(
        "/api/erstanmeldung/abschluss",
        json={
            "email": "admin@test.local",
            "einmalPasswort": einmal,
            "code": code,
            "name": "Test Admin",
            "passwort": PASSWORT,
            "passwort2": PASSWORT,
        },
    )
    assert r.status_code == 200, r.text
    return {"email": "admin@test.local", "passwort": PASSWORT, "einmal": einmal, "code": code, **r.json()}
