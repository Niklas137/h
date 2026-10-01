"""Geprüfte ZIP-Sicherungen; Wiederherstellung ausschließlich in einen neuen Ordner.

    python -m app.sicherung sichern --ziel /Pfad/Sicherung.zip
    python -m app.sicherung pruefen /Pfad/Sicherung.zip
    python -m app.sicherung wiederherstellen /Pfad/Sicherung.zip --ziel /Pfad/Neu
"""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
import os
import re
import shlex
import shutil
import sqlite3
import stat
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from . import config, db
from .pruefer import berichte, regeln


class SicherungsFehler(ValueError):
    pass


def _sha(daten: bytes) -> str:
    return hashlib.sha256(daten).hexdigest()


def _id(wert: str) -> str:
    if not re.fullmatch(r"[a-f0-9]{12}", wert):
        raise SicherungsFehler("Ungültige Prüfungs-ID in der Sicherung.")
    return wert


def sichern(ziel: Path) -> dict:
    ziel = ziel.expanduser().resolve()
    if ziel.exists():
        raise SicherungsFehler("Die Zieldatei existiert bereits. Bitte einen neuen Namen wählen.")
    if not config.DB_PFAD.is_file():
        raise SicherungsFehler("Keine Datenbank vorhanden.")
    ziel.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"format": 1, "erstellt": db.jetzt(), "dateien": {}}
    fd, name = tempfile.mkstemp(prefix=".dp-sicherung-", suffix=".tmp", dir=ziel.parent)
    os.close(fd)
    temp = Path(name)
    try:
        with tempfile.TemporaryDirectory(prefix="dp-db-") as verzeichnis:
            kopie = Path(verzeichnis) / "db.sqlite3"
            # Online-Backup berücksichtigt WAL und laufende Transaktionen.
            with closing(sqlite3.connect(config.DB_PFAD.resolve().as_uri() + "?mode=ro", uri=True)) as quelle:
                with closing(sqlite3.connect(kopie)) as con, con:
                    quelle.backup(con)
                    if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        raise SicherungsFehler("Die Datenbank ist beschädigt.")
                    con.row_factory = sqlite3.Row
                    pruefungen = [dict(r) for r in con.execute("SELECT * FROM pruefungen")]
            with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as z:
                def hinzufuegen(pfad: Path, name: str):
                    if not pfad.is_file() or pfad.is_symlink():
                        raise SicherungsFehler(f"Datei fehlt oder ist kein regulärer Bericht: {name}")
                    daten = pfad.read_bytes()
                    z.writestr(name, daten)
                    manifest["dateien"][name] = {"bytes": len(daten), "sha256": _sha(daten)}
                hinzufuegen(kopie, "daten/dokumentenpruefer.sqlite3")
                for row in pruefungen:
                    pid = _id(row["id"])
                    ordner = Path(row["ordner"]).resolve()
                    if ordner != (config.PRUEFUNGEN / pid).resolve():
                        raise SicherungsFehler("Ein Berichtsordner liegt außerhalb der aktuellen Datenablage.")
                    for sprache in json.loads(row["sprachen"]):
                        if sprache not in config.SPRACHEN:
                            raise SicherungsFehler("Ungültige Berichtssprache in der Datenbank.")
                        for art in ("pruef", "fach"):
                            datei = berichte.dateiname(art, row["dateiname"], sprache, row["erstellt"])
                            hinzufuegen(ordner / datei, f"daten/pruefungen/{pid}/{datei}")
                geheimnis = config.DATEN / "geheimnis.txt"
                if geheimnis.exists():
                    hinzufuegen(geheimnis, "daten/geheimnis.txt")
                for datei in regeln.DATEIEN.values():
                    pfad = config.REGELN / datei
                    if pfad.exists():
                        hinzufuegen(pfad, "regeln/" + datei)
                if config.OUTPUT.is_dir():
                    for pfad in sorted(config.OUTPUT.glob("*.pdf")):
                        hinzufuegen(pfad, "output/" + pfad.name)
                z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        pruefen(temp)
        with temp.open("rb") as f:
            os.fsync(f.fileno())
        os.link(temp, ziel)  # Nie vorhandene Sicherungen überschreiben.
    finally:
        temp.unlink(missing_ok=True)
    return manifest


def pruefen(archiv: Path) -> dict:
    try:
        with zipfile.ZipFile(archiv) as z:
            infos = z.infolist()
            namen = [i.filename for i in infos]
            if len(namen) != len(set(namen)) or len(namen) > 100000:
                raise SicherungsFehler("Doppelte oder zu viele Archivdateien.")
            if sum(i.file_size for i in infos) > 10 * 1024**3:
                raise SicherungsFehler("Sicherung überschreitet die Grenze von 10 GB.")
            for i in infos:
                p = PurePosixPath(i.filename)
                if (p.is_absolute() or ".." in p.parts or "\\" in i.filename or
                        str(p) != i.filename or i.is_dir() or
                        stat.S_ISLNK(i.external_attr >> 16) or i.file_size > 512 * 1024**2):
                    raise SicherungsFehler("Ungültiger Pfad oder Dateityp im Archiv.")
            info = z.getinfo("manifest.json")
            if info.file_size > 10 * 1024**2:
                raise SicherungsFehler("Sicherungsverzeichnis ist zu groß.")
            manifest = json.loads(z.read("manifest.json"))
            if manifest.get("format") != 1 or not isinstance(manifest.get("dateien"), dict):
                raise SicherungsFehler("Unbekanntes Sicherungsformat.")
            if set(namen) != set(manifest["dateien"]) | {"manifest.json"}:
                raise SicherungsFehler("Dateiliste der Sicherung stimmt nicht überein.")
            if "daten/dokumentenpruefer.sqlite3" not in namen:
                raise SicherungsFehler("Datenbank fehlt in der Sicherung.")
            for name, soll in manifest["dateien"].items():
                if not name.startswith(("daten/", "regeln/", "output/")):
                    raise SicherungsFehler("Unbekannter Inhalt im Archiv.")
                daten = z.read(name)
                if len(daten) != soll["bytes"] or _sha(daten) != soll["sha256"]:
                    raise SicherungsFehler(f"Prüfsumme stimmt nicht: {name}")
            return manifest
    except (OSError, zipfile.BadZipFile, KeyError, TypeError, AttributeError, UnicodeError, json.JSONDecodeError) as e:
        raise SicherungsFehler("Sicherung ist unvollständig, beschädigt oder nicht lesbar.") from e


def wiederherstellen(archiv: Path, ziel: Path) -> Path:
    manifest = pruefen(archiv)
    ziel = ziel.expanduser().resolve()
    if ziel.exists():
        raise SicherungsFehler("Wiederherstellung braucht einen neuen, noch nicht vorhandenen Zielordner.")
    ziel.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".dp-wiederherstellung-", dir=ziel.parent))
    try:
        with zipfile.ZipFile(archiv) as z:
            for name in manifest["dateien"]:
                pfad = temp / name
                pfad.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                daten = z.read(name)
                if _sha(daten) != manifest["dateien"][name]["sha256"]:
                    raise SicherungsFehler("Sicherung wurde während der Wiederherstellung verändert.")
                with pfad.open("xb") as f:
                    f.write(daten)
                pfad.chmod(0o600)
        for name in ("daten/pruefungen", "output", "regeln"):
            (temp / name).mkdir(mode=0o700, parents=True, exist_ok=True)
        with closing(sqlite3.connect(temp / "daten/dokumentenpruefer.sqlite3")) as con, con:
            if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise SicherungsFehler("Die gesicherte Datenbank ist beschädigt.")
            con.execute("DELETE FROM sessions")
            con.execute("UPDATE users SET code_hash=NULL, code_ablauf=NULL, code_versuche=0")
            for (pid,) in con.execute("SELECT id FROM pruefungen").fetchall():
                con.execute("UPDATE pruefungen SET ordner=? WHERE id=?",
                            (str(ziel / "daten/pruefungen" / _id(pid)), pid))
        # Ziel reservieren, um auch bei zwei Wiederherstellungen nichts zu ersetzen.
        ziel.mkdir(mode=0o700, exist_ok=False)
        try:
            os.rename(temp, ziel)
        except BaseException:
            ziel.rmdir()
            raise
        return ziel
    finally:
        if temp.exists():
            shutil.rmtree(temp)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dokumentenprüfer sichern und wiederherstellen")
    sub = parser.add_subparsers(dest="befehl", required=True)
    s = sub.add_parser("sichern"); s.add_argument("--ziel", type=Path, required=True)
    p = sub.add_parser("pruefen"); p.add_argument("archiv", type=Path)
    w = sub.add_parser("wiederherstellen"); w.add_argument("archiv", type=Path)
    w.add_argument("--ziel", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.befehl == "sichern":
            m = sichern(args.ziel)
            print(f"Sicherung geprüft und erstellt: {args.ziel.resolve()} ({len(m['dateien'])} Dateien)")
        elif args.befehl == "pruefen":
            m = pruefen(args.archiv)
            print(f"Alle {len(m['dateien'])} Prüfsummen stimmen. Stand: {m['erstellt']}")
        else:
            ziel = wiederherstellen(args.archiv, args.ziel)
            print(f"Wiederhergestellt: {ziel}. Bitte neu anmelden.")
            print("Start aus dem Programmordner:")
            print(" ".join(f"DP_{key}={shlex.quote(str(ziel / ordner))}" for key, ordner in
                           (("DATEN", "daten"), ("REGELN", "regeln"), ("OUTPUT", "output"))) + " ./start.command")
        return 0
    except (SicherungsFehler, OSError, sqlite3.Error) as e:
        print(f"Sicherung abgebrochen: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
