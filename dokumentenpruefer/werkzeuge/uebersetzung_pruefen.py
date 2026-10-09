"""Übersetzungen messen: Abdeckung, Platzhalter, deutsche und lateinische Reste, Glossar.

    ./.venv/bin/python werkzeuge/uebersetzung_pruefen.py          # Bericht je Sprache
    ./.venv/bin/python werkzeuge/uebersetzung_pruefen.py --json   # maschinenlesbar

Quellen: app/pruefer/texte.py (PDF), app/meldungen.py (API), app/static/i18n.js (Oberfläche),
regeln/*.json (Bereiche und Empfehlungen). Deutsch ist die Quelle, verglichen werden en, uk, ru.
Die Abdeckung zählt je Text: vorhanden, Platzhalter gleich, keine deutschen Reste, bei uk/ru keine
lateinischen Wörter außer erlaubten Eigennamen. Das Ergebnis ist ein Prozentwert je Sprache.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

BASIS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASIS))

from app import meldungen  # noqa: E402
from app.pruefer import texte  # noqa: E402

SPRACHEN = ("en", "uk", "ru")
# Eigennamen und Fachkürzel, die in jeder Sprache lateinisch bleiben.
ERLAUBT = {
    "DIN", "CE", "EU", "PDF", "ZIP", "FSH", "FSH-Documentation", "IBM", "Plex", "Sans", "SIL", "Open", "Font", "License",
    "FastAPI", "Uvicorn", "SQLite", "python-docx", "PyPDF2", "pdfplumber", "reportlab", "argon2-cffi", "requirements.txt",
    "Word", "Apple", "Mail", "docx", "pdf", "output", "daten/codes.log", "admin", "mitglied", "basis", "din", "ce",
    "de", "en", "uk", "ru", "ID", "CHK", "TXT", "Mac", "KB", "MB", "A4", "DE", "EN", "UK", "RU", "Fast", "Simple", "High", "Quality",
    "x", "v", "h", "n", "m", "s", "p", "a", "b", "i", "g", "y", "r", "d", "ids", "min", "satz", "liste", "name", "email",
    "tage", "datei", "langs", "lang", "gesamt", "pdfs", "ordner", "code", "status", "von", "aktiv", "weg", "grund", "telefon",
    "zeiten", "pruefungen", "datum", "score", "ampel", "firma", "seiten",
}
# Deutsche Wörter, die in einer Übersetzung nichts verloren haben (Wortgrenzen, ohne Groß/Klein).
DEUTSCH = re.compile(r"\b(und|oder|nicht|der|die|das|den|dem|ein|eine|mit|für|von|zu|bei|wird|werden|ist|sind|Prüfung|Bericht|Dokument"
                     r"|Datei|Dateien|Sprache|Regelsatz|Regelsätze|Konto|Fehler|bitte|Bitte|Seite|Seiten|geprüft|Empfehlung|Bereich)\b")
LATEIN = re.compile(r"[A-Za-z][A-Za-z0-9./-]*")
PLATZHALTER = re.compile(r"\{[a-z]+\}")
# Texte, die in jeder Sprache gleich bleiben dürfen (Kürzel, Eigennamen, internationale Wörter).
IDENTISCH_OK = {"Score", "Min.", "Format", "Code", "Name", "Team", "Admin", "Info", "Normal", "Status", "Version", "PDF {lang}", "{n} PDFs",
                "ID", "DIN 82079-1", "h", "%", "DIN", "CE", "PDF", "ZIP", "FSH-Documentation", "Deutsch", "English", "Українська", "Русский"}
LOCALE = re.compile(r"^[a-z]{2}-[A-Z]{2}$")


def i18n_laden() -> dict[str, dict[str, str]]:
    """Liest i18n.js über node; ohne node wird die Oberfläche übersprungen."""
    pfad = BASIS / "app" / "static" / "i18n.js"
    skript = "global.window={};require(%s);process.stdout.write(JSON.stringify(window.UI_TEXTE));" % json.dumps(str(pfad))
    try:
        out = subprocess.run(["node", "-e", skript], capture_output=True, text=True, check=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    return json.loads(out)


def regeln_laden() -> dict[str, dict[str, str]]:
    """Regeltexte als Tabellen je Sprache: Schlüssel 'ID.bereich' und 'ID.empfehlung'."""
    tabellen: dict[str, dict[str, str]] = {"de": {}, "en": {}, "uk": {}, "ru": {}}
    for datei in ("pruefkatalog.json", "normlogik_82079.json", "ce_logik.json"):
        for r in json.loads((BASIS / "regeln" / datei).read_text(encoding="utf-8")):
            for feld in ("bereich", "empfehlung"):
                tabellen["de"][f"{r['id']}.{feld}"] = r[feld]
                for sp in SPRACHEN:
                    if r.get(f"{feld}_{sp}"):
                        tabellen[sp][f"{r['id']}.{feld}"] = r[f"{feld}_{sp}"]
    return tabellen


def pruefen(quelle: str, tabellen: dict[str, dict[str, str]]) -> dict[str, dict]:
    de = tabellen.get("de", {})
    ergebnis: dict[str, dict] = {}
    for sp in SPRACHEN:
        fremd = tabellen.get(sp, {})
        maengel: list[str] = []
        for key, original in de.items():
            text = fremd.get(key)
            if not isinstance(text, str) or not text.strip():
                maengel.append(f"{key}: fehlt")
                continue
            if sorted(PLATZHALTER.findall(text)) != sorted(PLATZHALTER.findall(original)):
                maengel.append(f"{key}: Platzhalter {PLATZHALTER.findall(original)} ≠ {PLATZHALTER.findall(text)}")
                continue
            ohne_platzhalter = PLATZHALTER.sub("", text)
            if text == original and original not in IDENTISCH_OK and not LOCALE.match(original) and not re.fullmatch(r"[A-Z0-9 ./-]+|[0-9.,]+", original):
                # Gleich wie Deutsch ist nur bei Eigennamen und Kürzeln in Ordnung.
                maengel.append(f"{key}: unverändert deutsch ({original[:40]})")
                continue
            if DEUTSCH.search(ohne_platzhalter):
                maengel.append(f"{key}: deutsches Wort in '{text[:60]}'")
                continue
            if sp in ("uk", "ru") and not LOCALE.match(text):
                woerter = [w.rstrip(".,;:") for w in LATEIN.findall(ohne_platzhalter)]
                fremdwoerter = [w for w in woerter if w and w not in ERLAUBT and not w.startswith(("CHK", "DIN", "CE-", "TXT"))]
                if fremdwoerter:
                    maengel.append(f"{key}: lateinische Wörter {fremdwoerter[:4]}")
                    continue
        gesamt = len(de)
        ergebnis[sp] = {"quelle": quelle, "gesamt": gesamt, "maengel": maengel, "prozent": round(100 * (gesamt - len(maengel)) / gesamt, 2) if gesamt else 100.0}
    return ergebnis


# Glossar: Kernbegriffe müssen in PDF-Texten und Oberfläche gleich übersetzt sein.
GLOSSAR = {
    "en": {"Prüfbericht": "Test report", "Fachbericht": "Technical report"},
    "uk": {"Prüfbericht": "Протокол перевірки", "Fachbericht": "Фаховий звіт"},
    "ru": {"Prüfbericht": "Протокол проверки", "Fachbericht": "Экспертный отчёт"},
}


def glossar_pruefen(ui: dict, pdf: dict) -> dict[str, list[str]]:
    fehler: dict[str, list[str]] = {}
    for sp, begriffe in GLOSSAR.items():
        liste = []
        for deutsch, fremd in begriffe.items():
            schluessel = {"Prüfbericht": ("titel_pruef", "pruefbericht"), "Fachbericht": ("titel_fach", "fachbericht")}[deutsch]
            if pdf.get(sp, {}).get(schluessel[0]) != fremd:
                liste.append(f"PDF {schluessel[0]}: {pdf.get(sp, {}).get(schluessel[0])!r} ≠ {fremd!r}")
            if ui and ui.get(sp, {}).get(schluessel[1]) != fremd:
                liste.append(f"Oberfläche {schluessel[1]}: {ui.get(sp, {}).get(schluessel[1])!r} ≠ {fremd!r}")
        fehler[sp] = liste
    return fehler


def bericht() -> dict:
    ui = i18n_laden()
    quellen = {"PDF (texte.py)": texte.TEXTE, "API (meldungen.py)": meldungen.TEXTE, "Regeln (regeln/*.json)": regeln_laden()}
    if ui:
        quellen["Oberfläche (i18n.js)"] = ui
    einzel = {name: pruefen(name, tab) for name, tab in quellen.items()}
    gesamt: dict[str, dict] = {}
    for sp in SPRACHEN:
        n = sum(e[sp]["gesamt"] for e in einzel.values())
        m = sum(len(e[sp]["maengel"]) for e in einzel.values())
        gesamt[sp] = {"texte": n, "maengel": m, "prozent": round(100 * (n - m) / n, 2) if n else 100.0}
    return {"quellen": einzel, "gesamt": gesamt, "glossar": glossar_pruefen(ui, texte.TEXTE), "oberflaeche_geprueft": bool(ui)}


def main(argv: list[str]) -> int:
    b = bericht()
    if "--json" in argv:
        print(json.dumps(b, ensure_ascii=False, indent=2))
    else:
        for name, e in b["quellen"].items():
            print(f"== {name}")
            for sp in SPRACHEN:
                print(f"  {sp}: {e[sp]['prozent']:6.2f} % ({e[sp]['gesamt'] - len(e[sp]['maengel'])} von {e[sp]['gesamt']})")
                for m in e[sp]["maengel"]:
                    print(f"      - {m}")
        print("== Gesamt")
        for sp in SPRACHEN:
            g = b["gesamt"][sp]
            print(f"  {sp}: {g['prozent']:6.2f} % ({g['texte'] - g['maengel']} von {g['texte']} Texten)")
        for sp, liste in b["glossar"].items():
            for z in liste:
                print(f"  Glossar {sp}: {z}")
        if not b["oberflaeche_geprueft"]:
            print("  Hinweis: node fehlt, Oberfläche (i18n.js) nicht geprüft.")
    schlecht = [sp for sp in SPRACHEN if b["gesamt"][sp]["prozent"] < 98.9] + [sp for sp, l in b["glossar"].items() if l]
    return 1 if schlecht else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
