"""Regelsätze aus regeln/ laden: pruefkatalog.json, normlogik_82079.json, ce_logik.json."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .. import config

log = logging.getLogger("dokumentenpruefer.regeln")

DATEIEN = {
    "basis": "pruefkatalog.json",
    "din": "normlogik_82079.json",
    "ce": "ce_logik.json",
}

_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}


def laden(schluessel: str, ordner: Path | None = None) -> list[dict[str, Any]]:
    pfad = (ordner or config.REGELN) / DATEIEN[schluessel]
    if not pfad.exists():
        log.warning("Regeldatei fehlt: %s", pfad)
        return []
    mtime = pfad.stat().st_mtime
    eintrag = _cache.get(str(pfad))
    if eintrag and eintrag[0] == mtime:
        return eintrag[1]
    try:
        with pfad.open("r", encoding="utf-8") as f:
            regeln = json.load(f)
    except json.JSONDecodeError as e:
        log.error("Regeldatei fehlerhaft: %s (%s)", pfad, e)
        return []
    if not isinstance(regeln, list):
        return []
    _cache[str(pfad)] = (mtime, regeln)
    return regeln


def vorhanden(ordner: Path | None = None) -> dict[str, bool]:
    """Welche Regeldateien liegen vor. Fehlende Dateien meldet die Oberfläche."""
    return {k: ((ordner or config.REGELN) / v).exists() for k, v in DATEIEN.items()}
