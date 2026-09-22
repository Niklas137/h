#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erzeugt das Prüfpaket für den Rechtsprüfer: Impressum, Datenschutzerklärung und AGB aus
`website/inhalt/*.json` als Markdown (Variante aus `site.json` → `hosting`), mit Deckblatt
(Änderungen, Fragen, E-Mail-Vorlage) aus `website/tools/pruefpaket-deckblatt.md`.

    python3 website/tools/pruefpaket.py            # schreibt website/pruefpaket-rechtstexte.md
    python3 seo-audit/tools/md_to_pdf.py website/pruefpaket-rechtstexte.md --out website/pruefpaket-rechtstexte.pdf
"""
import html
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
WEB = HIER.parent
INHALT = WEB / "inhalt"


def md_text(s: str) -> str:
    """HTML-Fragment aus dem Inhalt nach Markdown."""
    s = re.sub(r"<a\s+href=\"([^\"]+)\"[^>]*>(.*?)</a>", r"[\2](\1)", s)
    s = re.sub(r"</?strong>", "**", s)
    s = re.sub(r"</?em>", "*", s)
    s = re.sub(r"</?code>", "`", s)
    s = re.sub(r"<br\s*/?>", "  \n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s)


def bloecke(items, varianten, hosting):
    out = []
    for it in items:
        if isinstance(it, str):
            out.append(md_text(it) + "\n")
        elif "liste" in it:
            out.append("\n".join("- " + md_text(x) for x in it["liste"]) + "\n")
        elif "nummern" in it:
            out.append("\n".join(f"{i}. " + md_text(x) for i, x in enumerate(it["nummern"], 1)) + "\n")
        elif "h3" in it:
            out.append("### " + md_text(it["h3"]) + "\n")
        elif "links" in it:
            out.append(", ".join(f"[{md_text(l['text'])}]({l['ziel']})" for l in it["links"]) + "\n")
        elif "variante" in it:
            out.append(bloecke(varianten[hosting][it["variante"]], varianten, hosting))
    return "\n".join(out)


def seite_md(name: str, hosting: str) -> str:
    d = json.loads((INHALT / f"{name}.json").read_text(encoding="utf-8"))
    teile = [f"# {md_text(d['h1'])}\n"]
    if d.get("einleitung"):
        teile.append(md_text(d["einleitung"]) + "\n")
    for a in d.get("abschnitte", []):
        teile.append("## " + md_text(a["h2"]) + "\n")
        teile.append(bloecke(a.get("inhalt", []), d.get("varianten", {}), hosting))
    return "\n".join(teile)


def main():
    site = json.loads((INHALT / "site.json").read_text(encoding="utf-8"))
    hosting = site.get("hosting", "strato")
    deckblatt = (HIER / "pruefpaket-deckblatt.md").read_text(encoding="utf-8")
    teile = [deckblatt.replace("{{hosting}}", hosting)]
    for name in ("impressum", "datenschutz", "agb"):
        teile.append("\n\n---\n\n" + seite_md(name, hosting))
    ziel = WEB / "pruefpaket-rechtstexte.md"
    ziel.write_text("\n".join(teile), encoding="utf-8")
    print("geschrieben:", ziel, "| Hosting-Variante:", hosting)


if __name__ == "__main__":
    main()
