#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baut die Website von FSH-Documentation aus `website/inhalt/*.json` nach `website/dist/`.

Aufruf (aus dem Repo-Wurzelverzeichnis):

    python3 website/build.py                    # baut nach website/dist/, Links site-absolut (/agb/)
    python3 website/build.py --pruefen          # baut und prüft Titel, Descriptions, Überschriften,
                                                # Alt-Texte, interne Links, JSON-LD (Fehler = Exit 1)
    python3 website/build.py --relativ --ausgabe /tmp/vorschau
                                                # Vorschau mit relativen Links (index.html per Doppelklick)
    python3 website/build.py --basis-url https://fsh-documentation.de

Keine Abhängigkeiten außer Python 3.8+. Inhalte: `inhalt/site.json` (Firmendaten, Navigation,
Reihenfolge der Seiten) und je Seite eine JSON-Datei (siehe README.md, Abschnitt „Inhalte pflegen").
Textfelder sind HTML-Fragmente: erlaubt sind <strong>, <em>, <a>, <br>, <code>; ein nacktes „&"
wird automatisch zu „&amp;".
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import posixpath
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

HIER = Path(__file__).resolve().parent
INHALT = HIER / "inhalt"
ASSETS = HIER / "assets"
STANDARD_AUSGABE = HIER / "dist"

SPRACHEN_BCP47 = ["de", "en", "uk", "ru"]


# ----------------------------------------------------------------------------- Hilfen
def esc(s) -> str:
    """Text für Attribute und reinen Text (Title, Description, Alt) escapen."""
    return html.escape("" if s is None else str(s), quote=True)


_AMP = re.compile(r"&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#[0-9]+|#x[0-9a-fA-F]+);)")


def frag(s) -> str:
    """Inhaltstext als HTML-Fragment übernehmen; ein nacktes & wird zu &amp;."""
    return _AMP.sub("&amp;", "" if s is None else str(s))


def lade_json(pfad: Path):
    with pfad.open(encoding="utf-8") as f:
        return json.load(f)


def git_datum(pfad: Path) -> str:
    """Datum des letzten Commits der Datei (JJJJ-MM-TT), sonst heute."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(pfad)],
            capture_output=True, text=True, cwd=str(HIER), timeout=10,
        )
        d = out.stdout.strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            return d
    except Exception:
        pass
    return dt.date.today().isoformat()


def json_script(daten) -> str:
    text = json.dumps(daten, ensure_ascii=False, indent=1)
    return text.replace("</", "<\\/")


# ----------------------------------------------------------------------------- Datenmodell
class Seite:
    def __init__(self, name: str, daten: dict, quelle: Path | None):
        self.name = name
        self.daten = daten
        self.quelle = quelle
        self.pfad: str = daten["pfad"]
        self.datei = self.pfad + "index.html" if self.pfad.endswith("/") else self.pfad
        self.typ: str = daten.get("typ", "leistung")

    @property
    def menue(self) -> str:
        return self.daten.get("menue", self.daten.get("h1", self.name))

    @property
    def hat_kontakt(self) -> bool:
        return bool(self.daten.get("kontakt"))


class Bau:
    def __init__(self, site: dict, seiten: list[Seite], ausgabe: Path, modus: str, basis: str, noindex: bool = False):
        self.site = site
        self.seiten = seiten
        self.ausgabe = ausgabe
        self.modus = modus  # "absolut" | "relativ"
        self.basis = basis.rstrip("/")
        self.noindex = noindex  # Testbetrieb: keine Seite indexieren
        self.nach_pfad = {s.pfad: s for s in seiten}
        self.css_version = ""
        self.heute = dt.date.today().isoformat()

    # Link-Ziele: site-absolute Pfade (/agb/, /#kontakt, /assets/…) werden je nach Modus umgeschrieben.
    def href(self, ziel: str, aktuell: Seite) -> str:
        if not ziel or not ziel.startswith("/"):
            return ziel
        if self.modus == "absolut":
            return ziel
        pfad, _, anker = ziel.partition("#")
        if pfad.endswith("/"):
            pfad += "index.html"
        rel = posixpath.relpath(pfad, posixpath.dirname(aktuell.datei))
        return rel + ("#" + anker if anker else "")

    def url(self, pfad: str) -> str:
        return self.basis + pfad

    def seite_zu(self, pfad: str) -> Seite:
        rein = pfad.partition("#")[0]
        if rein not in self.nach_pfad:
            raise SystemExit(f"Fehler: Link auf unbekannte Seite {pfad!r}")
        return self.nach_pfad[rein]


# ----------------------------------------------------------------------------- Bausteine
def cta_link(bau: Bau, seite: Seite, cta: dict, klasse: str) -> str:
    ziel = cta["ziel"]
    if ziel == "tel":
        ziel = "tel:" + bau.site["telefon_link"]
    elif ziel == "mail":
        ziel = "mailto:" + bau.site["email"]
    elif ziel == "#kontakt" and not seite.hat_kontakt:
        ziel = "/#kontakt"
    return f'<a class="{klasse}" href="{esc(bau.href(ziel, seite))}">{frag(cta["text"])}</a>'


def kopf(bau: Bau, seite: Seite) -> str:
    site = bau.site
    links = []
    for n in site["navigation"]:
        ziel = n["ziel"]
        if ziel.startswith("#") and not seite.hat_kontakt:
            ziel = "/" + ziel
        aktuell = ' aria-current="page"' if ziel == seite.pfad else ""
        links.append(f'<a href="{esc(bau.href(ziel, seite))}"{aktuell}>{esc(n["text"])}</a>')
    logo = bau.href("/assets/img/logo.png", seite)
    return f"""<header class="kopf">
  <div class="innen kopf-innen">
    <a class="logo" href="{esc(bau.href('/', seite))}" aria-label="{esc(site['name'])}, zur Startseite"><img src="{esc(logo)}" alt="{esc(site['logo_alt'])}" width="285" height="88" decoding="async"></a>
    <nav class="nav" id="hauptnav" aria-label="Hauptnavigation">{''.join(links)}</nav>
    <div class="kopf-aktionen">
      <a class="cta kopf-cta" href="{esc(bau.href('#kontakt' if seite.hat_kontakt else '/#kontakt', seite))}">{esc(site['cta_kopf'])}</a>
      <button class="schalter" type="button" id="thema-schalter" aria-label="Farbschema wechseln" title="Farbschema: Auto, Dunkel oder Hell">Auto</button>
      <button class="schalter menue-schalter" type="button" id="menue-schalter" aria-expanded="false" aria-controls="hauptnav" aria-label="Menü öffnen oder schließen"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    </div>
  </div>
</header>"""


def pfadnavigation(bau: Bau, seite: Seite) -> str:
    if seite.typ == "start":
        return ""
    teile = [f'<a href="{esc(bau.href("/", seite))}">Start</a>']
    if seite.typ == "leistung":
        teile.append(f'<a href="{esc(bau.href("/#leistungen", seite))}">Leistungen</a>')
    teile.append(f'<span aria-current="page">{esc(seite.menue)}</span>')
    trenner = ' <span aria-hidden="true">›</span> '
    return f'<nav class="innen pfad" aria-label="Pfad">{trenner.join(teile)}</nav>'


def held(bau: Bau, seite: Seite) -> str:
    d = seite.daten
    site = bau.site
    cta = d["cta"] if "cta" in d else site["cta_standard"]
    teile = [f'<p class="kicker">{frag(d["kicker"])}</p>' if d.get("kicker") else "",
             f'<h1>{frag(d["h1"])}</h1>',
             f'<p class="einleitung">{frag(d["einleitung"])}</p>' if d.get("einleitung") else ""]
    if cta:
        knoepfe = cta_link(bau, seite, cta["primaer"], "cta")
        if cta.get("sekundaer"):
            knoepfe += cta_link(bau, seite, cta["sekundaer"], "cta-zweit")
        teile.append(f'<div class="cta-reihe">{knoepfe}</div>')
        if seite.typ in ("start", "leistung", "region"):
            teile.append(f'<p class="hinweis muted">{frag(site["erstreaktion_kurz"])}</p>')
    karte = ""
    sk = d.get("seitenkarte")
    if sk:
        inhalt = [f'<p class="karte-kicker">{frag(sk["kicker"])}</p>' if sk.get("kicker") else ""]
        if sk.get("text"):
            inhalt.append(f"<p>{frag(sk['text'])}</p>")
        for a in sk.get("absaetze", []):
            inhalt.append(f"<p>{frag(a)}</p>")
        if sk.get("chips"):
            inhalt.append('<ul class="chips" aria-label="Normen">' + "".join(f'<li class="chip">{frag(c)}</li>' for c in sk["chips"]) + "</ul>")
        if sk.get("hinweis"):
            inhalt.append(f'<p class="muted klein">{frag(sk["hinweis"])}</p>')
        karte = f'<aside class="karte held-karte" aria-label="{esc(sk.get("kicker", "Hinweis"))}">{"".join(inhalt)}</aside>'
    return f'<section class="innen held{" held-ohne-karte" if not karte else ""}"><div class="held-text">{"".join(teile)}</div>{karte}</section>'


def abschnitt_kopf(a: dict) -> str:
    if not a.get("h2"):
        return ""
    text = f'<p class="muted abschnitt-text">{frag(a["text"])}</p>' if a.get("text") else ""
    return f'<div class="abschnitt-kopf"><h2>{frag(a["h2"])}</h2>{text}</div>'


def inhalt_bloecke(bau: Bau, seite: Seite, items: list, site_varianten: dict | None = None) -> str:
    """Geordnete Inhaltsbausteine: String = Absatz, {"liste": […]}, {"h3": …}, {"links": […]}, {"variante": …}."""
    out = []
    for it in items:
        if isinstance(it, str):
            out.append(f"<p>{frag(it)}</p>")
        elif "liste" in it:
            out.append("<ul>" + "".join(f"<li>{frag(x)}</li>" for x in it["liste"]) + "</ul>")
        elif "nummern" in it:
            out.append("<ol>" + "".join(f"<li>{frag(x)}</li>" for x in it["nummern"]) + "</ol>")
        elif "h3" in it:
            out.append(f"<h3>{frag(it['h3'])}</h3>")
        elif "links" in it:
            out.append('<p class="links-liste">' + "".join(
                f'<a class="link-pfeil" href="{esc(bau.href(l["ziel"], seite))}">{frag(l["text"])}</a>' for l in it["links"]) + "</p>")
        elif "variante" in it:
            if not site_varianten:
                raise SystemExit(f"Fehler: Variante {it['variante']!r} ohne Variantendaten in {seite.name}")
            wahl = bau.site.get("hosting", "strato")
            block = site_varianten.get(wahl, {}).get(it["variante"])
            if block is None:
                raise SystemExit(f"Fehler: Variante {it['variante']!r} für hosting={wahl!r} fehlt in {seite.name}")
            out.append(inhalt_bloecke(bau, seite, block, site_varianten))
        else:
            raise SystemExit(f"Fehler: unbekannter Inhaltsbaustein {it!r} in {seite.name}")
    return "".join(out)


def karten_raster(bau: Bau, seite: Seite, karten: list, spalten: int = 3) -> str:
    teile = []
    for k in karten:
        titel = f"<h3>{frag(k['h3'])}</h3>"
        text = f'<p class="muted">{frag(k["text"])}</p>' if k.get("text") else ""
        if k.get("link"):
            mehr = frag(k.get("linktext", "Mehr erfahren"))
            teile.append(f'<a class="karte karte-link" href="{esc(bau.href(k["link"], seite))}">{titel}{text}<span class="mehr">{mehr} <span aria-hidden="true">→</span></span></a>')
        else:
            teile.append(f'<div class="karte">{titel}{text}</div>')
    klasse = "raster raster-4" if spalten == 4 else ("raster raster-2" if spalten == 2 else "raster")
    return f'<div class="{klasse}">{"".join(teile)}</div>'


def abschnitt(bau: Bau, seite: Seite, a: dict, varianten: dict | None) -> str:
    art = a.get("art", "text")
    ident = f' id="{esc(a["id"])}"' if a.get("id") else ""
    site = bau.site

    if art == "zahlen":
        z = "".join(f'<div class="zahl-block"><span class="zahl">{frag(x["wert"])}</span><span class="zahl-text">{frag(x["text"])}</span></div>' for x in a["zahlen"])
        return f'<section class="band band-zahlen"{ident}><div class="innen zahlen">{z}</div></section>'

    if art == "band":
        punkte = "".join(f"<p><strong>{frag(p['titel'])}</strong>: {frag(p['text'])}</p>" for p in a["punkte"])
        hinweis = f'<p class="band-hinweis">{frag(a["hinweis"])}</p>' if a.get("hinweis") else ""
        return f'<section class="band"{ident}><div class="innen band-raster"><h2>{frag(a["h2"])}</h2><div class="punkte">{punkte}{hinweis}</div></div></section>'

    if art == "karten":
        return f'<section class="innen abschnitt"{ident}>{abschnitt_kopf(a)}{karten_raster(bau, seite, a["karten"], a.get("spalten", 3))}</section>'

    if art == "schritte":
        schritte = a.get("schritte") or site["ablauf"]
        s = "".join(
            f'<li class="karte schritt"><span class="schritt-nr" aria-hidden="true">{i}</span><h3>{frag(x["h3"])}</h3><p class="muted">{frag(x["text"])}</p></li>'
            for i, x in enumerate(schritte, 1))
        return f'<section class="innen abschnitt"{ident}>{abschnitt_kopf(a)}<ol class="raster raster-4 schritte">{s}</ol></section>'

    if art == "fragen":
        f = "".join(f'<div class="karte"><h3>{frag(x["frage"])}</h3><p class="muted">{frag(x["antwort"])}</p></div>' for x in a["fragen"])
        return f'<section class="innen abschnitt"{ident}>{abschnitt_kopf(a)}<div class="raster raster-2">{f}</div></section>'

    if art == "referenzen":
        r = "".join(
            f'<div class="karte"><h3>{frag(x["h3"])}</h3><p><strong>Leistung:</strong> {frag(x["leistung"])}</p><p><strong>Ergebnis:</strong> {frag(x["ergebnis"])}</p></div>'
            for x in a["referenzen"])
        hinweis = f'<p class="muted referenz-hinweis">{frag(a["hinweis"])}</p>' if a.get("hinweis") else ""
        return f'<section class="innen abschnitt"{ident}>{abschnitt_kopf(a)}<div class="raster">{r}</div>{hinweis}</section>'

    if art == "ueber":
        b = a["bild"]
        quellen = f'<source srcset="{esc(bau.href(b["webp"], seite))}" type="image/webp">' if b.get("webp") else ""
        bild = f'<picture>{quellen}<img src="{esc(bau.href(b["src"], seite))}" alt="{esc(b["alt"])}" width="{b["breite"]}" height="{b["hoehe"]}" loading="lazy" decoding="async"></picture>'
        figur = f'<figure class="portraet">{bild}<figcaption>{frag(a["bildunterschrift"])}</figcaption></figure>' if a.get("bildunterschrift") else bild
        absaetze = "".join(f"<p>{frag(x)}</p>" for x in a.get("absaetze", []))
        chips = ('<ul class="chips" aria-label="Schwerpunkte">' + "".join(f'<li class="chip">{frag(c)}</li>' for c in a["chips"]) + "</ul>") if a.get("chips") else ""
        return f'<section class="innen abschnitt ueber"{ident}>{figur}<div class="ueber-text"><h2>{frag(a["h2"])}</h2>{absaetze}{chips}</div></section>'

    if art == "bild":
        b = a["bild"]
        quellen = ""
        if b.get("webp"):
            srcset = esc(bau.href(b["webp"], seite)) + f' {b["breite"]}w'
            if b.get("webp_klein"):
                srcset = esc(bau.href(b["webp_klein"], seite)) + f' {b["breite_klein"]}w, ' + srcset
            quellen = f'<source srcset="{srcset}" sizes="(min-width: 1180px) 1068px, 100vw" type="image/webp">'
        bild = f'<picture>{quellen}<img src="{esc(bau.href(b["src"], seite))}" alt="{esc(b["alt"])}" width="{b["breite"]}" height="{b["hoehe"]}" loading="lazy" decoding="async"></picture>'
        return f'<section class="innen bild-breit"{ident}>{bild}</section>'

    if art == "verwandt":
        karten = []
        for pfad in a["seiten"]:
            z = bau.seite_zu(pfad)
            karten.append({"h3": z.menue, "text": z.daten.get("kurz", ""), "link": pfad, "linktext": "Zur Leistung"})
        kopf_ = abschnitt_kopf({"h2": a.get("h2", "Verwandte Leistungen"), "text": a.get("text")})
        return f'<section class="innen abschnitt"{ident}>{kopf_}{karten_raster(bau, seite, karten, a.get("spalten", 3))}</section>'

    if art == "text":
        inhalt = inhalt_bloecke(bau, seite, a.get("inhalt", []), varianten)
        return f'<section class="innen abschnitt text-abschnitt"{ident}>{abschnitt_kopf(a)}<div class="fliess">{inhalt}</div></section>'

    raise SystemExit(f"Fehler: unbekannte Abschnittsart {art!r} in {seite.name}")


def kontakt_abschnitt(bau: Bau, seite: Seite) -> str:
    k = seite.daten.get("kontakt")
    if not k:
        return ""
    site = bau.site
    betreff = html.escape(k.get("betreff", "Anfrage"), quote=True).replace(" ", "%20")
    mail = f'<a class="cta" href="mailto:{esc(site["email"])}?subject={betreff}">E-Mail schreiben</a>'
    tel = f'<a class="cta-zweit" href="tel:{esc(site["telefon_link"])}">{esc(site["telefon"])}</a>'
    adr = site["adresse"]
    return f"""<section class="innen abschnitt" id="kontakt">
  <div class="karte kontakt-karte">
    <div class="kontakt-text"><h2>{frag(k['h2'])}</h2><p>{frag(k['text'])}</p><div class="cta-reihe">{mail}{tel}</div></div>
    <address class="adresse"><strong>{esc(site['firma'])}</strong><span>{esc(adr['strasse'])}<br>{esc(adr['plz'])} {esc(adr['ort'])}, {esc(adr['land'])}</span><a href="mailto:{esc(site['email'])}">{esc(site['email'])}</a><a href="tel:{esc(site['telefon_link'])}">{esc(site['telefon'])}</a><span class="muted">Sprachen: {esc(site['sprachen'])}</span></address>
  </div>
</section>"""


def fuss(bau: Bau, seite: Seite) -> str:
    site = bau.site
    adr = site["adresse"]
    leistungen = "".join(f'<a href="{esc(bau.href(p, seite))}">{esc(bau.seite_zu(p).menue)}</a>' for p in site["leistungsseiten"])
    recht = "".join(f'<a href="{esc(bau.href(p, seite))}">{esc(bau.seite_zu(p).menue)}</a>' for p in site["rechtsseiten"])
    profile = "".join(f'<a href="{esc(p["url"])}" rel="me noopener">{esc(p["text"])}</a>' for p in site.get("profile", []))
    profile_block = f'<nav aria-label="Profile"><strong>Profile</strong>{profile}</nav>' if profile else ""
    jahr = bau.heute[:4]
    return f"""<footer class="fuss">
  <div class="innen">
    <div class="fuss-spalten">
      <address class="adresse"><strong>{esc(site['firma'])}</strong><span>{esc(adr['strasse'])}<br>{esc(adr['plz'])} {esc(adr['ort'])}, {esc(adr['land'])}</span><a href="tel:{esc(site['telefon_link'])}">{esc(site['telefon'])}</a><a href="mailto:{esc(site['email'])}">{esc(site['email'])}</a></address>
      <nav aria-label="Leistungen im Fußbereich"><strong>Leistungen</strong>{leistungen}</nav>
      <nav aria-label="Rechtliches"><strong>Rechtliches</strong>{recht}</nav>
      {profile_block}
    </div>
    <p class="fuss-klein">© {jahr} {esc(site['firma'])} · {esc(site['register'])} · USt-IdNr. {esc(site['ust_id'])}</p>
  </div>
</footer>"""


# ----------------------------------------------------------------------------- Strukturierte Daten
def json_ld(bau: Bau, seite: Seite) -> dict:
    site = bau.site
    d = seite.daten
    org_id = bau.url("/") + "#organisation"
    web_id = bau.url("/") + "#website"
    graph: list[dict] = []
    if seite.typ == "start":
        adr = site["adresse"]
        graph.append({
            "@type": "ProfessionalService",
            "@id": org_id,
            "name": site["firma"],
            "alternateName": site["name"],
            "url": bau.url("/"),
            "logo": bau.url("/assets/img/icon-512.png"),
            "image": bau.url(site["og_bild"]),
            "description": site["beschreibung"],
            "telephone": site["telefon"],
            "email": site["email"],
            "address": {"@type": "PostalAddress", "streetAddress": adr["strasse"], "postalCode": adr["plz"],
                        "addressLocality": adr["ort"], "addressRegion": adr["region"], "addressCountry": "DE"},
            "areaServed": site["einzugsgebiet"],
            "knowsLanguage": SPRACHEN_BCP47,
            "knowsAbout": site["normen"],
            "employee": {"@type": "Person", "name": site["geschaeftsfuehrer"], "jobTitle": site["geschaeftsfuehrer_titel"]},
            "sameAs": site.get("same_as", []),
        })
        graph.append({"@type": "WebSite", "@id": web_id, "url": bau.url("/"), "name": site["name"],
                      "publisher": {"@id": org_id}, "inLanguage": "de"})
    seite_url = bau.url(seite.pfad)
    web = {"@type": "WebPage", "@id": seite_url + "#webpage", "url": seite_url, "name": d["title"],
           "inLanguage": "de", "isPartOf": {"@id": web_id}, "about": {"@id": org_id}}
    if d.get("description"):
        web["description"] = d["description"]
    graph.append(web)
    if seite.typ in ("leistung", "region"):
        sch = d.get("schema", {})
        graph.append({
            "@type": "Service", "@id": seite_url + "#service",
            "name": sch.get("name", seite.menue), "serviceType": sch.get("serviceType", seite.menue),
            "description": d.get("description", ""), "url": seite_url, "provider": {"@id": org_id},
            "areaServed": sch.get("areaServed", site["einzugsgebiet"]), "availableLanguage": SPRACHEN_BCP47,
        })
    if seite.typ != "start":
        elemente = [{"@type": "ListItem", "position": 1, "name": "Start", "item": bau.url("/")}]
        if seite.typ == "leistung":
            elemente.append({"@type": "ListItem", "position": 2, "name": "Leistungen", "item": bau.url("/#leistungen")})
        elemente.append({"@type": "ListItem", "position": len(elemente) + 1, "name": seite.menue, "item": seite_url})
        graph.append({"@type": "BreadcrumbList", "itemListElement": elemente})
    fragen = [x for a in d.get("abschnitte", []) if a.get("art") == "fragen" for x in a["fragen"]]
    if fragen:
        graph.append({"@type": "FAQPage", "@id": seite_url + "#faq", "mainEntity": [
            {"@type": "Question", "name": re.sub("<[^>]+>", "", x["frage"]),
             "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", x["antwort"])}} for x in fragen]})
    return {"@context": "https://schema.org", "@graph": graph}


# ----------------------------------------------------------------------------- Seite
KOPF_SCRIPT = """(function(){var d=document.documentElement;d.classList.add('js');try{var t=localStorage.getItem('fsh-thema');if(t==='dark'||t==='light'){d.setAttribute('data-theme',t);}}catch(e){}})();"""

FUSS_SCRIPT = """(function(){var d=document.documentElement;var b=document.getElementById('thema-schalter');
function label(){if(!b){return;}var t=d.getAttribute('data-theme');b.textContent=t==='dark'?'Dunkel':t==='light'?'Hell':'Auto';}
label();if(b){b.addEventListener('click',function(){var t=d.getAttribute('data-theme');var n=t==='dark'?'light':t==='light'?null:'dark';
if(n){d.setAttribute('data-theme',n);}else{d.removeAttribute('data-theme');}
try{if(n){localStorage.setItem('fsh-thema',n);}else{localStorage.removeItem('fsh-thema');}}catch(e){}label();});}
var m=document.getElementById('menue-schalter'),n=document.getElementById('hauptnav');
if(m&&n){m.addEventListener('click',function(){var o=n.classList.toggle('offen');m.setAttribute('aria-expanded',o?'true':'false');});
n.addEventListener('click',function(e){if(e.target.tagName==='A'){n.classList.remove('offen');m.setAttribute('aria-expanded','false');}});}})();"""


def seite_html(bau: Bau, seite: Seite, varianten: dict | None) -> str:
    site = bau.site
    d = seite.daten
    seite_url = bau.url(seite.pfad)
    css = bau.href("/assets/site.css", seite) + ("?v=" + bau.css_version if bau.css_version else "")
    og_bild = bau.url(d.get("og_bild", site["og_bild"]))
    if bau.noindex:
        robots = '<meta name="robots" content="noindex, nofollow">\n'
    elif d.get("robots") == "noindex":
        robots = '<meta name="robots" content="noindex, follow">\n'
    else:
        robots = ""
    beschreibung = f'<meta name="description" content="{esc(d["description"])}">\n' if d.get("description") else ""
    og_desc = f'<meta property="og:description" content="{esc(d["description"])}">\n' if d.get("description") else ""
    fonts = "".join(
        f'<link rel="preload" href="{esc(bau.href("/assets/fonts/" + f, seite))}" as="font" type="font/woff2" crossorigin>\n'
        for f in site.get("fonts_vorladen", []))
    hauptteil = [pfadnavigation(bau, seite), held(bau, seite)]
    for a in d.get("abschnitte", []):
        hauptteil.append(abschnitt(bau, seite, a, varianten))
    hauptteil.append(kontakt_abschnitt(bau, seite))
    main_klasse = seite.typ
    canonical = "" if seite.typ == "fehler" else f'<link rel="canonical" href="{esc(seite_url)}">\n'
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(d['title'])}</title>
{beschreibung}{robots}{canonical}<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(site['name'])}">
<meta property="og:locale" content="de_DE">
<meta property="og:title" content="{esc(d['title'])}">
{og_desc}<meta property="og:url" content="{esc(seite_url)}">
<meta property="og:image" content="{esc(og_bild)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(site['og_bild_alt'])}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{esc(bau.href('/favicon.ico', seite))}" sizes="32x32">
<link rel="icon" href="{esc(bau.href('/assets/img/icon-512.png', seite))}" type="image/png" sizes="512x512">
<link rel="apple-touch-icon" href="{esc(bau.href('/assets/img/apple-touch-icon.png', seite))}">
<meta name="theme-color" content="#F4F1EC" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#10161F" media="(prefers-color-scheme: dark)">
{fonts}<link rel="stylesheet" href="{esc(css)}">
<script>{KOPF_SCRIPT}</script>
<script type="application/ld+json">{json_script(json_ld(bau, seite))}</script>
</head>
<body>
<a class="sprung" href="#inhalt">Zum Inhalt springen</a>
{kopf(bau, seite)}
<main id="inhalt" class="{main_klasse}">
{chr(10).join(t for t in hauptteil if t)}
</main>
{fuss(bau, seite)}
<script>{FUSS_SCRIPT}</script>
</body>
</html>
"""


# ----------------------------------------------------------------------------- Nebenprodukte
def sitemap(bau: Bau) -> str:
    zeilen = []
    for s in bau.seiten:
        if s.typ == "fehler" or s.daten.get("robots") == "noindex":
            continue
        datum = git_datum(s.quelle) if s.quelle else bau.heute
        zeilen.append(f"  <url><loc>{esc(bau.url(s.pfad))}</loc><lastmod>{datum}</lastmod></url>")
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(zeilen) + "\n</urlset>\n"


def robots_txt(bau: Bau) -> str:
    if bau.noindex:
        return "# Testbetrieb: nicht indexieren (gebaut mit --noindex)\nUser-agent: *\nDisallow: /\n"
    return f"User-agent: *\nAllow: /\n\nSitemap: {bau.url('/sitemap.xml')}\n"


HTACCESS = """# Apache (z. B. STRATO Webspace). Auf anderen Hostern ohne Wirkung.
AddDefaultCharset UTF-8
Options -Indexes
ErrorDocument 404 /404.html
<IfModule mod_headers.c>
  <FilesMatch "\\.(woff2|webp|jpg|png|ico)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
  <FilesMatch "\\.css$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
  <FilesMatch "\\.html$">
    Header set Cache-Control "public, max-age=600"
  </FilesMatch>
</IfModule>
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml
</IfModule>
"""


# ----------------------------------------------------------------------------- Prüfung
class Sammler(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self.description = None
        self.canonical = None
        self.lang = None
        self.h1: list[str] = []
        self.ueberschriften: list[int] = []
        self.imgs: list[dict] = []
        self.links: list[str] = []
        self.ids: set = set()
        self.jsonld: list[str] = []
        self._modus = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self._modus = "title"
            self.title = ""
        elif tag == "meta" and a.get("name") == "description":
            self.description = a.get("content")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.ueberschriften.append(int(tag[1]))
            if tag == "h1":
                self._modus = "h1"
                self.h1.append("")
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._modus = "ld"
            self.jsonld.append("")
        if a.get("id"):
            self.ids.add(a["id"])

    def handle_endtag(self, tag):
        if tag in ("title", "h1", "script"):
            self._modus = None

    def handle_data(self, data):
        if self._modus == "title":
            self.title += data
        elif self._modus == "h1":
            self.h1[-1] += data
        elif self._modus == "ld":
            self.jsonld[-1] += data


def pruefen(bau: Bau) -> int:
    fehler, warnungen = [], []
    gesammelt: dict[str, Sammler] = {}
    for s in bau.seiten:
        p = Sammler()
        p.feed((bau.ausgabe / s.datei.lstrip("/")).read_text(encoding="utf-8"))
        gesammelt[s.datei] = p
    for s in bau.seiten:
        p = gesammelt[s.datei]
        wo = s.datei
        if p.lang != "de":
            fehler.append(f"{wo}: lang ist {p.lang!r}, erwartet 'de'")
        if not p.title:
            fehler.append(f"{wo}: kein <title>")
        elif len(p.title) > 60:
            warnungen.append(f"{wo}: Title hat {len(p.title)} Zeichen (> 60)")
        if s.typ not in ("recht", "fehler"):
            if not p.description:
                fehler.append(f"{wo}: keine Meta-Description")
            elif not 150 <= len(p.description) <= 160:
                warnungen.append(f"{wo}: Description hat {len(p.description)} Zeichen (Ziel 150–160)")
        if len(p.h1) != 1:
            fehler.append(f"{wo}: {len(p.h1)} h1-Elemente, erwartet genau 1")
        vorher = 0
        for h in p.ueberschriften:
            if vorher and h > vorher + 1:
                warnungen.append(f"{wo}: Überschriftenebene springt von h{vorher} auf h{h}")
                break
            vorher = h
        for img in p.imgs:
            if "alt" not in img:
                fehler.append(f"{wo}: <img src={img.get('src')!r}> ohne alt-Attribut")
        if s.typ != "fehler" and bau.modus == "absolut" and p.canonical != bau.url(s.pfad):
            fehler.append(f"{wo}: canonical ist {p.canonical!r}, erwartet {bau.url(s.pfad)!r}")
        for text in p.jsonld:
            try:
                json.loads(text)
            except json.JSONDecodeError as e:
                fehler.append(f"{wo}: JSON-LD ungültig: {e}")
        if bau.modus == "absolut":
            for href in p.links:
                if href.startswith(("mailto:", "tel:", "http:", "https:")):
                    continue
                pfad, _, anker = href.partition("#")
                ziel_datei = s.datei if not pfad else (pfad + "index.html" if pfad.endswith("/") else pfad)
                if pfad and not (bau.ausgabe / ziel_datei.lstrip("/")).exists():
                    fehler.append(f"{wo}: interner Link {href!r} zeigt auf eine fehlende Datei")
                    continue
                if anker and ziel_datei in gesammelt and anker not in gesammelt[ziel_datei].ids:
                    fehler.append(f"{wo}: Anker {href!r} existiert auf der Zielseite nicht")
    # Sitemap gegen Seiten (im Testbetrieb gibt es keine)
    if not bau.noindex:
        sm = (bau.ausgabe / "sitemap.xml").read_text(encoding="utf-8")
        for s in bau.seiten:
            if s.typ != "fehler" and s.daten.get("robots") != "noindex" and bau.url(s.pfad) not in sm:
                fehler.append(f"sitemap.xml: {s.pfad} fehlt")
    for w in warnungen:
        print("Warnung:", w)
    for f in fehler:
        print("Fehler:", f)
    print(f"Prüfung: {len(bau.seiten)} Seiten, {len(fehler)} Fehler, {len(warnungen)} Warnungen")
    return 1 if fehler else 0


# ----------------------------------------------------------------------------- Hauptprogramm
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Baut die statische Website von FSH-Documentation.")
    ap.add_argument("--ausgabe", default=str(STANDARD_AUSGABE), help="Zielordner (Standard: website/dist)")
    ap.add_argument("--relativ", action="store_true", help="relative Links mit index.html (Vorschau ohne Webserver)")
    ap.add_argument("--basis-url", default=None, help="Basis-URL für canonical, Open Graph, Sitemap (Standard aus site.json)")
    ap.add_argument("--pruefen", action="store_true", help="nach dem Bau prüfen; Fehler ergeben Exit-Code 1")
    ap.add_argument("--hosting", default=None, choices=["strato", "cloudflare", "github"], help="Hosting-Variante für die Datenschutzerklärung (Standard aus site.json)")
    ap.add_argument("--noindex", action="store_true", help="Testbetrieb: alle Seiten noindex, robots.txt sperrt alles, keine Sitemap")
    args = ap.parse_args(argv)

    site = lade_json(INHALT / "site.json")
    if args.hosting:
        site["hosting"] = args.hosting
    seiten: list[Seite] = []
    for name in site["seiten"]:
        quelle = INHALT / f"{name}.json"
        seiten.append(Seite(name, lade_json(quelle), quelle))
    seiten.append(Seite("404", site["fehlerseite"], None))

    ausgabe = Path(args.ausgabe).resolve()
    bau = Bau(site, seiten, ausgabe, "relativ" if args.relativ else "absolut", args.basis_url or site["basis_url"], args.noindex)

    if ausgabe.exists():
        shutil.rmtree(ausgabe)
    ausgabe.mkdir(parents=True)
    shutil.copytree(ASSETS, ausgabe / "assets")
    shutil.copy2(ASSETS / "img" / "favicon.ico", ausgabe / "favicon.ico")
    css = (ASSETS / "site.css").read_bytes()
    bau.css_version = hashlib.sha256(css).hexdigest()[:8]

    varianten = None
    for s in seiten:
        varianten = s.daten.get("varianten")
        ziel = ausgabe / s.datei.lstrip("/")
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(seite_html(bau, s, varianten), encoding="utf-8")
    if not bau.noindex:
        (ausgabe / "sitemap.xml").write_text(sitemap(bau), encoding="utf-8")
    (ausgabe / "robots.txt").write_text(robots_txt(bau), encoding="utf-8")
    (ausgabe / ".htaccess").write_text(HTACCESS, encoding="utf-8")
    # CNAME: von GitHub Pages für die eigene Domain gelesen, auf anderen Hostern ohne Wirkung
    host = re.sub(r"^https?://", "", bau.basis).split("/")[0]
    (ausgabe / "CNAME").write_text(host + "\n", encoding="utf-8")
    print(f"Gebaut: {len(seiten)} Seiten nach {ausgabe} (Links {bau.modus}, Basis {bau.basis}, "
          f"Hosting {site.get('hosting')}{', NOINDEX-Testbetrieb' if bau.noindex else ''})")

    if args.pruefen:
        return pruefen(bau)
    return 0


if __name__ == "__main__":
    sys.exit(main())
