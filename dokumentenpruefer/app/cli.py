"""Kommandozeile: ein Dokument prüfen und die Berichte als PDF ablegen, ohne Browser und ohne Konto.

Beispiel:
    python -m app.cli pruefen ../inbox/Anleitung.docx --sprachen de,en --ausgabe ../output
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from . import config
from .pruefer import berichte, lesen, pruefung, regeln, texte


def _pruefen(args: argparse.Namespace) -> int:
    pfad = Path(args.datei)
    if not pfad.is_file():
        print(f"Datei nicht gefunden: {pfad}", file=sys.stderr)
        return 2
    sprachen = [s.strip() for s in args.sprachen.split(",") if s.strip()]
    unbekannt = [s for s in sprachen if s not in config.SPRACHEN]
    if not sprachen or unbekannt or len(sprachen) > 2:
        print(f"--sprachen: Basissprache und höchstens eine Zusatzsprache aus {', '.join(config.SPRACHEN)}", file=sys.stderr)
        return 2
    regelsaetze = list(dict.fromkeys(r.strip() for r in args.regelsaetze.split(",") if r.strip()))
    if not regelsaetze or any(r not in config.REGELSAETZE for r in regelsaetze):
        print(f"--regelsaetze: mindestens einer aus {', '.join(config.REGELSAETZE)}", file=sys.stderr)
        return 2
    try:
        struktur, lesehinweise = lesen.lesen_mit_hinweisen(pfad.name, pfad.read_bytes())
    except lesen.LeseFehler as e:
        print(f"Einlesen fehlgeschlagen: {e}", file=sys.stderr)
        return 3
    if not any(z.get("text", "").strip() for z in struktur):
        print("Kein Text gefunden. Bei PDF vermutlich ein Scan ohne Textebene.", file=sys.stderr)
        return 3

    try:
        ergebnis = pruefung.pruefen(struktur, regelsaetze)
    except regeln.RegelFehler as e:
        print(str(e), file=sys.stderr)
        return 4
    ergebnis["pruefer"] = args.pruefer
    ergebnis["lesehinweise"] = lesehinweise
    erstellt = datetime.now().isoformat(timespec="seconds")
    meta = {"dateiname": pfad.name, "erstellt": erstellt, "pruefer": args.pruefer}
    ausgabe = Path(args.ausgabe)
    ausgabe.mkdir(parents=True, exist_ok=True)
    dateien: list[str] = []
    for art in ("pruef", "fach"):
        for sp in sprachen:
            pdf = berichte.erzeugen(art, ergebnis, meta, sp)
            ziel = berichte.ablegen(ausgabe, art, pfad.name, sp, erstellt, pdf)
            dateien.append(str(ziel))

    zusammenfassung = {
        "datei": pfad.name,
        "score": ergebnis["score"],
        "ampel": ergebnis["ampel"],
        "funde": len(ergebnis["funde"]),
        "klassen": ergebnis.get("klassen", {}),
        "stunden": ergebnis["stunden"],
        "regelsaetze": regelsaetze,
        "sprachen": sprachen,
        "fazit": ergebnis["fazit"],
        "lesehinweise": lesehinweise,
        "pruefstatus": ergebnis["pruefstatus"],
        "freigabe": ergebnis["freigabe"],
        "pdfs": dateien,
    }
    if args.json:
        print(json.dumps(zusammenfassung, ensure_ascii=False, indent=2))
    else:
        print(f"{pfad.name}: {ergebnis['score']} %, {ergebnis['ampel']}, {len(ergebnis['funde'])} Funde, {ergebnis['stunden']} h")
        for k, n in zusammenfassung["klassen"].items():
            print(f"  {k}: {n}")
        print(f"Fazit: {ergebnis['fazit']}")
        for h in lesehinweise:
            print(f"Lesehinweis: {texte.lesehinweis('de', h)}")
        for d in dateien:
            print(f"PDF: {d}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.cli", description="Dokumentenprüfer ohne Browser")
    sub = parser.add_subparsers(dest="befehl", required=True)
    p = sub.add_parser("pruefen", help="Dokument prüfen und PDFs erzeugen")
    p.add_argument("datei", help="Word (.docx) oder PDF")
    p.add_argument("--sprachen", default="de", help="Basissprache[,Zusatzsprache], z. B. de,en")
    p.add_argument("--regelsaetze", default="basis,din,ce")
    p.add_argument("--ausgabe", default=str(config.OUTPUT), help="Zielordner für die PDFs")
    p.add_argument("--pruefer", default=config.BERICHT_KOPF, help="Name im Feld „Geprüft von“")
    p.add_argument("--json", action="store_true", help="Zusammenfassung als JSON")
    p.set_defaults(func=_pruefen)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
