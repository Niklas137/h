"""Kommandozeile: Dokumente prüfen und die Berichte als PDF ablegen, ohne Browser und ohne Konto.

Beispiele:
    python -m app.cli pruefen ../inbox/Anleitung.docx --sprachen de,en --ausgabe ../output
    python -m app.cli pruefen ../inbox/*.docx --regelsaetze basis,din
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from . import config
from .pruefer import berichte, lesen, pruefung, regeln, texte


def _eine_datei(pfad: Path, sprachen: list[str], regelsaetze: list[str], args: argparse.Namespace) -> tuple[int, dict | None]:
    """Prüft eine Datei und legt die PDFs ab. Rückgabe: Exit-Code und Zusammenfassung (oder None)."""
    if not pfad.is_file():
        print(f"Datei nicht gefunden: {pfad}", file=sys.stderr)
        return 2, None
    try:
        struktur, lesehinweise = lesen.lesen_mit_hinweisen(pfad.name, pfad.read_bytes())
    except lesen.LeseFehler as e:
        print(f"{pfad.name}: Einlesen fehlgeschlagen: {e}", file=sys.stderr)
        return 3, None
    if not any(z.get("text", "").strip() for z in struktur):
        print(f"{pfad.name}: Kein Text gefunden. Bei PDF vermutlich ein Scan ohne Textebene.", file=sys.stderr)
        return 3, None

    ergebnis = pruefung.pruefen(struktur, regelsaetze, [x.strip() for x in args.ohne.split(",") if x.strip()])
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
            ziel = berichte.freier_dateiname(ausgabe, art, pfad.name, sp, erstellt, pdf)
            if not ziel.exists():
                ziel.write_bytes(pdf)
            dateien.append(str(ziel))

    zusammenfassung = {
        "datei": pfad.name,
        "score": ergebnis["score"],
        "ampel": ergebnis["ampel"],
        "funde": len(ergebnis["funde"]),
        "klassen": ergebnis.get("klassen", {}),
        "stunden": ergebnis["stunden"],
        "regelsaetze": regelsaetze,
        "ausgelassen": [a["id"] for a in ergebnis.get("ausgelassen", [])],
        "sprachen": sprachen,
        "fazit": ergebnis["fazit"],
        "lesehinweise": lesehinweise,
        "pruefstatus": ergebnis["pruefstatus"],
        "freigabe": ergebnis["freigabe"],
        "pdfs": dateien,
    }
    if not args.json:
        print(f"{pfad.name}: {ergebnis['score']} %, {ergebnis['ampel']}, {len(ergebnis['funde'])} Funde, {ergebnis['stunden']} h")
        for k, n in zusammenfassung["klassen"].items():
            print(f"  {k}: {n}")
        print(f"Fazit: {ergebnis['fazit']}")
        for h in lesehinweise:
            print(f"Lesehinweis: {texte.lesehinweis('de', h)}")
        for d in dateien:
            print(f"PDF: {d}")
    return 0, zusammenfassung


def _pruefen(args: argparse.Namespace) -> int:
    """Eine oder mehrere Dateien. Exit-Code ist der schlechteste je Datei; 4 bei defekten Regeldateien."""
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
        pruefung.pruefen([], regelsaetze, [x.strip() for x in args.ohne.split(",") if x.strip()])
    except pruefung.AuswahlFehler as e:
        print(f"--ohne: {e}", file=sys.stderr)
        return 2
    except regeln.RegelFehler as e:
        print(str(e), file=sys.stderr)
        return 4
    pfade = [Path(d) for d in args.datei]
    schlechtester = 0
    ergebnisse: list[dict] = []
    for i, pfad in enumerate(pfade):
        if i and not args.json:
            print()
        try:
            rc, zusammenfassung = _eine_datei(pfad, sprachen, regelsaetze, args)
        except regeln.RegelFehler as e:
            print(str(e), file=sys.stderr)
            return 4
        schlechtester = max(schlechtester, rc)
        if zusammenfassung:
            ergebnisse.append(zusammenfassung)
    if args.json:
        print(json.dumps(ergebnisse[0] if len(pfade) == 1 and ergebnisse else ergebnisse, ensure_ascii=False, indent=2))
    elif len(pfade) > 1:
        uebrig = len(pfade) - len(ergebnisse)
        print(f"\n{len(ergebnisse)} von {len(pfade)} Dokumenten geprüft" + (f", {uebrig} nicht lesbar." if uebrig else "."))
    return schlechtester


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.cli", description="Dokumentenprüfer ohne Browser")
    sub = parser.add_subparsers(dest="befehl", required=True)
    p = sub.add_parser("pruefen", help="Dokument prüfen und PDFs erzeugen")
    p.add_argument("datei", nargs="+", help="Word (.docx) oder PDF, auch mehrere")
    p.add_argument("--sprachen", default="de", help="Basissprache[,Zusatzsprache], z. B. de,en")
    p.add_argument("--regelsaetze", default="basis,din,ce")
    p.add_argument("--ohne", default="", help="Prüfpunkte auslassen, z. B. CHK-008,DIN-008")
    p.add_argument("--ausgabe", default=str(config.OUTPUT), help="Zielordner für die PDFs")
    p.add_argument("--pruefer", default=config.BERICHT_KOPF, help="Name im Feld „Geprüft von“")
    p.add_argument("--json", action="store_true", help="Zusammenfassung als JSON")
    p.set_defaults(func=_pruefen)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
