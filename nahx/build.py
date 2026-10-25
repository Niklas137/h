#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baut die zweisprachige Website von NAHX Technologies aus `nahx/inhalt/*.json` nach `nahx/dist/`.

Aufruf (aus dem Repo-Wurzelverzeichnis):

    python3 nahx/build.py                     # baut nach nahx/dist/, Links site-absolut (/en/services/)
    python3 nahx/build.py --pruefen           # baut und prüft Titel, Descriptions, Überschriften,
                                              # Alt-Texte, interne Links und Anker, hreflang, Sitemap (Fehler = Exit 1)
    python3 nahx/build.py --relativ --ausgabe /tmp/vorschau
                                              # Vorschau mit relativen Links (index.html per Doppelklick)
    python3 nahx/build.py --basis-url https://nahx.de --noindex

Keine Abhängigkeiten außer Python 3.8+. Inhalte: `inhalt/site.json` (gemeinsame Daten, Sprachen,
Reihenfolge der Seiten), `inhalt/de.json` und `inhalt/en.json` (Texte je Sprache, gleiche Seitenschlüssel).
Textfelder sind HTML-Fragmente: erlaubt sind <strong>, <em>, <a>, <br>; ein nacktes „&“ wird zu „&amp;“.
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
    """HTML-Fragment aus dem Inhalt: nacktes & maskieren, Rest unverändert (erlaubte Tags)."""
    return _AMP.sub("&amp;", s)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def lade(pfad: Path) -> dict:
    with pfad.open(encoding="utf-8") as f:
        daten = json.load(f)
    return {k: v for k, v in daten.items() if not k.startswith("_")}


import math


def ring(nr: int) -> str:
    """Knoten-Ikone: Kern, Umlaufbahn und Satellit (ersetzt das frühere Zahnrad)."""
    w = [0.6, 2.7, 4.6][nr % 3]
    sx, sy = 50 + 38 * math.cos(w), 50 + 38 * math.sin(w)
    return (
        '<svg class="ring" viewBox="0 0 100 100" aria-hidden="true" focusable="false">'
        f'<g class="knoten" style="--dauer:{26 + nr * 6}s"><circle cx="50" cy="50" r="38" class="bahn"/>'
        f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="3.5" class="satellit"/></g>'
        '<circle cx="50" cy="50" r="22" class="kern"/><circle cx="50" cy="50" r="5" class="mitte"/></svg>'
    )


def woerter(text: str) -> str:
    """Zerlegt eine Überschrift in Wörter, die nacheinander einblenden (HTML-Fragment bleibt erlaubt)."""
    teile = text.split(" ")
    return " ".join(f'<span class="wort" style="--i:{i}">{w}</span>' for i, w in enumerate(teile))


class Bau:
    def __init__(self, site: dict, basis_url: str, relativ: bool, noindex: bool, ausgabe: Path, palette: str = ""):
        self.site = site
        self.palette = palette
        self.basis_url = basis_url.rstrip("/")
        self.relativ = relativ
        self.noindex = noindex
        self.ausgabe = ausgabe
        self.sprachen = {code: lade(INHALT / f"{code}.json") for code in site["sprachen"]}
        self.heute = dt.date.today().isoformat()
        self.pfade: dict[tuple[str, str], str] = {}  # (sprache, seite) -> site-absoluter Pfad
        for code, texte in self.sprachen.items():
            wurzel = site["sprachen"][code]["pfad"]
            for schluessel, seite in texte["seiten"].items():
                self.pfade[(code, schluessel)] = wurzel + seite["pfad"]

    # ------------------------------------------------------------------ Links
    def pfad(self, sprache: str, seite: str, anker: str | None = None) -> str:
        p = self.pfade[(sprache, seite)]
        return p + (f"#{anker}" if anker else "")

    def link(self, von: str, ziel: str) -> str:
        """Macht aus einem site-absoluten Ziel (/en/services/#x) je nach Modus einen relativen Link."""
        if not self.relativ or not ziel.startswith("/"):
            return ziel
        ziel_pfad, _, anker = ziel.partition("#")
        von_dir = posixpath.dirname(von) if not von.endswith("/") else von
        rel = posixpath.relpath(ziel_pfad or "/", von_dir)
        if ziel_pfad.endswith("/"):
            rel = "index.html" if rel == "." else rel + "/index.html"
        return rel + (f"#{anker}" if anker else "")

    def absolut(self, pfad: str) -> str:
        return self.basis_url + pfad

    # ------------------------------------------------------------------ Bausteine
    def kopf(self, sprache: str, seite_key: str, pfad: str) -> str:
        t = self.sprachen[sprache]
        ui = t["ui"]
        nav = []
        eintraege = [e for e in t["navigation"] if e["seite"] != "start"]
        if seite_key == "start":
            eintraege = [e for e in eintraege if e["seite"] in ("leistungen", "projekte", "kontakt")]
        for eintrag in eintraege:
            ziel = self.link(pfad, self.pfad(sprache, eintrag["seite"]))
            aktuell = ' aria-current="page"' if eintrag["seite"] == seite_key else ""
            nav.append(f'<a href="{esc(ziel)}"{aktuell}>{esc(eintrag["text"])}</a>')
        andere = [c for c in self.sprachen if c != sprache]
        sprach_links = []
        for c in andere:
            ziel = self.link(pfad, self.pfad(c, seite_key))
            name = self.site["sprachen"][c]["name"]
            sprach_links.append(f'<a class="schalter" href="{esc(ziel)}" lang="{c}" hreflang="{c}" title="{esc(name)}">{esc(self.site["sprachen"][c]["kurz"])}</a>')
        start = self.link(pfad, self.pfad(sprache, "start"))
        kontakt = self.link(pfad, self.pfad(sprache, "kontakt"))
        return f"""<a class="sprung" href="#inhalt">{esc(ui["sprung"])}</a>
<header class="kopf">
  <div class="innen kopf-innen">
    <a class="logo" href="{esc(start)}" aria-label="{esc(t["logo_alt"])}">{WORTMARKE}<span class="logo-zusatz" aria-hidden="true">Technologies</span></a>
    <nav class="nav" id="nav" aria-label="{esc(ui["fuss_navigation"])}">{"".join(nav)}</nav>
    <div class="kopf-aktionen">
      {"".join(sprach_links)}
      <button class="schalter" id="thema" type="button" aria-label="{esc(ui["thema"])}" data-auto="{esc(ui["thema_auto"])}" data-light="{esc(ui["thema_hell"])}" data-dark="{esc(ui["thema_dunkel"])}" hidden>{esc(ui["thema_auto"])}</button>
      <button class="schalter menue-schalter" type="button" aria-expanded="false" aria-controls="nav">{esc(ui["menue"])}</button>
    </div>
  </div>
</header>
<div class="fortschritt" aria-hidden="true"><span id="fortschritt"></span></div>"""

    def fuss(self, sprache: str, pfad: str) -> str:
        t = self.sprachen[sprache]
        ui = t["ui"]
        nav = "".join(f'<a href="{esc(self.link(pfad, self.pfad(sprache, e["seite"])))}">{esc(e["text"])}</a>' for e in t["navigation"])
        recht = "".join(f'<a href="{esc(self.link(pfad, self.pfad(sprache, s)))}">{esc(t["seiten"][s]["menue"])}</a>' for s in t["rechtsseiten"])
        sprachen = "".join(
            f'<a href="{esc(self.link(pfad, self.pfad(c, "start")))}" lang="{c}" hreflang="{c}">{esc(self.site["sprachen"][c]["name"])}</a>'
            for c in self.sprachen
        )
        return f"""<footer class="fuss">
  <div class="innen">
    <div class="fuss-spalten">
      <div class="marke">
        <div class="fuss-marke">{WORTMARKE}<span class="logo-zusatz">Technologies</span></div>
        <p>{esc(t["claim"])}</p>
        <p lang="{'en' if sprache == 'de' else 'de'}">{esc(t["claim_andere"])}</p>
      </div>
      <nav aria-label="{esc(ui["fuss_navigation"])}"><strong>{esc(ui["fuss_navigation"])}</strong>{nav}</nav>
      <nav aria-label="{esc(ui["fuss_recht"])}"><strong>{esc(ui["fuss_recht"])}</strong>{recht}</nav>
      <nav aria-label="{esc(ui["fuss_sprache"])}"><strong>{esc(ui["fuss_sprache"])}</strong>{sprachen}</nav>
    </div>
    <p class="fuss-klein">{esc(ui["fuss_hinweis"])}</p>
  </div>
</footer>"""

    def cta_html(self, sprache: str, pfad: str, cta: dict, klasse: str = "cta") -> str:
        ziel = self.link(pfad, self.pfad(sprache, cta["seite"], cta.get("anker")))
        return f'<a class="{klasse}" href="{esc(ziel)}">{esc(cta["text"])}</a>'

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
        if typ == "karten":
            karten = []
            ringe = a.get("id") in ("leistungen", "services")
            for nr, k in enumerate(a["karten"]):
                mehr = ""
                if k.get("link"):
                    l = k["link"]
                    mehr = f'<a class="mehr" href="{esc(self.link(pfad, self.pfad(sprache, l["seite"], l.get("anker"))))}">{esc(l["text"])}</a>'
                karten.append(f'<article class="karte reveal" style="--i:{nr}">{ring(nr) if ringe else ""}<h3>{frag(k["h3"])}</h3><p>{frag(k["text"])}</p>{mehr}</article>')
            hinweis = ""
            if a.get("hinweis") or a.get("link"):
                teile = []
                if a.get("hinweis"):
                    teile.append(frag(a["hinweis"]))
                if a.get("link"):
                    teile.append(self.cta_html(sprache, pfad, a["link"], "mehr"))
                hinweis = f'<p class="hinweis">{" ".join(teile)}</p>'
            return f'<section class="abschnitt innen"{ident}>{kopf}<div class="raster">{"".join(karten)}</div>{hinweis}</section>'
        if typ == "listen":
            karten = []
            for nr, k in enumerate(a["karten"]):
                punkte = "".join(f"<li>{frag(p)}</li>" for p in k["punkte"])
                karten.append(f'<article class="karte reveal" id="{esc(k["id"])}" style="--i:{nr}">{ring(nr)}<h2>{frag(k["h2"])}</h2><ul>{punkte}</ul></article>')
            return f'<section class="abschnitt innen"{ident}>{kopf}<div class="raster">{"".join(karten)}</div></section>'
        if typ == "schritte":
            schritte = "".join(f'<li class="reveal" style="--i:{i}"><h3>{frag(x["h3"])}</h3><p>{frag(x["text"])}</p></li>' for i, x in enumerate(a["schritte"]))
            return f'<section class="abschnitt innen"{ident}>{kopf}<div class="schritte-linie" aria-hidden="true"><span></span></div><ol class="schritte">{schritte}</ol></section>'
        if typ == "text":
            absaetze = "".join(f"<p>{frag(p)}</p>" for p in a["absaetze"])
            h2 = f'<h2>{frag(a["h2"])}</h2>' if a.get("h2") else ""
            return f'<section class="abschnitt innen"{ident}><div class="fliess">{h2}{absaetze}</div></section>'
        if typ == "band":
            hell = " band-hell" if a.get("id") in ("kontakt", "contact") else ""
            return f'<section class="band{hell}"{ident}><div class="innen reveal"><h2>{frag(a["h2"])}</h2><p>{frag(a["text"])}</p>{self.cta_html(sprache, pfad, a["cta"])}</div></section>'
        if typ == "kontakt":
            return self.kontakt(sprache, pfad, a)
        raise ValueError(f"Unbekannter Abschnittstyp: {typ}")

    def kontakt(self, sprache: str, pfad: str, a: dict) -> str:
        email = self.sprachen[sprache]["email"]
        if "@" in email:
            email_html = f'<a class="email" href="mailto:{esc(email)}">{esc(email)}</a>'
        else:
            email_html = f'<span class="platzhalter">{esc(email)}</span>'
        datenschutz = a["datenschutz"].replace("{datenschutz}", esc(self.link(pfad, self.pfad(sprache, "datenschutz"))))
        themen = "".join(f"<li>{frag(x)}</li>" for x in a["themen"])
        return f"""<section class="abschnitt innen" id="kontakt">
  <div class="kontakt-raster">
    <div class="karte email-karte reveal"><h2>{esc(a["email_label"])}</h2><p class="email-text">{frag(a["email_text"])}</p><p>{email_html}</p><p class="klein">{frag(datenschutz)}</p></div>
    <div class="karte reveal" style="--i:1"><h2>{frag(a["themen_h2"])}</h2><ul>{themen}</ul></div>
  </div>
</section>"""

    def palette_attr(self) -> str:
        return f' data-palette="{esc(self.palette)}"' if self.palette else ""

    def icons(self, pfad: str) -> str:
        l = lambda p: esc(self.link(pfad, p))
        return (f'<link rel="icon" href="{l("/assets/img/favicon.svg")}" type="image/svg+xml">\n'
                f'<link rel="icon" href="{l("/assets/img/favicon.ico")}" sizes="32x32">\n'
                f'<link rel="apple-touch-icon" href="{l("/assets/img/apple-touch-icon.png")}">')

    def saetze(self, text: str) -> list[str]:
        """Zerlegt einen Absatz in Sätze für die Schreibmaschine."""
        teile = [x.strip() for x in re.split(r"(?<=[.!?])\s+", text) if x.strip()]
        return teile or [text]

    def tippe(self, zeilen: list[str], klasse: str = "") -> str:
        return "".join(f'<span class="tippe {klasse}" data-text="{esc(z)}">{esc(z)}</span>' for z in zeilen)

    def start_main(self, sprache: str, pfad: str) -> str:
        t = self.sprachen[sprache]
        s = t["seiten"]["start"]
        ui = t["ui"]
        karten = [a for a in s["abschnitte"] if a["typ"] == "karten"]
        leistungen, projekte = karten[0], karten[1]
        schritte = next(a for a in s["abschnitte"] if a["typ"] == "schritte")
        band = next(a for a in s["abschnitte"] if a["typ"] == "band")
        email = t["email"]
        email_html = f'<a class="email" href="mailto:{esc(email)}">{esc(email)}</a>' if "@" in email else f'<span class="platzhalter">{esc(email)}</span>'
        ringe = "".join(
            f'<li class="ringkachel" style="--i:{i}"><span class="ringbild">{ring(i)}</span><h3>{frag(k["h3"])}</h3><p>{frag(k["text"])}</p></li>'
            for i, k in enumerate(leistungen["karten"])
        )
        schritt_html = "".join(
            f'<li style="--i:{i}"><span class="nr">0{i + 1}</span><h3>{frag(x["h3"])}</h3><p class="tippe" data-text="{esc(x["text"])}">{esc(x["text"])}</p></li>'
            for i, x in enumerate(schritte["schritte"])
        )
        projekt_html = "".join(
            f'<li style="--i:{i}"><h3 class="tippe" data-text="{esc(k["h3"])}">{esc(k["h3"])}</h3><p>{frag(k["text"])}</p></li>'
            for i, k in enumerate(projekte["karten"])
        )
        weiter = ui.get("weiter", "Scrollen")
        return f"""<canvas id="welt" aria-hidden="true"></canvas>
<main id="inhalt" class="start">
  <section class="szene szene-held" data-zoom="1.1" data-x="0.5" data-y="0.5" data-ordnung="0.05">
    <div class="szene-innen">
      <p class="kicker tippe" data-text="{esc(s["kicker"])}">{esc(s["kicker"])}</p>
      <h1>{self.tippe(self.saetze(s["h1"]), "zeile")}</h1>
      <p class="weiter" aria-hidden="true">{esc(weiter)}<span class="pfeil"></span></p>
    </div>
  </section>
  <section class="szene szene-tunnel" data-zoom="1.3" data-x="0.5" data-y="0.45" data-ordnung="0.55" data-rot="0.08">
    <div class="szene-innen"><p class="satz">{self.tippe(self.saetze(s["einleitung"]))}</p></div>
  </section>
  <section class="szene szene-ringe" id="{esc(leistungen.get("id", "leistungen"))}" data-zoom="1" data-x="0.5" data-y="0.5" data-ordnung="0.9" data-hubs="1">
    <div class="szene-innen breit">
      <h2 class="tippe" data-text="{esc(leistungen["h2"])}">{esc(leistungen["h2"])}</h2>
      <ul class="ringe">{ringe}</ul>
      <p class="mehr-zeile"><a href="{esc(self.link(pfad, self.pfad(sprache, "leistungen")))}">{esc(t["seiten"]["leistungen"]["menue"])} →</a></p>
    </div>
  </section>
  <section class="szene szene-ablauf" id="{esc(schritte.get("id", "ablauf"))}" data-zoom="1.2" data-x="0.5" data-y="0.5" data-ordnung="1" data-fluss="1">
    <div class="szene-innen breit">
      <h2 class="tippe" data-text="{esc(schritte["h2"])}">{esc(schritte["h2"])}</h2>
      <p class="satz klein-satz">{frag(schritte["text"])}</p>
      <ol class="ablauf">{schritt_html}</ol>
    </div>
  </section>
  <section class="szene szene-projekte" id="{esc(projekte.get("id", "projekte"))}" data-zoom="1.6" data-x="0.2" data-y="0.5" data-ordnung="1" data-rot="0.2">
    <div class="szene-innen breit">
      <h2 class="tippe" data-text="{esc(projekte["h2"])}">{esc(projekte["h2"])}</h2>
      <ul class="projekte">{projekt_html}</ul>
      <p class="mehr-zeile">{frag(projekte.get("hinweis", ""))} <a href="{esc(self.link(pfad, self.pfad(sprache, "projekte")))}">{esc(projekte["link"]["text"])} →</a></p>
    </div>
  </section>
  <section class="szene szene-kontakt" id="{esc(band.get("id", "kontakt"))}" data-zoom="1" data-x="0.5" data-y="0.5" data-ordnung="1" data-hell="1">
    <div class="szene-innen">
      <h2 class="tippe" data-text="{esc(band["h2"])}">{esc(band["h2"])}</h2>
      <p class="satz">{frag(band["text"])}</p>
      <p class="kontakt-zeile">{email_html}</p>
      <p class="mehr-zeile"><a class="cta-linie" href="{esc(self.link(pfad, self.pfad(sprache, "kontakt")))}">{esc(band["cta"]["text"])} →</a></p>
    </div>
  </section>
</main>"""

    # ------------------------------------------------------------------ Seite
    def seite_html(self, sprache: str, seite_key: str) -> tuple[str, str]:
        t = self.sprachen[sprache]
        s = t["seiten"][seite_key]
        pfad = self.pfade[(sprache, seite_key)]
        ui = t["ui"]
        robots = "noindex, nofollow" if (self.noindex or s.get("robots") == "noindex") else "index, follow"
        alternates = "".join(
            f'<link rel="alternate" hreflang="{c}" href="{esc(self.absolut(self.pfade[(c, seite_key)]))}">' for c in self.sprachen
        )
        alternates += f'<link rel="alternate" hreflang="x-default" href="{esc(self.absolut(self.pfade[("de", seite_key)]))}">'
        css = self.link(pfad, "/assets/site.css")
        fonts = "".join(
            f'<link rel="preload" href="{esc(self.link(pfad, "/assets/fonts/" + f))}" as="font" type="font/woff2" crossorigin>'
            for f in self.site["fonts_vorladen"]
        )
        hauptklasse = s.get("typ", "seite")
        cta = ""
        if s.get("cta"):
            cta = '<div class="cta-reihe reveal">' + self.cta_html(sprache, pfad, s["cta"]["primaer"]) + self.cta_html(sprache, pfad, s["cta"]["sekundaer"], "cta-zweit") + "</div>"
        text = f'<p class="abschnitt-text">{frag(s["text"])}</p>' if s.get("text") else ""
        warn = f'<p class="warnung">{esc(ui["platzhalter_hinweis"])}</p>' if s.get("platzhalter") else ""
        abschnitte = "".join(self.abschnitt(sprache, pfad, a) for a in s["abschnitte"])
        if seite_key == "start":
            hauptteil = self.start_main(sprache, pfad)
            welt = f'<script src="{esc(self.link(pfad, "/assets/welt.js"))}" defer></script>'
        else:
            welt = f'<script src="{esc(self.link(pfad, "/assets/welt.js"))}" defer></script>'
            hauptteil = f"""<canvas id="welt" aria-hidden="true"></canvas>
<main id="inhalt" class="{hauptklasse}">
  <section class="held">
    <div class="innen held-innen">
      <p class="kicker tipp" data-text="{esc(s["kicker"])}">{esc(s["kicker"])}</p>
      <h1>{woerter(frag(s["h1"]))}</h1>
      <p class="einleitung reveal">{frag(s["einleitung"])}</p>
      {text}{warn}{cta}
    </div>
  </section>
  {abschnitte}
</main>"""
        json_ld = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": s["title"],
            "description": s["description"],
            "url": self.absolut(pfad),
            "inLanguage": sprache,
            "isPartOf": {"@type": "WebSite", "name": self.site["name"], "url": self.absolut("/")},
            "about": {"@type": "ProfessionalService", "name": self.site["name"], "slogan": t["claim"]},
        }
        html_ = f"""<!doctype html>
<html lang="{sprache}"{self.palette_attr()}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(s["title"])}</title>
<meta name="description" content="{esc(s["description"])}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{esc(self.absolut(pfad))}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(self.site["name"])}">
<meta property="og:locale" content="{esc(self.site["sprachen"][sprache]["locale"])}">
<meta property="og:title" content="{esc(s["title"])}">
<meta property="og:description" content="{esc(s["description"])}">
<meta property="og:url" content="{esc(self.absolut(pfad))}">
<meta property="og:image" content="{esc(self.absolut(self.site["og_bild"]))}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(t["og_bild_alt"])}">
<meta name="twitter:card" content="summary_large_image">
{self.icons(pfad)}
{fonts}
<link rel="stylesheet" href="{esc(css)}">
<script>{KOPF_SCRIPT}</script>
<script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False).replace("</", "<\\/")}</script>
</head>
<body class="{"seite-start" if seite_key == "start" else "seite-unter"}">
{self.kopf(sprache, seite_key, pfad)}
{hauptteil}
{self.fuss(sprache, pfad)}
<script>{FUSS_SCRIPT}</script>{welt}
</body>
</html>
"""
        return pfad, html_

    def fehlerseite_html(self, sprache: str) -> tuple[str, str]:
        t = self.sprachen[sprache]
        f = t["fehlerseite"]
        pfad = self.site["sprachen"][sprache]["pfad"] + "404.html"
        css = self.link(pfad, "/assets/site.css")
        html_ = f"""<!doctype html>
<html lang="{sprache}"{self.palette_attr()}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(f["title"])}</title>
<meta name="robots" content="noindex, nofollow">
{self.icons(pfad)}
<link rel="stylesheet" href="{esc(css)}">
<script>{KOPF_SCRIPT}</script>
</head>
<body>
{self.kopf(sprache, "start", pfad).replace(' aria-current="page"', '')}
<main id="inhalt" class="fehler">
  <section class="held"><div class="innen held-innen">
    <p class="kicker">404</p>
    <h1>{esc(f["h1"])}</h1>
    <p class="einleitung">{esc(f["text"])}</p>
    <div class="cta-reihe">{self.cta_html(sprache, pfad, f["cta"])}</div>
  </div></section>
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
        shutil.copytree(ASSETS, self.ausgabe / "assets")
        seiten: list[tuple[str, Path]] = []
        for sprache in self.sprachen:
            for seite_key in self.site["seiten"]:
                pfad, html_ = self.seite_html(sprache, seite_key)
                seiten.append((pfad, self.schreibe(pfad, html_)))
            pfad, html_ = self.fehlerseite_html(sprache)
            seiten.append((pfad, self.schreibe(pfad, html_)))
        # 404 auf Wurzelebene = deutsche Fehlerseite (GitHub Pages, Netlify, Cloudflare Pages lesen /404.html)
        if self.noindex:
            (self.ausgabe / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
        else:
            (self.ausgabe / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {self.absolut('/sitemap.xml')}\n", encoding="utf-8")
            urls = []
            for seite_key in self.site["seiten"]:
                for sprache in self.sprachen:
                    s = self.sprachen[sprache]["seiten"][seite_key]
                    if s.get("robots") == "noindex":
                        continue
                    alt = "".join(
                        f'<xhtml:link rel="alternate" hreflang="{c}" href="{esc(self.absolut(self.pfade[(c, seite_key)]))}"/>' for c in self.sprachen
                    )
                    urls.append(f"<url><loc>{esc(self.absolut(self.pfade[(sprache, seite_key)]))}</loc>{alt}<lastmod>{self.heute}</lastmod></url>")
            sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                       'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n")
            (self.ausgabe / "sitemap.xml").write_text(sitemap, encoding="utf-8")
        return seiten


WORTMARKE = (
    '<svg class="wortmarke" viewBox="-8 0 300 100" aria-hidden="true" focusable="false">'
    '<g fill="none" stroke="currentColor" stroke-width="14" stroke-linecap="square" stroke-linejoin="miter">'
    '<path class="zug" style="--i:0" d="M7 90V10l42 80V10"/><path class="zug" style="--i:2" d="M159 10v80M201 10v80M159 50h42"/><path class="zug" style="--i:3" d="M228 10l56 80M284 10l-56 80"/></g>'
    '<g fill="none" stroke="var(--accent-2,#22B8E0)" stroke-width="14" stroke-linecap="square" stroke-linejoin="miter"><path class="zug" style="--i:1" d="M76 90l28-80 28 80M90 62h28"/></g></svg>'
)

KOPF_SCRIPT = (
    "(function(){var d=document.documentElement;d.classList.add('js');"
    "try{var t=localStorage.getItem('nahx-thema');if(t==='dark'||t==='light'){d.setAttribute('data-theme',t);}}catch(e){}})();"
)
FUSS_SCRIPT = (
    "(function(){var d=document.documentElement;var b=document.getElementById('thema');"
    "var m=document.querySelector('.menue-schalter');var n=document.getElementById('nav');"
    "var L=b?{a:b.getAttribute('data-auto')||b.textContent,l:b.getAttribute('data-light'),k:b.getAttribute('data-dark')}:null;"
    "function label(){if(!b){return;}var t=d.getAttribute('data-theme');b.textContent=t==='dark'?L.k:t==='light'?L.l:L.a;}"
    "if(b){b.hidden=false;label();b.addEventListener('click',function(){var t=d.getAttribute('data-theme');"
    "var x=t==='dark'?'light':t==='light'?null:'dark';if(x){d.setAttribute('data-theme',x);}else{d.removeAttribute('data-theme');}"
    "try{if(x){localStorage.setItem('nahx-thema',x);}else{localStorage.removeItem('nahx-thema');}}catch(e){}label();});}"
    "if(m&&n){m.addEventListener('click',function(){var o=n.classList.toggle('offen');m.setAttribute('aria-expanded',o?'true':'false');});}"
    "var ruhig=window.matchMedia('(prefers-reduced-motion: reduce)').matches;"
    "var R=document.querySelectorAll('.reveal');"
    "if(ruhig||!('IntersectionObserver' in window)){R.forEach(function(e){e.classList.add('sichtbar');});}"
    "else{var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('sichtbar');io.unobserve(x.target);}});},{rootMargin:'0px 0px -10% 0px',threshold:0.15});R.forEach(function(e){io.observe(e);});}"
    "var T=document.querySelector('.tipp');"
    "if(T&&!ruhig){var txt=T.getAttribute('data-text');T.textContent='';T.classList.add('tippt');var i=0;"
    "(function tick(){if(i<=txt.length){T.textContent=txt.slice(0,i);i++;setTimeout(tick,i<3?400:28);}else{T.classList.remove('tippt');T.classList.add('fertig');}})();}"
    "var F=document.getElementById('fortschritt');"
    "function lauf(){var h=document.documentElement;var max=h.scrollHeight-h.clientHeight;var y=max>0?h.scrollTop/max:0;"
    "if(F){F.style.transform='scaleX('+y+')';}h.style.setProperty('--scroll',String(h.scrollTop));}"
    "if(!ruhig){window.addEventListener('scroll',lauf,{passive:true});}lauf();})();"
)


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
        self._in = None
        self._puffer = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
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
            if not s.canonical:
                fehler.append(f"{pfad}: Canonical fehlt")
            if s.json_ld != 1:
                fehler.append(f"{pfad}: {s.json_ld} JSON-LD-Blöcke (erwartet 1)")
            erwartet = set(bau.sprachen) | {"x-default"}
            if set(s.hreflang) != erwartet:
                fehler.append(f"{pfad}: hreflang {sorted(s.hreflang)} statt {sorted(erwartet)}")
        if s.bilder_ohne_alt:
            fehler.append(f"{pfad}: {s.bilder_ohne_alt} Bild(er) ohne alt")
        for href in s.links:
            if href.startswith(("http", "mailto:", "tel:")):
                continue
            ziel, _, anker = href.partition("#")
            if bau.relativ:
                ziel_abs = posixpath.normpath(posixpath.join(posixpath.dirname(pfad) if not pfad.endswith("/") else pfad, ziel)) if ziel else pfad
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
    if not bau.noindex:
        sitemap = (bau.ausgabe / "sitemap.xml").read_text(encoding="utf-8")
        for pfad in alle:
            s = None
            for sprache in bau.sprachen:
                for key, p in bau.pfade.items():
                    if p == pfad and key[0] == sprache:
                        s = bau.sprachen[sprache]["seiten"][key[1]]
            if pfad.endswith("404.html") or (s and s.get("robots") == "noindex"):
                continue
            if f"<loc>{html.escape(bau.absolut(pfad))}</loc>" not in sitemap:
                fehler.append(f"Sitemap: {pfad} fehlt")
    # Texte beider Sprachen müssen dieselben Seiten und Anker-IDs der Leistungen tragen
    de, en = bau.sprachen["de"]["seiten"], bau.sprachen["en"]["seiten"]
    if set(de) != set(en):
        fehler.append(f"Seitenschlüssel DE/EN unterschiedlich: {sorted(set(de) ^ set(en))}")
    return fehler


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Baut die NAHX-Website.")
    ap.add_argument("--pruefen", action="store_true", help="nach dem Bau prüfen (Fehler = Exit 1)")
    ap.add_argument("--relativ", action="store_true", help="relative Links für Vorschau ohne Webserver")
    ap.add_argument("--noindex", action="store_true", help="Testbetrieb: alle Seiten noindex, robots.txt sperrt, keine Sitemap")
    ap.add_argument("--basis-url", default=None, help="Basis-URL für Canonical, hreflang, Sitemap")
    ap.add_argument("--ausgabe", default=None, help="Zielordner (Standard: nahx/dist)")
    ap.add_argument("--palette", default="", help="Farbwelt: bernstein, violett, lime, indigo (leer = Cyan)")
    args = ap.parse_args(argv)

    site = lade(INHALT / "site.json")
    bau = Bau(site, args.basis_url or site["basis_url"], args.relativ, args.noindex, Path(args.ausgabe or STANDARD_AUSGABE), args.palette)
    seiten = bau.bauen()
    print(f"{len(seiten)} Seiten nach {bau.ausgabe} gebaut ({'relativ' if bau.relativ else 'site-absolut'}, Basis {bau.basis_url}).")
    if args.pruefen:
        fehler = pruefen(bau, seiten)
        if fehler:
            print(f"\n{len(fehler)} Fehler:")
            for f in fehler:
                print("  -", f)
            return 1
        print("Prüfung ohne Befund: h1, Überschriftenfolge, Title, Description, Alt, Canonical, hreflang, JSON-LD, Links, Anker, Sitemap.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
