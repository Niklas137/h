#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baut die zweisprachige Website von NAHX Technologies aus `nahx/inhalt/*.json` nach `nahx/dist/`.

    python3 nahx/build.py                     # baut nach nahx/dist/, Links site-absolut (/en/services/)
    python3 nahx/build.py --pruefen           # baut und prüft (h1, Überschriften, Title, Description, Alt,
                                              # Links, Anker, hreflang und Sitemap sofern Basis-URL gesetzt); Fehler = Exit 1
    python3 nahx/build.py --relativ --ausgabe /tmp/vorschau     # Vorschau mit relativen Links
    python3 nahx/build.py --basis-url https://example.org --noindex

Keine Abhängigkeiten außer Python 3.8+. Inhalte: `inhalt/site.json` (gemeinsame Daten), `inhalt/de.json`,
`inhalt/en.json` (gleiche Seitenschlüssel). Textfelder sind HTML-Fragmente (<strong>, <em>, <a>, <br> erlaubt).
Ohne Basis-URL (Domain noch offen) werden Canonical, hreflang, og:url und Sitemap weggelassen.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import posixpath
import re
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path

HIER = Path(__file__).resolve().parent
INHALT = HIER / "inhalt"
ASSETS = HIER / "assets"
STANDARD_AUSGABE = HIER / "dist"

_AMP = re.compile(r"&(?!(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);)")


def frag(s: str) -> str:
    return _AMP.sub("&amp;", s)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def zeilen(h: str) -> str:
    """Zerlegt eine Überschrift an <br> in maskierte Zeilen für den gestaffelten Einlauf (wie im Referenzvideo)."""
    teile = [t.strip() for t in re.split(r"<br\s*/?>", h) if t.strip()]
    return "".join(f'<span class="zeile" style="--z:{i}"><span>{frag(t)}</span></span>' for i, t in enumerate(teile))


def lade(pfad: Path) -> dict:
    with pfad.open(encoding="utf-8") as f:
        daten = json.load(f)
    return {k: v for k, v in daten.items() if not k.startswith("_")}


# Vektor-Wortmarke (Maße aus der Logo-Vorlage gemessen, Einheiten 1:1), inline mit currentColor
WORTMARKE = (
    '<svg class="wortmarke" viewBox="0 0 1100 216" aria-hidden="true" focusable="false">'
    '<defs><linearGradient id="nahx-c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2BFFD3"/><stop offset="1" stop-color="#00C99A"/></linearGradient></defs>'
    '<path fill="currentColor" d="M0 0H51V216H0Z M207 0H258V216H207Z M0 0H60L258 216H198Z M578 0H629V216H578Z M760 0H811V216H760Z M578 87H811V132H578Z M824 0H893L1098 216H1029Z M1029 0H1098L893 216H824Z"/>'
    '<path fill="url(#nahx-c)" fill-rule="evenodd" d="M414 0L562 216H276Z M414 76L504 216H325Z M414 137L465 216H364Z"/></svg>'
)

# Bereichs-Piktogramme: ruhige Liniengrafiken (Dokument, Fenster, Verzweigung)
PIKTO = {
    0: '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M12 6h17l9 9v27H12z"/><path d="M29 6v9h9M18 24h14M18 30h14M18 36h9"/></svg>',
    1: '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="6" y="9" width="36" height="30" rx="2"/><path d="M6 17h36M12 13h2M17 13h2M18 27l-4 4 4 4M30 27l4 4-4 4M26 25l-4 12"/></svg>',
    2: '<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="10" cy="24" r="4"/><circle cx="38" cy="12" r="4"/><circle cx="38" cy="36" r="4"/><path d="M14 24h8c4 0 6-2 8-6l4-6M22 24c4 0 6 2 8 6l4 6M14 24h20"/></svg>',
}

KOPF_SCRIPT = "document.documentElement.classList.add('js');"
FUSS_SCRIPT = ""  # Bewegung und Menü liegen in assets/bewegung.js


class Bau:
    def __init__(self, site: dict, basis_url: str, relativ: bool, noindex: bool, ausgabe: Path):
        self.site = site
        self.basis_url = (basis_url or "").rstrip("/")
        self.relativ = relativ
        self.noindex = noindex
        self.ausgabe = ausgabe
        self.sprachen = {code: lade(INHALT / f"{code}.json") for code in site["sprachen"]}
        self.heute = dt.date.today().isoformat()
        self.pfade: dict[tuple[str, str], str] = {}
        for code, texte in self.sprachen.items():
            wurzel = site["sprachen"][code]["pfad"]
            for schluessel, seite in texte["seiten"].items():
                self.pfade[(code, schluessel)] = wurzel + seite["pfad"]

    # ------------------------------------------------------------------ Links
    def pfad(self, sprache: str, seite: str, anker: str | None = None) -> str:
        return self.pfade[(sprache, seite)] + (f"#{anker}" if anker else "")

    def link(self, von: str, ziel: str) -> str:
        if not self.relativ or not ziel.startswith("/"):
            return ziel
        ziel_pfad, _, anker = ziel.partition("#")
        von_dir = posixpath.dirname(von) if not von.endswith("/") else von
        rel = posixpath.relpath(ziel_pfad or "/", von_dir)
        if ziel_pfad.endswith("/"):
            rel = "index.html" if rel == "." else rel + "/index.html"
        return rel + (f"#{anker}" if anker else "")

    def absolut(self, pfad: str) -> str | None:
        return (self.basis_url + pfad) if self.basis_url else None

    def bild(self, sprache: str, pfad: str, name: str, sizes: str, lazy: bool = True, klasse: str = "", prio: bool = False) -> str:
        f = self.site["fotos"][name]
        breiten = f["breiten"]
        l = lambda w, ext: esc(self.link(pfad, f"/assets/img/foto/{name}-{w}.{ext}"))
        webp = ", ".join(f"{l(w, 'webp')} {w}w" for w in breiten)
        jpg = ", ".join(f"{l(w, 'jpg')} {w}w" for w in breiten)
        attrs = f'loading="{"lazy" if lazy else "eager"}" decoding="async"' + (' fetchpriority="high"' if prio else "")
        return (f'<picture class="foto {klasse}".strip()><source type="image/webp" srcset="{webp}" sizes="{sizes}">'
                f'<img src="{l(breiten[-2] if len(breiten) > 1 else breiten[-1], "jpg")}" srcset="{jpg}" sizes="{sizes}" alt="{esc(f["alt"][sprache])}" {attrs} style="aspect-ratio:{f["seitenverhaeltnis"]}"></picture>')

    def cta(self, sprache: str, pfad: str, cta: dict, klasse: str = "cta") -> str:
        ziel = self.link(pfad, self.pfad(sprache, cta["seite"], cta.get("anker")))
        return f'<a class="{klasse}" href="{esc(ziel)}">{esc(cta["text"])}</a>'

    # ------------------------------------------------------------------ Kopf und Fuß
    def kopf(self, sprache: str, seite_key: str, pfad: str) -> str:
        t = self.sprachen[sprache]
        ui = t["ui"]
        nav = []
        for e in t["navigation"]:
            if e["seite"] == "start":
                continue
            ziel = self.link(pfad, self.pfad(sprache, e["seite"]))
            aktuell = ' aria-current="page"' if e["seite"] == seite_key else ""
            nav.append(f'<a href="{esc(ziel)}"{aktuell}>{esc(e["text"])}</a>')
        sprach = []
        for c in self.sprachen:
            if c == sprache:
                continue
            sprach.append(f'<a class="schalter" href="{esc(self.link(pfad, self.pfad(c, seite_key)))}" lang="{c}" hreflang="{c}" aria-label="{esc(self.site["sprachen"][c]["name"])}">{esc(self.site["sprachen"][c]["kurz"])}</a>')
        start = self.link(pfad, self.pfad(sprache, "start"))
        kontakt = self.link(pfad, self.pfad(sprache, "kontakt"))
        return f"""<a class="sprung" href="#inhalt">{esc(ui["sprung"])}</a>
<header class="kopf">
  <div class="innen kopf-innen">
    <a class="logo" href="{esc(start)}" aria-label="{esc(ui["logo_alt"])}">{WORTMARKE}<span class="logo-zusatz" aria-hidden="true">Technologies</span></a>
    <nav class="nav" id="nav" aria-label="{esc(ui["fuss_navigation"])}">{"".join(nav)}<a class="cta kopf-cta" href="{esc(kontakt)}">{esc(ui["kopf_cta"])}</a></nav>
    <div class="kopf-aktionen">{"".join(sprach)}<button class="schalter menue-schalter" type="button" aria-expanded="false" aria-controls="nav">{esc(ui["menue"])}</button></div>
  </div>
</header>"""

    def fuss(self, sprache: str, pfad: str) -> str:
        t = self.sprachen[sprache]
        ui = t["ui"]
        nav = "".join(f'<a href="{esc(self.link(pfad, self.pfad(sprache, e["seite"])))}">{esc(e["text"])}</a>' for e in t["navigation"])
        recht = "".join(f'<a href="{esc(self.link(pfad, self.pfad(sprache, s)))}">{esc(t["seiten"][s]["menue"])}</a>' for s in t["rechtsseiten"])
        sprachen = "".join(f'<a href="{esc(self.link(pfad, self.pfad(c, "start")))}" lang="{c}" hreflang="{c}">{esc(self.site["sprachen"][c]["name"])}</a>' for c in self.sprachen)
        email = t["email"]
        email_html = f'<a href="mailto:{esc(email)}">{esc(email)}</a>' if "@" in email else esc(email)
        return f"""<footer class="fuss">
  <div class="innen">
    <div class="fuss-spalten">
      <div class="marke">
        <div class="fuss-marke">{WORTMARKE}<span class="logo-zusatz">Technologies</span></div>
        <p class="fuss-claim">{esc(t["claim"])}</p>
        <p class="fuss-claim" lang="{'en' if sprache == 'de' else 'de'}">{esc(t["claim_andere"])}</p>
      </div>
      <nav aria-label="{esc(ui["fuss_navigation"])}"><strong>{esc(ui["fuss_navigation"])}</strong>{nav}</nav>
      <nav aria-label="{esc(ui["fuss_recht"])}"><strong>{esc(ui["fuss_recht"])}</strong>{recht}</nav>
      <div><strong>{esc(ui["fuss_sprache"])}</strong><nav aria-label="{esc(ui["fuss_sprache"])}">{sprachen}</nav><strong class="fuss-kontakt-titel">{esc(ui.get("fuss_kontakt", "Kontakt"))}</strong><p>{email_html}</p></div>
    </div>
    <p class="fuss-klein">{esc(ui["fuss_hinweis"])}</p>
    <details class="bildnachweis"><summary>{esc(ui.get("bildnachweis", "Bildnachweis"))}</summary><p class="fuss-klein">{esc(ui.get("fotos_hinweis", ""))} {" · ".join(f'<a href="{esc(f["quelle"])}" rel="noopener">{esc(f["fotograf"])}</a>' for f in self.site["fotos"].values() if not f.get("variante_von"))}</p></details>
  </div>
</footer>"""

    # ------------------------------------------------------------------ Abschnitte
    def abschnitt(self, sprache: str, pfad: str, a: dict) -> str:
        typ = a["typ"]
        ident = f' id="{esc(a["id"])}"' if a.get("id") else ""
        kopf = ""
        if a.get("h2") or a.get("text"):
            kopf = '<div class="abschnitt-kopf reveal">'
            if a.get("h2"):
                kopf += f'<h2>{frag(a["h2"])}</h2>'
            if a.get("text"):
                kopf += f'<p class="abschnitt-text">{frag(a["text"])}</p>'
            kopf += "</div>"
        mehr = ""
        if a.get("link"):
            mehr = f'<p class="mehr-zeile reveal">{self.cta(sprache, pfad, a["link"], "mehr")}</p>'

        if typ == "bereiche-start":
            reihen = []
            for nr, k in enumerate(a["karten"]):
                l = k["link"]
                ziel = self.link(pfad, self.pfad(sprache, l["seite"], l.get("anker")))
                reihen.append(f"""<article class="reihe reveal{" reihe-umgekehrt" if nr % 2 else ""}">
  <a class="reihe-bild" href="{esc(ziel)}" tabindex="-1" aria-hidden="true">{self.bild(sprache, pfad, k["bild"], "(min-width: 900px) 56vw, 100vw", True, "parallax")}</a>
  <div class="reihe-text"><p class="nr">0{nr + 1}</p><h3>{frag(k["h3"])}</h3><p>{frag(k["text"])}</p><a class="mehr" href="{esc(ziel)}">{esc(l["text"])}</a></div>
</article>""")
            return f'<section class="abschnitt abschnitt-breit"{ident}><div class="innen">{kopf}</div><div class="reihen">{"".join(reihen)}</div></section>'

        if typ == "leistungskarten":
            # Drei Karten mit Foto, Mint-Piktogramm, Titel, Satz und Link (Markenboard 2026-10-26)
            karten = []
            for nr, k in enumerate(a["karten"]):
                l = k["link"]
                ziel = self.link(pfad, self.pfad(sprache, l["seite"], l.get("anker")))
                karten.append(f'''<article class="lk-karte reveal" style="--i:{nr}">
  <div class="lk-bild">{self.bild(sprache, pfad, k["bild"], "(min-width: 900px) 30vw, 100vw")}</div>
  <div class="lk-text"><span class="lk-icon">{PIKTO[nr % 3]}</span><h3>{frag(k["h3"])}</h3><p>{frag(k["text"])}</p><a class="mehr" href="{esc(ziel)}">{esc(l["text"])}</a></div>
</article>''')
            kopf_lk = f'<div class="abschnitt-kopf reveal"><p class="kicker">{esc(a.get("kicker", ""))}</p><h2>{frag(a["h2"])}</h2>' + (f'<p class="abschnitt-text">{frag(a["text"])}</p>' if a.get("text") else "") + "</div>"
            return f'<section class="abschnitt innen leistungskarten"{ident}>{kopf_lk}<div class="lk-raster">{"".join(karten)}</div>{mehr}</section>'

        if typ == "ablauf":
            # Foto links, Leitsatz in der Mitte, nummerierte Schritte rechts (Markenboard 2026-10-26)
            schritte = "".join(f'<li class="reveal" style="--i:{i}"><span class="nr">0{i + 1}</span><div><h3>{frag(x["h3"])}</h3><p>{frag(x["text"])}</p></div></li>' for i, x in enumerate(a["schritte"]))
            cta = self.cta(sprache, pfad, a["link"], "pfeil") if a.get("link") else ""
            return f"""<section class="ablauf szene"{ident}><div class="ablauf-foto">{self.bild(sprache, pfad, a["bild"], "(min-width: 900px) 38vw, 100vw", True, "parallax")}</div>
  <div class="ablauf-text reveal"><p class="kicker">{esc(a.get("kicker", ""))}</p><h2>{frag(a["h2"])}</h2><p class="abschnitt-text">{frag(a["text"])}</p><p>{cta}</p></div>
  <ol class="ablauf-liste">{schritte}</ol>
</section>"""

        if typ == "collage":
            # Bildcollage mit Fakten (nur zählbare Angaben aus der Website selbst, keine Leistungskennzahlen)
            teile = []
            for nr, b in enumerate(a["bilder"]):
                l = b.get("link")
                ziel = self.link(pfad, self.pfad(sprache, l["seite"], l.get("anker"))) if l else ""
                inner = self.bild(sprache, pfad, b["bild"], "(min-width: 900px) 34vw, 60vw") + (f'<span class="collage-label">{esc(b["label"])}</span>' if b.get("label") else "")
                teile.append((f'<a class="collage-bild cb{nr + 1} reveal" href="{esc(ziel)}" data-tempo="{b.get("tempo", 0.4)}" aria-label="{esc(b.get("label", ""))}">{inner}</a>') if l else f'<div class="collage-bild cb{nr + 1} reveal" data-tempo="{b.get("tempo", 0.4)}">{inner}</div>')
            for nr, f in enumerate(a["fakten"]):
                wert = f["wert"]
                zahl = f' data-zahl="{esc(wert)}"' if re.fullmatch(r"\d+", wert) else ""
                teile.append(f'<div class="fakt fk{nr + 1} reveal" style="--i:{nr + 1}"><p class="fakt-wert"{zahl}>{frag("0" * len(wert) if zahl else wert)}</p><p class="fakt-text">{frag(f["text"])}</p></div>')
            absatz = f'<p class="collage-absatz reveal">{frag(a["text"])}</p>' if a.get("text") else ""
            cta = f'<p class="collage-cta reveal">{self.cta(sprache, pfad, a["cta"], "pfeil")}</p>' if a.get("cta") else ""
            return f'<section class="leinwand collage szene"{ident}><div class="innen collage-innen"><h2 class="collage-titel reveal">{frag(a["h2"])}</h2><div class="collage-raster">{"".join(teile)}{absatz}{cta}</div></div></section>'

        if typ == "buehne":
            # Vollbildfoto mit Glas-Markierungen (Hotspots) auf echte Projekte; mobil als Liste
            punkte = []
            for nr, pkt in enumerate(a["punkte"]):
                l = pkt["link"]
                ziel = self.link(pfad, self.pfad(sprache, l["seite"], l.get("anker")))
                punkte.append(f'<li class="punkt reveal" style="--x:{pkt["x"]};--y:{pkt["y"]};--i:{nr + 1}"><span class="punkt-dot" aria-hidden="true"></span><span class="punkt-linie" aria-hidden="true"></span><a class="glas punkt-glas" href="{esc(ziel)}"><span class="punkt-titel">{frag(pkt["titel"])}</span><span class="punkt-text">{frag(pkt["text"])}</span></a></li>')
            cta = f'<p class="buehne-cta reveal">{self.cta(sprache, pfad, a["cta"], "pfeil")}</p>' if a.get("cta") else ""
            absatz = f'<p class="buehne-absatz reveal">{frag(a["text"])}</p>' if a.get("text") else ""
            return f"""<section class="leinwand buehne szene licht"{ident}><div class="licht-ring" aria-hidden="true"></div><div class="buehne-foto">{self.bild(sprache, pfad, a["bild"], "100vw", True, "parallax")}</div>
  <ul class="punkte" aria-label="{esc(a.get("punkte_label", ""))}">{"".join(punkte)}</ul>
  <div class="innen buehne-innen"><div class="buehne-text"><p class="kicker reveal">{esc(a.get("kicker", ""))}</p><h2 class="zeilen reveal">{zeilen(a["h2"])}</h2>{absatz}</div>{cta}</div>
</section>"""

        if typ == "marke":
            return f"""<section class="markenbuehne leinwand"{ident}><canvas id="szene3d" class="szene3d" aria-hidden="true"></canvas>
  <div class="innen marke-innen reveal"><p class="kicker">NAHX</p><h2 class="zeilen">{zeilen(a["h2"])}</h2><p class="abschnitt-text">{frag(a["text"])}</p><p class="marke-claim">{esc(a["claim"])}</p></div>
</section>"""

        if typ == "karten":
            karten = []
            for nr, k in enumerate(a["karten"]):
                l = k.get("link")
                kl = f'<a class="mehr" href="{esc(self.link(pfad, self.pfad(sprache, l["seite"], l.get("anker"))))}">{esc(l["text"])}</a>' if l else ""
                karten.append(f'<article class="karte reveal" style="--i:{nr}"><span class="pikto">{PIKTO[nr % 3]}</span><h3>{frag(k["h3"])}</h3><p>{frag(k["text"])}</p>{kl}</article>')
            return f'<section class="abschnitt innen"{ident}>{kopf}<div class="raster">{"".join(karten)}</div>{mehr}</section>'

        if typ == "projekte":
            liste = next(x for x in self.sprachen[sprache]["seiten"]["projekte"]["abschnitte"] if x["typ"] == "projektliste")
            bloecke = []
            for nr, p in enumerate(liste["projekte"]):
                if nr >= 3:
                    break
                ziel = self.link(pfad, self.pfad(sprache, "projekte")) + f"#projekt-{nr + 1}"
                bloecke.append(f"""<article class="projekt-block reveal" style="--i:{nr}">
  <a class="projekt-bild" href="{esc(ziel)}" tabindex="-1" aria-hidden="true">{self.bild(sprache, pfad, p["bild"], "(min-width: 900px) 33vw, 100vw")}</a>
  <p class="bereich">{esc(p["bereich"])}</p><h3>{frag(p["titel"])}</h3><p>{frag(p.get("kurz", p["herausforderung"]))}</p><p class="klein tech">{esc(p["technologien"].split(";")[0])}</p><a class="mehr" href="{esc(ziel)}">{esc(liste["legende"].get("mehr", "Details"))}</a>
</article>""")
            return f'<section class="abschnitt innen"{ident}>{kopf}<div class="projekt-bloecke">{"".join(bloecke)}</div>{mehr}</section>'

        if typ == "projektliste":
            L = a["legende"]
            eintraege = []
            for nr, p in enumerate(a["projekte"]):
                felder = "".join(f'<div><dt>{esc(L[k])}</dt><dd>{frag(p[k])}</dd></div>' for k in ("ausgang", "herausforderung", "beitrag", "ansatz", "technologien"))
                fluss = ""
                if p.get("ablauf"):
                    schritte = "".join(f'<li>{esc(x)}</li>' for x in p["ablauf"])
                    fluss = f'<div class="fluss"><p class="fluss-titel">{esc(L.get("ablauf", "Ablauf"))}</p><ol class="fluss-kette">{schritte}</ol></div>'
                bild = self.bild(sprache, pfad, p["bild"], "(min-width: 900px) 42vw, 100vw") if p.get("bild") else ""
                eintraege.append(f'<article class="projekt reveal{" projekt-umgekehrt" if nr % 2 else ""}" id="projekt-{nr + 1}"><div class="projekt-kopf"><div class="projekt-foto szene">{bild}</div><header><p class="bereich">{esc(p["bereich"])}</p><h2>{frag(p["titel"])}</h2><p class="projekt-kurz">{frag(p.get("kurz", ""))}</p></header></div>{fluss}<dl class="felder">{felder}</dl><p class="status"><span>{esc(L["status"])}</span>{frag(p["status"])}</p></article>')
            hinweis = f'<p class="hinweis reveal">{frag(a["hinweis"])}</p>' if a.get("hinweis") else ""
            return f'<section class="abschnitt innen"{ident}>{"".join(eintraege)}{hinweis}</section>'

        if typ == "bereiche":
            bl = []
            t = self.sprachen[sprache]["ui"]
            for nr, b in enumerate(a["bereiche"]):
                def liste(items):
                    return "".join(f"<li>{frag(x)}</li>" for x in items)
                bl.append(f"""<article class="bereich reveal" id="{esc(b["id"])}">
  <div class="bereich-kopf"><div class="bereich-foto szene">{self.bild(sprache, pfad, b["bild"], "(min-width: 900px) 40vw, 100vw") if b.get("bild") else ""}</div><div><span class="pikto">{PIKTO[nr % 3]}</span><h2>{frag(b["h2"])}</h2><p class="abschnitt-text">{frag(b["text"])}</p></div></div>
  <div class="bereich-raster">
    <div><h3>{esc(t["l_herausforderungen"])}</h3><ul>{liste(b["herausforderungen"])}</ul></div>
    <div><h3>{esc(t["l_leistungen"])}</h3><ul>{liste(b["leistungen"])}</ul></div>
    <div><h3>{esc(t["l_faelle"])}</h3><ul>{liste(b["faelle"])}</ul></div>
  </div>
  <p class="fuer">{frag(b["fuer"])}</p>
</article>""")
            cta = f'<p class="mehr-zeile reveal">{frag(a.get("cta_text", ""))} {self.cta(sprache, pfad, a["cta"], "mehr")}</p>' if a.get("cta") else ""
            return f'<section class="abschnitt innen"{ident}>{"".join(bl)}{cta}</section>'

        if typ == "listen":
            karten = []
            for nr, k in enumerate(a["karten"]):
                punkte = "".join(f"<li>{frag(p)}</li>" for p in k["punkte"])
                karten.append(f'<article class="karte reveal" id="{esc(k["id"])}" style="--i:{nr}"><h2>{frag(k["h2"])}</h2><ul>{punkte}</ul></article>')
            return f'<section class="abschnitt innen"{ident}>{kopf}<div class="raster">{"".join(karten)}</div></section>'

        if typ == "schritte":
            schritte = "".join(f'<li class="reveal" style="--i:{i}"><span class="nr">0{i + 1}</span><h3>{frag(x["h3"])}</h3><p>{frag(x["text"])}</p></li>' for i, x in enumerate(a["schritte"]))
            return f'<section class="abschnitt innen"{ident}>{kopf}<ol class="schritte">{schritte}</ol>{mehr}</section>'

        if typ == "prinzipien":
            punkte = "".join(f'<li class="reveal" style="--i:{i}"><h3>{frag(x["h3"])}</h3><p>{frag(x["text"])}</p></li>' for i, x in enumerate(a["punkte"]))
            return f'<section class="abschnitt innen"{ident}>{kopf}<ul class="prinzipien">{punkte}</ul></section>'

        if typ == "stack":
            gruppen = "".join(f'<div class="karte reveal" style="--i:{i}"><h3>{esc(g["h3"])}</h3><ul>{"".join(f"<li>{frag(x)}</li>" for x in g["punkte"])}</ul></div>' for i, g in enumerate(a["gruppen"]))
            return f'<section class="abschnitt innen"{ident}>{kopf}<div class="raster">{gruppen}</div></section>'

        if typ == "faq":
            fragen = "".join(f'<details class="frage reveal" style="--i:{i}"><summary><h3>{frag(q["f"])}</h3></summary><p>{frag(q["a"])}</p></details>' for i, q in enumerate(a["fragen"]))
            return f'<section class="abschnitt innen"{ident}>{kopf}<div class="fragen">{fragen}</div></section>'

        if typ == "text":
            absaetze = "".join(f"<p>{frag(p)}</p>" for p in a["absaetze"])
            h2 = f'<h2>{frag(a["h2"])}</h2>' if a.get("h2") else ""
            return f'<section class="abschnitt innen"{ident}><div class="fliess reveal">{h2}{absaetze}</div></section>'

        if typ == "band":
            foto = f'<div class="band-foto">{self.bild(sprache, pfad, a["bild"], "100vw", True, "parallax")}</div>' if a.get("bild") else ""
            return f'<section class="band leinwand szene{" band-mit-foto licht" if a.get("bild") else ""}"{ident}>{foto}<div class="innen band-innen"><div class="band-text reveal"><p class="kicker">{esc(a.get("kicker", ""))}</p><h2 class="zeilen">{zeilen(a["h2"])}</h2><p>{frag(a["text"])}</p></div><p class="band-cta reveal">{self.cta(sprache, pfad, a["cta"], "pfeil")}</p></div></section>'

        if typ == "kontakt":
            return self.kontakt(sprache, pfad, a)
        raise ValueError(f"Unbekannter Abschnittstyp: {typ}")

    def kontakt(self, sprache: str, pfad: str, a: dict) -> str:
        email = self.sprachen[sprache]["email"]
        email_html = f'<a class="email" href="mailto:{esc(email)}">{esc(email)}</a>' if "@" in email else f'<span class="platzhalter">{esc(email)}</span>'
        datenschutz = a["datenschutz"].replace("{datenschutz}", esc(self.link(pfad, self.pfad(sprache, "datenschutz"))))
        themen = "".join(f"<li>{frag(x)}</li>" for x in a["themen"])
        return f"""<section class="abschnitt innen" id="kontakt">
  <div class="kontakt-raster">
    <div class="karte email-karte reveal"><h2>{esc(a["email_label"])}</h2><p class="email-text">{frag(a["email_text"])}</p><p>{email_html}</p><p class="klein">{frag(datenschutz)}</p></div>
    <div class="karte reveal" style="--i:1"><h2>{frag(a["themen_h2"])}</h2><ul>{themen}</ul></div>
  </div>
</section>"""

    # ------------------------------------------------------------------ Seite
    def head(self, sprache: str, seite_key: str, pfad: str, title: str, description: str, robots: str, json_ld: dict | None) -> str:
        t = self.sprachen[sprache]
        l = lambda p: esc(self.link(pfad, p))
        teile = [
            '<meta charset="utf-8">', '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{esc(title)}</title>", f'<meta name="description" content="{esc(description)}">',
            f'<meta name="robots" content="{robots}">', '<meta name="theme-color" content="#030907">',
        ]
        if self.basis_url and seite_key:
            teile.append(f'<link rel="canonical" href="{esc(self.absolut(pfad))}">')
            for c in self.sprachen:
                teile.append(f'<link rel="alternate" hreflang="{c}" href="{esc(self.absolut(self.pfade[(c, seite_key)]))}">')
            teile.append(f'<link rel="alternate" hreflang="x-default" href="{esc(self.absolut(self.pfade[("de", seite_key)]))}">')
        teile += [
            '<meta property="og:type" content="website">', f'<meta property="og:site_name" content="{esc(self.site["name"])}">',
            f'<meta property="og:locale" content="{esc(self.site["sprachen"][sprache]["locale"])}">',
            f'<meta property="og:title" content="{esc(title)}">', f'<meta property="og:description" content="{esc(description)}">',
        ]
        if self.basis_url:
            teile.append(f'<meta property="og:url" content="{esc(self.absolut(pfad))}">')
            teile.append(f'<meta property="og:image" content="{esc(self.absolut(self.site["og_bild"]))}">')
        else:
            teile.append(f'<meta property="og:image" content="{l(self.site["og_bild"])}">')
        teile += [
            '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
            f'<meta property="og:image:alt" content="{esc(t["og_bild_alt"])}">', '<meta name="twitter:card" content="summary_large_image">',
            f'<link rel="icon" href="{l("/assets/img/favicon.svg")}" type="image/svg+xml">',
            f'<link rel="icon" href="{l("/assets/img/favicon.ico")}" sizes="32x32">',
            f'<link rel="apple-touch-icon" href="{l("/assets/img/apple-touch-icon.png")}">',
        ]
        for f in self.site["fonts_vorladen"]:
            teile.append(f'<link rel="preload" href="{l("/assets/fonts/" + f)}" as="font" type="{'font/ttf' if f.endswith('.ttf') else 'font/woff2'}" crossorigin>')
        teile.append(f'<link rel="stylesheet" href="{l("/assets/site.css")}">')
        teile.append(f"<script>{KOPF_SCRIPT}</script>")
        if json_ld:
            teile.append('<script type="application/ld+json">' + json.dumps(json_ld, ensure_ascii=False).replace("</", "<\\/") + "</script>")
        return "\n".join(teile)

    def held(self, sprache: str, seite_key: str, pfad: str, s: dict) -> str:
        """Aufmacher als Vollbild-Leinwand: Foto, Kicker, Zeilenüberschrift, Einleitung und Schaltflächen links, Glaskarte unten rechts."""
        ui = self.sprachen[sprache]["ui"]
        cta = ""
        if s.get("cta"):
            cta = '<div class="cta-reihe">' + self.cta(sprache, pfad, s["cta"]["primaer"]) + self.cta(sprache, pfad, s["cta"]["sekundaer"], "cta-zweit") + "</div>"
        text = f'<p class="held-klein">{frag(s["text"])}</p>' if s.get("text") else ""
        warn = f'<p class="warnung">{esc(ui["platzhalter_hinweis"])}</p>' if s.get("platzhalter") else ""
        klasse = " held-start" if seite_key == "start" else ""
        foto = f'<div class="held-foto parallax-held">{self.bild(sprache, pfad, s["bild"], "100vw", False, "", True)}</div>' if s.get("bild") else ""
        karte = ""
        if s.get("karte"):
            k = s["karte"]
            zahl = f' data-zahl="{esc(k["titel"])}"' if re.fullmatch(r"\d+", k["titel"]) else ""
            karte = f'<aside class="glas held-karte reveal" aria-label="{esc(k.get("label", k["titel"]))}"><p class="glas-titel"{zahl}>{frag("0" * len(k["titel"]) if zahl else k["titel"])}</p><p>{frag(k["text"])}</p></aside>'
        weiter = f'<a class="weiter" href="#inhalt-weiter" aria-label="{esc(ui.get("weiter", "Scrollen"))}"><span>{esc(ui.get("weiter", "Scrollen"))}</span><i></i></a>' if s.get("bild") else ""
        return f"""<section class="held leinwand szene{" licht" if s.get("bild") else ""}{klasse}{" held-foto-seite" if s.get("bild") else ""}">{foto}<div class="licht-ring" aria-hidden="true"></div><div class="held-schleier" aria-hidden="true"></div><div class="innen held-innen">
  <div class="held-text">
    <p class="kicker">{esc(s["kicker"])}</p>
    <h1 class="zeilen">{zeilen(s["h1"])}</h1>
    <p class="held-absatz">{frag(s["einleitung"])}</p>
    {text}{warn}{cta}
  </div>{karte}{weiter}
</div></section><span id="inhalt-weiter"></span>"""

    def seite_html(self, sprache: str, seite_key: str) -> tuple[str, str]:
        t = self.sprachen[sprache]
        s = t["seiten"][seite_key]
        pfad = self.pfade[(sprache, seite_key)]
        robots = "noindex, nofollow" if (self.noindex or s.get("robots") == "noindex") else "index, follow"
        json_ld = {
            "@context": "https://schema.org", "@type": "WebPage", "name": s["title"], "description": s["description"], "inLanguage": sprache,
            "isPartOf": {"@type": "WebSite", "name": self.site["name"]},
            "about": {"@type": "ProfessionalService", "name": self.site["name"], "slogan": t["claim"]},
        }
        if self.basis_url:
            json_ld["url"] = self.absolut(pfad)
            json_ld["isPartOf"]["url"] = self.absolut("/")
        abschnitte = "".join(self.abschnitt(sprache, pfad, a) for a in s["abschnitte"])
        html_ = f"""<!doctype html>
<html lang="{sprache}">
<head>
{self.head(sprache, seite_key, pfad, s["title"], s["description"], robots, json_ld)}
</head>
<body class="seite-{esc(seite_key)}">
{self.kopf(sprache, seite_key, pfad)}
<main id="inhalt" class="{esc(s.get("typ", "seite"))}">
  {self.held(sprache, seite_key, pfad, s)}
  {abschnitte}
</main>
{self.fuss(sprache, pfad)}
<script src="{esc(self.link(pfad, "/assets/bewegung.js"))}" defer></script>
<script src="{esc(self.link(pfad, "/assets/szene3d.js"))}" defer></script>
</body>
</html>
"""
        return pfad, html_

    def fehlerseite_html(self, sprache: str) -> tuple[str, str]:
        t = self.sprachen[sprache]
        f = t["fehlerseite"]
        pfad = self.site["sprachen"][sprache]["pfad"] + "404.html"
        s = {"kicker": "404", "h1": f["h1"], "einleitung": f["text"]}
        html_ = f"""<!doctype html>
<html lang="{sprache}">
<head>
{self.head(sprache, "", pfad, f["title"], f["text"], "noindex, nofollow", None)}
</head>
<body class="seite-fehler">
{self.kopf(sprache, "start", pfad).replace(' aria-current="page"', '')}
<main id="inhalt" class="fehler">
  {self.held(sprache, "fehler", pfad, s).replace('</p>\n    \n  </div>', '</p><div class="cta-reihe">' + self.cta(sprache, pfad, f["cta"]) + '</div></div>')}
</main>
{self.fuss(sprache, pfad)}
<script>{FUSS_SCRIPT}</script>
</body>
</html>
"""
        return pfad, html_

    # ------------------------------------------------------------------ Ausgabe
    def schreibe(self, pfad: str, inhalt: str) -> Path:
        ziel = self.ausgabe / pfad.lstrip("/")
        if pfad.endswith("/"):
            ziel = ziel / "index.html"
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(inhalt, encoding="utf-8")
        return ziel

    def bauen(self) -> list[tuple[str, Path]]:
        if self.ausgabe.exists():
            shutil.rmtree(self.ausgabe)
        self.ausgabe.mkdir(parents=True)
        shutil.copytree(ASSETS, self.ausgabe / "assets", ignore=shutil.ignore_patterns("_*"))
        seiten: list[tuple[str, Path]] = []
        for sprache in self.sprachen:
            for seite_key in self.site["seiten"]:
                pfad, html_ = self.seite_html(sprache, seite_key)
                seiten.append((pfad, self.schreibe(pfad, html_)))
            pfad, html_ = self.fehlerseite_html(sprache)
            seiten.append((pfad, self.schreibe(pfad, html_)))
        if self.noindex:
            (self.ausgabe / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
        elif self.basis_url:
            (self.ausgabe / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {self.absolut('/sitemap.xml')}\n", encoding="utf-8")
            urls = []
            for seite_key in self.site["seiten"]:
                for sprache in self.sprachen:
                    if self.sprachen[sprache]["seiten"][seite_key].get("robots") == "noindex":
                        continue
                    alt = "".join(f'<xhtml:link rel="alternate" hreflang="{c}" href="{esc(self.absolut(self.pfade[(c, seite_key)]))}"/>' for c in self.sprachen)
                    urls.append(f"<url><loc>{esc(self.absolut(self.pfade[(sprache, seite_key)]))}</loc>{alt}<lastmod>{self.heute}</lastmod></url>")
            (self.ausgabe / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
        else:
            # Domain offen: keine Sitemap mit erfundenen URLs
            (self.ausgabe / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
        return seiten


# ---------------------------------------------------------------------- Prüfung
class Sammler(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h: list[tuple[int, str]] = []
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.bilder_ohne_alt = 0
        self.title = ""
        self.description = None
        self.canonical = None
        self.hreflang: list[str] = []
        self.json_ld = 0
        self.lang = None
        self._in = None
        self._puffer = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if a.get("id"):
            self.ids.add(a["id"])
        if tag in ("h1", "h2", "h3", "h4", "title"):
            self._in = tag
            self._puffer = ""
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "img" and not a.get("alt"):
            self.bilder_ohne_alt += 1
        if tag == "meta" and a.get("name") == "description":
            self.description = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tag == "link" and a.get("rel") == "alternate" and a.get("hreflang"):
            self.hreflang.append(a["hreflang"])
        if tag == "script" and a.get("type") == "application/ld+json":
            self.json_ld += 1

    def handle_data(self, data):
        if self._in:
            self._puffer += data

    def handle_endtag(self, tag):
        if tag == self._in:
            if tag == "title":
                self.title = self._puffer.strip()
            else:
                self.h.append((int(tag[1]), self._puffer.strip()))
            self._in = None


def pruefen(bau: Bau, seiten: list[tuple[str, Path]]) -> list[str]:
    fehler: list[str] = []
    alle: dict[str, Sammler] = {}
    for pfad, datei in seiten:
        s = Sammler()
        s.feed(datei.read_text(encoding="utf-8"))
        alle[pfad] = s
    for pfad, s in alle.items():
        ist_fehler = pfad.endswith("404.html")
        if not s.lang:
            fehler.append(f"{pfad}: lang-Attribut fehlt")
        h1 = [t for n, t in s.h if n == 1]
        if len(h1) != 1:
            fehler.append(f"{pfad}: {len(h1)} h1 (erwartet 1)")
        vorher = 1
        for n, t in s.h:
            if n > vorher + 1:
                fehler.append(f"{pfad}: Überschriftensprung h{vorher} → h{n} („{t}“)")
            vorher = n
        if not s.title or len(s.title) > 60:
            fehler.append(f"{pfad}: Title fehlt oder länger als 60 Zeichen ({len(s.title)}): {s.title}")
        if not ist_fehler:
            if s.description is None or not (150 <= len(s.description) <= 160):
                fehler.append(f"{pfad}: Description nicht 150–160 Zeichen ({len(s.description or '')})")
            if s.json_ld != 1:
                fehler.append(f"{pfad}: {s.json_ld} JSON-LD-Blöcke (erwartet 1)")
            if bau.basis_url:
                if not s.canonical:
                    fehler.append(f"{pfad}: Canonical fehlt")
                erwartet = set(bau.sprachen) | {"x-default"}
                if set(s.hreflang) != erwartet:
                    fehler.append(f"{pfad}: hreflang {sorted(s.hreflang)} statt {sorted(erwartet)}")
            elif s.canonical or s.hreflang:
                fehler.append(f"{pfad}: Canonical/hreflang trotz fehlender Basis-URL")
        if s.bilder_ohne_alt:
            fehler.append(f"{pfad}: {s.bilder_ohne_alt} Bild(er) ohne alt")
        for href in s.links:
            if href.startswith(("http", "mailto:", "tel:")):
                continue
            ziel, _, anker = href.partition("#")
            if bau.relativ:
                basis = posixpath.dirname(pfad) if not pfad.endswith("/") else pfad
                ziel_abs = posixpath.normpath(posixpath.join(basis, ziel)) if ziel else pfad
                if ziel_abs.endswith("/index.html"):
                    ziel_abs = ziel_abs[: -len("index.html")]
                elif ziel_abs == "index.html":
                    ziel_abs = "/"
                if not ziel_abs.startswith("/"):
                    ziel_abs = "/" + ziel_abs
            else:
                ziel_abs = ziel or pfad
            if ziel_abs.startswith("/assets/"):
                if not (bau.ausgabe / ziel_abs.lstrip("/")).exists():
                    fehler.append(f"{pfad}: Datei fehlt: {href}")
                continue
            if ziel_abs not in alle:
                fehler.append(f"{pfad}: Link ins Leere: {href} (→ {ziel_abs})")
                continue
            if anker and anker not in alle[ziel_abs].ids:
                fehler.append(f"{pfad}: Anker fehlt: {href}")
    if bau.basis_url and not bau.noindex:
        sitemap = (bau.ausgabe / "sitemap.xml").read_text(encoding="utf-8")
        for (sprache, key), pfad in bau.pfade.items():
            if bau.sprachen[sprache]["seiten"][key].get("robots") == "noindex":
                continue
            if f"<loc>{html.escape(bau.absolut(pfad))}</loc>" not in sitemap:
                fehler.append(f"Sitemap: {pfad} fehlt")
    elif (bau.ausgabe / "sitemap.xml").exists():
        fehler.append("Sitemap vorhanden, obwohl keine Basis-URL gesetzt ist")
    de, en = bau.sprachen["de"]["seiten"], bau.sprachen["en"]["seiten"]
    if set(de) != set(en):
        fehler.append(f"Seitenschlüssel DE/EN unterschiedlich: {sorted(set(de) ^ set(en))}")
    return fehler


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Baut die NAHX-Website.")
    ap.add_argument("--pruefen", action="store_true", help="nach dem Bau prüfen (Fehler = Exit 1)")
    ap.add_argument("--relativ", action="store_true", help="relative Links für Vorschau ohne Webserver")
    ap.add_argument("--noindex", action="store_true", help="Testbetrieb: alle Seiten noindex, robots.txt sperrt")
    ap.add_argument("--basis-url", default=None, help="Basis-URL für Canonical, hreflang, og:url, Sitemap (sonst aus site.json; leer = ohne)")
    ap.add_argument("--ausgabe", default=None, help="Zielordner (Standard: nahx/dist)")
    args = ap.parse_args(argv)
    site = lade(INHALT / "site.json")
    basis = args.basis_url if args.basis_url is not None else site.get("basis_url", "")
    bau = Bau(site, basis, args.relativ, args.noindex, Path(args.ausgabe or STANDARD_AUSGABE))
    seiten = bau.bauen()
    print(f"{len(seiten)} Seiten nach {bau.ausgabe} gebaut ({'relativ' if bau.relativ else 'site-absolut'}, Basis-URL {bau.basis_url or 'keine, Domain offen'}).")
    if args.pruefen:
        fehler = pruefen(bau, seiten)
        if fehler:
            print(f"\n{len(fehler)} Fehler:")
            for f in fehler:
                print("  -", f)
            return 1
        print("Prüfung ohne Befund: lang, h1, Überschriftenfolge, Title, Description, Alt, JSON-LD, Links, Anker" + (", Canonical, hreflang, Sitemap." if bau.basis_url else "; Canonical/hreflang/Sitemap zurückgestellt (keine Domain)."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
