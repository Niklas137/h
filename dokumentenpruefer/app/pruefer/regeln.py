"""Regelsätze vollständig laden und validieren, sonst keine Prüfung zulassen."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .. import config

DATEIEN = {
    "basis": "pruefkatalog.json",
    "din": "normlogik_82079.json",
    "ce": "ce_logik.json",
}


class RegelFehler(ValueError):
    """Ein gewählter Regelsatz ist nicht verlässlich ausführbar."""


def laden(schluessel: str, ordner: Path | None = None) -> list[dict[str, Any]]:
    if schluessel not in DATEIEN:
        raise RegelFehler(f"Unbekannter Regelsatz: {schluessel}.")
    datei = DATEIEN[schluessel]

    def fehler(grund: str) -> RegelFehler:
        return RegelFehler(f"Regelsatz {datei}: {grund}. Prüfung abgebrochen. Bitte die Regeldatei korrigieren.")

    # Drei kleine Dateien: je Aufruf frisch lesen, kein veralteter mtime-Cache.
    try:
        regeln = json.loads(((ordner or config.REGELN) / datei).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as e:
        raise fehler("Datei fehlt, ist nicht lesbar oder enthält ungültiges JSON") from e
    if not isinstance(regeln, list) or not regeln:
        raise fehler("eine nicht leere Regelliste ist erforderlich")
    ids: set[str] = set()
    for nr, regel in enumerate(regeln, 1):
        if not isinstance(regel, dict):
            raise fehler(f"Regel {nr} ist kein Objekt")
        for feld in ("id", "bereich", "empfehlung"):
            if not isinstance(regel.get(feld), str) or not regel[feld].strip():
                raise fehler(f"Regel {nr}, Feld {feld} fehlt oder ist leer")
        if regel["id"] in ids:
            raise fehler(f"Regel-ID {regel['id']} ist mehrfach vorhanden")
        ids.add(regel["id"])
        keywords = regel.get("keywords")
        if not isinstance(keywords, list) or not keywords or any(not isinstance(k, str) or not k.strip() for k in keywords):
            raise fehler(f"Regel {nr} braucht eine nicht leere Liste von Suchwörtern")
        if regel.get("fehlerklasse") not in ("Kritisch", "Schwer", "Mittel", "Gering"):
            raise fehler(f"Regel {nr} hat eine ungültige Fehlerklasse")
        gewicht = regel.get("gewichtung")
        if type(gewicht) not in (int, float) or not 0 < gewicht <= 100:
            raise fehler(f"Regel {nr} braucht eine Gewichtung größer als 0 und höchstens 100")
        if schluessel == "din" and type(regel.get("pflicht")) is not bool:
            raise fehler(f"Regel {nr}, Feld pflicht muss true oder false sein")
        for feld, wert in regel.items():
            if feld.startswith(("empfehlung_", "bereich_")) and (not isinstance(wert, str) or not wert.strip()):
                raise fehler(f"Regel {nr}, Übersetzung {feld} ist leer oder ungültig")
    return regeln


def vorhanden(ordner: Path | None = None) -> dict[str, bool]:
    """True nur für lesbare und vollständig validierte Regelsätze."""
    ergebnis = {}
    for k in DATEIEN:
        try:
            laden(k, ordner)
            ergebnis[k] = True
        except RegelFehler:
            ergebnis[k] = False
    return ergebnis
