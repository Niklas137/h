"""Konfiguration des Dokumentenprüfers.

Alles, was je Installation anders ist, kommt aus Umgebungsvariablen (Präfix DP_).
Zugangsdaten stehen nie im Code und nie im Repo.
"""
from __future__ import annotations

import os
import secrets
from pathlib import Path

BASIS = Path(__file__).resolve().parent.parent  # Ordner dokumentenpruefer/
APP = BASIS / "app"
STATIC = APP / "static"
FONTS = STATIC / "fonts"
TEXTE = APP / "texte"
REGELN = Path(os.environ.get("DP_REGELN", BASIS / "regeln"))

DATEN = Path(os.environ.get("DP_DATEN", BASIS / "daten"))
DATEN.mkdir(parents=True, exist_ok=True)
DB_PFAD = DATEN / "dokumentenpruefer.sqlite3"
PRUEFUNGEN = DATEN / "pruefungen"
PRUEFUNGEN.mkdir(parents=True, exist_ok=True)
OUTPUT = Path(os.environ.get("DP_OUTPUT", BASIS / "output"))

SPRACHEN = ["de", "en", "uk", "ru"]
SPRACHNAMEN = {"de": "Deutsch", "en": "English", "uk": "Українська", "ru": "Русский"}
SPRACHNAMEN_DE = {"de": "Deutsch", "en": "Englisch", "uk": "Ukrainisch", "ru": "Russisch"}
REGELSAETZE = ["basis", "din", "ce"]

SITZUNG_TAGE = int(os.environ.get("DP_SITZUNG_TAGE", "14"))
EINMAL_PASSWORT_TAGE = int(os.environ.get("DP_EINMAL_TAGE", "7"))
CODE_MINUTEN = 10
FEHLVERSUCHE_MAX = 8
SPERRE_MINUTEN = 15
PASSWORT_MIN = 14

# "code": Verifizierung per Code an die E-Mail-Adresse (Empfehlung).
# "aus": das Einmal-Passwort allein gilt als Nachweis.
VERIFIZIERUNG = os.environ.get("DP_VERIFIZIERUNG", "code")

# Entwicklung: Codes und Einmal-Passwörter werden zusätzlich im Protokoll ausgegeben
# und von der API zurückgegeben. Niemals im Betrieb einschalten.
ENTWICKLUNG = os.environ.get("DP_DEV", "0") == "1"

SMTP_HOST = os.environ.get("DP_SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("DP_SMTP_PORT", "587"))
SMTP_USER = os.environ.get("DP_SMTP_USER", "")
SMTP_PASSWORT = os.environ.get("DP_SMTP_PASSWORT", "")
SMTP_ABSENDER = os.environ.get("DP_SMTP_ABSENDER", SMTP_USER)

BERICHT_KOPF = os.environ.get("DP_BERICHT_KOPF", "FSH-Documentation")
BERICHT_FUSS = os.environ.get("DP_BERICHT_FUSS", "Fast. Simple. High Quality.")
SUPPORT_ADRESSE = os.environ.get("DP_SUPPORT", "")
SUPPORT_TELEFON = os.environ.get("DP_TELEFON", "")
SUPPORT_ZEITEN = os.environ.get("DP_ZEITEN", "")

COOKIE_NAME = "dp_sitzung"
COOKIE_SECURE = os.environ.get("DP_COOKIE_SECURE", "0") == "1"

UPLOAD_MAX_BYTES = 25 * 1024 * 1024
# Höchstzahl Dateien je Prüfung (ein Lauf); jede Datei bekommt eigene Berichte.
MAX_DATEIEN = int(os.environ.get("DP_MAX_DATEIEN", "20"))


def geheimnis() -> str:
    """Zufälliges Geheimnis je Installation, liegt nur in daten/, nie im Repo."""
    pfad = DATEN / "geheimnis.txt"
    if pfad.exists():
        return pfad.read_text(encoding="utf-8").strip()
    wert = secrets.token_urlsafe(48)
    pfad.write_text(wert, encoding="utf-8")
    try:
        os.chmod(pfad, 0o600)
    except OSError:
        pass
    return wert
