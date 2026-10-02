"""Prüfbare Qualitätsvorgaben aus QUALITAET.md (ISO 25010). Nummern wie dort: L1, K1, B2, S2, W1, X1, P1 ..."""
import ast
import io
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest
from docx import Document
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from app import config
from app.main import app
from app.pruefer import texte

BASIS = Path(__file__).resolve().parent.parent
APP = BASIS / "app"
STATIC = APP / "static"


def _docx(absaetze):
    d = Document()
    for a in absaetze:
        d.add_paragraph(a)
    b = io.BytesIO(); d.save(b)
    return b.getvalue()


# ---------------------------------------------------------------- F Funktionale Eignung


def test_f4_scan_ohne_text_wird_abgewiesen(client, admin):
    b = io.BytesIO(); c = canvas.Canvas(b); c.rect(72, 72, 100, 100); c.showPage(); c.save()
    r = client.post("/api/pruefung", files={"datei": ("scan.pdf", b.getvalue())})
    assert r.status_code == 422
    assert "Scan" in r.json()["fehler"]


# ---------------------------------------------------------------- L Leistungseffizienz


def test_l1_api_antwortet_unter_200ms(client, admin):
    for url in ("/api/status", "/api/ich"):
        zeiten = []
        for _ in range(20):
            t = time.perf_counter(); assert client.get(url).status_code == 200; zeiten.append(time.perf_counter() - t)
        median = sorted(zeiten)[len(zeiten) // 2]
        assert median < 0.2, f"{url}: Median {median*1000:.0f} ms"


def test_l2_pruefung_200_absaetze_unter_10s(client, admin):
    inhalt = _docx([f"Absatz {i}: Installation, Wartung und Sicherheitshinweise für das Gerät." for i in range(200)])
    t = time.perf_counter()
    r = client.post("/api/pruefung", files={"datei": ("gross.docx", inhalt)}, data={"zusatzsprache": "en"})
    dauer = time.perf_counter() - t
    assert r.status_code == 200 and len(r.json()["pdfs"]) == 4
    assert dauer < 10, f"{dauer:.1f} s"


def test_l3_oberflaeche_klein_und_offline():
    groesse = sum((STATIC / n).stat().st_size for n in ("index.html", "app.js", "app.css"))
    assert groesse < 160 * 1024, f"{groesse / 1024:.0f} KB"
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    css = (STATIC / "app.css").read_text(encoding="utf-8")
    assert not re.search(r'<(script|link)[^>]+(src|href)="https?://', html), "externes Skript oder Stylesheet"
    assert "https://" not in css and "http://" not in css, "externe Schrift oder Ressource im CSS"


# ---------------------------------------------------------------- K Kompatibilität


def test_k1_fehler_immer_json(client, admin):
    faelle = [
        ("GET", "/api/gibt-es-nicht", None, None),
        ("GET", "/api/pruefung/unbekannt", None, None),
        ("POST", "/api/anmelden", None, "kein json"),
        ("PATCH", "/api/ich", {"name": "x"}, None),
        ("GET", "/api/pruefung/abc/pdf/pruef/xx", None, None),
    ]
    for methode, url, js, roh in faelle:
        r = client.request(methode, url, json=js, content=roh)
        assert r.status_code >= 400, (methode, url)
        assert r.headers["content-type"].startswith("application/json"), (methode, url, r.headers.get("content-type"))
        assert "fehler" in r.json() or "detail" in r.json(), (methode, url, r.text)
        assert "Traceback" not in r.text


@pytest.mark.parametrize("name,inhalt", [("bild.png", b"\x89PNG"), ("text.txt", b"hallo"), ("makro.docm", b"PK"), ("ohne-endung", b"x")])
def test_k3_fremde_dateien_400(client, admin, name, inhalt):
    r = client.post("/api/pruefung", files={"datei": (name, inhalt)})
    assert r.status_code == 400 and "Word" in r.json()["fehler"]


# ---------------------------------------------------------------- B Benutzerfreundlichkeit


def test_b2_felder_beschriftet():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    labels = set(re.findall(r'<label[^>]*\bfor="([^"]+)"', html))
    for m in re.finditer(r'<(input|select)\b([^>]*)>', html):
        attrs = m.group(2)
        if 'type="file"' in attrs or 'type="hidden"' in attrs:
            continue
        ident = re.search(r'\bid="([^"]+)"', attrs)
        assert ident, f"Feld ohne id: {attrs[:60]}"
        assert ident.group(1) in labels or "aria-label=" in attrs, f"Feld ohne label: {ident.group(1)}"
    # Symbolknöpfe (nur SVG, kein Text) brauchen aria-label oder title
    for m in re.finditer(r'<button\b([^>]*)>(.*?)</button>', html, re.S):
        attrs, inhalt = m.group(1), m.group(2)
        text = re.sub(r"<[^>]+>", "", inhalt).strip()
        if not text:
            assert "aria-label=" in attrs or "title=" in attrs, f"Symbolknopf ohne Beschriftung: {attrs[:80]}"


def test_b3_fehlermeldungen_sind_saetze(client, admin):
    antworten = [
        client.post("/api/anmelden", json={"email": "niemand@test.local", "passwort": "x"}),
        client.post("/api/benutzer", json={"email": "kaputt", "name": "Test Person"}),
        client.patch("/api/ich/einstellungen", json={"language": "klingonisch"}),
        client.post("/api/pruefung", files={"datei": ("x.txt", b"x")}),
        client.request("DELETE", "/api/benutzer/999999", json={"bestaetigung": "x"}),
    ]
    for r in antworten:
        text = r.json()["fehler"]
        assert len(text) >= 15 and text[0].isupper() and text.rstrip().endswith((".", "!")), text
        assert not re.search(r"\b(None|Traceback|Exception|KeyError|500)\b", text), text


# ---------------------------------------------------------------- Z Zuverlässigkeit


def test_z5_ungueltige_eingaben_kein_500(client, admin):
    faelle = [
        ("POST", "/api/anmelden", "[]"), ("POST", "/api/anmelden", "null"), ("POST", "/api/anmelden", "{\"email\": 5}"),
        ("POST", "/api/erstanmeldung/start", "{}"), ("POST", "/api/erstanmeldung/abschluss", "{\"passwort\": null}"),
        ("PATCH", "/api/ich", "{}"), ("PATCH", "/api/ich", "{\"name\": [1]}"), ("PATCH", "/api/ich/einstellungen", "[1,2]"),
        ("POST", "/api/ich/passwort", "{}"), ("POST", "/api/benutzer", "{\"rolle\": {}}"),
        ("PATCH", "/api/benutzer/1", "{\"status\": 7}"), ("DELETE", "/api/benutzer/1", "\"text\""),
        ("POST", "/api/pruefung", ""), ("DELETE", "/api/ich/sitzungen/%00", ""),
    ]
    for methode, url, body in faelle:
        r = client.request(methode, url, content=body, headers={"Content-Type": "application/json"})
        assert 400 <= r.status_code < 500, (methode, url, body, r.status_code, r.text[:120])


# ---------------------------------------------------------------- S Sicherheit


def test_s2_keine_geheimnisse_in_antworten(client, admin):
    verboten = ("passwort_hash", "einmal_hash", "code_hash", "token_hash", "sitzung_hash", "$argon2")
    antworten = [client.get("/api/ich"), client.get("/api/benutzer?geloeschte=1"), client.get("/api/ich/sitzungen"),
                 client.get("/api/protokoll"), client.get("/api/pruefungen"), client.get("/api/status")]
    for r in antworten:
        assert r.status_code == 200
        for wort in verboten:
            assert wort not in r.text, (r.request.url, wort)


def test_s3_cookie_httponly_samesite(admin):
    with TestClient(app) as c:
        r = c.post("/api/anmelden", json={"email": admin["email"], "passwort": admin["passwort"]})
        cookie = r.headers["set-cookie"].lower()
        assert "httponly" in cookie and "samesite=lax" in cookie and "path=/" in cookie
        assert c.cookies.get(config.COOKIE_NAME) and len(c.cookies.get(config.COOKIE_NAME)) >= 32
        from app import db
        with db.transaktion() as con:
            for row in con.execute("SELECT token_hash FROM sessions").fetchall():
                assert re.fullmatch(r"[0-9a-f]{64}", row["token_hash"]), "Token muss als SHA-256-Hash liegen"


def test_s8_upload_grenze(client, admin):
    zu_gross = b"PK" + b"\0" * (config.UPLOAD_MAX_BYTES + 1)
    r = client.post("/api/pruefung", files={"datei": ("gross.docx", zu_gross)})
    assert r.status_code == 413
    assert config.UPLOAD_MAX_BYTES == 25 * 1024 * 1024


# ---------------------------------------------------------------- W Wartbarkeit


def test_w1_pyflakes_und_keine_todos():
    r = subprocess.run([sys.executable, "-m", "pyflakes", "app", "tests"], cwd=BASIS, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    for pfad in list(APP.rglob("*.py")) + list((BASIS / "tests").glob("*.py")) + list(STATIC.glob("*.js")):
        if pfad.name == "test_qualitaet.py":
            continue
        assert not re.search(r"\b(TODO|FIXME)\b", pfad.read_text(encoding="utf-8")), pfad.name


def test_w2_dateien_und_funktionen_begrenzt():
    for pfad in APP.rglob("*.py"):
        quelle = pfad.read_text(encoding="utf-8")
        zeilen = quelle.count("\n") + 1
        assert zeilen <= 800, f"{pfad.relative_to(BASIS)}: {zeilen} Zeilen"
        for knoten in ast.walk(ast.parse(quelle)):
            if isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef)):
                laenge = knoten.end_lineno - knoten.lineno + 1
                assert laenge <= 120, f"{pfad.relative_to(BASIS)}::{knoten.name}: {laenge} Zeilen"


def test_w3_module_in_readme():
    readme = (BASIS / "README.md").read_text(encoding="utf-8")
    aufbau = readme[readme.index("## Aufbau"):]
    for pfad in APP.rglob("*.py"):
        if pfad.name == "__init__.py":
            continue
        assert str(pfad.relative_to(BASIS)) in aufbau, f"{pfad.relative_to(BASIS)} fehlt im Abschnitt Aufbau"


def test_w4_vorgaben_haben_tests():
    text = (BASIS / "QUALITAET.md").read_text(encoding="utf-8")
    tests = {p.name: p.read_text(encoding="utf-8") for p in (BASIS / "tests").glob("test_*.py")}
    zeilen = [z for z in text.splitlines() if z.startswith("| ") and "[T]" in z]
    assert len(zeilen) >= 30
    for zeile in zeilen:
        for datei, funktion in re.findall(r"`(test_[a-z0-9_]+\.py)(?:::([a-z0-9_]+))?`", zeile):
            assert datei in tests, f"{datei} fehlt ({zeile[:40]})"
            if funktion:
                assert f"def {funktion}(" in tests[datei], f"{datei}::{funktion} fehlt ({zeile[:40]})"


def test_w5_nur_erklaerte_abhaengigkeiten():
    erklaert = {re.split(r"[<>=\[]", z.strip())[0].lower() for z in (BASIS / "requirements.txt").read_text().splitlines() if z.strip()}
    paket_fuer_modul = {"docx": "python-docx", "pypdf2": "pypdf2", "argon2": "argon2-cffi", "starlette": "fastapi", "multipart": "python-multipart"}
    stdlib = set(sys.stdlib_module_names)
    for pfad in APP.rglob("*.py"):
        for knoten in ast.walk(ast.parse(pfad.read_text(encoding="utf-8"))):
            namen = [a.name for a in knoten.names] if isinstance(knoten, ast.Import) else ([knoten.module] if isinstance(knoten, ast.ImportFrom) and knoten.level == 0 and knoten.module else [])
            for name in namen:
                kopf = name.split(".")[0].lower()
                if kopf in stdlib or kopf == "app":
                    continue
                paket = paket_fuer_modul.get(kopf, kopf)
                assert paket in erklaert, f"{pfad.name} importiert {name}, nicht in requirements.txt"
    assert not (BASIS / "package.json").exists(), "Oberfläche braucht keinen Build-Schritt"


# ---------------------------------------------------------------- X Flexibilität


def test_x1_keine_absoluten_pfade_oder_zugangsdaten():
    for pfad in APP.rglob("*.py"):
        quelle = pfad.read_text(encoding="utf-8")
        for m in re.finditer(r'["\'](/Users/|/home/|/Volumes/|[A-Z]:\\\\)', quelle):
            pytest.fail(f"{pfad.name}: absoluter Pfad {m.group(0)}")
        assert not re.search(r"(passwor[dt]|secret|token)\s*=\s*['\"][^'\"]{6,}['\"]", quelle, re.I), f"{pfad.name}: Zugangsdatum im Code"
    quelle = (APP / "config.py").read_text(encoding="utf-8")
    for var in re.findall(r'os\.environ\.get\("([A-Z_]+)"', quelle):
        assert var.startswith("DP_"), var


def test_x3_texte_in_allen_sprachen():
    de = set(texte.TEXTE["de"])
    for sprache in config.SPRACHEN:
        fehlend = de - set(texte.TEXTE[sprache])
        assert not fehlend, f"{sprache}: {sorted(fehlend)[:5]}"
        assert all(texte.TEXTE[sprache][k].strip() for k in de), sprache


# ---------------------------------------------------------------- P Betriebssicherheit


def test_p1_kein_mailversand_ausser_code():
    treffer = []
    for pfad in APP.rglob("*.py"):
        for i, zeile in enumerate(pfad.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"\.(send_message|sendmail)\(", zeile):
                treffer.append((pfad.name, i))
    assert treffer == [("mail.py", treffer[0][1])] if treffer else False, treffer
    main = (APP / "main.py").read_text(encoding="utf-8")
    assert "smtplib" not in main.replace("mail.smtplib.SMTPException", "")
    # AppleScript legt nur einen sichtbaren Entwurf an, kein "send"
    skript = main[main.index("def _applescript_entwurf"):]
    assert "send" not in skript.split("return")[0].replace("visible", "")


def test_p2_original_bleibt_unveraendert(client, admin, tmp_path):
    datei = tmp_path / "Original.docx"
    inhalt = _docx(["Installation und Wartung."])
    datei.write_bytes(inhalt)
    vorher = datei.stat().st_mtime_ns
    with datei.open("rb") as f:
        r = client.post("/api/pruefung", files={"datei": ("Original.docx", f.read())})
    assert r.status_code == 200
    assert datei.read_bytes() == inhalt and datei.stat().st_mtime_ns == vorher
    # Hochgeladene Datei liegt nirgends ab: im Prüfordner nur PDFs
    for p in config.PRUEFUNGEN.rglob("*"):
        assert p.is_dir() or p.suffix == ".pdf", p
