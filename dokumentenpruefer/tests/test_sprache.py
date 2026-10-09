"""Sprache der API-Antworten: Kopf X-Sprache steuert Meldungen und Anzeigetexte, ohne Kopf bleibt Deutsch."""
import io

from docx import Document


def _docx(absaetze):
    doc = Document()
    for a in absaetze:
        doc.add_paragraph(a)
    puffer = io.BytesIO()
    doc.save(puffer)
    return puffer.getvalue()


def test_meldungen_in_oberflaechensprache(client, admin):
    r = client.post("/api/anmelden", json={"email": "niemand@test.local", "passwort": "x"}, headers={"X-Sprache": "en"})
    assert r.status_code == 401 and r.json()["fehler"] == "E-mail address or password is incorrect."
    r = client.post("/api/anmelden", json={"email": "niemand@test.local", "passwort": "x"}, headers={"X-Sprache": "uk"})
    assert r.json()["fehler"] == "Неправильна адреса електронної пошти або пароль."
    r = client.post("/api/anmelden", json={"email": "niemand@test.local", "passwort": "x"})
    assert r.json()["fehler"] == "E-Mail-Adresse oder Passwort stimmt nicht."
    r = client.post("/api/anmelden", json={"email": "niemand@test.local", "passwort": "x"}, headers={"X-Sprache": "xx"})
    assert r.json()["fehler"] == "E-Mail-Adresse oder Passwort stimmt nicht."
    # HTTPException mit Schlüssel (404) ebenfalls übersetzt
    r = client.get("/api/pruefung/gibtesnicht", headers={"X-Sprache": "ru"})
    assert r.status_code == 404 and r.json()["fehler"] == "Проверка не найдена."
    r = client.post("/api/pruefung", files={"datei": ("x.txt", b"hallo", "text/plain")}, headers={"X-Sprache": "en"})
    assert r.status_code == 400 and r.json()["fehler"] == "x.txt: Only Word (.docx) and PDF (.pdf) are checked."
    r = client.post("/api/pruefung", files={"datei": ("kaputt.docx", b"kein zip", "application/octet-stream")}, headers={"X-Sprache": "en"})
    assert r.status_code == 422 and r.json()["fehler"].startswith("The Word file cannot be opened.")


def test_ergebnis_anzeigetexte_in_oberflaechensprache(client, admin):
    datei = {"datei": ("Sprache.docx", _docx(["Diese Anleitung richtet sich an die Zielgruppe der Benutzer."]), "application/octet-stream")}
    r = client.post("/api/pruefung", files=datei, data={"regelsaetze": "basis,ce", "ausgelassen": "CHK-008"}, headers={"X-Sprache": "uk"})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["fazit"].startswith("У поточному вигляді")
    assert d["ausgelassen"][0]["bereich"] == "Гарантія"
    ce = [f for f in d["funde"] if f["ID"] == "CE-001"][0]
    assert ce["bereichAnzeige"] == "Маркування CE" and ce["Bereich"] == "CE-Kennzeichnung"
    assert ce["empfehlungAnzeige"].startswith("Маркування CE має") and ce["klasseAnzeige"] == "Критичний"
    assert ce["bewertungAnzeige"] == "Недостатньо підтверджено"
    r = client.get(f"/api/pruefung/{d['id']}", headers={"X-Sprache": "en"})
    e = r.json()
    assert e["fazit"].startswith("In its current form") and e["ausgelassen"][0]["bereich"] == "Warranty"
    r = client.get(f"/api/pruefung/{d['id']}")
    assert r.json()["fazit"].startswith("Das Dokument ist in der vorliegenden Form")
    r = client.get("/api/regeln", headers={"X-Sprache": "ru"})
    basis = r.json()["regelsaetze"]["basis"]
    assert basis["nameAnzeige"] == "Базовая проверка"
    txt = [p for p in basis["punkte"] if p["id"] == "TXT-001"][0]
    assert txt["bereichAnzeige"] == "Читаемость" and txt["empfehlungAnzeige"] == "Избегайте предложений длиннее 25 слов" and txt["klasseAnzeige"] == "Средний"
