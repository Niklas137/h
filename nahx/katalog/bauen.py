"""Baut den NAHX-Aufgabenkatalog: katalog.html (Artefakt-Seite) und KATALOG.md (Lesefassung) aus aufgaben.json.

Aufruf:  python3 nahx/katalog/bauen.py [--ausgabe ORDNER]
Die Seite speichert Status und Notizen im Artefakt-Speicher (db, Sammlung "status", Dokument je Aufgaben-id);
die Aufgaben selbst stehen in der Seite. Neue Aufgabe: Eintrag in aufgaben.json, neu bauen, neu veröffentlichen.
"""
import argparse, json, pathlib

HIER = pathlib.Path(__file__).resolve().parent
WER = {"niklas": "Niklas", "falk": "Falk · FSH Documentation", "beide": "Gemeinsam", "claude": "Claude"}

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ausgabe", default=str(HIER))
    ziel = pathlib.Path(ap.parse_args().ausgabe); ziel.mkdir(parents=True, exist_ok=True)
    auf = json.loads((HIER / "aufgaben.json").read_text(encoding="utf-8"))
    ids = [a["id"] for a in auf]; assert len(ids) == len(set(ids)), "doppelte id"
    vorlage = (HIER / "vorlage.html").read_text(encoding="utf-8")
    assert "/*AUFGABEN*/[]" in vorlage
    js = json.dumps(auf, ensure_ascii=False).replace("</", "<\\/")
    (ziel / "katalog.html").write_text(vorlage.replace("/*AUFGABEN*/[]", js), encoding="utf-8")
    md = ["# NAHX Aufgabenkatalog bis zum Livegang", "",
          "Lesefassung von `aufgaben.json`. Den aktuellen Status (offen, läuft, erledigt) und die Notizen zeigt nur die",
          "Artefakt-Seite: https://claude.ai/artifact/KsKynwTEwnXxWeXT1Qdw4u", ""]
    for wer, titel in WER.items():
        teil = sorted([a for a in auf if a["wer"] == wer], key=lambda a: a["wann"] != "vor")
        md += [f"## {titel} ({len(teil)})", "", "| Wann | Bereich | Aufgabe | Liefern |", "|---|---|---|---|"]
        for a in teil:
            wann = "vor Livegang" if a["wann"] == "vor" else "nach Livegang"
            md.append(f"| {wann} | {a['bereich']} | **{a['titel']}**: {a['text']} | {a['liefern'] or '–'} |")
        md.append("")
    (ziel / "KATALOG.md").write_text("\n".join(md), encoding="utf-8")
    print(f"{len(auf)} Aufgaben → {ziel / 'katalog.html'}, {ziel / 'KATALOG.md'}")

if __name__ == "__main__":
    main()
