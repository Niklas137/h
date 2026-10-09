"""Übersetzungsgüte: Abdeckung je Sprache mindestens 98,9 %, Glossar einheitlich, Platzhalter gleich."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "werkzeuge"))

import uebersetzung_pruefen as up  # noqa: E402


def test_uebersetzungen_vollstaendig():
    b = up.bericht()
    for sp in ("en", "uk", "ru"):
        g = b["gesamt"][sp]
        maengel = [m for e in b["quellen"].values() for m in e[sp]["maengel"]]
        assert g["prozent"] >= 98.9, (sp, g, maengel[:10])
        assert not b["glossar"][sp], (sp, b["glossar"][sp])
