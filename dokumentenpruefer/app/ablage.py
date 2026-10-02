"""Vollständige Dateien atomar veröffentlichen, vorhandene Dateien nie ersetzen."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path


def schreiben_neu(ziel: Path, inhalt: bytes) -> None:
    """Auch parallele Prozesse sehen nur vollständige Dateien; Kollision => FileExistsError."""
    ziel.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".dp-", suffix=".tmp", dir=ziel.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(inhalt)
            f.flush()
            os.fsync(f.fileno())
        # Hardlink veröffentlicht den fertigen Inhalt in einem Schritt, ohne Überschreiben.
        os.link(temp, ziel)
    finally:
        temp.unlink(missing_ok=True)
